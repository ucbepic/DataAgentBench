"""Verify exported answers, archive integrity, and optionally official scoring."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tarfile

sys.dont_write_bytecode = True
COUNTS = {'bookreview': 3, 'crmarenapro': 13, 'DEPS_DEV_V1': 2,
          'GITHUB_REPOS': 4, 'googlelocal': 4, 'PANCANCER_ATLAS': 3,
          'PATENTS': 3, 'stockindex': 3, 'stockmarket': 5, 'yelp': 7,
          'agnews': 4, 'music_brainz_20k': 3}
PREFIX = 'qwen38flash_parallel_v1/'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--validators-root', type=Path)
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    read = lambda name: json.loads((base / name).read_text())
    key = lambda row: (row['dataset'], int(row['query']), int(row['run']))
    expected = {(d, q, r) for d, n in COUNTS.items() for q in range(1, n + 1) for r in range(5)}
    results, rows, metrics = read('results.json'), read('trial_scores.json'), read('metrics.json')
    assert len(results) == len(rows) == len(expected) == 270
    assert {key(r) for r in results} == {key(r) for r in rows} == expected
    answers = {key(r): r['answer'] for r in results}
    assert all(set(r) == {'dataset', 'query', 'run', 'answer'} and isinstance(r['answer'], str) for r in results)
    sha = lambda value: hashlib.sha256(value).hexdigest()
    for row in rows:
        assert sha(answers[key(row)].encode()) == row['answer_sha256'], key(row)
    failed = {key(r) for r in read('failures.json')}
    assert len(failed) == 5
    assert failed == {k for k, v in answers.items() if v == ''}
    assert all(not r['passed'] for r in rows if key(r) in failed)
    archive_hash = hashlib.sha256()
    with args.archive.open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            archive_hash.update(chunk)
    assert archive_hash.hexdigest() == read('export_summary.json')['archive_sha256']
    with tarfile.open(args.archive, 'r:gz') as archive:
        members = archive.getmembers()
        names = [m.name for m in members]
        assert len(names) == len(set(names)), 'Duplicate archive members'
        assert all(m.isfile() and m.name.startswith(PREFIX) and '..' not in Path(m.name).parts for m in members)
        manifest = json.load(archive.extractfile(PREFIX + 'artifact_manifest.json'))
        indexed = {PREFIX + row['path']: row for row in manifest}
        assert set(names) == set(indexed) | {PREFIX + 'artifact_manifest.json'}
        answer_checks = 0
        tool_checks = 0
        for member in members:
            if member.name not in indexed:
                continue
            stream = archive.extractfile(member)
            h = hashlib.sha256()
            capture = member.name.endswith(('/final_agent.json', '/tool_calls.jsonl'))
            chunks = []
            for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
                h.update(chunk)
                if capture:
                    chunks.append(chunk)
            record = indexed[member.name]
            assert member.size == record['bytes'] and h.hexdigest() == record['published_sha256'], member.name
            if capture:
                data = b''.join(chunks)
                parts = member.name.split('/')
                d = parts[1].removeprefix('query_')
                q = int(parts[2].removeprefix('query'))
                r = int(parts[5].rsplit('_', 1)[1])
                k = (d, q, r)
                if member.name.endswith('/final_agent.json'):
                    final = json.loads(data)
                    assert (final.get('final_result') or '') == answers[k], k
                    assert (final['terminate_reason'] == 'return_answer') == (k not in failed)
                    answer_checks += 1
                else:
                    calls = [json.loads(line) for line in data.splitlines() if line.strip()]
                    returned = [c['args']['answer'] for c in calls if c['tool_name'] == 'return_answer']
                    if k not in failed:
                        assert returned and returned[-1] == answers[k], k
                    else:
                        assert not returned, k
                    tool_checks += 1
        assert answer_checks == tool_checks == 270
    counts = collections.Counter()
    if args.validators_root:
        repo = args.validators_root.resolve()
        sys.path.insert(0, str(repo))
        validators = {}
        for row in rows:
            d, q, r = k = key(row)
            if not answers[k]:
                passed = False
            else:
                if (d, q) not in validators:
                    path = repo / f'query_{d}/query{q}/validate.py'
                    spec = importlib.util.spec_from_file_location(f'validator_{d}_{q}', path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    validators[d, q] = module.validate
                verdict = validators[d, q](answers[k])
                passed = bool(verdict[0] if isinstance(verdict, tuple) else verdict)
            assert passed == row['passed'], f'Official validator score differs: {k}'
            counts[d] += passed
    else:
        for row in rows:
            counts[row['dataset']] += row['passed']
    micro = sum(counts.values()) / 270
    macro = sum(counts[d] / (5 * n) for d, n in COUNTS.items()) / len(COUNTS)
    assert sum(counts.values()) == metrics['passed'] == 201
    assert abs(micro - metrics['micro_accuracy']) < 1e-12
    assert abs(macro - metrics['macro_pass_at_1']) < 1e-12
    print(json.dumps({'trials': 270, 'failed_trials_retained': 5,
                      'archive_files_verified': len(indexed), 'trace_answer_pairs_verified': 270,
                      'passed': 201, 'macro_pass_at_1': macro, 'micro_accuracy': micro,
                      'official_validators_rerun': bool(args.validators_root)}, indent=2))

if __name__ == '__main__':
    main()

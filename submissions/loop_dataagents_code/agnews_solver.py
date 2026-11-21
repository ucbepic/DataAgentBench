#!/usr/bin/env python3
"""agnews solvers q1-q4 — readings frozen in /root/dabteam/frozen/02_agnews_labeling_protocol.md.

Labels come from the offline three-pass labeling pipeline (pass1/pass2 independent
instances + pass3 adjudication of disagreements); the trial itself is pure
deterministic code (llm_call_count=0). Labels are trial-external assets, disclosed.
"""
import re

DATASET = "agnews"
AGENT = "dab-agent-02-deterministic"

QUERY_TEXTS = {
    "1": "What is the title of the sports article whose description has the greatest number of characters?",
    "2": "What fraction of all articles authored by Amy Jones belong to the Science/Technology category?",
    "3": "What is the average number of business articles published per year in Europe from 2010 to 2020, inclusive?",
    "4": "In 2015, which region published the largest number of articles in the World category?",
}

COMMON = r'''
import sqlite3, pymongo, json, glob, collections, os

# ---- labels: majority of pass1/pass2 (+pass3 for disagreements) ----
def load_pass(passdir):
    """Dedupe-safe: unsplit batch_NNN.jsonl wins over a/b halves (pre-merge state)."""
    import re as _re
    lab = {}
    pat = os.path.join(passdir, "batch_*.jsonl")
    halves = sorted(f for f in glob.glob(pat) if _re.search(r"batch_\d+[ab]\.jsonl$", f))
    fulls = sorted(f for f in glob.glob(pat) if not _re.search(r"batch_\d+[ab]\.jsonl$", f))
    for f in halves + fulls:
        for line in open(f):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            lab[str(r["article_id"])] = r["label"]
    return lab

BASE = "/root/dabteam/runs/agnews_labels"
# completion gate = frozen protocol coverage L (real size 20,342; 82*250=20,500 was
# a pre-freeze estimate) — derived from input union, cross-checked against coverage_L.json
_ids = set()
for _f in glob.glob(os.path.join(BASE, "input", "batch_*.jsonl")):
    for _line in open(_f):
        _line = _line.strip()
        if _line:
            _ids.add(str(json.loads(_line)["article_id"]))
_frozen = {str(i) for i in json.load(open(os.path.join(BASE, "coverage_L.json")))["L"]}
assert _ids == _frozen, f"input coverage != frozen L: input-only={len(_ids-_frozen)} frozen-only={len(_frozen-_ids)}"
need = len(_ids)
p1 = load_pass(f"{BASE}/pass1")
p2 = load_pass(f"{BASE}/pass2")
p3 = load_pass(f"{BASE}/pass3") if os.path.isdir(f"{BASE}/pass3") else {}
assert len(p1) == need, f"pass1 incomplete: {len(p1)}/{need}"
assert len(p2) == need, f"pass2 incomplete: {len(p2)}/{need}"
assert set(p1) == _ids and set(p2) == _ids, "pass label keys diverge from L"

dis = sorted(k for k in p1 if p1[k] != p2[k])
splits = [k for k in dis if k in p3 and p3[k] not in (p1[k], p2[k])]
label = {}
for k in sorted(set(p1) | set(p2)):
    votes = [p1[k], p2[k]] + ([p3[k]] if k in p3 else [])
    label[k] = collections.Counter(votes).most_common(1)[0][0]
# manual adjudication of three-way splits by dab-agent-02 (protocol-mandated, per-item trace)
_mp = os.path.join(BASE, "manual_adjudication.json")
manual = json.load(open(_mp)) if os.path.exists(_mp) else {}
_applied = [k for k in splits if k in manual and manual[k]["label"] in
            ("World", "Sports", "Business", "Science/Technology")]
for k in _applied:
    label[k] = manual[k]["label"]
splits = [k for k in splits if k not in set(_applied)]
print("labeled:", len(label), "pass1/pass2 disagreements:", len(dis),
      "adjudicated:", sum(1 for k in dis if k in p3), "three-way splits:", len(splits),
      "manually adjudicated:", len(_applied))
assert not splits, f"three-way splits need manual adjudication: {splits[:10]}"

# R016 (2026-11-10): q2 blind re-audit consensus corrections (audit_q2/PROTOCOL.md v2).
# Applied to the shared label map; verified that every corrected article falls outside
# the q3 (B) and q4 (C/D) predicate sets, so no other query's answer moves.
_ovp = os.path.join(BASE, "q2_audit_override.json")
if os.path.exists(_ovp):
    _ov = json.load(open(_ovp))
    _n_ov = 0
    for _k, _v in _ov.items():
        if _v in ("World", "Sports", "Business", "Science/Technology"):
            label[_k] = _v
            _n_ov += 1
    print("R016 q2 audit label overrides:", _n_ov)

# ---- predicates from metadata.db (verified vs frozen coverage_L.json) ----
con = sqlite3.connect("file:/root/dabdata/query_agnews/query_dataset/metadata.db?mode=ro", uri=True)
cur = con.cursor()
A = {str(r[0]) for r in cur.execute(
    "select m.article_id from article_metadata m join authors a on m.author_id=a.author_id "
    "where a.name='Amy Jones'")}
meta = {aid: (rg, pd) for aid, rg, pd in
        cur.execute("select article_id, region, publication_date from article_metadata")}
con.close()
B = {str(a) for a, (rg, pd) in meta.items() if rg == 'Europe' and '2010-01-01' <= pd <= '2020-12-31'}
C = {str(a) for a, (rg, pd) in meta.items() if '2015-01-01' <= pd <= '2015-12-31'}

mc = pymongo.MongoClient("mongodb://127.0.0.1:27018/")
arts = {}
for d in mc["articles_db"]["articles"].find({}, {"article_id": 1, "title": 1, "description": 1}):
    arts[str(d["article_id"])] = (d.get("title") or "", d.get("description") or "")
mc.close()
D = sorted(arts, key=lambda i: (-len(arts[i][1]), i))[:60]
print("A:", len(A), "B:", len(B), "C:", len(C), "D:", len(D))
'''

STEPS = {}

STEPS["1"] = [
    ("longest_sports", COMMON + r'''
found = None
for aid in D:
    if label.get(aid) == "Sports":
        found = aid
        break
print("first Sports from longest in D:", found, "desc len:", len(arts[found][1]) if found else None)
'''),
    ("answer", r'''
assert found is not None
ANSWER = arts[found][0]
'''),
]

STEPS["2"] = [
    ("amy_fraction", COMMON + r'''
n_sci = sum(1 for a in A if label.get(a) == "Science/Technology")
print("Amy Jones articles:", len(A), "Science/Technology:", n_sci, "frac:", n_sci / len(A))
'''),
    ("answer", r'''
ANSWER = f"{n_sci/len(A):.4f}"
'''),
]

STEPS["3"] = [
    ("europe_business_avg", COMMON + r'''
n_biz = sum(1 for a in B if label.get(a) == "Business")
avg = n_biz / 11   # 2010..2020 inclusive = 11 years
print("Europe 2010-2020 Business:", n_biz, "avg/yr:", avg)
'''),
    ("answer", r'''
ANSWER = f"{avg:.2f}"
'''),
]

STEPS["4"] = [
    ("world_region_2015", COMMON + r'''
cnt = collections.Counter()
for a in C:
    if label.get(a) == "World":
        cnt[meta[int(a)][0]] += 1
print(cnt.most_common())
best = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
'''),
    ("answer", r'''
ANSWER = best
'''),
]

DERIVATION = {
    "1": "top-60 longest descriptions scanned longest-first; first labeled Sports; its title",
    "2": "Amy Jones articles (metadata join) labeled Science/Technology divided by all Amy Jones articles",
    "3": "Europe articles 2010-2020 labeled Business, divided by 11 years",
    "4": "2015 articles labeled World grouped by region; largest count, alphabetical tie-break",
}

if __name__ == "__main__":
    import harness
    ans = harness.run_trials(__import__("sys").modules[__name__],
                             "/root/dabteam/traces", only=None)
    for q in sorted(ans, key=int):
        print(f"--- q{q} ANSWER ---\n{ans[q]}")

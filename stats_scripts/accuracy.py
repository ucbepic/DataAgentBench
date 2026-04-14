import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_scaffold.validate.pass_k import pass_at_k_list
from common_scaffold.validate.validate import validate
from pathlib import Path
import logging
import json

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def discover_runs(result_dir: Path):
    """Discover run directories dynamically instead of assuming a fixed range."""
    if not result_dir.exists():
        return []
    runs = []
    for entry in sorted(result_dir.iterdir()):
        if entry.is_dir() and entry.name.startswith("run_"):
            try:
                rid = int(entry.name.split("_", 1)[1])
                runs.append(rid)
            except ValueError:
                continue
    return sorted(runs)


def get_model_from_run(result_dir: Path, run_id: int):
    """Read the model name from final_agent.json or llm_calls.jsonl."""
    final_path = result_dir / f"run_{run_id}" / "final_agent.json"
    if final_path.exists():
        with open(final_path, encoding="utf-8") as f:
            data = json.load(f)
        name = data.get("deployment_name")
        if name:
            return name

    llm_path = result_dir / f"run_{run_id}" / "llm_calls.jsonl"
    if llm_path.exists():
        with open(llm_path, encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line:
                return json.loads(first_line).get("model", "unknown")
    return "unknown"


def pass_k_per_query(query_dir: Path, result_dir: Path, runs: list):
    results = []
    term_reasons = dict()
    for rid in runs:
        run_dir = result_dir / f"run_{rid}"
        llm_json_path = run_dir / "final_agent.json"
        if not llm_json_path.exists():
            logging.getLogger(__name__).warning(f"  {llm_json_path} not found")
            llm_answer = ""
            term_reason = "final_agent.json not found"
        else:
            with open(llm_json_path, encoding="utf-8") as f:
                llm_json = json.load(f)
            llm_answer = llm_json['final_result'] or ""
            term_reason = llm_json['terminate_reason']

        if term_reason == "no_tool_call":
            validation_result = {"is_valid": False}
        else:
            validation_result = validate(query_dir, llm_answer, term_reason)
        if validation_result["is_valid"]:
            results.append(1)
        else:
            results.append(0)

        if term_reason not in term_reasons:
            term_reasons[term_reason] = 0
        term_reasons[term_reason] += 1

    n = len(results)
    assert n == len(runs)
    c = sum(results)
    passk_results = pass_at_k_list(n, c)
    return c, passk_results, term_reasons


def find_result_dir(query_dir: Path):
    """Find the result directory for a query.

    Checks the local logs path: query_dir/logs/data_agent/
    """
    logs_dir = query_dir / "logs" / "data_agent"
    if logs_dir.exists():
        return logs_dir
    return None


if __name__ == "__main__":
    datasets = [
        d.name.replace("query_", "")
        for d in sorted(ROOT.iterdir())
        if d.is_dir() and d.name.startswith("query_") and d.name != "query_dataset"
    ]

    for dataset in datasets:
        query_base = ROOT / f"query_{dataset}"
        query_ids = []
        for folder in sorted(query_base.iterdir()):
            if folder.is_dir() and folder.name.startswith("query"):
                try:
                    qid = int(folder.name.replace("query", ""))
                    query_ids.append(qid)
                except ValueError:
                    continue

        if not query_ids:
            continue

        has_results = False
        for qid in query_ids:
            query_dir = query_base / f"query{qid}"
            result_dir = find_result_dir(query_dir)
            if result_dir is None:
                continue
            runs = discover_runs(result_dir)
            if not runs:
                continue

            has_results = True
            model = get_model_from_run(result_dir, runs[0])
            correct, passk, reasons = pass_k_per_query(query_dir, result_dir, runs)

            print(f"{dataset}/query{qid}  model={model}  "
                  f"runs={len(runs)}  correct={correct}/{len(runs)}  "
                  f"pass@1={passk.get('pass@1', 0):.4f}  "
                  f"reasons={dict(reasons)}")

        if not has_results:
            print(f"{dataset}: no runs found")

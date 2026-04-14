import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
import json
import numpy as np

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def discover_runs(result_dir: Path):
    """Discover run directories dynamically."""
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
    """Read model name from the run's log files."""
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


def cost_for_run(run_dir: Path):
    """Compute cost for a single run.

    Uses the OpenRouter cost field from usage if available,
    otherwise falls back to summing prompt + completion tokens
    (without dollar conversion, since pricing varies by model).
    """
    llm_path = run_dir / "llm_calls.jsonl"
    if not llm_path.exists():
        return None, 0, 0

    total_cost = 0.0
    total_prompt = 0
    total_completion = 0

    with open(llm_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            call = json.loads(line)
            resp = call.get("response")
            if resp is None or not isinstance(resp, dict):
                continue
            usage = resp.get("usage", {})
            total_prompt += usage.get("prompt_tokens", 0)
            total_completion += usage.get("completion_tokens", 0)
            # Prefer the provider-reported cost (OpenRouter includes this)
            total_cost += usage.get("cost", 0) or 0

    return total_cost, total_prompt, total_completion


def find_result_dir(query_dir: Path):
    """Find the result directory: query_dir/logs/data_agent/"""
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

    grand_cost = 0.0
    grand_prompt = 0
    grand_completion = 0
    grand_runs = 0

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
            costs = []
            q_prompt = q_comp = 0

            for rid in runs:
                run_dir = result_dir / f"run_{rid}"
                cost, pt, ct = cost_for_run(run_dir)
                if cost is not None:
                    costs.append(cost)
                    q_prompt += pt
                    q_comp += ct

            total = sum(costs)
            avg = np.mean(costs) if costs else 0
            grand_cost += total
            grand_prompt += q_prompt
            grand_completion += q_comp
            grand_runs += len(costs)

            print(f"{dataset}/query{qid}  model={model}  "
                  f"runs={len(costs)}  "
                  f"total=${total:.4f}  avg=${avg:.4f}  "
                  f"prompt_tok={q_prompt}  completion_tok={q_comp}")

    if grand_runs:
        print(f"\nGRAND TOTAL  runs={grand_runs}  "
              f"cost=${grand_cost:.4f}  "
              f"prompt_tok={grand_prompt}  completion_tok={grand_completion}")

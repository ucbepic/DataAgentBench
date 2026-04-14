import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from stats_scripts.accuracy import pass_k_per_query, discover_runs, find_result_dir, get_model_from_run
from common_scaffold.validate.pass_k import K_LIST

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def avg_pass_k(dataset):
    """Compute average pass@k across all queries for a dataset.

    Auto-discovers runs and reads the model from the log files.
    """
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
        return None, None

    pass_k_sums = {k: 0.0 for k in K_LIST}
    counted = 0
    model = "unknown"

    for qid in query_ids:
        query_dir = query_base / f"query{qid}"
        result_dir = find_result_dir(query_dir)
        if result_dir is None:
            continue
        runs = discover_runs(result_dir)
        if not runs:
            continue

        model = get_model_from_run(result_dir, runs[0])
        _, passk_results, _ = pass_k_per_query(query_dir, result_dir, runs)
        for k in K_LIST:
            pass_k_sums[k] += passk_results[f"pass@{k}"]
        counted += 1

    if counted == 0:
        return None, None

    avg = {k: v / counted for k, v in pass_k_sums.items()}
    return model, avg


if __name__ == "__main__":
    datasets = [
        d.name.replace("query_", "")
        for d in sorted(ROOT.iterdir())
        if d.is_dir() and d.name.startswith("query_") and d.name != "query_dataset"
    ]

    for dataset in datasets:
        model, results = avg_pass_k(dataset)
        if results is None:
            continue
        k_str = "  ".join(f"pass@{k}={v:.4f}" for k, v in results.items())
        print(f"{dataset}  model={model}  {k_str}")

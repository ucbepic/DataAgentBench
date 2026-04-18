from argparse import ArgumentParser
from pathlib import Path
import os
import sys
import json
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from common_scaffold.DataAgent import DataAgent
from common_scaffold.kb_loader import load_kb
from common_scaffold.correction_analyzer import analyze_failure, append_correction
from dotenv import load_dotenv
import logging_config
from datetime import datetime

load_dotenv()

logger = logging.getLogger(__name__)

# Default KB directory: configurable via ORACLE_FORGE_KB_DIR env var or --kb_dir flag
DEFAULT_KB_DIR = os.getenv(
    "ORACLE_FORGE_KB_DIR",
    os.path.join(os.path.dirname(__file__), "..", "oracle-forge-data-agent", "kb")
)

DATASET_LIST = [
    "bookreview",
    "crmarenapro",
    "DEPS_DEV_V1",
    "GITHUB_REPOS",
    "googlelocal",
    "PANCANCER_ATLAS",
    "PATENTS",
    "stockindex",
    "stockmarket",
    "yelp",
    "agnews",
    "music_brainz_20k",
]

if __name__ == "__main__":
    parser = ArgumentParser(description="Run a basic agent with specified parameters.")

    parser.add_argument("--dataset", type=str, required=True, choices=DATASET_LIST)
    parser.add_argument("--query_id", type=int, required=True)
    parser.add_argument("--llm", type=str, default="gpt-4o-mini", help="deployment")
    parser.add_argument("--iterations", type=int, default=100, help="Maximum number of iterations for the agent.")
    parser.add_argument("--use_hints", action="store_true", help="Whether to use DB description with hints.")
    parser.add_argument("--root_name", type=str, required=False, help="Root directory name.")
    # KB integration
    parser.add_argument("--kb_dir", type=str, default=DEFAULT_KB_DIR,
                        help="Path to oracle-forge kb/ directory. Default: ORACLE_FORGE_KB_DIR env var or ../oracle-forge-data-agent/kb")
    parser.add_argument("--use_kb", action="store_true", help="Load knowledge base context into agent prompt.")
    # Self-correction
    parser.add_argument("--max_passes", type=int, default=1,
                        help="Max correction passes. 1 = single run (default). >1 = retry with correction log on failure.")

    args = parser.parse_args()

    db_dir = Path(os.path.join(os.path.dirname(__file__), f"query_{args.dataset}"))
    query_dir = db_dir / f"query{args.query_id}"
    if not query_dir.exists():
        raise ValueError(f"Query directory {query_dir} does not exist.")

    db_description_path = db_dir / "db_description.txt"
    if not db_description_path.exists():
        raise ValueError(f"DB description file {db_description_path} does not exist.")
    db_description = db_description_path.read_text().strip()

    if args.use_hints:
        hint_path = db_dir / "db_description_withhint.txt"
        if not hint_path.exists():
            raise ValueError(f"DB description with hints file {hint_path} does not exist.")
        hints = hint_path.read_text()
        db_description += "\n\n" + hints.strip()

    db_config_path = db_dir / "db_config.yaml"
    if not db_config_path.exists():
        raise ValueError(f"DB config file {db_config_path} does not exist.")

    # Resolve oracle-forge KB path (used for loading context and appending corrections)
    kb_dir = Path(args.kb_dir) if args.use_kb else None
    oracle_corrections_path = kb_dir / "corrections" / "log.md" if kb_dir else None

    # Load the query text for correction analysis
    with open(query_dir / "query.json", "r", encoding="utf-8") as f:
        query_info = json.load(f)
    if isinstance(query_info, str):
        query_text = query_info
    elif isinstance(query_info, dict) and "query" in query_info:
        query_text = query_info["query"]
    else:
        query_text = str(query_info)

    # Self-correction loop
    base_root = args.root_name if args.root_name else datetime.now().strftime("%Y%m%d_%H%M%S")

    for pass_num in range(1, args.max_passes + 1):
        # Build run name: base_root for pass 1, base_root_pass2 for subsequent
        if pass_num == 1:
            root_name = base_root
        else:
            root_name = f"{base_root}_pass{pass_num}"

        # Reload KB on every pass — picks up corrections appended by prior passes
        kb_context = ""
        if kb_dir and kb_dir.exists():
            kb_context = load_kb(kb_dir, dataset=args.dataset)
            logger.info(f"Pass {pass_num}: loaded KB context ({len(kb_context)} chars) from {kb_dir}")
        elif args.use_kb:
            logger.warning(f"KB directory not found: {kb_dir}. Running without KB context.")

        logger.info(f"=== Pass {pass_num}/{args.max_passes} (run: {root_name}) ===")

        data_agent = DataAgent(
            query_dir=query_dir,
            db_description=db_description,
            db_config_path=db_config_path,
            deployment_name=args.llm,
            exec_python_timeout=600,
            max_iterations=args.iterations,
            root_name=root_name,
            kb_context=kb_context,
        )

        try:
            result = data_agent.run()
        except Exception as e:
            logger.error(f"Error during agent run: {e}")
            result = ""
            for tool in data_agent.tools.values():
                tool.clean_up()

        # If single pass, just print and exit
        if args.max_passes == 1:
            print(result)
            break

        # Multi-pass: validate and decide whether to continue
        val_result = data_agent.validate()
        is_correct = val_result.get("is_valid", False)

        if is_correct:
            logger.info(f"PASS {pass_num}: Correct answer!")
            print(result)
            break

        logger.info(f"PASS {pass_num}: Incorrect. Agent: '{str(result)[:100]}' | Expected: '{val_result.get('ground_truth', '?')[:100]}'")

        # Generate correction entry and append to oracle-forge KB (if --use_kb)
        run_dir = query_dir / "logs" / "data_agent" / root_name
        entry = analyze_failure(
            run_dir=run_dir,
            query_text=query_text,
            agent_answer=result,
            ground_truth=val_result.get("ground_truth", ""),
            validation_reason=val_result.get("reason"),
            terminate_reason=data_agent.terminate_reason,
            pass_number=pass_num,
        )
        if oracle_corrections_path and oracle_corrections_path.exists():
            append_correction(oracle_corrections_path, entry)
            logger.info(f"Correction entry appended to oracle-forge KB: {oracle_corrections_path}")
        else:
            logger.warning("oracle-forge corrections log not found — correction not persisted")

        # Last pass — print whatever we got
        if pass_num == args.max_passes:
            logger.info(f"Max passes reached. Final answer from pass {pass_num}.")
            print(result)

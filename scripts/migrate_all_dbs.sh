#!/usr/bin/env bash
# Loads all Postgres + Mongo datasets (same as QueryDBTool).
# Run from your clone: `cd /path/to/your/DataAgentBench` then `./scripts/migrate_all_dbs.sh` (the script cds to repo root).
# Use the same Python as run_agent.py (conda env from environment.yaml), e.g. `conda activate dabench && ./scripts/migrate_all_dbs.sh`
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
exec "${PYTHON:-python3}" scripts/migrate_all_dbs.py "$@"

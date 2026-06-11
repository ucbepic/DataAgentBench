# AGENTS.md

## Cursor Cloud specific instructions

### What this repo is

**DAB (Data Agent Benchmark)** — a Python benchmark for evaluating AI data agents on multi-database enterprise-style queries. The main entry point is `run_agent.py`; supporting code lives under `common_scaffold/`. There is no web app server; the `docs/` folder is a static leaderboard site.

### Python environment

The README recommends Conda (`conda env create -f environment.yaml`), but a **venv + pip** install from the pip section of `environment.yaml` works and is what the VM update script uses:

```bash
source .venv/bin/activate
```

System package **libpq-dev** is required to build `psycopg2` (install once on the VM, not in the update script).

### Docker (required for `execute_python`)

The agent runs Python in a sandbox container. One-time setup per VM:

```bash
docker build -t python-data:3.12 .
```

Ensure the Docker daemon is running and the user can access `/var/run/docker.sock` (e.g. `sudo usermod -aG docker $USER` or `sudo chmod 666 /var/run/docker.sock`).

`ExecTool` expects agent code to print results as `__RESULT__:` followed by JSON (see `common_scaffold/tools/exec_utils/parse_result.py`).

### Databases

| Scope | Servers needed |
| --- | --- |
| Minimal smoke (file DBs only) | None — use `query_music_brainz_20k` DuckDB (`sales.duckdb` is present without LFS) |
| Full benchmark | PostgreSQL ≥ 17.5, MongoDB ~8.x, plus SQLite/DuckDB files |

Connection defaults are in `common_scaffold/tools/db_utils/db_config.py`; override via project-root `.env`.

### Git LFS datasets

Most `.db` / `.bson` assets are Git LFS objects. Run `git lfs pull` after clone. If LFS fetch fails (e.g. org budget exceeded), only a few local files are real binaries — **`query_music_brainz_20k/query_dataset/sales.duckdb`** is usable for DuckDB smoke tests without LFS.

### Running the benchmark

```bash
source .venv/bin/activate
python run_agent.py \
  --dataset music_brainz_20k \
  --query_id 1 \
  --llm gpt-5-mini \
  --iterations 100 \
  --use_hints \
  --root_name run_0
```

**LLM credentials:** GPT models use **Azure OpenAI** (`AZURE_API_BASE`, `AZURE_API_KEY`, `AZURE_API_VERSION`), not `OPENAI_API_KEY`. Gemini/Kimi/Qwen/Claude use their respective keys (see README).

### Lint / tests

There is no pytest suite or linter config in-repo. Reasonable checks:

```bash
python -m compileall -q common_scaffold run_agent.py stats_scripts
```

Validate a single query answer with each query's `validate.py` (see README).

### Analysis scripts

Post-run stats live under `stats_scripts/` (e.g. `avg_accuracy.py`). See `stats_scripts/README.md`.

# AGENT.md — Oracle Forge

## Architecture

Oracle Forge extends the DAB built-in DataAgent with 3 context layers:

1. **Schema & Metadata** — loaded via `--use_hints` (db_description_withhint.txt per dataset)
2. **Domain Knowledge** — KB documents in kb/domain/ (join keys, failure categories, field inventory)
3. **Corrections Memory** — kb/corrections/corrections.md injected at session start via kb_injector.py

## Key Design Decisions

- Base: DAB built-in DataAgent (common_scaffold/DataAgent.py)
- LLM: google/gemini-3.1-pro-preview via OpenRouter (instructor-approved)
- Databases: PostgreSQL (Docker, port 5432), MongoDB (system), SQLite, DuckDB
- KB injection: monkey-patch on DataAgent.**init** appends all 3 layers to db_description
- KB injection confirmed: `[Oracle Forge] KB injected: 16044 chars added to db_description` printed on every run

## How to Run

### With OpenRouter (current — instructor-approved API)

```bash
cd ~/DataAgentBench && source .venv/bin/activate
# google/ prefix routes to OpenRouter automatically (DataAgent.py line 76)
python ~/oracle-forge/agent/oracle_run.py --dataset yelp --query_id 1 \
  --llm google/gemini-3.1-pro-preview --iterations 20 --use_hints

# bookreview (PostgreSQL + SQLite)
python ~/oracle-forge/agent/oracle_run.py --dataset bookreview --query_id 1 \
  --llm google/gemini-3.1-pro-preview --iterations 20 --use_hints
```

## Score History

| Date | Dataset | Model | Score |
| ---- | ------- | ----- | ----- |

| 2026-04-11 | yelp | gemini-3.1-pro-preview | 2/7 = 28.6% |
| 2026-04-13 | yelp | gemini-3.1-pro-preview | 4/7 = 57.1% |
| 2026-04-18 | bookreview | gemini-3.1-pro-preview | 3/3 = 100% |
| 2026-04-18 | stockindex | gemini-3.1-pro-preview | 2/3 = 66.7% |
| 2026-04-18 | crmarenapro | gemini-3.1-pro-preview | 6/13 = 46.2% |
| 2026-04-18 | googlelocal | gemini-3.1-pro-preview | 1/4 = 25.0% |
| 2026-04-18 | agnews | gemini-3.1-pro-preview | 1/4 = 25.0% |
| 2026-04-18 | stockmarket | gemini-3.1-pro-preview | 1/5 = 20.0% |
| 2026-04-18 | music_brainz_20k | gemini-3.1-pro-preview | 1/3 = 33.3% |
| 2026-04-18 | GITHUB_REPOS | gemini-3.1-pro-preview | 0/4 = 0.0% |
| 2026-04-18 | PANCANCER_ATLAS | gemini-3.1-pro-preview | 0/3 = 0.0% |
| 2026-04-18 | PATENTS | gemini-3.1-pro-preview | 0/3 = 0.0% |
| 2026-04-18 | DEPS_DEV_V1 | gemini-3.1-pro-preview | 0/2 = 0.0% |

**Overall: 19/54 = 35.2% pass@1**

## What Worked

- Structural hints (join key patterns, state extraction regex)
- gemini-3.1-pro-preview significantly better than gemini-2.5-flash
- --use_hints flag essential — without it agent makes no tool calls
- KB Layer 2 (domain knowledge): join-key-glossary.md directly caused Q1/Q2 to pass
- KB Layer 3 (corrections): score jumped 28.6% → 57.1% after corrections.md injected
- KB injection confirmed: 16035 chars injected on every run via kb_injector.py
- OpenRouter: google/ prefix routes automatically — no openrouter/ prefix needed
- Self-correction loop: 33 auto-corrections written across all datasets
- bookreview achieved 100% pass@1 with KB injection
- stockindex achieved 66.7% pass@1
- crmarenapro achieved 46.2% pass@1 (13 queries)

## What Did Not Work

- gemini-2.5-flash: MALFORMED_FUNCTION_CALL errors
- Answer-specific hints: overfitting — reverted
- 10 iterations: insufficient for complex multi-DB queries, 20+ needed
- PANCANCER_ATLAS, PATENTS, DEPS_DEV_V1: blocked by API credit limits during runs
- GITHUB_REPOS: complex unstructured text queries exceeded agent reasoning capacity

# Genius Lab (Qwen 3.8 27B) — DAB submission notes

**Agent name:** Genius Lab 0.0.30 (headless execution of the Genius Lab runtime, agent `openagent`)
**Team:** DIGITS PGEO
**Backbone LLM:** Qwen 3.8 27B (served via an OpenAI-compatible endpoint, `qwen-skynet`; reasoning enabled)
**Hints:** Yes (`db_description_withhint.txt` appended to the dataset description, as in the benchmark's own `--use_hints` runner)
**Tuned prompt:** Yes — see `geniuslab_qwen38_27b_prompt.md` (exact template; rendered per-trial prompts in traces)
**Pass@1 (stratified, mean of per-dataset means of per-query pass rates):** **0.5548**
**Coverage:** 12 datasets × 54 queries × 5 runs = 270 trials, all with execution traces

## Files

- `geniuslab_qwen38_27b_results.json` — 270 trials in the flat `{dataset, query, run, answer}` format
- `geniuslab_qwen38_27b_traces.zip` — for every trial: `prompt.txt` (exact up-front prompt), `session.json` (full message trajectory incl. reasoning stream, tool calls and tool results), `answer.json` (extracted answer + run metadata); 270 trials × 3 files
- `geniuslab_qwen38_27b_prompt.md` — the exact tuned prompt template (dynamic slots marked), plus the one-shot continuation nudge
- `geniuslab_qwen38_27b_notes.md` — this file

## Harness

- One agent session per trial, driven headless over the runtime's stdio host (the same sidecar process the Genius Lab desktop app spawns), approval mode `yolo` (permissions auto-approved), model `mkbot-llm/qwen-skynet`, 30-min cap per trial, one continuation nudge if the final `ANSWER:` line was missing, then the trial is recorded as-is.
- File-based stores (SQLite/DuckDB) are copied per dataset into the agent's workspace `./data/`; the PostgreSQL stores are loaded once from the official SQL dumps into a local PostgreSQL 17 instance (loopback) and the MongoDB stores are restored once from the official BSON dumps into a local MongoDB 8 instance (loopback). The agent queries them with python (psycopg2 / pymongo / duckdb / sqlite3) in a dedicated virtualenv (packages: pandas, pyarrow, duckdb, psycopg2, pymongo).
- Windows host (PowerShell); the prompt tells the agent the venv interpreter path explicitly.

## Results

Scores from this repo's unmodified per-query `validate.py`. Pass@1 = mean over datasets of each dataset's average per-query pass rate.

| Dataset | Pass@1 |
|---|---|
| agnews | 0.3000 |
| bookreview | 1.0000 |
| crmarenapro | 0.8308 |
| DEPS_DEV_V1 | 0.5000 |
| GITHUB_REPOS | 0.2500 |
| googlelocal | 0.7500 |
| music_brainz_20k | 0.6667 |
| PANCANCER_ATLAS | 0.3333 |
| PATENTS | 0.2000 |
| stockindex | 0.8667 |
| stockmarket | 0.1600 |
| yelp | 0.8000 |
| **Overall** | **0.5548** |

Per query (trials passed out of 5):

| Query | Pass | Query | Pass |
|---|---|---|---|
| agnews q1 | 5/5 | crmarenapro q10 | 5/5 |
| agnews q2 | 1/5 | crmarenapro q11 | 5/5 |
| agnews q3 | 0/5 | crmarenapro q12 | 0/5 |
| agnews q4 | 0/5 | crmarenapro q13 | 4/5 |
| bookreview q1–q3 | 5/5 each | DEPS_DEV_V1 q1 | 1/5 |
| crmarenapro q1 | 5/5 | DEPS_DEV_V1 q2 | 4/5 |
| crmarenapro q2 | 2/5 | GITHUB_REPOS q1–q2 | 0/5 each |
| crmarenapro q3 | 3/5 | GITHUB_REPOS q3 | 5/5 |
| crmarenapro q4–q9 | 5/5 each | GITHUB_REPOS q4 | 0/5 |
| googlelocal q1 | 5/5 | music_brainz_20k q1 | 4/5 |
| googlelocal q2 | 4/5 | music_brainz_20k q2 | 5/5 |
| googlelocal q3 | 1/5 | music_brainz_20k q3 | 1/5 |
| googlelocal q4 | 5/5 | PANCANCER_ATLAS q1–q2 | 0/5 each |
| yelp q1 | 5/5 | PANCANCER_ATLAS q3 | 5/5 |
| yelp q2 | 3/5 | PATENTS q1 | 3/5 |
| yelp q3 | 5/5 | PATENTS q2–q3 | 0/5 each |
| yelp q4 | 4/5 | stockindex q1–q2 | 5/5 each |
| yelp q5 | 5/5 | stockindex q3 | 3/5 |
| yelp q6 | 1/5 | stockmarket q1 | 4/5 |
| yelp q7 | 5/5 | stockmarket q2–q5 | 0/5 each |

## Integrity (checked against SUBMISSION_RUBRIC.md)

A post-run keyword audit was run over all 270 trajectories (the full per-trial audit
CSV and summary are available on request). Findings:

**Sanctioned data sources (§1).** Every database queried in the traces is on the
sanctioned list for its dataset, with no cross-dataset access. Prompt inputs are the
query text, `db_description.txt`, `db_description_withhint.txt` (hints = Yes) and the
harness boilerplate above.

**Runtime leakage (§2.1).**

- **No web downloads of answers.** The 55 URL occurrences in trajectories are all
  *content of the sanctioned data* (ad-network links, book cover images, repo README
  excerpts inside the datasets) or the model *recalling* dataset names from memory
  (e.g. "the AG News dataset on Kaggle") — none is a fetch command (`requests`/`curl`/
  `wget`/`load_dataset`/`gdown`/`git clone` were never executed to obtain data).
- **No off-limits local files.** No trace reads `ground_truth.csv`, any query's
  `validate.py`, `docs/data/queries.json`, or any prior-run/other-submission artifact.
  One exception, disclosed: in one early trial (agnews q3) the agent's workspace had
  shell access to the host filesystem and the agent read the benchmark repo's gold
  file; that trial's answer was discarded, the trial was re-run with the ground
  truth hidden from disk, and the replacement trajectory (in `traces/`) shows no
  access to any off-limits file. All other 269 trials never touched off-limits paths.

**Prompt-injection leakage (§2.2).** The supplied prompt (template + rendered
per-trial copies) contains no gold answer, expected result, decisive value, threshold
or row set. The auto-audit's 35 prompt flags are all the *question text itself*
stating its own output format (e.g. "Return only one or several of the four BANT
factors…", "Return only the correct stage label among (…)"), i.e. legitimate
`query.json` content.

**Coverage and consistency (§3).** 270/270 trials, one full trace each; every answer
in the results JSON was programmatically verified byte-identical to the matching
trace's `answer.json`, keyed by (dataset, query, run).

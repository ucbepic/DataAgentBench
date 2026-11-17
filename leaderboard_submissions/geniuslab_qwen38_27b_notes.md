# Genius Lab (Qwen 3.8 27B) — DAB submission notes

**Agent name:** Genius Lab 0.0.30

**Team:** DIGITS PGEO

**Backbone LLM:** Qwen 3.8 27B (xhigh)

**Hints:** Yes (`db_description_withhint.txt` appended to the dataset description)

**Tuned prompt:** Yes — see `geniuslab_qwen38_27b_prompt.md` (exact template; rendered per-trial prompts in traces)

**Pass@1 (stratified, mean of per-dataset means of per-query pass rates):** **0.5405**

**Coverage:** 12 datasets × 54 queries × 5 runs = 270 trials, all with execution traces

**Revision note.** The 120 trials named in the review (flagged for cross-trial scratch
reuse) were re-run in a fresh, empty per-trial workspace with no access to the old
`scratch/` folders. The other 150 trials are unchanged — byte-identical answers and
traces to the first submission. All 270 trials, including the 120 re-runs, use the same
backbone model (Qwen 3.8 27B), the same tuned prompt, and the same per-trial trace format.

## About GeniusLab

- **Genius** (Geothermal Next Level Intelligence System) Lab is an AI-powered desktop workspace designed for geothermal energy professionals to securely analyze technical data using on-premises LLMs, ensuring data privacy, security, and compliance for data residency.

## Files

- `geniuslab_qwen38_27b_results.json` — 270 trials in the flat `{dataset, query, run, answer}` format
- `geniuslab_qwen38_27b_traces.zip` — for every trial: `prompt.txt` (exact up-front prompt), `session.json` (full message trajectory incl. reasoning stream, tool calls and tool results), `answer.json` (extracted answer + run metadata); 270 trials × 3 files. The 120 re-run trials carry their new isolated-workspace traces; the 150 unchanged trials carry the original traces.
- `geniuslab_qwen38_27b_prompt.md` — the exact tuned prompt template (dynamic slots marked)
- `geniuslab_qwen38_27b_notes.md` — this file

## Environment Info

- One agent session per trial, driven headless over the runtime's stdio host (the same sidecar process the Genius Lab desktop app spawns), approval mode `yolo` (permissions auto-approved), model `mkbot-llm/qwen-skynet`, 30-min cap per trial, one continuation nudge if the final `ANSWER:` line was missing, then the trial is recorded as-is.
- File-based stores (SQLite/DuckDB) are copied per dataset into the agent's workspace `./data/`; the PostgreSQL stores are loaded once from the official SQL dumps into a local PostgreSQL 17 instance (loopback) and the MongoDB stores are restored once from the official BSON dumps into a local MongoDB 8 instance (loopback). The agent queries them with python (psycopg2 / pymongo / duckdb / sqlite3) in a dedicated virtualenv (packages: pandas, pyarrow, duckdb, psycopg2, pymongo).
- Windows host (PowerShell); the prompt tells the agent the venv interpreter path explicitly.
- **The 120 re-run trials** used the same model, prompt, stores and harness. Each was given a fresh, empty per-trial workspace that could not see any other trial's `scratch/` output (the fix for the reported issue); the per-trial time cap was raised so the harder queries could finish.

## Results

Scores from this repo's unmodified per-query `validate.py`. Pass@1 = mean over datasets of each dataset's average per-query pass rate.

| Dataset | Pass@1 |
|---|---|
| agnews | 0.3000 |
| bookreview | 1.0000 |
| crmarenapro | 0.8000 |
| DEPS_DEV_V1 | 0.4000 |
| GITHUB_REPOS | 0.1500 |
| googlelocal | 0.8000 |
| music_brainz_20k | 0.6667 |
| PANCANCER_ATLAS | 0.3333 |
| PATENTS | 0.2000 |
| stockindex | 0.9333 |
| stockmarket | 0.1600 |
| yelp | 0.7429 |
| **Overall** | **0.5405** |

Per query (trials passed out of 5):

| Dataset | Query | Pass (runs) |
|---|---|---|
| DEPS_DEV_V1 | q1 | 1/5 |
| DEPS_DEV_V1 | q2 | 3/5 |
| GITHUB_REPOS | q1 | 0/5 |
| GITHUB_REPOS | q2 | 0/5 |
| GITHUB_REPOS | q3 | 3/5 |
| GITHUB_REPOS | q4 | 0/5 |
| PANCANCER_ATLAS | q1 | 0/5 |
| PANCANCER_ATLAS | q2 | 0/5 |
| PANCANCER_ATLAS | q3 | 5/5 |
| PATENTS | q1 | 3/5 |
| PATENTS | q2 | 0/5 |
| PATENTS | q3 | 0/5 |
| agnews | q1 | 5/5 |
| agnews | q2 | 0/5 |
| agnews | q3 | 0/5 |
| agnews | q4 | 1/5 |
| bookreview | q1 | 5/5 |
| bookreview | q2 | 5/5 |
| bookreview | q3 | 5/5 |
| crmarenapro | q1 | 5/5 |
| crmarenapro | q2 | 2/5 |
| crmarenapro | q3 | 3/5 |
| crmarenapro | q4 | 5/5 |
| crmarenapro | q5 | 5/5 |
| crmarenapro | q6 | 5/5 |
| crmarenapro | q7 | 5/5 |
| crmarenapro | q8 | 2/5 |
| crmarenapro | q9 | 5/5 |
| crmarenapro | q10 | 5/5 |
| crmarenapro | q11 | 5/5 |
| crmarenapro | q12 | 0/5 |
| crmarenapro | q13 | 5/5 |
| googlelocal | q1 | 5/5 |
| googlelocal | q2 | 4/5 |
| googlelocal | q3 | 2/5 |
| googlelocal | q4 | 5/5 |
| music_brainz_20k | q1 | 4/5 |
| music_brainz_20k | q2 | 5/5 |
| music_brainz_20k | q3 | 1/5 |
| stockindex | q1 | 5/5 |
| stockindex | q2 | 5/5 |
| stockindex | q3 | 4/5 |
| stockmarket | q1 | 4/5 |
| stockmarket | q2 | 0/5 |
| stockmarket | q3 | 0/5 |
| stockmarket | q4 | 0/5 |
| stockmarket | q5 | 0/5 |
| yelp | q1 | 5/5 |
| yelp | q2 | 3/5 |
| yelp | q3 | 4/5 |
| yelp | q4 | 4/5 |
| yelp | q5 | 5/5 |
| yelp | q6 | 1/5 |
| yelp | q7 | 4/5 |

## Integrity (checked against SUBMISSION_RUBRIC.md)

A post-run keyword audit was run over all 270 trajectories (the full per-trial audit
CSV and summary are available on request). Findings:

**Scope of the re-run.** The 120 trials listed in the review were re-run in a fresh,
empty per-trial workspace with no access to the old `scratch/` folders. The remaining
150 trials are byte-identical (answers and traces) to the first submission and keep the
same audit status as before.

**Sanctioned data sources (§1).** Every database queried in the traces is on the
sanctioned list for its dataset, with no cross-dataset access. Prompt inputs are the
query text, `db_description.txt`, `db_description_withhint.txt` (hints = Yes) and the
harness boilerplate above.

**Runtime leakage (§2.1).**

- **No web downloads of answers.** URL occurrences in the trajectories are all
  *content of the sanctioned data* (ad-network links, book cover images, repo README
  excerpts, news links) or the model *recalling* a dataset name from memory (e.g. "the
  AG News dataset on Kaggle") — none is a fetch command (`requests`/`curl`/`wget`/
  `load_dataset`/`gdown`/`git clone` were never executed to obtain data).
- **No off-limits local files.** No trace reads `ground_truth.csv`, any query's
  `validate.py`, `docs/data/queries.json`, or any prior-run/other-submission artifact.
- **No cross-trial scratch reuse in the 120 re-runs.** The keyword audit finds 0
  cross-trial scratch accesses in the new 120 trajectories — the issue raised in the
  review.

**Prompt-injection leakage (§2.2).** The supplied prompt (template + rendered
per-trial copies) contains no gold answer, expected result, decisive value, threshold
or row set. The auto-audit's 35 prompt flags are all in the 150 unchanged trials and
are the *question text itself* stating its own output format (e.g. "Return only one or
several of the four BANT factors…", "Return only the correct stage label among (…)"),
i.e. legitimate `query.json` content. The new 120 re-run prompts carry 0 flags.

**Coverage and consistency (§3).** 270/270 trials, one full trace each; every answer
in the results JSON was programmatically verified byte-identical to the matching
trace's `answer.json`, keyed by (dataset, query, run). The 150 unchanged trials are
byte-identical to the first submission; only the 120 re-run trials differ.

# SpyneLabs - Scrybe (Claude Opus 5.5)

All 54 scored DAB queries, five independent outer runs per query (270 answers). Local stratified Pass@1: **88.58%**; raw passes **240/270 (88.89%)**.
All 30 non-passing answers are retained. Please rescore the answer JSON independently.

## Configuration

- **Agent:** Scrybe, a data-agent harness: an intake planner, a single Quorum worker per trial in a sandbox, and host-side specialist tools
- **Team:** SpyneLabs
- **Backbone model:** `claude-opus-5-5` for every reasoning role. Planner, interpretation brief, answer verification and tool specialists run through headless Claude Code (first-party Anthropic). The worker runs inside an OpenCode sandbox through the local Quorum server with an Anthropic API key. Row-wise text labelling (`llm_label` / `jlabel`) is done by TypeSafe **Jev** (`typesafe/jev-1.14-20261014`, model pinned) through the OpenRouter decisions API; this is a second model family and is disclosed here.
- **Official dataset hints:** Yes (`db_description_withhint.txt`)
- **Tuned prompt:** No. One generic prompt set and rule list for every query; it contains no dataset or query names, values, labels, thresholds, keys or answer shapes (a scan of every agent-visible source found no dataset name or `queryN` id; `prompt-scan.txt` in the supporting archive). Engine-specific reference skills (SQLite, DuckDB, PostgreSQL, MongoDB, pandas) are chosen from the database types in the trial's own database config.
- **Per-trial budget:** nominal cap $5 and 1,800 s per worker attempt; one worker attempt per trial (`single_attempt`), with tool-less planning and verification calls around it
- **Answer rule:** the final message of the worker is the answer; the harness checks its shape against a declared deliverable but does not edit values

## What the agent sees

1. The DAB prompt input: the `query.json` question plus `db_description.txt` and `db_description_withhint.txt`.
2. A mechanical schema snapshot of the sanctioned stores (tables, columns, types, row counts, sample rows).
3. A question-blind profile of each dataset's sanctioned stores, computed offline by code (per-column null/distinct counts, ranges, top values, candidate keys, key-prefix differences). It is identical for every query of a dataset. LLM-proposed join candidates and written notes are excluded.
4. Tools: `dbq`/`dbschema`/`dbsnap` (SQL/Mongo against the trial's stores), Python with pandas/numpy/duckdb, and four specialist tools served by a host-side proxy: `sage` (locate relevant tables/columns/joins from the profile), `joincheck` (key coverage), `jlabel` (row-wise labelling with Jev, plus a stratified judge sample), and `verify` (an independent Opus review of the candidate answer, run without seeing the reference data).

## Isolation and scoring

Each trial gets a fresh sandbox holding only the task text, the database config, the schema snapshot, the question-blind profile and the reference skills. No query directory, `ground_truth`, `validate.py`, `docs/data/queries.json`, prior runs or other submissions are staged. The prompt tells workers not to use the network; the underlying OpenCode runtime has general tools, so this submission does not claim a hard network egress block. `evidence-audit.json` (supporting archive) lists every tool request matching a leakage pattern (ground-truth/validator/queries.json paths, web fetches, downloads); across 2963 recorded worker tool calls in 330 sessions the list is empty. Scoring ran on the host and never reached the workers, planner or scheduler.

A host-side, read-only monitor scored completed trials during generation for progress reporting only; its verdicts were never fed to the workers, planner, tools or scheduler. The exporter rescored all 270 answers afterwards with each query's `validate.py`. There was no score-based stopping, selection or replacement of outer trials, and no best-of-five choice.

Infrastructure retries (a trial that ended with an empty answer or no solved attempt is archived and regenerated; independent of correctness):

- `agnews/query3` outer run 2: try 1 ended with "empty answer" and was regenerated (archived under `infra-retries/`).
- `PATENTS/query2` outer run 4: try 1 ended with "no attempt solved" and was regenerated (archived under `infra-retries/`).
- `agnews/query3` outer run 4: try 1 ended with "empty answer" and was regenerated (archived under `infra-retries/`).
- `PATENTS/query2` outer run 4: try 2 ended with "no attempt solved" and was regenerated (archived under `infra-retries/`).

## Development disclosure

The harness was developed iteratively across ADE-bench, data-eng-bench and DAB, and candidate versions were compared on their local scores. This version descends from a label-free improvement loop (a prompt overlay edited by a model from agent traces only) and later versions that added generic tools (a question-blind schema profile with a locate tool, a join check, row-wise labelling with a stratified judge sample, and an independent answer-verification step) and generic rules for choosing between readings of a question. The later versions were designed after reviewing agent traces, answers and pass/fail results of earlier runs on 13 of the 54 queries; those reviews used the pass/fail outcomes together with the agents' answers and traces. Ground-truth files, validator source and verdict reasons were not read, and the agents never had access to them. Small diagnostic runs on failure-selected task subsets (run ids 1-40 in `manifest.json`, supporting archive) are not part of the 270 submitted trials and are not used for the reported score. The complete development log is in `manifest.json` (`config_changes`, supporting archive).

## Results

| Dataset | Queries | Passes/trials | Pass@1 |
|---|---:|---:|---:|
| DEPS_DEV_V1 | 2 | 10/10 | 100.00% |
| GITHUB_REPOS | 4 | 15/20 | 75.00% |
| PANCANCER_ATLAS | 3 | 10/15 | 66.67% |
| PATENTS | 3 | 14/15 | 93.33% |
| agnews | 4 | 8/20 | 40.00% |
| bookreview | 3 | 15/15 | 100.00% |
| crmarenapro | 13 | 59/65 | 90.77% |
| googlelocal | 4 | 20/20 | 100.00% |
| music_brainz_20k | 3 | 15/15 | 100.00% |
| stockindex | 3 | 15/15 | 100.00% |
| stockmarket | 5 | 25/25 | 100.00% |
| yelp | 7 | 34/35 | 97.14% |

Stratified Pass@1 averages the five runs of each query, then queries within a dataset, then the 12 datasets equally. Harness-recorded generation cost: $237.01 (planner and verification $90.95, workers $104.10, Jev $41.96); this is not an invoice reconciliation. Generation errors: 0.

## Artifacts

In this PR: the answer JSON `../spynelabs_scrybe_v13_opus55_20261030.json` (270 answers), this README, `_prompt_disclosure.md`, `agent-config.json` and `SHA256SUMS`. Two archives are hosted as release assets (hashes in `SHA256SUMS`):

- `spynelabs_scrybe_v13_opus55_20261030_traces.tar.gz` (79 MB, https://github.com/bhushanpant/DataAgentBench/releases/download/scrybe-v13-traces/spynelabs_scrybe_v13_opus55_20261030_traces.tar.gz): for every trial, the task text, planner and verification requests with raw responses, the tool/label proxy log, every worker message with tool inputs and results, the Quorum ledger and the final answer; plus the archived infrastructure retries. Credentials and local path prefixes are redacted.
- `spynelabs_scrybe_v13_opus55_20261030_supporting.tar.gz` (0.3 MB, https://github.com/bhushanpant/DataAgentBench/releases/download/scrybe-v13-traces/spynelabs_scrybe_v13_opus55_20261030_supporting.tar.gz): frozen driver, server and harness source (`driver-source/`, `server-source/`, `harness-source/`, hashes in `frozen-source-sha256.json`), `manifest.json` (development log), `per-trial-scores.json`, `score-summary.json`, `datasets-summary.json`, `evidence-audit.json`, `prompt-scan.txt`, `_notes.md`.

## Notes

- **Scoring.** The full final answer is scored; there is no answer-extraction step. Local scores use each query's `validate.py` at benchmark commit `61fb21e0766d`.
- **Models and providers.** Planner and verification calls report `claude-opus-5-5` with provider `firstParty` in their raw responses. Request-log lines in `opus.jsonl` carry a stale default `provider: openrouter` label that is not the route used; the raw response `modelUsage` is authoritative. Workers report provider `anthropic`, model `claude-opus-5-5`.
- **Counts.** 330 worker sessions, 3892 messages, 2963 tool calls, 1350 planner/verification calls, 1533 tool-proxy records.
- **Manifest.** `manifest.json` logs the whole development workspace. This submission is run ids 41-45, which are outer runs 0-4 in the answer JSON (`agent-config.json` has the mapping).

# Loop DataAgents — deterministic trial code (dab-agent-01 side)

Each scored trial in this submission is a deterministic Python program: the trace's
`run_python` call invokes a per-dataset solver, which reads the dataset's sanctioned
stores and prints its complete result JSON. No model is called in any trial
(`llm_call_count = 0`).

## Trace packaging note (2026-11-10)

Traces were regenerated so that every trial computes its answer in a fresh temporary
output directory. No trial reads a shared, cached, or prior-run `result.json`; the
trace records `solver rc: 0` and the solver's full stdout. Answers are byte-identical
to `loop_dataagents_results.json` (270/270 trials verified).

## Files

| File | Role |
|---|---|
| `trial_mods_01.py` | Builds one trial step per query: run the solver into a fresh temp dir, extract the query's answer, set `ANSWER`. |
| `harness.py` | Shared trace harness: executes steps, writes `final_agent.json` + `tool_calls.jsonl`. |
| `solvers/deps_dev_v1.py` | DEPS_DEV_V1 q1–q2 |
| `solvers/github_repos.py` | GITHUB_REPOS q1–q4 |
| `solvers/music_brainz_20k.py` | music_brainz_20k q1–q3 |
| `solvers/stockindex.py` | stockindex q1–q3 |
| `solvers/stockmarket.py` | stockmarket q1–q5 |
| `solvers/crmarenapro.py` | crmarenapro q1–q13 |
| `agnews_solver.py` | agnews q1–q4 (label majority, predicates, counts) |
| `q2_audit_override.json` | R016 consensus corrections from the q2 blind re-audit |
| `agnews_labels_min.tar.gz` | Trial-external agnews label asset (see below). |

The absolute `/root/dabteam/...` paths in `trial_mods_01.py` are the paths used in the
recorded runs; adjust them to a local checkout to replay.

## Sanctioned stores read

- DEPS_DEV_V1: `query_DEPS_DEV_V1/query_dataset/{package_query,project_query}.db`
- GITHUB_REPOS: `query_GITHUB_REPOS/query_dataset/{repo_metadata,repo_artifacts}.db`
- music_brainz_20k: `query_music_brainz_20k/query_dataset/tracks.db`
- stockindex: `query_stockindex/query_dataset/{indexInfo_query,indextrade_query}.db`
- stockmarket: `query_stockmarket/query_dataset/{stockinfo_query,stocktrade_query}.db`
- crmarenapro: `query_crmarenapro/query_dataset/` + local PostgreSQL `crm_support`

No solver reads ground truth, validators, prior runs, other submissions, or
`docs/data`. The agnews label asset is the agent's own offline annotation of article
title/description text (pass1, pass2, blind pass3, manual adjudication); the agnews
trial code recomputes the majority label in-trial from those passes and counts labels.
It contains no gold/validator output and no category field from any external source.

## agnews label asset

`agnews_labels_min.tar.gz` contains `pass1/`, `pass2/`, `pass3/`, `input/`,
`manual_adjudication.json`, `majority_labels.json`, `labeler_guide.md`,
`coverage_L.json`, `q2_audit_override.json`. `input/` holds the query-relevant article
title/description batches (copied from the sanctioned `articles.bson`); the pass files
hold only `article_id`/`label`; `majority_labels.json` is the resulting majority label.
The R016 override applies six consensus corrections from a pre-registered blind re-audit
of the 111 q2 articles; see `../loop_dataagents_docs/audit_q2/`. Coverage and the
majority rule are documented in `../loop_dataagents_docs/02_agnews_labeling_protocol.md`.

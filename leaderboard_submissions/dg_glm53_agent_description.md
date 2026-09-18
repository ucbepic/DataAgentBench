# DG — Agent Description (DAB Leaderboard Submission)

| Field | Value |
|---|---|
| **Agent name** | DG |
| **Backbone LLM** | GLM-5.3 (full context length), temperature 0.0, served via an OpenAI-compatible gateway |
| **Dataset hints used** | **Yes** — the official `db_description_withhint.txt` content plus a per-dataset playbook prepended to the user query (see "Dataset playbooks" below; this corresponds to the withhint submission track) |
| **Score** | **0.7828** stratified Pass@1 (mean of per-dataset per-query pass rates over 5 runs × 54 queries = 270 trials; missing trials counted as failures) |
| **Framework** | Single-agent ReAct loop (DataGallary agent runtime, max 100 iterations, 2400 s per-trial wall clock) |

## Architecture

DG is a single ReAct-style agent (no sub-agents, no planner/executor split) with these tools per
query: `query_db` / `list_db` (the benchmark's sanctioned database access tools), a Python
execution tool, and a constrained local shell/file toolset operating inside a per-trial
container. All answers are recorded via an explicit `return_answer` tool call; the runner
accepts the last recorded answer.

## Special settings and compliance notes

1. **Deterministic decoding.** temperature = 0.0 for all LLM calls.

2. **Dataset playbooks (hints = Yes).** Each query's user message is prepended with a short
   playbook (≤ ~60 lines) for its dataset covering: output-format conventions (exact values,
   no rounding, list separators, decimal precision), schema quirks of that dataset, and
   analysis-method reminders (e.g., which tables to join, cross-check row counts). The playbooks
   were derived from our own failure analyses on earlier internal runs. **They contain no
   ground-truth values**: every candidate leak identified in an audit (example values matching
   hidden answers, named example rows, exact expected counts) was rewritten to a generalized
   form before the submitted runs.

3. **Runtime network blocking (`DAB_FORBID_NET=1`).** The agent's outbound network access is
   disabled at runtime by a submission-policy patch: `urllib.request.urlopen`, `http.client`,
   `socket.connect`/`create_connection`, and `requests` are blocked except for the LLM gateway
   and localhost services. The block is applied both in-process and in child processes via a
   `sitecustomize.py` interpreter bootstrap, so `execute_python` subprocesses cannot bypass it.
   This prevents fetching external copies of hidden labels (rubric §2.1.1).

4. **Off-limits file guard (rubric §2.1.2).** The shell tool rejects any command that touches
   the benchmark definition/validation tree (`/opt/DataAgentBench`) other than plain directory
   listings, and Python child processes have `open`/`os.listdir`/`os.scandir`/`os.open` audited
   to reject `ground_truth.csv`, `validate.py`, `query.json`, and benchmark config/description
   files. Dataset database files (`.db`/`.sql`, the same stores `query_db` serves) remain
   readable. 10 trials from an earlier pass of the 5-run suite in which the agent did read
   answer/validation files were **discarded and re-run** with these guards active; the
   submitted 270 trials contain no such reads (see traces).

5. **LLM robustness layer (no benchmark information involved).** Whole-call buffered streaming
   retry (mid-stream disconnects/5xx/429 retry the entire call), a reasoning-token cap with a
   relaxed final-attempt budget, and early termination when `return_answer` has recorded an
   answer. These only affect transport/retry behavior and loop termination.

## Reproducibility

- 5 runs, run 0–4, same configuration; each run is one full pass over all 54 leaderboard
  queries. Per-trial results and execution traces are in `dg_glm53_results.json` and
  `dg_glm53_traces.tar.gz` (`dg_glm53_traces/<dataset>/query<N>/trial<R>/final_agent.json`,
  embedding the full agent message history).
- Scoring: strict official convention — mean over the 12 datasets of the per-dataset pass rate
  (mean over its queries of the 5-run pass indicator); trials missing a `final_agent.json` are
  counted as failures. Per-run overall: run0 0.8216, run1 0.7536, run2 0.7781, run3 0.7724,
  run4 0.7883.

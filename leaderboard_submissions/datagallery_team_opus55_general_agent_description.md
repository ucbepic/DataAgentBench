# Agent Description — DataGallery Team - Opus 5.5

> **Tuned Prompt: No.** This submission uses one general-purpose data-agent prompt, unchanged across all 270 runs. It does not use a DAB-specific tuned prompt.
>
> **Hints: Yes.** The official `db_description_withhint.txt` files were used. Under the DAB leaderboard definition, using official hints is reported separately from prompt tuning and does not by itself make the prompt tuned.

## Configuration

- **Team / agent name:** DataGallery Team - Opus 5.5
- **Agent type:** single ReAct planner/executor loop using a LangGraph backend; no sub-agents or master-worker delegation
- **Backbone model:** `claude-opus-5-5`, used for every model step
- **Tuned Prompt:** **No — general-purpose prompt**
- **Dataset hints used:** Yes (`db_description_withhint.txt` for every dataset)
- **Prompt profile:** `lean_prompt_v1.1` for all 270 runs
- **Maximum iterations:** 100
- **Runs:** 5 consecutive trials per query across all 54 queries
- **Execution:** 12-way dynamic-refill parallelism with a 3600-second per-query timeout
- **Network:** outbound network access from the execution sandbox was blocked; database tools could access only the configured local benchmark stores

The included agent configuration contains the common task instructions. The exact prompt and conversation executed for each run are preserved in that run's `final_agent.json`.

## Why Tuned Prompt is No

The [DAB leaderboard](https://github.com/ucbepic/DataAgentBench#leaderboard) defines a tuned prompt as an up-front prompt that is DAB-specific and built around DAB task conventions, including domain rules, parsing or interpretation choices, or expected answer shapes.

This submission does not provide those DAB-specific prompt inputs:

- **No DAB-specific domain rules:** no benchmark dataset facts, business rules, keys, denominators, thresholds, labels, or expected values are supplied by the common prompt.
- **No DAB-specific parsing or interpretation choices:** the prompt does not tell the agent how to interpret or solve any DAB query. It contains only general instructions to inspect source data and validate transformations.
- **No DAB-specific expected answer shapes:** the prompt contains one generic typed-table tool protocol, used unchanged for every task. It does not provide query-specific columns, rows, ordering, candidate answers, or output schemas.
- **No dataset/query-specific branches:** every run uses the same `lean_prompt_v1.1` common instructions.
- **No auxiliary prompt knowledge:** there is no external evidence catalog, cached data profile, retrieval/ranking system, selector model, semantic service, or second LLM.

Therefore this submission is explicitly submitted as **Tuned Prompt = No**. Official dataset hints remain disclosed separately as **Hints = Yes**.

## Prompt inputs

All 270 runs used the same common task instructions. The task-varying prompt material was limited to:

- the query text;
- the official database description;
- the official dataset hints.

No author-provided dataset profile, query note, methodology note, candidate answer, or precomputed result was added to an individual task prompt. See the included prompt-disclosure document for the mechanical consistency check and disclosure scope.

## Toolset

| Tool | Role |
|---|---|
| `list_db` | On-demand schema and sample-row profiling of a configured database |
| `query_db` | SQL or MongoDB queries against configured databases |
| `execute_python` | Python analysis with in-process, read-only access to the configured databases |
| `read_file` / `write_file` | Files under the run workspace (`/tmp_workspace`) |
| `submit_result` | Typed-table result delivery through `result.json` |

Joins, extraction, aggregation, and validation of intermediate computations were performed at runtime through `query_db` and/or `execute_python` over the configured stores. The agent could call `list_db` when it needed schema or sample-row inspection.

## Results

- **Macro Pass@1:** `0.888644688645` over 12 datasets (`0.8886` rounded to four decimal places)
- **Coverage:** 270 runs = 54 queries × 5 trials

## Trace contents

The release trace archive contains, for every run:

- `final_agent.json`, including the executed prompt, agent messages, tool calls, and final result;
- `tool_calls.jsonl`;
- container stdout and stderr logs.

**Submission classification: Tuned Prompt = No; Hints = Yes. The Agent prompt is general-purpose, not DAB-specific.**

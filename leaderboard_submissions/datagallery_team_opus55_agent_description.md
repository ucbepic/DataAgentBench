# DataGallery — Agent Description (Claude Opus 5.5)

## Submission summary

| Field | Value |
|---|---|
| Agent | DataGallery (Claude Opus 5.5) |
| Team | DataGallery Team |
| Backbone model | `claude-opus-5-5` (Opus-5.5) |
| Trials | 5 per query; 54 queries; 270 trials total |
| Dataset hints | Yes — official `db_description_withhint.txt` content was used |
| Highly tuned prompt | **Yes** |
| Local stratified Pass@1 | **0.95609** |
| Runtime network policy | `DAB_FORBID_NET=1` |

The score above is a local re-score with the official validators. It is not
described as an official leaderboard score until the DAB maintainers reproduce
and accept it.

## Architecture and tools

The agent uses a single ReAct loop with no checker/repair loop and no
self-consistency voting. The configuration registers seven tools:

- database access: `list_db`, `query_db`, `execute_python`;
- result delivery: `submit_result`, with `return_answer` as an emergency fallback;
- workspace access: `read_file`, `write_file`.

The exact submitted configuration and prompt are included in
`datagallery_team_opus55_agent_config.yaml`.

## Prompt profile

This is a highly tuned, DAB-specific prompt. It contains:

1. dataset-agnostic workflow and verification instructions;
2. a `DATABASE SEMANTICS` annex containing pre-profiled storage facts from the
   sanctioned benchmark databases;
3. a `BENCHMARK READINGS` section containing DAB-specific interpretation
   conventions, including aggregation-grain rules, compliance-policy selection,
   category boundaries, tie handling, and an equal-class-balance constraint for
   broad content-classification tasks;
4. a typed-table output contract.

## Scoring provenance

Local validation produced the following stratified scores:

| Run | Score |
|---:|---:|
| 0 | 0.972756 |
| 1 | 0.951923 |
| 2 | 0.951923 |
| 3 | 0.951923 |
| 4 | 0.951923 |
| Overall | **0.95609** |

The result file contains all 270 `dataset × query × run` entries. Every submitted
answer is byte-identical to the corresponding trace's `final_result`.

## Trace packaging and hygiene

- The archive contains all 270 run directories and their `final_agent.json`,
  `tool_calls.jsonl`, container stdout, and container stderr files.
- Packaged traces contain no `ground_truth` or `is_valid` fields and no
  `validation.jsonl` files.
- A package scan found no reads of `ground_truth.csv`, `ground_truth.txt`,
  query `validate.py`, prior submissions, or leaderboard result artifacts.

## PR files

- `datagallery_team_opus55.json` — leaderboard answers;
- `datagallery_team_opus55_traces.tar.gz` — complete execution traces;
- `datagallery_team_opus55_agent_description.md` — agent description;
- `datagallery_team_opus55_agent_config.yaml` — exact agent configuration and prompt.

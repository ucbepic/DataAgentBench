# YouData Data Agent — DAB Leaderboard Submission

| Field | Value |
|---|---|
| **Agent name** | YouData Data |
| **Backbone LLM** | DeepSeek V4.1 Flash |
| **Dataset hints used** | **Yes**  |
| **Tuned prompt** | **Yes**  |
| **Trials** | 5 runs × 54 queries = 270 trials |
| **Official Pass@1** | **0.8554** (12-dataset equal-weight mean; 229 / 270 = 0.8481 overall) |
| **Framework** | [YouData](https://youdata.163.com/) |

## Architecture

The submission uses twelve dataset-specific YouData assistants, one for each DAB dataset.
Each assistant is a single ReAct-style data agent with the platform's SQL, Python and file
analysis tools. The agent receives:

1. the official database description;
2. the official hints (`db_description_withhint.txt`);
3. dataset-level schema and analysis conventions;
4. a common harness/answer-format block.

Benchmark data is isolated between assistants. Each assistant was provisioned only with
the sanctioned stores for its own dataset and could not use another dataset's stores or a
shared cross-dataset connection. The assistants share only the platform runtime and
backbone model. The exact prompts are recorded in
[youdata_data_agent_system_prompts.md](youdata_data_agent_system_prompts.md).

## Clean rerun note

Following review feedback on cross-run workspace contamination, `stockmarket` query 2 runs
0-2 were rerun in isolated workspaces with the same assistant configuration (prompt, model,
resources, and tool-call limit). The rerun traces contain no references to prior dialog
directories or assistant-level `.claude/projects` session logs. All three reruns passed the
official validator.


## Data access

For this experiment, every sanctioned store was imported one-to-one into PostgreSQL schemas
with the original table and column names. The import was verified at schema/table/row level:
**43 schemas, 0 anomalies**. This is a storage translation only; no extra source data was
added.

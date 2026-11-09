# Alibaba QwenPaw-Data powered by qwen3.8-max

QwenPaw-Data is an agentic system developed by Alibaba Group designed for autonomous enterprise data analysis and business intelligence.

## Core Agent Configuration

- **Agent system:** Alibaba QwenPaw-Data.
- **Backend Model:** qwen3.8-max by DashScope, with thinking enabled.
- **System Prompt (Tuned Prompt: No):** A single generic system prompt is used by all queries in all runs. It is based on the DataAgentBench baseline prompt, plus descriptions of the harness mechanisms (schema profile, planning tools, time budget) and generic reporting rules. It contains no text about any specific query and no query-specific interpretation rules. The full text is given below.
- **User Input (Hints: Yes):** A user input to the agent consists of the content from query.json, db_description.txt and db_description_withhint.txt of the benchmark codebase. Nothing else is added to the user input.
- **Tools:** ListDBTool, QueryDBTool, ExecTool and ReturnAnswerTool from the DataAgentBench codebase, plus GetSchemaTool, PlanCreate and TaskStateUpdate of our own. No other tool is registered. ExecTool runs arbitrary Python in the sandbox.

## Agent Capabilities

1. **Data profiling.** GetSchemaTool returns a live profile of each database: row counts, the complete set of field names, types, low-cardinality values, numeric/date min-max, and whether id fields contain duplicates. The same profile is also provided once right after the question, so the agent starts from the real structure and contents of the data rather than assumptions about it.
2. **Planning.** With PlanCreate and TaskStateUpdate, the agent breaks the question into an ordered plan of lookups and calculations and tracks the progress of each step. The current plan is shown to the model at every reasoning step, and a runtime reminder reports the elapsed time against the time budget, so the agent stays on track to a complete answer within the time limit.
3. **Sandboxed execution.** Each query runs in a fresh sandbox with no Internet access and no state from other sessions. Ground truth, validate.py and other runs' artifacts are not in it.
4. **Consistent prompt.** The prompt is internally consistent from start to end: every rule points the same way, and no instruction conflicts with another, so the agent never has to choose between competing directions.

## Runtime Configuration

- **Hardware:** Two 96-core servers with 376GB of memory each, running up to 28 queries in parallel per server, and one 8-core Mac with 16GB of memory running up to 4.
- **Timeout:** Each query run has a 2-hour time budget.
- **Data access:** Answers are derived only from the sanctioned stores of each dataset. The ground truth, validate.py, and other runs' or submissions' artifacts do not exist in the agent's environment; answers are validated outside it.

## Runtime Hints

Besides the system prompt and the user input, the harness adds exactly three kinds of content to the agent context:

- `**<current_plan>…</current_plan>**`, appended to the end of the system prompt at each reasoning step once a plan exists. It lists the task ids, states and subjects that the agent itself wrote with PlanCreate and TaskStateUpdate, whose calls are in the traces.
- `**<schema-profile>…</schema-profile>**`, given once after the question as a message with `"type": "hint"` and `"metadata": {"source": "dab_runtime"}` in the traces.
  - It is the GetSchemaTool output for all databases of the dataset, i.e. ordinary profiling of the sanctioned data.
  - It is computed only from that dataset's sanctioned stores and does not depend on the query. It contains nothing about the question, the expected answer, or any interpretation choice.
  - Its full text is in every trace.
- `**<time-budget>elapsed Em of 120m</time-budget>**`, a message of the same kind before each reasoning step. After 80% of the budget it ends with "Return your best answer soon." Only the latest one is kept in the context.

## System Prompt

```
You are a data analysis agent. Use only the tools listed below to answer the user's query, based on the provided DATABASE DESCRIPTION for logical database names and their types (SQL or MongoDB), the SCHEMA PROFILE of the live dump, and the results of previous tool calls.

TOOLS (system will execute):
- QueryDBTool: run a SQL query or a MongoDB find query. Returns JSON with `n` (row count), `path` (absolute path of a JSON file holding the full result, for ExecTool to open), and `preview` (first 20 records).
  Required args: {"db_name": "<logical_db_name>", "query": "<SQL or Mongo query>"}
  A MongoDB query is a JSON object with `collection` (required) and optional `filter`, `projection`, `sort` ({"field": 1 or -1}), `skip`, and `limit`. Without `limit`, every matching document is returned. Aggregation pipelines are not supported.
- ListDBTool: list tables or collections for a given database.
  Required args: {"db_name": "<logical_db_name>"}
- GetSchemaTool: return a live schema profile (row counts, field_names, types, low-cardinality values, min/max, duplicate ids). field_names is the complete live column set; a concept not listed is not stored.
  Required args: {"db_name": "<logical_db_name>"}
- ExecTool: run Python code.
  Required args: {"code": "<python_code>"}
- PlanCreate: before looking up or computing, write the question's implied lookups and calculations as an ordered plan, then follow it.
  Required args: {"tasks": [{"id": "<id>", "subject": "<short step>", "description": "<what to look up or compute>"}]}
- TaskStateUpdate: mark one plan step pending, in_progress, or completed.
  Required args: {"task_id": "<id>", "state": "pending|in_progress|completed"}
- ReturnAnswerTool: finish and return the final answer (plain text).
  Required args: {"answer": "<final plain-text answer>"}

KEY RULES (must follow exactly):
1. Always use tool calls. Do not output plain text, explanations, or reasoning.
2. Include all required arguments for the tool you call.
3. For QueryDBTool, always specify db_name and query. Refer to the DATABASE DESCRIPTION for db_name and query format.
4. For PostgreSQL, wrap mixed-case or uppercase column names in double quotes.
5. For ListDBTool and GetSchemaTool, refer to the DATABASE DESCRIPTION to specify db_name. The SCHEMA PROFILE provided after the question is from the live dump; treat it as authoritative. GetSchemaTool refreshes it.
6. Use ExecTool for data processing as needed.
7. When using ExecTool, your code will be quoted by triple double-quotes and passed as a string to `exec(...)` for execution in a Python 3.12 environment with only pandas and pyarrow installed. So you must ensure your code is compatible with this execution method. For example, do not use triple double-quotes in your code, as they may interfere with parsing. Do not use non-built-in or non-installed packages.
8. Each ExecTool call runs in a fresh process; variables do not persist. Save intermediate results as files in the current working directory and reload them in later calls.
9. When using ExecTool, your code must print the result at the end exactly as shown in the PRINT FORMAT section below. The printed result must be a string that can be successfully parsed by json.loads() without errors.
10. Category labels and join keys must come from the data in the databases or be derived from it. Do not rely on remembered public dataset layouts, id ranges, splits, or label schemes.
11. The environment has no internet access, and nothing outside the databases and your working directory is relevant — do not try to download data or browse other directories.
12. Runtime reminders report the elapsed time and the time budget. Whatever happens, call ReturnAnswerTool with the best answer you have before the time budget runs out; never return an explanation instead of an answer.
13. Return the final answer only via a single ReturnAnswerTool tool call. Do not include extra text, explanation, or formatting.

PRINT FORMAT (must match exactly):
----BEGIN PRINT FORMAT----
print("__RESULT__:")
print(your_json_serializable_string_here)
----END PRINT FORMAT----

For simple types (int, float, str, bool, None), you may use json.dumps() to produce a valid JSON string.
For complex or non-JSON-serializable types, you must convert them into JSON-compatible forms before printing.
For lists or dictionaries, you must ensure that all nested elements are also converted into JSON-serializable types.

EXAMPLES:
- QueryDBTool:
{"tool": "QueryDBTool", "args": {"db_name": "some_db_name", "query": "SELECT * FROM some_table LIMIT some_limit;"}} # for SQL databases
{"tool": "QueryDBTool", "args": {"db_name": "some_db_name", "query": "{\"collection\": \"some_collection\", \"filter\": {some_filter}, \"projection\": {some_projection}}"}} # for MongoDB databases

- ListDBTool:
{"tool": "ListDBTool", "args": {"db_name": "some_db_name"}}

- GetSchemaTool:
{"tool": "GetSchemaTool", "args": {"db_name": "some_db_name"}}

- ExecTool:
{"tool": "ExecTool", "args": {"code": "import json, pandas as pd\n# path is the `path` field from a QueryDBTool result\nrows = json.load(open(path))\ndf = pd.DataFrame(rows)\nresult = df.head(10).to_json(orient='records')\nprint('__RESULT__:')\nprint(result)"}}

- ReturnAnswerTool:
{"tool": "ReturnAnswerTool", "args": {"answer": "…final plain-text answer…"}}

Do not output explanations, reasoning, or any natural language outside of the required tool calls.


When dealing with data coming out from database, keep the original data encoding, especially for the non-ascii letters.

When using a database table column for filtering, joining, or sorting, do necessary data profiling on the data of that column, to understand the nature of the data, such as format, etc.

When returning or displaying the output of ReturnAnswerTool, return or display the complete output content, do not truncate the content. Return the output content in English language only, do not use any other language.

REPORTING DISCIPLINE (apply when you answer):
1. Answer exactly what the question asks, in the form the question itself implies. If it asks for a single value, return only that value — no explanation, no extra fields. If it asks for multiple records or columns, return each record on its own line with comma-separated fields, in the order the question lists or implies them, with no header and no prose unless the question asks for them.
2. Report the precise value you computed — do not round, rescale, or reformat it, and keep whatever units, basis, or framing the question uses. If the question asks for a share or ratio, decide from the question's own wording (and any examples it gives) whether a decimal, fraction, or percentage is expected; when the question leaves it open, prefer the unrounded decimal.
3. If the answer is a list of items, include EVERY matching item: never truncate, never output 'the top N' or '...' in place of the items, and never replace the items with a count of them. Verify the item count matches your query result before returning.
4. Copy names, titles, identifiers, and codes verbatim from the query results — never abbreviate, truncate, or paraphrase them.
5. Compute every count, ratio, sum, average, or ranking with ExecTool over the full queried rows — never estimated or counted by hand.
6. Never return a restatement of the question as the answer.
```

## Submission Materials

There are 3 files in this submission.

- This description md
- A result json file containing a json array of 270 json objects (5 runs * 54 queries).
- A traces .tar.gz file containing 270 json files, organized as `<trace_root>/run_<k>/query_<dataset>/query<id>/trace.json`. They match the answers in the result json file: each answer is the argument of the last ReturnAnswerTool call in its trace. Each trace has `user_input` (the user input event), `mcp_connections` (empty; no MCP is used) and `messages` (the full agent context: hints, model reasoning, tool calls and tool outputs, in order).
- One run, `run_0/query_agnews/query4`, hit the 2-hour time budget before calling ReturnAnswerTool and no trace was saved, so this trace file is a placeholder with a note; its answer is empty and counts as wrong.


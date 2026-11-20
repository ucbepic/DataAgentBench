# QwenPaw-Data Agent powered by claude-opus-5-5

QwenPaw-Data is an agentic system developed by Alibaba Group designed for autonomous enterprise data analysis and business intelligence.

## Agent ID
Please use "Alibaba QwenPaw-Data" as the agent name should this be put on to the leaderboard.

## Core Agent Configuration
- **Agent system:** QwenPaw-Data Agent.
- **Backend Model:** claude-opus-5-5 by Anthropic.
- **Tuned Prompt:** No
- **Hints:** Yes
- **System Prompt:** A single generic system prompt is designed. It is used by all queries in all the runs. This prompt consists of the tool description portion of the prompt in DAB codebase, plus some generic rules for data processing. It is NOT tuned for any specific query. It does not contain text regarding any of the queries.
- **User queries with database hint applied:** A user input to the agent consists of the content from query.json, db_description.txt, db_description_withhint.txt. Nothing else is added to the user input.
- **Tools:** We only use the 4 tools provided in the DataAgentBench codebase to work with our agent. No other tool is used. These 4 tools are ListDBTool, QueryDBTool, ExecTool, and ReturnAnswerTool. We only made minimal changes to make them work with our agent tool call protocol. The functional code of these tools is not changed.

## Runtime Configuration
- **Hardware:** A 32-core CPU server with 192GB of memory.
- **Docker:** QwenPaw-Data agent is built into a docker image. It runs in up to 8 containers to process the queries in parallel.
- **Timeout:** Each query run has a 2-hour timeout limit.
- **Benchmark DB data access:** Agent is able to access the database files provided by benchmark via the listed tools.
- **Cleaned image and containers:** The ground truth, validate.py, all sample data and documents in the DataAgentBench codebase do not exist in the image and do not exist in the container environment.
- **Internet Access:** Agent process in a container is able to access Internet to call Claude model. In our runs Agent did not write or run script via ExecTool to search for or download data online, as verified in the traces.
- **Query set run:** One query set run is defined as the process of processing all the 54 queries of the 12 query sets. This submission contains the results of 5 complete runs.

## System Prompt
> - The text from the beginning up to the "KEY DATABASE ANALYTICS RULES" section is copied from the DataAgentBench codebase. It is the original generic prompt text.
>
> - Starting from the "KEY DATABASE ANALYTICS RULES" section are the generic rules for data access and data processing.
>
> - This same prompt is used by our agent to answer all queries.

You are a data analysis agent. Use only the tools listed below to answer the user's query, based on the provided DATABASE DESCRIPTION for logical database names and their types (SQL or MongoDB), and the results of previous tool calls.

TOOLS (system will execute):
- QueryDBTool: run a SQL or Mongo query. Returns a list of JSON-serializable records or an error string.
  Required args: {"db_name": "<logical_db_name>", "query": "<SQL or Mongo query>"}
- ListDBTool: list tables or collections for a given database.
  Required args: {"db_name": "<logical_db_name>"}
- ExecTool: run Python code.
  Required args: {"code": "<python_code>"}
- ReturnAnswerTool: finish and return the final answer (plain text).
  Required args: {"answer": "<final plain-text answer>"}

KEY RULES FOR USING TOOLS (must follow exactly):
1. Always use tool calls. Do not output plain text, explanations, or reasoning.
2. Include all required arguments for the tool you call.
3. For QueryDBTool, always specify db_name and query. Refer the DATABASE DESCRIPTION for db_name and query format.
4. For PostgreSQL, wrap mixed-case or uppercase column names in double quotes.
5. For ListDBTool, refer the DATABASE DESCRIPTION to specify db_name.
6. Use ExecTool for data processing as needed.
7. When using ExecTool, your code will be quoted by triple double-quotes and passed as a string to `exec(...)` for execution in a Python 3.12 environment with only pandas and pyarrow installed. So you must ensure your code is compatible with this execution method. For example, do not use triple double-quotes in your code, as they may interfere with parsing. Do not use non-built-in or non-installed packages.
8. When using ExecTool, your code must print the result at the end exactly as shown in the PRINT FORMAT section below. The printed result must be a string that can be successfully parsed by json.loads() without errors.

PRINT FORMAT (must match exactly):
----BEGIN PRINT FORMAT----
print("__RESULT__:")
print(your_json_serializable_string_here)
----END PRINT FORMAT----

For simple types (int, float, str, bool, None), you may use json.dumps() to produce a valid JSON string.
For complex or non-JSON-serializable types, you must convert them into JSON-compatible forms before printing.
For lists or dictionaries, you must ensure that all nested elements are also converted into JSON-serializable types.
9. Return the final answer only via a single ReturnAnswerTool tool call. Do not include extra text, explanation, or formatting.

TOOL EXAMPLES:
- QueryDBTool:
{"tool": "QueryDBTool", "args": {"db_name": "some_db_name", "query": "SELECT * FROM some_table LIMIT some_limit;"}} # for SQL databases
{"tool": "QueryDBTool", "args": {"db_name": "some_db_name", "query": "{\"collection\": \"some_collection\", \"filter\": {some_filter}, \"projection\": {some_projection}, \"limit\": some_limit}"}} # for MongoDB databases

- ListDBTool:
{"tool": "ListDBTool", "args": {"db_name": "some_db_name"}}

- ExecTool:
{"tool": "ExecTool", "args": {"code": "import pandas as pd\n# rl1 and rl2 are the keys of two JSON-serializable record lists in storage\ndf1 = pd.DataFrame(rl1)\ndf2 = pd.DataFrame(rl2)\nresult = pd.merge(df1, df2, on='id').head(10).to_json(orient='records')\nprint('__RESULT__:')\nprint(result)"}}

- ReturnAnswerTool:
{"tool": "ReturnAnswerTool", "args": {"answer": "…final plain-text answer…"}}

If you cannot proceed, call ReturnAnswerTool with a short explanatory message.

Do not output explanations, reasoning, or any natural language outside of the required tool calls.

KEY DATABASE ANALYTICS RULES:
- Check and understand the actual database table schema before using the table.
- When using database table columns for filtering, joining, or sorting, do necessary data profiling to understand the nature of the data, such as the meaning of the column and the format of the data, etc.
- When dealing with data in database, keep the original data encoding, do not change it.

KEY DATA PROCESSING RULES
- When an answer entry consists of multiple attributes that are required by the question, put these attribute values next to each other, do not add other attributes that are not required by the question.
- When feeding the final answer to the ReturnAnswerTool, make sure the answer clean and concise, providing only what the question asked for, and do not put reasoning information and context information in the answer.
- When returning or displaying the output of ReturnAnswerTool, return or display the complete output content, do not truncate the content. Return the output content in English language only, do not use any other language.
- When creating temporary folders or files, put a unique id in the folder name or file name, to avoid accessing temporary files of other queries by mistake.
- When dealing with numbers, keep their precise values to prevent loss of precision.

## User Input
Each query is presented as a user input text to the agent. This input contains
- the query,
- db description,
- db description with hints text

They are from the original query, db_descrition, db_description_withhint files of the benchmark codebase. No other text exists in each query.

## Submission Materials
There are 3 files in this submission.
- This description md
- A result json file containing a json array of 270 json objects (5 runs * 54 queries).
- A trace.tar.gz file contains 270 json files, organized in the structure of /trace_root/run_id/query_set/query_id/trace.json. They match to the answers in the result json file. Note this .tar.gz file is large because some of the trace files contain a large amount of tool data. The extracted folder is about 3.6GB in size.

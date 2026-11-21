# MindsHub Cowork (Claude Opus 5.5)

- Agent name: MindsHub Cowork
- Team: MindsDB
- Backbone LLM: `claude-opus-5-5` for planning, code and every LLM call the agent's code makes
- Planning reasoning effort: high
- Coding reasoning effort: high
- Hints used: yes (`db_description.txt` followed by `db_description_withhint.txt`, as `run_agent.py` builds it)
- Tuned prompt: no (the agent's production system prompt)
- Runs per query: 5 (54 queries, 270 runs)
- DataAgentBench commit: `bcc2e1b06c708abfde5fa3c69e1e4e514eaaf716`

## Components

MindsHub Cowork is an open-source AI agent made of three parts:

- [anton](https://github.com/mindsdb/anton): the agent. It plans, writes SQL and Python, runs the code in a separate Python process ("scratchpad") and checks its answer before replying.
- [cowork-server](https://github.com/mindsdb/cowork-server): the server that runs the agent, keeps chats and holds the database connections.
- [cowork](https://github.com/mindsdb/cowork): the desktop and web user interface. Not used in this run: the harness talked to cowork-server directly.

| Component | Version | Commit |
|---|---|---|
| anton | 2.26.11.3.2rc6 | `06c27db87631977413788bff2d8a6cc35e4d2948` |
| cowork-server | 0.26.11.3.2rc7 | `4474112a26b6ce771b7adf64e2ef2abb1232866f` |

## Settings

- Each run is a new chat with a fresh agent session. The prompt is the question from `query.json`, the list of the dataset's databases, the database description with hints, and one answer-format line asking for a final `FINAL ANSWER: <answer>` line. The submitted answer is the text after `FINAL ANSWER:`.
- Only the connections of the current dataset are enabled in a run: PostgreSQL and MongoDB through a read-only user, SQLite and DuckDB as read-only copies of the benchmark files.
- Web search, web fetch and internet research: off. Agent memory: off.
- Before replying, the agent runs a completion check with the coding model.
- 5 runs at a time. No run timed out or ended with an error.

## Notes

- In 22 runs (agnews queries 1-4, yelp queries 4 and 7) the agent's code called the LLM (`get_llm()`) on text it read from the sanctioned stores.
- The scratchpad tool installs the Python packages the agent asks for from PyPI (`uv pip install`): database drivers and common libraries such as `duckdb`, `pandas`, `psycopg2-binary`, `pymongo`.

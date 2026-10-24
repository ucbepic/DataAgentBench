# Genius Lab — DAB tuned prompt (exact template)

The prompt below is the complete, verbatim up-front user prompt sent to the agent for
every trial. `{{...}}` marks the dynamic slots; everything else is byte-identical across
all 270 trials. The fully rendered prompt for each trial is also in `traces.zip`
(`traces/<dataset>/query<N>/run_M/prompt.txt`), so this template can be diffed against
the actual sends.

Composition (per SUBMISSION_RUBRIC.md §1, "Legitimate prompt inputs"):

1. the query's `query.json` question text — `{{question}}`
2. `db_description.txt`, with `db_description_withhint.txt` appended verbatim
   (hints used = Yes) — `{{db_description}}`
3. standard harness boilerplate: how to open the sanctioned stores, the python
   environment, the required `ANSWER:` line
4. a DAB-specific tuned conventions section (task conventions / answer shapes only —
   no decisive value, label, threshold, row set, or interpretation choice for any query)

---

## Template

```
You are a data analysis agent solving one benchmark task. All the data you need is in your current workspace.

=== TASK ===
{{question}}

=== DATABASE DESCRIPTION ===
{{db_description}}

=== WORKSPACE & DATA ACCESS (harness boilerplate) ===
Your workspace layout:
- Data: {{data_dir}} — the database files for this task. This is the ONLY data you may use.
- Scratch: {{scratch_dir}} — an empty directory for your own intermediate files (scripts, CSVs, dumps). Put ALL your working files here.

Store locations (logical name from the description -> actual store):
{{store_lines}}

Python interpreter: {{python_exe}}
Installed packages: pandas, pyarrow, duckdb, psycopg2, pymongo (sqlite3 is built-in).
Run code as: "{{python_exe}}" -c "..."  or write scripts under the scratch dir and run them.
You are on Windows (PowerShell). The default python on PATH is NOT suitable — always use the full interpreter path above.

Rules of the environment:
- Use ONLY the data under the data directory above. Do not read files outside your workspace and do not download or fetch data from the internet.
- Keep all queries read-only; do not modify the data stores.

=== ANSWER FORMAT (must follow exactly) ===
When you are done, your LAST message MUST end with the exact line
ANSWER: <your final answer as plain text>
with nothing after the answer on that line.

Answer-format conventions:
- Plain text only (no markdown tables, no code fences, no explanations on that line).
- Keep the whole answer on that single line: if it is a list of items, join the items with "; " and preserve each item's exact text.
- Keep each key adjacent to its own value (e.g. "key: value" pairs), never split keys and values across far-apart columns.
- If the question asks for a number, give the exact number (full precision unless a rounding is requested).
- Answer exactly what is asked (which/how many/ordering/units) — re-read the question before writing the line.

=== RECOMMENDED APPROACH ===
1. Explore before querying: list tables/collections, inspect columns, row counts, and sample/distinct values of the columns you will join or filter on.
2. Enterprise data is often messy: keys can carry stray whitespace, case variants, or "#"-prefixed / "Name (Label)" formats — profile distinct key values and normalize consistently on BOTH sides of a join.
3. Verify intermediate results (counts, spot-checks of joined rows) before composing the final answer.
4. If a result looks suspicious (empty joins, off-by-one filters, duplicates), diagnose and fix before answering.
```

## Slot formats

- `{{question}}` — the full text of `query_<dataset>/query<N>/query.json` (a JSON string).
- `{{db_description}}` — the full text of `query_<dataset>/db_description.txt`, followed
  by a blank line and the full text of `query_<dataset>/db_description_withhint.txt`
  (hints used = Yes; this is how the benchmark's own `--use_hints` runner composes it).
- `{{store_lines}}` — one line per sanctioned store of the dataset, in this format
  (example, crmarenapro):
  ```
  - "core_crm" -> SQLite file {{data_dir}}\core_crm.db  (open with the sqlite3 stdlib module or duckdb.read_sqlite("{{data_dir}}\core_crm.db"))
  - "sales_pipeline" -> DuckDB file {{data_dir}}\sales_pipeline.duckdb  (open with duckdb.connect("{{data_dir}}\sales_pipeline.duckdb", read_only=True))
  - "support" -> PostgreSQL database "crm_support" on 127.0.0.1:5432 (psycopg2, user=postgres, password=*** dbname=crm_support) — read-only
  - "products_orders" -> SQLite file {{data_dir}}\products_orders.db  (open with the sqlite3 stdlib module or duckdb.read_sqlite("{{data_dir}}\products_orders.db"))
  - "activities" -> DuckDB file {{data_dir}}\activities.duckdb  (open with duckdb.connect("{{data_dir}}\activities.duckdb", read_only=True))
  - "territory" -> SQLite file {{data_dir}}\territory.db  (open with the sqlite3 stdlib module or duckdb.read_sqlite("{{data_dir}}\territory.db"))
  ```
  (MongoDB stores use: `- "<logical>" -> MongoDB database "<name>" at mongodb://127.0.0.1:27017 (pymongo)`.)
- `{{python_exe}}` — absolute path of the per-run virtualenv interpreter
  (Windows), e.g. `.../runs/<trial>/env/venv/Scripts/python.exe`.
- `{{data_dir}}` / `{{scratch_dir}}` — per-trial absolute Windows paths.


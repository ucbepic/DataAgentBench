# Oracle Forge Agent

## Architecture Overview

Oracle Forge is an orchestrated data-agent runtime for DataAgentBench. It combines:

- an orchestrator that owns the turn lifecycle
- a planner that infers query shape and required sources
- layered context retrieval
- execution routing across available database paths
- validation and repair
- answer synthesis
- experience logging and memory promotion

## Key Design Decisions

- Hybrid runtime:
  Toolbox is present for PostgreSQL, SQLite, and MongoDB, while benchmark-critical DuckDB access currently flows through the remote DAB path.
- Benchmark-first execution:
  The current runtime prioritizes verified end-to-end benchmark execution over premature interface uniformity.
- Layered context:
  The agent separates reusable rules, project memory, schema hints, join-key knowledge, text-field hints, and episodic recall.

## Tool Scoping & Connection Declarations

To handle the DataAgentBench environment, the agent tools are specifically scoped and configured to access all four DAB databases:
- **PostgreSQL (`mcp_postgres_query`)**: Scoped to retrieve and normalize structured transactional data. Connected directly via the shared server database layer using `psycopg2`.
- **SQLite (`mcp_sqlite_query`)**: Scoped for querying cached local metric tables. Connected locally via standard `sqlite3` bindings mapped to the benchmark's internal paths.
- **MongoDB (`mcp_mongodb_find`)**: Scoped specifically for retrieving unstructured document records (e.g., Yelp business reviews or JSON logs). Configured via standard `pymongo` connection strings in `tools.yaml`.
- **DuckDB (`mcp_duckdb_query`)**: Scoped for fast analytical aggregations on flat parquet or denormalized tables. Connected natively for fast OLAP tasks before synthesization.

## Context Layer Population & Reading

Our 3-Layer context architecture avoids context window bloat by strictly separating and conditionally injecting data:
1. **Global/Architecture Memory (`kb/architecture`)**: Contains overarching agent behavior rules and execution constraints.
   * *How it is populated*: Hardcoded directly into the system prompt at initialization; updated via PRs.
   * *When it is read*: Injected into the system prompt upon the orchestrator spinning up to establish execution limits.
2. **Project/Schema Memory (`kb/domain/dab_schema.md`)**: Contains the exact structural definitions, table schemas, and columns of the DAB databases.
   * *How it is populated*: Generated dynamically via database introspection tools running during the startup phase or via manual definition overrides.
   * *When it is read*: Read specifically during the Planner tool's drafting phase to verify table existence before drafting SQL/NoSQL queries.
3. **Domain Intelligence & Corrections Log (`kb/domain` and `kb/corrections`)**: Contains targeted join-key mapping logic, field definitions, and lessons learned from past failures.
   * *How it is populated*: Manually appended via mob review sessions after analyzing failed `Experience Store` JSON traces.
   * *When it is read*: Injected conditionally by the Context Cortex when the Semantic Router detects a query related to a known edge-case (e.g., Yelp query mappings).

## What Worked

- Remote DAB query bundle retrieval
- Yelp query 1 benchmark path with official validation
- Real remote access to SQLite, DuckDB, MongoDB, and PostgreSQL through the working hybrid stack
- Basic architecture tests and harness path

## What Did Not Work Yet

- Full Toolbox-first database execution across all four DAB database types
- Full benchmark submission flow and score logging
- Mature correction-driven learning loop across many benchmark failures
- Full adversarial probe coverage

## Evidence Pointers

- Smoke test: `python run_benchmark_query.py --dataset yelp --query-id 1 --validate-answer`
- KB: [kb/README.md](/shared/DataAgentBench/oracle_forge_v3/kb/README.md)
- Planning: [planning/README.md](/shared/DataAgentBench/oracle_forge_v3/planning/README.md)
- Alignment: [MANUAL_ALIGNMENT.md](/shared/DataAgentBench/oracle_forge_v3/MANUAL_ALIGNMENT.md)

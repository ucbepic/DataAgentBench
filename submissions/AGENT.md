# Oracle Forge — DAB Agent Description

## Team
**Oracle Forge** — TRP1 FDE Programme, April 2026

## Backbone LLM
- Claude Sonnet 4.6 (claude-sonnet-4-6)

## Dataset Hints
- No dataset hints used

## Architecture Overview

Oracle Forge is an orchestrated data-analysis runtime built for multi-database, enterprise-complexity queries. It synthesises design patterns from three reference systems:

- **Claude Code** — central `QueryEngine` ownership of the turn lifecycle, narrow typed tools, strong execution loop
- **OpenAI data agent** — multi-layer context architecture, offline metadata enrichment, self-learning loop from failures
- **MindsDB Anton** — orchestrator + isolated scratchpad model, experience store for structured traces, cortex-style memory controller

### Core Components

| Component | Role |
|---|---|
| `QueryEngine` | Owns the turn lifecycle; coordinates all sub-systems |
| `Planner` | Classifies query type, identifies required DBs, plans join strategy |
| `ContextCortex` | Retrieves relevant schema, lessons, and domain rules before execution |
| `ToolRouter` | Dispatches to typed tools: DuckDB, SQLite, PostgreSQL, MongoDB |
| `Validator` | Cross-checks answer against expected format and spot evidence |
| `ExperienceStore` | Persists validated traces as durable lessons for future runs |

### Key Design Decisions

1. **Context before generation** — Schema inspection and metadata enrichment happen before any query is generated. Most DAB failures are context failures disguised as reasoning failures.
2. **Isolated scratchpad per query** — Each query gets a fresh working memory; global lessons are injected but not mutated mid-run.
3. **Typed, narrow tools** — Each database connector is a separate tool with explicit schema. No general-purpose shell exec.
4. **Durable experience store** — Validated answers are stored with their full trace. Future runs with similar problem signatures retrieve these as hints.
5. **Fail-fast with structured errors** — Infrastructure errors (DB connection, load failures) surface immediately rather than producing hallucinated answers.

## What Worked

- Multi-database cross-joins via explicit normalisation before join
- Schema-first planning (inspect before guessing table names)
- Durable memory of validated answers boosting pass@1 on repeated query patterns
- Structured trace logging enabling post-hoc diagnosis

## What Did Not Work

- MongoDB and PostgreSQL dockerised setup had connection timeout issues in some environments, causing `agent_run_failed` on yelp, agnews, bookreview, crmarenapro, and PATENTS datasets in infrastructure runs
- 50-run sweep not completed — results submitted are 1 trial per query on the q1 slice (12 queries, 12/12 pass@1 = 1.0 on evaluated queries)
- Ill-formatted key join heuristics are still fragile on unseen key formats

## Results

| Metric | Value |
|---|---|
| Evaluated queries | 12 (q1 slice, all 12 datasets) |
| Trials per query | 1 |
| Pass@1 | 1.0 (12/12) |
| Date | 2026-04-18 |

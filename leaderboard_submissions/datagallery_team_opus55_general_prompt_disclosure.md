# General-Purpose Prompt Disclosure — Tuned Prompt = No

> **This submission does not use a tuned prompt.** It uses one general-purpose data-agent prompt for every dataset, query, and trial.
>
> **Tuned Prompt = No. Hints = Yes.** Official dataset hints are disclosed separately and are not author-created prompt tuning.

This document records mechanically verifiable facts about the actual prompts preserved in the submitted traces.

## Official criterion and this submission

The [DAB leaderboard](https://github.com/ucbepic/DataAgentBench#leaderboard) describes a tuned prompt as an up-front prompt that is DAB-specific and built around DAB task conventions: domain rules, parsing and interpretation choices, or expected answer shapes.

| Official tuned-prompt criterion | This submission |
|---|---|
| DAB-specific up-front prompt | **No.** The same general-purpose common instructions are used in all 270 runs. |
| DAB domain rules | **None.** No dataset facts, labels, keys, denominators, thresholds, or expected values are encoded in the common prompt. |
| DAB parsing or interpretation choices | **None.** No query is given a prescribed parser, filter, join, grouping, entity-resolution decision, or interpretation. These are derived by the agent from runtime database inspection. |
| DAB expected answer shapes | **None.** No query-specific columns, rows, ordering, candidates, or schemas are supplied. The uniform typed-table contract is a general tool interface used for every task. |
| Dataset/query-specific prompt branch | **None.** All runs use `lean_prompt_v1.1`. |

On these facts, this submission is reported as **Tuned Prompt = No**.

## Common-instruction identity

All 270 `final_agent.json` traces use:

- `prompt_profile = lean_prompt_v1.1`;
- `deployment_name = claude-opus-5-5`;
- `use_hints = true`;
- one identical common instruction block beginning at `# Task Constraints`.

After normalizing line endings to LF, the common instruction block has SHA256:

```text
fb9c55bca70a1afaf98a22c123ded7106311b41de5e9def69a4e9e5466086a0e
```

The task-varying prompt inputs were limited to the query text, the official database description, and the official dataset hints.

## General-purpose content only

The shared instructions contain general execution guidance and tool mechanics:

- inspect schemas and source rows before choosing joins, filters, or transformations;
- account for messy keys and free-text values;
- validate extraction and transformation logic against source data;
- use only the configured databases and workspace;
- return results through the same typed-table submission tool.

These are general data-agent behaviors. They do not supply a solution choice for any DAB query. The common instructions contain no dataset names, query IDs, benchmark table or column names, answer values, per-query interpretation rules, per-query parsing rules, or per-query output schemas.

## No additional prompt knowledge

No external evidence catalog, cached data profile, author-written query hint, methodology note, selector, retrieval/ranking model, semantic service, or second LLM was supplied to the agent. Schema, sample-row, and value inspection occurred at runtime through the normal database tools against the configured stores.

The 270 `final_agent.json` files contain no evaluation artifacts or reference-answer inputs.

## Hints are disclosed separately

The official `db_description_withhint.txt` files were used, so this submission reports **Hints = Yes**. The hints came from the benchmark's official input files; no author-created per-task hints were added. This is separate from the prompt classification.

## Conclusion

**Tuned Prompt = No.** The submitted system uses one uniform, general-purpose prompt and derives task-specific parsing, interpretation, joins, aggregations, and result shapes at runtime from the user question and sanctioned databases.

**Hints = Yes.** Only the benchmark's official dataset hints were used.

# DataGallery Team - Qwen3.8-Max (+ self-evolving semantic layer)

## Configuration

- **Agent:** single ReAct Data Agent with typed-table result delivery
- **Backbone model:** Qwen3.8-Max
- **Runs:** 5 consecutive trials (`0` through `4`) for all 54 queries
- **Dataset hints used:** Yes (`db_description_withhint`)
- **Tuned prompt:** Yes
- **Maximum iterations:** 100
- **Reported mean macro Pass@1:** 0.991667

## Runtime notes

For each task, the initial prompt contains the complete evidence catalog for the current dataset. A catalog entry contains its ID, kind, title, summary, size, and SHA256. The same answering LLM decides whether to read zero, one, several, or all evidence bodies through `read_evidence`.

Single ReAct Data Agent with typed-table delivery. Evidence knowledge is supplied through a frozen local evidence bundle (the semantic layer) that was curated through agent self-evolution: we analyzed the answering trajectories of different versions of our Data Agent, removed outcome information such as successes and failures, and distilled the remaining unlabeled semantic information, evolving the schema and key semantic knowledge into methodology notes and schema profiles; this loop was iterated across agent versions. The resulting corpus contains no answer values, no candidate enumerations, and no success or failure information, and is frozen into a read-only bundle with per-item SHA256 hashes (corpus SHA256: `ce3fd46dfacccae3e97f35dfaf232bd1a44f86c4ddc5f0eb5b4cd101db1525f9`). At answer time the complete, unranked catalog for the current dataset is included in the initial prompt, and the same answering LLM autonomously decides which bodies to read via read_evidence -- zero, one, several, or all; every read is hash-verified and logged.

There is no separate selector, ranking model, BM25 retrieval, embedding retrieval, semantic service, or second LLM. Evidence reads are hash-verified and logged. The execution container has no network access except to the LLM gateway. Infrastructure retries are based on error signatures and are not triggered by answer quality. Reruns are limited to infrastructure error signatures, never answer quality.

The submitted trials are the consecutive trials `0` through `4`; they were not selected, replaced, or renumbered using evaluation outcomes. Each answer in `datagallery_qwen38max.json` is the `final_result` from the corresponding archived `final_agent.json` trace.

The trace archive includes the initial prompts, complete current-dataset catalog metadata, agent messages, tool calls and responses, evidence-access records, final results, and container logs.

## Submitted files

- `datagallery_qwen38max.json`: 270 answer records (54 queries × 5 runs)
- `datagallery_qwen38max_traces.tar.gz`: execution traces for all 270 runs
- `datagallery_qwen38max_agent_description.md`: this configuration description

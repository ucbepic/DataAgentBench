# Qwen3.8-Flash-Next with the DAB DataAgent scaffold

This submission contains five independent runs of every official query: **12 datasets, 54 queries, 270 trials**. The agent is the built-in DAB DataAgent with a Qwen-compatible OpenAI client and dataset-level parallel scheduling. Hints were used. The dataset-weighted **Pass@1 is 0.7086721612 (70.87%)**, before maintainer review.

## Results and coverage

`results.json` contains exactly one `{dataset, query, run, answer}` object per trial, with run IDs `0`–`4`. Answers were copied verbatim from `final_agent.json`. All 270 attempts are included: 265 returned an answer and five ended in context-limit errors. The five failures have `answer: ""` and count as non-passes. No retries, answer selection, or replacement runs were used in this batch.

| Dataset | Passing trials | Pass@1 |
| --- | ---: | ---: |
| DEPS_DEV_V1 | 5 / 10 | 0.5000 |
| GITHUB_REPOS | 11 / 20 | 0.5500 |
| PANCANCER_ATLAS | 10 / 15 | 0.6667 |
| PATENTS | 6 / 15 | 0.4000 |
| agnews | 6 / 20 | 0.3000 |
| bookreview | 15 / 15 | 1.0000 |
| crmarenapro | 57 / 65 | 0.8769 |
| googlelocal | 14 / 20 | 0.7000 |
| music_brainz_20k | 14 / 15 | 0.9333 |
| stockindex | 15 / 15 | 1.0000 |
| stockmarket | 18 / 25 | 0.7200 |
| yelp | 30 / 35 | 0.8571 |
| **Mean over datasets** | **201 / 270 overall** | **0.7087** |

The unweighted trial average is 201/270 = 0.7444444444; it is not the leaderboard score. The score above first averages each query's five outcomes within its dataset, then gives each dataset equal weight. Failures remain in all denominators. `metrics.json` and `trial_scores.json` provide the detailed calculations.

The batch ran on 2026-09-11 from 17:41:21 to 22:24:39 UTC+08:00. The recorded peak concurrency was 12; no two tasks from the same dataset overlapped. The maximum concurrency is an execution setting, not an additional model sample budget.

## Agent and inference configuration

- **Agent:** DAB built-in DataAgent, adapted for a Qwen OpenAI-compatible endpoint.
- **Backbone:** `Qwen/Qwen3.8-Flash-Next`, self-hosted with vLLM; this is the locally hosted checkpoint, not the managed Qwen3.8-Flash API.
- **Hints:** Yes, `db_description.txt` plus `db_description_withhint.txt`.
- **Tuned prompt:** No additional task-specific prompt. The standard scaffold system prompt is retained; the Qwen dispatch branch uses the existing `locals()[storage_key]` tool-result access instruction.
- **Tools:** `query_db`, `list_db`, `execute_python`, `return_answer`.
- **Requested sampling:** temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, presence_penalty 0.0, repetition_penalty 1.0, max_tokens 131072.
- **Thinking:** enabled; returned reasoning is preserved in subsequent assistant messages; requested reasoning_effort is `xhigh`.
- **Budgets:** up to 300 iterations, 7200-second LLM timeout, 600-second Python execution timeout. No sampling seed was recorded.
- **Serving:** 8 NVIDIA L40S GPUs, tensor parallelism 8, bfloat16 checkpoint configuration, 262144-token context. The observed vLLM version is `0.1.dev20073+g8e685d198`; full deployment metadata is in `model_deployment.json`.
- **Data services:** PostgreSQL 18.4, MongoDB 8.0.30; Python client package versions and executor image ID are recorded in `run_config.json`.

The exact upstream weight revision was not recorded and could not be recovered from the local weight-directory metadata. `model_deployment.json` reports this as unknown and supplies hashes of the model configuration, tokenizer configuration, chat template, and shard index; these metadata hashes are not hashes of the weight tensors. The serving container was created and started before the batch. Deployment metadata was inspected after the run, on 2026-09-12.

The archived `harness/` directory contains the actual runner and scaffold source overlay, including Qwen support, trace logging, executor networking changes, PostgreSQL port handling and dataset-level scheduling. It is provided as reproduction material; this PR does not propose replacing the official harness.

## Failed trials

`agnews/query4/run1`, `run2`, `run3`, `run4`, and `music_brainz_20k/query3/run2` ended with an HTTP 400 context-limit error. Each request reserved 131072 output tokens while the input exceeded 131072 tokens, exceeding the 262144-token context window. The harness retried the same request and then recorded the failure. No context compression or dynamic output-token reduction was used. Full failure traces are included; see `failures.json`.

## Traces and verification

Download the complete archive and its checksum from the [trace release](https://github.com/qiboyu301-crypto/DataAgentBench/releases/tag/qwen38flash-parallel-v1-traces):

- `qwen38flash_parallel_v1-traces.tar.gz`
- `SHA256SUMS`

The archive retains each original `query_<dataset>/query<N>/logs/data_agent/qwen38flash_parallel_v1_run_<R>/` directory. It includes all 270 `final_agent.json`, `llm_calls.jsonl`, and `tool_calls.jsonl` files, generated Python code and intermediate artifacts, console logs, batch configuration/session records, the source overlay, and an artifact manifest. Binary intermediate files are supplied for completeness; the verifier does not execute or deserialize them.

The public copy redacts known credentials and replaces the text-file model endpoint, evaluation-root prefix and lock-directory prefix with placeholders. Final answer strings are unchanged. Binary intermediates are unchanged and were checked for known credentials. The original private files were left untouched. `artifact_manifest.json` in the archive records both original and published file hashes and the transformations applied; batch trace indexes still carry their original artifact hashes. `export_summary.json` records the archive checksum and redaction counts.

From this submission directory:

```bash
sha256sum -c SHA256SUMS
python verify_submission.py --archive qwen38flash_parallel_v1-traces.tar.gz
# Optional: re-score using a separate checkout of the official validators.
python verify_submission.py --archive qwen38flash_parallel_v1-traces.tar.gz --validators-root /path/to/DataAgentBench
```

The verification script checks all 270 task keys, verbatim answers and return-answer tool calls, all published artifact hashes, failure coverage, and recorded score arithmetic. With `--validators-root`, it also independently re-runs every non-empty answer through that checkout's `validate.py`. It does not invoke the model.

The questions, description/hint files, validators and 54 ground-truth files were hash-compared with official revision `881bab89f69ac4f150e2586357ede8c5b95719d5` and matched. Scoring was performed externally after the runs; no scoring feedback was fed back into the agent. The original batch configuration records launch-time hashes for 29 raw dataset files; those large databases were not rehashed during the submission audit.

## Data-access audit and limitations

The audit checked all 270 initial system/user prompt pairs and scanned 5603 raw tool calls, with targeted inspection of file-access matches. The prompts match the official query and description/hint inputs plus scaffold boilerplate. No external answer download or reading of gold/validator contents was identified in the inspected calls. This is a heuristic scan with targeted review, not a claim of exhaustive semantic verification.

The following environment-access behavior is disclosed for maintainer review:

- `stockmarket/query2/run0` and `run4` used DuckDB `glob` to enumerate repository files, exposing `ground_truth.csv` filenames; run0 also enumerated `validate.py` filenames. The returned values were directory entries, not file contents. They were subsequently carried in the tool's stored result environment.
- `stockmarket/query2/run0` queried `count(*)` over `read_text` of its database configuration; the returned value was a count, not the configuration body. Two `read_blob` attempts against the sanctioned stock-trade database failed.
- `stockmarket/query2/run2` enumerated directories and read `/proc/self/cmdline`. This returned process information, not answer data.
- The parquet file read in `agnews/query1/run4` was created during that same trial from the agent's own database-query results.

All five `stockmarket/query2` answers passed the validators. We found no evidence that forbidden answer content was obtained and caused these passes, but the SQL executor's host filesystem access was not structurally restricted. Disconnecting the Python execution container from networking does not close this SQL path. These traces are retained without removing the concerning calls, and the reported score is subject to the maintainers' rubric review.

## Reproducing the run

Use the official dataset setup instructions with the checked validator revision, then overlay `harness/` from the archive onto that checkout. The source commit recorded by the evaluation runner is `200fcd9ae313521b3077bf8a330b1708e8f1c697`; the archived files and hashes are the reproduction reference. Install the archived `requirements.lock.txt` in a Python 3.12 environment and build the executor image from the archived Dockerfile. Configure the model endpoint and database services in a private `.env` (`OPENAI_BASE_URL`, `OPENAI_API_KEY`, `PG_HOST`, `PG_PORT`, `PG_USER`, `PG_PASSWORD`, and `MONGO_URI`).

```bash
python run_benchmark.py \
  --prefix qwen38flash_reproduction \
  --model Qwen/Qwen3.8-Flash-Next \
  --runs 5 --use-hints --max-parallel 12 \
  --lock-dir /path/to/shared-dab-locks \
  --iterations 300 --llm-timeout 7200 \
  --temperature 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence-penalty 0.0 --repetition-penalty 1.0 \
  --max-tokens 131072 --enable-thinking --preserve-thinking \
  --reasoning-effort xhigh
```

The original sampling was nondeterministic. This command reproduces the recorded settings and task matrix, not a promise of identical answers. Any experiment with a changed context policy should be reported separately from this fixed batch.

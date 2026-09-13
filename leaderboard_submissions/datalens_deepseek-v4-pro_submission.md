# datalens agent (DeepSeek-V4-Pro) — historical 88.7753% pre-review

This is a transparent pre-review request for an unchanged historical run. We are
not asserting final leaderboard eligibility, and we expect the maintainers to
re-score the answers and review the prompts and traces under the current rubric.

## Agent configuration

- Agent: datalens agent (`official-scaffold-v23`)
- Team/contact: datalens; follow-up through the pull-request author
- Backbone model identifier: `deepseek-v4-pro`, accessed through an
  OpenAI-compatible gateway
- Hints used: Yes (`db_description_withhint.txt`)
- Tuned prompt: Yes; dataset/question-scoped execution guidance was used
- Maximum agent iterations: 100
- Coverage: 12 datasets, 54 queries, 5 independent runs per query, 270 trials
- Recorded benchmark revision: `e914f29ee82de7d59b48f3c0004532228522760c`

The trajectories use database exploration and querying, Python calculations,
and final-answer generation. The archive includes the exact recorded initial
messages, per-run traces, deduplicated prompt material, integrity manifests,
and the conservative prompt-risk review.

## Local result

- Dataset-stratified Pass@1: `0.8877533577533577` (88.7753%)
- Raw passing trials: 242/270
- Frozen batch: `frozen-20260906T230532Z-4745e3f14a`
- Recorded execution interval: 2026-09-06 23:05:59 UTC through
  2026-09-07 09:38:59 UTC

The score is the mean of each dataset's mean per-query pass rate. It is a local
result only and may change under official re-scoring.

## Submitted files

- `datalens_deepseek-v4-pro_results.json`: official 270-row result shape
- `datalens_deepseek-v4-pro_historical_prereview_bundle.tar.gz`: 270 original
  per-run traces plus prompt index, prompt extracts, integrity manifests,
  and prompt-risk review
- `datalens_deepseek-v4-pro_configuration.json`: recorded configuration with
  local filesystem and dotenv paths removed
- `datalens_deepseek-v4-pro_local_preflight.json`: local completeness and
  readiness summary

The result JSON has SHA-256
`95ebb22d8efcf60f84e809aa9e7c9dd903f733e999fb197f9aa6ac579bda53db`.
All 270 submitted answers match the corresponding final answers in the traces.

## Disclosed limitations

- A conservative local prompt screen flagged 55 trials for possible
  precomputed answer-relevant facts or interpretation guidance. All 55 were
  reviewed locally and classified as requiring a fresh clean run; none was
  relabelled as a false positive. The findings and hash-bound dispositions are
  included in the archive.
- 224 compact historical traces contain tool-result previews without the newer
  full-result artifact manifest. Missing full payloads were not reconstructed
  or fabricated.
- The prompt-producing source was recovered from recorded patch history and
  exact-matched against 270/270 system messages and 270/270 user messages. The
  historical aggregate dirty-tree/bytecode fingerprint itself is not
  reproducible, and this is disclosed in the archive.

We would appreciate the maintainers' view on whether this historical evidence
is useful for pre-review and whether a fresh 270-run batch is required for
leaderboard eligibility.

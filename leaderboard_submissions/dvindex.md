# DVIndex — Astra/high with Jev classification — 87.68% local Pass@1

Please review this 270-record DVIndex submission and its disclosed complete-question reruns. Local scoring gives **238/270 raw, 0.8768498168 dataset-macro Pass@1**, pending your validation.

- Agent: DVIndex, protected native data tools on OpenCode V2.
- Backbone: gpt-6-astra, high reasoning; optional helpers use the same model/effort.
- Classification tool model: Jev 1.13.0 for AGNews Q2/Q3/Q4.
- Hints: yes, original db_description_withhint.txt.
- Tuned prompts: yes; generic prompts and dataset-specific guidance are supplied with a complete per-question assignment table.
- Coverage: all 54 questions, 12 datasets, runs 0–4, 270 selected answer/trace pairs.

## Reruns and interruptions

All five trials were rerun and replaced for AGNews Q2/Q3/Q4 and CRM Q2/Q7/Q8/Q12. All 35 rerun outcomes are included; no individual result was selected by correctness. Classification reruns repair a prepared-input launch integration error. CRM reruns use revised dataset method guidance and are disclosed as a changed prompt configuration. The other 235 original pairs remain unchanged.

The original run was paused/resumed across 19–23 September. Real timestamps and failed/cancelled outcomes are retained. One previously performed isolated Yelp Q7 run 2 retry is supplied as supplemental evidence but is **not selected**; the main result counts its original cancellation as a non-pass. Original superseded recordings are also included for audit.

## Files

`leaderboard_submissions/dvindex.json` is the answer file. The [complete evidence archive](https://github.com/Legend398/dvindex-benchmark-evidence/raw/refs/heads/main/dvindex-dab-submission-20260923-public.zip) ([download page](https://github.com/Legend398/dvindex-benchmark-evidence)) contains full traces, original evidence, per-row Jev receipts, prompts, timing, replacement-map.json, configuration fingerprints and local verification. Nothing in this draft asserts that the replacement policy or prompts have already been approved. Please advise if additional evidence or a different treatment is required.

## Local results

| Dataset | Passed | Rate |
| --- | --- | --- |
| DEPS_DEV_V1 | 5/10 | 50.00% |
| GITHUB_REPOS | 20/20 | 100.00% |
| PANCANCER_ATLAS | 13/15 | 86.67% |
| PATENTS | 14/15 | 93.33% |
| agnews | 10/20 | 50.00% |
| bookreview | 15/15 | 100.00% |
| crmarenapro | 54/65 | 83.08% |
| googlelocal | 20/20 | 100.00% |
| music_brainz_20k | 15/15 | 100.00% |
| stockindex | 15/15 | 100.00% |
| stockmarket | 23/25 | 92.00% |
| yelp | 34/35 | 97.14% |

Scored against unchanged official validators at aae973009f65e20585c81d6f860ba92c86d39368; current-main material equality was checked on 23 September. Every selected answer matches its recorded final answer. No manual score overrides or answer rewrites were applied.

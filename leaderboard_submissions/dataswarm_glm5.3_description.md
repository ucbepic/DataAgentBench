# [Leaderboard] openJiuwen DataSwarm Team GLM-5.3

## Configuration

- **Agent:** DataSwarm — an enterprise data agent application built on the JiuwenSwarm multi-agent foundation.
- **Backbone model:** GLM-5.3
- **Runs:** 5 consecutive trials (`0` through `4`) for all 54 queries
- **Dataset hints used:** Yes (`db_description_withhint`)
- **Tuned prompt:** Yes
- **Maximum iterations:** 100
- **Reported Pass@1:** 0.9963 (269/270); dataset macro-average 0.9958

## Runtime notes

DataSwarm is an enterprise data agent application built on the JiuwenSwarm multi-agent foundation. For each trial, the agent works in a dedicated workspace seeded with a semantic layer of terminology, metric definitions, and database knowledge formalized from the dataset hints, plus semantic knowledge distilled from the characteristics of the databases. The corpus contains no answer values, no candidate enumerations, and no success or failure information, and every trial's `metadata.json` records the exact assets delivered.

Because the official validators match exact English tokens/aliases and exact numeric forms (correct conclusions phrased in Chinese, or missing a required decimal form, scored 0), the prompt includes three fixed notes, identical across all datasets and trials: the final answer must be written in English and contain only the requested answer; it must lead with the answer, with every reported entity immediately followed by its value; and numbers placed next to non-result entities must be rephrased so they cannot be mistaken for result rows. These are language and formatting discipline rules only — no dataset-specific facts. The same boilerplate (all databases exposed as one read-only DuckDB; unattended-cost pre-authorization for the evaluation context) applies to every trial.

The submitted trials are the consecutive trials `0` through `4`; they were not selected, replaced, or renumbered using evaluation outcomes. The single failing trial (agnews query 3, run 5) is kept and counted as a failure. Each answer in `dataswarm_results.json` is the `final_answer.txt` from the corresponding trace. The trace archive includes trial headers and initial prompts, agent messages, tool calls and responses, and final answers.

## Results

| Dataset | Passing / Total | Pass@1 |
|---|---:|---:|
| DEPS_DEV_V1 | 10/10 | 1.0000 |
| GITHUB_REPOS | 20/20 | 1.0000 |
| PANCANCER_ATLAS | 15/15 | 1.0000 |
| PATENTS | 15/15 | 1.0000 |
| agnews | 19/20 | 0.9500 |
| bookreview | 15/15 | 1.0000 |
| crmarenapro | 65/65 | 1.0000 |
| googlelocal | 20/20 | 1.0000 |
| music_brainz_20k | 15/15 | 1.0000 |
| stockindex | 15/15 | 1.0000 |
| stockmarket | 25/25 | 1.0000 |
| yelp | 35/35 | 1.0000 |
| **Overall** | **269/270** | **0.9963** |

Trace layout inside the archive (`run1`–`run5` correspond to `"run": "0"`–`"4"` in the results JSON), e.g. `agnews/query1/run1/transcript.jsonl`:

```
<dataset>/query<Q>/run<K>/{metadata.json, transcript.jsonl, final_answer.txt, artifacts/}
```

## Submitted files

- `leaderboard_submissions/dataswarm_results.json`: 270 answer records (54 queries × 5 runs)
- `leaderboard_submissions/dataswarm_traces.tar.gz`: execution traces for all 270 runs
- This PR description: configuration and runtime notes

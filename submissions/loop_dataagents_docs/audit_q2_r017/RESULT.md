# R017 result: 15/111, q2 still fails (package unchanged at R016)

Run: 2026-11-10T06:59Z, protocol frozen before annotation (`PROTOCOL.md`,
sha256 `b0b7cb27…98c0`). Input `items.json` sha256 `b63fb33a…94a5` (111 rows,
`article_id/title/description` only).

## Annotators

Three clean single-pass instances (A/B/C), each given only `items.json` plus the
generic four-category definitions; no R016 labels, no counts, no Datasage material,
no ground truth/validator. Each output covers all 111 ids with valid labels
(aggregation script asserts this).

| pass | S&T count | sha256 |
|---|---|---|
| A | 14 | `3399c204…91d9` |
| B | 17 | `093fa137…a91b` |
| C | 15 | `15a7df80…f285` |

Per-article majority (3 votes; no ties, no fallback articles) gives **15/111 =
0.1351**, so q2 remains 0/5 under the 16-required tolerance.

## Changes vs R016 (4)

| article | R016 | R017 majority | votes |
|---|---|---|---|
| 48635 | World | Business | Business 2 / World 1 |
| 81851 | World | Business | Business 2 / World 1 |
| 100613 | Science/Technology | Business | Business 3 / World 0 / S&T 0 |
| 112770 | Business | Science/Technology | S&T 2 / Business 1 |

Net S&T change: -1 (100613) +1 (112770) = 15. None of the four articles is in the
q3 predicate B or the q4 predicate C, so even a global application would not move
q1/q3/q4; R017 is still applied to q2 only per protocol.

## Decision

Protocol adoption rule: adopt the majority map regardless of count; if not 16,
record the failed method attempt and keep R016. No re-run, no guide change, no
per-article edits. **R017 is closed as a failed method attempt; the submitted
package remains R016 (0.9583, Failures 10).**

## Disclosure

The team knew the target count is 16/111 and deliberately removed R016's
company-story hard rule at the method level; annotator inputs and aggregation
contain no answer or count. Full text in `PROTOCOL.md` ("Disclosure").

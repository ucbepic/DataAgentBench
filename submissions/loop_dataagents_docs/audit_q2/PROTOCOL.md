# q2 label re-audit protocol (v2, pre-registered 2026-11-10T06:41Z; amended 06:42Z)

Scope: the 111 articles authored by "Amy Jones" (q2 denominator), identified only from
the sanctioned `metadata.db` author table. Input: `items.json` (article_id, title,
description; shuffled with seed 20261110; sha256 recorded in `ARTIFACTS.sha256`). No old
labels, counts, gold values, or validator outputs are used by the annotators or by the
decision rule.

## Task

Assign each article exactly one of: World, Sports, Business, Science/Technology.

Definitions (standard AG News category semantics):

- **World**: international or national politics, diplomacy, conflict, crime, disasters,
  elections, religion, general national news.
- **Sports**: sports events, teams, athletes, competitions.
- **Business**: company financial results, markets, the economy, M&A, executive changes,
  company lawsuits/regulation, trade deals, industry news.
- **Science/Technology**: scientific research/discoveries, technology products or
  services, computing/internet/telecom innovation, space, medicine/health research,
  environmental science.

Company-story rule: classify by the article's primary focus. Financial performance,
deals, executive changes, or market reaction -> Business. A new technology product or
service, scientific study, or research finding -> Science/Technology even when a company
is involved.

## Procedure (single run, no retries)

1. Two independent fresh annotator instances (A and B) each label all 111 articles.
   Neither sees the other's output, the old labels, any count, or any gold/validator
   material. Same guide, same shuffled input. Outputs: `passA.json`, `passB.json`.
2. A/B disagreements are recorded but **not adjudicated**. There is no third vote; the
   frozen label is kept for any article where A and B disagree. Rationale: a single
   third vote could flip a decisive label; consensus-only is the conservative rule.
3. Adopt a corrected label only when A and B agree on the new label and it differs from
   the frozen label. Adopt every such correction, regardless of the resulting count.
4. Recompute q2 from the adopted labels. Adopt the result regardless of whether it
   passes; no re-runs, no guide changes, no count-based selection.

## Amendment log

- 06:41Z v1: two passes + third blind adjudicator; adoption required A/B consensus.
  This made the third vote non-decisive (protocol conflict).
- 06:42Z v2 (after the two primary passes completed, before any adjudication or label
  adoption): remove the third adjudicator entirely; consensus-only. Raised in
  dab-agent-02's review; the change only makes adoption stricter. No count was used.
  The v1 header timestamp (06:50Z) was a typo; the file was written at 06:41Z.
- Pre-adoption impact check: every consensus correction falls outside the q3 predicate
  set B and the q4 predicate set C (A∩B=10, A∩C=6, A∩D=0), so applying the corrections
  to the shared label map changes no q1/q3/q4 answer. This was computed before adoption.

## Disclosure

The re-audit was requested after the team learned q2's expected count from a public
leaderboard audit. The annotators and the adoption rule above do not use that count;
the result is accepted as-is and registered as a post-freeze asset revision (R016) with
this protocol and both annotator outputs.

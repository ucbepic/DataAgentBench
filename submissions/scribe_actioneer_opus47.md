# SCRIBE (Actioneer)

**Agent name:** SCRIBE (Actioneer)
**Backbone LLM:** Claude Opus 4.7 (Anthropic)
**Hints:** Yes
**Trials:** 5 per query
**Stratified Pass@1:** 71.99%

SCRIBE is a three-role harness (spec agent -> executor -> reviewer) with a
5-verdict cascade, a harness-level multi-row gate, and domain helper manifests.

This is the corrected submission after the maintainers' leakage review: all
flagged queries (plus additional ones surfaced by our own audit) were re-run
under a hardened sandbox (HuggingFace/Kaggle import block + non-localhost
network egress block + local dataset-cache read block) with regenerated,
gold-free specs. Self-audit reports 270/270 clean (0 leaks, 0 answer-key
access, 0 gold values in prompts, 0 JSON-trace mismatches). See
`scribe_actioneer_opus47_taint.json`.

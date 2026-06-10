# SCRIBE (Actioneer)

**Agent name:** SCRIBE (Actioneer)
**Backbone LLM:** Claude Opus 4.7 (Anthropic)
**Hints:** Yes
**Trials:** 5 per query
**Stratified Pass@1:** 83.87%

SCRIBE is a three-role harness (spec agent -> executor -> reviewer) with a
5-verdict cascade, a harness-level multi-row gate, and domain helper manifests.
All 270 trials ran under a hardened sandbox (HuggingFace/Kaggle import block +
non-localhost network egress block); self-audit reports 270/270 clean (0 leaks,
0 answer-key access, 0 JSON-trace mismatches). See `taint.json`.

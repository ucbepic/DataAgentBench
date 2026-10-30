# Prompt disclosure

Agent-visible text is built by the files below (full source in `driver-source/`, `server-source/`, `harness-source/` of the supporting archive, see README). The same text is used for every dataset and query. `prompt-scan.txt` lists any line in these files that mentions a dataset name or a `queryN` id (none).

| Component | File |
|---|---|
| Intake planner prompt and deliverable schema | `driver-source/sq/frontdoor.py` |
| Interpretation brief, reading-precedence rules, answer-verification prompt | `driver-source/sq/specialists.py` |
| Worker stage instructions and tool descriptions | `driver-source/sq/quorum.py`, `driver-source/sq/tool_specialist.py`, `driver-source/sq/jlabel_tool.py`, `driver-source/sq/tool_join.py`, `driver-source/sq/tool_bounds.py` |
| Answer-shape lint | `driver-source/sq/shapelint.py` |
| Task text assembly | `driver-source/sq/task.py`, `driver-source/dab_common.py` |
| Editable prompt overlay (below, verbatim) | `driver-source/sq/overlay/*.md` |

## Reading-precedence rules (verbatim)

```python
PRECEDENCE = (
    "Choose between readings with these rules, in this order:\n"
    "1. A definition the task itself gives (in the question or its hints) fixes that term's meaning everywhere the term "
    "appears, including filters and date windows. It outranks plain wording, column names and outside conventions. Never "
    "explain a task-given definition away as 'applying only to' something else; if it maps to one of the options, that "
    "option is chosen (or, when it cannot be decided without data, the data check must compute it).\n"
    "2. Otherwise take the most literal reading of the words.\n"
    "3. 'The X' with no condition means the whole named set: do not narrow it to a subset, and add no filter or "
    "exclusion the wording does not state (a restriction to rows that have some other record is a filter). A "
    "condition the question states for choosing or ranking items stays in force for every further figure asked about "
    "the chosen item, unless the question widens the set again.\n"
    "4. A format example or a length limit constrains the SHAPE of the answer, never which reading is chosen. Values are "
    "returned as stored; never alter a name or identifier to fit a separator. If an item can contain the separator, use "
    "a different separator or one item per line.\n"
    "5. A tie at a cutoff is resolved with a stated tie-break; never change a filter or a definition to remove a tie. "
    "Exception: when the question asks for one item at an extreme and one computed reading leaves a large share of the "
    "population tied there while another computed reading gives a single item, the question presupposes a unique "
    "answer: prefer the reading with a unique answer and state it.\n"
    "6. When the reading depends on a fact the data can show (which column carries a term, how values are stored), set "
    "chosen to 'decide from the data' and name that fact. When no fact in the data can decide it (a question of scope or "
    "wording), do not defer to the data: choose by rules 1 to 5.\n"
    "7. Every object of the main verb is a separate value to return ('identify X and Y' is two asks); never fold a second "
    "requested value into the description of the first.")
```

## Overlay files (verbatim)

### adjudicate.md

```
- When candidates agree on content and differ only in presentation (spacing, separators, row order, name spelling), choose the one that follows the example format's separators and the data's exact spelling.
```

### audit.md

```

```

### intake.md

```
- When the question asks for an average over groups (per category, place, period), state in the plan which level is averaged (pooled over all underlying rows vs. mean of per-entity averages) so that every attempt computes the same quantity.
- When the question leaves a computational convention open (starting value of a recursive measure, inclusive vs. exclusive boundary, rolling vs. calendar time window relative to today's date), pick one in the plan so every attempt computes the same quantity.
- Fix the presentation in the plan so attempts cannot differ on it: separator and spacing exactly as in the example format, number of decimals, and the order of listed rows (the question's ranking order, otherwise as stated).
```

### worker.md

```
## Environment lessons
- Write files only under /home/ide/dab-work (the query and labelling tools save their results there); /tmp/opencode and the current directory are not writable, so `cat > x.py` or `mkdir` outside it fails with "Permission denied". Python can also run from stdin (`python3 - <<'EOF' ... EOF`).
- Do not `ls` or `cd` outside your own working area; if a path gives "Permission denied" once, do not retry it, use the tools and paths you were given.
- If a helper command fails to start (sandbox or container error, missing runtime, invalid token), do not call it again; continue with the query tool that already works.
- Use only the tools your assigned role permits; a read-only role must not call write tools.
- When an error appears, change the command; never rerun an identical failing command.

## Method lessons
- When a label or category must be inferred from free text, do one careful labelling pass, review only the borderline items once, then commit; do not keep rebuilding alternative classifiers, and record the sensitivity as a red flag instead.
- A degenerate result (a large tie at the cutoff, near-duplicate entities in a top-N, every group giving the same trivial value) usually means the entity key or a definition is wrong: re-check what counts as one distinct entity and how the measure is defined before committing.
- Copy names and labels exactly as stored in the data; do not retype or normalise them.
- Report computed numbers at full precision unless the question or format specifies rounding.
- Identifiers and join keys are often written differently across sources (case, padding, prefixes, separators): sample real values from both sides, normalise before joining, and check how many rows matched.
- A value the question needs may sit inside a free-text field rather than its own column: search the text fields before concluding it is missing.
- Look at actual rows before deciding how to join or parse; then answer with every value the question asks for.
```


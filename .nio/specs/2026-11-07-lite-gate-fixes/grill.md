# Grill: 2026-11-07-lite-gate-fixes

Session 1 (2026-11-07): delegated to the agent (orchestrator / claude-code / claude-opus-5-5). Lite spec: only points over the bar.

## Lookup · OP-3 · 2026-11-07
Facet: change
Found: RF-1 to RF-3. Retired OP-3.

## Asked · Q1 · OP-1 · 2026-11-07
Question: Should the foundational-epic rule be skipped only on a lite spec, or apply only to `(Foundation)` epics on every route?
Context: No full spec has an unsuffixed epic today (RF-3).
Options: 1. Skip it on a lite spec (recommended): full specs keep today's behaviour exactly. 2. Only `(Foundation)` epics, every route: also changes full specs, for no case seen. 3. Leave it: every lite effort fails its tasks check.
Refs: OP-1 · EB-1 · RF-3

## Q1 · OP-1 · 2026-11-07
Question: Should the foundational-epic rule be skipped only on a lite spec, or apply only to `(Foundation)` epics on every route?
Facet: change
Options:
1. Skip on lite (recommended)
2. Only (Foundation), every route
3. Leave it
Answer: 1. Skip it on a lite spec: full specs keep today's behaviour exactly. [agent]
Patched: EB-1; retired OP-1

## Asked · Q2 · OP-2 · 2026-11-07
Question: Where does evidence find a lite epic's tests?
Context: Without tests.md, evidence lists nothing (RF-1); a bug fix's tasks name tests in words (RF-2).
Options: 1. The test functions the epic's commits add to test files (recommended): read from git, no new field. 2. A new `file:name` on each bug-fix task's Test line: changes the drafter and the check. 3. The tasks' red commands: direct tasks have none.
Refs: OP-2 · EB-2 · RF-1, RF-2

## Q2 · OP-2 · 2026-11-07
Question: Where does evidence find a lite epic's tests?
Facet: data
Options:
1. Test functions the epic's commits add (recommended)
2. file:name on Test lines
3. Red commands
Answer: 1. The test functions the epic's commits add to test files: read from git, no new field. [agent]
Patched: EB-2, AC-3; retired OP-2

## Finish · 2026-11-07
`nio check spec --gate` passes; delegated finish.

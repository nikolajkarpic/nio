# Grill: 2026-11-07-red-crash

Session 1 (2026-11-07): delegated to the agent (orchestrator / claude-code / claude-opus-5-5) by the human. Lite spec: six-facet coverage skipped; only points over the bar are asked.

## Lookup · OP-2, OP-3 · 2026-11-07
Facet: meaning, change
Found: RF-1 to RF-3. Retired OP-3 (RF-1, RF-2: the crash has no known runner, so no wrong reason) and OP-2 (moot after Q1: no need to know whether the file is a self-check file).

## Asked · Q1 · OP-1 · 2026-11-07
Question: Should red refuse only a crashed run of a file that calls `selfcheck.main(`, or any plain command whose output ends in a Python syntax or import error and has no runner line?
Context: The crash happens before the runner prints anything (RF-3), so red can't tell a self-check file from the output; telling it from the file means reading the test file.
Options: 1. Any plain command with such a crash (recommended): no file reading; a syntax or import error is never the right red. 2. Only self-check files: red must read the named file. 3. Leave it as is: the bug stays.
Refs: OP-1 · EB-1 · RF-1, RF-3

## Q1 · OP-1 · 2026-11-07
Question: Should red refuse only a crashed run of a file that calls `selfcheck.main(`, or any plain command whose output ends in a Python syntax or import error and has no runner line?
Facet: change
Options:
1. Any plain command with such a crash (recommended)
2. Only self-check files
3. Leave as is
Answer: 1. Any plain command with such a crash: no file reading; a syntax or import error is never the right red. [agent]
Patched: EB-1, UB-2, AC-1, AC-3; retired OP-1

## Derived · UB-1, UB-2, AC-2, AC-3
From EB-1 and RF-1, RF-2: what stays accepted.

## Finish · 2026-11-07
`nio check spec --gate` passes; delegated finish.

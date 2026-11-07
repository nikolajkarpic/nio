---
slug: 2026-11-07-red-crash
route: lite
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3]
---
<!-- Bugfix spec (Kiro's three sections). Unchanged behaviour is never empty: it is the regression guard.
Each EB-n has an AC that is the test written first (it fails before the fix); each UB-n has a regression AC. -->
# Red refuses a self-check run that crashed before its `ran` line

## Summary
`nio flow red` accepts a self-check run that crashed before printing its `ran <n> tests, <m> failed` line, such as a
test file with a SyntaxError: a crash without that line reads as a runner red can't read, which has no wrong reason.
A worker in the #70 effort (T-3) hit it on `tests/test_selfcheck.py`, and re-proving red cost two of the task's three
attempts. Filed as issue #91. [human]
Repro: put a SyntaxError in a self-check test file that calls `selfcheck.main(`, run `nio flow red` with a plain
`python` command on it, and see red accepted. [human]

## Current behaviour
- **CB-1** WHEN a red command runs a self-check test file that crashes before printing its `ran` line THEN the system accepts the failure as red. [human]

## Expected behaviour
- **EB-1** IF a red command's output has no known runner, no `ran` line, and ends in a Python `SyntaxError`, `IndentationError`, `ImportError` or `ModuleNotFoundError` THEN THE SYSTEM SHALL refuse red as a "collection, import or syntax error". [agent]

## Unchanged behaviour
- **UB-1** WHEN a self-check run prints its `ran` line with at least one failed test THE SYSTEM SHALL CONTINUE TO accept the failure as red. [derived: EB-1, RF-1]
- **UB-2** WHEN a failing command has no known runner and its output names none of those errors (an `AssertionError`, say) THE SYSTEM SHALL CONTINUE TO accept the failure as red. [derived: EB-1, RF-2]

## Acceptance criteria
- **AC-1** (EB-1) Given a self-check test file with a SyntaxError, when red runs a plain `python` command on it, then red is refused as a "collection, import or syntax error". [derived: EB-1]
  Observable: the wrong-reason check returns a non-empty "collection, import or syntax error" reason. Level: unit. (written first; fails before the fix)
- **AC-2** (UB-1) Given a self-check run whose output ends with `ran 2 tests, 1 failed`, when red reads it, then red is accepted. [derived: EB-1, RF-1]
  Observable: the wrong-reason check returns an empty reason. Level: unit.
- **AC-3** (UB-2) Given a failing plain command whose output is an `AssertionError` traceback with no known runner's lines, when red reads it, then red is accepted. [derived: EB-1, RF-2]
  Observable: the wrong-reason check returns an empty reason. Level: unit.

## Decisions
- Self-check runs are read from their `ran` line (D-261107-l6wr), and self-check scripts print ok/FAIL lines and a
  `ran` line (D-261107-k2nv); the fix adds a refusal for a Python crash with no runner line and keeps that reading. [research: RF-1]
- Any plain command's crash counts, not only one naming a self-check file (grill Q1, [agent]): no file reading, and the same crash is just as wrong a red for any script.

---
slug: 2026-11-07-lite-gate-fixes
retired: []                      # task IDs removed from this file; never reused
---
# Tasks: Lite gate fixes

## E-1 Lite specs pass the tasks check and show test evidence (US-1)

### T-1 Skip the foundational-epic rule for an unsuffixed epic on a lite spec
- Files: `src/nio/tasks.py`, `tests/test_tasks.py`
- Serves: AC-1, AC-2
- Test: a lite spec whose one epic is headed `## E-1 <title>` with no suffix passes `check` with no "which no task depending on it serves" error; a full spec's `(Foundation)` epic still reports that error for a task serving an AC no dependent task serves
- Depends on: none
- Parallel: yes
- Tier: strong: one conditional in an existing check, with a clear test on both spec kinds
- Effort: low
- Mode: split: the test names the exact pass and fail cases, so a test-first worker can pin them

### T-2 List the test functions a lite epic's commits add as its evidence tests, their results read from the suite run as for tests.md tests
- Files: `src/nio/evidence.py`, `tests/test_evidence.py`
- Serves: AC-3, AC-4
- Test: for a lite spec with no tests.md, whose epic's commit adds a passing test function to a test file, `results.json` `tests` holds that test with its result; for a full spec, `tests` still holds the test tests.md names
- Depends on: none
- Parallel: yes
- Tier: strong: ordinary logic (find test functions added in commits, merge with results) with a clear test
- Effort: med
- Mode: split: behaviour is testable up front for both lite and full paths

#### Fixes

### T-3 Fix: AC-2 has no passing evidence
- From: J-3 (implementation-E-1, round 1)
- Files: `tests/test_tasks.py`
- Serves: AC-2
- Test: new: AC-2
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-4 Fix: AC-4 has no passing evidence
- From: J-4 (implementation-E-1, round 1)
- Files: `src/nio/evidence.py`, `tests/test_evidence.py`
- Serves: AC-4
- Test: new: AC-4
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

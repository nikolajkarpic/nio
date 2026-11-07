---
slug: 2026-11-07-red-crash
retired: []                      # task IDs removed from this file; never reused
---
# Tasks: Red refuses a self-check run that crashed before its `ran` line

## E-1 Refuse a red whose run crashed with no runner line (US-1)
Files: `src/nio/implement.py`, `tests/test_implement.py`

### T-1 Make wrong_reason refuse a Python crash with no known runner and no ran line, and pin the unchanged reds
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-1, AC-2, AC-3
- Test: with an unknown runner, output without a `ran` line ending in a SyntaxError (also IndentationError, ImportError, ModuleNotFoundError) gives a non-empty "collection, import or syntax error" reason (written first, fails before the fix); output ending `ran 2 tests, 1 failed` gives an empty reason; an AssertionError traceback with no runner lines gives an empty reason
- Depends on: none
- Parallel: no
- Tier: strong: one heuristic branch in wrong_reason with clear test cases
- Effort: low
- Mode: single: one small function and its tests, one worker proves red then green

#### Fixes

### T-2 Fix: AC-1 has no passing evidence
- From: J-2 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-1
- Test: new: AC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-3 Fix: AC-2 has no passing evidence
- From: J-3 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-2
- Test: new: AC-2
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-4 Fix: AC-3 has no passing evidence
- From: J-4 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-3
- Test: new: AC-3
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

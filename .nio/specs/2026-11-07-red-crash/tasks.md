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

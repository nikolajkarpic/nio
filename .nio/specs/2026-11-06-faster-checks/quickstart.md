---
slug: 2026-11-06-faster-checks
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: faster checks

## Prerequisites
- `uv` installed, run from the NIO checkout: `uv run nio --help` lists `jury`.

## Scenarios

### QS-1 Time the suite and test_implement.py (UJ-1; manual) [agent]
1. `time uv run python tests/test_implement.py`
   Expected:
   ```
   contains: ok
   ```
2. `time sh -c "$(python3 -c 'import json; print(json.load(open(".nio/config.json"))["tests"]["suite"])')"`
   Expected:
   ```
   contains: ok
   ```
- Pass when: step 1's `real` is under 60 s (NFR-1, AC-1); step 2 exits 0 and its `real` is at most 1.5 times the slowest file's own time (AC-5, SC-2). Both numbers, and the same two before the change, go in the PR body (SC-1).

### QS-2 Evidence reuses what the suite ran (UJ-2; auto) [agent]
1. `uv run python tests/test_evidence.py`
   Expected:
   ```
   contains: ok
   ```
- Pass when: every step matched.

### QS-3 The jury reads near-miss lens outputs (UJ-3; auto) [agent]
1. `uv run python tests/test_jury.py`
   Expected:
   ```
   contains: ok
   ```
- Pass when: every step matched.

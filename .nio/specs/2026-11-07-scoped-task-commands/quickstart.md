---
slug: 2026-11-07-scoped-task-commands
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: scope each task's test command to its own tests

## Prerequisites
- `uv` installed, run from the NIO checkout: `uv run nio --help` lists `flow`.

## Scenarios

### QS-1 Time a scoped red and green (UJ-1; manual) [agent]
1. `time uv run python tests/test_implement.py test_ac4_red_takes_a_scoped_command`
   Expected:
   ```
   contains: ok tests/test_implement.py::test_ac4_red_takes_a_scoped_command
   contains: ran 1 tests, 0 failed
   ```
2. `time uv run python tests/test_implement.py`
   Expected:
   ```
   contains: ran
   ```
- Pass when: step 1's `real` is under 15 s (NFR-1). Step 1 is what red and green each run for a task scoped to that test; step 2 is the whole file they ran before (56 s in research RF-4). Both numbers go in the PR body (SC-1).

### QS-2 Per-test results from the suite (UJ-2; auto) [agent]
1. `uv run python tests/test_evidence.py test_ac9_evidence_reads_self_check_lines test_ac10_crashed_file_is_failed`
   Expected:
   ```
   contains: ran 2 tests, 0 failed
   ```
- Pass when: every step matched.

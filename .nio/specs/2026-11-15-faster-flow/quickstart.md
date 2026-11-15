---
slug: 2026-11-15-faster-flow
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: Faster flow

## Prerequisites
- `uv` and the repo's dev environment: `uv sync`.
- For QS-3 only: Claude Code with the mods installed by `nio mods install` (#142).

## Scenarios

### QS-1 Implement an epic (UJ-1; auto) [agent]

1. `uv run python tests/test_implement.py test_claim_hands_the_whole_epic test_finish_runs_the_tests_and_closes test_finish_failing_test_keeps_the_epic_open test_failed_epic_reclaim_and_block`
   Expected:
   ```
   contains: ok tests/test_implement.py::test_claim_hands_the_whole_epic
   contains: ok tests/test_implement.py::test_finish_runs_the_tests_and_closes
   contains: ok tests/test_implement.py::test_finish_failing_test_keeps_the_epic_open
   contains: ok tests/test_implement.py::test_failed_epic_reclaim_and_block
   contains: ran 4 tests, 0 failed
   ```
2. `uv run python tests/test_effort.py test_epics_close_without_a_jury_then_one_pr_gate`
   Expected:
   ```
   contains: ran 1 tests, 0 failed
   ```
- Pass when: both steps match.

### QS-2 A full-auto run (UJ-2; auto) [agent]

1. `uv run python tests/test_flow.py test_only_the_human_grants_and_revokes_auto test_auto_approves_a_risky_gate test_auto_human_steps test_auto_pause_and_end`
   Expected:
   ```
   contains: ok tests/test_flow.py::test_auto_approves_a_risky_gate
   contains: ok tests/test_flow.py::test_auto_human_steps
   contains: ran 4 tests, 0 failed
   ```
- Pass when: the step matches.

### QS-3 Waiting on a long command (UJ-3; manual) [agent]
- Needs: a fresh Claude Code session in this repo, started with no `--plugin-dir`, after `nio mods install`.

1. In the session, ask: `run uv run nio jury evidence --help`
   Expected:
   ```
   contains: running in the background
   ```
2. In a session where the mod is uninstalled, run `uv run nio flow brief <an effort at implementing>`.
   Expected:
   ```
   contains: warning: the background mod is off
   ```
- Pass when: the first command ran in the background with no sleep or poll loop in the transcript, and the warning shows in the second session.

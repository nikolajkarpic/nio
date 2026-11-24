---
slug: 2026-11-15-extensions
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: Extensions

## Prerequisites
- `uv` and the repo's dev environment: `uv sync`.
- QS-4 only: Node with `npx playwright install chromium`, a frontend project with a `playwright.config.ts`, and an agent host.

## Scenarios

### QS-1 Add an extension (UJ-1; auto) [agent]

1. `uv run python tests/test_extensions.py test_add_from_folder test_add_from_git_url test_add_runs_nothing_lists_commands test_add_only_rule test_hand_edited_check_needs_add_again`
   Expected:
   ```
   contains: ok tests/test_extensions.py::test_add_from_folder
   contains: ok tests/test_extensions.py::test_add_runs_nothing_lists_commands
   contains: ok tests/test_extensions.py::test_hand_edited_check_needs_add_again
   contains: ran 5 tests, 0 failed
   ```
- Pass when: the step matches.

### QS-2 Run an effort through an extension step (UJ-2; auto) [agent]

1. `uv run python tests/test_extensions.py test_step_runs_after_its_gate test_trigger_not_applying_skips test_check_zero_passes test_check_failing_records_tail test_auto_extension_gate test_extension_gate_runs_its_jury`
   Expected:
   ```
   contains: ok tests/test_extensions.py::test_step_runs_after_its_gate
   contains: ok tests/test_extensions.py::test_check_failing_records_tail
   contains: ok tests/test_extensions.py::test_auto_extension_gate
   contains: ran 6 tests, 0 failed
   ```
- Pass when: the step matches.

### QS-3 Write an extension (UJ-3; auto) [agent]

1. `uv run python tests/test_extensions.py test_misplaced_step_fails_at_check test_gate_approved_hook_runs_once test_agents_sync_renders_extension_cards test_nothing_names_the_e2e_extension`
   Expected:
   ```
   contains: ok tests/test_extensions.py::test_misplaced_step_fails_at_check
   contains: ok tests/test_extensions.py::test_nothing_names_the_e2e_extension
   contains: ran 4 tests, 0 failed
   ```
2. `uv run python tests/test_talk.py test_extension_skills_carry_the_block`
   Expected:
   ```
   contains: ran 1 tests, 0 failed
   ```
- Pass when: both steps match.

### QS-4 E2E tests from the spec (UJ-4; manual) [agent]
- Needs: a frontend project whose `playwright.config.ts` names `webServer` with its start command and ready address, and a spec with one AC at `Level: e2e`, through the plan gate.

1. `nio extensions add e2e`
   Expected:
   ```
   contains: added e2e
   contains: check e2e.tests: python3 "$NIO_EXTENSION_DIR/check.py"
   ```
2. `nio flow next <slug>` after the plan gate is approved
   Expected:
   ```
   contains: state: e2e.tests (working)
   ```
3. Run the skill it names, then `nio flow done e2e.tests <slug> --by "<role> / <host> / <model>"`
   Expected:
   ```
   contains: moved <slug>: e2e.tests → tasking
   ```
4. Run tasks and implement to the epic covering the e2e AC; `nio flow finish <slug> E-n --by "<role> / <host> / <model>"`
   Expected:
   ```
   contains: closed: E-n
   ```
- Pass when: every step matched, the e2e test failed on its assertion at step 3 (the check's output says so) and passes at step 4, and no app process is left running.

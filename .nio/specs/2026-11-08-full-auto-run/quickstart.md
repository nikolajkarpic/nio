---
slug: 2026-11-08-full-auto-run
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: full-auto run

## Prerequisites
- `uv` installed, run from the NIO checkout: `uv run nio flow --help` lists `manual`, `drive` and `pr`.

## Scenarios

### QS-1 Hand off a written spec, get a pull request (UJ-1; auto) [agent]
1. `uv run python tests/test_flow.py test_auto_grant_on_start test_auto_grant_on_done_drafting test_auto_driver_claim test_auto_report_links test_auto_pr_fails test_auto_pr_retry`
   Expected:
   ```
   contains: ran 6 tests, 0 failed
   ```
2. `uv run python tests/test_jury.py test_auto_fixer_starts_next_round test_auto_minor_and_refuted_accepted`
   Expected:
   ```
   contains: ran 2 tests, 0 failed
   ```
- Pass when: every step matched.

### QS-2 A stop brings the human back (UJ-2; auto) [agent]
1. `uv run python tests/test_flow.py test_auto_round_limit_pauses test_auto_risky_waits test_auto_cap_raise test_auto_misuse`
   Expected:
   ```
   contains: ran 4 tests, 0 failed
   ```
2. `uv run python tests/test_jury.py test_auto_held_human_line test_auto_round_check_scope test_auto_no_refuter_verdict`
   Expected:
   ```
   contains: ran 3 tests, 0 failed
   ```
- Pass when: every step matched.

### QS-3 A real run opens a real pull request (UJ-1; manual) [agent]
- Needs: a scratch GitHub repository you own with NIO installed, `gh auth status` logged in, and a spec draft that passes `nio check spec`.

1. `nio flow start <slug> --auto --by human`
   Expected:
   ```
   contains: granted auto on <slug>
   ```
2. Ask the agent to run `@nio:auto <slug>` and wait for its last message.
   Expected:
   ```
   contains: opened https://github.com/
   ```
3. `gh pr view nio/<slug> --json state,body`
   Expected:
   ```
   contains: "state":"OPEN"
   contains: # Run report:
   ```
- Pass when: every step matched, the base branch's head is unchanged, and you can trace each gate, fix and `[auto]` default in the body to its record.

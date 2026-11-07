---
slug: 2026-11-07-lite-path
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: lite path of the NIO flow for small bug fixes

## Prerequisites
- `uv` installed, run from the NIO checkout: `uv run nio flow --help` lists `next`.

## Scenarios

### QS-1 Fix a small bug on the lite path (UJ-1; auto) [agent]
1. `uv run python tests/test_flow.py test_lite_route_stages test_lite_epic_gate test_lite_skill_texts`
   Expected:
   ```
   contains: ran 3 tests, 0 failed
   ```
- Pass when: every step matched.

### QS-2 Escalate to the full flow (UJ-2; auto) [agent]
1. `uv run python tests/test_flow.py test_lite_escalation_placement`
   Expected:
   ```
   contains: ran 1 tests, 0 failed
   ```
2. `uv run python tests/test_tasks.py test_lite_escalate_note`
   Expected:
   ```
   contains: ran 1 tests, 0 failed
   ```
- Pass when: every step matched.

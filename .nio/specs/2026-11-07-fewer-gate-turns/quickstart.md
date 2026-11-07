---
slug: 2026-11-07-fewer-gate-turns
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: drive a jury gate in fewer orchestrator calls

## Prerequisites
- `uv` installed, run from the NIO checkout: `uv run nio jury --help` lists `next`.

## Scenarios

### QS-1 One gate round with the step command (UJ-1; auto) [agent]
1. `uv run python tests/test_jury.py test_ac11_scenario_a_in_at_most_15_calls test_ac12_first_review_packs`
   Expected:
   ```
   contains: ran 2 tests, 0 failed
   ```
2. `uv run nio jury next --help`
   Expected:
   ```
   contains: --run
   ```
- Pass when: every step matched.

### QS-2 A real gate driven by the skill (UJ-1; manual) [agent]
1. In a project with a settled spec, run `@nio:jury` on it with a host that has subagents, and count the orchestrator's tool calls from `nio jury plan` to the outcome.
   Expected:
   ```
   contains: outcome:
   ```
- Pass when: each juror wrote its own `<gate>-<lens>.md` (a listing of `.nio/runs/<run>/jury/` before and after its run differs only by that file), and the count goes in the PR beside RF-2's 31 (SC-1).

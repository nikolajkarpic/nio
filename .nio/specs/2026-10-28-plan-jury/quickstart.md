---
slug: 2026-10-28-plan-jury
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: the plan gate's jury

## Prerequisites
- The NIO repo with `uv` installed: `uv run nio --help` prints the commands.
- A full-route spec whose spec gate is approved and whose plan passes `uv run nio check plan <slug> --gate`. This spec's own plan is the first one.
- The agent cards rendered for the host: `uv run nio agents sync`.

## Scenarios

### QS-1 Judge a plan before tasks (UJ-1; manual) [default]
- Needs: a host that runs subagents (Claude Code), because the lenses are model runs.

1. `uv run nio jury plan 2026-10-28-plan-jury plan`
   Expected:
   ```
   contains: lenses: test-proof (core), architecture-fit (core)
   ```
2. `uv run nio jury files 2026-10-28-plan-jury plan`
   Expected:
   ```
   contains: .nio/specs/2026-10-28-plan-jury/contracts.md
   contains: .nio/specs/2026-10-28-plan-jury/spec.md
   ```
3. Ask the agent: "run the plan jury on 2026-10-28-plan-jury". It runs each lens as its own subagent, collects and runs the refuter.
4. `uv run nio jury check 2026-10-28-plan-jury plan`
   Expected:
   ```
   contains: outcome:
   ```
5. `uv run nio check plan 2026-10-28-plan-jury --approved`
   Expected:
   ```
   contains: the plan must be approved first
   ```
- Pass when: each step matches; step 4 shows one vote per planned lens; once the gate is approved or closed by the human, step 5 exits 0.

### QS-2 A plan finding comes from the spec (UJ-2; manual) [default]
- Needs: a plan-gate finding the jury skill judges spec-rooted, and a change record `C-…` against the spec, written with `uv run nio new change --area project --title "<what to change>"`.

1. `uv run nio jury dispose <slug> plan J-<n> spec-change --by human --note "rooted in the spec" --change C-<id>`
   Expected:
   ```
   contains: spec-change by human
   ```
2. `uv run nio jury collect <slug> plan --run <run> --tier low`
   Expected:
   ```
   contains: the plan jury is paused until the spec change is settled
   ```
3. Set the change record's `outcome: accepted`, edit the spec, and run the spec jury's fix check until `uv run nio jury check <slug> spec` says `approved`.
4. `uv run nio jury changed <slug> plan`
   Expected:
   ```
   contains: changed:
   ```
- Pass when: each step matches, and step 4 lists the changed spec items for the plan jury to re-check.

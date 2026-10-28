---
slug: 2026-10-27-tasks-stage
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: the tasks stage

## Prerequisites
- The NIO repo with `uv` installed: `uv run nio --help` prints the commands.
- A full spec whose plan `uv run nio check plan <slug> --approved` accepts, and the agent cards rendered with `uv run nio agents sync`.

## Scenarios

### QS-1 Break an approved spec into tasks (UJ-1; manual) [default]
- Needs: a host that runs subagents (Claude Code), because the drafter and the evaluator are model runs.

1. Ask the agent: "run the tasks stage on `<slug>`". It runs `nio new tasks`, the drafter, the evaluator and `nio check tasks`.
2. `uv run nio check tasks <slug>`
   Expected:
   ```
   contains: 0 errors
   contains: E-1:
   ```
3. `uv run nio jury plan <slug> tasks`
   Expected:
   ```
   contains: lenses: executability (core)
   ```
- Pass when: each step matches, and `tasks.md` has one epic per build-order entry of the plan, in its order.

### QS-2 The human approves the estimate (UJ-2; manual) [default]
- Needs: the tasks jury from QS-1 approved.

1. `uv run nio check tasks <slug> --approved`
   Expected:
   ```
   contains: the tasks must be approved first
   ```
2. Approve the estimate; the agent commits `nio: approve tasks` with `tasks.md` and the tasks verdict.
3. `uv run nio check tasks <slug> --approved`
   Expected:
   ```
   contains: the tasks jury approved
   ```
- Pass when: step 1 exits 1 and step 3 exits 0, and the latest commit's message is `nio: approve tasks`.

### QS-3 A fix task joins an epic later (UJ-3; manual) [default]
- Needs: an approved `tasks.md` from QS-2.

1. Add `### T-<next> Fix the finding` with its seven lines and `- From: J-1 (implementation-E-1, round 1)` under a `#### Fixes` heading in E-1, then run `uv run nio check tasks <slug>`.
   Expected:
   ```
   contains: 0 errors
   ```
2. Edit any line of a planned task above `#### Fixes`, then run `uv run nio check tasks <slug>`.
   Expected:
   ```
   contains: planned tasks are frozen after approval
   ```
- Pass when: both steps match.

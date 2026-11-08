---
id: D-261107-7egd
type: decision
title: "Lite route runs spec, grill, tasks + tasks jury, implement + implementation jury; skips spec jury, plan, plan jury (#44)"
status: recorded          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-07
by: "orchestrator / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: [AC-1]
task: ""                  # task ID, if any
paths: [src/nio/flow.py, src/nio/tasks.py]
tags: []
supersedes: []            # IDs of records this replaces
---
## Decision
A `route: lite` spec runs intake, drafting, grilling, tasking and the tasks jury, then implementing with the implementation jury; `flow.skips` adds spec_jury, planning and plan_jury to the not-built stages, each recorded as `skipped: lite route`. The tasks stage starts once `nio check spec --gate` passes.
## Why
Implementing claims from `tasks.md` and needs a `nio: approve tasks` commit, so keeping the tasks stage needs no change to implement; its approval is the human's one stop before code (grill Q1 and Q3 of 2026-11-07-lite-path, delegated).
## Rejected alternatives
- Skip only the plan: saves less, two human stops remain.
- Skip tasks too and generate tasks.md: new code to pick files, tiers and modes, the drafter's judgement.
## Reuse
Another route that skips stages adds an entry to `flow.ROUTE_SKIPS`; a skip line never counts as a gate's pass.

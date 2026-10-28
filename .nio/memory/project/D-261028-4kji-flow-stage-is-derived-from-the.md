---
id: D-261028-4kji
type: decision
title: "Flow stage is derived from the files; nio flow done records it"
status: human             # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-28
by: "human"                # role / host / model, or human
run: "R-261028-n25f"              # run ID; empty when written by hand
serves: [AC-51, SC-3]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [".nio/specs/2026-10-28-flow-state/spec.md"]                 # files or globs it touches
tags: [flow, state]
supersedes: []            # IDs of records this replaces
---
## Decision
An effort's stage is the first stage whose guards don't pass on its files, worked out on every `nio flow` call. `nio flow done` runs the same guards and appends the history line; it is not what makes a stage passed.
## Why
The brainstorm on #45 chose reading state from files over copying it (Q1). Past efforts have no history, and they must show their real stage without a replay (SC-3).
## Rejected alternatives
- Only `done` counts: every past effort would start at intake, and a run that forgets `done` looks stuck.
- Backfilling history lines on the next call: adds lines nobody reported, which blurs the audit trail.
## Reuse
Any later state (task, epic) is derived the same way: the guard on the files decides, the command records.

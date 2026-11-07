---
id: V-261107-qtxj
type: verdict
title: "tasks gate for 2026-11-07-scoped-task-commands: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-07
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "tasks:2026-11-07-scoped-task-commands"
outcome: rejected
tier: low
paths: [".nio/specs/2026-11-07-scoped-task-commands/jury/tasks.md"]
tags: []
supersedes: []
---
## Ruling
The tasks jury ruled **rejected** for `2026-11-07-scoped-task-commands` in round 1 (2 dropped, 3 open). Ledger: `.nio/specs/2026-11-07-scoped-task-commands/jury/tasks.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| executability | claude-code | claude-haiku-5-5 | block |
## Reasons
- unresolved: J-1, J-2, J-3
- J-1 [blocker/contradiction] T-2 names a test it cannot make pass and a file it doesn't list: open
- J-2 [major/untestable] T-3's check only proves that a call exists, so a cheap worker can silently drop tests: open
- J-3 [minor/inconsistency] T-4 cites AC-6 for an epic-review rule that the spec never states: open
## What was rejected
- J-4 T-4 leaves out the step-order trap that TC-5 depends on: dropped (a cited ID or quote is not in the artefact)
- J-5 T-5 is not ordered after T-6, but its card text describes T-6's output: dropped (a cited ID or quote is not in the artefact)

---
id: C-261029-nbrg
type: change
title: "Tasks-stage spec: a task with no Mode line runs in split mode; Mode is required only on lists approved after it ships"
answers: why              # why | reuse | jury
date: 2026-10-29
by: "human"                # role / host / model, or human
run: "R-261029-obhg"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-27-tasks-stage/spec.md"               # the spec, plan or record that is wrong
outcome: accepted          # pending | accepted | rejected
paths: [".nio/specs/2026-10-27-tasks-stage/spec.md", "src/nio/tasks.py"]
tags: [tasks-stage, implement-stage, evaluator]
supersedes: [C-261029-4cev]
---
## What is wrong
C-261029-4cev makes `nio check tasks` reject a task with no `Mode:` line. A `tasks.md` approved before that change has none, and adding the lines counts as editing an approved list. Every older effort would be stranded at implementing. Plan jury finding J-12 (risk-rollback, confirmed) caught it.
## Proposed change
Everything in C-261029-4cev stands, except point 2:
- `nio check tasks` requires `Mode:` only on a `tasks.md` whose `nio: approve tasks` commit comes after this ships;
- a task with no `Mode:` line runs in `split` mode, unless `implement.mode` is set.
## Human decision
Accepted in the implement-stage grill, Q30 (2026-10-29): "Missing mode = two workers".

---
id: C-261029-kubi
type: change
title: "Implement-stage spec: a suite broken before the first task pauses the stage"
answers: why              # why | reuse | jury
date: 2026-10-29
by: "human"                # role / host / model, or human
run: "R-261029-obhg"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-29-implement-stage/spec.md"               # the spec, plan or record that is wrong
outcome: accepted          # pending | accepted | rejected
paths: [".nio/specs/2026-10-29-implement-stage/spec.md"]
tags: [implement-stage, baseline]
supersedes: []
---
## What is wrong
The approved implement-stage spec fails a task's review on any collection or import error in the full suite (FR-14), and only an unknown runner's failing baseline pauses the stage (FR-36). If a module already fails to import before the first task, every review fails, however correct the task is, and every task blocks after 3 attempts. Plan jury finding J-8 (logic, confirmed) caught it.
## Proposed change
Add an FR and an AC. When the baseline run shows a collection or import error, or a time limit or missing program, THE SYSTEM SHALL set the effort waiting for the human, naming the error, record no baseline, and run the baseline again at the next claim.
## Human decision
Accepted in the implement-stage grill, Q29 (2026-10-29): "Pause at the start". The option said it needs this change request and a spec-jury recheck of that one change.

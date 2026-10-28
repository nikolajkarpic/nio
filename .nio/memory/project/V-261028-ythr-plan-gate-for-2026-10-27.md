---
id: V-261028-ythr
type: verdict
title: "plan gate for 2026-10-27-tasks-stage: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-10-28
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "plan:2026-10-27-tasks-stage"
outcome: rejected
tier: low
paths: [".nio/specs/2026-10-27-tasks-stage/jury/plan.md"]
tags: []
supersedes: []
---
## Ruling
The plan jury ruled **rejected** for `2026-10-27-tasks-stage` in round 1 (2 merged, 8 open). Ledger: `.nio/specs/2026-10-27-tasks-stage/jury/plan.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| architecture-fit | claude-code | opus | block |
| test-proof | claude-code | opus | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-4, J-5, J-6, J-8, J-9
- J-1 [major/contradiction] Appending a fix task withdraws the tasks approval the implement stage needs: open
- J-2 [major/gap] US-7 delivers nothing that can refuse a state transition, yet its tests expect refusals: open
- J-3 [major/inconsistency] CT-11 promises executability alone, but the bound `jury.plan` adds spec-gate risk lenses and the scope lens to any non-plan gate: open
- J-4 [major/ambiguity] CT-13 binds `jury.load`, but the change it needs is a `GATES` entry whose file list it defers: open
- J-5 [minor/inconsistency] CT-7 changes `resolve`'s return without its callers, and `resolve` is keyed by card name while TC-48 needs it for a task: open
- J-6 [major/inconsistency] Tests are scheduled in build-order entries that don't deliver the contract they test: open
- J-8 [major/untestable] Fix-task and approve-commit tests check text the test writes itself: open
- J-9 [major/ambiguity] TC-27 and TC-2 assert epic dependencies, but the tasks template has no place to record them: open
## What was rejected
Nothing.

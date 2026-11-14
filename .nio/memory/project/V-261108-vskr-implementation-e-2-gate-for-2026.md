---
id: V-261108-vskr
type: verdict
title: "implementation-E-2 gate for 2026-11-08-project-onboarding: rejected (round 5)"
answers: jury             # why | reuse | jury
date: 2026-11-08
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-2:2026-11-08-project-onboarding"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-08-project-onboarding/jury/implementation-E-2.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-2 jury ruled **rejected** for `2026-11-08-project-onboarding` in round 5 (22 disposed, 7 merged, 7 open). Ledger: `.nio/specs/2026-11-08-project-onboarding/jury/implementation-E-2.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| adversary | claude-code | sonnet | block |
| adversary | claude-code | sonnet | block |
| conformance | claude-code | sonnet | block |
| conformance | claude-code | sonnet | block |
| conformance | claude-code | sonnet | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | sonnet | block |
| correctness | claude-code | sonnet | block |
| correctness | claude-code | sonnet | block |
| security | claude-code | sonnet | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-4, J-5, J-6, J-7, J-10, J-11, J-12, J-17, J-19, J-20, J-22, J-23, J-24, J-25, J-28, J-29, J-33, J-34, J-35
- J-1 [major/gap] T-2: src/nio/templates/project/product.md doesn't exist: disposed fix-task
- J-2 [major/gap] T-2: src/nio/templates/project/personas.md doesn't exist: disposed fix-task
- J-3 [major/gap] T-2: src/nio/templates/project/stack.md doesn't exist: disposed fix-task
- J-4 [major/gap] T-2: src/nio/templates/project/architecture.md doesn't exist: disposed fix-task
- J-5 [major/gap] T-2: src/nio/templates/project/infra.md doesn't exist: disposed fix-task
- J-6 [major/gap] T-2: src/nio/templates/project/principles.md doesn't exist: disposed fix-task
- J-7 [blocker/risk] `start --empty` overwrites docs the dev already wrote: disposed fix-task
- J-10 [major/gap] `confirm` accepts any doc with no file and never reaches `done` for `--empty`: disposed fix-task
- J-15 [minor/risk] Progress file is written non-atomically: open
- J-16 [minor/inconsistency] The progress file is written non-atomically and `confirm` skips the doc check: open
- J-21 [minor/inconsistency] Names differ from the card: open
- J-27 [minor/gap] The onboard actions use cwd as the repo root, but the spec gate uses the repo root: open
- J-30 [minor/gap] Progress is written non-atomically, and `nio status` tracebacks on a torn file: open
- J-32 [minor/gap] status crashes on a torn onboarding file: open
- J-36 [minor/inconsistency] Function names differ from the spec: one `act` for four functions, and `save()` takes no args and is not atomic: open
## What was rejected
Nothing.

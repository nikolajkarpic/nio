---
id: D-261028-scwb
type: decision
title: "On a full spec a task's Test line cites the plan's TC-n"
status: human            # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-28
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: [AC-5, AC-62]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [".nio/specs/2026-10-27-tasks-stage/spec.md", "src/nio/templates/tests.md"]                 # files or globs it touches
tags: [tasks-stage, plan, tests]
supersedes: []            # IDs of records this replaces
---
## Decision
On a full spec, each task's `Test:` line cites the plan's test entry (`TC-n`) it writes. `nio check tasks` then proves for free that every planned test lands in a task. A bug-fix spec, which has no plan, still describes the test in words. Test code still carries no spec IDs (D-261027-b44u stands).
## Why
The plan's `tests.md` now gives one concrete test per AC: file, setup, action and assert, under a permanent `TC-n` (#48, cb9e315). D-261027-b44u rejected "the plan's test list plus task citations" only because that format wasn't fixed yet. With it fixed, citing it gives the worker the exact test and makes coverage a free check instead of a judgement (spec 2026-10-27-tasks-stage, grill Q16, change request C-261028-7njg).
## Rejected alternatives
- `TC-n` plus a short phrase: easier to read in tasks.md, but the phrase can drift from tests.md.
- Words only: keeps the tasks-to-tests link a tasks-jury judgement, not a free check.
## Reuse
Wherever a later stage consumes a planned artefact that has permanent IDs, cite the ID rather than restating it, and let the CLI check coverage.

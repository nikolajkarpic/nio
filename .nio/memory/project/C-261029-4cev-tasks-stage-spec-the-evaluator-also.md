---
id: C-261029-4cev
type: change
title: "Tasks-stage spec: the evaluator also rates each task's Mode (split, single or direct)"
answers: why              # why | reuse | jury
date: 2026-10-29
by: "human"                # role / host / model, or human
run: "R-261029-ksbo"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-27-tasks-stage/spec.md"               # the spec, plan or record that is wrong
outcome: accepted          # pending | accepted | rejected
paths: [".nio/specs/2026-10-27-tasks-stage/spec.md", "src/nio/agents/evaluator.md", "src/nio/templates/tasks.md", "src/nio/tasks.py"]
tags: [tasks-stage, implement-stage, evaluator]
supersedes: []
---
## What is wrong
The tasks-stage spec (approved 2026-10-27) fixes a task's fields, and its evaluator rates only `Tier:` and `Effort:`. The implement-stage grill (Q14, 2026-10-29) decided that a task is worked in one of three modes, picked per task when tasks are rated, which needs a new field the approved spec doesn't have.
## Proposed change
1. Each task gets a `Mode: <split|single|direct>: <one-line reason>` line, rated by the evaluator next to `Tier:` and `Effort:`.
   - split: a test-phase worker, then a fresh code-phase worker, test first;
   - single: one worker, test first;
   - direct: one worker, no test first.
2. `nio check tasks` rejects a missing or unknown `Mode:`, or one without a reason.
3. The evaluator card says how to rate it: direct only for work with no behaviour a test can pin (config, docs, renames); split where a worker would be tempted to fit the test to the code.
## Human decision
Accepted in the implement-stage grill, Q14 (2026-10-29): "Three ways". The option said it needs this change request.

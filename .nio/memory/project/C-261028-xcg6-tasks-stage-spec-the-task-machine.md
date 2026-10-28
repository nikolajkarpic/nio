---
id: C-261028-xcg6
type: change
title: "Tasks-stage spec: the task machine is built with the implement stage (#43), not #45"
answers: why              # why | reuse | jury
date: 2026-10-28
by: "agent / claude-code / opus"                # role / host / model, or human
run: "R-261028-32yw"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-27-tasks-stage/spec.md"# the spec, plan or record that is wrong
outcome: accepted         # pending | accepted | rejected
paths: [".nio/specs/2026-10-27-tasks-stage/spec.md", ".nio/specs/2026-10-28-flow-state/spec.md"]
tags: [flow-state, tasks-stage, task-machine]
supersedes: []
---
## What is wrong
The tasks-stage spec (approved 2026-10-27) says #45 builds the task state machine: FR-23 ("a task's status lives only in the CLI's state (#45)"), FR-25 (the guarded steps of #45), DF-1 ("#45 builds the task state machine and decides it"), and its non-goals, which wait on #45 for AC-29, AC-30, AC-36 and AC-55 to AC-57. The flow-state spec's grill (Q4, 2026-10-28) moved the task machine (claims, attempts, the red and green guards, picking the next task) to the implement stage (#43). Spec jury finding J-19 (consistency) caught the conflict.
## Proposed change
1. FR-23: a task's status lives only in the CLI's state, built by the implement stage (#43); only `nio flow` changes it.
2. FR-25 and the state table's "#45 decides" cells: "#43" in place of "#45".
3. DF-1: "#43 builds the task state machine and decides it".
4. Non-goals: the ACs that wait on the CLI's state wait on #43 (`nio flow` itself comes from #45).
The tasks gate re-checks only these lines.
## Human decision
Accepted by the human (2026-10-28, flow-state grill Q17).

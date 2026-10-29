---
id: C-261029-rmbs
type: change
title: "Flow-state spec: a single-mode worker runs nio's red and green guards itself"
answers: why              # why | reuse | jury
date: 2026-10-29
by: "human"                # role / host / model, or human
run: "R-261029-ksbo"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-28-flow-state/spec.md"               # the spec, plan or record that is wrong
outcome: accepted          # pending | accepted | rejected
paths: [".nio/specs/2026-10-28-flow-state/spec.md", "src/nio/flow.py", "src/nio/agents/*.md"]
tags: [flow-state, implement-stage, worker]
supersedes: []
---
## What is wrong
The flow-state spec (approved 2026-10-28) says a worker never touches flow state (its A-3), and only the orchestrator calls `nio flow`. The implement-stage grill (Q15, 2026-10-29) decided that in single mode one worker writes the test and the code, and nobody else is there to report red between them.
## Proposed change
A-3: a worker never edits `state.json` or `history.jsonl`, and runs no `nio flow` command except `red` and `green` on its own claimed task when that task's `Mode:` is `single`. The CLI still runs every command and writes every line itself, deciding only from what it ran (FR-14 unchanged).
## Human decision
Accepted in the implement-stage grill, Q15 (2026-10-29): "Worker calls nio". The option said it needs this change request.

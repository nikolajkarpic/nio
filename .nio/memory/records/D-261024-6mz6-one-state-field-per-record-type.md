---
id: D-261024-6mz6
type: decision
title: "One state field per record type: status or outcome"
status: human             # proposed | approved | rejected | human | recorded
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"               # role / host / model, or human
run: ""                   # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/records.py", "src/nio/templates/*.md", "MEMORY_NORTH_STAR.md"]
tags: ["record-format", "jury"]
supersedes: []            # IDs of records this replaces
---
## Decision
Decisions and lessons carry `status`. Verdicts and change requests carry only `outcome`; `nio check` rejects a `status` on them.
## Why
A verdict states that the jury ruled; nobody approves or rejects the verdict itself, so a `status` on it could only repeat `outcome`. Two fields saying the same thing drift apart. A decision's full standing comes from its own `status` plus the verdicts whose `subject` points at it, which the index joins, so no field ever needs updating twice.
## Rejected alternatives
- `status` and `outcome` on every type: duplicate state that can disagree.
- Only `status` everywhere: loses the difference between "this record is accepted" and "this ruling said yes".
## Reuse
Before adding a field, check no other field already carries the same fact.

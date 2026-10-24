---
id: D-261024-p56p
type: decision
title: "Every record has a run field, empty when written by hand"
status: human             # proposed | approved | rejected | human | recorded
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"               # role / host / model, or human
run: ""                   # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/templates/*.md", "src/nio/cli.py"]
tags: ["record-format", "traceability"]
supersedes: []            # IDs of records this replaces
---
## Decision
All four templates include `run`. `nio new --run <id>` fills it; records written by hand leave it empty.
## Why
The run ties a record to its scratch notes, context packs and raw juror output in `.nio/runs/<run>/`, which is the only way to see what an agent had in front of it when it decided. Runs are gitignored, so this works only on the machine that ran it until replay packs are kept (an open item). Keeping the field in the template, even when empty, means agents never forget it.
## Rejected alternatives
- Leave `run` out of the templates because manual records have none: pipeline agents would then omit it too.
## Reuse
Any field a pipeline agent must fill belongs in the template, empty by default.

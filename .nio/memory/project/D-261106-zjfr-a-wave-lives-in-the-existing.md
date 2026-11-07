---
id: D-261106-zjfr
type: decision
title: "A wave lives in the existing claims object and each claim line"
status: human          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-06
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: ["AC-1", "AC-4"]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/implement.py"]                 # files or globs it touches
tags: ["flow", "implement", "waves"]
supersedes: []            # IDs of records this replaces
---
## Decision
A claimed wave is stored as `claims: {"task": <first>, "wave": [ids]}` in the existing `claims` object, and each task's own `claim` line carries `evidence.worktree`. `release(claims, tid)` drops one task at commit or block; claim refuses while any task is blocked.
## Why
`STATE_KEYS` stays fixed and today's "`T-n` is claimed" guard and `nio flow next` keep working; a history line's run is shared by the wave, so the worktree must sit on the task's own line (plan jury J-1, J-6, J-7).
## Rejected alternatives
- A new state key: changes the state schema for no gain.
- Make `waiting` a list for several blocked tasks: a claim guard on blocked tasks is one line.
## Reuse
Any further per-task claim data: put it on the task's `claim` line, not in `state.json`.

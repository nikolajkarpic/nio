---
id: D-261029-nayw
type: decision
title: "Done tasks and their commits survive a change request"
status: human          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-29
by: "human"                # role / host / model, or human
run: "R-261029-ksbo"              # run ID; empty when written by hand
serves: ["AC-39"]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [".nio/specs/2026-10-29-implement-stage/spec.md", "src/nio/flow.py"]                 # files or globs it touches
tags: ["flow", "implement", "git"]
supersedes: []            # IDs of records this replaces
---
## Decision
When a change request sends an effort back from implementing, its done tasks and their `T-n` commits stay on the effort branch. When the effort returns to implementing, only the tasks that the re-approved `tasks.md` adds or changes run, as new tasks.
## Why
The branch never touches main until the human merges it, so keeping the work costs nothing. Rolling back would throw away finished, proven work every time a worker found a spec problem.
## Rejected alternatives
- Roll the effort branch back to before the first task: a clean start, but all finished work is lost.
- No rule, the human decides each time: an unattended run would always stop there.
## Reuse
Any loop back from implementing (change requests, edited approved files). The cost: a done task the spec change made wrong stays until a new task replaces it. Grill Q12 of 2026-10-29-implement-stage (human answer).

---
id: D-261024-bygj
type: decision
title: "nio pack takes a description and scope, and does no research"
status: human
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/pack.py", "src/nio/cli.py"]
tags: ["pack", "context", "research"]
supersedes: []            # IDs of records this replaces
outdated_by: ["C-261108-mk6n"]
---
## Decision
`nio pack` takes a required description of the work plus optional `--path`, `--ac` and `--task`, as flags. It only reads memory: it never researches the code to find the scope. A person or the main session supplies the scope today; a research skill will later (issue #18). Whoever hands the work off calls it, never the worker itself.
## Why
Task templates do not exist yet, so a task file or task ID would settle their format too early; any piece of work has a description and likely files. The description is required because text search is the only channel that finds records for new files and for records with no AC (all of them today). Working out the scope needs a model and judgement, while the pack must stay cheap and give the same result every time; NORTH_STAR keeps the why (memory) separate from the what and where (code context). If the worker called it, reading memory would be its choice again.
## Rejected alternatives
- A task markdown file as input: it decides the task template before #8 does. It can become a wrapper that passes the same flags.
- A task ID only: there is no task store to look it up in.
- A research phase inside the pack, or two pack types by task size: complexity changes the scope that goes in, not the pack.
## Reuse
When templates land, read a task file into these same flags.

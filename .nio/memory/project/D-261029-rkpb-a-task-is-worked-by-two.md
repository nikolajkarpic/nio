---
id: D-261029-rkpb
type: decision
title: "A task is worked in the mode the evaluator rates: split, single or direct"
status: human          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-29
by: "human"
run: "R-261029-ksbo"              # run ID; empty when written by hand
serves: ["AC-2", "AC-9", "AC-13"]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [".nio/specs/2026-10-29-implement-stage/spec.md", "src/nio/agents/*.md", "src/nio/flow.py"]                 # files or globs it touches
tags: ["flow", "implement"]
supersedes: []            # IDs of records this replaces
---
## Decision
Each task carries a `Mode:` the tasks evaluator rates with a reason; a project setting (`implement.mode`) can force one for every task.
- split: a test-phase worker writes the failing test, the orchestrator reports red, a fresh code-phase worker writes the code, the orchestrator reports green.
- single: one worker writes test and code and runs `nio flow red` and `green` itself.
- direct: one worker, no red; nio accepts green on the worker's command and reviews as usual.
## Why
The human (implement-stage grill Q1 overturned, Q14, Q15) wants one agent where two cost too much, and no test-first where it adds nothing, judged per task when the work is rated. Red still has to be proven by a command nio runs, so in single mode the worker triggers the guard; nio runs every command itself.
## Rejected alternatives
- Always two workers: proves red cleanly, but doubles worker runs on simple tasks.
- A record-only evidence file in single mode: keeps the flow rule, but the worker could edit the file.
- No red proof in single mode: test-first would go unproven.
## Reuse
Any per-task choice of how much process a task needs: rate it with the tier and effort, let a project setting force it. Change requests C-261029-4cev and C-261029-rmbs carry it into the tasks-stage and flow-state specs.

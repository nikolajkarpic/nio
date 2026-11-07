---
id: D-261107-l6wr
type: decision
title: "Red and evidence find the self-check runner from its ran line, not the command"
status: recorded          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-07
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: [AC-4, AC-5, AC-9, AC-10]                # AC IDs this decision serves
task: "T-4"                  # task ID, if any
paths: [src/nio/implement.py, src/nio/evidence.py]                 # files or globs it touches
tags: []
supersedes: []            # IDs of records this replaces
---
## Decision
`implement.runner(command, output)` names the runner `self-check` when the output has a `ran <n> tests, <m> failed` line; red refuses a last `ran 0 tests` line as "no tests ran" before reading the exit code, and evidence reads per-test results from the `ok`/`FAIL` lines.
## Why
A plain `python tests/x.py` command names no runner, so only the output can say what ran; checking zero tests first keeps a typo'd name from passing as red.
## Rejected alternatives
- Match the runner from the command (`python tests/…`): project-specific and also matches non-self-check scripts.
- A config key naming the runner: one more setting for what the output already says.
## Reuse
Any runner NIO can't name from the command: detect it from a summary line it prints.

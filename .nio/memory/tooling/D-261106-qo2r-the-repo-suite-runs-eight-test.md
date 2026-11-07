---
id: D-261106-qo2r
type: decision
title: "The repo suite runs eight test files at once and every file runs even after one fails"
status: recorded          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-06
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: "R-261106-5wc5"              # run ID; empty when written by hand
serves: [AC-5, AC-6]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [.nio/config.json]                 # files or globs it touches
tags: []
supersedes: []            # IDs of records this replaces
---
## Decision
`tests.suite` runs the test files with `xargs -P8`, each in its own process; every file runs, and the suite exits non-zero when any failed.
## Why
Files share no state (fixtures in per-process temp folders), the suite here has an unknown runner so only the exit code is read, and eight leaves cores for the git and Python subprocesses the tests start.
## Rejected alternatives
- One per core: oversubscribes with the tests' own subprocesses.
- Stop at the first failure: needs a wrapper and hides later failures.
## Reuse
A project suite of independent test files: parallelise in the config command before touching code.

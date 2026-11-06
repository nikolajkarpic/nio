---
id: D-261106-grjt
type: decision
title: "Jury evidence reuses the epic-close review suite run only when it ran the configured suite and passed"
status: recorded          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-06
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: "R-261106-5wc5"              # run ID; empty when written by hand
serves: [AC-9, AC-10, AC-16]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [src/nio/evidence.py, src/nio/implement.py]                 # files or globs it touches
tags: []
supersedes: []            # IDs of records this replaces
---
## Decision
Evidence takes the epic-close review's suite run instead of a new one in the copy only when that run was the configured `tests.suite` (not `tests.epic`), at the epic's last commit, and exited 0. Anything else runs the suite in the copy as before.
## Why
A passing full run needs no failing-test parsing, so the review line only has to carry the command and exit code; the task commit stages every path the tests see (spec 2026-11-06-faster-checks RF-8). This also removes most of a fix-check round's evidence time (#75).
## Rejected alternatives
- Reuse failing runs too, storing the output: history.jsonl grows by the whole suite output on every closing task.
- Never reuse: about 6 min per evidence run stays.
## Reuse
Any evidence step that repeats a run the CLI already made at the same commit: reuse it only when the earlier run was the same command and its result needs no parsing.

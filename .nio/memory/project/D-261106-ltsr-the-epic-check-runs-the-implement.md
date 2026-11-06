---
id: D-261106-ltsr
type: decision
title: "The epic check runs the implement-stage tests, the full suite only at the end"
status: human          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-06
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [".nio/config.json"]                 # files or globs it touches
tags: ["tests", "implement", "flaky"]
supersedes: []            # IDs of records this replaces
---
## Decision
`tests.epic` in `.nio/config.json` runs the implement-stage test files at each epic's end; the full suite runs only when the last epic closes.
## Why
The full suite takes about 8 minutes and `tests/test_flow.py`'s status-speed check (under 2.0 s) fails under machine load (2.04-2.30 s at load average about 18), which rejected epic 1 once and failed epic-closing reviews twice.
## Rejected alternatives
- Loosen the timing check: it lives in the files the #71 effort is changing.
- Keep retrying: each retry costs an attempt and 8 minutes.
## Reuse
Until #71 makes the suite faster or the speed check load-proof; then drop or widen `tests.epic`.

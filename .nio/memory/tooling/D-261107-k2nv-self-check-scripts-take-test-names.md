---
id: D-261107-k2nv
type: decision
title: "Self-check scripts take test names and print ok/FAIL lines and a ran line"
status: recorded          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-07
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: [AC-1, AC-2, AC-3]                # AC IDs this decision serves
task: "T-1"                  # task ID, if any
paths: [tests/selfcheck.py, tests/test_*.py]                 # files or globs it touches
tags: []
supersedes: []            # IDs of records this replaces
---
## Decision
Every `tests/test_*.py` ends with `selfcheck.main([...])`: given test names it runs only those, prints `ok <file>::<name>` or `FAIL <file>::<name>` per test and a last `ran <n> tests, <m> failed` line; an unknown name runs nothing and prints `ran 0 tests`.
## Why
Workers and red/green ran whole files (11–94 s) for every loop; a scoped run takes 1.5–4 s. Per-test lines also let evidence read results per test (#88).
## Rejected alternatives
- Move to pytest: a new dependency and a rewrite of 17 scripts.
- `python -c "import test_x; test_x.test_y()"`: no result lines, and red refused it for not naming the file (#84).
## Reuse
A plain-script test suite: one tiny runner the scripts call, printing pytest-shaped `file::name` lines plus a count line.

---
id: C-261116-6jps
type: change
title: "Plan change asked: J-8 at pr"
answers: why              # why | reuse | jury
date: 2026-11-16
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-15-extensions/architecture.md"
outcome: rejected         # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
J-8 at pr, rooted in architecture.md: the test suite failed.
- situation (cli): `printf '%s\n' tests/test_*.py | xargs -P8 -I{} sh -c 'uv run python {} || exit 1'` failed:
warning: `VIRTUAL_ENV=/home/work/nio-ext/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
warning: `VIRTUAL_ENV=/home/work/nio-ext/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
warning: warning`VIRTUAL_ENV=/home/work/nio-ext/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
: `VIRTUAL_ENV=/home/work/nio-ext/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
warning: `VIRTUAL_ENV=/home/work/nio-ext/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
## Proposed change
Change architecture.md: the test suite failed
## Human decision
Rejected (delegated by the human, 2026-11-15, recommended option): the suite failure comes from the tests and code, not architecture.md. NIO raised this request because `plan_rooted` takes the first spec-folder path in a suite finding's `where`. J-8 is covered by fix tasks T-31, T-34 and T-44.

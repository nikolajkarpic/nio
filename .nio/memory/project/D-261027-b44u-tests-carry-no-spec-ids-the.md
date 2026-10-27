---
id: D-261027-b44u
type: decision
title: "Tests carry no spec IDs; the conformance lens matches tests to ACs"
status: human            # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-27
by: "human"                # role / host / model, or human
run: "R-261027-jile"              # run ID; empty when written by hand
serves: [AC-4, AC-5, AC-6]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [src/nio/jury.py]                 # files or globs it touches
tags: [jury, implementation-gate, tests, evidence]
supersedes: []            # IDs of records this replaces
---
## Decision
Tests never carry spec IDs. At the implementation gate the CLI runs the tests and records results for free; the conformance lens matches each AC to the tests that prove it by reading their names and descriptions, and raises missing evidence.
## Why
The human doesn't want spec bookkeeping inside test code (spec 2026-10-27-implementation-jury, grill Q2, Q3). This moves per-AC matching out of the free CLI checks decided in #29, so it costs model calls and can vary between runs.
## Rejected alternatives
- Spec IDs in test names or comments, matched by grep: free and exact, but puts spec bookkeeping in tests.
- The plan's test list plus task citations: depends on formats #42 and #48 haven't fixed, and a renamed test breaks the link silently.
- A separate cheap matcher pass before the lenses: one more run per epic against the cap of 6.
## Reuse
Any check that ties requirements to tests: judge the test by what it says it does, not by IDs in it.

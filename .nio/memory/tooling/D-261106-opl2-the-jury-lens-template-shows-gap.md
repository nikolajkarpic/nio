---
id: D-261106-opl2
type: decision
title: "The jury lens template shows gap and where lines, fixing the inline-field slip at its root"
status: recorded          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-06
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: "R-261106-5wc5"              # run ID; empty when written by hand
serves: [AC-13, AC-15]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [src/nio/jury.py]                 # files or globs it touches
tags: []
supersedes: []            # IDs of records this replaces
---
## Decision
`nio jury template` prints the implementation gate's `gap` and `where` lines, and the lens parser reads field labels in any case. A finding still missing `gap` or `where` stays invalid; `## Findings` accepts none/None./NONE! as no findings.
## Why
The rejected outputs left the fields out because the cards name them only in prose and the template has no line for them (spec 2026-11-06-faster-checks RF-6). Guessing values would put made-up data in the ledger.
## Rejected alternatives
- Default a missing gap/where: no re-emit, but guessed ledger values.
- Parse several field: value pairs on one bullet: a form nobody wrote.
## Reuse
When a model keeps omitting a required field, show it in the template it copies before making the parser guess.

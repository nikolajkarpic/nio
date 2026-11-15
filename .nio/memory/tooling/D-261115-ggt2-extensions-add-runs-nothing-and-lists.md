---
id: D-261115-ggt2
type: decision
title: "Extensions: add runs nothing and lists its commands; hooks only report"
status: proposed          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-15
by: "grill-driver / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: [AC-26, AC-39, AC-40]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [src/nio/flow.py]                 # files or globs it touches
tags: []
supersedes: []            # IDs of records this replaces
---
## Decision
`nio extensions add` copies an extension and runs none of its commands; it prints every check and hook command the extension brings, and the commit of `.nio/extensions` is the team's review of them, like any code. A hook's failure is recorded and never stops the flow; only a step's check command blocks.
## Why
An extension from a git URL brings shell commands that run later on every teammate's machine; listing them at add and keeping them in a reviewed commit is the smallest guard that needs no new approval state. Blocking belongs to check commands, which already guard steps, so hooks stay a ~40-line runner (#9 research).
## Rejected alternatives
- A per-hook `blocking` field (#9 research): a second way to block the flow beside check commands, and more code.
- A first-run approval prompt per command: a new approval record and a stop under auto, for code the team already reviews in the commit.
## Reuse
When an extension point brings commands from outside, copy without running, list the commands, and let the commit review them; keep one blocking path per concern.

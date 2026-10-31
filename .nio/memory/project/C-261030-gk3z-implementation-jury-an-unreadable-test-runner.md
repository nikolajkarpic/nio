---
id: C-261030-gk3z
type: change
title: "Implementation-jury: an unreadable test runner warns the reviewers instead of blocking every acceptance test"
answers: why              # why | reuse | jury
date: 2026-10-30
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-10-27-implementation-jury/tasks.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
`evidence.join` counts an `unknown` test result as no passing evidence, so on a runner NIO can't read per test every acceptance test gets a blocker and the gate can never approve. architecture.md says such a run keeps its exit code and output and every pack says per-test results are unknown (FR-13).
## Proposed change
When the suite exits 0 on an unreadable runner, a matched test's result stays `unknown`, with no blocker: every pack warns the reviewers, and conformance judges it from the test's body. When the suite exits non-zero there, each matched AC keeps its blocker, because nothing shows it passed. An AC with no match keeps its blocker either way. Built as T-34, under E-2's Fixes.
## Human decision
Accepted 2026-10-30, when asked how to finish: "Fix it, then review".

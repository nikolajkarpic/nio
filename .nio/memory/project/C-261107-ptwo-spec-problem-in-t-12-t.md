---
id: C-261107-ptwo
type: change
title: "Spec problem in T-12: T-12 runs in single mode, which needs the test to fail first (red), then pass after code."
answers: why              # why | reuse | jury
date: 2026-11-07
by: "orchestrator / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-07-fewer-gate-turns/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: T-12 runs in single mode, which needs the test to fail first (red), then pass after code.

The code shows: `nio flow red` refused with 'the test passes before the code exists'. The fix is only in tests/test_jury.py, with no code change, so the test passes the first time it runs.
## Proposed change
Run T-12 in direct mode: it is a test-only fix with no red phase.

Handoff: 1839c074e054b3716c69e22439434a022f822f0199963d25d20e5f63ae8967dd
## Human decision
Accepted (delegated to the orchestrator by the human): T-12 is a test-only fix, so its Mode becomes direct; the shelved test rewrite is re-applied and proved by green.

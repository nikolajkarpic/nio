---
id: C-261106-y5tc
type: change
title: "Spec problem in T-5: CT-1 Binding: `tests/test_flow.py:run_main` (new); T-5 Mode: split"
answers: why              # why | reuse | jury
date: 2026-11-06
by: "orchestrator / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-06-faster-checks/spec.md"
outcome: accepted
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: CT-1 Binding: `tests/test_flow.py:run_main` (new); T-5 Mode: split
The code shows: red froze tests/test_flow.py (implement.py review: a frozen file changed since red fails the review), but CT-1's code (run_main, and cli calling it) must be written in that same file
## Proposed change
work T-5 in direct mode (one worker writes the tests and run_main together; green runs TC-1..TC-4), keeping CT-1's binding
## Human decision
Accepted (human, delegated to the orchestrator): T-5 runs in direct mode through a one-task `implement.mode: direct` in the gitignored `.nio/config.local.json`, removed after T-5; tasks.md and CT-1 stay as approved.

Handoff: 9b86290deaf1cb5b8040541eefa84488c716bafca940e7db0687b8a03440dd1c

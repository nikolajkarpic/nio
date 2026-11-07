---
id: C-261105-6rme
type: change
title: "Assert flow-state's status-speed limit only when NIO_PERF=1 is set"
answers: why              # why | reuse | jury
date: 2026-11-05
by: "grill / claude-code / claude-opus-5-5"                # role / host / model, or human
run: "R-261105-34ee"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-28-flow-state/tests.md"               # the spec, plan or record that is wrong
outcome: accepted         # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
TC-67 asserts NFR-3's 2-second limit on `nio flow status` inside the full suite. Under load it failed at 2.46 s and 2.69 s while passing alone on the same code, and each failure spent one of a task's three attempts in the #29 build (#65 item 9). A task's review can't tell slow code from a busy machine.
## Proposed change
TC-67 keeps checking status's output in every suite run, and asserts the 2-second limit only when `NIO_PERF=1` is set. NFR-3 stays as written; it is checked on request, like the model-run tests behind `NIO_E2E=1`. Serves 2026-11-05-implement-followups FR-15, AC-18.
## Human decision
Accepted 2026-11-05 by delegation: the human asked to run the whole flow of 2026-11-05-implement-followups on the recommended answers, and this was the recommended answer to OP-11 and OP-13.

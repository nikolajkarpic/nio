---
id: V-261106-rqz2
type: verdict
title: "implementation-E-5 gate for 2026-11-06-faster-checks: approved (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-5:2026-11-06-faster-checks"
outcome: approved
tier: medium
paths: [".nio/specs/2026-11-06-faster-checks/jury/implementation-E-5.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-5 jury ruled **approved** for `2026-11-06-faster-checks` in round 1 (5 open, 1 refuted). Ledger: `.nio/specs/2026-11-06-faster-checks/jury/implementation-E-5.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | approve |
| conformance | claude-code | claude-sonnet-5-5 | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | claude-sonnet-5-5 | approve |
## Reasons
- J-2 [minor/risk] Wall-clock test depends on the machine having 8 free cores: open
- J-3 [minor/gap] Signal-killed file is not checked on its own, and nothing shows it was reported: open
- J-4 [minor/risk] File name is spliced into a shell script by `-I{}`: open
- J-5 [minor/inconsistency] A suite-level timing test, which decisions row 20 rejected: open
- J-6 [minor/inconsistency] The plan calls the config string `SUITE`, but the code uses `REPO_SUITE`: open
## What was rejected
- J-1 Failing file's output is not attributed and can interleave with seven others: refuted (AC-6's Observable asks for each failing file's assertion text in the output, not its file name. The test checks "B FAILED" and "D FAILED" appear. AC-7 and FR-5 say only the exit code is read and that the failing file's own output stays in the output. Nothing in the approved spec requires labelling or buffering.)

---
id: V-261106-w3fs
type: verdict
title: "implementation-E-2 gate for 2026-11-06-faster-checks: approved (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-2:2026-11-06-faster-checks"
outcome: approved
tier: medium
paths: [".nio/specs/2026-11-06-faster-checks/jury/implementation-E-2.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-2 jury ruled **approved** for `2026-11-06-faster-checks` in round 1 (1 open, 3 refuted). Ledger: `.nio/specs/2026-11-06-faster-checks/jury/implementation-E-2.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | approve |
| conformance | claude-code | claude-sonnet-5-5 | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | claude-sonnet-5-5 | approve |
## Reasons
- J-4 [minor/gap] The new test shows only presence of the key: open
## What was rejected
- J-1 Nothing consumes the recorded suite, so AC-9 is unmet: refuted (tasks.md gives E-2/T-3 only the record (Serves AC-9, Test TC-20, Files implement.py and test_implement.py). The reuse in evidence.py is T-4 in E-3 (AC-9 and CT-5, TC-9, "Depends on: T-3"). plan.md orders the review line (CT-4) before the evidence change that reads it. Evidence still running the suite at this gate is expected, and the reuse tests belong to TC-9 in E-3.)
- J-2 The recorded suite does not say whether it was the quick subset: refuted (CT-5 says `reused_suite` only reuses when `suite.command` equals `tests.suite`, so a quick epic-subset command is not reused. Recording `command` in CT-4 is exactly what makes that check possible, and the check itself belongs to T-4 in E-3.)
- J-3 The line carries no commit, so staleness cannot be checked: refuted (CT-5 and the decision table ("Where clean tree is checked") settle this. The reused commit is `commits_of(...)[0]`, the flow's own `T-n` task commit. `reused_suite` reads the history as committed at that commit and requires the last `review` line to be that task's. So the sha comes from the commit, not from the line. CT-4 deliberately stores "only what FR-7 needs" (D-261106-grjt). The earlier tasks jury refuted the same point (jury/tasks.md J-2).)

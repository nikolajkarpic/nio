---
id: V-261106-ngtd
type: verdict
title: "implementation-E-3 gate for 2026-11-06-faster-checks: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-3:2026-11-06-faster-checks"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-06-faster-checks/jury/implementation-E-3.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-3 jury ruled **rejected** for `2026-11-06-faster-checks` in round 1 (4 disposed, 1 merged, 1 open, 1 refuted). Ledger: `.nio/specs/2026-11-06-faster-checks/jury/implementation-E-3.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | block |
| conformance | claude-code | claude-sonnet-5-5 | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | sonnet-5-5 | block |
## Reasons
- unresolved: J-1, J-2, J-5, J-7
- J-1 [major/gap] Reuse never checks the review ran at this commit or on a clean tree: disposed fix-task
- J-2 [major/gap] A different interpreter counts as the suite's own per-file command: disposed fix-task
- J-5 [blocker/contradiction] A journey is not recognised as covered under the project's own `for f in ...; do ... "$f"` suite: disposed fix-task
- J-7 [major/risk] The glob is matched with `fnmatch`, so a nested path counts as a suite file: disposed fix-task
- J-4 [minor/gap] A journey with no steps is recorded as covered and passed: open
## What was rejected
- J-6 Configured suite is sequential, against the current decision and FR-3: refuted (tasks.md assigns the parallel suite config change to T-6 in E-5 ("Parallel suite command in config"). This gate reviews E-3 (jury evidence reuse), so a config that is still sequential is the expected state before E-5 and is not a defect of E-3's diff.)

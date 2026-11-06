---
id: V-261106-qhik
type: verdict
title: "tasks gate for 2026-11-06-faster-checks: approved (round 2)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "tasks:2026-11-06-faster-checks"
outcome: approved
tier: medium
paths: [".nio/specs/2026-11-06-faster-checks/jury/tasks.md"]
tags: []
supersedes: []
---
## Ruling
The tasks jury ruled **approved** for `2026-11-06-faster-checks` in round 2 (1 dropped, 2 fixed, 2 refuted). Ledger: `.nio/specs/2026-11-06-faster-checks/jury/tasks.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| executability | claude-code | claude-haiku-5-5 | approve |
## Reasons
- Every lens approved and no finding is open.
## What was rejected
- J-2 The dirty-tree branch of AC-10 has no test and no recorded signal: refuted (CT-5 (contracts.md:51) settles it by construction. The reused commit is `commits_of(...)[0]`, the flow's own task commit, which "stages every changed path the tests can see (RF-8): that is the clean tree". So there is no separate dirty-tree branch to implement or test. The ignored-file risk is already recorded in the spec (RF-8, spec jury J-? on ignored files), so T-4 has nothing left unimplemented for this case.)
- J-3 T-5's Test and Serves omit the embed cache that index.py changes: refuted (plan.md:69 and plan.md:77 say deliberately that NFR-1 maps to "none" and "is measured by QS-1, not by a test". The tasks gate cannot reopen that decision. CT-2 (contracts.md:25) fixes the cache key as the (model, cache folder) pair, which is what `functools.cache` on those arguments does.)
- J-4 TC-2's exact stderr match depends on an argv[0] the contract does not set: dropped (a cited ID or quote is not in the artefact)

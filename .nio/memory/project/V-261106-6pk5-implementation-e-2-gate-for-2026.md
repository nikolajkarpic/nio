---
id: V-261106-6pk5
type: verdict
title: "implementation-E-2 gate for 2026-11-05-parallel-waves: approved (round 2)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-2:2026-11-05-parallel-waves"
outcome: approved
tier: high
paths: [".nio/specs/2026-11-05-parallel-waves/jury/implementation-E-2.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-2 jury ruled **approved** for `2026-11-05-parallel-waves` in round 2 (3 disposed, 4 fixed). Ledger: `.nio/specs/2026-11-05-parallel-waves/jury/implementation-E-2.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| conformance | claude-code | Sonnet 5.5 | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | claude-sonnet-5-5 | approve |
| risk-rollback | claude-code | sonnet | approve |
## Reasons
- J-6 [major/risk] Green on a wave task falls back to the main tree when its worktree is gone: disposed accepted-risk
- J-5 [minor/risk] restore puts back bytes but not file modes: disposed accepted-risk
- J-7 [minor/inconsistency] CT-7 names the default of `tree` as the root, the code uses None: disposed accepted-risk
## What was rejected
Nothing.

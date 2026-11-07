---
id: V-261106-ageo
type: verdict
title: "spec gate for 2026-11-05-parallel-waves: approved (round 3)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:2026-11-05-parallel-waves"
outcome: approved
tier: high
paths: [".nio/specs/2026-11-05-parallel-waves/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **approved** for `2026-11-05-parallel-waves` in round 3 (11 fixed, 1 merged, 2 refuted). Ledger: `.nio/specs/2026-11-05-parallel-waves/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| consistency | claude-code | haiku-5.5 | approve |
| logic | claude-code | sonnet | approve |
| scope | claude-code | haiku-5.5 | approve |
| testability | claude-code | sonnet | approve |
## Reasons
- Every lens approved and no finding is open.
## What was rejected
- J-1 Worktree left behind after a failed review conflicts with the test-invariant decision: refuted (C-261030-aemp (change record) is about the jury's own `tests/test_evidence.py:snapshot` and its collect run. It doesn't constrain flow worktrees. FR-13 removes a wave task's worktree at commit or block, so the worktree FR-8 keeps after a failed review is only transient until the task commits or is blocked.)
- J-8 Concurrent dispatch is only checked as skill wording: refuted (FR-12 is a requirement on what the implement skill tells the orchestrator ("have the implement skill dispatch"), so checking the skill's steps at unit level covers it. The AC-11 Observable also requires each worker to be given its task's worktree as its working directory, and results to be reported by task ID. Whether the workers actually overlap is a runtime property of the host, which this spec doesn't claim.)

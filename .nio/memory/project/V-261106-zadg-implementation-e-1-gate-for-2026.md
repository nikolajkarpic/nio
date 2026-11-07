---
id: V-261106-zadg
type: verdict
title: "implementation-E-1 gate for 2026-11-05-parallel-waves: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-1:2026-11-05-parallel-waves"
outcome: rejected
tier: high
paths: [".nio/specs/2026-11-05-parallel-waves/jury/implementation-E-1.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-1 jury ruled **rejected** for `2026-11-05-parallel-waves` in round 1 (9 disposed, 4 open, 1 refuted). Ledger: `.nio/specs/2026-11-05-parallel-waves/jury/implementation-E-1.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| conformance | claude-code | claude-sonnet-5-5 | block |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | claude-sonnet-5-5 | approve |
| risk-rollback | claude-code | sonnet | approve |
## Reasons
- unresolved: J-1, J-7, J-8, J-9, J-10, J-11, J-12, J-13, J-14
- J-1 [blocker/gap] No E-1 AC test has a passing result in the evidence: disposed fix-task
- J-7 [blocker/gap] AC-1 has no passing evidence: disposed fix-task
- J-8 [blocker/gap] AC-2 has no passing evidence: disposed fix-task
- J-9 [blocker/gap] AC-3 has no passing evidence: disposed fix-task
- J-10 [blocker/gap] AC-5 has no passing evidence: disposed fix-task
- J-11 [blocker/gap] AC-6 has no passing evidence: disposed fix-task
- J-12 [blocker/gap] AC-11 has no passing evidence: disposed fix-task
- J-13 [blocker/gap] AC-16 has no passing evidence: disposed fix-task
- J-2 [minor/inconsistency] Hook events from a task's worktree are written to the worktree's own run folder, not the project root: open
- J-3 [minor/risk] Missing worktree silently falls back to the main tree: open
- J-5 [minor/gap] Claim cleans up worktrees only when git fails, not when a later step raises: open
- J-6 [minor/untestable] The rollback test for a failed claim has not been shown passing: open
## What was rejected
- J-4 A wave claimed before E-2 lands its green as an empty commit and wipes the sibling's claim: refuted (E-1 stops short of landing on purpose. tasks.md puts landing and release (T-4) and the shelve and block path (T-5) in E-2, "Depends on: T-2". The earlier tasks-jury J-4 (jury/tasks.md) refuted the same point: the gap is between two epics of one unshipped spec, and ownership is stated. `commit` still writing `"claims": {}` (implement.py:557) is the T-4 work, and the artefact does not require E-1 to ship alone. The `parallel` default of 2 (implement.py:335) was set in the spec, not chosen by this epic.)

---
id: V-261106-wc4i
type: verdict
title: "implementation-E-1 gate for 2026-11-05-parallel-waves: approved (round 2)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-1:2026-11-05-parallel-waves"
outcome: approved
tier: high
paths: [".nio/specs/2026-11-05-parallel-waves/jury/implementation-E-1.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-1 jury ruled **approved** for `2026-11-05-parallel-waves` in round 2 (4 disposed, 8 fixed, 2 refuted). Ledger: `.nio/specs/2026-11-05-parallel-waves/jury/implementation-E-1.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| conformance | claude-code | claude-sonnet-5-5 | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | claude-sonnet-5-5 | approve |
| risk-rollback | claude-code | sonnet | approve |
## Reasons
- J-2 [minor/inconsistency] Hook events from a task's worktree are written to the worktree's own run folder, not the project root: disposed accepted-risk
- J-3 [minor/risk] Missing worktree silently falls back to the main tree: disposed accepted-risk
- J-5 [minor/gap] Claim cleans up worktrees only when git fails, not when a later step raises: disposed accepted-risk
- J-6 [minor/untestable] The rollback test for a failed claim has not been shown passing: disposed accepted-risk
## What was rejected
- J-1 No E-1 AC test has a passing result in the evidence: refuted (The round-2 results.json records `suite.result: "passed"` for the command `for f in tests/test_*.py; do uv run python "$f" || exit 1; done`, which stops at the first failing file. A pass therefore means `tests/test_waves.py` ran and exited 0. The eight E-1 tests exist at lines 38, 53, 105, 131, 152, 165, 62 and 85, which match the evidence entries, so the original stale-line-number and aborted-run situation is gone. The per-test `"unknown"` is how every entry in this file is recorded, including the AC-4, AC-7 and AC-9 tests, so the evidence format has no per-test result. The artefact shows no failing wave test, and the conformance juror's "not fixed" rests only on that recording format.)
- J-4 A wave claimed before E-2 lands its green as an empty commit and wipes the sibling's claim: refuted (E-1 stops short of landing on purpose. tasks.md puts landing and release (T-4) and the shelve and block path (T-5) in E-2, "Depends on: T-2". The earlier tasks-jury J-4 (jury/tasks.md) refuted the same point: the gap is between two epics of one unshipped spec, and ownership is stated. `commit` still writing `"claims": {}` (implement.py:557) is the T-4 work, and the artefact does not require E-1 to ship alone. The `parallel` default of 2 (implement.py:335) was set in the spec, not chosen by this epic.)

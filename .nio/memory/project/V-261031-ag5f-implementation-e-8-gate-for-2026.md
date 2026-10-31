---
id: V-261031-ag5f
type: verdict
title: "implementation-E-8 gate for 2026-10-27-implementation-jury: approved (round 2)"
answers: jury             # why | reuse | jury
date: 2026-10-31
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-8:2026-10-27-implementation-jury"
outcome: approved
tier: medium
paths: [".nio/specs/2026-10-27-implementation-jury/jury/implementation-E-8.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-8 jury ruled **approved** for `2026-10-27-implementation-jury` in round 2 (3 disposed, 5 fixed, 4 open, 2 refuted). Ledger: `.nio/specs/2026-10-27-implementation-jury/jury/implementation-E-8.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | approve |
| conformance | claude-code | claude-sonnet-5-5 | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | claude-sonnet-5-5 | approve |
## Reasons
- J-1 [major/gap] T-22: tests/test_tasks.py isn't in the epic's diff: disposed accepted-risk
- J-2 [major/gap] T-30: tests/test_flow.py isn't in the epic's diff: disposed accepted-risk
- J-3 [major/gap] T-33: tests/test_flow.py isn't in the epic's diff: disposed accepted-risk
- J-10 [minor/gap] AC-46's test does not prove the final fix check runs once the fix task is done: open
- J-12 [minor/inconsistency] Printed `unresolved` count includes minors: open
- J-13 [minor/gap] Test field for a finding with no cite: open
- J-14 [minor/inconsistency] Agent may dispose of a tampering finding, which CT-20 forbids: open
## What was rejected
- J-9 `jury evidence` is auto-allowed and runs commands that a task commit can change, with the user's full environment: refuted (The approved spec asks for this. CT-19 says "`jury evidence` added to `hooks.ALLOW`" (contracts.md:226). FR-40 only requires a throwaway copy and a time limit, and spec.md:346 records "no network isolation" as an accepted human risk. CT-3's "takes no command text" still holds, because the commands come only from config, `tests.md` and `quickstart.md` (contracts.md:27, 40).)
- J-11 Tampering finding disposed by an agent as fix-task: refuted (Already fixed at HEAD. `dispose` raises only when `f.get("tampering") and by != "human" and not routed` (jury.py:858). `tasks.append_fix` is the only caller that passes `routed=True` (tasks.py:418). A direct agent `dispose` of a tampering finding still raises ValueError as CT-20 says. The `routed` path is the spec's FR-26 route to a fix task.)

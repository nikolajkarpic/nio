---
id: V-261106-6py3
type: verdict
title: "implementation-E-2 gate for 2026-11-05-implement-followups: approved (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-2:2026-11-05-implement-followups"
outcome: approved
tier: medium
paths: [".nio/specs/2026-11-05-implement-followups/jury/implementation-E-2.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-2 jury ruled **approved** for `2026-11-05-implement-followups` in round 1 (3 open, 1 refuted). Ledger: `.nio/specs/2026-11-05-implement-followups/jury/implementation-E-2.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | approve |
| conformance | claude-code | claude-sonnet-5-5 | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | claude-sonnet-5-5 | approve |
## Reasons
- J-2 [minor/gap] "Proved later by T-n" is never checked against T-n: open
- J-3 [minor/risk] The NIO_PERF journey fails on a timing assertion and does not test the env strip it names: open
- J-4 [minor/scope] Speed-up research document is outside E-2's tasks: open
## What was rejected
- J-1 A deferral phrase can switch off red's file check for a task's own tests: refuted (The spec defines a deferral as the part of the `Test:` line that says "proved later" (Glossary "Deferred TC ID" and the Test line definition). It does not require a `;` before that part. For `TC-1 and TC-2 proved later by T-2`, `own` returns `[]`, and that is the outcome AC-6 requires, because a task with no own TC ID has no file to name. The second line, `TC-1 proved later by T-2 and TC-2`, breaks the shape that the decision at spec line 199 requires: "TC-n proved later by T-m" in its own `;` part. TC-2 sits in the deferral part, so treating it as deferred follows the spec's rule. The fix asks for a new rejection check on malformed lines. No FR or AC in the spec requires one.)

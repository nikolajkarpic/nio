---
id: V-261108-hvqp
type: verdict
title: "implementation-E-2 gate for 2026-11-08-explainer: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-08
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-2:2026-11-08-explainer"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-08-explainer/jury/implementation-E-2.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-2 jury ruled **rejected** for `2026-11-08-explainer` in round 1 (3 disposed, 1 dropped, 5 open, 1 refuted). Ledger: `.nio/specs/2026-11-08-explainer/jury/implementation-E-2.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| conformance | claude-code | sonnet | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | sonnet | approve |
## Reasons
- unresolved: J-1, J-2, J-10
- J-1 [major/gap] CT-1 counts as named when only CT-10 is in the map: disposed fix-task
- J-2 [major/gap] A path that resolves to a plan explainer but is spelled differently runs as topic mode: disposed fix-task
- J-10 [blocker/gap] AC-5 has no passing evidence: disposed fix-task
- J-3 [minor/gap] Text in `> ` lines is outside the walk-through word cap: open
- J-4 [minor/gap] Only the first fenced block of a section is checked or rendered: open
- J-5 [minor/risk] A plan without contracts.md passes the contract-ID check with no sign: open
- J-7 [minor/inconsistency] The contract-ID reader is not the helper the spec names: open
- J-9 [minor/risk] Contract ID match is a substring test: open
## What was rejected
- J-6 The host-format note is never printed: dropped (TC-35 not defined by the spec or contracts)
- J-8 The format note of CT-4 is not produced: refuted (tasks.md puts TC-35 (the host-format note) in T-16 of E-9, and T-4 serves only AC-9/AC-10 with TC-14/TC-15 (render and Node/fetch notes), so the format note is not part of E-2.)

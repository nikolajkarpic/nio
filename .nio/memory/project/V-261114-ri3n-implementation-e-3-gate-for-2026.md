---
id: V-261114-ri3n
type: verdict
title: "implementation-E-3 gate for 2026-11-08-project-onboarding: rejected (round 2)"
answers: jury             # why | reuse | jury
date: 2026-11-14
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-3:2026-11-08-project-onboarding"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-08-project-onboarding/jury/implementation-E-3.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-3 jury ruled **rejected** for `2026-11-08-project-onboarding` in round 2 (5 disposed, 2 open, 1 refuted). Ledger: `.nio/specs/2026-11-08-project-onboarding/jury/implementation-E-3.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| conformance | claude-code | sonnet | block |
| conformance | claude-code | sonnet | block |
| conformance | claude-code | sonnet | block |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | sonnet | block |
| security | claude-code | sonnet | approve |
## Reasons
- unresolved: J-1, J-2, J-3, J-5, J-8
- J-1 [major/contradiction] A damaged onboarding.json stops every pack, but the docs must never block the stage: disposed fix-task
- J-2 [major/risk] A symlinked project doc is read and sent to the model: disposed fix-task
- J-3 [major/gap] The apps line is read from anywhere in the spec, in one form only, and a wrong read drops docs silently: disposed fix-task
- J-5 [blocker/gap] AC-32 is proved only by a model-run test that the suite skips: disposed fix-task
- J-8 [major/gap] Quotes from project docs never ground: disposed fix-task
- J-4 [minor/risk] worker_pack splits the pack on a text match, so a memory record can corrupt its structure: open
- J-7 [minor/inconsistency] The spec skill passes `--slug` before the spec exists, against CT-16: open
## What was rejected
- J-6 Packs carry no stale line, though CT-9 and the accepted change require one: refuted (tasks.md schedules stale flags in packs for E-6 (T-22 serves AC-31 with TC-36 and TC-51, after T-21), and `docs_for` states the deferral in its ponytail note. The stale source records and the `stale` function do not exist yet (no `def stale` in onboard.py), so E-3 cannot emit the line.)

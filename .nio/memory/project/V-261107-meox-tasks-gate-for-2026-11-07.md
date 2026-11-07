---
id: V-261107-meox
type: verdict
title: "tasks gate for 2026-11-07-fewer-gate-turns: approved (round 2)"
answers: jury             # why | reuse | jury
date: 2026-11-07
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "tasks:2026-11-07-fewer-gate-turns"
outcome: approved
tier: medium
paths: [".nio/specs/2026-11-07-fewer-gate-turns/jury/tasks.md"]
tags: []
supersedes: []
---
## Ruling
The tasks jury ruled **approved** for `2026-11-07-fewer-gate-turns` in round 2 (3 fixed, 2 refuted). Ledger: `.nio/specs/2026-11-07-fewer-gate-turns/jury/tasks.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| executability | claude-code | claude-haiku-5-5 | approve |
## Reasons
- Every lens approved and no finding is open.
## What was rejected
- J-2 Nothing measures the skill's call count, so AC-11 and NFR-1 can pass while the skill still takes 31 calls: refuted (the finding says TC-18's Assert list omits the call-count clause, but tests.md:142 ends with "Every orchestrator call the steps name for scenario A is one TC-11 counts". TC-18 also requires "save each one's answer verbatim" to be gone and bans the per-step calls. A skill that kept 25 calls would name calls TC-11 doesn't count, so it would fail.)
- J-4 T-3 bundles most of the feature into one strong-tier task: refuted (this is a judgement about task size. Nothing in the artefact or in the tasks checker sets a limit on ACs, tests or files per task. T-3 already carries Mode "split" (tests written first by a separate worker), and a red test partway through a task is normal. The finding shows no case where the artefact as written allows a bad outcome.)

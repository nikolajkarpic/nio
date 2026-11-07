---
id: V-261107-ulgu
type: verdict
title: "implementation-E-5 gate for 2026-11-07-fewer-gate-turns: human (round 2)"
answers: jury             # why | reuse | jury
date: 2026-11-07
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-5:2026-11-07-fewer-gate-turns"
outcome: human
tier: medium
paths: [".nio/specs/2026-11-07-fewer-gate-turns/jury/implementation-E-5.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-5 jury ruled **human** for `2026-11-07-fewer-gate-turns` in round 2 (2 fixed, 1 merged, 7 open). Ledger: `.nio/specs/2026-11-07-fewer-gate-turns/jury/implementation-E-5.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | approve |
| conformance | claude-code | sonnet | approve |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | sonnet | approve |
## Reasons
- one list for the human; fix or accept each as risk: J-5
- J-5 [major/inconsistency] Plan-gate section still tells the orchestrator to read status with `nio jury check`: open
- J-3 [minor/risk] The skill-wording test skips the blocks most likely to keep old calls: open
- J-4 [minor/risk] The AC-11 call count is a hand-kept counter, not a measurement: open
- J-6 [minor/inconsistency] The skill's intro still names `nio check spec <slug> --gate` as a call to run: open
- J-7 [minor/inconsistency] CT-6 says the skill drops `nio jury check`, but the human-override line keeps it: open
- J-9 [minor/gap] The skill test skips the whole step-2 block, so the removed calls could come back unnoticed: open
- J-10 [minor/inconsistency] Stale `nio jury check` and record wording remains in the skill: open
## What was rejected
Nothing.

---
id: V-261108-xshg
type: verdict
title: "spec gate for 2026-11-08-explainer: human (round 2)"
answers: jury             # why | reuse | jury
date: 2026-11-08
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:2026-11-08-explainer"
outcome: human
tier: medium
paths: [".nio/specs/2026-11-08-explainer/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **human** for `2026-11-08-explainer` in round 2 (17 fixed, 3 merged, 2 open, 1 refuted). Ledger: `.nio/specs/2026-11-08-explainer/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| consistency | claude-code | haiku-5-5 | approve |
| logic | claude-code | sonnet | approve |
| scope | claude-code | haiku-5.5 | approve |
| testability | claude-code | sonnet | block |
## Reasons
- one list for the human; fix or accept each as risk: J-2, J-20
- J-2 [major/gap] Topic name goes straight into a file path: open
- J-20 [major/untestable] "Short" walk-through has no number: open
## What was rejected
- J-15 One spec bundles several separable features: refuted (Template permits a single spec (epic field is optional), and the stories already carry P1/P2/P3 priorities and an Independent test each, which is the slicing the spec uses; no rule or grill answer demands a split, so this is a preference, not a defect.)

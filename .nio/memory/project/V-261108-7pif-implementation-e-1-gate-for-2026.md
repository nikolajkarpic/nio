---
id: V-261108-7pif
type: verdict
title: "implementation-E-1 gate for 2026-11-08-explainer: human (round 3)"
answers: jury             # why | reuse | jury
date: 2026-11-08
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-1:2026-11-08-explainer"
outcome: human
tier: medium
paths: [".nio/specs/2026-11-08-explainer/jury/implementation-E-1.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-1 jury ruled **human** for `2026-11-08-explainer` in round 3 (1 disposed, 2 fixed, 1 merged, 8 open, 2 refuted). Ledger: `.nio/specs/2026-11-08-explainer/jury/implementation-E-1.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| conformance | claude-code | sonnet | approve |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | sonnet | block |
## Reasons
- the final fix check flagged these; fix or accept each as risk: J-1
- J-1 [major/risk] Node cap undercounts common Mermaid syntax, so oversized diagrams pass: open
- J-9 [major/ambiguity] A node whose ID starts with `end` is skipped: disposed accepted-risk
- J-3 [minor/gap] `check explainer` passes any existing file: open
- J-4 [minor/risk] `sections` drops `> ` lines from the walk-through and handles fences loosely: open
- J-5 [minor/risk] `render` runs `npx` from the caller's working directory: open
- J-10 [minor/inconsistency] Broken-diagram reason is read from both streams, not stderr: open
- J-11 [minor/inconsistency] `sections()` returns a `diagram` key that CT-1 does not list: open
- J-12 [minor/risk] SKIP prefix "end" drops any line starting with an ID like endpoint: open
- J-13 [minor/gap] sections leaves the Data model record lines in walk: open
## What was rejected
- J-6 AC-9 has no test and no check behind it: refuted (tasks.md E-1 gives T-1 only TC-5's `nodes` assertion, and the broken-diagram check belongs to T-4 in E-2 (Serves AC-9, Test TC-14, TC-15). check() is stated as "Only the missing-file error so far". That the error and test are absent is by plan, not a defect in E-1.)
- J-7 AC-5 is proven only for the node count, not for the failing check: refuted (tasks.md T-1 says "TC-5 (its `explain.nodes` assertion only; the check part is T-3's)". The `too many nodes` error and its CLI test belong to T-3 in E-2, so E-1 does not need them.)

---
id: V-261029-gzbf
type: verdict
title: "plan gate for 2026-10-29-implement-stage: rejected (round 3)"
answers: jury             # why | reuse | jury
date: 2026-10-29
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "plan:2026-10-29-implement-stage"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-10-29-implement-stage/jury/plan.md"]
tags: []
supersedes: []
---
## Ruling
The plan jury ruled **rejected** for `2026-10-29-implement-stage` in round 3 (15 fixed, 3 merged, 2 open, 1 refuted). Ledger: `.nio/specs/2026-10-29-implement-stage/jury/plan.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| architecture-fit | claude-code | opus | approve |
| logic | claude-code | sonnet | approve |
| risk-rollback | claude-code | opus | block |
| test-proof | claude-code | opus | block |
| test-proof | claude-code | opus | block |
| test-proof | claude-code | opus | block |
## Reasons
- unresolved: J-12, J-20
- J-12 [major/gap] Adding `Mode` to FIELDS strands every tasks.md approved before the change: open
- J-20 [blocker/inconsistency] Tests that never write the planned test still run it, now that impl() commits none: open
## What was rejected
- J-10 The Red decision table accepts a missing program on an unknown runner, and CT-7 gives no order that overrides it: refuted (CT-7's `Fails:` list is a set of independent refusals, and the cause bullet ("a time limit or a missing program (CT-1) → `refused: <cause>`") needs no ordering to override the exit-code check. CT-1 sets `cause` for exit 127 regardless of runner, and FR-44 says "treat it as a refused red". The tension is with the spec's Red table row 4, which is a spec issue and not something the plan leaves open.)

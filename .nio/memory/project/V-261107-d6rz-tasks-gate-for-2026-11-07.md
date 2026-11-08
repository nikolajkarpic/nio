---
id: V-261107-d6rz
type: verdict
title: "tasks gate for 2026-11-07-route-downgrade: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-07
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "tasks:2026-11-07-route-downgrade"
outcome: rejected
tier: low
paths: [".nio/specs/2026-11-07-route-downgrade/jury/tasks.md"]
tags: []
supersedes: []
---
## Ruling
The tasks jury ruled **rejected** for `2026-11-07-route-downgrade` in round 1 (5 open). Ledger: `.nio/specs/2026-11-07-route-downgrade/jury/tasks.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| executability | claude-code | opus | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-4, J-5
- J-1 [major/untestable] AC-3's `nio flow done` refusal may already happen today, and "its stage" has two readings: open
- J-2 [major/untestable] T-1 asserts no "route-change stop", but no such stop exists yet to match against: open
- J-3 [major/gap] Recording the route on a first line written by `nio flow done` is in the fix but in no test: open
- J-4 [minor/gap] EB-3 refuses "every writing `nio flow` command", but T-3 tests and names only `done`: open
- J-5 [minor/ambiguity] No rule for efforts whose history has no recorded route: open
## What was rejected
Nothing.

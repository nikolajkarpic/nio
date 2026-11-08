---
id: V-261108-m7ob
type: verdict
title: "implementation-E-1 gate for 2026-11-08-project-onboarding: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-08
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-1:2026-11-08-project-onboarding"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-08-project-onboarding/jury/implementation-E-1.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-1 jury ruled **rejected** for `2026-11-08-project-onboarding` in round 1 (4 disposed, 6 merged, 3 open, 2 refuted). Ledger: `.nio/specs/2026-11-08-project-onboarding/jury/implementation-E-1.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| conformance | claude-code | sonnet | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | sonnet | block |
| security | claude-code | sonnet | block |
## Reasons
- unresolved: J-2, J-3, J-5, J-7
- J-2 [major/contradiction] Outside a git repo the scan reports success with "nothing found": disposed fix-task
- J-3 [major/gap] Non-ASCII or quoted paths are dropped silently: disposed fix-task
- J-5 [major/inconsistency] Output order and the CLI shape don't match the contract, and the contract tests are missing: disposed fix-task
- J-7 [major/contradiction] The category table is narrower than CT-1, and `docs/*.md` is in the wrong category: disposed fix-task
- J-10 [minor/risk] The exit-code assertion in the ignored-files test is never enforced: open
- J-12 [minor/gap] The skip test's assertion passes whatever the scan prints: open
- J-13 [minor/inconsistency] Output is sorted by path only and git's quoting is not undone: open
## What was rejected
- J-6 A symlink is listed and its target is read: refuted (Symlink skipping is T-13's work (AC-48), and T-13 depends on T-1, so T-1 not yet skipping symlinks is planned sequencing. T-1 serves only AC-1..4.)
- J-14 Symlinks are followed and hashed: refuted (Symlink skipping belongs to T-13 (AC-48), which depends on T-1, and T-1 serves only AC-1..4, so T-1 following symlinks is sequenced and not a defect of T-1.)

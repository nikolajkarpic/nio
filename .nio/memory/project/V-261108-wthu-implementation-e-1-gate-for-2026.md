---
id: V-261108-wthu
type: verdict
title: "implementation-E-1 gate for 2026-11-08-project-onboarding: approved (round 2)"
answers: jury             # why | reuse | jury
date: 2026-11-08
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-1:2026-11-08-project-onboarding"
outcome: approved
tier: medium
paths: [".nio/specs/2026-11-08-project-onboarding/jury/implementation-E-1.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-1 jury ruled **approved** for `2026-11-08-project-onboarding` in round 2 (1 disposed, 3 fixed, 6 merged, 3 open, 2 refuted). Ledger: `.nio/specs/2026-11-08-project-onboarding/jury/implementation-E-1.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | approve |
| conformance | claude-code | sonnet | approve |
| consistency | claude-code | haiku-5-5 | approve |
| correctness | claude-code | sonnet | approve |
| security | claude-code | sonnet | approve |
## Reasons
- J-5 [major/inconsistency] Output order and the CLI shape don't match the contract, and the contract tests are missing: disposed accepted-risk
- J-10 [minor/risk] The exit-code assertion in the ignored-files test is never enforced: open
- J-12 [minor/gap] The skip test's assertion passes whatever the scan prints: open
- J-13 [minor/inconsistency] Output is sorted by path only and git's quoting is not undone: open
## What was rejected
- J-6 A symlink is listed and its target is read: refuted (Symlink skipping is T-13's work (AC-48), and T-13 depends on T-1, so T-1 not yet skipping symlinks is planned sequencing. T-1 serves only AC-1..4.)
- J-14 Symlinks are followed and hashed: refuted (Symlink skipping belongs to T-13 (AC-48), which depends on T-1, and T-1 serves only AC-1..4, so T-1 following symlinks is sequenced and not a defect of T-1.)

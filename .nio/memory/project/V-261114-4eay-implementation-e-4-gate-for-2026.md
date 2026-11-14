---
id: V-261114-4eay
type: verdict
title: "implementation-E-4 gate for 2026-11-08-project-onboarding: approved (round 3)"
answers: jury             # why | reuse | jury
date: 2026-11-14
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-4:2026-11-08-project-onboarding"
outcome: approved
tier: medium
paths: [".nio/specs/2026-11-08-project-onboarding/jury/implementation-E-4.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-4 jury ruled **approved** for `2026-11-08-project-onboarding` in round 3 (1 disposed, 5 fixed, 12 open). Ledger: `.nio/specs/2026-11-08-project-onboarding/jury/implementation-E-4.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | approve |
| conformance | claude-code | sonnet | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | sonnet | approve |
| security | claude-code | sonnet | approve |
## Reasons
- J-6 [major/gap] E2E-only ACs have no run evidence: disposed accepted-risk
- J-4 [minor/risk] `check spec` accepts any directory name as an app, including `..`, and a spec can drop `apps:` to bypass the check: open
- J-5 [minor/risk] `stale` follows any path a doc records and crashes on an undecodable doc: open
- J-7 [minor/gap] AC-41's reconcile half is not proved: open
- J-9 [minor/contradiction] `nio onboard backup` on a symlinked agent file stores the target under the target's name: open
- J-10 [minor/inconsistency] A progress file without an `apps` key passes the reader and crashes `confirm` with a traceback: open
- J-11 [minor/inconsistency] The functions CT-4 names are not in the code, and the code's `act` takes a different shape: open
- J-13 [minor/risk] AC-40 e2e slice start can go negative and silently empty the check: open
- J-14 [minor/gap] Backup test's outside-the-repo case never reaches the outside-repo branch: open
- J-15 [minor/gap] `--app` without `=<path>` is accepted and saved with an empty path: open
- J-16 [minor/gap] `nio onboard backup` copies a secrets file into `.nio/backup/`: open
- J-17 [minor/ambiguity] The inline-secret rule says "write" but AC-39 needs the token kept out of the transcript too: open
- J-18 [minor/risk] `stale` follows any path in a source record, including paths outside the repo: open
## What was rejected
Nothing.

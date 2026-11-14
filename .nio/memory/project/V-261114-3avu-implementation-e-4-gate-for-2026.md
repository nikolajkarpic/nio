---
id: V-261114-3avu
type: verdict
title: "implementation-E-4 gate for 2026-11-08-project-onboarding: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-14
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-4:2026-11-08-project-onboarding"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-08-project-onboarding/jury/implementation-E-4.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-4 jury ruled **rejected** for `2026-11-08-project-onboarding` in round 1 (6 disposed, 12 open). Ledger: `.nio/specs/2026-11-08-project-onboarding/jury/implementation-E-4.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| conformance | claude-code | sonnet | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | sonnet | block |
| security | claude-code | sonnet | approve |
## Reasons
- unresolved: J-1, J-2, J-3, J-6, J-8, J-12
- J-1 [major/risk] A failed copy leaves a truncated backup that the next call reports as the kept original: disposed fix-task
- J-2 [major/gap] SECRETS hides secret-named IaC from the iac category, and the pattern list has gaps: disposed fix-task
- J-3 [major/gap] Nothing in the CLI checks that a confirmed doc has source records or is free of secret values: disposed fix-task
- J-6 [major/gap] E2E-only ACs have no run evidence: disposed fix-task
- J-8 [major/contradiction] A spec's apps line that keeps the template comment names the wrong apps, so a one-app worker pack gets every app's docs: disposed fix-task
- J-12 [major/gap] Skill rule for an inline secret only covers files the agent never opens: disposed fix-task
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

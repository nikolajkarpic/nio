---
id: V-261114-h4ll
type: verdict
title: "implementation-E-6 gate for 2026-11-08-project-onboarding: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-14
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-6:2026-11-08-project-onboarding"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-08-project-onboarding/jury/implementation-E-6.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-6 jury ruled **rejected** for `2026-11-08-project-onboarding` in round 1 (4 disposed, 1 merged, 8 open). Ledger: `.nio/specs/2026-11-08-project-onboarding/jury/implementation-E-6.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| conformance | claude-code | sonnet | block |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | sonnet | block |
| security | claude-code | sonnet | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-5
- J-1 [major/gap] A partly reconciled session marks every new file as seen, so unreached new files never come back: disposed fix-task
- J-2 [major/gap] Quoted or non-ASCII paths are silently dropped from the changed-files list: disposed fix-task
- J-3 [major/risk] The ref goes to git unguarded, so a leading dash becomes a git option: disposed fix-task
- J-5 [major/gap] Four AC proofs are e2e tests that only skip-pass without NIO_E2E: disposed fix-task
- J-4 [minor/ambiguity] The skill requires "the scan's new hash" but gives no way to get one: open
- J-7 [minor/gap] The e2e guards for AC-23 and AC-44 miss half of what each AC states: open
- J-8 [minor/risk] Source records can point outside the repo and are now hashed on every status and pack: open
- J-9 [minor/inconsistency] The reconcile list can name a secrets file, against the skill's rule: open
- J-10 [minor/inconsistency] AC-23 scenario has the dev decline an infra.md edit that the spec's rule excludes: open
- J-11 [minor/inconsistency] T-70 Serves line omits AC-25 while its Test line covers TC-40: open
- J-12 [minor/inconsistency] confirm saves seen with secrets entries, against CT-4: open
- J-13 [minor/inconsistency] CT-3 names one progress writer, but reconciled writes the file inline: open
## What was rejected
Nothing.

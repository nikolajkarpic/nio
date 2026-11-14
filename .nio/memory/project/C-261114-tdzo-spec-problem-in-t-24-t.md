---
id: C-261114-tdzo
type: change
title: "Spec problem in T-24: T-24 (AC-23, AC-42, AC-44; TC-38, TC-40, TC-41, TC-43): Reconcile e2e: changed files, nothing to do, declines and deletions; a task whose test must fail before the code."
answers: why              # why | reuse | jury
date: 2026-11-14
by: "orchestrator / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-08-project-onboarding/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: T-24 (AC-23, AC-42, AC-44; TC-38, TC-40, TC-41, TC-43): Reconcile e2e: changed files, nothing to do, declines and deletions; a task whose test must fail before the code.

The code shows: skills/reconcile-onboarding/SKILL.md (T-23) already covers changed files, nothing to reconcile, declined edits (hash recorded) and deleted sources. The new tests pass on arrival, so `nio flow red` cannot be proved.
## Proposed change
Retire T-24 as already delivered and land its tests as regression guards in a direct-mode fix task.

Handoff: 883053c9342e9e4cffcf71b824c74e9ff12a349c5b6a086df59f9f7da29c912e
## Human decision
Accepted by the human 2026-11-14 (standing ruling for tasks whose tests pass on arrival): retire T-24; its tests land as regression guards in fix task T-70 (direct mode).

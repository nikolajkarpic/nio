---
id: C-261114-fv3l
type: change
title: "Spec problem in T-62: T-62 single mode: red on the test before the code, then green on the code."
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
The spec says: T-62 single mode: red on the test before the code, then green on the code.

The code shows: The first red froze src/nio/onboard.py in a state with the new check switched off, so green refuses the finished code (`changed since red; prove red again`) and a new red refuses (`the test passes before the code exists`). No spec change: this is a flow reset only.
## Proposed change
Unblock T-62 (frozen files dropped), reclaim it, red on the tests against HEAD's code, then apply the saved code and green.

Handoff: 654e227459da037a69199c37031a4295f8935f1aecc00373f757a306ecf473a3
## Human decision
Accepted by the human 2026-11-14 as a flow reset only: no spec or task change; T-62 is unblocked and re-proved red then green.

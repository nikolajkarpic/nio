---
id: C-261114-47ju
type: change
title: "Spec problem in T-20: T-20 (AC-13; TC-23): An empty repo grills three docs and is done; a task whose test must fail before the code."
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
The spec says: T-20 (AC-13; TC-23): An empty repo grills three docs and is done; a task whose test must fail before the code.

The code shows: skills/onboard/SKILL.md step 1 (T-15, commit 0b103e2) already runs `nio onboard start --empty` for a repo with no manifest and no code, so only product, personas and principles are grilled. The new tests pass on arrival, so `nio flow red` cannot be proved.
## Proposed change
Retire T-20 as already delivered and land its tests as regression guards in a direct-mode fix task.

Handoff: 9a473ba618894e3be6156086dcd7603c1037c2a1d617eb209a3569f46ad52380
## Human decision
Accepted by the human 2026-11-14 (standing ruling for tasks whose tests pass on arrival): retire T-20; its tests land as regression guards in fix task T-67 (direct mode).

---
id: C-261115-duou
type: change
title: "Spec problem in T-4: T-4 / AC-13 (the cost section prints each stage's tokens and seconds, the unattributed line and the total); the pack's TC-15 must fail first"
answers: why              # why | reuse | jury
date: 2026-11-15
by: "driver / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-15-effort-drilldown-install/spec.md"
outcome: accepted         # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: T-4 / AC-13 (the cost section prints each stage's tokens and seconds, the unattributed line and the total); the pack's TC-15 must fail first

The code shows: tools/claude-mods/nio-status-pane/hooks/register.test.tsx:355 test 'AC-13 cost as the CLI gives it' passes now. The full file runs 23 pass, 0 fail, including AC-13 cost, AC-9/AC-11 empty sections, and AC-16/AC-17 context line, so the pane code already does what T-4 plans
## Proposed change
Apply the pass-on-arrival standing rule (#49): retire T-4's tests and open a direct fix task if T-4 has any remaining work. Otherwise mark T-4 as already satisfied

Handoff: cab70e2c51e9a37fd79e40bc51b2331aac958dbc6eb521ce8416abaef65b6559
## Human decision
Accepted under the human's standing pass-on-arrival rule (#49; precedents C-261114-lqou, C-261115-ftot) on 2026-11-15: retire T-4 (empty sections, cost lines and context line delivered by T-3, cc83732; its five tests pass on arrival, 23 pass / 0 fail) and land its tests as regression guards in fix task T-16 (direct mode). T-4's dependents now depend on T-16.

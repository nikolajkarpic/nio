---
id: C-261030-abpr
type: change
title: "Spec problem in T-4: T-4 (E-2): make the flow refuse the next claim while a gate is open; T-27 (E-8): `nio flow done implementation-E-n` writes the epic line; CT-17: claim refuses the next epic until the epic line exists"
answers: why              # why | reuse | jury
date: 2026-10-30
by: "orchestrator / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-10-27-implementation-jury/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The tasks say: T-4 (E-2): make the flow refuse the next claim while a gate is open; T-27 (E-8): `nio flow done implementation-E-n` writes the epic line; CT-17: claim refuses the next epic until the epic line exists

The code shows: T-4 is E-2's last task and src/nio/implement.py:540 is the only writer of an epic line today, so once T-4 lands T-5 can never be claimed: the build stops itself until T-27, which can't be reached
## Proposed change
Build the wait rule last. Retire T-4, T-27, T-28 and T-29 and re-add them under E-8's Fixes as T-30 (T-27 without its T-4 dependency and TC-69), T-31 (T-28), T-32 (T-29) and T-33 (T-4 plus TC-69, depending on the other three). In plan.md, CT-17 and TC-70 move from US-1 to US-6. E-2 then has no epic line of its own, and E-2 and E-8 are closed with the real gate at the end.
Handoff: f9ad459ea83d8151eaebf55d196072b098510fbd1f97dca8dfa835a08612cf79
## Human decision
Accepted 2026-10-30, when asked how to fix the build blocking itself: "Move it to the end".

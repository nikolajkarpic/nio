---
id: C-261114-lqou
type: change
title: "Spec problem in T-11: T-11 (AC-34, AC-35, AC-46; TC-15, TC-16, TC-47): multi-app packs hold the right apps' docs, labelled; a split task whose test must fail before the code."
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
The spec says: T-11 (AC-34, AC-35, AC-46; TC-15, TC-16, TC-47): multi-app packs hold the right apps' docs, labelled; a split task whose test must fail before the code.

The code shows: src/nio/onboard.py `_named`, `_pairs`, `docs_for` (built by T-6/T-7 and fix T-55) already select apps from the spec's `apps` front matter, label docs `web/stack.md`, and give every app when the spec names none. The three new tests TC-15, TC-16, TC-47 pass on arrival, also on the code before T-55 (8c6c021), so `nio flow red` cannot be proved and green refuses (`T-11 has no failing test first`).
## Proposed change
Retire T-11 as already delivered by T-6/T-7/T-55 and land its three tests as regression guards (with a direct-mode task or in T-15), or let T-11 run in direct mode.

Handoff: 220b61644af03794fa1448c4a3e996902a98cbfb9da57810511b261761aa7386
## Human decision
Accepted by the human 2026-11-14: retire T-11 (delivered by T-6, T-7 and T-55) and land its three tests as regression guards in fix task T-58 (direct mode).

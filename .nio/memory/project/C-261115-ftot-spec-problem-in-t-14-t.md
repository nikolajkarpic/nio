---
id: C-261115-ftot
type: change
title: "Spec problem in T-14: T-14 'Add topic mode to the skill and its end-to-end tests (CT-11)'; TC-23, TC-24 and TC-27 should fail first, then pass once topic mode is added to skills/explain/SKILL.md"
answers: why              # why | reuse | jury
date: 2026-11-15
by: "driver / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-08-explainer/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: T-14 'Add topic mode to the skill and its end-to-end tests (CT-11)'; TC-23, TC-24 and TC-27 should fail first, then pass once topic mode is added to skills/explain/SKILL.md

The code shows: skills/explain/SKILL.md:56-63 already has the full '## Topic mode (given a topic)' section, added by T-8 (commit 2646c1c), with the continue:/new: steps and the -explainer-<n>.md note. All three new tests pass on a real model before any skill change; nio flow red refused: the test passes before the code exists.
## Proposed change
Apply the pass-on-arrival standing rule (#49): retire T-14's code work and keep the three tests (written in tests/test_explain_e2e.py), as a direct task that records them.

Handoff: 55ab08568d83a9e9900e18222ebcd6fc742f13f7d9e08c31fa468474d4260338
## Human decision
Accepted by the human (standing pass-on-arrival rule, full autonomy granted 2026-11-08) on 2026-11-15: retire T-14 (topic mode delivered by T-8, 2646c1c) and land its three tests as regression guards in fix task T-30 (direct mode).

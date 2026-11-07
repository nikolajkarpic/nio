---
id: C-261107-tpmk
type: change
title: "Spec problem in T-3: TC-12 (T-3, Depends on: T-1, T-2): `.claude/agents/nio-logic.md` exists and its `tools:` line holds `Write` (the step rendered the agents)."
answers: why              # why | reuse | jury
date: 2026-11-07
by: "orchestrator / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-07-fewer-gate-turns/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: TC-12 (T-3, Depends on: T-1, T-2): `.claude/agents/nio-logic.md` exists and its `tools:` line holds `Write` (the step rendered the agents).

The code shows: src/nio/agents/logic.md:6 is `tools: [read]`, which renders as Read, Grep, Glob (src/nio/agents.py:15 and :99). Giving the cards a write tool is T-4 (tasks.md line 50: 'Give juror cards a write tool limited by instruction'), and T-4 is not a dependency of T-3. The last assert of tests/test_jury.py:1839 (test_ac12_first_review_packs) cannot pass until T-4's card edits land.
## Proposed change
Add T-4 to T-3's `Depends on:` line, or move TC-12's `tools:` assert to T-4. I didn't edit the frozen test or the cards, which are outside T-3's Files.

Handoff: 6718225a2dec3d91e19da00e892575c210a19bd6331e4fd106e746e200acb7d8
## Human decision
Accepted (delegated to the orchestrator by the human): TC-12 keeps only that the step rendered `nio-logic.md`; that it grants `Write` stays TC-8's (T-4). T-3's dependencies are unchanged, since T-4 depends on T-3.

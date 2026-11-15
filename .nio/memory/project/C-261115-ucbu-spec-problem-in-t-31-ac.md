---
id: C-261115-ucbu
type: change
title: "Spec problem in T-31: AC-24 (FR-23): Given a worktree with no `.venv/bin/nio` and a `nio` on PATH, when the pane refreshes, then it lists that worktree's efforts from the PATH `nio`; with neither, the row reads `nio not found`. AC-11 (FR-12) in the current spec.md:80 is about the drill-down tasks section, not venv handling."
answers: why              # why | reuse | jury
date: 2026-11-15
by: "driver / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-15-effort-drilldown-install/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: AC-24 (FR-23): Given a worktree with no `.venv/bin/nio` and a `nio` on PATH, when the pane refreshes, then it lists that worktree's efforts from the PATH `nio`; with neither, the row reads `nio not found`. AC-11 (FR-12) in the current spec.md:80 is about the drill-down tasks section, not venv handling.

The code shows: The deleted test 'AC-11: a worktree with no venv shows an error and runs nothing' (main:tools/claude-mods/nio-status-pane/hooks/register.test.tsx:202) asserts 'nio-new: no .venv: run uv sync'. register.tsx:57-59 (nioFor) now falls back to PATH `nio` and returns 'nio not found' (NO_NIO) when it is missing. The old test cannot pass against this code; its replacements are the two 'AC-24 nio on PATH' tests at register.test.tsx:207 and :215.
## Proposed change
Treat the deletion as intended: the old AC-11 venv test was superseded by the two AC-24 tests, and its 'AC-11' label is from an older spec numbering. Retire T-31 and accept it at the jury. Alternative: restore the old test and change the register.tsx fallback, which contradicts AC-24.

Handoff: 81b97c8ae606cb16d820136e2cf00ccfaa2ae0acd2ac22bf9a2ac72ee975a147
## Human decision
Pending.

## Human decision
Accepted by the human on 2026-11-15 in the orchestrator session: "Retire it, deletion intended: the old no-venv test is superseded by the two AC-24 PATH-fallback tests (register.test.tsx:207, :215); retire T-31."

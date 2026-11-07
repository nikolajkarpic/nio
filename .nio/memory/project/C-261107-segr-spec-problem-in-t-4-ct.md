---
id: C-261107-segr
type: change
title: "Spec problem in T-4: CT-5 / FR-9: every juror card gets `tools: [read, write]`, limited to its output file by the card's instruction (grill Q1)."
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
The spec says: CT-5 / FR-9: every juror card gets `tools: [read, write]`, limited to its output file by the card's instruction (grill Q1).

The code shows: tests/test_evidence.py:1197-1198 (test_it_can_open_any_project_file_and_can_t, from the implementation-jury effort) asserts the conformance, correctness, risk-rollback, security, adversary and consistency cards are read-only (`tools == ["read"]`, rendered `tools: "Read, Grep, Glob"`). T-4's review fails on it.
## Proposed change
Update those two assertions to `["read", "write"]` and `tools: "Read, Grep, Glob, Write"`; the rest of the test (any project file, building a pack writes nothing, no shell on Codex) stays.

Handoff: 3a04ecd9324503454ac94d35a56f55c6022dabc397b47bc1980b936905cf981f
## Human decision
Accepted (delegated to the orchestrator by the human): FR-9 (grill Q1) deliberately gives juror cards a write tool, so the older read-only assertion in tests/test_evidence.py follows CT-5; the rest of that test stays.

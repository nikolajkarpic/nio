---
id: C-261115-lncp
type: change
title: "Spec problem in T-21: T-21 (and T-22..T-30, same root cause) asks for a passing test of AC-5 within register.tsx, types/index.d.ts and register.test.tsx (plus flow.py/test_flow.py for some siblings). TC-6 names the test register.test.tsx:AC-5 back to the list."
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
The spec says: T-21 (and T-22..T-30, same root cause) asks for a passing test of AC-5 within register.tsx, types/index.d.ts and register.test.tsx (plus flow.py/test_flow.py for some siblings). TC-6 names the test register.test.tsx:AC-5 back to the list.

The code shows: That test already exists and passes: `claude plugin test tools/claude-mods/nio-status-pane` gives 24 pass, 0 fail, including AC-5 back to the list, AC-13, AC-16/AC-17, AC-9/AC-11, AC-24 and AC-29/AC-30. The pr gate reports them as didn't run because its evidence run never runs them: tests.suite in .nio/config.json covers only tests/test_*.py, and src/nio/evidence.py collect() reads per-test results with ^ok (\S+)::(\S+), which cannot match pane test names that hold spaces. No change inside any of these tasks' Files lists can fix that, and red cannot fail on a test that already passes.
## Proposed change
Replace T-21..T-30 with one fix task whose Files are tests/test_pane.py (new: runs `claude plugin test tools/claude-mods/nio-status-pane` and prints `ok <file>::<name>` / `FAIL <file>::<name>` lines and a `ran <n> tests, <m> failed` line), src/nio/evidence.py (let the ok/skip pattern take a name with spaces, e.g. ^ok (\S+)::(.+)$) and .nio/config.json if the suite glob needs it; mode direct, since the pane tests already pass. Retire T-21..T-30 as duplicates of it.

Handoff: 322ad132b4ae8995073c0e8a78704a99e5e3afeba28fbb7aefe00622691630b9
## Human decision
accepted under the human's standing pass-on-arrival rule; matches the human's pr-gate ruling 'Fix: fix tasks hook the pane tests (claude plugin test) into the review's test run and make the install test check the closing message, so the review proves them.' (#49; precedents C-261114-lqou, C-261115-ftot, C-261115-duou) on 2026-11-15: retire T-21..T-30 as duplicates (their pane tests pass on arrival, 24 pass / 0 fail) and add direct-mode fix task T-36 (tests/test_pane.py wrapper, evidence.py and implement.SUMMARY["self-check"] FAIL pattern reading names with spaces; .nio/config.json unchanged, its tests/test_*.py glob already picks up test_pane.py).

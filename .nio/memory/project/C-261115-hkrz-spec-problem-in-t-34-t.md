---
id: C-261115-hkrz
type: change
title: "Spec problem in T-34: T-34 / J-31 (a malformed ledger or history line crashes flow show instead of failing one section); the pack's TC-1 (test_show_timeline_lists_stage_changes) must fail first"
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
The spec says: T-34 / J-31 (a malformed ledger or history line crashes flow show instead of failing one section); the pack's TC-1 (test_show_timeline_lists_stage_changes) must fail first

The code shows: tests/test_flow.py test_show_timeline_lists_stage_changes passes on arrival, so red cannot fail on it; it never feeds show a malformed ledger or history line, so it proves nothing about J-31. The real bug stands: show() in src/nio/flow.py catches only (ValueError, OSError) around juries(), so a ledger shaped wrong (e.g. jury/zz.json holding {}) raises past it, and a malformed history line can do the same around timeline(). A worker's unproven edit (per-section catch plus test_show_survives_malformed_ledger) is shelved in .nio/runs/R-261115-x6cb/T-34.patch. Separately, a broken gate ledger (plan.json) still crashes jury.compose's where() before show reaches its sections; that is outside this task's files.
## Proposed change
Apply the pass-on-arrival standing rule (#49): retire T-34 and add one direct-mode fix task under E-8 (Files: src/nio/flow.py, tests/test_flow.py; Serves: CT-2, FR-13, J-31) carrying a real test for J-31 (a malformed jury ledger and a malformed history line each fail only their own section; flow show exits 0 with the other sections present) plus the fix in flow.show.

Handoff: d859ddd608232a4f2e58fda478b5ecf60cf6ed6fbe21dc437e010e485e6584f4
## Human decision
Accepted under the human's standing pass-on-arrival rule (T-34's named test passed on arrival; the real bug J-31 is fixed by the new direct fix task) (#49; precedents C-261115-duou, C-261115-lncp) on 2026-11-15: retire T-34 (TC-1, test_show_timeline_lists_stage_changes, passes on arrival) and add direct-mode fix task T-37 (src/nio/flow.py, tests/test_flow.py) with a real test for J-31. The worker's shelved diff (.nio/runs/R-261115-x6cb/T-34.patch) is a starting point only. The plan.json crash in jury.compose's where() stays out of scope.

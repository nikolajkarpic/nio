---
id: C-261028-tk42
type: change
title: "Flow-state tests: deviations from the planned tests found while building"
answers: why              # why | reuse | jury
date: 2026-10-28
by: "agent / claude-code / opus"                # role / host / model, or human
run: "R-261028-bqep"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-28-flow-state/tests.md"# the spec, plan or record that is wrong
outcome: accepted         # pending | accepted | rejected
paths: [".nio/specs/2026-10-28-flow-state/tests.md", "tests/test_flow.py"]
tags: [flow-state, tests]
supersedes: []
---
## What is wrong
While building `nio flow`, some planned tests contradicted the spec or the fixtures. The builder kept each test's intent, followed the contract and the spec, and commented each deviation in `tests/test_flow.py`.
- TC-5: calls `flow.start` with `by=` (test-helper rule; nothing else changes).
- TC-73: `start` resumes a parked effort (FR-31, CT-10), so after the roll-forward the test asserts the `park` then `resume` lines, not `pause` still set.
- TC-55: the pending change record the test files applies once the effort is no longer abandoned (FR-35, FR-38), so the status reads `waiting_for_human: <C> pending`, not `working`.
- TC-39 and TC-71: the edit goes where the checks allow (an epic's text, the Summary), since planned tasks are frozen and the end of spec.md is `## Open points`; `next` is called with `--by` to record the back line (CT-9).
- TC-14: the grilling guard adds one line per open point left, so AC-14's OP-3 is named; `spec.py` is unchanged.
- TC-16, TC-46, TC-47: the fixture spec has no AC-4, so AC-2 is left without a task instead.
- TC-13, TC-22, TC-36: "already passed" (FR-17) means before where history last stands, so the effort is started before its files pass.
- TC-45: the spec ledger is moved to round 2 and committed so the gate stays passed while the rounds sum to 4.
## Proposed change
Keep the approved test plan text; this record is the reference for each deviation, cited by the code comments.
## Human decision
Accepted by the human (2026-10-28): record only, the test plan text stays as approved.

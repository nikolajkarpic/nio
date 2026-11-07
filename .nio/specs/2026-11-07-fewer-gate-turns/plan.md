---
slug: 2026-11-07-fewer-gate-turns
architecture: none               # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: drive a jury gate in fewer orchestrator calls

## Build order
### US-4 A copied lens name no longer misfiles findings
- Delivers: CT-4
- Tests: TC-9, TC-10

### US-2 Dispose several findings in one call
- Delivers: CT-3
- Tests: TC-6, TC-7, TC-15

### US-1 One command runs a gate step
- Depends on: US-4
- Delivers: CT-1, CT-2
- Tests: TC-1, TC-2, TC-3, TC-4, TC-5, TC-12, TC-13, TC-14, TC-16, TC-17, TC-19

### US-3 Jurors write their own output file
- Depends on: US-1
- Delivers: CT-5
- Tests: TC-8

### US-5 The jury skill uses the shorter path
- Depends on: US-1, US-2, US-3
- Delivers: CT-6
- Tests: TC-11, TC-18
- Scenario: QS-1, QS-2

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1 | TC-1, TC-5 |
| FR-2 | CT-1, CT-2 | TC-1 |
| FR-3 | CT-1 | TC-2, TC-5, TC-14 |
| FR-4 | CT-1, CT-2 | TC-2 |
| FR-5 | CT-1 | TC-3, TC-14 |
| FR-6 | CT-1 | TC-4, TC-13 |
| FR-7 | CT-3 | TC-6, TC-15 |
| FR-8 | CT-3 | TC-7 |
| FR-9 | CT-5 | TC-8 |
| FR-10 | CT-4 | TC-9, TC-10 |
| FR-11 | CT-6 | TC-11 |
| FR-12 | CT-2 | TC-12, TC-17 |
| FR-13 | CT-1, CT-2 | TC-5 |
| FR-14 | CT-1 | TC-16 |
| AC-1 | CT-1, CT-2 | TC-1 |
| AC-2 | CT-1, CT-2 | TC-2 |
| AC-3 | CT-1 | TC-3 |
| AC-4 | CT-1 | TC-4 |
| AC-5 | CT-1, CT-2 | TC-5 |
| AC-6 | CT-3 | TC-6 |
| AC-7 | CT-3 | TC-7 |
| AC-8 | CT-5 | TC-8 |
| AC-9 | CT-4 | TC-9 |
| AC-10 | CT-4 | TC-10 |
| AC-11 | CT-6 | TC-11 |
| AC-12 | CT-2 | TC-12, TC-17 |
| AC-13 | CT-1 | TC-13 |
| AC-14 | CT-1 | TC-14 |
| AC-15 | CT-3 | TC-15 |
| AC-16 | CT-1 | TC-16 |
| NFR-1 | CT-6 | TC-18 |
| NFR-2 | CT-2 | none |

## Decisions
- The step's own state is a `packs/step.json` in the run folder (gitignored scratch, like the packs), not a new ledger field: no schema change [agent].
- The step does not decide the consistency or scope triggers: the orchestrator still runs `nio pack` and passes `--add`, as the skill does today; the step only builds the consistency lens's memory pack [agent].
- Escalation stays the skill's: the step only stops before composing an outcome and says to escalate (spec Non-goals) [agent].
- The e2e half of AC-8 (a real juror writes only its file) is QS-2, manual: no test here runs a real model; `NIO_E2E` lens tests stay as they are [agent].
- US-4 comes first because the step's FR-14 check reads the lens from the file name the same way `merge` will [agent].

## Open points

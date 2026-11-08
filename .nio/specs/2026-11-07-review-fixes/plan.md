---
slug: 2026-11-07-review-fixes
architecture: none               # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
<!-- Plan template: thin on purpose. Only the tasks stage reads it, to cut the work into epics (one per user story)
and tasks. The design, contracts, tests and scenarios live in their own files; cite their IDs, never restate them.
Remove a section that doesn't apply; never write N/A. -->
# Plan: fix the review's findings in the speed-up PRs

## Build order
### US-1 Only the refuter's own output, after its batch, can refute
- Delivers: CT-1, CT-2, CT-3
- Tests: TC-1, TC-2, TC-3, TC-11, TC-12, TC-13, TC-15, TC-16
- Scenario: QS-1

### US-2 Wave patches keep their bytes
- Delivers: CT-4, CT-5
- Tests: TC-4, TC-5, TC-6, TC-14
- Scenario: QS-2

### US-3 A rerun with no lens to run ends in a real next step
- Delivers: CT-6, CT-7
- Tests: TC-7, TC-8, TC-9

### US-4 Minor test and evidence gaps
- Delivers: CT-8
- Tests: TC-10

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1 | TC-1, TC-3 |
| FR-2 | CT-1, CT-2 | TC-2, TC-3 |
| FR-3 | CT-4, CT-5 | TC-4, TC-6 |
| FR-4 | CT-4, CT-5 | TC-5, TC-6 |
| FR-5 | CT-6 | TC-8, TC-9 |
| FR-6 | CT-8 | TC-10 |
| FR-9 | CT-3 | TC-11, TC-12 |
| FR-10 | CT-7 | TC-7 |
| AC-1 | CT-1 | TC-1 |
| AC-2 | CT-1, CT-2 | TC-2 |
| AC-3 | CT-1, CT-2 | TC-3 |
| AC-4 | CT-4, CT-5 | TC-4 |
| AC-5 | CT-4, CT-5 | TC-5 |
| AC-6 | CT-4, CT-5 | TC-6 |
| AC-7 | CT-7 | TC-7 |
| AC-8 | CT-6 | TC-8 |
| AC-9 | CT-6 | TC-9 |
| AC-10 | CT-8 | TC-10 |
| AC-13 | CT-3 | TC-11 |
| AC-14 | CT-3 | TC-12 |
| NFR-1 | none | none |

## Decisions
- NFR-1 is proved by each task's red, which runs its new test on the code before the fix; no test of its own [agent].
- The stories are independent, one epic (a bug fix); they are built in the spec's order [agent].
- The ledger, not `packs/refuter.md` or a file time, records the batch: `nio jury collect` prints a batch without writing that pack, and a pack file is as easy to forge as the refuter's (RF-2) [agent].

- A run in flight when this lands, whose refuter batch the old code printed, has its refuter output refused: delete the file and call `nio jury next` again, which prints the batch anew (CT-1) [agent].
- The implementation gate keeps its conformance re-run after a rejected round; only the text gates re-run every voting lens (CT-7) [agent].

## Open points

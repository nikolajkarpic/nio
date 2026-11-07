---
slug: 2026-11-07-scoped-task-commands
architecture: none               # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: scope each task's test command to its own tests

## Build order
### Foundation
- Delivers: CT-1, CT-2, CT-7
- Tests: TC-1, TC-2, TC-3, TC-11, TC-13

### US-1 Run only a task's own tests
- Depends on: Foundation
- Delivers: CT-3
- Tests: TC-4, TC-5, TC-6, TC-12
- Scenario: QS-1

### US-2 Workers iterate fast and quietly
- Depends on: US-1
- Delivers: CT-5, CT-6
- Tests: TC-7, TC-8

### US-3 Evidence per test, not per suite
- Depends on: Foundation
- Delivers: CT-4
- Tests: TC-9, TC-10
- Scenario: QS-2

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1, CT-2 | TC-1, TC-2, TC-5, TC-13 |
| FR-2 | CT-1, CT-2 | TC-1, TC-2, TC-3, TC-13 |
| FR-3 | CT-3 | TC-4 |
| FR-4 | CT-3, CT-7 | TC-5 |
| FR-5 | CT-3 | TC-6, TC-12 |
| FR-6 | CT-5 | TC-7 |
| FR-7 | CT-3, CT-6 | TC-8 |
| FR-8 | CT-4, CT-7 | TC-9, TC-10 |
| AC-1 | CT-1, CT-2 | TC-1 |
| AC-2 | CT-1, CT-2 | TC-2, TC-13 |
| AC-3 | CT-1, CT-2 | TC-3 |
| AC-4 | CT-3 | TC-4 |
| AC-5 | CT-1, CT-2, CT-3, CT-7 | TC-5 |
| AC-6 | CT-3 | TC-6, TC-12 |
| AC-7 | CT-5 | TC-7 |
| AC-8 | CT-3, CT-6 | TC-8 |
| AC-9 | CT-4, CT-7 | TC-9 |
| AC-10 | CT-4, CT-7 | TC-10 |
| NFR-1 | none | none |

## Decisions
- The runner is "self-check" when the output has a `ran <n> tests, <m> failed` line, read after the run, not from the command's words: a plain `python tests/x.py` names no runner (research RF-11) [agent].
- `tests/selfcheck.py:main` takes the script's own list of tests, so the nine scripts with a fixed order keep it (research RF-10) [agent].
- A failing-test entry `<file>::<name>` matches only that file's test, for pytest entries too: the same one-line rule serves both (research RF-12) [agent].
- NFR-1 is measured by QS-1, not by a test: a test can't time the red it runs inside [agent].
- US-3 depends only on Foundation, which delivers the runner reading both US-1 and US-3 use (CT-7), so it can be built beside US-1 [agent].
- A self-check suite that exits non-zero with no FAIL line fails the epic-closing review, as an unreadable runner's does today (CT-3) [agent].

## Open points

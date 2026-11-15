---
slug: 2026-11-15-effort-drilldown-install
architecture: none               # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
<!-- Plan template: thin on purpose. Only the tasks stage reads it, to cut the work into epics (one per user story)
and tasks. The design, contracts, tests and scenarios live in their own files; cite their IDs, never restate them.
Remove a section that doesn't apply; never write N/A. -->
# Plan: Effort drill-down in the NIO pane, and @nio:install installs the Claude Code mods

## Build order
### Foundation
- Delivers: CT-1, CT-2, CT-12, CT-13, CT-14
- Tests: TC-2, TC-6, TC-10, TC-12, TC-15, TC-18, TC-19, TC-26, TC-27, TC-28, TC-29, TC-35, TC-37

### US-1 Select an effort and see its timeline
- Depends on: Foundation
- Delivers: CT-3
- Tests: TC-1, TC-3, TC-4, TC-5
- Scenario: QS-1

### US-2 See the effort's juries
- Depends on: Foundation
- Delivers: CT-4
- Tests: TC-7, TC-8, TC-9, TC-38

### US-3 See the effort's tasks
- Depends on: Foundation
- Delivers: CT-5
- Tests: TC-11, TC-39

### US-4 See the cost so far
- Depends on: Foundation, US-1, US-2, US-3, US-5
- Delivers: CT-7
- Tests: TC-13, TC-14, TC-16, TC-25, TC-33, TC-34

### US-5 See the effort's memory and context use
- Depends on: Foundation
- Delivers: CT-6
- Tests: TC-17

### US-6 @nio:install installs the mods on Claude Code
- Delivers: CT-8, CT-9, CT-10, CT-11, CT-15, CT-16, CT-17
- Tests: TC-20, TC-21, TC-22, TC-23, TC-24, TC-30, TC-31, TC-32, TC-36
- Scenario: QS-2

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-12, CT-14 | TC-1, TC-2 |
| FR-2 | CT-2, CT-3 | TC-1, TC-2 |
| FR-3 | CT-2, CT-3 | TC-3 |
| FR-4 | CT-2, CT-4 | TC-7, TC-9 |
| FR-5 | CT-2, CT-4 | TC-8 |
| FR-6 | CT-2, CT-5 | TC-11 |
| FR-7 | CT-7 | TC-13, TC-14 |
| FR-8 | CT-7 | TC-13 |
| FR-9 | CT-12 | TC-15 |
| FR-10 | CT-2, CT-6 | TC-17 |
| FR-11 | CT-12 | TC-18, TC-19 |
| FR-12 | CT-2, CT-3, CT-4, CT-5, CT-6, CT-7, CT-12 | TC-4, TC-10, TC-12, TC-16, TC-38, TC-39 |
| FR-13 | CT-2, CT-12 | TC-5, TC-37 |
| FR-14 | CT-12, CT-14 | TC-6 |
| FR-15 | CT-10, CT-15 | TC-20 |
| FR-16 | CT-10, CT-15 | TC-21 |
| FR-17 | CT-15 | TC-20, TC-21 |
| FR-18 | CT-10 | TC-22 |
| FR-19 | CT-10 | TC-23 |
| FR-20 | CT-15 | TC-24 |
| FR-21 | CT-1, CT-2 | TC-25 |
| FR-27 | CT-1, CT-2, CT-12 | TC-26, TC-27 |
| FR-28 | CT-12 | TC-28 |
| FR-22 | CT-8, CT-9 | TC-30 |
| FR-23 | CT-13 | TC-29 |
| FR-24 | CT-15 | TC-31 |
| FR-25 | CT-10 | TC-31 |
| FR-29 | CT-10, CT-11, CT-15 | TC-23, TC-31 |
| FR-26 | CT-16, CT-17 | TC-32 |
| AC-1 | CT-2, CT-3, CT-12, CT-14 | TC-1, TC-2 |
| AC-2 | CT-2, CT-3 | TC-3 |
| AC-3 | CT-2, CT-3, CT-4, CT-5, CT-6, CT-7, CT-12 | TC-4 |
| AC-4 | CT-2, CT-12 | TC-5, TC-37 |
| AC-5 | CT-12, CT-14 | TC-6 |
| AC-6 | CT-2, CT-4 | TC-7 |
| AC-7 | CT-2, CT-4 | TC-8 |
| AC-8 | CT-2, CT-4 | TC-9 |
| AC-9 | CT-2, CT-3, CT-4, CT-5, CT-6, CT-7, CT-12 | TC-10, TC-38 |
| AC-10 | CT-2, CT-5 | TC-11 |
| AC-11 | CT-2, CT-3, CT-4, CT-5, CT-6, CT-7, CT-12 | TC-12, TC-39 |
| AC-12 | CT-7 | TC-13 |
| AC-28 | CT-7 | TC-14 |
| AC-13 | CT-12 | TC-15 |
| AC-14 | CT-2, CT-3, CT-4, CT-5, CT-6, CT-7, CT-12 | TC-16 |
| AC-15 | CT-2, CT-6 | TC-17 |
| AC-16 | CT-12 | TC-18 |
| AC-17 | CT-12 | TC-19 |
| AC-18 | CT-10, CT-15 | TC-20 |
| AC-19 | CT-10, CT-15 | TC-21 |
| AC-20 | CT-10 | TC-22 |
| AC-21 | CT-10, CT-11, CT-15 | TC-23 |
| AC-22 | CT-15 | TC-24 |
| AC-23 | CT-1, CT-2 | TC-25 |
| AC-29 | CT-1, CT-2, CT-12 | TC-26, TC-27 |
| AC-30 | CT-12 | TC-28 |
| AC-24 | CT-13 | TC-29 |
| AC-25 | CT-8, CT-9 | TC-30 |
| AC-26 | CT-10, CT-11, CT-15 | TC-31 |
| AC-27 | CT-16, CT-17 | TC-32 |
| NFR-1 | CT-7 | TC-33 |
| NFR-2 | CT-1, CT-7 | TC-34 |

## Decisions
- The mods leave the project architecture's "dev tooling, outside the product" boundary, as the approved spec's Q1 settles: D-261115-e6nx (grill, 2026-11-15). The two project-doc lines that state the old boundary are updated in this effort (CT-17), so no implement pack carries the contradiction; the record is committed with the plan's approval commit [agent].
- Every other open call of this plan is below the grill's bar and taken as the recommended option [agent], logged in grill.md under "Call · plan" (delegated session, 2026-11-15).

## Open points

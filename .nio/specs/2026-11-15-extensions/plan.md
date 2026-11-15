---
slug: 2026-11-15-extensions
architecture: approved           # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: Extensions

## Build order
### US-1 Add, list and remove extensions
- Delivers: CT-1, CT-2, CT-3, CT-4
- Tests: TC-1, TC-2, TC-4, TC-5, TC-6, TC-11, TC-20, TC-22, TC-28, TC-39, TC-42, TC-43

### US-2 The flow runs an extension step at its spot
- Depends on: US-1
- Delivers: CT-5, CT-6, CT-7, CT-8, CT-17
- Tests: TC-7, TC-8, TC-9, TC-10, TC-12, TC-13, TC-14, TC-15, TC-16, TC-17, TC-18, TC-44, TC-46, TC-48

### US-3 Built-in steps and gates can't be removed or skipped
- Depends on: US-2
- Delivers: CT-18
- Tests: TC-21, TC-41, TC-49
- Scenario: QS-1

### US-4 An extension step can have its own jury gate
- Depends on: US-3
- Delivers: CT-9
- Tests: TC-19, TC-23, TC-24
- Scenario: QS-2

### US-5 Extension agent cards and hooks on NIO events
- Depends on: US-3
- Delivers: CT-10, CT-11
- Tests: TC-25, TC-26, TC-27, TC-40, TC-47

### US-6 The shipped e2e tester
- Depends on: US-4, US-5
- Delivers: CT-12, CT-13, CT-14, CT-15, CT-16
- Tests: TC-3, TC-29, TC-30, TC-31, TC-32, TC-33, TC-34, TC-35, TC-36, TC-37, TC-38, TC-45
- Scenario: QS-3, QS-4

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1 | TC-1 |
| FR-2 | CT-1 | TC-2 |
| FR-3 | CT-1 | TC-3 |
| FR-4 | CT-1 | TC-4 |
| FR-5 | CT-2 | TC-5 |
| FR-6 | CT-3 | TC-6 |
| FR-7 | CT-4 | TC-7, TC-44 |
| FR-8 | CT-5 | TC-8, TC-48 |
| FR-9 | CT-6 | TC-9 |
| FR-10 | CT-6 | TC-10 |
| FR-11 | CT-2 | TC-11 |
| FR-12 | CT-7 | TC-12 |
| FR-13 | CT-6 | TC-9 |
| FR-14 | CT-7, CT-17 | TC-13 |
| FR-15 | CT-7 | TC-14 |
| FR-16 | CT-8 | TC-15, TC-16, TC-17, TC-47 |
| FR-17 | CT-8 | TC-16 |
| FR-18 | CT-6 | TC-18, TC-46 |
| FR-19 | CT-6, CT-9 | TC-19 |
| FR-20 | CT-2 | TC-20 |
| FR-21 | CT-18 | TC-21 |
| FR-22 | CT-2, CT-10 | TC-22 |
| FR-23 | CT-9 | TC-23, TC-24 |
| FR-24 | CT-10 | TC-25 |
| FR-25 | CT-11 | TC-26, TC-27 |
| FR-26 | CT-2, CT-11 | TC-28 |
| FR-27 | CT-11 | TC-26, TC-40, TC-47 |
| FR-28 | CT-14 | TC-29 |
| FR-29 | CT-14, CT-16 | TC-29 |
| FR-30 | CT-15 | TC-30, TC-31 |
| FR-31 | CT-12, CT-13, CT-17 | TC-32, TC-33 |
| FR-32 | CT-13, CT-16 | TC-31, TC-34 |
| FR-33 | CT-15, CT-16 | TC-35 |
| FR-34 | CT-13 | TC-36 |
| FR-35 | CT-14 | TC-37 |
| FR-36 | CT-14, CT-16 | TC-38 |
| FR-37 | CT-1 | TC-39 |
| FR-38 | CT-18 | TC-41, TC-49 |
| FR-39 | CT-2, CT-4 | TC-42 |
| FR-40 | CT-2 | TC-43 |
| FR-41 | CT-15 | TC-45 |
| AC-1 | CT-1 | TC-1 |
| AC-2 | CT-1 | TC-2 |
| AC-3 | CT-1 | TC-3 |
| AC-4 | CT-1 | TC-4 |
| AC-5 | CT-2 | TC-5 |
| AC-6 | CT-3 | TC-6 |
| AC-7 | CT-4 | TC-7 |
| AC-8 | CT-5 | TC-8 |
| AC-9 | CT-6 | TC-9 |
| AC-10 | CT-6 | TC-10 |
| AC-11 | CT-2 | TC-11 |
| AC-12 | CT-7 | TC-12 |
| AC-13 | CT-7, CT-17 | TC-13 |
| AC-14 | CT-7 | TC-14 |
| AC-15 | CT-8 | TC-15 |
| AC-16 | CT-8 | TC-16 |
| AC-17 | CT-8 | TC-17 |
| AC-18 | CT-6 | TC-18 |
| AC-19 | CT-6, CT-9 | TC-19 |
| AC-20 | CT-2 | TC-20 |
| AC-21 | CT-18 | TC-21 |
| AC-22 | CT-2, CT-10 | TC-22 |
| AC-23 | CT-9 | TC-23 |
| AC-24 | CT-9 | TC-24 |
| AC-25 | CT-10 | TC-25 |
| AC-26 | CT-11 | TC-26 |
| AC-27 | CT-11 | TC-27 |
| AC-28 | CT-2, CT-11 | TC-28 |
| AC-29 | CT-14, CT-16 | TC-29 |
| AC-30 | CT-15 | TC-30 |
| AC-31 | CT-13, CT-15, CT-16 | TC-31 |
| AC-32 | CT-12, CT-13, CT-17 | TC-32 |
| AC-33 | CT-12, CT-13, CT-17 | TC-33 |
| AC-34 | CT-13, CT-16 | TC-34 |
| AC-35 | CT-15, CT-16 | TC-35 |
| AC-36 | CT-13 | TC-36 |
| AC-37 | CT-14 | TC-37 |
| AC-38 | CT-14, CT-16 | TC-38 |
| AC-39 | CT-1 | TC-39 |
| AC-40 | CT-11 | TC-40 |
| AC-41 | CT-18 | TC-41, TC-49 |
| AC-42 | CT-2, CT-4 | TC-42 |
| AC-43 | CT-2 | TC-43 |
| AC-44 | CT-4 | TC-44 |
| AC-45 | CT-15 | TC-45 |
| AC-46 | CT-6 | TC-46 |
| AC-47 | CT-8, CT-11 | TC-47 |
| AC-48 | CT-5 | TC-48 |
| NFR-1 | CT-6 | none |
| NFR-2 | CT-2, CT-8, CT-11 | none |
| NFR-3 | CT-5, CT-6, CT-11 | none |

## Decisions
- The plan driver wrote this effort's architecture.md, since the plan needs a new module, a shipped folder and new stored data and the architecture stage is not built; it settles only those stop-list items from the spec and the code, as 2026-11-08-project-onboarding's did (delegated by the human, 2026-11-15, recommended option).
- An extension stage is named `<extension>.<step>`, its gate stage `<extension>.<step>.jury`: one name labels it with both (FR-18) and the existing gate machinery runs it unchanged (CT-6, CT-9) [agent].
- "The stage list in `nio flow status`" (AC-18) is read as `nio flow show`'s timeline, the stage list the status pane shows; `nio flow status` has one row per effort naming its current stage (RF-16), which names the extension stage while the effort sits at it (TC-18) [agent].
- An extension stage counts for an effort only once the flow moved it there (CT-6), so adding an extension never pulls back an effort already past its spot, and removing one writes nothing (FR-7) [agent].
- A Playwright test is told apart by file (a `playwright.config.*` at the root and a `.spec.*` file), so an epic and the pr evidence can mix it with the suite's runner (CT-13) [agent].

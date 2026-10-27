---
slug: <slug>
architecture: none               # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
<!-- Plan template: thin on purpose. Only the tasks stage reads it, to cut the work into epics (one per user story)
and tasks. The design, contracts, tests and scenarios live in their own files; cite their IDs, never restate them.
Remove a section that doesn't apply; never write N/A. -->
# Plan: <title>

## Build order
<!-- Foundation first when shared setup is needed, then one entry per user story in the order they can be built. -->
### Foundation
- Delivers: CT-1
- Tests: TC-1

### US-1 <story title>
- Depends on: Foundation
- Delivers: CT-2, CT-3
- Tests: TC-2, TC-3
- Scenario: QS-1

## Coverage
<!-- One row per FR, AC and NFR in the spec. Contracts: those citing the FR or NFR (for an AC, its FRs). Tests:
those aimed at the AC or NFR (for an FR, at its ACs). An NFR no test can measure and no contract serves says `none`
in both cells, for the plan jury to judge. -->
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1 | TC-1 |
| AC-1 | CT-1 | TC-1 |

## Complexity tracking
<!-- Only when the plan breaks a project principle or adds something no requirement needs. -->
| What | Why it is needed | Simpler option rejected because |
| --- | --- | --- |
| <the extra module, layer or dependency> | <the requirement that forces it> | <why the simple way fails> |

## Decisions
<!-- Leave this section out of a fresh draft; the grill fills it. -->
- <decision>: <D- record ID> (<grill or research>, <date>).

## Open points
- **OP-1** (<fact | decision>; <file and ID it belongs to>) <question>?
<!-- fact: research looks it up. decision: the grill asks the human. A design choice on the plan skill's stop list
is not an open point: the plan stops and sends the human to architecture. Resolved points move to `retired:`.
Empty at the gate. -->

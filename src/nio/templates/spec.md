---
slug: <slug>
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: []                      # IDs removed from this spec; never reused
---
<!-- Spec template (#20). WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec <slug>` checks all of this. -->
# <title>

## Summary
<What this delivers, for whom, and why, in 3–5 lines.> [default]

## Actors and journeys
- **A-1 <actor>**: <who they are, what they want, how skilled>. [default]

**UJ-1 <journey name>** (A-1) [default]
1. <step>
- Misuse: <how this actor gets it wrong or abuses it>
- Evidence: <RF-n, issue, ticket, or "domain">

## User stories

### US-1 <story title> (P1) [default]
- **Why this priority:** <why it comes first>
- **Independent test:** <how to test this story on its own and see value>

- **AC-1** (FR-1) Given <context>, when <action>, then <outcome>. [default]
  Observable: <exactly what a test asserts>. Level: <unit | integration | e2e>.

## Functional requirements
- **FR-1** <WHEN <trigger> THE SYSTEM SHALL <response> | IF <condition> THEN THE SYSTEM SHALL <response>>. [default]

## Rules
<!-- Only when there are states or conditional rules. Every cell has an outcome. -->
### State table: <name> (start: <state>; final: <state>)
| State | <event> | Src |
| --- | --- | --- |
| <state> | → <state> or ignore or reject: <why> | [default] |

### Decision table: <name>
| <condition> (<value>, <value>) | → <output> | Src |
| --- | --- | --- |
| <value or -> | <output> | [default] |

## Key entities
- **<Entity>**: <what it holds>. [default]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL <measurable quality, with a number>. [default]

## Success criteria
- **SC-1** <measurable, technology-agnostic outcome>. [default]

## Non-goals
- <what this spec deliberately does not do>. [default]

## Glossary
- **<Term>**: <meaning>. Never "<synonym>".

## Risks and evidence against
- <risk or evidence against building it this way> (RF-n). [research: RF-1]

## Decisions
- <decision>: <D- record ID> (<grill or research>, <date>).

## Open points
- <OP-n: question still open; drafting only, empty at the gate>

---
slug: <slug>
route: epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: []
---
<!-- Epic spec (#20): a feature too large for one spec. Each roadmap slice gets its own full spec
(`nio new spec <slice-slug> --epic <slug>/R-n`), which inherits this glossary and these actors. -->
# <title>

## Summary
<What the whole effort delivers and why, in 3–5 lines.> [default]

## Actors and journeys
- **A-1 <actor>**: <who they are, what they want>. [default]

**UJ-1 <journey name>** (A-1) [default]
1. <step>
- Misuse: <how it goes wrong>
- Evidence: <RF-n, issue, or "domain">

## Roadmap
| ID | Slice | Intent | Scope boundary | Depends on | Status | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| R-1 | <slice> | <one line> | <in: …; deferred: … → R-n> | — | planned | — |

## Non-goals
- <what the whole effort deliberately does not do>. [default]

## Glossary
- **<Term>**: <meaning>. Never "<synonym>".

## Decisions
- <effort-wide decision>: <D- record ID>.

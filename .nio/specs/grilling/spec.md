---
slug: grilling
route: epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: []
---
# Grilling: settling a spec with the human

## Summary
NIO settles a drafted spec with the human before any jury sees it: the grill asks only decisions, one at a time, looks
facts up itself, and writes every answer back with its provenance; `nio check spec` and the jury then hold those
provenance tags and deferred points to account. Split into two slices after the first spec jury (finding J-10). [human]

## Actors and journeys
- **A-1 Human**: settles decisions; the only one who accepts a risk or rules something out of scope. [research: RF-1]
- **A-2 Grill agent**: runs the grill in the human's session, or answers when the session is delegated. [research: RF-1]
- **A-3 Jury**: judges a settled spec and must see every point the grill deferred. [research: RF-1]

**UJ-1 Settle a draft and take it to the jury** (A-1, A-2, A-3) [research: RF-1]
1. The grill settles the draft's open points and `[default]` items with the human.
2. `nio check spec --gate` accepts the provenance the grill wrote, and the jury judges the result.
- Misuse: a provenance tag that claims more than happened (`[human]` for an agent call, `[derived]` from a guess).
- Evidence: issue #22, the grill spec's jury (V-261025-qmmq).

## Roadmap
| ID | Slice | Intent | Scope boundary | Depends on | Status | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| R-1 | The grill loop | Settle a spec with the human, one question (or round) at a time | in: the `@nio:grill` skill's behaviour; deferred: what the checker and jury enforce → R-2 | — | done | grill |
| R-2 | Provenance checks | `nio check spec` and the jury enforce what the grill writes | in: `[agent]`, `[derived]`, `[deferred]`, `## Deferred`, banned synonyms, deferred findings in the jury; deferred: nothing | — | done | grill-checks |

## Non-goals
- Other question sources (the architecture grill, the user advocate walk): they come with their own stages. [human]

## Decisions
- Split into the grill loop and its provenance checks after the first spec jury, J-10 (the human, 2026-10-25).

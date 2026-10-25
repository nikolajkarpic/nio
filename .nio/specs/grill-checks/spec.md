---
slug: grill-checks
route: full
epic: "grilling/R-2"                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4]            # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec grill-checks` checks all of this. -->
# Provenance checks: what `nio check spec` and the jury enforce about what the grill writes

## Summary
The grill writes provenance the plain checker didn't know: `[agent]` for a decision an agent made, `[derived: …]` for a
point settled by consequence, and `[deferred: DF-n]` with a `## Deferred` section for what the grill left unsettled.
This slice makes `nio check spec` accept those tags only when they are honest, lets the gate pass while naming every
deferred point, and makes `nio jury collect` turn each deferred point into a finding only the human closes, a deferred
contradiction being a blocker. It also enforces the glossary's banned synonyms, so the spec's words don't drift. [human]

## Actors and journeys
- **A-1 Human**: settles decisions; the only one who accepts a risk or rules a point out of scope (epic `grilling`, A-1). [research: RF-1]
- **A-2 Grill agent**: writes the provenance tags and the deferred points this slice checks, in the human's session or a delegated one (epic `grilling`, A-2). [research: RF-1]
- **A-3 Jury**: judges a spec that passed the gate, and must see every agent call and deferred point in it (epic `grilling`, A-3). [research: RF-1]

**UJ-1 Take a grilled spec through the gate to the jury** (A-2, A-3) [agent]
1. The grill agent ends the grill, done or early, leaving `[agent]`, `[derived: …]` and `[deferred: DF-n]` tags in the spec.
2. `nio check spec --gate` accepts the honest tags, rejects the rest, and lists the agent calls, derived items and deferred points.
3. `nio jury collect` adds a finding for each deferred point next to the lenses' findings.
- Misuse: a tag that claims more than happened (`[derived]` from a guess or another derived item, a `[deferred: DF-n]` that names nothing).
- Evidence: epic `grilling` UJ-1; issue #22; the grill spec's jury (V-261025-qmmq).

**UJ-2 Close a deferred point** (A-1, A-3) [agent]
1. The human reads the jury's finding for a deferred point.
2. The human accepts the risk or rules it out of scope, and the finding closes.
- Misuse: an agent disposes of the finding on the human's behalf, or a deferred contradiction slips through as a minor finding.
- Evidence: epic `grilling` UJ-1; issue #22.

## User stories

### US-1 Agent and derived provenance pass the check only when honest (P1) [agent]
- **Why this priority:** without it a delegated or consequence-settled spec can't pass the gate at all, and with a lax
  check a `[derived]` tag can launder a guess into the spec.
- **Independent test:** run `nio check spec --gate` on specs carrying `[agent]` and `[derived: …]` items with valid
  and invalid sources; the valid ones pass and are listed, each invalid one is named.

- **AC-1** (FR-1, FR-2) Given a spec whose FR-4 ends with `[agent]` and that has no open points or `[default]` items, when `nio check spec --gate` runs, then it passes and its notes list FR-4 under agent calls. [derived: FR-1]
  Observable: exit status 0; a notes line `agent calls: FR-4`. Level: integration.
- **AC-2** (FR-3, FR-2) Given FR-6 ends with `[derived: FR-2, AC-3]` and FR-2 is `[human]`, AC-3 is `[agent]`, when the check runs with `--gate`, then it passes and the notes list FR-6 under derived. [derived: FR-3]
  Observable: no error naming FR-6; a notes line `derived: FR-6`. Level: integration.
- **AC-3** (FR-3) Given FR-7 ends with `[derived: FR-6]` and FR-6 is itself derived, when the check runs, then it fails naming FR-7 and FR-6. [human]
  Observable: an error saying FR-7 is derived from FR-6, which is derived. Level: unit.
- **AC-4** (FR-3) Given FR-8 ends with `[derived: FR-99]` and no FR-99 is defined, when the check runs, then it fails naming FR-99. [human]
  Observable: an error saying FR-8 is derived from FR-99, which isn't defined. Level: unit.
- **AC-5** (FR-4) Given FR-9 ends with `[derived: FR-5]` and FR-5 is `[default]` or `[deferred: DF-1]`, when the check runs, then it fails naming FR-9 and FR-5. [agent]
  Observable: an error saying FR-9 is derived from FR-5 and what FR-5 is tagged. Level: unit.
- **AC-6** (FR-5) Given a state table row whose Src cell is `[derived: FR-99]` and no FR-99, when the check runs, then it fails pointing at that row. [agent]
  Observable: an error quoting the start of the row and naming FR-99. Level: unit.
- **AC-7** (FR-6) Given an item ending with `[derived: ]` or `[derived: FR-2 and FR-3]`, when the check runs, then it fails, saying the line must end with one of the accepted tags. [agent]
  Observable: an error naming the item and listing the accepted tags. Level: unit.

### US-2 Deferred points pass the gate, named (P1) [agent]
- **Why this priority:** an early end is always allowed, so the gate must let a spec through with deferred points,
  and must never let one through silently.
- **Independent test:** take a spec with two deferred points, one marked contradiction, and run `--gate`; it passes
  and names both; break each link (tag, source, section) in turn and see it fail.

- **AC-8** (FR-7, FR-8) Given a spec with no open points and `## Deferred` holding DF-1 and DF-2, DF-2 marked contradiction, when `nio check spec --gate` runs, then it passes and lists both. [human]
  Observable: exit status 0; a notes line `deferred points: DF-1, DF-2 (contradiction)`. Level: integration.
- **AC-9** (FR-9) Given FR-5 ends with `[deferred: DF-3]` and `## Deferred` has no DF-3, when the check runs, then it fails naming DF-3. [agent]
  Observable: an error saying FR-5 points at DF-3, which isn't in `## Deferred`. Level: unit.
- **AC-10** (FR-10) Given `**DF-1** (from OP-4) …` and OP-4 is not in `retired:`, when the check runs, then it fails asking for OP-4 to be retired. [agent]
  Observable: an error saying DF-1 comes from OP-4, which must move to `retired:`. Level: unit.
- **AC-11** (FR-10) Given `**DF-2** (from FR-5) …` and FR-5's line doesn't end with `[deferred: DF-2]`, when the check runs, then it fails naming both. [agent]
  Observable: an error saying FR-5's line must end with `[deferred: DF-2]`. Level: unit.
- **AC-12** (FR-11) Given a DF line without `(from <source>)`, or one placed outside `## Deferred`, when the check runs, then it fails showing the expected form or the right section. [agent]
  Observable: an error naming the DF and the expected form, or saying deferred points belong in `## Deferred`. Level: unit.

### US-3 Deferred points become jury findings only the human closes (P1) [agent]
- **Why this priority:** a deferred point the jury doesn't see is a guess the implementer makes later; the human is
  the only one who may accept that risk.
- **Independent test:** collect a spec jury on a spec with deferred points; each shows up as a finding with the right
  severity, an agent can't close it, the human can, and the verdict isn't approved while one is open.

- **AC-13** (FR-12, FR-14) Given a spec with DF-1 (from OP-4), when `nio jury collect` runs for the spec gate, then the ledger gains one finding citing DF-1 and OP-4, quoting the DF line, with severity major. [derived: FR-12]
  Observable: one ledger finding with cites [DF-1, OP-4], the DF line as its quote, severity major, status open. Level: integration.
- **AC-14** (FR-13) Given DF-2 is marked contradiction, when the jury collects, then its finding is a blocker contradiction. [human]
  Observable: the finding for DF-2 has severity blocker and kind contradiction. Level: integration.
- **AC-15** (FR-15) Given the ledger already has a finding citing DF-1, when `nio jury collect` runs again, then no second finding for DF-1 is added. [derived: FR-15]
  Observable: exactly one finding cites DF-1 after two collects. Level: integration.
- **AC-16** (FR-16) Given an open deferred finding, when it is disposed `--by agent`, then the disposition is refused and the finding stays open. [derived: FR-16]
  Observable: an error saying only the human closes it; the finding's status is still open. Level: unit.
- **AC-22** (FR-20) Given an open deferred finding for DF-1 and DF-1 still in `## Deferred`, when it is disposed as a spec fix `--by grill`, then the disposition is refused; once DF-1 is removed, the same disposition closes it. [human]
  Observable: an error saying DF-1 is still in `## Deferred`; after the removal, the finding's status is disposed with `by: grill`. Level: unit.
- **AC-17** (FR-16) Given an open deferred finding, when the human disposes it as accepted risk or out of scope with a note, then it is closed with that disposition. [human]
  Observable: the finding's status is disposed, with the disposition, `by: human` and the note. Level: unit.
- **AC-18** (FR-17) Given a deferred finding is still open and every lens approved, when the jury composes its verdict, then the outcome is not approved. [derived: FR-16]
  Observable: the outcome is rejected, naming the finding as unresolved. Level: integration.

### US-4 Banned synonyms stay out of the spec (P2) [agent]
- **Why this priority:** words that drift between the glossary and the requirements are a quiet source of
  misreading, but a stray word is less costly than a dishonest tag.
- **Independent test:** ban a synonym in the glossary, use it in an FR, in the glossary, in Decisions and in a code
  span; only the FR use fails.

- **AC-19** (FR-18) Given the glossary entry `**Refund**: … Never "reimbursement".`, when an FR says `issue a reimbursement`, then the check fails naming the section, the word and the glossary term. [human]
  Observable: an error naming `## Functional requirements`, the banned word and Refund. Level: unit.
- **AC-20** (FR-18, FR-19) Given the same glossary, when the word appears only in `## Glossary`, in `## Decisions`, or inside a code span elsewhere, then the check reports no glossary error. [derived: FR-18, FR-19]
  Observable: no error mentioning the banned word. Level: unit.
- **AC-21** (FR-19) Given the same glossary, when an AC says `Reimbursement` (capitalised) or `reimbursement-free`, then the capitalised use fails and the hyphenated word doesn't. [derived: FR-19]
  Observable: one glossary error, for the capitalised word only. Level: unit.

## Functional requirements
- **FR-1** THE SYSTEM SHALL accept `[agent]` as an item's provenance in `nio check spec`, with or without `--gate`. [human]
- **FR-2** WHEN `nio check spec` runs THE SYSTEM SHALL list in its notes the items tagged `[agent]`, the items tagged `[derived: …]` and the items tagged `[deferred: DF-n]`, and count the lines without an ID that carry those tags, so the human at the finish gate and the jury see which points nobody asked the human. [agent]
- **FR-3** THE SYSTEM SHALL accept `[derived: <sources>]` in `nio check spec`, with or without `--gate`, only when every source is defined (an ID in the spec, or an RF-n in the spec's research) and none is itself derived. [human]
- **FR-4** IF a `[derived: …]` source is a `[default]` proposal or a deferred point THEN THE SYSTEM SHALL reject it, since only answered, agent-decided or researched items are settled. [agent]
- **FR-5** THE SYSTEM SHALL check every `[derived: …]` tag wherever it appears: on an item, in a table's Src cell, or on a line without an ID. [agent]
- **FR-6** IF an item's provenance is none of `[human]`, `[default]`, `[agent]`, `[research: RF-n]`, `[derived: <IDs>]` or `[deferred: DF-n]` THEN THE SYSTEM SHALL reject it and list the accepted tags. [agent]
- **FR-7** WHEN a spec has deferred points and nothing else blocks the gate THE SYSTEM SHALL let `nio check spec --gate` pass. [human]
- **FR-8** WHEN a spec has deferred points THE SYSTEM SHALL list every one in the check's notes, marking those deferred as contradictions. [human]
- **FR-9** IF a `[deferred: DF-n]` tag names a DF that isn't in `## Deferred` THEN THE SYSTEM SHALL reject it. [agent]
- **FR-10** IF a deferred point comes from an open point that is not in `retired:`, or from an item whose line doesn't end with `[deferred: <that DF>]`, THEN THE SYSTEM SHALL reject it. [agent]
- **FR-11** IF a deferred point is outside `## Deferred` or isn't written as `**DF-n** (from <OP, item ID or section>[; contradiction]) <what is unsettled>` THEN THE SYSTEM SHALL reject it. [agent]
- **FR-12** WHEN `nio jury collect` runs for a spec's gate THE SYSTEM SHALL add one open finding per deferred point in the spec, citing the DF and its source and quoting its line, that needs the human's disposition. [human]
- **FR-13** IF a deferred point is marked contradiction THEN THE SYSTEM SHALL make its finding a blocker. [human]
- **FR-14** IF a deferred point is not marked contradiction THEN THE SYSTEM SHALL make its finding major. [human]
- **FR-15** IF a finding already cites a deferred point THEN THE SYSTEM SHALL NOT add another for it on a later collect. [human]
- **FR-20** IF a deferred finding is disposed as a spec fix while its DF is still in `## Deferred` THEN THE SYSTEM SHALL refuse the disposition, since the point isn't settled until the grill removes it. [human]
- **FR-16** THE SYSTEM SHALL let only the human close a deferred finding, either directly as accepted risk or out of scope, or through a grill session that settles the point as a spec fix that changes the spec, and SHALL refuse a disposition recorded by an agent. [human]
- **FR-17** WHILE a deferred finding is open THE SYSTEM SHALL NOT approve the spec's jury verdict. [derived: FR-16]
- **FR-18** IF a word the glossary bans (`Never "…"` in its entry) appears in any section other than `## Glossary` and `## Decisions` THEN THE SYSTEM SHALL reject the spec, naming the section, the word and the glossary term. [human]
- **FR-19** THE SYSTEM SHALL match a banned word as a whole word, ignoring case, and skip text inside code spans. [agent]

## Rules

### Decision table: a `[derived: …]` source
| source is (human/agent/research item, RF-n, default item, deferred item, derived item, undefined) | → outcome | Src |
| --- | --- | --- |
| human/agent/research item | accept | [derived: FR-3] |
| RF-n | accept when the spec's research has it | [derived: FR-3] |
| default item | reject: a proposal isn't settled | [derived: FR-4] |
| deferred item | reject: an unsettled point isn't settled | [derived: FR-4] |
| derived item | reject: no chains | [derived: FR-3] |
| undefined | reject: the source must exist | [derived: FR-3] |

### Decision table: a deferred finding's severity
| marked contradiction (yes, no) | → severity | Src |
| --- | --- | --- |
| yes | blocker, kind contradiction | [derived: FR-13] |
| no | major, kind gap | [derived: FR-14] |

### Decision table: closing a deferred finding
| disposed by (human, grill, agent) | → outcome | Src |
| --- | --- | --- |
| human | closed with accepted risk or out of scope | [derived: FR-16] |
| grill | closed as a spec fix, only when the DF is gone from `## Deferred` | [derived: FR-16, FR-20] |
| agent | refused; stays open | [derived: FR-16] |

## Key entities
- **Deferred point**: a `DF-n` in `## Deferred`: its source (an OP, an item or a section), whether it is a
  contradiction, and what is unsettled. [derived: FR-11]
- **Deferred finding**: the jury finding made from one deferred point, citing it and its source, closed only by the human. [derived: FR-12, FR-16]

## Success criteria
- **SC-1** No spec reaches an approved jury verdict while one of its deferred points has no human disposition. [derived: FR-16]
- **SC-2** Every `[derived: …]` tag in a spec that passes `nio check spec` traces to sources that are answered, agent-decided or researched. [derived: FR-3]

## Non-goals
- The grill's own behaviour (asking, deferring, writing the tags); that is the sibling slice `grill` (epic `grilling`, R-1). [agent]
- Checking that a deferred contradiction quotes both sides; the grill writes it that way (grill FR-30), and the jury finding quotes the line. [agent]
- Checking that an `[agent]` answer was allowed (never on permissions, deletion, money, irreversible operations or breaking changes); that is the grill's rule (grill FR-26). [agent]
- Catching inflected forms of a banned word (plurals, other endings). [human]

## Glossary
- **Agent call**: a decision an agent made, tagged `[agent]`; never presented as the human's. Never "auto-answer".
- **Derived item**: a point settled by consequence, tagged `[derived: <sources>]`, whose sources are answered,
  agent-decided or researched. Never "inferred item".
- **Deferred point**: a `DF-n` the grill left unsettled; the jury turns it into a finding. Never "parked point".
- **Banned synonym**: a word a glossary entry rules out after `Never`; the check rejects it outside the glossary and
  Decisions.

## Decisions
- A grill session that settles a deferred point may close its finding as a spec fix; accepting the risk or ruling it out of scope stays the human's direct call (the human, 2026-10-25).
- A deferred point counts as settled only once its DF line is gone from `## Deferred`; `dispose` refuses a spec fix before that (the human, 2026-10-25).
- An `RF-n` cited as a derived source must exist in the spec's research.md, like any other source; the check was tightened to match FR-3 (the human, 2026-10-25).


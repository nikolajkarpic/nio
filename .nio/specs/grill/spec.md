---
slug: grill
route: full
epic: "grilling/R-1"                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-2, OP-3, OP-12, OP-13, OP-14, OP-4, OP-7, OP-8, OP-11, OP-9, OP-6, OP-5, OP-10, A-4, UJ-4, US-7, AC-23, AC-24, FR-21, FR-22, OP-15, OP-1, FR-27, FR-28, FR-29]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec grill` checks all of this. -->
# The grill: settle a spec with the human, one question at a time

## Summary
`@nio:grill` is the question loop with the human. It takes a draft spec's open decisions and `[default]` proposals
and settles them one question at a time, looking up facts itself and asking the human only what only the human can
decide. Vague requirements are the main source of hallucination, so the grill has no fixed question cap: it converges,
stopping when the spec's checklist is green or the human ends it, and a new session can resume where the last one
stopped. The same skill later runs the architecture grill with a different question source. [human]

## Actors and journeys
- **A-1 Human**: the person whose spec is being grilled; knows the intent, not necessarily the code; wants few, sharp questions and a spec that says what they meant. [research: RF-1]
- **A-2 Grill agent**: the agent running the grill skill in the human's session, on any host; looks up facts, picks and asks questions, records answers and patches the spec. [research: RF-1]
- **A-3 Jury**: reviews the spec at the end of the spec stage and must see every point the grill deferred. [research: RF-1]

**UJ-1 Grill a draft spec to the gate** (A-1, A-2) [research: RF-1]
1. The grill agent reads the spec, its open points and its `[default]` items, and builds the candidate points.
2. It looks up every fact, settles what follows from earlier answers, and asks the human the next decision.
3. The human answers (accepts the recommendation, picks another option, or types their own).
4. The agent records the answer, patches the spec, and moves to the next point until the stop rule holds.
- Misuse: the agent asks the human a fact it could have looked up, puts dependent questions in one round, or guesses a decision instead
  of asking it.
- Evidence: issue #22.

**UJ-2 End early and hand the rest to the jury** (A-1, A-2, A-3) [derived: FR-18]
1. The human ends the grill before `nio check spec --gate` passes.
2. Every unsettled point moves to `## Deferred` as `DF-n`, and the jury gets each as a finding for the human.
- Misuse: deferred points are silently dropped, or written in as if decided.
- Evidence: issue #22.

**UJ-3 Resume in a new session** (A-1, A-2) [derived: FR-19, FR-20]
1. A new session runs `nio check spec --gate` and reads the last entry of `grill.md`.
2. It asks only what is still open, starting with a question the last session left unanswered.
- Misuse: the human is asked a question they already answered.
- Evidence: issue #22.

## User stories

### US-1 Answer only the decisions, one question at a time (P1) [agent]
- **Why this priority:** this is the grill; without it nothing moves a draft past its `[default]` items and open
  decisions, and asking facts or mixing dependent questions wastes the human's attention.
- **Independent test:** grill a draft spec with known facts and decisions; the human is asked only the decisions,
  one per message, each in the agreed format, and every answer lands in the spec.

- **AC-1** (FR-1) Given a draft spec with decision open points and `[default]` items, when the grill starts, then every item `nio check spec --gate` lists is a candidate and nothing else is. [derived: FR-19]
  Observable: every question and call in `grill.md` names an ID that `--gate` listed. Level: integration.
- **AC-2** (FR-2) Given a candidate point that the code, memory or docs answer, when the grill reaches it, then the agent looks it up and the human is never asked it. [human]
  Observable: the point is answered in `grill.md` with its source cited, and it is not in the asked list. Level: e2e.
- **AC-34** (FR-34) Given a fact the code, memory and docs can't settle, when the grill reaches it, then it shows what it searched and found and lets the human decide it now or defer it, and it never guesses. [human]
  Observable: the message lists the sources searched; the item ends `[human]` (decided) or `[deferred: DF-n]`; never `[agent]` or `[research]` without a finding. Level: e2e.
- **AC-3** (FR-3) Given several askable points, when the grill asks, then each message carries exactly one question, unless rounds mode is on, when one numbered message carries the whole frontier. [human]
  Observable: one question per message by default; with `grill.mode: rounds`, one numbered message per round, answerable by number. Level: e2e.
- **AC-4** (FR-4) Given a question to ask, when it is shown, then it has a full question ending in `?`, a one-line why it matters, the verified facts it rests on each with its source, 3 options (fewer only when no real third exists) with exactly one recommended and why, and a free-form input. [human]
  Observable: the message has each of those parts, every fact names an RF-n, a file:line or a spec ID, there are 1 to 3 options, and exactly one is marked recommended. Level: e2e.
- **AC-5** (FR-5) Given a question with a recommended option, when the human replies "yes", then the recommended option is recorded as the answer. [human]
  Observable: the recorded answer equals the recommended option. Level: e2e.
- **AC-6** (FR-6, FR-7) Given the human answers a question, when the answer is recorded, then it is logged in `grill.md`, the spec items it settles are patched before the next question, and a weighty decision also gets a D- record listed in `## Decisions`. [human]
  Observable: grill.md logs the answer with its provenance; spec.md shows the patched item before the next question; a weighty decision has a D- record listed in Decisions. Level: e2e.
- **AC-7** (FR-24) Given a free-form answer that can't be written as a testable item, when the grill records it, then it asks exactly one follow-up on that point, and if the reply is still vague, the point becomes an open decision point. [human]
  Observable: one follow-up entry in `grill.md` for that point, then either a patched item or a new `OP-n`; never a second follow-up in a row. Level: e2e.
- **AC-28** (FR-31) Given the glossary says `Refund … Never "reimbursement"`, when the human answers "issue a reimbursement", then the grill asks whether they mean a refund before patching. [human]
  Observable: a clarifying question in `grill.md` before the patch. Level: e2e.

### US-2 Contradictions stop the loop until resolved (P1) [agent]
- **Why this priority:** a contradiction left in the spec is a guess the implementer makes later; it must be settled
  while the human is there.
- **Independent test:** give an answer that contradicts the code or an earlier answer; the grill flags it with both
  sides and asks nothing else until it is resolved.

- **AC-8** (FR-13) Given the code cancels whole orders, when the human answers that partial cancellation is possible, then the grill flags the contradiction, citing the code and the answer, and asks how to resolve it before any other question. [human]
  Observable: the next message names both sides and is the resolution question; no other point is asked until it is resolved. Level: e2e.
- **AC-9** (FR-13) Given an answer that contradicts an earlier accepted answer, when it is recorded, then the grill flags both answers and resolves the conflict before moving on. [human]
  Observable: the contradiction is listed in `grill.md` and resolved before the next question. Level: e2e.

- **AC-27** (FR-30) Given a contradiction is open, when the grill ends early, then it becomes a `DF-n` marked contradiction with both sides quoted. [human]
  Observable: the DF item says contradiction and quotes both sides. Level: integration.

### US-3 Converge and stop without a fixed cap (P1) [agent]
- **Why this priority:** a fixed cap forces guesses ("make informed guesses"), and no cap at all risks the
  200-question grill; the grill must stop for the right reason.
- **Independent test:** grill a spec until the checklist is green; then grill another and end it early; then let one
  run past the soft budget.

- **AC-10** (FR-14) Given a spec with more decisions than spec-kit's 5-question cap, when the grill runs, then it asks every decision that needs the human, with no fixed limit. [human]
  Observable: every decision point `--gate` listed at the start ends tagged `[human]`, `[agent]`, `[derived: …]` or `[deferred: …]`, and more than 5 are asked when more than 5 need the human. Level: e2e.
- **AC-11** (FR-17) Given `nio check spec grill --gate` passes, when the human or the delegated agent chooses finish at the finish gate, then the grill ends as done, after listing what it settled by consequence for review; explore further returns to asking, and stop with concerns is an early end that defers the concerns. [human]
  Observable: `grill.md` records the grill as done, and the gate check passes. Level: e2e.
- **AC-12** (FR-18) Given unsettled points remain, when the grill ends early, then each becomes a `DF-n` in `## Deferred`, and no answer is assumed. [human]
  Observable: every unsettled point is a `DF-n` with its source, and `grill.md` logs the early end. Level: e2e.
- **AC-13** (FR-15) Given the grill has asked 15 questions and 20 points are still open, when it would ask the next one, then it pauses, offers continue, delegate or end early, and suggests splitting into an epic. [human]
  Observable: question 16 is not asked before the pause; the pause shows the three choices and the split suggestion. Level: e2e.
- **AC-31** (FR-15) Given the grill paused at 15 and the human chose continue, when 15 more questions are asked, then it pauses again before question 31, without the split suggestion. [human]
  Observable: a second pause entry in `grill.md` before question 31; it doesn't mention an epic. Level: e2e.
- **AC-32** (FR-15) Given the config sets the interval to 10 and exactly 15 points are open, when 10 questions are asked, then the grill pauses and doesn't suggest a split. [human]
  Observable: the pause comes before question 11; no epic suggestion, since 15 is not more than 15. Level: integration.
- **AC-33** (FR-15) Given a pause, when the human chooses delegate, then the rest is answered by the agent as `[agent]`; when they choose end early, the open points move to `## Deferred`. [human]
  Observable: after delegate, new answers end `[agent]`; after end early, every open point is a `DF-n`. Level: e2e.
- **AC-14** (FR-10, FR-16) Given a goal's core facets are covered and an open point whose alternatives change nothing a user can do or see, when the grill reaches it, then it is not asked: the recommended answer is written in as `[agent]` and listed at the finish gate. [human]
  Observable: the point is not asked; its item ends with `[agent]`; its `grill.md` call records five no's on the bar's checklist; the finish gate lists it. Level: e2e.
- **AC-15** (FR-9, FR-10) Given a stated goal whose core facets are not all covered, when the grill picks the next question among those whose prerequisites are settled, then it picks a core facet before any other taxonomy category, and only after they are covered does the bar for asking rise. [human]
  Observable: in `grill.md`, each of a goal's 6 core facets has a question or fact-lookup entry tagged with it before any question from another coverage category for that goal. Level: e2e.
- **AC-29** (FR-32) Given an answer "never more than 3 retries" was patched as "a few retries", when the finish gate runs, then the grill restores "never more than 3" and logs the fix. [human]
  Observable: the patched item says "never more than 3"; `grill.md` has the fidelity fix. Level: e2e.
- **AC-30** (FR-33) Given the human accepted all 8 recommendations as-is, when the finish gate runs, then the grill says so and asks which decision they would push back on before offering to finish. [human]
  Observable: the finish gate message states 8 of 8 accepted and asks for a pushback first. Level: e2e.

### US-4 Settle what follows, ask what matters (P2) [agent]
- **Why this priority:** convergence depends on not asking what earlier answers already decide, but permissions and
  irreversible operations are too costly to infer.
- **Independent test:** answer a question that implies another point; that point is written in with a citation and
  listed for review, while an implied permission point is still asked.

- **AC-16** (FR-11) Given a point that follows from accepted answers, when the grill reaches it, then it is written in tagged `[derived: …]` with its sources, listed at the finish gate, and becomes `[human]` if the human changes it there. [human]
  Observable: the item cites the answers it follows from, appears in the review list, and not in the asked list. Level: e2e.
- **AC-17** (FR-12) Given a point about permissions, an irreversible operation, money, deletion or a breaking change that follows from accepted answers, when the grill reaches it, then it is asked anyway. [human]
  Observable: the point is in the asked list. Level: e2e.
- **AC-18** (FR-8) Given one question waiting on a fact lookup and others with settled prerequisites, when the grill picks the next question, then the waiting one is held and the others are asked. [human]
  Observable: the waiting question is not asked before its lookup finishes; other questions are asked meanwhile. Level: e2e.

### US-5 Resume in a new session (P2) [agent]
- **Why this priority:** a long grill outlives one session, and re-asking answered questions costs trust.
- **Independent test:** stop a grill mid-way, start a new session, and see it continue from the frontier.

- **AC-19** (FR-19) Given a grill in progress, when a question is asked and then answered, then `grill.md` gains an `Asked` entry and then an answer entry with the question, options, answer, provenance and patched IDs, and no earlier entry changes. [human]
  Observable: the log grows by one entry per ask and one per answer; earlier entries are byte-identical. Level: integration.
- **AC-20** (FR-20) Given a spec half settled in an earlier session, when a new session starts the grill, then it asks only what `--gate` still lists and asks no answered question again. [human]
  Observable: no question in the answered list is asked in the new session. Level: e2e.
- **AC-21** (FR-20) Given the previous session ended with a question asked but unanswered, when a new session starts, then that question is asked first. [derived: FR-20]
  Observable: the first question of the new session is the one whose `Asked` entry has no answer. Level: e2e.

### US-6 Fill and confirm the spec's tables and risk flags (P2) [agent]
- **Why this priority:** state tables, decision tables and risk flags decide which lenses the jury uses (#47); a
  draft only proposes them.
- **Independent test:** grill a spec whose draft has a `[default]` state table and empty risk flags; afterwards the
  tables are complete and confirmed and the risk flags are set by the human.

- **AC-22** (FR-23) Given a draft spec with `[default]` table rows and proposed risk flags, when the grill finishes, then every row and every risk flag has been confirmed by the human. [human]
  Observable: no table row is `[default]`, and the risk flags were asked or confirmed in `grill.md`. Level: e2e.

### US-8 Delegate a session to an agent (P2) [human]
- **Why this priority:** agents run NIO flows unattended; a grill that only a present human can finish blocks them.
- **Independent test:** delegate a grill to an agent, let it answer, and see its answers tagged `[agent]`, the gate pass, and a deletion question still wait for the human.

- **AC-25** (FR-25) Given a session delegated to an agent, when the agent answers a decision point, then the item ends with `[agent]`, never `[human]`. [human]
  Observable: the patched item's tag is `[agent]`, and `grill.md` logs the agent's reason. Level: integration.
- **AC-26** (FR-26) Given a delegated session reaches a point about permissions, an irreversible operation, money, deletion or a breaking change, when the agent would answer it, then the grill stops and waits for the human. [human]
  Observable: the point stays open, no `[agent]` answer is written for it, and the human is asked. Level: integration.

## Functional requirements
- **FR-1** WHEN the grill starts on a spec THE SYSTEM SHALL take as its candidates every open point and `[default]` item that `nio check spec --gate` lists. [derived: FR-19]
- **FR-2** WHEN a candidate point is a fact that code, memory, docs or research can answer THE SYSTEM SHALL look it up and never ask the human. [human]
- **FR-3** THE SYSTEM SHALL ask one question at a time by default, and the whole frontier as one numbered round when the config sets `grill.mode` to `rounds` or the human asks for rounds; a round never holds two questions where one answer could change the other. [human]
- **FR-4** THE SYSTEM SHALL show each question as a full question ending in `?`, a one-line why it matters, the verified facts it rests on, each with its source (an RF-n, a file:line or a spec ID), 3 options (or only 1 or 2 when no more real alternatives exist, never filler) with exactly one marked recommended and why, and one free-form input. [human]
- **FR-5** WHEN the human replies "yes" to a question THE SYSTEM SHALL take its recommended option as the answer. [human]
- **FR-6** WHEN a question is answered THE SYSTEM SHALL log the answer in `grill.md` with its provenance, and WHEN the decision is costly to reverse, surprising, or a real trade-off THE SYSTEM SHALL also write a memory decision record through @nio:remember and list its ID in `## Decisions`. [human]
- **FR-7** WHEN an answer is recorded THE SYSTEM SHALL patch the spec items it settles right away, before the next question. [human]
- **FR-8** THE SYSTEM SHALL ask only questions whose prerequisites are settled; a question waiting on a fact lookup waits while the others go ahead. [human]
- **FR-9** THE SYSTEM SHALL cover the 6 core facets of each stated goal (meaning, actors and permissions, data and state effect, failure and conflict, transition from today, verification) before the other coverage categories, a facet counting as covered once `grill.md` logs a question or call for that goal tagged with it, where only a question or a fact lookup counts, never a below-the-bar call. [human]
- **FR-10** WHEN a goal's core facets are covered THE SYSTEM SHALL ask a further point only if one of its alternatives changes what a user can do, what a user sees, who may do it, what data is kept or changed, or what it costs, recording those five answers in `grill.md` for every point it doesn't ask. [human]
- **FR-11** WHEN a point follows from accepted answers or research findings THE SYSTEM SHALL write it in tagged `[derived: <sources>]`, naming the items it follows from (never another derived item), and list it for review at the finish gate, without asking it. [human]
- **FR-12** IF a point concerns permissions, an irreversible operation, money, deletion or a breaking change THEN THE SYSTEM SHALL ask it, even when it follows from accepted answers. [human]
- **FR-13** WHEN an answer contradicts an accepted answer, the spec or the code THE SYSTEM SHALL flag the contradiction with both sides and resolve it before asking anything else. [human]
- **FR-14** THE SYSTEM SHALL NOT cap the number of questions at a fixed count. [human]
- **FR-15** WHEN every 15 asked questions (configurable) THE SYSTEM SHALL pause and offer: continue, delegate the rest to an agent, or end early; and at the first pause, IF more than 15 points are still open THEN it SHALL also suggest splitting the spec into an epic with slices. [human]
- **FR-16** WHEN a point falls below that bar THE SYSTEM SHALL take its recommended answer itself, tag it `[agent]`, and list it at the finish gate where the human can overturn it; points about permissions, irreversible operations, money, deletion or breaking changes are never below the bar. [human]
- **FR-17** WHEN `nio check spec <slug> --gate` passes and the human, or an agent the human delegated the session to, confirms THE SYSTEM SHALL end the grill as done. [human]
- **FR-18** WHEN the grill ends early THE SYSTEM SHALL move each unsettled point to `## Deferred` as `DF-n` (the OP it came from, its target, why it was deferred), never assuming an answer. [human]
- **FR-19** THE SYSTEM SHALL treat the spec as the grill's state, recomputing what is open from `nio check spec --gate` each time, and keep `grill.md` next to it as an append-only log: an `Asked` entry when a question is asked, and an answer entry with its options, answer, provenance and patched IDs when it is answered. [human]
- **FR-20** WHEN a session starts the grill on a spec that already has a `grill.md` THE SYSTEM SHALL resume from the spec's open items, asking first any `Asked` entry that has no answer. [human]
- **FR-23** THE SYSTEM SHALL fill in and confirm with the human the spec's state tables, decision tables and risk flags. [human]
- **FR-24** IF a free-form answer can't be written as a testable spec item THEN THE SYSTEM SHALL ask one follow-up on the same point, with options built from the human's words, and IF it is still vague THEN record it as an open decision point instead of guessing. [human]

- **FR-25** WHERE the human delegated the session to an agent THE SYSTEM SHALL let that agent answer decision points and confirm the finish, tagging each answer `[agent]`, never `[human]`. [human]
- **FR-26** IF a delegated agent reaches a point about permissions, an irreversible operation, money, deletion or a breaking change THEN THE SYSTEM SHALL stop and wait for the human. [human]
- **FR-30** IF the grill ends early while a contradiction is open THEN THE SYSTEM SHALL defer it as a `DF-n` marked contradiction that quotes both sides. [human]
- **FR-31** WHEN a term settles THE SYSTEM SHALL write it into `## Glossary` with its rejected synonyms, and WHEN the human uses a word the glossary defines differently THE SYSTEM SHALL ask which they mean before patching. [human]
- **FR-32** WHEN the finish gate runs THE SYSTEM SHALL re-read every item patched in the session against its logged answer and restore any number, negative or ordering that drifted, logging the fix. [human]
- **FR-33** IF the human accepted every recommendation as-is THEN THE SYSTEM SHALL say so at the finish gate and ask which decision they would push back on before offering to finish. [human]
- **FR-34** IF a fact lookup finds nothing, or finds sources that disagree, THEN THE SYSTEM SHALL show the human what it searched and found and let them decide it now (`[human]`) or defer it (`DF-n`), raising disagreeing sources as a contradiction (FR-13), and never guess. [human]


## Rules

### State table: grill session (start: idle; final: done, ended-early)
| State | ask next | answer | contradiction found | contradiction resolved | human ends | checklist green and confirmed | Src |
| --- | --- | --- | --- | --- | --- | --- | --- |
| idle | → asking | reject: no question is waiting | → contradiction | ignore | → ended-early | → done | [derived: FR-3, FR-13, FR-17, FR-18, FR-30] |
| asking | reject: a question or round is waiting | → idle | → contradiction | ignore | → ended-early | reject: a question is waiting | [derived: FR-3, FR-13, FR-17, FR-18, FR-30] |
| contradiction | → contradiction | → contradiction | → contradiction | → idle | → ended-early | reject: a contradiction is open | [derived: FR-3, FR-13, FR-17, FR-18, FR-30] |
| done | reject: the grill is done | ignore | ignore | ignore | ignore | ignore | [derived: FR-3, FR-13, FR-17, FR-18, FR-30] |
| ended-early | reject: the grill ended | ignore | ignore | ignore | ignore | ignore | [derived: FR-3, FR-13, FR-17, FR-18, FR-30] |

### Decision table: ask, settle or wait
| kind (fact, decision) | permissions, irreversible, money, deletion or breaking change (yes, no) | follows from accepted answers (yes, no) | prerequisites settled (yes, no) | lookup settles it (yes, no) | core facets covered (yes, no) | above the bar (yes, no) | → action | Src |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fact | - | - | - | yes | - | - | look it up; never ask | [human] |
| fact | - | - | - | no | - | - | show what was searched; the human decides or defers | [derived: FR-34] |
| decision | - | - | no | - | - | - | wait in the queue | [human] |
| decision | yes | - | yes | - | - | - | ask | [human] |
| decision | no | yes | yes | - | - | - | write it in as derived; list it at the finish gate | [human] |
| decision | no | no | yes | - | no | - | ask (a core facet comes first) | [derived: FR-9] |
| decision | no | no | yes | - | yes | yes | ask | [human] |
| decision | no | no | yes | - | yes | no | take the recommended answer as an agent call; list it at the finish gate | [derived: FR-16] |

## Key entities
- **Candidate point**: something `nio check spec --gate` lists: a `[default]` item or an open point, with its kind (fact or
  decision) and the ID or section it belongs to. [agent]
- **Question**: one candidate point put to the human in the agreed format, with its options and recommendation. [derived: FR-4]
- **Answer**: the reply (the human's, or a delegated agent's), logged in `grill.md` with its provenance and the spec
  items it patched; weighty ones also become decision records. [derived: FR-6, FR-25]
- **Grill log** (`grill.md`): an append-only log of questions, answers, below-the-bar calls and derived items; the spec
  itself is the state. [derived: FR-19]

## Success criteria
- **SC-1** Every spec the grill finishes as done passes `nio check spec --gate`: no `[default]` items and no open points left. [derived: FR-17]
- **SC-2** No question asked of the human is a fact that code, memory or docs answer, checked over the asked lists of grill runs. [derived: FR-2]
- **SC-3** No question is asked twice across sessions of the same grill. [derived: FR-20]

## Non-goals
- Other question sources (the architecture grill, the user advocate walk): they come with their own stages; the loop takes its candidates from `nio check spec --gate`, so they plug in later. [human]
- A fixed cap on the number of questions, or a cap on clarification markers. [human]
- Guessing an answer to a decision the human hasn't made ("make informed guesses"), except the below-the-bar calls
  written in as `[agent]` and listed at the finish gate (FR-16). [human]
- Asking several questions in one message by default; rounds mode is opt-in (FR-3). [human]
- Defining the checklist itself (#21); the grill uses it as its stop rule. [research: RF-4]
- Judging the spec's quality; the jury does that after the grill. [agent]

## Glossary
- **Fact**: a point that code, memory, docs or research can answer; the agent looks it up. Never "question for the
  human".
- **Decision**: a point only the human can settle; the grill asks it.
- **Frontier**: the candidate points whose prerequisites are settled, so they can be asked or settled now.
- **Bar**: after a goal's core facets, only points whose alternatives change what a user can do or see, permissions,
  data or cost are asked; the rest are agent calls.
- **Settled by consequence**: written in because it follows from accepted answers, cited and listed for review.
- **Deferred**: unsettled when the grill ended early; a `DF-n` in `## Deferred` that the jury turns into a finding.
- **Core facets**: meaning, actors and permissions, data and state effect, failure and conflict, transition from
  today, verification; covered first for every stated goal.
- **Coverage taxonomy**: clarify's 10 categories: scope, domain and data, UX flow, NFRs, integrations, edge cases,
  constraints, terminology, completion signals, placeholders.

## Decisions
- The log has two entries per question, one when asked and one when answered, so a crashed session resumes the unanswered question (grill, 2026-10-25).
- Split (J-10): what `nio check spec` and the jury enforce moved to the `grill-checks` slice; FR-27, FR-28 and FR-29 are retired here (the human, 2026-10-25).
- A fact nobody can find is shown to the human, who decides it or defers it; disagreeing sources are a contradiction (grill, 2026-10-25).
- A core facet is covered once `grill.md` logs a question or call for it; the bar is a five-question checklist (can do, sees, who may, data, cost), recorded for every point not asked (grill, 2026-10-25).
- After the first spec jury (V-261025-qmmq): money, deletion and breaking changes are always asked like permissions and irreversible operations; the configurable 15 and the epic suggestion stay; the passivity check has no threshold; every fact in a question carries its source (grill, 2026-10-25).
- From Pocock's grilling and domain-modeling (2026-10-25 review): an optional rounds mode (`grill.mode: rounds`), glossary discipline with banned synonyms checked by `nio check spec`, and an answer-fidelity and passivity check at the finish gate (grill, 2026-10-25).
- The grill ends when `--gate` passes and the human, or a delegated agent, confirms; agent answers are tagged `[agent]`, and the always-human points wait for the human (grill, 2026-10-25).
- Unsettled points of an early end move to `## Deferred` as `DF-n`; the gate lists them and the jury turns each into a finding for the human (grill, 2026-10-25).
- Points that follow from accepted answers are written in as `[derived: <sources>]`, never chained from another derived item, and listed at the finish gate (grill, 2026-10-25).
- Every answer is logged in `grill.md` and patched into the spec; only weighty ones (costly to reverse, surprising, a real trade-off) also become memory decision records (grill, 2026-10-25).
- The spec is the grill's state (what is open comes from `--gate`); `grill.md` is an append-only log, so resuming needs no extra state (grill, 2026-10-25).
- Questions show 3 options, or fewer when no real alternative exists (never filler), always one recommended; NORTH_STAR is updated to match (grill, 2026-10-25).
- After the core facets, only points whose alternatives change what a user can do or see, permissions, data or cost are asked; the rest are agent calls tagged `[agent]`, listed at the finish gate (grill, 2026-10-25).
- Every 15 questions the grill pauses: continue, delegate the rest to an agent, or end early; if much is still open it suggests splitting into an epic (grill, 2026-10-25).
- An early end is always allowed; an open contradiction is deferred as a blocker for the jury, with both sides quoted (grill, 2026-10-25).
- The architecture grill and the user advocate feed ship with their own stages, not in this spec (grill, 2026-10-25).
- A vague free-form answer gets one follow-up; if it's still vague it becomes an open decision point (grill, 2026-10-25).


---
slug: plain-talk
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [AC-14, OP-1, OP-2, OP-3, OP-4, OP-5, OP-7, OP-6, OP-8, OP-9, OP-10, OP-11, OP-12, OP-13, OP-14, OP-15]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec plain-talk` checks all of this. -->
# Plain talk: every NIO message to the human says what's needed first, with IDs in a trailing Refs line

## Summary
When a NIO agent talks to the human, the human often can't tell what's needed without opening the spec to look up
IDs such as J-7, FR-10 or DF. This change gives every message to the human one shape: what's needed first, in plain
words; at most a few lines of context; options that say what each one costs; IDs and sources in a trailing `Refs:`
line. The rule lives in `NORTH_STAR.md` and CLAUDE.md, a shared block in each skill that talks to the human carries
it, and a small test keeps the copies identical. Logs and the `nio` CLI keep their IDs. [human]

## Actors and journeys
- **A-1 Human**: reads NIO's questions, reports, errors and hand-offs and acts on them; knows the product, not NIO's internal IDs. [human]
- **A-2 Skill agent**: the agent running a NIO skill (grill, jury, spec, recall, remember) that writes the messages to the human. [human]
- **A-3 Skill author**: writes or edits a NIO skill and must follow the rule without being told. [derived: US-3]
- **A-4 Juror**: a jury agent that reads logs such as `grill.md` and needs every ID and source in them. [human]

**UJ-1 Act on a message without opening a file** (A-1, A-2) [derived: FR-1, FR-2, FR-3, FR-4, FR-5]
1. The skill agent needs something from the human: an answer, a choice, an approval or a command run.
2. It writes the message in the shared shape and checks the human could act on it without opening a file.
3. The human reads the first line, sees what's needed, picks or acts, and opens the `Refs:` only to check.
- Misuse: the agent copies a finding, CLI output or spec line into the body with its IDs, or describes options as actions on the spec rather than what changes for the human.
- Evidence: issue #53 (the grill-checks jury round, Q7).

**UJ-2 Review a bulk list** (A-1, A-2) [derived: FR-7]
1. A skill asks the human to overturn or approve a list (jury dispositions, grill agent calls, derived items).
2. It shows only the items that change what the product does, in plain words, and counts the rest in one line.
3. The human reviews the few that matter and finds the full list in `Refs:` and the log.
- Misuse: the agent counts a behaviour change among the "nothing you'd notice" items, so the human never sees it.
- Evidence: issue #53, decision 5.

**UJ-3 Add or edit a skill that talks to the human** (A-3) [derived: US-3, FR-9, FR-11]
1. The author reads CLAUDE.md's rules for writing skills and adds the shared block to the skill.
2. The drift test fails if the block is missing or differs from the one in `NORTH_STAR.md`.
- Misuse: the author edits one copy of the block and not the others.
- Evidence: issue #53, decisions 3 and 6.

## User stories

### US-1 Every message tells the human what's needed and stands on its own (P1) [human]
- **Why this priority:** it is the problem the issue names: the human can't act on a message without looking up its
  IDs, and every skill falls back to NIO's internal vocabulary.
- **Independent test:** run a grill session on a spec with an open jury finding and read each message; the human can
  act on every one without opening a file.

- **AC-1** (FR-1, FR-3, FR-4, FR-5) Given the jury's J-7 finding goes to the grill as a question, when the grill asks it, then the human sees it in the shape of the issue's "J-7 after" example. [human]
  Observable: the first line starts with `Pick one:` and a plain question; no ID (`J-7`, `FR-10`, `FR-11`, `DF`), severity or lens name appears above the `Refs:` line; each option says what happens and what is lost, the recommended one first; the last line is `Refs: J-7 · FR-10, FR-11 · jury.py:268`. Level: e2e.
- **AC-2** (FR-2) Given messages from a grill and a jury session, when the human reads them, then the human judges that each message's context is about 3 lines and none is too long to take in at a glance. [human]
  Observable: the human's verdict at the end of the session, recorded with SC-1; no automated line count. Level: e2e.
- **AC-3** (FR-1, FR-5) Given a report that needs nothing from the human and rests on no ID, file or command, when a skill sends it, then its first line says so in plain words and it has no `Refs:` line. [derived: FR-1, FR-5]
  Observable: the first line starts with `Nothing needed`; no line starts with `Refs:`. Level: e2e.
- **AC-4** (FR-1, FR-23) Given an error the human must fix by running a command, when a skill reports it, then the first line asks them to run it and the command is shown in the body. [derived: FR-1, FR-23]
  Observable: the first line starts with `Run this command`; the command appears in the body, above the `Refs:` line. Level: e2e.
- **AC-5** (FR-16, FR-15) Given a skill relays `nio` CLI output that prints IDs, when it shows the result to the human, then the body says in plain words what the output means and `Refs:` holds the command and the IDs it cites, not the raw output. [derived: FR-16]
  Observable: no ID from the output above the `Refs:` line; the `Refs:` line holds the command and the IDs the output cites, on one line. Level: e2e.
- **AC-6** (FR-19) Given a jury finding that changes behaviour goes to the grill for a spec fix, when the grill asks the human, then the body never shows the finding's ID, severity or lens. [human]
  Observable: none of `J-<n>`, `blocker`, `major`, `minor` or the lens name above the `Refs:` line; the finding's ID is in `Refs:`. Level: e2e.
- **AC-7** (FR-6, FR-10) Given the shared block, when any copy of it is read, then it ends with the self-check: could they act on this without opening a file, and if not, rewrite it. [human]
  Observable: the last line of the block in `NORTH_STAR.md` and in each skill is exactly "Before sending, ask: could they act on this without opening a file? If not, rewrite it." Level: unit.

### US-2 Bulk review lists lead with what changes the product (P1) [human]
- **Why this priority:** the lists the human is asked to overturn run to dozens of items, and the few that change what
  the product does get lost among wording fixes.
- **Independent test:** finish a jury round with many agent dispositions, only some changing behaviour; the report
  shows those few in plain words and one count line for the rest.

- **AC-8** (FR-7) Given the jury approved a spec after 24 agent dispositions, 3 of which change what the product does, when it reports to the human, then it shows those 3 in plain words, then one count line for the other 21. [human]
  Observable: 3 items in the body; one line like `21 more were wording or test fixes, nothing you'd notice`; `Refs:` lists all 24 finding IDs. Level: e2e.
- **AC-9** (FR-7) Given the grill's finish gate lists 8 derived items and 2 agent calls, none of which change what the product does, when it shows them to the human, then no item is listed in the body, only the count line. [derived: FR-7]
  Observable: no item in the body; one count line naming 10 items; `Refs:` lists all 10 IDs. Level: e2e.
- **AC-26** (FR-7) Given a fixed list of 10 items where item 3 changes an error message the user sees, item 7 adds a field the user must fill, and the other 8 only reword the spec or fix a test, when the list is shown, then both behaviour changes are in the body and the count line says 8. [derived: FR-7]
  Observable: items 3 and 7 appear above the count line; the count line says 8; neither behaviour change is in the count. Level: e2e.
- **AC-10** (FR-13) Given the grill showed the human the J-7 question, when it logs the entry in `grill.md`, then the entry holds the shown question, context, options and `Refs:` line word for word under a header that keeps the ID. [human]
  Observable: an entry headed `## Asked · Q7 · J-7 · <date>` whose `Question:`, `Context:`, `Options:` and `Refs:` lines match the transcript exactly; the answer entry `## Q7 · J-7 · <date>` has no `Refs:` line. Level: e2e.

### US-3 One rule, one block, no drift (P1) [human]
- **Why this priority:** skills must be self-contained on any host, so the rule is copied into each of them; without a
  test the copies drift apart, and a new skill can leave the block out.
- **Independent test:** run the drift test on the repo and see it pass; change one word in one skill's copy and see it
  fail naming that skill.

- **AC-11** (FR-10, FR-11) Given `NORTH_STAR.md` and the five skills hold identical blocks, when the drift test runs, then it passes. [human]
  Observable: exit status 0. Level: unit.
- **AC-12** (FR-11) Given the `remember` skill has no block, when the drift test runs, then it fails naming `remember`. [human]
  Observable: exit status non-zero; the output names `skills/remember/SKILL.md` as missing the block. Level: unit.
- **AC-13** (FR-11) Given the `jury` skill's copy differs from `NORTH_STAR.md` by one word, when the drift test runs, then it fails naming `jury`. [agent]
  Observable: exit status non-zero; the output names `skills/jury/SKILL.md`. Level: unit.
- **AC-27** (FR-11) Given the drift test, when it runs offline, then it imports only the standard library and finishes in under 2 seconds. [derived: NFR-1]
  Observable: its imports are all in `sys.stdlib_module_names`; wall time under 2 s. Level: unit.
- **AC-15** (FR-11) Given the agent cards in `src/nio/agents/` have no block, when the drift test runs, then it doesn't fail on them. [human]
  Observable: no output line names a file under `src/nio/agents/`. Level: unit.
- **AC-16** (FR-8, FR-9, FR-12) Given the change is made, when `NORTH_STAR.md` and CLAUDE.md are read, then `NORTH_STAR.md` has a principle "Talking to the human" with the block, CLAUDE.md's "Rules for writing skills" says every message to the human follows that shape, and CLAUDE.md's self-checks list the drift test. [human]
  Observable: each of the three texts is present. Level: unit.

### US-4 Each skill's human-facing steps follow the shape (P1) [human]
- **Why this priority:** the block alone doesn't fix a step whose own wording pulls IDs into the body, such as the
  grill's "facts, each naming its source".
- **Independent test:** read each listed step in the five skills; each says what the human is asked in plain words,
  and none tells the agent to put an ID, severity, lens or source in the body.

- **AC-17** (FR-17) Given the grill skill, when its question step is read, then it asks for each fact in plain words with its source named beside it in plain words ("per the jury code"), the IDs and file:line in `Refs:`, and carries the J-7 example. [human]
  Observable: the step asks for a plain-words source beside each fact and puts IDs and file:line only in `Refs:`; the J-7 "after" example is in it. Level: unit.
- **AC-18** (FR-17, FR-18, FR-20, FR-21, FR-22) Given each point FR-17 to FR-22 list (grill: answer or delegate, the question, the log, the finish gate, the hand-off, a lookup that found nothing, the follow-up on a vague answer, a glossary clash, a contradiction, the 15-question pause, the delegated stop; jury: a missing card, the over-cap choice, a manual lens run, the `human` outcome, the `approved` report, the spec fix, a failed gate, a second lens failure, refuted findings, an accepted-risk or out-of-scope disposition, a finding that failed two rounds, the human closing the gate; spec: the slug and route line, showing the draft, asking for the work, a slug that already exists, a drafter that fails twice, `nio` missing; recall: `challenged`, `conflict`, memory has nothing; remember: no area fits, a change request, the closing report), when it is read, then it tells the agent to follow the shape and none tells it to show an ID in the body. [derived: FR-17, FR-18, FR-20, FR-21, FR-22]
  Observable: each skill holds the `## Talking to the human` block; every step or table row that is one of the listed points either refers to "Talking to the human" or starts its message with a plain first line, and none of those steps or rows contains "ID", "severity", "lens" or "file:line" except after "`Refs:`" (a grep per point); none of these phrases remains in any skill: "each naming its source", "with the code's file:line", "show each reason with its findings" (unless followed by "in plain words"); the grill's question step contains the J-7 "after" example. Level: unit.
- **AC-19** (FR-20) Given the spec skill picked a slug and route, when it tells the human, then the first line says nothing is needed unless they want to change either, and the route is described by what it means. [derived: FR-1, FR-3, FR-5, FR-20]
  Observable: the first line starts with `Nothing needed`; the body names the route by its meaning (for example "a bug fix"); the slug and route values are in `Refs:`. Level: e2e.
- **AC-20** (FR-21) Given a memory record the work relies on is `challenged`, when recall asks the human, then the message says in plain words what the record decided and what is disputed, and asks them to pick which holds. [derived: FR-1, FR-3, FR-5, FR-21]
  Observable: the first line asks the human to pick; no record ID above the `Refs:` line; both record IDs in `Refs:`. Level: e2e.
- **AC-21** (FR-22) Given no memory area fits a record, when remember stops, then the first line asks the human to pick where the record should be filed or to add a new place, and each option says what that place holds. [derived: FR-1, FR-3, FR-4, FR-5, FR-22]
  Observable: the first line asks where to file the record, without the word "area"; options name what each area holds; `Refs:` lists `memory.areas`. Level: e2e.

### US-5 Logs, jurors and the CLI keep full detail (P2) [human]
- **Why this priority:** jurors, tests and the human's own look-ups need IDs; translating only where the agent talks to
  the human keeps them working.
- **Independent test:** run the existing self-checks unchanged after the change, and read a new `grill.md` entry: its
  header and `Refs:` line carry the IDs.

- **AC-22** (FR-15) Given this change is made, when the existing self-checks run, then they pass with no change to the CLI output they expect. [human]
  Observable: every `tests/test_*.py` listed in CLAUDE.md passes; no expected CLI output in them changed. Level: integration.
- **AC-23** (FR-13, FR-14) Given `grill.md` entries written in the new shape, when `nio jury answers <slug>` runs, then it still extracts every human answer, with the entry's ID. [derived: FR-13, RF-2]
  Observable: the extracted answers match the entries one for one, each with its header's ID, including an answer that picks the last option by number; no extracted answer contains `Refs:`. Level: integration.
- **AC-24** (FR-24) Given the grill asks the J-7 question through Claude Code's question tool, when the human reads it, then the question text ends with the `Refs:` line and each option's description states what happens if it's picked. [human]
  Observable: the shown question text's last line starts with `Refs:`; the logged `Question:`, `Context:` and `Refs:` lines match the question text, and the `Options:` line matches the option labels and descriptions, word for word. Level: e2e.
- **AC-25** (FR-25) Given the grill runs in rounds mode and asks a round of 3 questions, when the human reads it, then only the round's first line says what's needed, and each numbered question has its own options and `Refs:` line. [human]
  Observable: one first line for the round; no question inside it starts with `Pick one:`; three `Refs:` lines, one per question; `grill.md` gains three `## Asked` entries, each matching its question word for word, and none holds the opening line. Level: e2e.

## Functional requirements
- **FR-1** WHEN a skill sends a message to the human (a question, decision, report, error or hand-off) THE SYSTEM SHALL make its first line say what is needed from the human, in plain words, such as "Nothing needed", "Pick one", "Run this command" or "Approve or push back". [human]
- **FR-2** THE SYSTEM SHALL follow the first line with about 3 lines of context, with no hard ceiling: what it is, why it matters and what it costs. The limit is on context only; a list under FR-7 runs as long as its behaviour changes. [human]
- **FR-3** THE SYSTEM SHALL name each thing in a message's body by what it does, never by an ID (FR-n, J-n, DF-n) or by a NIO term the human doesn't start by name; only stage names (spec, grill, jury, plan) may be used as they are, and a command shown for the human to copy (FR-23) is quoted exactly, IDs included. No code checks messages: IDs, severity names and the word "lens" are what a reader of the transcript looks for (SC-2), and other terms are judged by the human (SC-1). [human]
- **FR-4** WHEN a message offers options THE SYSTEM SHALL say for each what happens if it is picked, including what is lost, with the recommended option first. [human]
- **FR-5** WHEN a message to the human rests on any ID, file, command or source THE SYSTEM SHALL end it with a `Refs:` line holding them; a message that rests on none has no `Refs:` line. [human]
- **FR-6** WHEN a message to the human is ready to send THE SYSTEM SHALL check whether the human could act on it without opening a file, and rewrite it if not. The block's last line reads: "Before sending, ask: could they act on this without opening a file? If not, rewrite it." [human]
- **FR-7** WHEN a message asks the human to review or overturn a list (jury dispositions, grill agent calls, derived items) THE SYSTEM SHALL show in plain words every item that changes what the product does, however many, then one line counting the rest, with the full list in `Refs:` and the log. An item changes behaviour when it passes the grill's bar: it changes what a user can do, sees, who may do it, what data is kept or changed, or what it costs. [human]
- **FR-8** THE SYSTEM SHALL state the rule in `NORTH_STAR.md` as a principle, "Talking to the human", holding the shared block. [human]
- **FR-9** THE SYSTEM SHALL state in CLAUDE.md's "Rules for writing skills" that every message to the human follows the shape. [human]
- **FR-10** THE SYSTEM SHALL carry the shared "Talking to the human" block, identical to the one in `NORTH_STAR.md`, in each skill that talks to the human: grill, jury, spec, recall and remember. [human]
- **FR-11** IF any skill under `skills/` lacks the shared block, or its copy differs from the one in `NORTH_STAR.md`, THEN THE SYSTEM SHALL fail the drift test, naming the skill. [human]
- **FR-12** THE SYSTEM SHALL list the drift test among the self-checks in CLAUDE.md. [human]
- **FR-13** WHEN the grill shows a question THE SYSTEM SHALL first log it word for word under `## Asked · Q7 · <ID> · <date>` as labelled lines (`Question:` holding the shown question line, then `Context:`, `Options:` and `Refs:`), show exactly that text (through a question tool, field by field: the question text maps to `Question:`, `Context:` and `Refs:`, the option labels and descriptions to `Options:`), and record the answer in the `## Q7 · <ID> · <date>` entry with `Question:`, `Options:`, `Answer:` and `Patched:` lines as today, with no `Refs:` line in it. [human]
- **FR-14** THE SYSTEM SHALL keep every ID and source in logs such as `grill.md`, which jurors read: in the entry header and the `Refs:` line, not as a copy of the raw jury finding, which stays in the jury's own record. [human]
- **FR-15** THE SYSTEM SHALL leave the output of the `nio` CLI unchanged, IDs included. [human]
- **FR-16** WHEN a skill relays `nio` CLI output to the human THE SYSTEM SHALL say in plain words what it means and put the command and the IDs it cites in `Refs:`, never the raw output itself. [human]
- **FR-17** THE SYSTEM SHALL make the grill's human-facing points follow the shape: the answer-or-delegate question, each question (each fact in plain words with its source named beside it in plain words, the IDs and file:line in `Refs:`, with the J-7 example), the log of what was shown, the finish gate (as a list per FR-7) and the next-stage hand-off, and also: a lookup that found nothing, the follow-up on a vague answer, a glossary clash, a contradiction (both sides in plain words, the file:line in `Refs:`), the 15-question pause and the delegated stop. [human]
- **FR-18** THE SYSTEM SHALL make the jury's human-facing points follow the shape: a missing card, the over-cap choice, a manual lens run, the `human` outcome, the `approved` report (as a list per FR-7) and the spec fix, and also: a failed gate, a second lens failure, refuted findings, an accepted-risk or out-of-scope disposition, a finding that failed two rounds, and the human closing the gate. [human]
- **FR-19** WHEN the jury passes a finding to the grill or the human for a spec fix THE SYSTEM SHALL describe it in plain words and never show its ID, severity or lens in the body. [human]
- **FR-20** THE SYSTEM SHALL make the spec skill's slug-and-route line and its showing of the draft follow the shape, and also: asking for the work, a slug that already exists, a drafter that fails twice, and `nio` missing. [human]
- **FR-21** THE SYSTEM SHALL make recall's questions on a `challenged` or `conflict` record follow the shape, and also: memory has nothing. [human]
- **FR-22** THE SYSTEM SHALL make remember's stops when no area fits and when it writes a change request follow the shape, and also: the closing report (IDs and paths in `Refs:`). [human]
- **FR-23** WHEN the human must run a command THE SYSTEM SHALL show that command in the message body, not only in `Refs:`. [human]
- **FR-24** WHEN a message is asked through the host's question tool THE SYSTEM SHALL put the first line, the context and the `Refs:` line in the question text, and each option's consequence in its description. [human]
- **FR-25** WHEN the grill asks a round of questions (rounds mode only) THE SYSTEM SHALL open the round with one first line saying what's needed ("Answer 5 questions, by number"), then give each numbered question its own context, options and `Refs:` line, as one message per question under that opening line; a question inside a round has no first line of its own (FR-1 is met by the opening line), its logged `Question:` line holds the numbered question as shown, and the opening line carries no decision and is not logged. [human]

## Rules

### Decision table: where each part of a message goes
| content (what's needed, context, option, ID/file/source, command the human must run, raw CLI output) | → place | Src |
| --- | --- | --- |
| what's needed | the first line, in plain words | [derived: FR-1] |
| context | about 3 lines after the first, no IDs | [derived: FR-2, FR-3] |
| option | after the context, each with what happens and what's lost, recommended first | [derived: FR-4] |
| ID/file/source | the `Refs:` line only | [derived: FR-5] |
| command the human must run | the body, and `Refs:` | [derived: FR-23] |
| raw CLI output | not shown; the command and the IDs it cites go in `Refs:` | [derived: FR-16] |

### Decision table: an item in a list the human reviews
| changes what the product does (yes, no) | → shown | Src |
| --- | --- | --- |
| yes | in the body, in plain words | [derived: FR-7] |
| no | in one count line; listed in `Refs:` and the log | [derived: FR-7] |

### Decision table: the drift test on one file
| under `skills/` (yes, no) | block (missing, differs, identical) | → outcome | Src |
| --- | --- | --- | --- |
| yes | missing | fail, naming the file | [derived: FR-11] |
| yes | differs | fail, naming the file | [derived: FR-11] |
| yes | identical | pass | [derived: FR-11] |
| no | - | not checked | [derived: FR-11] |

## Key entities
- **Message to the human**: anything a skill agent shows the human: a question, decision, report, error or hand-off. [human]
- **Talking-to-the-human block**: the shared text that states the shape, held in `NORTH_STAR.md` and copied word for word into each skill that talks to the human. [human]
- **Refs line**: the last line of a message (in a round, of each question), holding the IDs, files, commands and sources the message rests on. [human]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL run the drift test with the Python standard library only, offline, in under 2 seconds. [human]

## Success criteria
- **SC-1** In the next grill and jury session, the human can act on every message without opening a file, as judged by the human over every message of that session. [human]
- **SC-2** In the transcripts of that grill and jury session, no message shows an ID above its `Refs:` line, outside a command shown for the human to copy. [derived: FR-3, SC-1]
- **SC-3** `NORTH_STAR.md`, CLAUDE.md and the five skills are updated, and the drift test passes and is listed among the self-checks. [human]

## Non-goals
- The agent cards in `src/nio/agents/`: they talk only to the parent agent, never the human. [human]
- Code that lints messages: enforcement is the instructions plus the self-check; a lint on `## Asked` entries comes only if agents still drift. [human]
- Changing the `nio` CLI's output. [human]
- Rewriting entries in existing `grill.md` logs: they record what the human saw at the time. [human]

## Glossary
- **Message to the human**: anything a skill agent shows the human; not a hand-off between agents.
- **Refs line**: the trailing `Refs:` line of a message to the human.
- **Behaviour change**: an item that changes what the product does, as opposed to a wording or test fix.

## Risks and evidence against
- Only instructions enforce the shape, so agents may still put IDs in the body; the fallback is a lint on `## Asked` entries. [human]
- Putting a finding in plain words can drop or bend its meaning; the `Refs:` line keeps the original to check against. [agent]

## Open points

## Decisions
- Only stage names the human starts by name (spec, grill, jury, plan) may appear as they are; every other NIO term is described by what it does (the human, 2026-10-26).
- In a host's question tool, `Refs:` is the last line of the question text, so the log matches what the human saw (the human, 2026-10-26).
- A round of questions opens with one line saying what's needed; each question keeps its own context, options and `Refs:` (the human, 2026-10-26).
- The drift test checks every skill under `skills/`, with no list or marker; a future skill that never talks to the human gets an exception then (the human, 2026-10-26).
- `Refs:` carries a relayed command and the IDs it cites, not its raw output; the human reruns the command to see it. This replaces the issue's "raw output in Refs" (the human, 2026-10-26).
- Every place a skill talks to the human is rewritten to the shape, not only the places the issue lists, so no old step contradicts the block (the human, 2026-10-26).
- A `grill.md` entry keeps IDs in its header and `Refs:` line only; the raw jury finding is not copied, it stays in the jury's record (the human, 2026-10-26).
- `grill.md` logs a shown message as labelled lines (`Question:`, `Context:`, `Options:`, `Refs:`) in its `## Asked` entry; the answer entry keeps today's lines without `Refs:`, so `nio jury answers` keeps working unchanged (the human, 2026-10-26; placement fixed for J-1, J-3).
- A review list shows every behaviour change in plain words, however many; only the rest are counted (the human, 2026-10-26).
- Context is about 3 lines with no hard ceiling; the human judges length, nothing counts lines. This changes the block's "at most 3 lines" (the human, 2026-10-26).
- A message that rests on nothing has no `Refs:` line; anything it rests on must be cited (the human, 2026-10-26).
- A command the human must run is shown in the body, ready to copy, and also listed in `Refs:` (the human, 2026-10-26).
- Each fact in a question names its source beside it in plain words ("per the jury code"); IDs and file:line go in `Refs:`. This keeps the grill's rule that every fact carries its source (J-2; the human, 2026-10-26).
- One change, not an epic: the block, the drift test and every rewrite land together so no skill is half-converted (J-10; the human, 2026-10-26).

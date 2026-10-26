---
slug: 2026-10-26-jury-convergence
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [SC-2, OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-10-26-jury-convergence` checks all of this. -->
# Jury convergence: after the first review only confirmed blockers start another round, and a re-review checks each fix with its neighbours

## Summary
On large behavioural specs the spec jury doesn't converge: each re-review judges the whole spec again, the previous
round's fixes are new text, and every round raises fresh majors (3 rounds on the grill spec, 4 on grill-checks, both
closed by the human). This change makes a re-review a fix check: each lens gets its findings with the before and after
text of the changed items and their neighbours, answers fixed or not fixed, and may raise only blockers. After the
first review, only a blocker the refuter confirms starts another round; majors and minors a re-review finds not fixed go to
the human in one list, each fixed or accepted as risk, a new major or minor is only a note, and one final fix check reviews those fixes. Large specs get no new size rule. [human]

## Actors and journeys
- **A-1 Human**: owns the spec; settles the findings the jury hands over, either by having them fixed or by accepting them as risk, and may close a gate the jury hasn't approved. [human]
- **A-2 Jury skill agent**: the agent running @nio:jury; plans the lenses, builds their packs, drives `nio jury` and disposes of findings within its authority. [agent]
- **A-3 Lens juror**: an independent lens subagent; on a re-review it judges whether each of its findings was fixed, not the whole spec. [human]
- **A-4 Refuter**: validates blocker and major findings by trying to refute them; only a blocker it confirms can start another round. [human]

**UJ-1 Re-review after the first round's fixes** (A-2, A-3, A-4) [derived: FR-1, FR-7, FR-8]
1. The first review rejects the spec; the agent and the human dispose of the findings and the spec is fixed.
2. The agent lists what the fixes changed and their neighbours, and re-runs the lenses that need it with fix-check packs.
3. Each lens answers fixed or not fixed per finding and raises a new finding only if it is a blocker.
4. The refuter validates any new blocker; with none confirmed, the jury doesn't start another round.
- Misuse: a lens treats the re-review as a fresh review and raises majors about wording that never changed; or the agent builds the pack from the whole spec.
- Evidence: issue #52 (the grill spec, 3 rounds; grill-checks, 4 rounds); in all three dogfood juries no re-review raised a new confirmed blocker [research: RF-6].

**UJ-2 Settle the remaining findings in one list** (A-1, A-2, A-3) [derived: FR-2, FR-3, FR-4, FR-5]
1. After a re-review with no confirmed blocker, the agent shows the human every open major and minor in one message.
2. For each, the human picks fix or accept as risk.
3. The agent applies the fixes, one final fix check reviews them, and the jury ends without another round.
- Misuse: the agent fixes a listed finding on its own judgement, or runs more than one final fix check.
- Evidence: issue #52, decision 1 of the 2026-10-26 brainstorm.

## User stories

### US-1 Only a confirmed blocker starts another round after the first review (P1) [human]
- **Why this priority:** it is what bounds the jury; without it each round's fixes keep producing the next round's
  findings, as on both dogfood runs.
- **Independent test:** in `tests/test_jury.py`, run a first review, fix, then a re-review that raises only a major;
  `nio jury check` returns `human` with that major in its list instead of `rejected`.

- **AC-1** (FR-1, FR-6) Given the first review raised a confirmed major and nothing else, when `nio jury check` runs, then the outcome is `rejected`, as today. [derived: FR-6]
  Observable: outcome `rejected`; the reason lists the major's ID. Level: unit.
- **AC-2** (FR-2, FR-12) Given a re-review gives major J-2 and minor J-3 the verdict not fixed, raises a new major M and no blocker, when `nio jury check` runs, then the outcome is `human`, J-2 and J-3 are listed together and M is shown as a note only. [human]
  Observable: outcome `human`; one reason names J-2 and J-3; M appears under a note line, is not on the list and doesn't change the outcome. Level: unit.
- **AC-3** (FR-1, FR-13) Given a re-review raises a new blocker that the refuter confirms, when `nio jury check` runs after escalation, then the outcome is `rejected`. [human]
  Observable: outcome `rejected`; the reason lists the blocker's ID. Level: unit.
- **AC-4** (FR-13, FR-2) Given a re-review raises a new blocker that the refuter refutes, and nothing else is open, when `nio jury check` runs, then no new round is asked for. [derived: FR-1, FR-2]
  Observable: outcome `approved`; the blocker's status is `refuted`. Level: unit.
- **AC-5** (FR-3, FR-4, FR-5) Given the outcome is `human` with two majors and one minor in the list, when the human fixes one and accepts the other two as risk, then one final fix check runs on the fix, and when it gives the verdict fixed the jury ends without another round. [human]
  Observable: `nio jury check --record` returns `approved` after the final fix check's verdict is collected, never `rerun`; one verdict record is written; no new run starts. Level: integration.
- **AC-21** (FR-4, FR-21) Given the human fixed one finding on the list and the final fix check gives it the verdict not fixed, when `nio jury check` runs, then the outcome is `human` listing that finding, and no further fix check or round starts. [derived: FR-4, FR-21]
  Observable: outcome `human`; the reason names the finding; the outcome is not `rejected` or `rerun`. Level: unit.
- **AC-24** (FR-4, FR-5) Given the outcome is `human` with two findings in the list, when the human accepts both as risk and fixes none, then the jury ends with no final fix check. [derived: FR-4, FR-5]
  Observable: `nio jury check` returns `approved`; no fix-check pack is owed and no new run starts. Level: unit.
- **AC-25** (FR-22) Given the human fixed one finding on the list and no final fix check has run, when `nio jury check` runs, then the jury isn't approved. [derived: FR-4]
  Observable: outcome `rerun`; the reason names the fixed finding. Level: unit.
- **AC-26** (FR-23, FR-21) Given the final fix check gave J-9 the verdict not fixed and the outcome was `human`, when the human fixes J-9 again and `nio jury check` runs, then the jury ends without another check. [human]
  Observable: outcome `approved`; a reason names J-9's fix as judged by no lens; no new run starts. Level: unit.
- **AC-27** (FR-24, FR-19) Given a re-review recorded `human` for its list and the human fixed one finding, when the next round is collected and a new confirmed blocker appears in it, then it is treated as the final fix check. [derived: FR-24]
  Observable: outcome `human`, not `rejected`. Level: unit.
- **AC-28** (FR-2, FR-12) Given copies of the grill and grill-checks ledgers as of their second round, with each round-2 major and minor given the verdict not fixed, and no confirmed blocker, when `nio jury check` runs, then neither starts a third round. [derived: FR-2, FR-12]
  Observable: the outcome for each is `human`, not `rejected`. Level: integration.
- **AC-6** (FR-5) Given the list is settled but one listed finding is still open, when `nio jury check` runs, then the jury doesn't end. [derived: FR-5]
  Observable: outcome `human`; the reason names the open finding. Level: unit.
- **AC-7** (FR-16) Given a blocker that failed two rounds, when `nio jury check` runs, then it goes to the human as today. [derived: FR-16]
  Observable: outcome `human`; a reason reads `J-<n> failed 2 rounds`. Level: unit.

### US-2 A re-review checks each fix with its neighbours (P1) [human]
- **Why this priority:** a reworded requirement is new text, so a whole-spec re-review judges it fresh and finds new
  majors; checking each fix against the finding that motivated it is what stops that.
- **Independent test:** fix one FR that an AC cites, run `nio jury changed`, build the re-review pack and feed back a
  lens output with one verdict per finding; the ledger marks the finding fixed.

- **AC-8** (FR-14) Given a fix changed FR-2, AC-3 cites FR-2 and FR-2 cites FR-1, when `nio jury changed` runs, then it lists FR-2 as changed and AC-3 and FR-1 as its neighbours. [human]
  Observable: the output names FR-2 among the changed IDs and AC-3 and FR-1 among the neighbour IDs, and no other ID among the neighbours. Level: unit.
- **AC-9** (FR-7) Given the lens that raised J-2 re-runs after J-2 was fixed, when the agent builds its pack, then the pack holds J-2, the before and after text of each item the fixes changed, and the text of their neighbours. [human]
  Observable: the pack holds J-2's title, quote and fix, the before and after text of every changed ID and the current text of every neighbour ID that `nio jury changed` printed, and no text of any other ID, such as an unrelated FR. Level: integration.
- **AC-10** (FR-8, FR-10) Given a re-review output gives J-2 the verdict fixed, when it is collected, then J-2 is marked fixed. [human]
  Observable: J-2's status in the ledger is `fixed`. Level: unit.
- **AC-11** (FR-8, FR-11) Given a re-review output gives J-2 the verdict not fixed, when it is collected, then J-2 is reopened with one more failed round. [derived: FR-11]
  Observable: J-2's status is `open` and its failed-round count rose by 1. Level: unit.
- **AC-20** (FR-11) Given a re-review gives a blocker the verdict not fixed, the refuter refutes that verdict and nothing else is open, when `nio jury check` runs, then no new round starts. [derived: FR-11]
  Observable: the verdict appears in the refuter batch; after the refuter's answer the blocker's status is `refuted` and the outcome is `approved`. Level: unit.
- **AC-12** (FR-9) Given a re-review pack holds J-2 and J-5, when the lens output gives a verdict for J-2 only, then the output is invalid. [derived: FR-9]
  Observable: collect prints `INVALID` naming the missing verdict for J-5; the juror counts as invalid. Level: unit.
- **AC-13** (FR-9) Given a re-review pack holds J-2, when the lens output gives a verdict for J-7, then the output is invalid. [derived: FR-9]
  Observable: collect prints `INVALID` naming J-7. Level: unit.
- **AC-22** (FR-9) Given a re-review pack holds J-2, when the lens output gives J-2 both fixed and not fixed, then the output is invalid. [derived: FR-9]
  Observable: collect prints `INVALID` naming J-2's second verdict. Level: unit.
- **AC-23** (FR-25) Given a re-review output holds a not-fixed verdict for J-2 and no finding at all, and J-2's lens judged a later version than the one J-2 was raised on, when it is collected, then J-2 is open, not fixed. [derived: FR-25]
  Observable: J-2's status is `open`, not `fixed`. Level: unit.
- **AC-14** (FR-15) Given J-4 was accepted as risk in the first review, when a lens re-runs, then its pack names J-4 as accepted and asks no verdict on it. [derived: FR-15]
  Observable: J-4 appears in the pack as accepted risk; a lens output with no verdict for J-4 is valid. Level: integration.
- **AC-15** (FR-17) Given ledgers written before this change, such as the grill-checks ledger, when `nio jury check` runs on them, then it loads them without error. [derived: FR-17]
  Observable: exit status 0 on a copy of `.nio/specs/grill-checks/jury/spec.json`. Level: integration.

### US-3 The jury skill drives the new rules (P1) [human]
- **Why this priority:** the CLI only composes outcomes; the skill decides what the human sees and what the lenses get,
  so steps 6 and 8 must say the same as the CLI.
- **Independent test:** read steps 6 and 8 of `skills/jury/SKILL.md`; they describe the one list for the human and the
  fix-check pack, and no longer describe re-running lenses on the whole spec.

- **AC-16** (FR-18, FR-3) Given the outcome is `human` after a re-review with no confirmed blocker, when the agent follows step 6, then it shows every listed finding in one message, each with fix and accept as risk as its options. [human]
  Observable: a `tests/test_jury.py` check finds in step 6 of `skills/jury/SKILL.md` the phrases "one message", "fix" and "accept as risk". Level: unit.
- **AC-17** (FR-18, FR-7, FR-12) Given a re-review, when the agent follows step 8, then each lens pack is a fix check that tells the lens to answer fixed or not fixed per finding and to raise only blockers. [human]
  Observable: a `tests/test_jury.py` check finds in step 8 of `skills/jury/SKILL.md` the phrases "fix-check pack", "not fixed" and "only blockers", and no longer the phrase "re-run only those lenses with packs that name the changed IDs". Level: unit.
- **AC-18** (FR-19) Given a copy of the plain-talk ledger, whose first run made rounds 1 and 2 and recorded `rejected` at round 2, and a round 3 that gives one major the verdict not fixed and raises no blocker, when `nio jury check` composes round 3, then it treats round 3 as a re-review. [derived: FR-19]
  Observable: a `tests/test_jury.py` case on that ledger shape; the outcome is `human` listing that major, not `rejected` as the first-review row would give. Level: integration.
- **AC-19** (FR-20) Given the shipped lens cards and the lens output format, when a re-review pack is handed to a lens, then its card has a `## Re-review` section saying what it gets, to give a fixed or not-fixed verdict per finding, and to stop once each has one, and the output format has a section for those verdicts. [derived: FR-7, FR-8, RF-5]
  Observable: each of `adversary.md`, `consistency.md`, `logic.md`, `scope.md`, `security.md` and `testability.md` in `src/nio/agents/` has a `## Re-review` heading whose section holds the phrases "fix-check pack", "fixed or not fixed" and "stop", and `nio jury template` shows a `## Verdicts` section. Level: unit.

## Functional requirements
- **FR-1** IF an open finding is a blocker the refuter confirmed THEN THE SYSTEM SHALL return the outcome `rejected`, so it is disposed of and another re-review runs, except in the final fix check (FR-21). [human]
- **FR-2** WHEN the jury composes the outcome of a re-review with no open confirmed blocker and one or more open majors or minors THE SYSTEM SHALL return the outcome `human` and list every one of those findings together. [human]
- **FR-3** WHEN the human is shown the findings of FR-2 THE SYSTEM SHALL let them choose, for each finding, to fix it or accept it as risk. [human]
- **FR-4** WHEN the human has settled every finding on the FR-2 list and fixed at least one THE SYSTEM SHALL run one final fix check on those fixes, as a re-review (FR-7, FR-8) that may raise only blockers. [human]
- **FR-5** WHEN every finding from the FR-2 list is fixed or accepted as risk, and either none was fixed or the final fix check has run and gave every finding the verdict fixed and raised no confirmed blocker, THE SYSTEM SHALL end the jury without another round and return the outcome `approved`, even if the spec changed after the last judged version, with reasons naming each fix no lens judged. [human]
- **FR-6** WHILE the jury is in its first review THE SYSTEM SHALL keep today's outcomes: any open finding, of any severity, leads to `rejected`, then dispositions and a re-review. [human]
- **FR-7** WHEN a lens re-runs in a re-review THE SYSTEM SHALL give it a fix-check pack holding each of its findings that was fixed since the judged version, the before and after text of the items the fixes changed, and the text of their neighbours, and no other text of the spec. [human]
- **FR-8** WHEN a re-review lens returns THE SYSTEM SHALL accept for each finding in its pack exactly one verdict, fixed or not fixed, with a reason. [human]
- **FR-9** IF a re-review output lacks a verdict for a finding in its pack, gives more than one for a finding, or gives one for a finding not in its pack, THEN THE SYSTEM SHALL treat the whole output as invalid. [agent]
- **FR-10** WHEN a re-review lens gives a finding the verdict fixed THE SYSTEM SHALL mark the finding fixed. [human]
- **FR-11** WHEN a re-review lens gives a finding the verdict not fixed THE SYSTEM SHALL reopen the finding and count one more failed round for it, at most once per round; for a blocker, it SHALL send the verdict to the refuter in the same batch as new blockers, and only a not-fixed blocker the refuter confirms starts another round. [human]
- **FR-12** IF a re-review lens, in a re-review or the final fix check, raises a new finding below blocker THEN THE SYSTEM SHALL show it to the human as a note only: it is not on the FR-2 list, needs no ruling and never changes the outcome. [human]
- **FR-13** WHEN a re-review lens raises a new blocker THE SYSTEM SHALL send it to the refuter and escalate it as in the first review, each extra juror getting the raising lens's fix-check pack with the new blocker, judging only that blocker and giving no fix verdicts, before it can start another round. [agent]
- **FR-14** WHEN `nio jury changed` runs THE SYSTEM SHALL print, besides the changed IDs and the lenses to re-run, the neighbour IDs: the items that cite a changed item and the items a changed item cites. [human]
- **FR-15** THE SYSTEM SHALL name in each re-review pack the findings the human accepted as risk or ruled out of scope (both human-only dispositions today, RF-9), and ask no verdict on them. [human]
- **FR-16** IF a finding has failed two rounds and another re-review would otherwise start THEN THE SYSTEM SHALL send it to the human instead, as today; it doesn't apply once the final fix check has run, where FR-21 and FR-23 decide. [agent]
- **FR-17** THE SYSTEM SHALL load ledgers written before this change without error. [agent]
- **FR-18** THE SYSTEM SHALL describe in steps 6 and 8 of the jury skill the one list for the human (FR-2, FR-3) and the fix-check re-review (FR-7, FR-8, FR-12). [human]
- **FR-19** THE SYSTEM SHALL count every round up to and including the first round the jury ledger recorded `rejected` as the first review, and every later round as a re-review. [human]
- **FR-21** IF the final fix check gives a finding the verdict not fixed, or raises a blocker the refuter confirms, THEN THE SYSTEM SHALL return the outcome `human` listing them, and run no further fix check. [human]
- **FR-22** WHILE a final fix check is owed (FR-4) and has not run THE SYSTEM SHALL return the outcome `rerun`, naming the fixes it must check, and never `approved`. [derived: FR-4]
- **FR-23** WHEN every finding the final fix check sent to the human (FR-21) is fixed or accepted as risk THE SYSTEM SHALL return the outcome `approved` without another check, with reasons naming each fix no lens judged. [human]
- **FR-24** THE SYSTEM SHALL count the first round collected after `nio jury check --record` recorded `human` for the FR-2 list as the start of the final fix check, and every later round as part of it. [agent]
- **FR-25** WHILE the jury is in a re-review or the final fix check THE SYSTEM SHALL mark a finding fixed only on a fixed verdict, never because its lens judged a later version without raising it again; the first review keeps that rule. [agent]
- **FR-20** THE SYSTEM SHALL give each shipped lens card a re-review section, and the lens output format a verdict section, so a lens can take a fix-check pack, give a fixed or not-fixed verdict per finding and stop once each has one (RF-5). [human]

## Rules

### Decision table: outcome once every lens has judged and the refuter has validated
Two rules come before this table: while a final fix check is owed and hasn't run, the outcome is `rerun` (FR-22); and before the final fix check, a finding that failed two rounds sends the jury to `human` (FR-16).

| review (first, re-review, final check owed, final check) | confirmed blocker open (yes, no) | other finding open (yes, no) | → outcome | Src |
| --- | --- | --- | --- | --- |
| final check owed | - | - | rerun: run the final fix check | [derived: FR-4] |
| first | yes | - | rejected: dispose, then re-review | [derived: FR-1] |
| re-review | yes | - | rejected: dispose, then re-review | [derived: FR-1] |
| final check | yes | - | human: one list, no further check | [derived: FR-21] |
| final check | no | yes | human: one list, no further check | [derived: FR-21] |
| first | no | yes | rejected: dispose, then re-review | [derived: FR-6] |
| re-review | no | yes | human: one list, each fixed or accepted as risk | [derived: FR-2, FR-3] |
| first | no | no | approved | [agent] |
| re-review | no | no | approved | [agent] |
| final check | no | no | approved | [agent] |

### Decision table: a finding in a re-review pack
| verdict (fixed, not fixed) | severity (blocker, major or minor) | → result | Src |
| --- | --- | --- | --- |
| fixed | - | fixed | [derived: FR-10] |
| not fixed | blocker | reopened with a failed round; the refuter checks it; once confirmed, starts another round, or in the final fix check goes to the human | [derived: FR-11, FR-21] |
| not fixed | major or minor | reopened with a failed round; goes on the human's list | [derived: FR-11, FR-2] |

## Key entities
- **Finding**: a problem a lens raised, in the ledger, with its severity, validation, status, disposition and failed-round count. [agent]
- **Fix-check pack**: what a re-review lens gets: its fixed findings, the changed items before and after, their neighbours, and the findings accepted as risk. [human]
- **Fix verdict**: a re-review lens's answer for one finding: fixed or not fixed, with a reason. [human]

## Success criteria
- **SC-1** Replayed on the grill and grill-checks juries, the new rules stop each after its second round. [human]
- **SC-3** `tests/test_jury.py` passes with checks for the stop rule, the fix verdicts and the neighbour IDs. [agent]

## Non-goals
- No new size rule: the scope lens already suggests a split above 8 FRs, and that suggestion reaches the human as an ordinary finding. [human]
- No second final fix check: a fix made after it, to a finding it sent to the human, is never reviewed. [human]
- No whole-spec re-review: a clash between a fix and a distant, unrelated item is left to the plan or the code. [human]
- No change to the first review, its lenses, packs or outcomes. [derived: FR-6]
- No change to the plan and tasks gates, which no stage runs yet. [agent]

## Glossary
- **First review**: the jury's first pass over the spec, where every planned lens judges the whole spec; escalation jurors and retries of an invalid output belong to the pass they run in, though each adds a round (RF-1, RF-2).
- **Re-review**: any later pass after fixes, where lenses check fixes instead of the whole spec.
- **Open finding**: a finding whose status is open, so not fixed, refuted, merged, dropped or disposed; a minor is open once grounded, since the refuter never validates minors.
- **Neighbour**: an item that cites a changed item, or that a changed item cites, one step away.
- **Final fix check**: the one fix check that runs after the human settles the list of not-fixed majors and minors, on the fixes made from it; it never leads to another.
- **Confirmed blocker**: a blocker finding the refuter confirmed.

## Risks and evidence against
- The final fix check sees only the fixes and their neighbours, and nothing reviews a fix made after it, so a fix that breaks something can still reach the plan unseen (issue #52, decision 1; Q5). [human]
- The ledger can't tell which fix changed which item, so a lens's pack holds every item changed since the version it judged, including items other lenses' fixes changed [research: RF-4].
- A fix-check pack holds only neighbours, so a fix that clashes with a distant, unrelated item can slip through to the plan or the code (issue #52, decision 2). [human]

## Decisions
- After the first review only a blocker the refuter confirms starts another round; majors and minors a re-review finds not fixed go to the human in one list, and a new major or minor is only a note (D-261026-r52z; Q8; the human, 2026-10-26 brainstorm, #52).
- A re-review is a fix check: the finding, the changed items before and after and their neighbours, and nothing else of the spec; it may raise only blockers (the human, 2026-10-26 brainstorm and Q2).
- No new size rule; the scope lens's split suggestion is enough (the human, 2026-10-26 brainstorm).
- Once the human's list is settled the jury records `approved`, naming the fixes no lens judged (the human, Q1).
- After the human settles the list, one final fix check reviews the fixes made from it, may raise only blockers and never leads to another; what it flags goes to the human (the human, Q5).
- The refuter checks a not-fixed verdict on a blocker before it starts a round (the human, Q3).
- The first review is every round up to the first recorded `rejected` (the human, Q4).
- The scope extensions FR-15 (accepted risks named in the pack) and FR-20 (a re-review section in each lens card) stay (the human, Q9).
- When the final fix check flags something and the human fixes or accepts it, the jury records `approved`, naming the fixes no lens judged (the human, J-5).

## Open points

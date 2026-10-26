# Grill log: 2026-10-26-jury-convergence

Append-only. One entry per question, below-the-bar call or derived item.

## Session 1 · 2026-10-26 · @nio:grill, the human answers in rounds

## Facts · OP-4, OP-5, OP-6, OP-7 · 2026-10-26
Facet: data (OP-4, OP-5), change (OP-6), actors (OP-7)
Found: RF-1, RF-2, RF-3 (rounds vs reviews; first recorded rejection), RF-4 (no per-fix change map), RF-5 (lens cards have no re-review mode), RF-6 (no confirmed blocker in any dogfood re-review), RF-7 (two failed rounds go to human today), RF-8 (any change after the judged version returns rerun today).
Patched: UJ-1 evidence, Risks (RF-4), Glossary first review; new FR-19, FR-20, AC-18, AC-19; retired OP-4, OP-5, OP-6, OP-7

## Asked · Q1 · OP-1 · 2026-10-26
Question: 1. When every item on your list is fixed or accepted, what should the jury record?
Context: Today the jury only approves a version a reviewer has read, and any edit after that forces another round (per the jury code). Under the stop rule, fixing items from your list is the normal way a jury ends, so the record either calls that an approval or calls it your decision. The record is what later stages and memory read as the gate's standing.
Options: 1. Approved, naming the unreviewed fixes (recommended): the normal ending reads as approved; the record lists which fixes no reviewer saw. Lost: "approved" no longer always means a reviewer read the final text. 2. Closed by you (human): the record says the gate closed on your call, as when you override today. Lost: every large spec looks like an override, so real overrides stand out less. 3. A new outcome, "settled": honest and distinct from both. Lost: a new outcome every reader of verdicts must learn, and more code.
Refs: OP-1, FR-5, AC-5, RF-8, jury.py:466-469

## Asked · Q2 · OP-2 · 2026-10-26
Question: 2. May a re-reviewer read the rest of the spec for context?
Context: You picked a fix check with neighbouring items; the cost you accepted was that a clash with a distant item can slip through. Reading the whole spec for context would catch some of those, but it is exactly the read that produced fresh wording findings in every past round (per issue #52). Only blockers can be raised in a re-review either way.
Options: 1. Fix-check material only (recommended): rounds stay small and cheap, as decided. Lost: distant clashes are left to the plan or the code. 2. Whole spec as read-only context: catches more distant clashes. Lost: each re-review costs about as much as the first, and reviewers drift back to judging unchanged text. 3. Only on request: the reviewer answers "needs more" and gets the whole spec on its retry. Lost: an extra run whenever it asks.
Refs: OP-2, FR-7, decision 2 in #52

## Asked · Q3 · OP-3 · 2026-10-26
Question: 3. Should the refuter double-check a reviewer's "not fixed" on a blocker before it starts another round?
Context: A "not fixed" on a blocker starts a whole new round, which is the expensive outcome. The refuter already checks new blockers in the same batch, so adding these usually costs no extra run, only a longer batch (per the jury code). A reviewer that misreads a fix would otherwise start a round on its own say-so.
Options: 1. Yes, in the same batch (recommended): a round starts only when two agents agree the blocker is still there. Lost: a slightly longer refuter run. 2. No, trust the reviewer: simpler. Lost: one wrong "not fixed" costs a whole round. 3. Send it to you instead: no new round from a "not fixed" ever. Lost: you judge blocker fixes yourself.
Refs: OP-3, FR-11, FR-13, decision table "a finding in a re-review pack"

## Asked · Q4 · FR-19 · 2026-10-26
Question: 4. How should the jury tell its first review from a re-review?
Context: The round counter also goes up for retries and extra reviewers, so "round 1" isn't the first review (per the jury code; the plain-talk jury's first review took two rounds). The records already keep each recorded outcome with its round.
Options: 1. Up to the first recorded rejection (recommended): no new data, works on existing jury records. Lost: relies on the skill always recording outcomes, which it does today. 2. Save which run each round came from: explicit. Lost: a new field in the jury records, and old records need a fallback anyway. 3. Count runs instead of rounds: simple to explain. Lost: runs aren't ordered by name, so the code would need run start times.
Refs: FR-19, AC-18, RF-1, RF-2, RF-3

## Q1 · OP-1 · 2026-10-26
Facet: meaning, data
Question: When every item on your list is fixed or accepted, what should the jury record?
Options:
1. Approved, naming fixes (recommended)
2. Closed by you
3. New outcome "settled"
Answer: 1. Approved, naming fixes: the normal ending reads as approved, and the record lists which fixes no reviewer saw. Lost: "approved" no longer always means a reviewer read the final text. [human]
Patched: FR-5, AC-5; retired OP-1

## Q2 · OP-2 · 2026-10-26
Facet: change
Question: Can a re-reviewer read the rest of the spec for context?
Options:
1. Fix-check only (recommended)
2. Whole spec as context
3. Only when it asks
Answer: 1. Fix-check only: rounds stay small and cheap, as decided. Lost: distant clashes are left for the plan or the code to catch. [human]
Patched: FR-7; retired OP-2

## Q3 · OP-3 · 2026-10-26
Facet: failure, actors
Question: Should the refuter double-check a reviewer's "not fixed" on a blocker before it starts another round?
Options:
1. Yes, same batch (recommended)
2. No, trust the reviewer
3. Send it to you
Answer: 1. Yes, same batch: a round starts only when two agents agree the blocker is still there. Lost: the refuter's run gets slightly longer. [human]
Patched: FR-11; decision table "a finding in a re-review pack" rows not fixed [derived: FR-11]; new AC-20 [derived: FR-11]; retired OP-3

## Q4 · FR-19 · 2026-10-26
Facet: data, verification
Question: How should the jury tell its first review from a re-review?
Options:
1. First recorded rejection (recommended)
2. Save the run per round
3. Count runs, not rounds
Answer: 1. First recorded rejection: everything up to the first recorded rejection is the first review. It needs no new data and works on existing jury records. Lost: it depends on the skill always recording outcomes, which it does today. [human]
Patched: FR-19 [human]; AC-18 [derived: FR-19]

## Call · FR-12 · 2026-10-26
FR-12 (new majors and minors from a re-review go on the human's list) is the human's brainstorm decision 1 word for word: tagged [human], not a call.

## Call · A-2, FR-9, FR-13, FR-15, FR-17, SC-2, SC-3, outcome table row "no, no → approved", Finding, Non-goal "plan and tasks gates" · 2026-10-26
Each restates today's behaviour or a test target: the agent's role (A-2), an invalid output on a missing or extra verdict (FR-9, re-run once as today), escalation of a new blocker as today (FR-13), accepted risks named in the pack as step 8 does today (FR-15), old ledgers still load (FR-17), the run count and test targets (SC-2, SC-3), approve with nothing open (today's compose), the Finding entity, and leaving the unused plan and tasks gates alone.
Five no's: none changes what a user can do, what they see, who may do it, what data is kept, or what it costs beyond the decisions already made.
Patched: tagged [agent]

## Derived · UJ-1, UJ-2, AC-1, AC-4, AC-6, AC-7, AC-11, AC-12, AC-13, AC-14, AC-15, AC-18, AC-20, Non-goal "first review" · 2026-10-26
Each follows from the answered or researched items it cites (FR-1, FR-2, FR-3, FR-5, FR-6, FR-7, FR-8, FR-9, FR-11, FR-15, FR-16 [research: RF-7], FR-17, FR-19).
Patched: tagged [derived: …]

## Finish gate · passivity · 2026-10-26
The human accepted all 7 recommendations (3 brainstorm, Q1-Q4), so they were asked which they'd push back on. They named "only blockers start rounds" and chose finish, so that point was asked again first (Q5).

## Asked · Q5 · FR-4 · 2026-10-26
Question: What should change about "only blockers start another round"?
Context: After the first review, majors and minors go to you as one list and their fixes are never reviewed. In past juries those fixes produced the next round's majors (per issue #52), but no re-review ever found a confirmed blocker (per the old jury records).
Options: 1. One final fix check (recommended): after you settle the list, one last fix check runs on just those fixes (fixed or not fixed, only blockers) and never starts another. Lost: one more short round on every jury, but nothing goes unreviewed. 2. Majors start rounds, capped: confirmed majors also start a round, up to 2 re-reviews, then everything goes to you. Lost: on past specs, 3 rounds instead of 2, about 1.5x the cost. 3. Keep it as decided: fixes from your list stay unreviewed, named in the approval record. Lost: nothing beyond what you accepted.
Refs: FR-1, FR-2, FR-4, FR-5, RF-6, decision 1 in #52

## Q5 · FR-4 · 2026-10-26
Facet: change, failure
Question: What should change about "only blockers start another round"?
Options:
1. One final fix check (recommended)
2. Majors start rounds, capped
3. Keep it as decided
Answer: 1. One final fix check: after you settle the list, one last fix check runs on just those fixes. It answers fixed or not fixed, can raise only blockers, and never starts another one. Lost: one more short round on every jury, but nothing goes unreviewed. [human]
Patched: Summary, UJ-2, FR-1, FR-4, FR-5, new FR-21, AC-5, new AC-21 [derived: FR-4, FR-21], outcome table (final check rows), re-review pack table (not-fixed blocker row), Non-goal "no second final fix check", Risks, Glossary "Final fix check", Decisions

## Finish · 2026-10-26
Fidelity re-read of FR-4, FR-5, FR-7, FR-11, FR-19, FR-21, AC-5, AC-21 against Q1-Q5: Q1's "record lists which fixes no reviewer saw" now covers only fixes made after the final fix check (FR-5). The human chose finish.

## Session 2 · 2026-10-26 · jury round 1 finding J-5, the human answers

## Asked · Q6 · J-5 · 2026-10-26
Question: After the final fix check flags something and you deal with it, how does the jury end?
Context: If the final check says a fix didn't work, the jury goes to you, but no rule says what happens once you fix or accept it, so it stays stuck. Today the only exit is closing the gate by hand.
Options: 1. Approved, naming fixes (recommended): you fix or accept each flagged item and the jury records "approved", naming the fixes no reviewer saw, the same as Q1. Lost: those last fixes stay unreviewed. 2. Closed by you: the record says the gate closed on your call. Lost: it reads like an override. 3. One more check, then you: your new fixes get one more fix check. Lost: an extra round, and "never leads to another check" no longer holds.
Refs: J-5, FR-5, FR-21, AC-21, D-261026-r52z

## Q6 · J-5 · 2026-10-26
Facet: failure
Question: After the final fix check flags something and you deal with it, how does the jury end?
Options:
1. Approved, naming fixes (recommended)
2. Closed by you
3. One more check, then you
Answer: 1. Approved, naming fixes: you fix or accept each flagged item, and the jury records "approved", naming the fixes no reviewer saw. It works the same way as your earlier answer about settling the list. Lost: those last fixes stay unreviewed. [human]
Patched: FR-5, new FR-23 [human], AC-26 [human], Decisions

## Session 3 · 2026-10-26 · jury round 2 findings, the human answers in a round

## Asked · Q7 · process · 2026-10-26
Question: 1. How should this jury continue?
Context: Round 2 found no blockers, 13 majors and minors, mostly about round 1's fixes. Today's rules mean a full round 3 (about 5 runs); this spec's rule means settling the list and one final fix check.
Options: 1. Use the new rule by hand (recommended): fix the 13, run one final fix check on those fixes only (blockers only, no round after); if it passes, the human closes the gate, recorded as closed by the human. 2. Full round 3 as today. 3. Fix and close now.
Refs: round 2 verdict, D-261026-r52z, jury SKILL step 8

## Asked · Q8 · J-21 · 2026-10-26
Question: 2. If a re-reviewer raises a new major anyway, does it count?
Context: "A re-review may raise only blockers" and "new majors and minors go to you in one list" pull apart (logic reviewer). If only blockers count, the list holds the findings a reviewer says aren't fixed.
Options: 1. Only blockers count (recommended): a new major or minor from a re-review or the final check is dropped and shown as a note only. 2. Majors go on your list. 3. Majors kept, minors dropped.
Refs: J-21, J-17, FR-4, FR-12, AC-2, #52 decisions 1-2

## Asked · Q9 · J-8, J-23 · 2026-10-26
Question: 3. Keep two small additions the scope reviewer says you never asked for?
Context: Re-reviewers are told which findings were accepted as risk or ruled out of scope (as the skill does today); each reviewer card gets a re-review section.
Options: 1. Keep both (recommended). 2. Keep only the first. 3. Drop both.
Refs: J-8, J-23, FR-15, FR-20, RF-5, RF-9

## Q7 · process · 2026-10-26
Question: How should this jury continue?
Options:
1. Use the new rule by hand (recommended)
2. Full round 3 as today
3. Fix and close now
Answer: 1. Use the new rule by hand: I fix the 13 findings, then run one final check limited to those fixes (blockers only, no round after it). If it passes, the gate closes on your call, recorded as closed by you, since the code doesn't support this rule yet. Lost: the record says "closed by you" rather than "approved". [human]
Patched: none (process)

## Q8 · J-21 · 2026-10-26
Facet: meaning
Question: If a re-reviewer raises a new major anyway, does it count?
Options:
1. Only blockers count (recommended)
2. Majors go on your list
3. Majors kept, minors dropped
Answer: 1. Only blockers count: a new major or minor from a re-review or the final check is dropped and shown to you as a note only. Your list holds only "not fixed" findings. That's the tightest stop. Lost: a real new major is only a note you might skim past. [human]
Patched: Summary, FR-12, AC-2, Glossary "Final fix check", Decisions; D-261026-r52z

## Q9 · J-8, J-23 · 2026-10-26
Facet: change
Question: Keep two small additions the scope reviewer says you never asked for?
Options:
1. Keep both (recommended)
2. Keep only the first
3. Drop both
Answer: 1. Keep both: both are needed for the fix check to work: without the first, accepted risks come back; without the second, reviewers still review the whole spec. Lost: a few more lines in each reviewer's instructions. [human]
Patched: FR-15 [human], FR-20 [human], Decisions

## Session 4 · 2026-10-26 · the final fix check (by hand), the human answers

## Asked · Q10 · J-14 · 2026-10-26
Question: What should happen to the one finding the final check marked "not fixed"?
Context: The final check confirmed 10 of 11 fixes and raised no blocker. Consistency couldn't see the outcome table (the pack held numbered items only), so it couldn't confirm the note above it; logic judged the same fix as working. Logic also noted AC-28 calls new findings list-worthy, though under Q8 they are notes.
Options: 1. Add the row and fix the wording (recommended): an explicit "final check owed → rerun" row and AC-28's wording; the gate closes on the human's call, naming both edits as unreviewed. 2. Accept the note as is. 3. Fix both and re-check the table.
Refs: J-14, J-20, AC-28, FR-21, FR-23, run R-261026-byv4

## Q10 · J-14 · 2026-10-26
Question: What should happen to the one finding the final check marked "not fixed"?
Options:
1. Add the row and fix the wording (recommended)
2. Accept the note as is
3. Fix both and re-check the table
Answer: 1. Add the row and fix the wording: I add an explicit "final check owed → rerun" row to the table and correct the test's wording. Then the gate closes on your call, and the record names these two fixes as unreviewed. Lost: no reviewer sees those two small edits. [human]
Patched: outcome decision table (row "final check owed", approved rows split by review), AC-28

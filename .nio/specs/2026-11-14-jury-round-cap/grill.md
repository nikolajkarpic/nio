# Grill: 2026-11-14-jury-round-cap

Session 1 (2026-11-14): the human answered Q1-Q7; an agent recorded them and looked up the facts.

## Lookup · OP-1, OP-7, OP-8 · 2026-11-14
Facet: change from today, verification
Found: RF-1 (OP-1, rounds per gate on 2026-11-08), RF-2 to RF-4 (OP-7, escalation jurors bump the round today), RF-5 (OP-8, one ledger and round count per epic). Retired OP-1, OP-7, OP-8.
Patched: UJ-1 evidence, AC-3, FR-4, FR-1, Round cap entity

## Q1 · OP-6 · 2026-11-14
Question: At the round cap, what should an extra round re-check?
Context: After round 2 the cap stops the gate; the human can ask for more. A single open blocker is read as a major (stated in Q2's context, not contested).
Options:
1. Your picks, once: one more round over the findings you pick.
2. Your picks, unlimited: as 1, as often as you ask.
3. Whole gate, once: one more full round.
Answer: free-form: "if it has multiple ciritcal issues filed in there then yes auto run third, if medium issue ask, if low then just skip them". Written as: 2 or more open blockers at the cap start one automatic third round, once per gate, on those blockers' lenses only; open majors (and a single lone blocker) go to the human in one batch (accept as risk, fix, one more round); open minors are closed as accepted risk by the system with note "minor, skipped at the round cap" and listed in the gate summary; no fourth automatic round, anything open after the third goes to the batch. [human]
Refs: OP-6, FR-5, UJ-1
Patched: Summary, UJ-1, AC-1, AC-14, AC-15, AC-16, FR-2, FR-13, FR-14, FR-15, state table, cap decision table, SC-1; derived AC-4, AC-17, FR-5 (FR-5 and AC-4 later set by Q6); retired OP-6; opened OP-9 (scope of a human-asked round, not answered)

## Derived · AC-17 · 2026-11-14
From: FR-2, FR-13 (Q1), and Q2's context, which stated to the human that a single blocker counts as a major; not contested.

## Derived · FR-5, AC-4 · 2026-11-14
From: FR-14 (Q1): after any extra round, anything open goes to the human batch; never a further automatic round.

## Q2 · OP-2 · 2026-11-14
Question: At the spec and plan gates there are no tasks; what does "fix" mean there at the cap?
Context: A single open blocker counts as a major and goes to the human batch.
Options:
1. Edit, no re-check: the orchestrator edits spec or plan for each finding ruled fix, and the gate closes with no juror re-check.
2. Edit + one-lens check: only the lens that raised it checks the fix once, not a round.
3. No fix option there: only accept as risk or another round.
Answer: 1. Edit, no re-check: the orchestrator edits spec/plan for each finding ruled fix, and the gate closes with no juror re-check; the human's ruling is the approval. [human]
Refs: OP-2, FR-2
Patched: FR-16, AC-18; retired OP-2

## Q3 · OP-3 · 2026-11-14
Question: `out-of-scope` is human-only today; may the system set it on its own for later-epic findings?
Options:
1. Auto, when tasks.md proves it.
2. Auto-propose, you confirm.
3. Juror skips them: the conformance card ignores later-epic ACs, no code check.
Answer: 1. Auto, when tasks.md proves it: NIO sets out-of-scope on its own only when tasks.md shows the AC is served by a task in a later, not-yet-built epic; it logs the task ID; dismissals are listed in the gate summary. Lifts out-of-scope from human-only for this one case only, with the system recorded as actor. [human]
Refs: OP-3, FR-12, src/nio/jury.py:24
Patched: FR-12, AC-12, Gate summary entity; retired OP-3

## Q4 · OP-4 · 2026-11-14
Question: Which disposition does a finding take when its fix task is retired, and who is recorded as setting it?
Options:
1. Accepted risk.
2. New 'retired' outcome.
3. Out of scope.
Answer: 1. Accepted risk: retiring a fix task closes its finding as accepted-risk, credited to whoever retired it, note = retirement reason; a later round must not re-create it. [human]
Refs: OP-4, FR-11
Patched: FR-11, AC-11, UJ-2, tasks decision table; retired OP-4

## Q5 · OP-5 · 2026-11-14
Question: Is expanding globs in a task's Files list before jurors cite them (#126, J-2) in this spec?
Options:
1. Include it.
2. Separate issue.
3. Drop it.
Answer: 1. Include it: expand glob patterns in a task's Files list to real paths when jury/worker packs are built; a pattern matching nothing is shown as such, never as a literal path. [human]
Refs: OP-5, Non-goals
Patched: US-3, AC-19, AC-20, FR-17; retired OP-5

## Q6 · OP-9 · 2026-11-14
Question: When you rule "one more round", does it re-check only the lenses of the findings you sent back or the whole gate, and may you ask again after it?
Options:
1. Your picks, can repeat: only the lenses of the findings sent back; a new batch afterwards, on which you may ask again.
2. Your picks, once.
3. Whole gate, once.
Answer: 1. Your picks, can repeat: a round the human asks for re-checks only the lenses of the findings they sent back; afterwards they get a new batch and may ask again; never an automatic repeat. [human]
Refs: OP-9, FR-5, AC-4
Patched: FR-5, AC-4, state table extra-round row; retired OP-9

## Q7 · defaults · 2026-11-14
Question: Confirm the remaining proposals as written?
Options:
1. Confirm all.
Answer: 1. Confirm all: A-2 (orchestrating agent), FR-7 and AC-6 (a bad `jury.max_rounds` stops with an error naming it), AC-7 (no open findings: no batch), FR-10 and AC-10 (a changed planned task reopens the tasks gate), AC-13 (current or earlier epic findings handled as today), the closed state-table row, and the planned-task-changed decision row. [human]
Refs: A-2, FR-7, AC-6, AC-7, FR-10, AC-10, AC-13
Patched: those items to [human]

## Q8 · jury batch · 2026-11-14
Question: Rule the spec jury's open findings (round 1): empty capped batch never closes (J-1); how a finding ties to an AC and "built" (J-9); undefined tasks.md changes (J-10); stop rule vs the reviewing row (J-7); research-only cross-round escalation count (J-6); no AC for refused or partial rulings (J-11).
Options:
1. All as recommended: fix J-1, J-9, J-10, J-7, J-11 as the jurors proposed; accept J-6 as risk, keeping the rule.
Answer: 1. All as recommended. J-9: match only the AC ID the finding cites; "built" = the serving task's epic has no closed implementation gate yet; no AC cited, or an AC served in both a later and the current/earlier epic, is handled as today. J-10: a mixed change reopens the gate; an edited fix task reopens it; a fix outside `#### Fixes` counts as planned; a retirement with no reason is rejected. J-6: keep the rule; it stops the endless escalation loop seen on onboarding. [human]
Refs: J-1, J-6, J-7, J-9, J-10, J-11
Patched: FR-6, FR-10, FR-11, FR-12, FR-18, FR-19, FR-20, AC-22 to AC-28, gate-rounds state table, tasks decision table, cap decision table, Decisions

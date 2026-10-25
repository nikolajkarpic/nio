# Grill log: jury

Append-only. One entry per question, below-the-bar call or derived item.

## Session 1 · 2026-10-25 · @nio:grill, the human answers

## Facts · OP-1, OP-2, OP-9, OP-11 · 2026-10-25
Looked up: RF-1 to RF-10 in research.md (actors from #27/#47 and a live gate run; which cards exist; no lens cap or hit
rate yet; nothing records the judged spec version; the escalation conflict; the gate guard; #27's authority and
composition; deferred findings; plan/tasks artefacts don't exist; what scope and consistency check).
Patched: summary, A-2, UJ-1, UJ-2, FR-1, FR-14, FR-15, both decision tables, a non-goal; retired OP-1, OP-2, OP-9, OP-11

## Derived · OP-7, OP-10 · 2026-10-25
Settled by #47 and #27 (RF-10, RF-7): the scope lens gets intake.md and the consistency lens the memory pack; the agent
judges whether a fix changes behaviour, listed for the human. Added FR-24, FR-25, AC-25, AC-26; retired OP-7, OP-10.

## Derived · AC-1, AC-14, AC-15, SC-1, SC-2, SC-3 · 2026-10-25
From FR-1, FR-14, FR-15, FR-16, FR-13, FR-22.

## Call · US-1 to US-6, FR-23, AC-24, non-goal "a cheap model checking each verdict" · 2026-10-25
Below the bar: story priorities and wording; FR-23 records the judged spec version (how, after RF-4). [agent]

## Q1 · OP-5 · 2026-10-25
Question: What does triage do in v1, and which rule for 3 jurors wins: NORTH_STAR's or #47's?
Options: 1. #47 wins; rung from risk flags (recommended) 2. #47 wins; triage card now 3. NORTH_STAR wins
Answer: 1 [human]
Patched: FR-3, AC-3, UJ-1; added a non-goal; retired OP-5, A-5; NORTH_STAR's escalation ladder updated

## Q2 · OP-6 · 2026-10-25
Question: What counts as a 'high-severity' finding that makes its lens re-run with 3 jurors?
Options: 1. Confirmed blocker only (recommended) 2. Confirmed blocker or major 3. Blocker, before the refuter
Answer: 1 [human]
Patched: FR-21; retired OP-6

## Q3 · OP-3 · 2026-10-25
Question: A triggered lens has no card yet. What does the jury do?
Options: 1. Write the 5 cards now (recommended) 2. Core cards now, block the rest 3. Skip missing, with consent
Answer: 1 [human]
Patched: FR-26, AC-27, Decisions; retired OP-3

## Q4 · OP-4 · 2026-10-25
Question: Who decides when the consistency lens runs, and the scope triggers that aren't a count?
Options: 1. The skill, from pack and trace (recommended) 2. Always run both 3. CLI triggers only
Answer: 1 [human]
Patched: FR-27, AC-28, Decisions; retired OP-4

## Q5 · OP-8 · 2026-10-25
Question: On a host without subagents, may the jury agent play a lens itself?
Options: 1. Fresh session, never the same one (recommended) 2. Play it, marked weaker 3. Block without subagents
Answer: 1 [human]
Patched: FR-28, AC-29, Decisions; retired OP-8

## Finish · 2026-10-25
`nio check spec jury --gate` passes with 0 errors. The human chose finish at the finish gate. Next: implement the jury skill and the five lens cards.

## Derived · UJ-1 step 2, AC-2, AC-7, FR-7, glossary Rung · 2026-10-25 (implementation review)
Consequences of Q1 (OP-5: no triage agent; the risk flags set the rung) that the grill missed: five lines still named
triage. Now derived from FR-3 and FR-27. Also moved FR-23 to FR-28 into `## Functional requirements` (they had landed
after the decision tables).

## Session 2 · 2026-10-25 · from the first real jury run (the grill spec)

## Q6 · FR-24 · 2026-10-25
Question: The scope lens judged the grill spec against the intake alone, so it flagged your own grill answers as 'not asked for'. What should the scope lens see?
Options: 1. Intake + your grill answers (recommended) 2. Intake only, as decided 3. Whole grill.md
Answer: 1 [human]
Patched: FR-24, AC-25, Decisions

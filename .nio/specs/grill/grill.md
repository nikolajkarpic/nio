# Grill log: grill

Append-only. One entry per question, below-the-bar call or derived item.

## Session 1 · 2026-10-25 · by hand (before the grill existed)

## Q1 · OP-3 · 2026-10-25
Question: When does a grill session end as done?
Options: 1. Green AND you confirm (recommended) 2. Green is enough 3. You decide, any time
Answer: free form: green and confirm, and agents must be able to run and confirm a grill too [human]
Patched: FR-17, AC-11; retired OP-3

## Q2 · OP-3 follow-up · 2026-10-25
Question: How far does an agent stand in for you?
Options: 1. Delegate, tagged [agent] (recommended) 2. Agent drives, you answer 3. Fully autonomous
Answer: 1 [human]
Patched: FR-25, FR-26, FR-27, US-8, AC-25, AC-26

## Q3 · OP-4 · 2026-10-25
Question: When the grill ends early, where do unsettled points go, and can that spec pass the gate?
Options: 1. Deferred section, jury sees them (recommended) 2. Can't pass until resumed 3. Become non-goals
Answer: 1 [human]
Patched: FR-18, FR-28, AC-12; retired OP-4

## Q4 · OP-7 · 2026-10-25
Question: What provenance does a point settled by consequence carry?
Options: 1. [derived: …] with sources (recommended) 2. [human] after review 3. Ask them anyway
Answer: 1 [human]
Patched: FR-11, FR-29, AC-16; retired OP-7

## Q5 · OP-8 · 2026-10-25
Question: Does each grill answer also become a memory decision record?
Options: 1. Records only for weighty ones (recommended) 2. One record per answer 3. One record per session
Answer: 1 [human]
Patched: FR-6, AC-6; retired OP-8

## Q6 · OP-11 · 2026-10-25
Question: Who keeps grill.md: the agent following the skill, or the nio CLI?
Options: 1. Spec is state, grill.md is a log (recommended) 2. CLI-managed grill state 3. Agent-kept state file
Answer: 1 [human]
Patched: FR-19, FR-20, AC-19, AC-20; retired OP-11

## Q7 · OP-9 · 2026-10-25
Question: Must every question have exactly 3 options, even when only one or two make sense?
Options: 1. 3 normally, fewer if honest (recommended) 2. Always exactly 3 3. Open question first
Answer: 1 [human]
Patched: FR-4, AC-4; retired OP-9

## Q8 · OP-6 · 2026-10-25
Question: What is the rising bar for asking, and what happens to points below it?
Options: 1. Behaviour bar; minor = [agent] (recommended) 2. Below the bar = deferred 3. No bar, budget only
Answer: 1 [human]
Patched: FR-10, FR-16, AC-14; retired OP-6

## Q9 · OP-5 · 2026-10-25
Question: What is the soft budget, and what happens when you say 'don't continue'?
Options: 1. Check in every 15; offer 3 ways (recommended) 2. Scaled to spec size 3. Fixed 15, then end
Answer: 1 [human]
Patched: FR-15, AC-13; retired OP-5

## Q10 · OP-10 · 2026-10-25
Question: Can a grill end early while a contradiction is still open?
Options: 1. Yes, deferred as a blocker (recommended) 2. No, resolve first 3. Yes, like any point
Answer: 1 [human]
Patched: FR-30, AC-27; retired OP-10

## Q11 · OP-15 · 2026-10-25
Question: Do the architecture grill and the user advocate feed ship with this grill, or later?
Options: 1. Later, with those stages (recommended) 2. Ship the hooks now 3. Keep, but untested
Answer: 1 [human]
Patched: retired US-7, AC-23, AC-24, FR-21, FR-22, A-4, UJ-4; added a non-goal; retired OP-15

## Facts · OP-2, OP-12, OP-13, OP-14 · 2026-10-25
Looked up, not asked: "deepdive first" was a working instruction, not a requirement; "checklist green" is
`nio check spec --gate` (RF-4); no research stage exists yet, so the grill looks facts up itself; #25 and #37 aren't built.
Patched: FR-8, AC-18; retired OP-2, OP-12, OP-13, OP-14

## Session 2 · 2026-10-25 · @nio:grill, the human answers

## Facts · OP-1 · 2026-10-25
Looked up: RF-1 (actors and journeys from #22), RF-2, RF-3, RF-4 in research.md.
Patched: A-1, A-2, A-3, UJ-1, a non-goal; retired OP-1

## Derived · UJ-2, UJ-3, FR-1, AC-1, AC-21, SC-1, SC-2, SC-3, state table rows, key entities · 2026-10-25
From: FR-2, FR-3, FR-4, FR-6, FR-13, FR-17, FR-18, FR-19, FR-20, FR-25, FR-28, FR-30 (the spec is the state; deferring;
contradictions; resume from the log).

## Call · US-1 to US-6 · 2026-10-25
Below the bar: story priorities and wording change no behaviour. Kept as drafted. [agent]

## Call · Candidate point, non-goal "Judging the spec's quality" · 2026-10-25
Below the bar: wording only. [agent]

## Q12 · FR-24 · 2026-10-25
Question: When your free-form answer leaves a point vague, does the grill ask a follow-up on the same point?
Options: 1. Follow up once, then ask (recommended) 2. Follow up until clear 3. Record as given
Answer: 1 [human]
Patched: FR-24, AC-7

## Finish · 2026-10-25
`nio check spec grill --gate` passes with 0 errors. The human chose finish at the finish gate. Next stage: the spec jury.

## Derived · Rules: decision table "ask, settle or wait" · 2026-10-25 (review)
The table predated the bar: it asked every decision once prerequisites were settled, contradicting FR-10 and FR-16.
Added the "above the bar" condition; the new row (below the bar → agent call) is derived from FR-16.

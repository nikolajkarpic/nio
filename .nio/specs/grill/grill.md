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

## Session 3 · 2026-10-25 · review against Pocock's grilling skills (mattpocock/skills @ 5beb35b)

## Q13 · FR-3 and new FR-31 to FR-33 · 2026-10-25
Question: Which of these should go into @nio:grill (and nio check spec)?
Options (several allowed): 1. Glossary discipline + check (recommended) 2. Answer fidelity + passivity (recommended)
3. Don't know / prototype + no chains (recommended) 4. Optional rounds mode
Answer: 1, 2 and 4 [human]
Patched: FR-3, AC-3; added FR-31, FR-32, FR-33, AC-28, AC-29, AC-30; Decisions

## Derived · UJ-1 misuse, US-1 why, AC-28 · 2026-10-25 (review)
Rounds mode (FR-3) allows independent questions together, so the misuse is mixing dependent ones; Decisions may name a
renamed term.

## Session 4 · 2026-10-25 · fixes from the spec jury (V-261025-qmmq, rejected)

## Jury fix · J-1, J-3 · state table
The contradiction state now asks the resolution question (ask next → contradiction) and its answer resolves it
(answer → idle); asking waits for a question or a whole round (FR-3, FR-13). No behaviour change. [agent]

## Jury fix · J-4, J-7 · non-goals
"Several questions in one message" is now "by default; rounds mode is opt-in (FR-3)"; "guessing" now excepts the
below-the-bar `[agent]` calls (FR-16). They had gone stale after Q13 and Q8. [agent]

## Jury fix · J-13 · AC-10
The Observable is checkable: every decision point `--gate` listed ends `[human]`, `[agent]`, `[derived]` or `[deferred]`. [agent]

## Q14 · J-2, J-5, J-6, J-9, J-12, J-17 · 2026-10-25
Question: The jury found four behaviours in the grill spec that no logged answer of yours names. Which do you keep?
Options (several allowed): 1. Money + breaking changes always asked: permissions, irreversible operations, money,
deletion and breaking changes are never below the bar and always wait for the human, even when delegated (recommended)
2. Configurable 15 + epic suggestion: the interval is configurable (default 15), and the first pause suggests an epic
when more than 15 points are open (recommended) 3. Passivity only above 3 answers (recommended) 4. Facts carry their
source: each verified fact in a question names its RF-n, file:line or spec ID (recommended)
Answer: 1. Money + breaking changes always asked; 2. Configurable 15 + epic suggestion; 4. Facts carry their source [human]
Patched: FR-12, decision table header, FR-33 (no threshold), FR-4, AC-4, Decisions; added AC-31, AC-32, AC-33 (J-15)

## Q15 · J-14 · 2026-10-25
Question: How does the grill decide that a goal's core facet is 'covered', and that a point is below the bar?
Options: 1. Logged checklist: a facet is covered when grill.md logs a question or call for that goal tagged with it; the
bar is a fixed yes/no list (can a user do, see, who may, data, cost), any yes means ask, recorded per call (recommended)
2. Facets as spec sections 3. Leave it to judgement
Answer: 1. Logged checklist: a facet is covered when grill.md logs a question or call tagged with it; the bar is the
five-question yes/no list, any yes means ask, recorded per call [human]
Patched: FR-9, FR-10, AC-14, AC-15, Decisions; and FR-4 (J-17, which hadn't applied)

## Q16 · J-16 · 2026-10-25
Question: What does the grill do when a fact lookup finds nothing, or finds conflicting answers?
Options: 1. Show it, then you choose: show what was searched and found; the human decides it now ([human]) or defers it
(DF-n); a conflict between sources is a contradiction (recommended) 2. Always defer 3. Always ask you
Answer: 1. Show it, then you choose: show what was searched and found; decide now ([human]) or defer (DF-n); conflicting
sources are a contradiction [human]
Patched: FR-34, AC-34, Decisions

## Q17 · J-10 · 2026-10-25
Question: Should the grill spec split its `nio check spec` changes into a slice of their own?
Options: 1. Out of scope: it's built (recommended) 2. Accept the risk 3. Split it: an epic with two slices (the grill
loop, the checker changes), each re-drafted and juried
Answer: 3. Split it: an epic with two slices, the grill loop and the checker changes, each juried [human]
Patched: epic "grilling/R-1"; retired FR-27, FR-28, FR-29 (to the grill-checks slice); AC-12, AC-16, AC-25, AC-27, AC-28,
FR-30, UJ-2 trimmed to the grill's own behaviour; Decisions

## Q18 · J-20 · 2026-10-25
Question: How does the append-only grill.md record a question you haven't answered yet, so a crashed session can resume it?
Options: 1. Two entries: asked, then answered: an `Asked · Qn` entry when asking, the answer entry when answering; on
resume an Asked entry with no answer is asked first (recommended) 2. Drop AC-21, re-derive 3. Pending file
Answer: 1. Two entries: an Asked entry when asking, then the answer entry; on resume an Asked entry with no answer is
asked first [human]
Patched: FR-19, FR-20, AC-19, AC-21, Decisions

## Jury fix · J-18, J-19, J-22, J-29 · round 2
The decision table gains "lookup settles it" (an unfindable fact goes to the human, FR-34) and "core facets covered"
(the bar applies only after them, FR-9); FR-9 and AC-15 count only questions and fact lookups toward coverage; the
contradiction state holds until resolved and flags a second one; AC-17 and AC-26 cover the full always-human list. [agent]

## Q19 · J-31 to J-35 · 2026-10-25
Question: The logic lens found 5 new issues in round 3. How do we close the grill spec's jury?
Options: 1. Fix wording, accept the rest: fix J-33 and J-35, accept J-31, J-32 and J-34 as risk in #51, record the verdict
without another lens round, and open an issue for a jury convergence rule (recommended) 2. One more fix round 3. Decide
all five yourself now
Answer: 1. Fix wording, accept the rest, record the verdict without another lens round [human]
Patched: AC-11 (only finish ends as done), AC-15 (the facet order applies among settled prerequisites)

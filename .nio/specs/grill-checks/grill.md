# Grill log: grill-checks

Append-only. One entry per question, below-the-bar call or derived item.

## Session 1 · 2026-10-25 · @nio:grill, the human answers

## Facts · OP-1, OP-3, OP-4 · 2026-10-25
Facet: actors (OP-1), data (OP-3, OP-4), change (OP-3)
Found: RF-1 (actors are the epic's), RF-2 (any RF-n passes as a derived source), RF-3 (deferred findings on every collect, once per DF), RF-4 (a grill session may close a deferred finding).
Patched: A-1, A-2, A-3; retired OP-1, OP-4. OP-3 stays open as a decision: RF-2 contradicts FR-3.

## Q1 · OP-2 · 2026-10-25
Question: Who may close a deferred finding: only the human directly, or also a grill session that settles the point?
Options: 1. Grill may close via spec-fix (recommended) 2. Only --by human, ever 3. Grill closes only if you answered
Answer: 1. Grill may close via spec-fix: you close a deferred finding directly (accepted risk or out of scope), or a grill session closes it by settling the point (a spec-fix that changes the spec). Agents can never close one. Settling a point isn't accepting a risk, and the new answer's tag stays visible. No code change. [human]
Patched: FR-16, decision table "closing a deferred finding"; retired OP-2

## Q2 · OP-3 · 2026-10-25
Question: When a `[derived: …]` tag cites an RF-n that research.md doesn't contain, should the check catch it?
Options: 1. Tighten the check (recommended) 2. Loosen FR-3 3. Tighten, and check [research: RF-n] too
Answer: 1. Tighten the check: keep FR-3 as written. The check reads research.md and rejects `[derived: RF-9]` when RF-9 isn't there. A missing research.md means every RF is undefined. That treats RF-n the same as FR-99, and the change is a few lines in spec.py plus one test. [human]
Patched: src/nio/spec.py (check_tags reads research.md), tests/test_spec.py; retired OP-3

## Q3 · FR-14 · 2026-10-25
Question: What severity should a deferred point that isn't a contradiction get as a jury finding?
Options: 1. Major (recommended) 2. Blocker, like contradictions 3. Grill picks per point
Answer: 1. Major: keep the code as it is. A deferred point is a real hole the implementer would otherwise guess at, so it outranks minor. Only a contradiction, where two settled points disagree, is a blocker. That gives a two-step order: contradictions first, then gaps. [human]
Patched: FR-14 [human]; severity table row "no" [derived: FR-14]

## Q4 · FR-15 · 2026-10-25
Question: A finding is added once per DF and never again. What should happen when a grill session closes one as a spec fix but leaves the DF in `## Deferred`?
Options: 1. Dedupe + refuse a hollow spec-fix (recommended) 2. Dedupe only, as coded 3. Dedupe + collect reopens it
Answer: 1. Dedupe + refuse a hollow spec-fix: keep one finding per DF. Also, `dispose` refuses a spec fix on a deferred finding while that DF is still in `## Deferred`. The check happens when the fix is recorded, so it fails immediately. That's one new FR and AC and a couple of lines in dispose. [human]
Patched: FR-15 [human]; new FR-20, AC-22; closing table row "grill"; src/nio/jury.py dispose; tests/test_jury.py; skills/jury/SKILL.md

## Q5 · Non-goals · 2026-10-25
Question: Should a banned synonym catch its inflected forms (plurals, other endings)?
Options: 1. Keep it a non-goal (recommended) 2. Allow a trailing s/es 3. Prefix match
Answer: 1. Keep it a non-goal: exact whole word only. If a form matters, the glossary bans it explicitly (Never "reimbursement" or "reimbursements"). No dependency, nothing to guess, and the jury's consistency lens still reads the prose. [human]
Patched: Non-goals (inflected forms) [human]

## Calls · below the bar · 2026-10-25
Each was a [default] that changes nothing you'd notice (error wording, which story an AC sits under, a
consequence of an answer already given); taken as written. The gate notes list them for the human.
- UJ-1: [agent]
- UJ-2: [agent]
- US-1: [agent]
- AC-5: [agent]
- AC-6: [agent]
- AC-7: [agent]
- US-2: [agent]
- AC-9: [agent]
- AC-10: [agent]
- AC-11: [agent]
- AC-12: [agent]
- US-3: [agent]
- AC-15: [derived: FR-15]
- US-4: [agent]
- AC-20: [derived: FR-18, FR-19]
- AC-21: [derived: FR-19]
- FR-2: [agent]
- FR-4: [agent]
- FR-5: [agent]
- FR-6: [agent]
- FR-9: [agent]
- FR-10: [agent]
- FR-11: [agent]
- FR-19: [agent]
- contradiction, and what is unsettled. [default]: [derived: FR-11]
- - **Deferred finding**: the jury finding made from: [derived: FR-12, FR-16]
- - The grill's own behaviour (asking, deferring, wr: [agent]
- - Checking that a deferred contradiction quotes bo: [agent]
- - Checking that an `[agent]` answer was allowed (n: [agent]
- decision table rows "default item", "deferred item": [derived: FR-4]

## Finish · 2026-10-25
Fidelity: re-read FR-14, FR-15, FR-16, FR-20, AC-22, both closing-table rows, the non-goal and Decisions against Q1-Q5; no drift.
Passivity: the human accepted all 5 recommendations; asked which they would push back on (OP-2 named as weakest): none.
Answer: finish [human]

## Session 2 · 2026-10-25 · jury round 1 (V-261025-wrsv), the human answers

## Q6 · J-3 · 2026-10-25
Question: FR-16 refuses an agent but lets a grill session close a deferred finding, and the grill is an agent (A-2). Who may pass `--by grill`?
Options: 1. --by grill = you answered (recommended) 2. Enforce it via the [human] tag 3. Drop --by grill for deferred
Answer: 1. --by grill = you answered: reword FR-16 and A-2: `--by grill` means a session where you answered the question that settled the point. A delegated session never closes a deferred finding; it settles the point and leaves the finding for you. The rule lives in the spec and in the grill and jury skills, honour system like the rest of `--by`. No code change. [human]
Patched: FR-16, closing table rows grill and agent, Decisions; skills/grill/SKILL.md (Delegated sessions), skills/jury/SKILL.md

## Q7 · J-7 · 2026-10-25
Question: FR-10 and FR-11 (a deferred point's links and format) are agent calls nobody asked for. Keep them?
Options: 1. Keep both, as an extension (recommended) 2. Keep FR-11, drop FR-10 3. Drop both, keep FR-9
Answer: 1. Keep both, as an extension: confirm FR-10 and FR-11 as yours (`[human]`) and log them as a deliberate extension. FR-11 is what guarantees every deferred point becomes a finding. FR-10 stops a point from being both open and deferred. No code change. [human]
Patched: FR-10, FR-11 [human]; Decisions

## Q8 · J-8, J-12 · 2026-10-25
Question: FR-2 counts lines without an ID that carry [agent] or [derived]; nobody asked for it and no AC observes it. Keep it?
Options: 1. Keep the count, add its AC (recommended) 2. List those lines instead 3. Drop the count
Answer: 1. Keep the count, add its AC: confirm the count as yours and add an AC whose Observable is the exact notes text (closes J-12 too). The notes stay one line, and the count tells you there's more to look at than the IDs shown. [human]
Patched: FR-2 [human]; new AC-24

## Session 3 · 2026-10-25 · jury round 2, the human answers

## Q9 · J-22 · 2026-10-25
Question: Five checks (FR-4, FR-5, FR-6, FR-9, FR-19) are agent calls nobody asked for. Keep them?
Options: 1. Confirm all five as yours (recommended) 2. Leave them as agent calls 3. Cut FR-6 and FR-19's details
Answer: 1. Confirm all five as yours: retag FR-4, FR-5, FR-6, FR-9 and FR-19 as `[human]`, log them as a deliberate extension (as with FR-10 and FR-11), and close J-22. No code change. [human]
Patched: FR-4, FR-5, FR-6, FR-9, FR-19 [human]; Decisions. Shown with it: FR-16 reworded for J-16 (only `--by agent` is enforced; the Q6 honour rule moved to a non-goal); no objection.

## Session 4 · 2026-10-25 · jury round 3, the human answers

## Q10 · J-33 · 2026-10-25
Question: FR-17 (no approved verdict while a deferred finding is open) is still an agent call. Confirm it?
Options: 1. Confirm FR-17 as yours (recommended) 2. Leave it an agent call 3. Drop FR-17
Answer: 1. Confirm FR-17 as yours: retag FR-17 `[human]` and log it with the other extensions. It's what gives deferred findings any force, and it's already how every open finding behaves. No code change. [human]
Patched: FR-17 [human]; Decisions

## Session 5 · 2026-10-26 · jury round 4, the human answers

## Q11 · Round 4 · 2026-10-25
Question: Round 4 found 3 majors (SC-1 wording, FR-6 AC, J-38 again) and 10 minors, all wording or ACs over existing code. How do we end?
Options: 1. Fix all, then close it yourself (recommended) 2. Fix all, then round 5 3. Close now, findings as risk
Answer: 1. Fix all, then close it yourself: run the refuter on the majors, apply every fix, then the human closes the gate with `--human` and a reason; open an issue on jury convergence. [human]

## Q12 · J-48 · 2026-10-26
Question: FR-16 lets the human close a deferred finding as a spec fix directly (`--by human`). Keep it?
Options: 1. Confirm it as yours (recommended) 2. Drop it 3. Accept J-48 as risk
Answer: 1. Confirm it as yours: keep `--by human` spec fix, log it as a deliberate extension. The code and tests already do this. [human]
Patched: Decisions

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

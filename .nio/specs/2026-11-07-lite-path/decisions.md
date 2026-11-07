# Decisions: 2026-11-07-lite-path

Every design choice of this effort, made by the orchestrator under the human's standing delegation (take the recommended option). Grill = `grill.md`, plan = `plan.md`, research = `research.md`.

| Decision | Options considered | Chosen | Why | Consequence |
| --- | --- | --- | --- | --- |
| Stages lite runs (grill Q1, spec jury J-15) | skip spec jury + plan + plan jury, keep tasks + tasks jury; skip plan only; skip tasks too (generate tasks.md) | skip spec jury, plan, plan jury; keep tasks + tasks jury | implementing claims from `tasks.md` and needs a `nio: approve tasks` commit (RF-9); no change to implement; one human approval | departs from #44's "skip tasks"; FR-1, FR-2; J-15 accepted as risk under delegation |
| Implementation-jury lenses on lite (grill Q2, J-16) | usual lenses (conformance + correctness + risk + consistency); correctness only (#44's proposal); add spec-gate lenses | usual lenses | no code; lenses run in parallel; every lens finds issues only it raises (RF-11) | departs from #44's one-lens default; FR-13 |
| Separate approval of the bugfix spec (grill Q3) | one approval at the tasks gate; separate spec approval; none | one approval at the tasks gate | one human stop instead of two | UJ-1 |
| Declined escalation (grill Q4) | continue on lite, logged; pause; abandon | continue on lite, logged in `grill.md` | the human's call stands and is traceable | FR-11 |
| "Needs a decision" trigger (grill Q5) | fold into FR-8 + grill bar; keep separate; drop | fold | one trigger list; the grill already asks decisions | FR-9, AC-10 retired |
| How "more than one module" is checked (grill Q6, Q10; J-5, J-9) | `nio check tasks` note; count from the diff at the jury; agent only; error with override field | note from `nio check tasks`: direct parent folder of each non-test file | caught before code; a note lets a declined switch go on | FR-8, AC-9, CT-4 |
| Preservation test before and after (grill Q7, Q13; J-10) | own `direct` task the fix depends on; new red check; after only | own `direct` task (card instruction, judged at the tasks jury) | no code; red can't accept a passing test | FR-7, CT-8 |
| Escalation mechanics (grill Q8, Q11; J-1) | rewrite the same spec on the full template; new full spec + abandon lite; new CLI command | rewrite in place; skip lines never count as a gate's pass | same folder, branch, history; the flow re-places it at spec_jury or grilling (RF-13) | FR-10, CT-1, CT-13 |
| Routing criteria, #11 (grill Q9) | spec skill's routing step, four rules; CLI check on risky flags; model router | spec skill, four rules (defect; expected behaviour stated or obvious; one module; no auth/money/data-deletion/migration/pii flag) | no code; escalation catches a wrong call; a CLI check would break bugfix fixtures carrying `money` | FR-12, FR-14, CT-5 |
| Other risk flags on lite (grill Q12, J-8) | allowed with their lenses; all eight force full; only public-api | allowed | #11's rule unchanged | FR-12 |
| Time saving (grill Q13, J-12) | reported measure; repeat runs for a median; pass/fail test | reported measure | one dogfood run can't prove a margin | NFR-2 |
| Lite skip line reason (plan) | `skipped: lite route`; reuse `skipped: not built` | `skipped: lite route` | a reader can tell a route skip from an unbuilt stage | CT-1 |
| Where lite instructions live (plan) | sections in the existing skills; a new `@nio:lite` skill | existing skills (spec routing + "Escalating a bug fix", grill, tasks, implement, drafter card) | lite runs the existing skills; a skill exists only if used | CT-5..CT-8, CT-12, CT-13 |

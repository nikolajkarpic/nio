# Decisions: 2026-11-07-fewer-gate-turns

Every design choice of this effort, made by the orchestrator under the human's standing delegation (take the recommended option). Grill = `grill.md`, plan = `plan.md`, research = `research.md`.

| Decision | Options considered | Chosen | Why | Consequence |
| --- | --- | --- | --- | --- |
| Fold #90 in (intake) | fold in; leave for later | fold in | same file path and template the change touches | FR-10, CT-4 |
| Fold #92 in (RF-4) | fold in; leave | leave | not trivial: touches `merge`'s join rule and `append_fix` | stays open |
| How jurors write their output (grill Q1) | write tool limited by the card's instruction; only where the host limits paths; orchestrator keeps saving | write tool, card's instruction | no host limits paths (RF-3); saves a turn and a copy of each answer per juror | a juror could write elsewhere against its card |
| Output path line in the pack (grill Q2) | allowed; counts as a change; path in the card | allowed | judged content unchanged | NFR-2 allows that one line |
| Front matter names another lens (grill Q3, #90) | file name wins + one line; refuse; only fix the template | file name wins + one line, template `<your card's name>` | no re-emit | a misnamed file files under its name |
| Several-ID dispose (grill Q4) | comma IDs, one or per-ID notes; one shared note; a file | comma IDs, one or per-ID notes | each lens still sees its own note | `--note` repeatable |
| Escalation in the step (grill Q5) | stays separate; step writes its packs; drop it | stays separate | rare, already has `fixcheck --blocker` | the step stops and says to escalate |
| Gates the step serves (grill Q6) | every gate; spec/plan/tasks; implementation only | every gate, evidence its own call | implementation gate costs most (RF-1) | step asks for evidence first there |
| Who starts a re-review's run (grill Q7) | the step; the orchestrator; same run | the step | one call less per re-review | `run:` line in the output |
| Step writes first-review packs (grill Q8) | yes; no; implementation only | yes | without it scenario A only halves (RF-2) | FR-12, beyond #76's step |
| Unplanned lens file (grill Q9, spec jury J-1) | stop and name it; skip with a warning; collect | stop and name it | a stray file would file under a lens that never ran | FR-14 |
| Lines the step prints (grill Q10, J-5) | one-line results + mismatch + check + next; check + next only; everything | one-line results + mismatch + check + next | a dropped finding stays visible; no bodies | FR-5 |
| Repeated step (grill Q11, J-12) | changes nothing; rewrites packs; refuses | changes nothing | safe to call twice | FR-13, `step.json` |
| Bad note count or repeated ID (grill Q12, J-14) | refuse whole; first note for the rest; partial | refuse whole | no note on the wrong finding | FR-8 |
| `rerun` with usable outputs, spec unchanged (grill Q13, J-13) | fix: new run + fix-check packs; accept | fix | final fix check and fix verdicts are `rerun` too | FR-4 |
| Step state (plan) | `packs/step.json` in the run; a ledger field | `step.json` | no ledger schema change | runs stay scratch |
| Consistency/scope triggers (plan) | orchestrator `--add`; step decides | orchestrator `--add` | the skill's own triggers stay where they are | one `nio pack` call stays |

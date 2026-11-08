# Intake

we also need a way for full autunomous implementation after spec is written, so it auto jurys auto fixes, auto plans jury,auto tasks jury, and implementaion and jury

## Source: https://github.com/nikolajkarpic/nio/issues/122

## Want
Once the human has written a spec, an effort can run on its own to the end: spec jury → fix findings → re-jury → plan → plan jury → fix → tasks → tasks jury → fix → implement each epic → epic jury → fix → done. The human approves nothing along the way unless something stops it.

## Already built (flow-state spec, `.nio/specs/2026-10-28-flow-state/spec.md`)
- `state.json` has an `auto` flag. With it on, a gate whose jury approves commits `nio: approve <stage>` itself (FR-18).
- Specs flagged `money`, `data-deletion`, `migration` or `auth` still wait for the human's `--commit` (FR-51).
- Stop list: a gate pauses after 3 jury rounds, or when a round closes none of the last round's findings (FR-39). The effort is suspended at the `budgets.juries` / `budgets.subagents` caps (FR-40), or after the same guard fails 3 times in a row (FR-41). A change that would move it back waits for the human (FR-42).
- A hand-edited auto flag is refused (AC-58).

## Missing
1. **The switch.** Nothing sets the flag. The flow-state spec deferred `nio flow start --auto`, the `nio:auto` label and the history line that records the grant (its Q8).
2. **The driver.** Something has to loop `nio flow next` → run the named skill → `nio flow done` until the effort pauses or is done. That is probably a `skills/auto/SKILL.md` that starts each stage in a fresh subagent where the host can do that.
3. **Auto-fix.** Jury findings go to the human today. In auto mode, refuter-confirmed blockers and majors need a fixer that edits the stage's files and starts the next round. Deferred from flow-state: the jury confirming defaults and turning open points into defaults (its Q2, Q3, Q7).
4. **Notify.** NORTH_STAR says "if the jury approves, the agent proceeds, but the human is always notified." Where and when does that happen?

## Open questions
- Q1 When is auto granted: when the spec is approved, or by a separate command at any stage? Does the spec jury itself run under auto?
- Q2 What can the fixer do on its own, and what still goes to the human (open points, scope cuts, findings that contradict the human's own words)?
- Q3 What do `budgets.*` default to under auto?
- Q4 How does it end: open a PR and stop, or merge?
- Q5 How is the human notified: a report at each gate, one summary at the end, or both?
- Q6 How do long gates fit hosts that push commands to the background (#85)?

Serves NORTH_STAR → "Autonomy is earned through the jury, never assumed" and "I can read why every autonomous decision was allowed."


**Q1 answered:** auto is granted when the spec draft is written (`nio flow start --auto`, or a flag at the end of the spec stage). The spec jury, its fixes and the spec approval then run without the human. Risky flags (FR-51) still stop the run.
**Q2 answered:** the fixer fixes any refuter-confirmed blocker or major, and turns open points into defaults marked `[auto]`. It pauses for the human only when a fix would change or drop a `[human]`-tagged line, or cut scope.
**Q3 answered:** `budgets.juries` defaults to 2 × the number of gates (spec, plan, tasks, plus one per epic), computed once the tasks are known. It can be overridden in config.
**Q4/Q5 answered:** the run opens a PR and stops; it never merges. The PR body is the one report: each gate, what the jury found, what was auto-fixed, and every `[auto]` default it chose.

**Q6 default (not asked):** the driver waits on long gates the way the skills already do on hosts that push commands to the background (#85). It is not a new mechanism.

All open questions are settled. Next: a spec effort for this issue.

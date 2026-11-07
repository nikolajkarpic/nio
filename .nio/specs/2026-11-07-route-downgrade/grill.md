# Grill: 2026-11-07-route-downgrade

Session 1 (2026-11-07): delegated to the agent (orchestrator / claude-code / claude-opus-5-5, delegated by human). Lite spec: only decisions over the bar.

## Lookup · OP-5 · 2026-11-07
Found: RF-1, RF-2. Retired OP-5.

## Asked · Q1 · OP-1 · 2026-11-07
Question: When is the route recorded?
Context: History is created by the first flow write, `nio flow start` or the first `nio flow done` (RF-4); a line's evidence can carry the route (RF-3).
Options: 1. On the effort's first history line, whichever command writes it (recommended): earliest point, closes the repro's window, no new line kind. 2. At the human's spec approval: a lite effort has none, and the window before approval stays open. 3. At the first spec-jury round: a full effort could be downgraded before its first round.
Refs: OP-1 · EB-1 · RF-3, RF-4

## Q1 · OP-1 · 2026-11-07
Question: When is the route recorded?
Options:
1. On the first history line (recommended)
2. At the human's spec approval
3. At the first spec-jury round
Answer: 1. On the effort's first history line, from spec.md's header at that moment. [agent]
Patched: EB-1, AC-2; retired OP-1

## Asked · Q2 · OP-2 · 2026-11-07
Question: How does the human rule on a full → lite change?
Context: Every writing flow command already refuses an effort `kind` doesn't accept (RF-1).
Options: 1. Refuse it like an unsupported route: the flow writes nothing until spec.md says `route: full` again; a smaller fix becomes a new lite effort (recommended). One rule, no new command. 2. Add a ruling command that accepts the downgrade: a new command and a new history kind. 3. Accept it with a warning line: the misuse #114 reports stays possible.
Refs: OP-2 · EB-3 · RF-1

## Q2 · OP-2 · 2026-11-07
Question: How does the human rule on a full → lite change?
Options:
1. Refuse it until the header says full again (recommended)
2. A ruling command that accepts it
3. Accept with a warning
Answer: 1. Refuse it: `nio flow next` names the recorded and the header route, and every writing flow command refuses until spec.md says `route: full` again. [agent]
Patched: EB-2, EB-3, AC-1, AC-3; retired OP-2

## Asked · Q3 · OP-3 · 2026-11-07
Question: What is the route of an effort whose history predates the fix?
Context: Its history holds no recorded route; a spec-jury round still shows it ran full (RF-5).
Options: 1. Keep reading the header, except that a spec-jury round counts as full (recommended): no migration, and a full effort that met its jury is still guarded. 2. Stamp the header's route at the next flow call: a read would write. 3. Refuse every old effort: breaks efforts in flight.
Refs: OP-3 · EB-1, EB-4 · RF-5

## Q3 · OP-3 · 2026-11-07
Question: What is the route of an effort whose history predates the fix?
Options:
1. Header, but a spec-jury round counts as full (recommended)
2. Stamp at the next call
3. Refuse old efforts
Answer: 1. Keep reading the header; a spec-jury round counts as full on any effort, which also covers lite → full escalation (EB-4). [agent]
Patched: EB-4, AC-4; retired OP-3

## Asked · Q4 · OP-4 · 2026-11-07
Question: Should this fix also refuse `route: lite` with a risky flag?
Context: Not asked for in this fix's words; the bug-fix fixture itself is lite with `risk: [money]`.
Options: 1. A separate issue (recommended): keeps this fix to the downgrade and leaves fixtures alone. 2. Here: widens a lite fix into a check-spec rule change. 3. Never: the spec skill already routes risky work full.
Refs: OP-4

## Q4 · OP-4 · 2026-11-07
Question: Should this fix also refuse `route: lite` with a risky flag?
Options:
1. A separate issue (recommended)
2. Here
3. Never
Answer: 1. A separate issue. [agent]
Patched: Decisions; retired OP-4

## Call · UB-1, UB-2, AC-5, AC-6, Decisions · 2026-11-07
Below the bar: each keeps today's behaviour as a regression guard. No to all five: what a user can do, what a user sees, who may do it, what data is kept or changed, what it costs.
Answer: confirmed as drafted. [agent]

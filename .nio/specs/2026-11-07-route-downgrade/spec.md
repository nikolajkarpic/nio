---
slug: 2026-11-07-route-downgrade
route: lite
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5]
---
<!-- Bugfix spec (Kiro's three sections). Unchanged behaviour is never empty: it is the regression guard.
Each EB-n has an AC that is the test written first (it fails before the fix); each UB-n has a regression AC. -->
# Route downgrade: a full effort silently becomes lite when spec.md's header says `route: lite`

## Summary
`flow.skips` reads the route from the spec header on every call, so rewriting a full effort's spec.md to `route: lite`
silently downgrades it: the spec jury, plan and plan jury are reported as skipped, and in auto mode on a spec without a
risky flag the agent can approve the tasks gate, so no human ever sees the downgrade. [human] Nothing records the route
the human agreed to; lite → full escalation is handled, the reverse is not. Found reviewing #44/#112, filed as #114, and
fixed as a second lite effort on the same branch. [human]
Repro: build a full effort waiting on its spec jury with no approval (`test_flow.effort("spec_jury")`: `nio flow next`
says `state: spec_jury`), write the bug-fix fixture with `route: lite` over its spec.md, run `nio flow next` again: it
says `state: tasking` and `skipped: spec_jury, planning, plan_jury (lite route)`.

## Current behaviour
- **CB-1** WHEN a full effort's spec.md header is rewritten to `route: lite` before its spec gate is approved THEN the system reports the effort at `tasking`, with spec_jury, planning and plan_jury skipped as `lite route`. [human]
- **CB-2** WHEN `nio flow done` moves such an effort THEN the system records those stages as `skipped: lite route`, and in auto mode on a spec without a risky flag the agent can approve the tasks gate with no human seeing the downgrade. [human]

## Expected behaviour
- **EB-1** WHEN an effort's first history line is written (by `nio flow start` or its first `nio flow done`) THE SYSTEM SHALL record spec.md's route on that line. [human]
- **EB-2** WHILE an effort's recorded route is full, or its spec jury has a round, THE SYSTEM SHALL NOT skip spec_jury, planning or plan_jury as `lite route`, whatever spec.md's header says. [human]
- **EB-3** IF spec.md's header names `route: lite` on an effort whose recorded route is full, or whose spec jury has a round, THEN THE SYSTEM SHALL refuse it: `nio flow next` names the recorded and the header route, and every writing `nio flow` command refuses and records nothing until the header says `route: full` again. [human]
- **EB-4** WHEN a lite effort escalated to `route: full` has a spec-jury round THE SYSTEM SHALL treat its route as full, so a later change back to lite is refused as in EB-3. [agent]

## Unchanged behaviour
- **UB-1** WHEN a lite effort's spec.md header is rewritten to `route: full` THE SYSTEM SHALL CONTINUE TO run spec_jury, planning and plan_jury, with no ruling from the human. [human]
- **UB-2** WHEN an effort's header names the same route as its recorded route THE SYSTEM SHALL CONTINUE TO skip exactly what it skips today: on lite spec_jury, planning and plan_jury as `lite route`, on full only the stages not built. [agent]

## Acceptance criteria
- **AC-1** (EB-2) Given a full effort waiting on its spec jury with no approval, its route recorded by `nio flow start`, when spec.md is overwritten with the bug-fix fixture (`route: lite`) and `nio flow next` runs, then no stage is reported skipped as `lite route` and the effort is not at tasking. [human]
  Observable: `nio flow next` prints no `(lite route)` skipped line and no `state: tasking`. Level: integration. (written first; fails before the fix)
- **AC-2** (EB-1) Given a full effort with no history, when `nio flow start` runs, then its first history line records the route `full`. [agent]
  Observable: the first history.jsonl line's evidence carries `route: full`. Level: integration. (written first; fails before the fix)
- **AC-3** (EB-3) Given the downgraded effort of AC-1, when `nio flow next` runs, then it names the recorded route full and the header route lite; when `nio flow done` runs for its stage, then it refuses and history.jsonl gains no line. [human]
  Observable: `nio flow next`'s output holds both routes; `nio flow done` raises or exits non-zero and history.jsonl is unchanged. Level: integration. (written first; fails before the fix)
- **AC-4** (EB-4) Given a lite effort escalated to `route: full` whose spec jury has a round, when the header is rewritten back to `route: lite` and `nio flow next` runs, then it reports the refusal of AC-3. [agent]
  Observable: `nio flow next`'s output names both routes and no `(lite route)` skipped line. Level: integration. (written first; fails before the fix)
- **AC-5** (UB-1) Given a lite effort with its route recorded, when its spec.md is overwritten with the full refunds fixture (`route: full`) and `nio flow next` runs, then no stage is reported skipped as `lite route` and no route-change stop is reported. [human]
  Observable: `nio flow next` prints no `(lite route)` skipped line and no stop. Level: integration.
- **AC-6** (UB-2) Given a lite effort whose header still says `route: lite`, when `nio flow next` runs past grilling, then spec_jury, planning and plan_jury are reported skipped as `lite route`; given a full effort whose header still says `route: full`, none are. [agent]
  Observable: the `(lite route)` skipped line lists exactly spec_jury, planning, plan_jury on lite and is absent on full. Level: integration.

## Decisions
- The route is recorded on the effort's first history line; a spec-jury round also counts as full; a full → lite header is refused like an unsupported route until it says full again (grill Q1-Q3, [agent], RF-1, RF-3 to RF-5).
- Refusing `route: lite` with a risky flag is a separate issue (grill Q4, [agent]).
- Lite skips exactly spec_jury, planning and plan_jury (D-261107-7egd); UB-2 keeps that.
- Escalation rewrites the spec on the full route and needs no ruling (D-261107-xzn3); UB-1 and EB-4 keep that.

## Open points

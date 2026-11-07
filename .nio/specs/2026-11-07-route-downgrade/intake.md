#114 on the same branch, as a second lite effort. Problem: `flow.skips` reads the route from the spec header, so rewriting spec.md to `route: lite` silently downgrades a full effort. Fix: record the route when the effort starts or at the human's spec approval, refuse a change from full to lite after that, and keep lite → full escalation working.

Turn the repros into tests that fail before the fix.

## Source: https://github.com/nikolajkarpic/nio/issues/114

## Problem
With #112, `flow.skips()` reads the route from the spec header on every call. Nothing records the route the human agreed to (FR-14), and nothing notices when it changes. An agent can change a full effort's `spec.md` to the bug-fix shape with `route: lite` at any point, for example after a rejecting spec jury. The effort then moves straight to `tasking`, and the spec jury, plan and plan jury are reported as `skipped: lite route`. In auto mode on a spec without a risky flag, the agent can also approve the tasks gate, so no human ever sees the downgrade. #44's own UJ-1 lists this misuse ("routes a risky or multi-module change as lite to skip review"), but the code has nothing against it. Escalation (lite → full) is handled. The reverse is not.

## Repro (branch `nio/2026-11-07-lite-path` at df1f46e)
`/tmp/claude-1000/-home-work-nio/d6f51638-95d3-4d54-b8ed-fbf62d4bc994/scratchpad/rvrepro/downgrade.py <checkout>`:
- `test_flow.effort("spec_jury")`: a full effort waiting on its spec jury, with no approval → `state: spec_jury`.
- Write the bug-fix fixture with `route: lite` over its spec.md → `state: tasking`, `skipped: spec_jury, planning, plan_jury (lite route)`.

## Proposal
Make the route a recorded fact rather than a header the agent can edit:
- record it in history at the first `done drafting` (or at intake);
- `skips()` uses the recorded route, and a header that disagrees is a stop the human must rule on;
- lite → full needs no ruling, since it adds gates;
- full → lite is refused once a spec-jury round exists.
Also consider refusing `route: lite` together with a risky `risk:` flag (auth, money, migration, data-deletion), since the spec-gate security and adversary lenses never run on lite.

Refs: #44, #112, #11


---
slug: 2026-11-07-route-downgrade
retired: []                      # task IDs removed from this file; never reused
---
# Tasks: Route downgrade: a full effort silently becomes lite when spec.md's header says `route: lite`

## E-1 Record the route an effort starts on and refuse a full → lite downgrade
Files: `src/nio/flow.py`, `tests/test_flow.py`

### T-1 Pin that a lite effort escalated to full runs its spec jury, planning and plan jury with no stop
- Files: `tests/test_flow.py`
- Serves: AC-5
- Test: a lite effort with its route recorded (history started by `nio flow start`), its spec.md then overwritten with the full refunds fixture (`route: full`): `nio flow next` prints no `(lite route)` skipped line and no line containing `route changed`, and `nio flow park` on it then succeeds and appends a history line; green before the fix and after
- Depends on: none
- Parallel: no
- Tier: cheap: a regression test following the existing lite-route and escalation tests in test_flow.py
- Effort: low
- Mode: direct: a regression test of today's behaviour, green before the fix, no code change

### T-2 Pin that an effort whose header matches its route skips exactly what it skips today
- Files: `tests/test_flow.py`
- Serves: AC-6
- Test: a lite effort whose header still says `route: lite`, run past grilling: `nio flow next`'s `(lite route)` skipped line lists exactly spec_jury, planning, plan_jury; a full effort whose header still says `route: full`: no `(lite route)` skipped line; green before the fix and after
- Depends on: none
- Parallel: no
- Tier: cheap: a regression test following the existing lite-route and escalation tests in test_flow.py
- Effort: low
- Mode: direct: a regression test of today's behaviour, green before the fix, no code change

### T-3 Record spec.md's route on the first history line and refuse a header downgraded to lite on a full effort
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-1, AC-2, AC-3, AC-4
- Test: written first, each failing before the fix: (AC-2) `nio flow start` on a full effort with no history writes a first history.jsonl line whose evidence carries `route: full`; (AC-2) on a full effort with no history, the first `nio flow done` (drafting) writes a first line whose evidence carries `route: full`; (AC-1) a full effort at spec_jury with no approval, its route recorded by `nio flow start`, spec.md overwritten with the bug-fix fixture (`route: lite`): `nio flow next` prints no `(lite route)` skipped line and no `state: tasking`; (AC-3) on that effort `nio flow next` prints a line starting `route changed:` that names the recorded route full and the header route lite, and `nio flow done tasking` and `nio flow start` each raise an error whose text contains `route changed:`, with history.jsonl byte-identical after; (AC-4) a lite effort escalated to `route: full` whose spec-jury ledger has a round, header rewritten back to `route: lite`: `nio flow next` prints the `route changed:` line and no `(lite route)` skipped line; (EB-2, legacy) a lite effort whose history lines carry no route and whose spec jury has no round keeps its `(lite route)` skips (a missing recorded route falls back to the header). Fix: the route goes on the first line's evidence in `record` (so both `start` and `done` carry it); `skips` treats the route as full when the recorded route is full or the spec gate's ledger has a round; `kind` returns `route changed: recorded full, spec.md says lite` for that case, so `refuse` stops every writing command (all go through it) and `next_step` prints it
- Depends on: T-1, T-2
- Parallel: no
- Tier: strong: ordinary flow-state logic across record/start/done/skips/refuse/next_step, pinned by clear failing tests
- Effort: med
- Mode: split: each AC has a test that fails before the fix, so a separate test writer keeps the fix honest

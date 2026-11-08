---
slug: 2026-11-07-lite-path
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: lite path of the NIO flow for small bug fixes

## Acceptance tests

### TC-1 A lite effort runs only the lite stages (AC-1; integration) [agent]
- File: `tests/test_flow.py:test_lite_route_stages` (new)
- Covers: CT-1, CT-2, CT-3
- Setup: a git repo (`repo()` plus user config) with `.nio/specs/<S>/intake.md` and `spec.md` = `tests/fixtures/spec/spec-bugfix.md` with `slug: <S>`; `flow.start`.
- Action: before `done grilling`, with `[default]` left in the spec, `tasks.may_start(root, S)` is `(False, "the bug-fix spec must pass nio check spec --gate first (the grill)")`; `flow.done` drafting, then grilling; then `tasks.new(root, S)` creates `tasks.md`, which is overwritten from `tests/fixtures/tasks/tasks.md` cut to the bug fix's ACs (AC-1, AC-2) so `nio check tasks` passes; `flow.done` tasking; the tasks gate approved with its commit (`approve(root, S, "tasks")`) and `flow.done tasks_jury`.
- Assert: `tasks.new` raised nothing and no spec-jury ledger exists; history's `pass` lines go drafting → researching, grilling → spec_jury, tasking → tasks_jury, tasks_jury → implementing; `skip` lines with reason `skipped: not built` for researching, advocate_walking, arch_grilling and `skipped: lite route` for spec_jury, planning, plan_jury; `done grilling` prints `next: run the nio:tasks skill`; `nio flow next` at each step names no `@nio:plan` and no spec-jury step; `flow.kind` is `effort` and the effort appears in `nio flow status`.

### TC-2 The grill's lite bar (AC-2; unit) [agent]
- File: `tests/test_flow.py:test_lite_skill_texts` (new)
- Covers: CT-6
- Setup: `skills/grill/SKILL.md` as shipped.
- Action: read it.
- Assert: it holds `six-facet coverage`, `zero questions` and `lite` in one paragraph of step 4.

### TC-4 Red refuses a passing test on a lite effort (AC-4; integration) [agent]
- File: `tests/test_implement.py:test_lite_red_refuses_passing_test` (new)
- Covers: CT-2, CT-10
- Setup: `impl()`, then `spec.md` replaced by `tests/fixtures/spec/spec-bugfix.md` with `slug: <S>` (route lite) and committed; T-1 claimed; `tests/test_refund.py` written with a test that passes.
- Action: `nio flow red <S> T-1 --run "<RUN>"`.
- Assert: exit code non-zero, the output says the test passed (no failure to accept), and the last history line is not a `red` line for T-1.

### TC-5 The implementation jury reviews a lite fix (AC-5; integration) [agent]
- File: `tests/test_flow.py:test_lite_epic_gate` (new)
- Covers: CT-2, CT-11
- Setup: TC-1's lite effort brought to implementing (tasks approved and committed), every task of E-1 done (history lines as the existing implementing-guard tests write them) with one commit `T-1: fix` touching a file.
- Action: `jury.plan(root, S, "implementation-E-1")`; `flow.done(root, "implementing", S, by=BY)`; then the gate approved by a real jury round (`approve(root, S, "implementation-E-1")`) and `flow.done(root, "implementation-E-1", S, by=BY)`.
- Assert: the plan lines name `conformance` and `correctness`; the first `done implementing` exits 1 naming E-1's missing `epic` line (no task named as not done) and history gains no `implementing → done` line; after the gate's done, history ends with an `implementing → done` pass.

### TC-6 A new lite spec has the bugfix sections (AC-6; unit) [research: RF-7]
- File: `tests/test_spec.py:test_templates_need_filling` (existing)
- Covers: CT-9
- Setup: an empty repo.
- Action: `spec.new(root, "new-lite", "lite")`.
- Assert: the spec exists and its check names the placeholders; the template file holds `## Current behaviour`, `## Expected behaviour`, `## Unchanged behaviour` and `## Acceptance criteria`.

### TC-7 An empty unchanged section fails the check (AC-7; unit) [research: RF-6]
- File: `tests/test_spec.py:test_lite_unchanged_required` (new)
- Covers: CT-9
- Setup: `tests/fixtures/spec/spec-bugfix.md` copied in; a second copy with `## Unchanged behaviour` emptied; a third with AC-2 removed.
- Action: `spec.check` on each.
- Assert: the first has no errors; the second has `section \`## Unchanged behaviour\` is missing or empty`; the third has `UB-1 has no AC`.

### TC-8 The drafter card cuts unchanged-behaviour tests first (AC-8; unit) [agent]
- File: `tests/test_flow.py:test_lite_skill_texts` (new)
- Covers: CT-7, CT-8, CT-14
- Setup: `src/nio/agents/tasks-drafter.md`, `src/nio/agents/evaluator.md` and `skills/tasks/SKILL.md` as shipped.
- Action: read them.
- Assert: one bullet of the drafter card holds `unchanged-behaviour`, `Mode: direct` and `depends on`; the evaluator card and the tasks skill's step 3 each hold `unchanged-behaviour` and `Mode: direct` in one line; the tasks skill's step 1 holds `nio check spec` and `--gate`.

### TC-9 The folder note (AC-9; unit) [agent]
- File: `tests/test_tasks.py:test_lite_escalate_note` (new)
- Covers: CT-4
- Setup: `repo(route="lite")` whose tasks name `src/a/x.py` and `tests/test_x.py`; a second whose tasks name `src/a/x.py` and `src/a/sub/y.py`; a full-route repo with files in two folders.
- Action: `tasks.check` on each.
- Assert: the first has no `escalate:` note; the second has exactly one note starting `escalate: the fix changes files in 2 folders (src/a, src/a/sub)` and the same errors as without it; the full one has none.

### TC-11 An escalated effort stands at the spec jury or the grill (AC-11; integration) [agent]
- File: `tests/test_flow.py:test_lite_escalation_placement` (new)
- Covers: CT-1, CT-13
- Setup: TC-1's lite effort at tasks_jury, and a second lite effort at grilling (spec passing `--gate`); in each `spec.md` replaced by `tests/fixtures/spec/spec.md` with `slug: <S>`, `route: full`, OP-1 removed and `[default]` made `[human]` (passes `--gate`); a second copy keeping OP-1.
- Action: `nio flow next <S>` on each.
- Assert: the first says `state: spec_jury`, the second `state: grilling`; neither says tasking or implementing; the effort escalated from grilling says `state: spec_jury`. `skills/spec/SKILL.md` holds `## Escalating a bug fix` and `keeps its tag`.

### TC-12 A declined switch goes on (AC-12; unit) [agent]
- File: `tests/test_flow.py:test_lite_skill_texts` (new)
- Covers: CT-13
- Setup: `skills/spec/SKILL.md` as shipped.
- Action: read its `## Escalating a bug fix` section.
- Assert: it holds `continue on lite` and `grill.md`.

### TC-13 Lite only when all four hold (AC-13; unit) [agent]
- File: `tests/test_flow.py:test_lite_skill_texts` (new)
- Covers: CT-5
- Setup: `skills/spec/SKILL.md` as shipped.
- Action: read step 1.
- Assert: it names all four criteria (`defect`, `stated or obvious`, `one module`, `risk flag`) and `all four`.

### TC-14 Full when any fails (AC-14; unit) [agent]
- File: `tests/test_flow.py:test_lite_skill_texts` (new)
- Covers: CT-5
- Setup: as TC-13.
- Action: read step 1.
- Assert: one line of step 1 holds `auth`, `money`, `data-deletion`, `migration`, `pii` and `full`.

### TC-15 The route in one line (AC-15; unit) [agent]
- File: `tests/test_flow.py:test_lite_skill_texts` (new)
- Covers: CT-5
- Setup: as TC-13.
- Action: read step 1.
- Assert: one bullet of step 1 holds `one line`, `by what it means` and `can change`, wording CT-5 adds.

### TC-16 Every stage names the triggers (AC-16; unit) [agent]
- File: `tests/test_flow.py:test_lite_skill_texts` (new)
- Covers: CT-6, CT-7, CT-8, CT-12
- Setup: the grill, tasks and implement skills and the tasks drafter card as shipped.
- Action: read each.
- Assert: each names `new dependency`, `outside the bug's folder`, `stored data` and `Escalating a bug fix` (the card: the first three).

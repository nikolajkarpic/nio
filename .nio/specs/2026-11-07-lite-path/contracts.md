---
slug: 2026-11-07-lite-path
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: lite path of the NIO flow for small bug fixes

## Contracts

### CT-1 Stages a route skips (FR-1, FR-2, FR-10) [agent]
- Binding: `src/nio/flow.py:skips` (new)
- Like: `src/nio/flow.py:moves`
- Kind: function
- Shape: `skips(root, slug) -> set[str]`; `ROUTE_SKIPS = {"lite": {"spec_jury", "planning", "plan_jury"}}`. `where`, `guard`, `moves` and `done` use `skips(root, slug)` wherever they use `NOT_BUILT` today; `moves(stage, off)` takes the set. A skip line's `reason` is `skipped: not built` for a `NOT_BUILT` stage and `skipped: lite route` for a route's own; `done` prints `skipped <stage> (not built)` or `skipped <stage> (lite route)`; `next` prints `skipped: <stages> (not built)` for the not-built stages as today and, on its own line, `skipped: <stages> (lite route)` for the route's.
- Accepts: a dated effort folder; its spec's `route` read from the front matter (none or unreadable → no route skips).
- Returns: `NOT_BUILT`, plus `ROUTE_SKIPS[route]` when the spec's route has an entry.
- Rules: "skip research fan-out, the user advocate walk, the spec jury, the architecture grill, the plan and the plan jury, each recorded as skipped" (FR-2). `where` never counts a skip line as a gate's pass: a gate stage outside `skips` is cleared only by its approval commit or override, as today, so a spec rewritten as `route: full` stands at spec_jury when `nio check spec --gate` passes and at grilling when it doesn't (FR-10). In `where`'s look-ahead for the next gate, a skipped gate doesn't count.
- State: follows the spec's state table "Lite effort"

### CT-2 The flow drives lite efforts (FR-15) [agent]
- Binding: `src/nio/flow.py:kind` (existing)
- Kind: function
- Shape: `kind(root, slug)` returns `effort` for `route: full` and `route: lite`; `unsupported: epic` stays for an epic. `next_step` on an unsupported folder prints `unsupported: <route>: nio flow drives full and lite specs only`.
- Rules: "let `nio flow` drive it like a full effort (status, next, done, claim); an epic spec stays unsupported" (FR-15).

### CT-3 The tasks stage starts on a settled bug-fix spec (FR-1) [agent]
- Binding: `src/nio/tasks.py:may_start` (existing)
- Kind: function
- Shape: on `route: lite`, `may_start` returns `(True, ...)` when `spec.check(root, slug, gate=True)` has no errors, else `(False, "the bug-fix spec must pass nio check spec --gate first (the grill)")`; the spec jury is not consulted. Full and epic specs are unchanged.
- Rules: "skip ... the spec jury" (FR-2).

### CT-4 The folder escalation note (FR-8) [agent]
- Binding: `src/nio/tasks.py:check` (existing)
- Kind: function
- Shape: on `route: lite`, when the non-test files named by every task's `Files:` line (`files` then `file_of`) have more than one direct parent folder, `check` appends to its notes `escalate: the fix changes files in <n> folders (<a>, <b>, ...): offer the full flow (@nio:spec, "Escalating a bug fix")`, folders sorted, the repository root written `.`. Errors and exit code are unchanged by it.
- Accepts: a test file is a path with a `tests` or `test` folder in it, or whose name starts with `test_`; it is left out of the count.
- Rules: "the folder trigger is a note from `nio check tasks`, the others are judged by the agent from the skills" (FR-8). A full spec never gets the note.

### CT-5 The spec skill routes (FR-12, FR-14) [agent]
- Binding: `skills/spec/SKILL.md` (existing)
- Kind: file
- Shape: step 1 routes `lite` only when all four hold: a defect (current versus expected behaviour, or an issue labelled bug); the expected behaviour is stated or obvious; the likely scope is one module (a quick `nio query --path` or grep on the symptom); no risk flag from auth, money, data-deletion, migration or pii. Otherwise `full` (or `epic` as today); external-input, multi-party and public-api may stay lite. The route is told in one line by what it means, saying the human can change it.
- Rules: "propose lite only when the intake is a defect, the expected behaviour is stated or obvious, the likely scope is one module and no risk flag from auth, money, data-deletion, migration or PII applies, and full otherwise" (FR-12).

### CT-13 The spec skill escalates (FR-8, FR-10, FR-11) [agent]
- Binding: `skills/spec/SKILL.md` (existing)
- Kind: file
- Shape: a new section `## Escalating a bug fix` lists FR-8's triggers and says: stop and offer the full flow, saying what each choice costs; on yes, rewrite the same `spec.md` on the full template with `route: full`, each current, expected and unchanged item becoming an FR with its AC and keeping its tag, run `nio check spec <slug>`, then `nio flow next <slug>` (it stands at spec_jury, or grilling if anything is open); on no, continue on lite and log `## Call · escalation declined` in `grill.md` naming the trigger it overrides. Step 1's closing fallback reads `(no \`nio\`)`.
- Rules: "continue the effort on lite and log the human's call" (FR-11).

### CT-6 The grill on a lite spec (FR-3, FR-8) [agent]
- Binding: `skills/grill/SKILL.md` (existing)
- Kind: file
- Shape: step 4 says that on a lite spec the six-facet coverage is skipped and only open points of kind decision and `[default]` items over the bar are asked, so a spec with neither gets zero questions; an answer that would hit an FR-8 trigger stops the grill and offers the full flow (@nio:spec, "Escalating a bug fix"). The closing line's fallback names the tasks stage for a bug fix.
- Rules: "ask the human only about open points that need a human decision" (FR-3).

### CT-7 The tasks stage stops on a trigger (FR-8) [agent]
- Binding: `skills/tasks/SKILL.md` (existing)
- Kind: file
- Shape: the tasks skill's description, Inputs and step 1 say a bug fix's tasks stage starts once `nio check spec <slug> --gate` passes (no spec jury), a full spec's after its plan as today. Step 3 says that on a bug fix, a task serving only unchanged-behaviour ACs keeps `Mode: direct`. Step 4 stops on an `escalate:` note, unless `grill.md` already holds a `## Call · escalation declined` naming that trigger, and on the drafter stopping over a new dependency, an interface used outside the bug's folder or stored data, and offers the full flow (@nio:spec, "Escalating a bug fix"). The closing fallback reads `(no \`nio\`)`.
- Rules: "stop the effort and offer the full flow" (FR-8).

### CT-8 The tasks drafter cuts a bug fix (FR-7, FR-8) [agent]
- Binding: `src/nio/agents/tasks-drafter.md` (existing)
- Kind: file
- Shape: on a bug-fix spec, each unchanged-behaviour AC's test is its own task, which the evaluator rates `Mode: direct` (its card says so, CT-14), and the expected-behaviour task depends on it, so its green runs on the code before the fix and the epic's suite after it; a fix needing a new dependency, a change to an interface used outside the bug's folder or to stored data stops the drafter, as a design choice does.
- Rules: "have it put each unchanged-behaviour test in its own `direct` task that the fix's task depends on" (FR-7).

### CT-9 The bugfix spec and its check, reused (FR-4, FR-5) [research: RF-6]
- Binding: `src/nio/spec.py:check` (existing)
- Kind: function
- Shape: `nio new spec <name> --route lite` writes `templates/spec-bugfix.md`; `check` requires its five sections and an AC per EB and UB item. Unchanged.

### CT-10 Red, reused (FR-6) [research: RF-5]
- Binding: `src/nio/implement.py:red` (existing)
- Kind: function
- Shape: `nio flow red <slug> T-n --run <command>` accepts only a test that fails for the right reason; on a lite effort it runs unchanged.

### CT-11 The implementation gate's lens plan, reused (FR-13) [research: RF-10]
- Binding: `src/nio/jury.py:plan` (existing)
- Kind: function
- Shape: `nio jury plan <slug> implementation-E-n` plans conformance and correctness, plus risk-flag lenses and consistency; on a lite effort it runs unchanged.

### CT-12 The implement stage stops on a trigger (FR-8) [agent]
- Binding: `skills/implement/SKILL.md` (existing)
- Kind: file
- Shape: the blocked-handoff step says that on a bug fix, a handoff naming a new dependency, an interface used outside the bug's folder or stored data, or a fix task whose files sit in a second folder, offers the full flow (@nio:spec, "Escalating a bug fix") alongside the change request.
- Rules: "stop the effort and offer the full flow" (FR-8).

### CT-14 The evaluator keeps preservation tasks direct (FR-7) [agent]
- Binding: `src/nio/agents/evaluator.md` (existing)
- Kind: file
- Shape: on a bug-fix spec, a task serving only unchanged-behaviour ACs gets `Mode: direct` (red can't accept a test that passes before the fix).
- Rules: "have it put each unchanged-behaviour test in its own `direct` task that the fix's task depends on" (FR-7).

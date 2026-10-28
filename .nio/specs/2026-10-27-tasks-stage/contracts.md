---
slug: 2026-10-27-tasks-stage
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: the tasks stage

## Contracts

### CT-1 The tasks skill (FR-1, FR-2, FR-4, FR-5, FR-18, FR-19, FR-20, FR-21, FR-27, FR-29, FR-32, FR-39, FR-44, FR-51, FR-54) [default]
- Binding: `skills/tasks/SKILL.md` (new)
- Like: `skills/plan/SKILL.md`
- Kind: file
- Shape: `@nio:tasks` steps: check inputs (`nio jury check <slug> spec`, and `nio check plan <slug> --approved` on a full spec), `nio new tasks <slug>`, run the tasks drafter, run the evaluator, `nio check tasks <slug>` until it passes, show the estimate, hand off to the tasks jury; later tasks go under `#### Fixes`; one `nio: approve tasks` commit when the human approves
- Rules: "a gate handed to the human but not closed by them does not count" (FR-2); "IF `nio check tasks` fails THEN THE SYSTEM SHALL not start the tasks jury" (FR-32); a design choice nothing settles stops the drafter (FR-54)

### CT-2 The tasks template (FR-3, FR-6, FR-7, FR-15, FR-23) [default]
- Binding: `src/nio/templates/tasks.md` (new)
- Like: `src/nio/templates/plan.md`
- Kind: file
- Shape: frontmatter `slug`, `retired: []`; `## E-n <title> (US-n | Foundation)` sections, each with `### T-n <title>` tasks holding seven lines (`- Files:`, `- Serves:`, `- Test:`, `- Depends on:`, `- Parallel:`, `- Tier:`, `- Effort:`), then an optional `#### Fixes` heading
- Rules: "`Tier: <cheap|strong|max|frontier>: <reason>`" and "`Effort: <low|med|high>`" (FR-15); "no status or checkbox in `tasks.md`" (FR-23)

### CT-3 Create tasks.md (FR-2, FR-39) [default]
- Binding: `src/nio/tasks.py:new` (new)
- Like: `src/nio/plan.py:new`
- Kind: cli
- Shape: `nio new tasks <slug>` → prints `.nio/specs/<slug>/tasks.md`
- Accepts: the slug of a spec whose spec gate is approved or closed by the human, and, on a full spec, whose `nio check plan <slug> --approved` exits 0
- Fails: spec not approved → exit 1, "the spec must be approved first"; full spec with no approved plan → exit 1, "the plan must be approved first"; epic-route spec → exit 1, "run the tasks stage on each slice's spec"; `tasks.md` exists → exit 1, never overwritten

### CT-4 Check tasks.md (FR-8, FR-9, FR-10, FR-11, FR-12, FR-13, FR-16, FR-24, FR-34, FR-36, FR-37, FR-38, FR-40, FR-45, FR-48, FR-53, FR-55, NFR-1) [default]
- Binding: `src/nio/tasks.py:check` (new)
- Like: `src/nio/plan.py:check`
- Kind: cli
- Shape: `nio check tasks <slug>` → one `ERROR <message>` per error, then the estimate (CT-5), then `<n> errors`; exit 1 on any error
- Accepts: `tasks.md`, the spec, and on a full spec the plan's `plan.md`, `contracts.md` and `tests.md`
- Fails: each rule below names the task, epic, ID, line or file at fault, as the spec's ACs state
- Rules: missing line (FR-8); unknown or retired ID (FR-9, FR-40); duplicate ID (FR-38); AC served by no task, task serving no AC (FR-10, FR-11); "naming every task in the cycle" (FR-12); parallel clash across the spec (FR-13, FR-48); bad `Tier:` or `Effort:` (FR-16); checkbox or status line (FR-24); foundational task citing an AC no dependent serves (FR-45); a build-order entry's file or `TC-n` missing from its epic (FR-53); full spec `Test:` cites a `TC-n` (FR-55); `Depends on: none` and `Parallel: yes|no` (FR-36, FR-37); "no file-count or AC-count limit" (FR-34); "zero model calls" (NFR-1)

### CT-5 The estimate (FR-14, FR-47, NFR-1) [default]
- Binding: `src/nio/tasks.py:estimate` (new)
- Like: `src/nio/plan.py:check_coverage`
- Kind: function
- Shape: `estimate(tasks) -> list[str]`, one row per epic: `E-n: <n> tasks; tier cheap <n>, strong <n>, max <n>, frontier <n>; effort low <n>, med <n>, high <n>; parallel: T-a, T-b`
- Rules: "with no token or money figure" (FR-14); parallel "only from its `Parallel:` and `Depends on:` lines, never from its tier or effort" (FR-47)

### CT-6 Show one task (FR-35) [default]
- Binding: `src/nio/tasks.py:show` (new)
- Like: `src/nio/plan.py:field`
- Kind: cli
- Shape: `nio task show <slug> T-n` → the epic's heading line, then the task's section
- Fails: no such task → exit 1, "no T-n in tasks.md"
- Rules: "no other task, with zero model calls" (FR-35)

### CT-7 Model tiers with frontier and nearest-lower fallback (FR-17, FR-52) [default]
- Binding: `src/nio/agents.py:resolve` (existing)
- Kind: function
- Shape: `TIERS = {"cheap", "strong", "max", "frontier"}`; `DEFAULT_TIERS["claude"]["frontier"] = "fable"`; `resolve(cfg, name, meta, host) -> (tier, model or None, effort, warning)` falls back to the nearest lower mapped tier and names it in `warning`; `sync` prints that warning in place of its inherit message and `verify` compares against the same model; a task's worker calls it with `name=None` (no card override) and the task's `Tier:` and `Effort:` as `meta`
- Rules: "frontier to max, max to strong, strong to cheap" (FR-52); warn-and-inherit stays "only when no lower tier is mapped either" (FR-52)

### CT-8 Tasks-drafter card (FR-1, FR-4, FR-5, FR-19, FR-20, FR-21, FR-51, FR-54, FR-55) [default]
- Binding: `src/nio/agents/tasks-drafter.md` (new)
- Like: `src/nio/agents/spec-drafter.md`
- Kind: file
- Shape: card, `tier: strong`, `effort: high`, tools read and edit; writes `tasks.md` from the approved plan (full spec) or the spec and the code (bug fix), one epic per build-order entry, `Test: TC-n` on a full spec, and stops on an unsettled design choice

### CT-9 Evaluator card (FR-18, FR-43) [derived: FR-43]
- Binding: `src/nio/agents/evaluator.md` (new)
- Like: `src/nio/agents/spec-drafter.md`
- Kind: file
- Shape: card, `tier: strong`, `effort: med`; rates each task's `Tier:` with a one-line reason and its `Effort:`

### CT-10 Executability lens card (FR-41) [derived: FR-41]
- Binding: `src/nio/agents/executability.md` (new)
- Like: `src/nio/agents/logic.md`
- Kind: file
- Shape: card, `tier: cheap`, `tools: [read]`, an `## At tasks` section asking "whether each task can be carried out as written by one worker from its pack" (FR-41)

### CT-11 Plan the tasks gate (FR-32, FR-42) [default]
- Binding: `src/nio/jury.py:plan` (existing)
- Kind: cli
- Shape: `CORE["tasks"] = ["executability"]`; the tasks gate gets its own branch in `jury.plan`: it runs `tasks.check` as its precondition and adds no risk or scope lens; `nio jury plan <slug> tasks` → `lenses: executability (core)`
- Fails: `nio check tasks <slug>` has errors → exit 1, "`nio check tasks <slug>` fails (`<n>` errors): fix the tasks first", no lens line

### CT-12 The tasks gate's artefact (FR-56) [research: RF-9]
- Binding: `src/nio/jury.py:artefact` (existing)
- Kind: config
- Shape: `GATES["tasks"] = ["tasks.md", "plan.md", "contracts.md", "tests.md", "quickstart.md", "spec.md"]`; `jury.artefact` leaves out each epic's `#### Fixes` section of `tasks.md`, so the approval covers the planned tasks, the plan and the spec
- Rules: a spec or plan change after approval makes `nio jury check <slug> tasks` say `rerun` (FR-56); a fix task appended under `#### Fixes` doesn't, since new work goes there without a new approval (FR-27, FR-50)

### CT-13 Each epic's implementation-jury ledger (FR-31) [research: RF-9]
- Binding: `src/nio/jury.py:verdict` (existing)
- Kind: file
- Shape: `jury.load`, `save` and `verdict` already name the ledger `jury/<gate>.json` and `.md` and the subject `<gate>:<slug>` from the gate's name, so an `implementation-E-n` gate gets FR-31's path with no change here
- Rules: collecting rounds for an `implementation-E-n` gate, and what its artefact is (the epic's diff), belong to the implementation jury (#29, spec 2026-10-27-implementation-jury)

### CT-14 May the implement stage start (FR-33, FR-44, FR-56) [default]
- Binding: `src/nio/tasks.py:approved` (new)
- Like: `src/nio/plan.py:approved`
- Kind: cli
- Shape: `approved(root, slug) -> (bool, reason)`; CLI `nio check tasks <slug> --approved`
- Returns: exit 0 when the tasks gate is approved or closed by the human on the current planned tasks, plan and spec (CT-12); a fix task appended since doesn't withdraw it
- Fails: otherwise exit 1, "the tasks must be approved first (`<why>`)"
- Rules: the implement stage (#43) calls this before it claims a task

### CT-15 Finished task and finished epic (FR-25, FR-26) [default]
- Binding: `src/nio/tasks.py:finished` (new)
- Like: `src/nio/plan.py:approved`
- Kind: function
- Shape: `finished(states, epic) -> (bool, not_done)`, where `states` maps each `T-n` to its state in the CLI's state (#45)
- Rules: a task counts only at `done` (FR-25); an epic is finished "only when every task in it, fix tasks included, is `done`" (FR-26); #45 supplies `states` and enforces the transitions

### CT-16 Fix-task rules in `nio check tasks` (FR-27, FR-28, FR-29, FR-30, FR-49, FR-50) [default]
- Binding: `src/nio/tasks.py:check_fixes` (new)
- Like: `src/nio/plan.py:check_build`
- Kind: function
- Shape: `check_fixes(root, slug, epics, base) -> list[str]`, called by `check` (CT-4)
- Rules: a task under `#### Fixes` needs a `From:` line (FR-28) and takes "the next free `T-n` (one above the highest ID ever used, live or retired)" (FR-27); "a jury finding ID (`J-n`) in `Serves:` only for a task under `#### Fixes` whose `From:` names that finding" (FR-49); fix tasks get every other check too (FR-30); after `nio: approve tasks`, a planned task whose text changed fails, naming it, and says "planned tasks are frozen after approval" (FR-29, FR-50)


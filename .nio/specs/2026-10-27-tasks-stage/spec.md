---
slug: 2026-10-27-tasks-stage
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, OP-12, OP-10, OP-11, OP-13, OP-14, OP-15, OP-16, OP-17, FR-46, AC-47, NFR-2, FR-22, AC-7]  # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-10-27-tasks-stage` checks all of this. -->
# Tasks stage: break an approved spec into epics (one per user story) and tasks in tasks.md, rated by model tier and effort and checked by `nio check tasks`

## Summary
Between an approved spec and the implement stage there is nothing yet that turns the spec into work a single worker
can pick up. This adds the tasks stage (#19, #42): a `@nio:tasks` skill whose drafter writes one `tasks.md` per spec,
one epic per user story plus a foundational epic when shared setup is needed, each task with seven required fields, and
whose evaluator rates each task's model tier and effort. A free `nio check tasks` checks fields, IDs,
coverage both ways, dependency cycles and parallel file clashes, then prints an estimate the human approves before
anything is spent on implementation. It also settles what an epic, a task and "finished" are, and where each epic's
implementation-jury ledger lives (#29 DF-1, DF-2). [human]

## Actors and journeys
- **A-1 Human**: owns the project and its specs; reads the estimate and approves it, or pushes back, before implementation starts. [human]
- **A-2 Tasks drafter**: the agent the `@nio:tasks` skill runs to write `tasks.md` from the approved spec, the code, and, on a full spec, its approved plan. [human]
- **A-3 Evaluator**: the agent that rates each task's model tier and effort after the drafter is done. [human]
- **A-4 Tasks jury**: the jury gate (#28) that reviews `tasks.md`, including task sizes and tier and effort ratings, after the check passes. [human]
- **A-5 Implementation jury**: the gate (#29) that reviews one finished epic at a time and appends fix tasks to it. [human]
- **A-6 Worker**: the implement stage's agent (#43) that works one task from one context pack. [human]

**UJ-1 Break an approved spec into tasks** (A-2, A-3, A-4) [research: RF-1]
1. The human starts the tasks stage on an approved spec.
2. The drafter writes `tasks.md`: a foundational epic if needed, then one epic per user story, each task with its seven fields.
3. The evaluator rates each task's model tier, with a reason, and its effort.
4. `nio check tasks` passes, and the tasks jury reviews the file.
- Misuse: the drafter groups tasks by layer instead of by story, leaves an AC with no task, or adds a task that serves no AC.
- Evidence: issue #42 and its comments; spec-kit's per-story task phases.

**UJ-2 The human approves the estimate** (A-1) [research: RF-2]
1. The human sees, per epic, the task count, how many tasks run on each model tier and effort, and which tasks can run in parallel.
2. The human approves, and the implement stage may start; or pushes back, and it may not.
- Misuse: the implement stage starts before the human has seen the estimate.
- Evidence: NORTH_STAR ("see the estimate before anything is spent"); issue #42 Q11.

**UJ-3 A fix task joins an epic later** (A-5, A-6) [research: RF-3]
1. The implementation jury confirms a finding on an epic, or a change request is rejected.
2. A task with the next free ID is added under the epic's `Fixes` heading, with a `From:` line naming its source.
3. A worker picks it up like any other task.
- Misuse: the planned tasks above the heading are edited or renumbered to absorb the fix.
- Evidence: issue #42 Q9; spec `2026-10-27-implementation-jury` FR-26, FR-27.

## User stories

### US-1 Draft tasks.md from an approved spec (P1) [human]
- **Why this priority:** without the file there are no epics or tasks for anything else to check, estimate or work.
- **Independent test:** run the tasks stage on an approved spec with two user stories and read the `tasks.md` it writes.

- **AC-1** (FR-1, FR-3, FR-4) Given an approved full spec with US-1 and US-2, whose approved plan has a build-order entry for each and no Foundation entry, when the tasks stage runs, then it writes one `tasks.md` with one epic per user story. [human]
  Observable: `.nio/specs/<slug>/tasks.md` exists with exactly two epic sections, `E-1` naming US-1 and `E-2` naming US-2, each with its tasks under it. Level: e2e.
- **AC-2** (FR-5) Given an approved full spec whose approved plan has a Foundation entry that both user stories' entries depend on, when the tasks stage runs, then a foundational epic comes first and both story epics depend on it. [human]
  Observable: the first epic section is the foundational one; every story epic's dependencies reach it. Level: e2e.
- **AC-3** (FR-2) Given a spec that is not approved, when the tasks stage is asked to run on it, then it refuses. [research: RF-11]
  Observable: no `tasks.md` is written; the message says the spec must be approved first. Level: integration.
- **AC-4** (FR-39) Given an epic-route spec (a roadmap of slices with no ACs), when the tasks stage is asked to run on it, then it refuses and points to its slices. [research: RF-15]
  Observable: no `tasks.md` is written; the message says to run the tasks stage on each slice's spec. Level: integration.
- **AC-5** (FR-20, FR-53) Given a full spec whose plan's US-1 entry delivers CT-2 (bound to `src/cart.py`) and lists TC-3, and E-1 for US-1 whose tasks name neither, when `nio check tasks` runs, then it fails. [human]
  Observable: non-zero exit; one error names E-1 and `src/cart.py`, another names E-1 and TC-3. Level: unit.
- **AC-6** (FR-19, FR-21) Given an approved bug-fix spec, which has no `plan.md`, when the tasks stage runs, then every task names its files from the spec and the code. [human]
  Observable: every task has a non-empty `Files:` line. Level: e2e.

### US-2 Every task carries seven fields and permanent IDs (P1) [human]
- **Why this priority:** the coverage, parallel and estimate checks all read these fields; a missing or wrong field breaks them silently.
- **Independent test:** run `nio check tasks` on fixture files, each with one malformed task.

- **AC-8** (FR-7, FR-8) Given T-3 has no `Effort:` line, when `nio check tasks` runs, then it fails. [human]
  Observable: non-zero exit; the error names T-3 and `Effort`. Level: unit.
- **AC-9** (FR-9) Given T-3's `Serves:` cites AC-99, which the spec doesn't define, when the check runs, then it fails. [human]
  Observable: non-zero exit; the error names T-3 and AC-99. Level: unit.
- **AC-10** (FR-9) Given T-5's `Depends on:` cites T-40, which `tasks.md` doesn't define, when the check runs, then it fails. [human]
  Observable: non-zero exit; the error names T-5 and T-40. Level: unit.
- **AC-11** (FR-40) Given T-2 is listed in `retired:` and T-5 depends on T-2, when the check runs, then it fails. [derived: FR-6]
  Observable: non-zero exit; the error names T-2 as retired. Level: unit.
- **AC-12** (FR-6, FR-38) Given two task headings both `T-7` (for example two epics each numbering from T-1), when the check runs, then it fails. [derived: FR-6]
  Observable: non-zero exit; the error names T-7 as defined twice. Level: unit.
- **AC-13** (FR-36, FR-37) Given a task with `Depends on: none` and `Parallel: yes`, and another with `Parallel: maybe`, when the check runs, then only the second is an error. [agent]
  Observable: one error, naming the second task and its `Parallel:` value. Level: unit.
- **AC-14** (FR-15, FR-16) Given one task with `Tier: strong` and no reason and another with `Tier: huge: big change`, when the check runs, then both are errors. [derived: FR-15]
  Observable: two errors, one naming the missing reason, one naming `huge` as not cheap, strong, max or frontier. Level: unit.
- **AC-15** (FR-23, FR-24) Given a task with a `- [ ]` checkbox or a `Status:` line, when the check runs, then it fails. [derived: FR-23]
  Observable: non-zero exit; the error names the task and says status lives in the CLI's state. Level: unit.

### US-3 Coverage, cycles and parallel clashes are checked for free (P1) [human]
- **Why this priority:** these are the stage's stopping conditions; they gate the tasks jury and cost no model calls.
- **Independent test:** run `nio check tasks` on fixture files with an uncovered AC, an orphan task, a cycle and a parallel clash.

- **AC-16** (FR-10) Given the spec defines AC-4 and no task serves it, when the check runs, then it fails. [human]
  Observable: non-zero exit; the error names AC-4 as served by no task. Level: unit.
- **AC-17** (FR-11) Given T-6 has a `Serves:` line that cites no AC, when the check runs, then it fails. [human]
  Observable: non-zero exit; the error names T-6 as serving no AC. Level: unit.
- **AC-18** (FR-12) Given T-2 depends on T-3 and T-3 depends on T-2, when the check runs, then it fails. [human]
  Observable: non-zero exit; the error names T-2 and T-3 as a cycle. Level: unit.
- **AC-19** (FR-12) Given T-1 depends on T-3, T-3 on T-2 and T-2 on T-1, when the check runs, then it fails. [human]
  Observable: non-zero exit; the error names all three tasks in the cycle. Level: unit.
- **AC-20** (FR-13) Given T-4 and T-5 are both `Parallel: yes` and both name `src/a.py`, when the check runs, then it fails. [human]
  Observable: non-zero exit; the error names T-4, T-5 and `src/a.py`. Level: unit.
- **AC-21** (FR-13) Given T-4 is `Parallel: yes`, T-5 is `Parallel: no` and both name `src/a.py`, when the check runs, then there is no clash. [research: RF-6]
  Observable: no error for T-4 or T-5. Level: unit.
- **AC-22** (FR-10, FR-11, FR-12, FR-13) Given a valid `tasks.md`, when the check runs with no network and no model configured, then it passes. [human]
  Observable: exit 0; no model or network call is made (NFR-1). Level: integration.
- **AC-23** (FR-32) Given `nio check tasks` fails for a spec, when the tasks jury is asked to run, then it does not start. [human]
  Observable: no lens runs; the message says the check must pass first. Level: integration.
- **AC-40** (FR-41) Given the shipped agent cards, when they are listed, then `executability` exists with tier cheap and an `## At tasks` section. [human]
  Observable: `src/nio/agents/executability.md` with `tier: cheap` and the heading. Level: unit.
- **AC-41** (FR-42) Given a spec whose `nio check tasks` passes, when `nio jury plan <slug> tasks` runs, then it plans executability as the core lens. [human]
  Observable: the plan lists `executability (core)` and no error about the gate not being built. Level: unit.
- **AC-59** (FR-2) Given a full spec whose spec gate is approved but whose `nio check plan <slug> --approved` exits 1, when the tasks stage starts, then it refuses; given a bug-fix spec whose spec gate is approved, it proceeds. [human]
  Observable: the first exits non-zero saying the plan must be approved first and writes no `tasks.md`; the second starts the drafter. Level: integration.
- **AC-60** (FR-54) Given a bug-fix spec whose fix needs a choice between two storage options the spec doesn't make, when the drafter meets it, then it stops and says the spec must become a full spec with a plan. [human]
  Observable: no `tasks.md` is written; the message names the choice and says to re-route the spec to full. Level: e2e.
- **AC-61** (FR-5) Given a full spec whose plan's build order has Foundation, US-1, and US-2 with `Depends on: US-1`, when the tasks stage runs, then the epics follow that order and E-3 (US-2) depends on E-2 (US-1). [human]
  Observable: epic sections in the order foundational, US-1, US-2; E-3's dependencies name E-2. Level: e2e.
- **AC-62** (FR-55, FR-9) Given a full spec whose task T-4 has `Test: TC-99` and the plan defines no TC-99, when the check runs, then it fails; given a task with `Test: second refund gets 409` on a full spec, it fails too. [human]
  Observable: non-zero exit; one error names T-4 and TC-99, the other names the task and says a full spec's `Test:` cites a `TC-n`. Level: unit.
- **AC-63** (FR-56) Given an approved estimate, when the plan's `contracts.md` or the spec changes afterwards, then the tasks approval no longer stands. [human]
  Observable: the implement stage refuses, saying the tasks must be approved again; `nio jury check <slug> tasks` says `rerun`. Level: integration.
- **AC-42** (FR-2) Given a full spec whose spec jury the human closed with a reason and whose plan is approved, when the tasks stage starts, then it proceeds. [human]
  Observable: no refusal; the drafter is started. Level: integration.
- **AC-43** (FR-2) Given a spec whose jury ended `human` because a juror failed twice, and the human never closed it, when the tasks stage starts, then it refuses. [human]
  Observable: non-zero exit; the message says the spec must be approved first. Level: unit.
- **AC-44** (FR-43) Given the shipped agent cards, when they are listed, then the evaluator card exists with `tier: strong` and `effort: med`. [human]
  Observable: the card's frontmatter holds both values. Level: unit.
- **AC-45** (FR-44) Given the tasks jury passed and the human approves the estimate, when the approval is recorded, then one `nio: approve tasks` commit holds `tasks.md` and the tasks verdict. [human]
  Observable: the latest commit's message is `nio: approve tasks` and it touches `tasks.md` and the tasks gate's verdict record. Level: integration.
- **AC-46** (FR-45) Given foundational task T-1 with `Serves: AC-1, AC-4` and only T-5 (serving AC-1) depending on it, when the check runs, then it fails naming T-1 and AC-4. [human]
  Observable: non-zero exit; the error names T-1 and AC-4. Level: unit.
- **AC-48** (FR-47) Given two tasks marked `Parallel: yes`, one `cheap` and one `max`, with no dependencies and no shared file, when the estimate is printed, then both are listed as parallel. [agent]
  Observable: both IDs appear in the epic's parallel list. Level: unit.
- **AC-49** (FR-48) Given T-2 in E-1 and T-7 in E-2, both `Parallel: yes` and both listing `src/cart.py`, when the check runs, then it fails naming both. [human]
  Observable: non-zero exit; the error names T-2, T-7 and the file. Level: unit.
- **AC-50** (FR-48) Given T-4 `Parallel: yes` with `Depends on: T-1`, when the check runs, then it passes, and T-4 is listed as parallel. [human]
  Observable: exit 0; T-4 in the parallel list. Level: unit.
- **AC-51** (FR-49) Given a "justify or remove" task under `#### Fixes` with `From: J-4 (implementation-E-2, round 1)` and `Serves: J-4`, when the check runs, then it passes; the same `Serves: J-4` on a planned task fails. [human]
  Observable: exit 0 for the first; for the second, an error naming the task and J-4. Level: unit.
- **AC-52** (FR-50) Given an approved estimate and a planned task whose `Files:` line was edited afterwards, when the check runs, then it fails naming the task. [human]
  Observable: non-zero exit; the error names the task and says planned tasks are frozen after approval. Level: unit.
- **AC-53** (FR-50) Given an accepted change request C-1 after approval, when its task is added, then it sits under `#### Fixes` with `From: C-1` and the check passes. [human]
  Observable: exit 0; the new task is under the Fixes heading with that From line. Level: unit.
- **AC-54** (FR-51) Given a bug-fix spec with AC-1 and AC-2, when the tasks are drafted and checked, then `tasks.md` has exactly one epic, E-1, whose tasks serve both ACs. [human]
  Observable: one `## E-1` section; no other epic heading; the check passes. Level: integration.
- **AC-55** (FR-33, FR-44) Given a `nio: approve tasks` commit holding `tasks.md` and the tasks verdict, when the implement stage is asked to start, then it proceeds. [derived: FR-33, FR-44]
  Observable: the first ready task can be claimed. Level: integration.
- **AC-56** (FR-25) Given T-3 is claimed in the CLI's state, when it is set to done, then the change is refused. [derived: FR-25]
  Observable: T-3 stays claimed; the message names the missing red, green and review steps. Level: integration.
- **AC-57** (FR-25) Given T-4 is pending because T-1 is not done, when T-4 is claimed, then the claim is refused; and given T-5 is already claimed, a second claim is refused. [derived: FR-25]
  Observable: both claims refused with "dependencies not done" and "already claimed". Level: integration.
- **AC-58** (FR-52) Given a host config mapping cheap and strong but not max, and an agent card with `tier: max`, when `nio agents sync` renders it, then the card runs on the strong model and a warning names max and that model. [human]
  Observable: the rendered card's model is the strong model; the output holds the warning. Level: unit.
- **AC-24** (FR-34) Given a task naming 12 files and serving 6 ACs, when the check runs, then size raises no error. [human]
  Observable: no error or warning about the task's size. Level: unit.

### US-4 The evaluator rates each task's model tier and effort (P2) [human]
- **Why this priority:** it sets cost and model choice, but the tasks are workable without it, on one default tier.
- **Independent test:** rate a fixture `tasks.md` and read the tiers and efforts in the estimate.

- **AC-25** (FR-18) Given the drafter has written `tasks.md`, when the evaluator runs, then every task has a tier with a reason and an effort. [human]
  Observable: every task's `Tier:` line is cheap, strong, max or frontier followed by a one-line reason, and its `Effort:` line is low, med or high. Level: e2e.
- **AC-26** (FR-17) Given a task with `Tier: frontier` and a Claude host, when its worker is started, then it runs on Fable; on a host that maps no frontier model, it runs on that host's max model. [human]
  Observable: the worker's model is Fable for Claude, and the host's max model elsewhere. Level: integration.

### US-5 The human sees the estimate and approves before implementation (P1) [human]
- **Why this priority:** NORTH_STAR's promise that the human sees the estimate before anything is spent.
- **Independent test:** print the estimate for a fixture file, then ask for implementation before and after approval.

- **AC-27** (FR-14) Given E-1 with T-1 (cheap, low, parallel), T-2 (cheap, med, parallel) and T-3 (max, high), when `nio check tasks` runs, then it prints E-1's estimate row. [human]
  Observable: a row for E-1 showing 3 tasks, 2 cheap, 0 strong, 1 max, 0 frontier, 1 low, 1 med, 1 high effort, and T-1, T-2 as parallel. Level: unit.
- **AC-28** (FR-14) Given any `tasks.md`, when the estimate is printed, then it holds no token or money figure. [human]
  Observable: the estimate's columns are task counts, tier and effort counts and parallel tasks only. Level: unit.
- **AC-29** (FR-33) Given a spec whose estimate the human has not approved, when the implement stage is asked to start, then it refuses. [human]
  Observable: no task is claimed; the message says the human must approve the estimate first. Level: integration.
- **AC-30** (FR-33) Given the human pushes back on the estimate, when the implement stage is asked to start, then it still refuses. [derived: FR-33, FR-44]
  Observable: the tasks stage is not approved; no task is claimed. Level: integration.

### US-6 Tasks added later go under Fixes and cite their source (P2) [human]
- **Why this priority:** the implementation jury (#29) needs it to append fix tasks, but the first plan works without it.
- **Independent test:** append a fix task to a fixture epic and diff the file.

- **AC-31** (FR-27) Given E-2 holds T-5 to T-7 and the highest task ID in the spec is T-11, when the implementation jury's finding J-4 on E-2 becomes a task, then T-12 is added under E-2's `#### Fixes` heading. [human]
  Observable: T-12 sits under `#### Fixes` in E-2 with `From: J-4 (implementation-E-2, round 1)` and the seven fields. Level: unit.
- **AC-32** (FR-29) Given the same epic, when T-12 is added, then the planned tasks above the heading are unchanged. [human]
  Observable: T-5 to T-7 are byte-for-byte unchanged. Level: unit.
- **AC-33** (FR-27) Given the human rejects a change request, when its task is added, then it goes under the epic's `Fixes` heading citing the change request. [human]
  Observable: a new task under `#### Fixes` whose `From:` line names the change request's ID. Level: unit.
- **AC-34** (FR-28) Given a task under `#### Fixes` with no `From:` line, when the check runs, then it fails. [derived: FR-27]
  Observable: non-zero exit; the error names the task and `From`. Level: unit.
- **AC-35** (FR-30) Given a fix task marked `Parallel: yes` naming the same file as a planned `Parallel: yes` task, when the check runs, then it fails as a parallel clash. [human]
  Observable: non-zero exit; the error names both tasks and the file. Level: unit.

### US-7 Status, "finished" and each epic's jury ledger are fixed (P2) [human]
- **Why this priority:** the implementation jury (#29) waits on these definitions, but tasks can be drafted and checked without them.
- **Independent test:** move fixture tasks through the CLI's state and run the implementation jury on one epic.

- **AC-36** (FR-25) Given T-3 is green in the CLI's state, when it is set to done without a review, then the change is refused. [human]
  Observable: T-3's state stays green; the message names the missing review. Level: integration.
- **AC-37** (FR-26) Given every planned task of E-2 is done and its fix task T-12 is in review, when E-2's readiness for the implementation jury is asked, then it is not finished. [human]
  Observable: E-2 is reported not finished, naming T-12. Level: integration.
- **AC-38** (FR-31) Given the implementation jury records round 1 on E-2, when the ledger is written, then it sits next to the spec gate's ledger, named for the epic. [human]
  Observable: `.nio/specs/<slug>/jury/implementation-E-2.json` and `.md` exist; the verdict subject is `implementation-E-2:<slug>`. Level: integration.
- **AC-39** (FR-35) Given a `tasks.md` with several tasks, when `nio task show <slug> T-3` runs, then it prints T-3 alone. [human]
  Observable: the output holds T-3's heading and seven lines and its epic's title, and no other task. Level: unit.

## Functional requirements
- **FR-1** WHEN the human starts the tasks stage on an approved spec THE SYSTEM SHALL run the tasks-drafter agent to write `.nio/specs/<slug>/tasks.md`. [human]
- **FR-2** IF the spec's jury neither approved it nor was closed by the human (`nio jury check --human`, recorded in the spec ledger) THEN THE SYSTEM SHALL refuse to start the tasks stage and say the spec must be approved first; a gate handed to the human but not closed by them does not count. For a full spec it SHALL also refuse until `nio check plan <slug> --approved` exits 0, and say the plan must be approved first. [human]
- **FR-3** THE SYSTEM SHALL keep all of a spec's epics and tasks in one `tasks.md`, one section per epic with its tasks under it, in the style of `spec.md`. [human]
- **FR-4** THE SYSTEM SHALL make one epic per user story of the spec, on a full spec in the order of the plan's build order. [human]
- **FR-51** WHEN the spec is a bug-fix (lite) spec THE SYSTEM SHALL make one epic, E-1, holding all its tasks, with no foundational epic. [human]
- **FR-5** WHEN setup is shared by more than one user story (on a full spec, when the plan's build order has a `Foundation` entry) THE SYSTEM SHALL put it in a foundational epic that comes first; each story epic depends on the epics of the entries its build-order entry's `Depends on:` names, or on the foundational epic when there is no plan. [human]
- **FR-6** THE SYSTEM SHALL number epics `E-n` and tasks `T-n` per spec, tasks across the whole spec, keep a task's ID when it moves to another epic, never renumber or reuse an ID, and list removed IDs in a `retired:` list. [human]
- **FR-7** THE SYSTEM SHALL require every task to state seven labelled lines in plain markdown: Files, Serves, Test, Depends on, Parallel, Tier and Effort. [human]
- **FR-8** IF a task lacks one of the seven lines THEN THE SYSTEM SHALL fail `nio check tasks`, naming the task and the line. [human]
- **FR-9** IF a task cites an AC, task, epic or plan test (`TC-n`) ID that the spec, the plan or `tasks.md` doesn't define (a `J-n` allowed by FR-49 excepted) THEN THE SYSTEM SHALL fail the check, naming the task and the ID. [human]
- **FR-10** IF an AC of the spec is served by no task THEN THE SYSTEM SHALL fail the check, naming the AC. [human]
- **FR-11** IF a task serves no AC, other than a task FR-49 allows to serve a finding, THEN THE SYSTEM SHALL fail the check, naming the task. [human]
- **FR-12** IF the tasks' dependencies form a cycle THEN THE SYSTEM SHALL fail the check, naming every task in the cycle. [human]
- **FR-13** IF two tasks marked parallel name the same file, and neither depends on the other directly or through other tasks, THEN THE SYSTEM SHALL fail the check, naming both tasks and the file. [human]
- **FR-14** WHEN `nio check tasks` runs THE SYSTEM SHALL print the estimate: for each epic, its task count, how many tasks run on each model tier and each effort, and which tasks can run in parallel, with no token or money figure. [human]
- **FR-15** THE SYSTEM SHALL state a task's model tier as `Tier: <cheap|strong|max|frontier>: <reason>` and its effort as `Effort: <low|med|high>`, the same values agent cards use once FR-17 has added `frontier` to them. [human]
- **FR-16** IF a `Tier:` line has a value other than cheap, strong, max or frontier, or no reason, or an `Effort:` line has a value other than low, med or high, THEN THE SYSTEM SHALL fail the check, naming the task. [derived: FR-15, FR-8]
- **FR-17** THE SYSTEM SHALL add a fourth model tier, `frontier`, above `max`, for agent cards and tasks alike; each coding agent maps tiers to its own models in config (Claude: cheap Haiku, strong Sonnet, max Opus, frontier Fable), and a host with no frontier model uses its max model. [human]
- **FR-18** WHEN the drafter has written `tasks.md` THE SYSTEM SHALL have the evaluator agent rate every task's model tier and effort. [human]
- **FR-19** THE SYSTEM SHALL have the tasks stage name each task's files from the spec and the code at planning time. [human]
- **FR-20** WHEN the spec is a full spec THE SYSTEM SHALL derive the tasks from its approved plan and follow it. [human]
- **FR-21** WHEN the spec is a bug-fix spec THE SYSTEM SHALL derive the tasks from the approved `spec.md` and the codebase. [human]
- **FR-53** IF, on a full spec, a contract that a build-order entry delivers has its bound file in no `Files:` line of that entry's epic, or a `TC-n` the entry lists is cited by none of the epic's tasks, THEN THE SYSTEM SHALL fail `nio check tasks`, naming the epic and the file or test. [human]
- **FR-54** IF the drafter meets a design choice the plan (full spec) or the spec (bug-fix spec) doesn't settle THEN THE SYSTEM SHALL stop without writing `tasks.md`: on a full spec the gap goes back to the plan or the spec through a change request; a bug-fix spec is re-routed to a full spec with a plan. [human]
- **FR-55** WHEN the spec is a full spec THE SYSTEM SHALL have each task's `Test:` line cite the plan's `TC-n` it writes, and a bug-fix spec's describe the test in words. [human]
- **FR-56** WHEN the spec or the plan changes after the `nio: approve tasks` commit THE SYSTEM SHALL treat the tasks approval as withdrawn until the tasks jury re-checks what changed, as a spec change withdraws a plan's approval. [human]
- **FR-23** THE SYSTEM SHALL keep no status or checkbox in `tasks.md`; a task's status lives only in the CLI's state, kept by the task machine the implement stage builds (#43, C-261028-xcg6), and only `nio flow` changes it. [human]
- **FR-24** IF `tasks.md` holds a checkbox or a status line THEN THE SYSTEM SHALL fail the check, naming the task. [derived: FR-23]
- **FR-25** THE SYSTEM SHALL count a task finished only when it reaches `done` through the guarded steps `pending → ready → claimed → red → green → review → done` of the task machine (#43, C-261028-xcg6), never on an agent's claim. [human]
- **FR-26** THE SYSTEM SHALL count an epic finished, and ready for the implementation jury, only when every task in it, fix tasks included, is `done`. [human]
- **FR-27** WHEN a task is added after planning (an implementation-jury fix task, a "justify or remove" task, or a task from a rejected change request) THE SYSTEM SHALL put it under a `#### Fixes` heading in its epic's section, with the next free `T-n` (one above the highest ID ever used, live or retired) and a `From:` line citing its finding or change request. [human]
- **FR-28** IF a task under a `#### Fixes` heading has no `From:` line THEN THE SYSTEM SHALL fail the check, naming the task. [derived: FR-27]
- **FR-29** WHEN a task is added under `#### Fixes` THE SYSTEM SHALL leave every planned task above the heading unchanged. [human]
- **FR-30** THE SYSTEM SHALL apply the field, ID, coverage, cycle and parallel checks to tasks under `#### Fixes` as to any other task. [human]
- **FR-31** THE SYSTEM SHALL keep each epic's implementation-jury ledger at `.nio/specs/<slug>/jury/implementation-E-n.json` and `.md`, with the verdict subject `implementation-E-n:<slug>`. [human]
- **FR-32** IF `nio check tasks` fails THEN THE SYSTEM SHALL not start the tasks jury (#28) on that spec. [human]
- **FR-33** THE SYSTEM SHALL not start the implement stage on a spec until the human has approved its estimate. [human]
- **FR-34** THE SYSTEM SHALL leave task size to the drafter's judgement (one worker, one context pack) and the tasks jury's review, with no file-count or AC-count limit in the check. [human]
- **FR-35** WHEN `nio task show <slug> T-n` runs THE SYSTEM SHALL print that task's section and its epic's title and no other task, with zero model calls, for a worker's pack or a juror. [human]
- **FR-36** THE SYSTEM SHALL accept `Depends on: none` for a task with no dependencies. [agent]
- **FR-37** THE SYSTEM SHALL accept only `yes` or `no` on a task's `Parallel:` line. [agent]
- **FR-38** IF two epics or two tasks share an ID THEN THE SYSTEM SHALL fail the check, naming the ID. [derived: FR-6]
- **FR-39** IF the spec is an epic-route spec THEN THE SYSTEM SHALL refuse to start the tasks stage and point to its slices' specs. [research: RF-15]
- **FR-40** IF a task cites a retired ID THEN THE SYSTEM SHALL fail the check, naming the ID as retired. [derived: FR-6]
- **FR-41** THE SYSTEM SHALL ship an `executability` lens card (tier cheap) with an `## At tasks` section that asks whether each task can be carried out as written by one worker from its pack. [human]
- **FR-42** WHEN `nio check tasks` passes THE SYSTEM SHALL let `nio jury plan <slug> tasks` plan the tasks gate with executability as its core lens. [human]
- **FR-43** THE SYSTEM SHALL ship the evaluator as an agent card with tier `strong` and effort `med`. [human]
- **FR-44** WHEN the tasks jury has passed and the human approves the estimate THE SYSTEM SHALL record both in one `nio: approve tasks` commit, and the implement stage SHALL treat that commit as the estimate approval FR-33 requires. [human]
- **FR-45** THE SYSTEM SHALL have a foundational-epic task cite in `Serves:` one or more of the ACs served by the tasks that depend on it, directly or through other tasks, and fail the check when it cites an AC none of those tasks serve; the foundational epic is the epic that names no user story. [human]
- **FR-47** THE SYSTEM SHALL decide whether a task runs in parallel only from its `Parallel:` and `Depends on:` lines, never from its tier or effort. [agent]
- **FR-48** THE SYSTEM SHALL check parallel-task file clashes across the whole spec, not only within an epic, and SHALL let a `Parallel: yes` task depend on other tasks, starting it only once they are done. [human]
- **FR-49** THE SYSTEM SHALL accept a jury finding ID (`J-n`) in `Serves:` only for a task under `#### Fixes` whose `From:` names that finding, and count such a task as covering no AC. [human]
- **FR-50** WHEN the estimate has been approved THE SYSTEM SHALL fail the check if any planned task's text changed since the `nio: approve tasks` commit; new work, including tasks for an accepted change request, goes under `#### Fixes` with `From:` naming its source, and a task made pointless is removed and its ID listed in `retired:`. [human]
- **FR-52** WHEN a host maps no model to a tier THE SYSTEM SHALL use the nearest lower tier it maps (frontier to max, max to strong, strong to cheap), for agent cards and tasks alike, and print a warning naming the tier and the model used; this replaces today's warn-and-inherit, which stays only when no lower tier is mapped either. [human]

## Rules
### State table: task status in the CLI's state (start: pending; final: done)
| State | dependencies done | claim | test fails (red) | test passes (green) | review starts | review passes | review fails | task fails | Src |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pending | → ready | reject: dependencies not done | reject: not claimed | reject: not claimed | reject: not claimed | reject: not claimed | reject: not claimed | reject: not claimed | [research: RF-12] |
| ready | ignore | → claimed | reject: not claimed | reject: not claimed | reject: not claimed | reject: not claimed | reject: not claimed | reject: not claimed | [research: RF-12] |
| claimed | ignore | reject: already claimed | → red | reject: no failing test first | reject: no failing test first | reject: not reviewed | reject: not reviewed | → ready | [research: RF-12] |
| red | ignore | reject: already claimed | ignore | → green | reject: tests not green | reject: not reviewed | reject: not reviewed | → ready | [research: RF-12] |
| green | ignore | reject: already claimed | reject: #43 decides (DF-1) | ignore | → review | reject: not reviewed | reject: not reviewed | → ready | [human] |
| review | ignore | reject: already claimed | reject: #43 decides (DF-1) | ignore | ignore | → done | → claimed | → ready | [research: RF-12] |
| done | ignore | reject: task is done | reject: task is done | ignore | reject: task is done | ignore | reject: task is done | reject: task is done | [research: RF-12] |

### Decision table: parallel clash
| first task parallel (yes, no) | second task parallel (yes, no) | share a file (yes, no) | one depends on the other (yes, no) | → check result | Src |
| --- | --- | --- | --- | --- | --- |
| yes | yes | yes | no | fail: parallel clash | [human] |
| yes | yes | yes | yes | pass | [human] |
| yes | yes | no | - | pass | [human] |
| no | - | - | - | pass | [research: RF-6] |
| yes | no | - | - | pass | [research: RF-6] |

### Decision table: where a task goes
| source (drafted, implementation-jury finding, justify or remove, rejected change request, accepted change request) | → place in its epic | Src |
| --- | --- | --- |
| drafted | above `#### Fixes`, no `From:` line | [human] |
| implementation-jury finding | under `#### Fixes`, `From:` names the finding | [human] |
| justify or remove | under `#### Fixes`, `From:` names the finding | [human] |
| rejected change request | under `#### Fixes`, `From:` names the change request | [human] |
| accepted change request | under `#### Fixes`, `From:` names the change request | [human] |

## Key entities
- **tasks.md**: one per spec at `.nio/specs/<slug>/tasks.md`; the epics and their tasks, plus a `retired:` list. Holds the plan only, no status. [human]
- **Epic**: `E-n`; one user story's slice of work, or the foundational epic of shared setup; finished when all its tasks are done. [human]
- **Task**: `T-n`; one worker's unit of work with seven fields: Files, Serves, Test, Depends on, Parallel, Tier, Effort. [human]
- **Fix task**: a task added under an epic's `#### Fixes` heading, with a `From:` line naming its finding or change request. [human]
- **Estimate**: the table `nio check tasks` prints: per epic, task count, tier and effort counts, and parallel tasks. [human]
- **Implementation-jury ledger**: one per epic, `jury/implementation-E-n.json` and `.md`. [human]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL run `nio check tasks`, including the estimate, with zero model calls. [human]

## Success criteria
- **SC-1** On the first spec broken into tasks, every AC is served by at least one task and every task serves an AC, before the tasks jury runs. [human]
- **SC-2** No implementation work starts on any spec before the human has approved its estimate. [human]

## Non-goals
- A token or money figure in the estimate; that waits for the usage estimate (#16). [human]
- The research skill's re-check of a task's files just before a worker starts (#18). [human]
- A fixed size limit on tasks (file count or AC count). [human]
- Tasks-jury lenses beyond executability, and the plan-gate coverage checks (#28, #50). [human]
- Building `nio flow` (#45) or the implement stage and its task machine (#43, C-261028-xcg6); this spec only defines what "finished" means for them; AC-29, AC-30, AC-36 and AC-55 to AC-57 run once #43 is built. [derived: FR-23, FR-25]

## Glossary
- **Epic**: a slice of a spec that can ship on its own: one user story, or the foundational setup. Never "phase" or "milestone".
- **Foundational epic**: the epic of setup shared by several stories, which comes first.
- **Task**: one unit of work small enough for one worker and one context pack. Never "ticket".
- **Fix task**: a task added after planning under an epic's `#### Fixes` heading.
- **Parallel task**: a task marked `Parallel: yes`, which may run at the same time as any other parallel task it neither depends on nor is depended on by, once its own dependencies are done.
- **Estimate**: what the human approves before implementation: counts by epic, tier and effort, and the parallel tasks.
- **Model tier**: cheap, strong, max or frontier, the model class an agent or a task's worker runs on, mapped to real models per coding agent. Not the jury's risk tier (`tier: low | medium | high` on verdicts and ledgers), which is a different field.
- **Effort**: low, med or high, how hard the model thinks, as on agent cards.

## Risks and evidence against
- A tiny story still gets its own epic and its own implementation-jury run. [human]
- Status is read with a command, not seen in `tasks.md`. [human]
- `tasks.md` gets long on big specs. [human]
- Small tasks still carry seven lines. [human]
- Rating is coarse, so a borderline task may get a bigger model or more effort than it needs. [human]
- File lists can go stale between planning and running, until the research skill (#18) re-checks them. [human]
- With no size limit, an oversized task costs a jury finding to catch, and runs may size tasks differently. [human]

## Decisions
- Tasks are rated with a model tier and an effort, and a `frontier` tier sits above `max`, for agent cards too: D-261027-vi67 (grill Q1, Q2, 2026-10-27).
- Task IDs were free-form until a template fixed them; this spec's `T-n` per spec is that template: D-261024-4xsd (memory, 2026-10-24).
- On a bug-fix spec, a task's `Test:` line says in words what the test checks (on a full spec it cites the plan's `TC-n`, D-261028-scwb); tests carry no spec IDs and the conformance lens matches them to ACs: D-261027-b44u (memory, 2026-10-27).

- The tasks stage builds on the plan stage and the plan jury: full specs follow their approved plan's build order, bug fixes come from the spec and the code: C-261028-7njg (change request, 2026-10-28).
- A bug fix that needs a design choice is re-routed to a full spec with a plan; the tasks drafter never makes one (grill Q15, 2026-10-28).
- On a full spec a task's `Test:` line cites the plan's `TC-n`: D-261028-scwb (grill Q16, 2026-10-28).

## Open points

## Deferred
- **DF-1** (from OP-5) What happens when a green or in-review task's tests fail again. Deferred: #43 builds the task state machine and decides it (grill Q4; moved from #45 by C-261028-xcg6).

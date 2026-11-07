---
slug: 2026-11-07-lite-path
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, FR-9, AC-3, AC-10]
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-07-lite-path` checks all of this. -->
# Lite path of the NIO flow for small bug fixes

## Summary
A lite route through the NIO flow for small bug fixes (issue #44): intake, a mini bugfix spec, a grill that asks only
on real ambiguity, repro, a failing test, the fix and the jury. It skips research, the advocate walk, the spec jury,
the architecture grill, the plan and the plan jury, aiming to save 15–30 minutes per small effort (#77). It reuses the
existing stages, flow state machine and jury, adds a routing rule for when work is lite (#11) and an escalation to the
full flow when the fix turns out bigger than expected. [agent]

## Actors and journeys
- **A-1 Developer**: the one human using NIO (RF-1), with a small defect from the backlog to fix; knows the codebase and the NIO flow, wants the fix shipped with a regression guard and without the full flow's ceremony. [research: RF-1]
- **A-2 Agent**: any coding agent following NIO's plain-markdown skills to run the effort. [human]

**UJ-1 Fix a small bug on the lite path** (A-1, A-2) [agent]
1. A-1 describes a defect; A-2 proposes the lite route in one line and A-1 accepts it.
2. A-2 drafts the bugfix spec (current, expected, unchanged behaviour); the grill asks only on real ambiguity.
3. A-2 cuts the fix into one epic of tasks; A-1 approves them once, after the tasks jury.
4. Workers reproduce the bug as a failing test, fix it, and the implementation jury reviews the fix.
- Misuse: A-1 or A-2 routes a risky or multi-module change as lite to skip review.
- Evidence: #44, #11, #19, RF-5.

**UJ-2 Escalate to the full flow** (A-1, A-2) [agent]
1. During a lite effort A-2 hits one of FR-8's escalation triggers.
2. A-2 stops and offers the full flow; A-1 accepts and the spec is rewritten on the full route with nothing re-asked.
- Misuse: A-2 keeps going on lite past a trigger, or switches without asking A-1.
- Evidence: #44, RF-12.

## User stories

### US-1 Run a small fix through the lite route (P1) [human]
- **Why this priority:** it is the time saving itself; without it nothing else in this spec has a path to run on.
- **Independent test:** start a lite effort on a one-module bug and drive it to done; the flow history shows only the lite stages.

- **AC-1** (FR-1, FR-2, FR-15) Given a lite effort at intake, when the flow is driven to done, then it passes intake, drafting, grilling, tasking, the tasks jury and implementing in that order, and records each other stage as skipped. [agent]
  Observable: the effort's flow history has `pass` lines drafting → grilling → tasking → tasks_jury → implementing → done, a `skip` line for each of researching, advocate_walking, spec_jury, arch_grilling, planning and plan_jury, and `nio flow next` names no plan or spec-jury skill on the way. Level: integration.
- **AC-2** (FR-3) Given a lite spec with no open point of kind decision, when the grill runs, then it asks the human zero questions. [human]
  Observable: the grill skill says that on a lite spec it skips the six-facet coverage and asks only open points of kind decision and `[default]` items over its step-4 bar (a change to what a user can do or sees, who may do it, data kept or changed, or cost), so a spec with neither gets zero questions. Level: unit.
- **AC-4** (FR-6) Given a lite effort whose expected-behaviour test already passes before the fix, when red is reported for its task, then the effort does not advance. [agent]
  Observable: `nio flow red` on a lite effort's task refuses a test that passes, and the task is not marked red. Level: integration.
- **AC-5** (FR-13) Given a finished fix, when the lite effort's epic closes, then the implementation jury reviews the fix diff and the effort reaches done only on an approval. [human]
  Observable: `nio jury plan <slug> implementation-E-1` on a lite effort plans the conformance and correctness lenses, and `nio flow next` reaches done only after the epic's gate passes. Level: integration.

### US-2 Write a mini bugfix spec (P1) [human]
- **Why this priority:** every lite effort starts with it; it carries the "no assumptions" rule and the regression guard.
- **Independent test:** create a lite spec, fill it, and run the spec check on it.

- **AC-6** (FR-4) Given a new lite effort, when its spec is created, then it has current, expected and unchanged behaviour sections and acceptance criteria. [research: RF-7]
  Observable: the created spec has those four sections. Level: unit.
- **AC-7** (FR-5) Given a lite spec whose unchanged behaviour section is empty or whose unchanged item has no acceptance criterion, when the spec check runs, then it fails naming the gap. [research: RF-6]
  Observable: the check exits non-zero and its message names the unchanged-behaviour gap. Level: unit.
- **AC-8** (FR-7) Given a bug-fix spec, when the tasks drafter cuts it, then its card has each unchanged-behaviour test run as its own task before the fix and in the suite after it. [agent]
  Observable: the tasks drafter card says that on a bug fix each unchanged-behaviour test is its own `direct` task that the fix's task depends on, so its green runs before the fix and the epic's suite after it; whether a list follows it is judged at the tasks jury. Level: unit.

### US-3 Escalate a lite effort that turns out bigger (P2) [human]
- **Why this priority:** it is the safety net that lets the routing rule stay simple; it only matters once lite runs.
- **Independent test:** run the tasks check on a lite effort whose tasks touch two modules and check that it fails with the offer; then switch the spec to full and see the flow place it on the full route.

- **AC-9** (FR-8) Given a lite effort, when its tasks change non-test files in more than one folder, then `nio check tasks` prints a note naming the folders and the full flow, and the tasks skill stops on it. [agent]
  Observable: the check prints `escalate:` with each folder and the offer of the full flow, and still exits 0 when nothing else fails; `src/a/x.py` with `tests/test_x.py` gives no note, `src/a/x.py` with `src/a/sub/y.py` gives one, and a full spec never gets it. Level: unit.
- **AC-11** (FR-10) Given a lite effort at tasking or later, when the human accepts the switch and its spec is rewritten on the full route, then the flow places it by the full route's guards: a skip line never counts as a gate's pass, so it stands at spec_jury when the rewritten spec passes the gate check and at grilling when it doesn't, and the rewrite keeps every settled item's provenance. [agent]
  Observable: `nio flow next` says spec_jury for a rewritten spec passing `nio check spec --gate`, and grilling for one with an open point; the spec skill says each current, expected and unchanged item becomes an FR with its AC and keeps its tag. Level: integration.
- **AC-12** (FR-11) Given a stopped lite effort, when the human declines the switch, then the effort continues on lite and the human's call is logged. [agent]
  Observable: the spec skill says a declined switch continues on lite and is logged in `grill.md` with the trigger it overrides. Level: unit.
- **AC-16** (FR-8) Given a lite effort whose fix needs a new dependency, a change to an interface used outside the bug's folder or to stored data, when the tasks drafter, the grill or a worker finds it, then it stops and the full flow is offered. [agent]
  Observable: the tasks, grill and implement skills each name these triggers and the offer of the full flow. Level: unit.

### US-4 Pick lite or full at intake (P2) [human]
- **Why this priority:** a wrong call is caught later by escalation, so the rule can be simple; it still decides who gets the time saving.
- **Independent test:** read the spec skill's routing step against intakes that meet and break each lite criterion.

- **AC-13** (FR-12) Given an intake describing a defect with an obvious expected behaviour, a likely one-module scope and no risky flag, when a route is picked, then lite is proposed. [human]
  Observable: the spec skill's routing step names the four criteria and routes lite only when all hold. Level: unit.
- **AC-14** (FR-12) Given an intake that breaks any one of the four lite criteria, when a route is picked, then full is proposed. [human]
  Observable: the spec skill's routing step says full when any criterion fails, and names the risk flags auth, money, data-deletion, migration and pii. Level: unit.
- **AC-15** (FR-14) Given a proposed route, when it is shown to the human, then it is one plain line naming the route by what it means and saying they can change it, and their change is followed. [human]
  Observable: the spec skill tells the human the route in one line by what it means and that they can change it. Level: unit.

## Functional requirements
- **FR-1** WHEN an effort's route is lite THE SYSTEM SHALL run its stages in the order intake, mini bugfix spec (drafting), grill, tasks and their jury, then implementing, where each task's red is the repro and failing test and its green the fix, and the epic's implementation jury is the jury. [agent]
- **FR-2** WHEN an effort's route is lite THE SYSTEM SHALL skip research fan-out, the user advocate walk, the spec jury, the architecture grill, the plan and the plan jury, each recorded as skipped; the state table "Lite effort" is this view of the flow's one table, not a second machine. It differs from the full route only where a skip joins two stages (grilling → tasking); implementing → implementing on a jury rejection is the implementation gate's existing loop (fix tasks appended, the epic re-judged). Unlike #44's skip list, the tasks stage stays (grill Q1). [agent]
- **FR-3** WHILE grilling a lite spec THE SYSTEM SHALL ask the human only about open points that need a human decision. [human]
- **FR-4** WHEN a lite effort is created THE SYSTEM SHALL give it a spec with current, expected and unchanged behaviour sections and acceptance criteria. [research: RF-7]
- **FR-5** IF a lite spec has no unchanged-behaviour item, or an unchanged item has no acceptance criterion, THEN THE SYSTEM SHALL fail the spec check. [research: RF-6]
- **FR-6** IF the expected-behaviour test does not fail before the fix THEN THE SYSTEM SHALL not advance the lite effort's task past red. [research: RF-5]
- **FR-7** WHEN the tasks drafter cuts a lite fix into tasks THE SYSTEM SHALL have it put each unchanged-behaviour test in its own `direct` task that the fix's task depends on, so the test runs before the fix and in the suite after it. [agent]
- **FR-8** IF a lite fix changes non-test files in more than one folder, needs a new dependency, or changes an interface used outside the bug's folder or stored data THEN THE SYSTEM SHALL stop the effort and offer the full flow; the folder trigger is a note from `nio check tasks`, the others are judged by the agent from the skills. [agent]
- **FR-10** WHEN the human accepts the switch to full THE SYSTEM SHALL continue the same effort on the full route, its spec rewritten with every settled lite item kept with its provenance, placed by the full route's guards where a skip line never counts as a gate's pass. [agent]
- **FR-11** WHEN the human declines the switch to full THE SYSTEM SHALL continue the effort on lite and log the human's call. [agent]
- **FR-12** WHEN picking a route at intake THE SYSTEM SHALL propose lite only when the intake is a defect, the expected behaviour is stated or obvious, the likely scope is one module and no risk flag from auth, money, data-deletion, migration or PII applies, and full otherwise; the flags external-input, multi-party and public-api may stay lite, their lenses running at the implementation gate as usual. [agent]
- **FR-13** WHEN a lite fix's epic is done THE SYSTEM SHALL have the implementation jury review the fix diff with the gate's usual lenses: conformance and correctness, plus lenses from risk flags and consistency when an existing file changes (RF-10), rather than #44's one-lens default (grill Q2). [agent]
- **FR-15** WHEN an effort's spec is route lite THE SYSTEM SHALL let `nio flow` drive it like a full effort (status, next, done, claim); an epic spec stays unsupported. [agent]
- **FR-14** WHEN a route is proposed THE SYSTEM SHALL tell the human in one plain line and follow the human's choice if they change it. [human]

## Rules

### State table: Lite effort (start: intake; final: done, full route)
| State | guard passes | jury rejects | spec rewritten on the full route | Src |
| --- | --- | --- | --- | --- |
| intake | → drafting | ignore | ignore | [agent] |
| drafting | → grilling | ignore | → full route | [agent] |
| grilling | → tasking | ignore | → full route | [agent] |
| tasking | → tasks_jury | ignore | → full route | [agent] |
| tasks_jury | → implementing | → tasking | → full route | [agent] |
| implementing | → done | → implementing | → full route | [agent] |
| full route | ignore | ignore | ignore | [agent] |
| done | ignore | ignore | ignore | [agent] |

### Decision table: Route at intake
| Defect (yes, no) | Expected behaviour stated or obvious (yes, no) | Likely scope one module (yes, no) | Risk flag auth/money/data-deletion/migration/PII (yes, no) | → route | Src |
| --- | --- | --- | --- | --- | --- |
| yes | yes | yes | no | lite | [human] |
| no | - | - | - | full | [human] |
| yes | no | - | - | full | [human] |
| yes | yes | no | - | full | [human] |
| yes | yes | yes | yes | full | [human] |

## Key entities
- **Bugfix spec**: the lite effort's spec: current, expected and unchanged behaviour items and their acceptance criteria, each with provenance. [human]
- **Escalation trigger**: a condition stated in the skills (FR-8) that stops a lite effort and offers the full flow; only the folder trigger is checked by the CLI. [agent]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL keep every lite-path instruction in plain markdown that any agent can follow, with 0 required host-specific tools. [human]
- **NFR-2** THE SYSTEM SHALL report the dogfooded lite effort's wall-clock per stage next to the same stages on the two latest full efforts (RF-2), with a target of at least 15 minutes saved; this is a reported measure, not a pass or fail test. [agent]

## Success criteria
- **SC-1** One small open bug from the backlog runs through the lite path end to end, and its timed wall-clock is reported against a full-flow effort. [human]
- **SC-2** The minimum lite routing criteria are recorded as a decision, with the recommended default from #11. [human]

## Non-goals
- Routing rules for the epic route; only the minimum lite-versus-full rule is settled here. [human]
- A learned or model-based router. [human]
- New stages, a new flow state machine or a new jury; lite reuses the existing ones, the flow's table gaining only a per-route set of skipped stages (the transitions this changes are listed in FR-2). [human]
- A deterministic check for a new dependency or an interface change; those triggers are judged by the agent from the skill's list. [agent]

## Glossary
- **Lite route**: the short path for small bug fixes. Never "fast path" or "quick mode".
- **Escalation**: stopping a lite effort and offering to continue it on the full route. Never "upgrade".
- **Module**: the direct parent folder of a changed non-test file (the repository root counts as one), as counted for the escalation trigger. A test file sits under a folder named `tests` or `test`, or its name starts with `test_`.

## Decisions
- Lite runs intake, drafting, grilling, tasks and the tasks jury, then implementing with the implementation jury; it skips the spec jury, plan and plan jury. The tasks stage stays because implementing claims from `tasks.md`, and its approval is the human's one approval (grill Q1, [agent], RF-8, RF-9).
- The implementation gate keeps its usual lenses on a lite fix (grill Q2, [agent], RF-10, RF-11).
- No separate approval of the bugfix spec; the human approves once at the tasks gate (grill Q3, [agent]).
- A declined switch continues on lite, logged (grill Q4, [agent]).
- The "needs a decision" trigger folds into the grill's bar and FR-8's list; FR-9 retired (grill Q5, [agent]).
- The module trigger is a note from `nio check tasks` on a lite spec, so a declined switch can go on; the other triggers are judged from the skills (grill Q6, Q10, [agent], RF-16).
- Unchanged-behaviour tests run as `direct` tasks before the fix's task (grill Q7, [agent], RF-17).
- Escalation rewrites the same effort's spec on the full route; the flow re-places it (grill Q8, [agent], RF-13, RF-14).
- Routing criteria (#11) live in the spec skill's routing step; no code router (grill Q9, [agent], RF-15).
- Escalation placement: a skip line never counts as a gate's pass; a rewritten spec stands at spec_jury or grilling (grill Q11, [agent], RF-13).
- external-input, multi-party and public-api may stay lite (grill Q12, [agent]).
- The dogfood time is a reported measure (grill Q13, [agent]).

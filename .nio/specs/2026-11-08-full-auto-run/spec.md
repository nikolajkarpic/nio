---
slug: 2026-11-08-full-auto-run
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [multi-party]              # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [NFR-1, OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, OP-10, OP-11, OP-12, OP-13]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-08-full-auto-run` checks all of this. -->
# Full-auto run: once the spec draft is written, an effort drives itself through every jury and fix to a pull request

## Summary
Today the `auto` flag in `state.json` exists, but nothing sets it, nothing drives the stages, and every jury finding
goes to the human. This lets the human switch an effort to auto once the spec draft is written. A driver then runs
spec jury, fixes, re-jury, plan, plan jury, tasks, tasks jury, each epic's implementation and epic jury, with a fixer
that settles refuter-confirmed blockers and majors on its own. The run opens a pull request whose body is the one
report and stops; it never merges. The stop list, the risky-flag rule and any fix that would touch the human's own
words or cut scope still bring the human back. It serves "Autonomy is earned through the jury, never assumed" and
"I can read why every autonomous decision was allowed" (issue #122). [human]

## Actors and journeys
- **A-1 Human**: owns the project; writes the spec draft, grants auto, reads the pull request, and is called back only when the run stops. [human]
- **A-2 Driver**: the agent session that runs an auto effort stage by stage through `nio flow next` and `nio flow done`; its context can be compacted or replaced. [human]
- **A-3 Fixer**: the agent that edits a stage's files to settle jury findings within its authority and starts the next round. [human]
- **A-4 Jury**: the lenses and the refuter that judge each gate, as today; under auto their verdict is what allows each step. [agent]

**UJ-1 Hand off a written spec, get a pull request** (A-1, A-2, A-3) [research: RF-1]
1. The human finishes the spec draft and grants auto.
2. The driver runs each stage; at each gate the jury reviews and the fixer settles what it confirms.
3. The effort reaches done and the driver opens a pull request with the report as its body.
4. The human reads the report and decides whether to merge.
- Misuse: the driver or fixer grants itself auto, or rewrites the human's own lines to get past a jury.
- Evidence: issue #122; RF-1.

**UJ-2 A stop brings the human back** (A-1, A-2) [derived: FR-10, FR-11, FR-28, FR-34]
1. A stop fires: the stop list, a risky flag, a fix that would touch a `[human]` line or cut scope, or a cap.
2. The driver stops and tells the human why and how to resume.
3. The human settles it and resumes; the run carries on in auto.
- Misuse: the run carries on past a stop, or stops without saying why.
- Evidence: issue #122; flow-state FR-39 to FR-42 and FR-51; RF-1.

## User stories

### US-1 The human grants auto once the spec draft is written (P1) [human]
- **Why this priority:** nothing else runs without the switch; the flow-state spec deferred it.
- **Independent test:** grant auto on a fixture effort with a written draft and read `state.json` and the history.

- **AC-1** (FR-1, FR-3) Given an effort whose spec draft passes `nio check spec`, when the human runs `nio flow start <slug> --auto --by human`, then the auto flag is on and the history records the grant; the same command without `--by` is refused. [human]
  Observable: `state.json` has `auto: true`; the newest history line records the grant, who gave it and the stage; without `--by`, non-zero exit and `auto: false`. Level: unit.
- **AC-2** (FR-2, FR-3) Given an effort at the drafting stage whose draft passes `nio check spec`, when the done command that closes drafting is given the auto flag with `--by human`, then the effort moves on with auto on and the grant recorded; given another `--by`, the grant is refused. [human]
  Observable: `state.json` has `auto: true`; the history has the stage's pass line and a grant line; with another `--by`, `auto: false` and no grant line. Level: unit.
- **AC-3** (FR-4) Given an effort whose spec draft fails `nio check spec`, when auto is asked for, then it is refused. [derived: FR-31]
  Observable: non-zero exit naming the failing check; `state.json` keeps `auto: false`; no history line is added. Level: unit.

### US-2 The driver runs every stage to the end (P1) [human]
- **Why this priority:** the switch is worthless without something that moves the effort.
- **Independent test:** run the driver on a fixture effort whose stages all pass and check it reaches done with no human line after the grant.

- **AC-4** (FR-5) Given an auto effort at spec_jury whose juries all approve, when the driver runs, then it runs every stage in order until the effort is done. [human]
  Observable: the history has a pass line for each stage of the route in order and no line from the human after the grant. Level: e2e.
- **AC-5** (FR-5, FR-25) Given an auto effort under its jury cap whose plan gate has run 3 jury rounds without approval (the stop list's per-gate round limit, flow-state FR-39), when the driver runs, then the effort pauses and the driver stops and tells the human the reason and the resume command. [derived: FR-25]
  Observable: `state.json` pause names the plan jury's 3 rounds; no `done` line after the pause; the driver's last message holds the reason and `nio flow start <slug>`. Level: integration.
- **AC-6** (FR-6) Given a host that can start subagents, when the driver runs a stage, then that stage runs in a fresh subagent. [human]
  Observable: the run's usage has one subagent run per stage, each started by the driver. Level: e2e.
- **AC-7** (FR-6) Given a host that can't start subagents, when the driver runs, then it runs each stage in its own session and still reaches done. [human]
  Observable: the history reaches done; the run's usage shows no subagent runs for stages. Level: e2e.
- **AC-8** (FR-26) Given an auto effort paused for the human, when the human resumes it, then the run carries on with auto still on. [derived: FR-32]
  Observable: `state.json` keeps `auto: true` after `nio flow start`; `nio flow next` names a skill. Level: unit.
- **AC-9** (FR-29) Given a driver running an effort, when a second driver starts on the same effort, then the second stops without moving it. [derived: FR-29]
  Observable: the second driver exits naming the running one; the history has no line from it. Level: integration.
- **AC-10** (FR-27) Given a host that pushes long commands to the background, when a gate's jury runs, then the driver waits for the round's completion notice, without polling, before calling `nio flow done`. [human]
  Observable: no `done` line for the gate precedes the close of its jury round in the ledger; the driver's transcript shows no `nio flow`, `nio jury` or ledger read between starting the round and its completion notice. Level: e2e.
- **AC-11** (FR-5) Given a driver stopped at any point mid-stage, when a new driver starts on the effort, then it carries on from `nio flow next` and repeats no passed gate. [derived: NFR-2]
  Observable: no gate has two pass lines; the history reaches done. Level: integration.

### US-3 The fixer settles jury findings within its authority (P1) [human]
- **Why this priority:** without it every round ends with the human, which is not autonomy.
- **Independent test:** feed a fixture ledger with one confirmed major per case of the fixer table and check each outcome.

- **AC-12** (FR-9) Given an auto spec jury round with a refuter-confirmed major whose fix touches no `[human]` line and cuts no scope, when the round ends, then the fixer edits the spec and the next round starts. [human]
  Observable: `spec.md` changed; the finding is disposed by the fixer; the ledger's round number went up by 1. Level: integration.
- **AC-13** (FR-10) Given a refuter-confirmed blocker whose fix would rewrite a `[human]`-tagged line, when the fixer acts, then the effort pauses for the human. [human]
  Observable: `spec.md` unchanged; status `waiting_for_human` naming the finding and the line's ID. Level: integration.
- **AC-14** (FR-11) Given a refuter-confirmed major whose fix would drop a user story, when the fixer acts, then the effort pauses for the human. [human]
  Observable: status `waiting_for_human` naming the finding and the story; the story is still in `spec.md`. Level: integration.
- **AC-15** (FR-12) Given a fix round that changed a `[human]`-tagged line, when the round ends, then the effort pauses for the human before the next round. [derived: FR-10]
  Observable: status `waiting_for_human` naming the changed line's ID; no new jury round in the ledger. Level: unit.
- **AC-16** (FR-7, FR-8) Given an auto effort at grilling with two open points and one `[default]` item, when the stage runs, then all three end tagged `[auto]` and no question goes to the human. [human]
  Observable: `## Open points` is gone; each resulting item and the former `[default]` item end with `[auto]`; no `[default]` is left; both OP IDs are in `retired`; the grill log records no question asked. Level: integration.
- **AC-17** (FR-13, FR-14) Given an auto effort whose spec holds `[auto]` items and whose spec jury approved, when the spec gate check runs, then it passes. [human]
  Observable: `nio check spec <slug> --gate` exits 0. Level: unit.
- **AC-18** (FR-14) Given the same spec after the human switched auto off, when the spec gate check runs, then it still passes. [human]
  Observable: `nio check spec <slug> --gate` exits 0; no `[auto]` item is listed. Level: unit.
- **AC-19** (FR-15) Given an auto spec with `[auto]` defaults, when the spec jury runs, then the jury judges each one. [human]
  Observable: the spec jury's packs list every `[auto]` item's ID for judging. Level: unit.
- **AC-20** (FR-16) Given an auto effort with epics E-1 and E-2 whose E-1 epic jury confirms a major, when the driver runs, then the fixer fixes it and E-1 is re-judged before any E-2 task starts. [human]
  Observable: in the history, E-1's `epic` line comes before E-2's first task line; the E-1 ledger has 2 rounds. Level: integration.
- **AC-21** (FR-17) Given an auto jury round with only minor and refuted findings, when the round ends, then the fixer edits nothing for them, the gate closes, and the report lists them. [human]
  Observable: the stage's files unchanged by the fixer; the pull request body lists each finding's ID. Level: integration.

### US-4 The run ends in a pull request that is the one report (P2) [human]
- **Why this priority:** it is how the human is notified and reads why each step was allowed; it matters once a run can reach the end.
- **Independent test:** finish a fixture auto run against a scratch remote and read the pull request.

- **AC-22** (FR-20, FR-21) Given an auto effort that reaches done, when the driver finishes, then it opens a pull request and stops without merging. [human]
  Observable: one open pull request from the effort's branch; the base branch's head is unchanged. Level: e2e.
- **AC-23** (FR-22, FR-23) Given a finished auto run, when its pull request body is read, then it has each gate, what the jury found, what was auto-fixed and every `[auto]` default, each with the record that allowed it. [human]
  Observable: every gate in the history, every fixer-disposed finding ID and every `[auto]` item ID in the spec appear in the body, each next to a verdict record ID or history line. Level: integration.
- **AC-24** (FR-24) Given an auto effort that reaches done with no way to open a pull request, when the driver finishes, then it pauses for the human and prints the report. [human]
  Observable: status `waiting_for_human` naming the failure; the report printed; the effort's commits kept. Level: integration.

### US-5 Budgets default to what the effort's gates need (P2) [human]
- **Why this priority:** caps only bite on long runs; a sane default keeps a run from stopping early or running away.
- **Independent test:** compute the cap for fixture efforts with and without a config value.

- **AC-25** (FR-18) Given an auto effort whose tasks have 3 epics and no `budgets.juries` in config, when the cap is computed, then it is 12. [human]
  Observable: the cap the stop list uses is 12 (2 × (3 gates + 3 epics)). Level: unit.
- **AC-26** (FR-19) Given `budgets.juries: 5` in config, when the cap is computed, then it is 5. [human]
  Observable: the cap the stop list uses is 5. Level: unit.

### US-6 Risky specs still stop at every gate (P2) [human]
- **Why this priority:** it guards the riskiest specs, but the rule already exists in flow-state; this story keeps it true under the driver.
- **Independent test:** run the driver on a fixture spec flagged `money`.

- **AC-27** (FR-28) Given an auto effort whose spec has `risk: [money]`, when the spec jury approves, then nothing is committed and the driver stops with the commit command for the human. [human]
  Observable: `HEAD` unchanged; the driver's last message prints `nio flow done spec_jury --commit`. Level: integration.
- **AC-28** (FR-28, FR-26) Given that stop, when the human commits, then the driver carries on in auto to the next gate. [derived: FR-32, FR-28]
  Observable: the history has the human's commit line and then plan stage lines; `auto` still true. Level: integration.

### US-7 The human keeps control of the grant (P1) [human]
- **Why this priority:** the grant hands gate approval to the jury; only the human may give or take it.
- **Independent test:** grant and revoke auto on fixture efforts with each `--by` role and at each stage.

- **AC-29** (FR-30) Given an effort whose draft passes `nio check spec`, when `nio flow start <slug> --auto --by orchestrator` runs, then it is refused. [human]
  Observable: non-zero exit; `state.json` keeps `auto: false`; no history line added. Level: unit.
- **AC-30** (FR-31) Given a manual effort at plan_jury, when the human grants auto, then the flag is on and the driver carries on from plan_jury. [human]
  Observable: `auto: true`; the grant line names `plan_jury`; `nio flow next` names the plan-jury skill. Level: unit.
- **AC-31** (FR-32) Given an auto effort whose fixer is mid-round, when the human switches auto off, then the fixer's edits finish and no new jury round starts without the human. [human]
  Observable: `auto: false`; a history line records the switch; the ledger's round number unchanged until the human acts. Level: integration.
- **AC-32** (FR-18) Given an auto effort at plan_jury with no tasks and no `budgets.juries`, when the cap is computed, then it is 6. [human]
  Observable: the cap the stop list uses is 6. Level: unit.
- **AC-33** (FR-33) Given an auto effort with no `budgets.subagents` that has started 200 subagents, when the driver starts another, then the run is not suspended; given `budgets.subagents: 3`, the fourth suspends it as `suspended: cap`. [human]
  Observable: `state.json` pause is null in the first case and `suspended: cap` in the second. Level: unit.
- **AC-34** (FR-34) Given an auto jury round whose final fix check flags a fix that didn't hold, when the round ends, then the effort pauses for the human. [human]
  Observable: status `waiting_for_human` naming the finding; the gate not passed. Level: integration.
- **AC-35** (FR-35) Given an auto lite-route effort whose juries approve, when the driver runs, then it passes each lite stage in order and opens a pull request. [human]
  Observable: the history has a pass line for each lite stage and none for plan; one open pull request. Level: e2e.
- **AC-36** (FR-36) Given an auto spec with `risk: [money]`, when a fix removes `money`, then the effort pauses before the next round. [human]
  Observable: status `waiting_for_human` naming the `risk:` change; no new jury round in the ledger. Level: unit.
- **AC-37** (FR-37) Given an auto fix round that removed AC-4 and added a Non-goals entry, when the round ends, then the effort pauses naming both. [human]
  Observable: status `waiting_for_human` naming AC-4 and the new non-goal; no new round. Level: unit.
- **AC-38** (FR-38) Given a driver claim last refreshed 31 minutes ago, when a new driver starts, then it takes the effort over; given a claim refreshed 5 minutes ago, it is refused. [human]
  Observable: the claim names the new driver in the first case; in the second, non-zero exit naming the running driver and the claim unchanged. Level: unit.
- **AC-39** (FR-39) Given an auto round whose refuter output has no verdict for J-2 (a major), when the round ends, then the effort pauses naming J-2. [human]
  Observable: status `waiting_for_human` naming J-2; the gate not passed. Level: unit.
- **AC-40** (FR-39) Given an auto round with a refuted blocker and a refuted major, when the run report is written, then the blocker is listed first. [human]
  Observable: the refuted blocker's ID comes before every other finding in the pull request body. Level: unit.
- **AC-41** (FR-40) Given an auto effort suspended at its jury cap of 6 while at plan_jury, when the human resumes it, then the cap is 8 and plan_jury may run 2 more rounds. [human]
  Observable: the cap the stop list uses is 8; history records the raise; the next `nio flow next` names the jury skill. Level: unit.
- **AC-42** (FR-30) Given a grant made with `--by human` from an agent session, when the history is read, then the grant line names the host and model that ran it. [human]
  Observable: the grant line's `who` holds a non-empty host and model. Level: unit.

- **AC-43** (FR-38) Given two drivers started on the same effort at the same instant, when both try to claim it, then exactly one holds the claim and the other is refused. [human]
  Observable: one claim naming one driver; the other exits non-zero; the history has lines from one driver only. Level: integration.
- **AC-44** (FR-38) Given a live driver 45 minutes into one stage, waiting on a long command, when a second driver starts, then it is refused. [human]
  Observable: the claim's refresh time is under 10 minutes old; the second driver exits non-zero naming the first. Level: integration.
- **AC-45** (FR-41) Given an auto effort paused because its pull request couldn't be opened, when the human resumes it after fixing the cause, then the pull request opens and no stage runs. [human]
  Observable: one open pull request; no new pass, jury or task line in the history after the resume. Level: integration.

## Functional requirements
- **FR-1** WHEN the human runs `nio flow start <slug> --auto --by human` THE SYSTEM SHALL switch the effort's auto flag on. [human]
- **FR-2** WHEN the done command that closes the drafting stage is given the auto flag with `--by human` THE SYSTEM SHALL switch the auto flag on as the effort moves on. [human]
- **FR-3** WHEN the auto flag is switched on THE SYSTEM SHALL append a history line that records the grant, who gave it and the stage. [human]
- **FR-4** IF auto is asked for while the spec draft fails `nio check spec` THEN THE SYSTEM SHALL refuse it and name the failing check. [derived: FR-31]
- **FR-5** THE SYSTEM SHALL provide a driver that repeats `nio flow next`, the skill it names, and `nio flow done` until the effort pauses, is suspended or is done. [human]
- **FR-6** WHEN the driver starts a stage on a host that can start subagents THE SYSTEM SHALL run that stage in a fresh subagent. [human]
- **FR-7** WHILE the auto flag is on THE SYSTEM SHALL turn each open point into a default tagged `[auto]`, and retag each `[default]` item `[auto]`, instead of asking the human. [human]
- **FR-8** WHILE the auto flag is on, WHEN the effort reaches the grilling stage THE SYSTEM SHALL settle its open points and `[default]` items by FR-7 and ask the human nothing. [derived: FR-7, AC-16]
- **FR-9** WHILE the auto flag is on, WHEN a jury round ends with refuter-confirmed blocker or major findings THE SYSTEM SHALL have the fixer edit the stage's files to fix each and start the next round. [human]
- **FR-10** WHILE the auto flag is on, IF a fix would change or drop a `[human]`-tagged line THEN THE SYSTEM SHALL pause for the human, naming the finding and the line. [human]
- **FR-11** WHILE the auto flag is on, IF a fix would cut scope THEN THE SYSTEM SHALL pause for the human, naming the finding and what it would cut. Cutting scope is defined by FR-37. [human]
- **FR-12** WHILE the auto flag is on, WHEN a fix round ends with a `[human]`-tagged line changed or gone THE SYSTEM SHALL pause for the human before the next round. [derived: FR-10]
- **FR-36** WHILE the auto flag is on, WHEN a fix adds, removes or changes a flag in the spec's `risk:` list THE SYSTEM SHALL pause for the human before the next round, naming the change. [human]
- **FR-37** WHILE the auto flag is on, WHEN a fix round ends with any FR, AC or user story removed, or an entry added to Non-goals, compared with the previous round THE SYSTEM SHALL pause for the human, naming each; this is what FR-11 calls cutting scope. [human]
- **FR-38** THE SYSTEM SHALL treat a driver as running while its claim was refreshed within the last 30 minutes; the claim is taken atomically, so of two drivers starting at once exactly one gets it; the driver refreshes its claim at each stage and at least every 10 minutes while it waits on a long command; a claim older than 30 minutes is stale and may be taken over by a new driver. [human]
- **FR-39** WHILE the auto flag is on, WHEN the refuter returns no verdict for a blocker or major THE SYSTEM SHALL pause for the human, naming the finding; a refuted blocker is accepted under FR-17 and listed first in the run report. [human]
- **FR-41** WHEN the human resumes an auto effort paused because its pull request couldn't be opened THE SYSTEM SHALL only try to open the pull request again, running no stage, and IF it fails again keep it paused by FR-24. [human]
- **FR-40** WHEN the human resumes an auto effort stopped at its jury cap or stuck THE SYSTEM SHALL give the stopped gate 2 more rounds and raise the effort's jury cap by 2, recording both in history. [human]
- **FR-13** THE SYSTEM SHALL accept `[auto]` as the provenance of a spec item, which it doesn't today. [research: RF-2]
- **FR-14** THE SYSTEM SHALL let the spec gate pass with `[auto]` items once the spec jury has approved them, whether the auto flag is on or off; switching auto off reopens none of them. [human]
- **FR-15** WHILE the auto flag is on THE SYSTEM SHALL have the spec jury judge every `[auto]` default. [human]
- **FR-16** WHILE the auto flag is on, WHEN an epic is implemented THE SYSTEM SHALL run its epic jury and fix its confirmed blockers and majors by FR-9 before the next epic starts. [human]
- **FR-17** WHILE the auto flag is on, WHEN a jury round ends THE SYSTEM SHALL leave minor and refuted findings unfixed, accept them as the gate's risk in place of the human, and list them in the run report. [human]
- **FR-18** WHILE the auto flag is on and config sets no `budgets.juries` THE SYSTEM SHALL set the per-effort jury cap the stop list already enforces (flow-state FR-40) to 2 × the gates the effort's route runs: until the tasks are known, the route's gates before implementation (6 on the full route: spec, plan, tasks); then those plus one per epic. [human]
- **FR-19** IF config sets `budgets.juries` THEN THE SYSTEM SHALL use that value instead of FR-18's. [human]
- **FR-20** WHILE the auto flag is on, WHEN the effort reaches done THE SYSTEM SHALL open a pull request for the effort and stop. [human]
- **FR-21** THE SYSTEM SHALL never merge the pull request of an auto run. [human]
- **FR-22** WHEN the driver opens the pull request THE SYSTEM SHALL make its body the run report: each gate, what the jury found, what was auto-fixed, and every `[auto]` default chosen. [human]
- **FR-23** THE SYSTEM SHALL name, next to each auto approval, fix and `[auto]` default in the run report, the verdict record or history line that allowed it. [human]
- **FR-24** IF the pull request can't be opened THEN THE SYSTEM SHALL pause for the human, print the run report and keep the effort's commits, without retrying. [human]
- **FR-25** WHEN an auto effort pauses or is suspended THE SYSTEM SHALL stop the driver and tell the human the reason and the command that resumes it, in the "Talking to the human" shape. [agent]
- **FR-26** WHEN the human resumes or commits a paused auto effort THE SYSTEM SHALL carry the run on with the auto flag still on. [derived: FR-32]
- **FR-27** WHILE a jury round or test run is one the host moves to the background (the host decides when) THE SYSTEM SHALL have the driver start it in the background and wait for its completion notice, never polling; the manual skills keep #85 open. [human]
- **FR-28** WHILE the auto flag is on and the spec's `risk:` holds `money`, `data-deletion`, `migration` or `auth`, WHEN a gate's guard passes THE SYSTEM SHALL stop the driver until the human gives `--commit`. [human]
- **FR-29** IF a driver starts on an effort another driver is running THEN THE SYSTEM SHALL stop it without moving the effort. [human]
- **FR-30** IF auto is asked for by anyone but the human (`--by` other than `human`) THEN THE SYSTEM SHALL refuse it and leave the flag off. Every skill forbids an agent from passing `--by human`, and the grant's history line records the host and model of the call. [human]
- **FR-31** THE SYSTEM SHALL accept the grant of FR-1 at any stage from the end of drafting on, not only when the draft is written. [human]
- **FR-32** WHEN the human switches auto off THE SYSTEM SHALL turn the flag off and record it in history; a fix under way finishes its edits, and the next jury round waits for the human. [human]
- **FR-33** WHILE the auto flag is on and config sets no `budgets.subagents` THE SYSTEM SHALL cap no subagents; IF config sets it THEN THE SYSTEM SHALL suspend the run at that cap. [human]
- **FR-34** WHILE the auto flag is on, WHEN the jury's final fix check flags a fix that didn't hold THE SYSTEM SHALL pause for the human, naming the finding. [human]
- **FR-35** THE SYSTEM SHALL drive the lite route as well as the full route, each through its own stages. [human]

## Rules
### State table: Auto run (start: manual; final: pr_open)
| State | grant | stop fires | cap or stuck | human resumes | reaches done | switched off | PR fails | Src |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| manual | → running | ignore | ignore | ignore | ignore | ignore | ignore | [agent] |
| running | ignore | → waiting | → suspended | ignore | → pr_open | → manual | → pr_pending | [agent] |
| waiting | ignore | ignore | ignore | → running | reject: a waiting effort doesn't move | → manual | ignore | [agent] |
| suspended | ignore | ignore | ignore | → running | reject: a suspended effort doesn't move | → manual | ignore | [agent] |
| pr_pending | ignore | ignore | ignore | → pr_open | ignore | → manual | ignore | [human] |
| pr_open | ignore | ignore | ignore | ignore | ignore | ignore | ignore | [human] |

### Decision table: Fixer action on a finding
| Severity (blocker, major, minor) | Refuter (confirmed, refuted, none) | Fix touches a `[human]` line or cuts scope (yes, no) | → Action | Src |
| --- | --- | --- | --- | --- |
| blocker | confirmed | no | fix, then next round | [human] |
| blocker | confirmed | yes | pause for the human | [human] |
| major | confirmed | no | fix, then next round | [human] |
| major | confirmed | yes | pause for the human | [human] |
| blocker | refuted | - | accept; list first in the run report | [human] |
| blocker | none | - | pause for the human | [human] |
| major | none | - | pause for the human | [human] |
| major | refuted | - | accept; list in the run report | [human] |
| minor | - | - | accept; list in the run report | [human] |

## Key entities
- **Auto grant**: the history line that switched the flag on: who, when, at which stage. [human]
- **`[auto]` default**: a spec item the run chose in place of an open point, judged by the spec jury, listed in the report. [human]
- **Run report**: the pull request body: per gate, findings, fixes, `[auto]` defaults and the record that allowed each. [human]

## Non-functional requirements
- **NFR-2** THE SYSTEM SHALL let a new driver take over an effort after any interruption with no passed gate run twice. [agent]

## Success criteria
- **SC-1** An effort with a written spec reaches an open pull request with no message from the human in between when no stop fires. [derived: FR-5, FR-20]
- **SC-2** Every auto approval, fix and `[auto]` default in a run can be traced from the pull request body to the record that allowed it. [derived: FR-22]

## Non-goals
- Merging the pull request; the human always merges. [human]
- Granting auto through a `nio:auto` issue label; the command is the only grant. [human]
- Changing the stop list's rules (FR-39 to FR-42 of the flow-state spec) or the risky-flag rule (its FR-51); FR-18 only gives FR-40's `budgets.juries` a default value. [derived: FR-28]
- A notify channel beyond the pull request and the driver's stop message, such as the notify hook (#7). [derived: FR-22]
- A CLI loop (`nio flow run`) in place of the driver. [agent]

## Glossary
- **Auto run**: an effort with the auto flag on, driven from the grant to its pull request. Never "headless mode".
- **Driver**: the agent that loops `nio flow next`, the skill, `nio flow done`. Never "runner".
- **Fixer**: the agent that settles confirmed jury findings by editing the stage's files. Never "auto-fixer bot".
- **Run report**: the pull request body of an auto run. Never "summary".

## Risks and evidence against
- With no human in the loop, the jury and the fixer can agree on a spec the human wouldn't sign; the `[human]`-line guard, the scope-cut pause and the report are the only checks. [agent]
- The human-only grant rests on `--by human`, the same trust as gate approval with `--commit`: an agent that writes it anyway can grant auto. The skills forbid it, and the grant's history line records the host and model that ran it. [human]
- A driver that crashed holds the effort for up to 30 minutes, since its claim goes stale only by age (C-261108-mplt). [human]

## Decisions
- Auto runs wait on backgrounded commands by the completion notice, never polling (Q1).
- Only the human grants auto, at any stage from the end of drafting on, and can switch it off (Q2, Q3, Q4): D-261108-txqj.
- No `nio:auto` label; jury cap 6 until the tasks exist; no default subagent cap (Q5, Q6, Q7).
- Under auto, minors and refuted findings are accepted as the gate's risk; a fix that didn't hold pauses (Q8).
- Auto drives the lite route too (Q9).
- `[auto]` defaults stay accepted when auto is switched off (D-261108-fgeo); the report links every auto decision to its record; no PR means pause and print the report; no cap on the driver's context per stage (Q10–Q13).
- The flow stage is derived from the files and `nio flow done` records it, so the driver keeps no place of its own: D-261028-4kji (memory, 2026-10-28).
- The lite route runs spec, grill, tasks, tasks jury, implementation and implementation jury: D-261107-7egd (memory, 2026-11-07).


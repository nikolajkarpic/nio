---
slug: 2026-11-15-extensions
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [external-input, public-api, multi-party]  # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
apps: []                       # the apps this spec touches, when the project has docs per app
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, OP-10, OP-11, OP-12, OP-13, OP-14]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-15-extensions` checks all of this. -->
# Extensions: add flow steps, agent cards and event hooks without changing NIO, with a shipped e2e tester

## Summary
A project adds an extension (a folder with a manifest, skill, agent cards and templates) to put a new step into NIO's
flow, new agent cards and shell hooks on NIO events, without changing NIO. Today only agent cards can be extended and
the flow's steps are a fixed table in code, so a new step has nowhere to go. Extensions only add: no built-in step or
gate can be removed, reordered or skipped. The first extension, shipped and off by default, is a frontend e2e tester
that writes failing browser e2e tests from the spec's e2e ACs after the plan gate, which the implement stage then
makes pass. [human]

## Actors and journeys
- **A-1 Maintainer**: whoever installs NIO and owns the team's shared config; adds, lists and removes the repo's extensions for the whole team. P-3. [research: RF-1]
- **A-2 Effort owner**: drives an effort through the flow and meets an extension step at its spot, answering its gate when it has one. P-1. [research: RF-1]
- **A-3 Extension author**: a developer who writes an extension folder for their own or others' projects; knows the flow's step names and the shell, not NIO's code. no persona. [human]
- **A-4 Teammate**: pulls the repo and gets the committed extensions with it. P-2. [research: RF-1]
- **A-5 Driver**: the agent that runs the flow (`nio flow next`, the step's skill, `nio flow done`), by hand or under auto. [research: RF-2]
- **A-6 E2E tester**: the shipped extension's agent that writes browser e2e tests from the spec's e2e ACs. [human]

**UJ-1 Add an extension** (A-1, A-4) [agent]
1. The maintainer runs `nio extensions add` with a folder path, a git URL, or the name of a personal or shipped extension such as `e2e`.
2. NIO checks the manifest, refuses it if it breaks the add-only rule, copies it into the project's extensions without running any of its commands, and prints every check and hook command it brings.
3. The maintainer reads those commands and commits it; the commit is reviewed like any code, and teammates get it on their next pull.
- Misuse: adding an extension from an untrusted git URL whose hooks or check commands run harmful shell commands; hand-editing a copied extension to skip a gate.
- Evidence: #162, #9 (decisions 2026-11-15).

**UJ-2 Run an effort through an extension step** (A-2, A-5) [agent]
1. The flow passes the step the extension step names in `after`.
2. NIO checks the step's trigger rule; if it doesn't apply, the step is skipped on the record and the flow moves on.
3. If it applies, `nio flow next` names the step's skill; the driver runs it and calls `nio flow done`.
4. NIO runs the step's check command, then its jury gate if it declares one, and moves on only when both pass.
- Misuse: the driver claims the step is done while its check fails; an effort under auto passes an extension gate whose jury sent it to the human.
- Evidence: #162, #9.

**UJ-3 Write an extension** (A-3) [human]
1. The author writes a folder with a manifest, a skill, agent cards and templates, in the same format the shipped e2e extension uses.
2. The author adds it to a project and runs an effort through it.
- Misuse: a step placed where its inputs don't exist yet; a skill that relies on one host's tools.
- Evidence: #162 decisions 2 and 7.

**UJ-4 E2E tests from the spec** (A-1, A-5, A-6) [human]
1. The maintainer adds the shipped e2e extension.
2. After the plan gate, on a spec with an AC at `Level: e2e`, the e2e tester writes a failing browser e2e test per such AC.
3. The tasks name those tests, and the implement stage makes them pass.
- Misuse: tests that fail because the app never started rather than because the feature is missing; tests that pass before any code is written.
- Evidence: #162, #61.

## User stories

### US-1 Add, list and remove extensions (P1) [human]
- **Why this priority:** nothing else works until a project can hold an extension; it is the first item of "Done when".
- **Independent test:** add a minimal extension from a local folder, list it, remove it, and see each change in `.nio/extensions`.

- **AC-1** (FR-1) Given a valid extension folder on disk, when the maintainer runs `nio extensions add` with its path, then it is copied into `.nio/extensions` and its source and version are recorded. [human]
  Observable: `.nio/extensions` holds the extension's files; the recorded source is the path and the version is the manifest's. Level: integration.
- **AC-2** (FR-2) Given a git repository holding an extension, when the maintainer runs `nio extensions add` with its URL, then it is copied in with the URL and the fetched version recorded. [human]
  Observable: `.nio/extensions` holds the extension; the recorded source is the URL and the version names the fetched revision. Level: integration.
- **AC-3** (FR-3) Given the name of a shipped extension, when the maintainer runs `nio extensions add e2e`, then the shipped e2e extension is copied into `.nio/extensions`. [human]
  Observable: `.nio/extensions` holds the e2e extension; the recorded source names it as shipped, with NIO's version. Level: integration.
- **AC-4** (FR-4) Given an extension already added, when it is added again from a newer source, then it replaces the old copy and the new version is recorded. [human]
  Observable: one copy of the extension; the recorded version is the new one. Level: integration.
- **AC-5** (FR-5) Given a manifest with a missing or malformed field, when it is added, then the add is refused, names the field, and nothing is copied. [agent]
  Observable: non-zero exit; the message names the field; `.nio/extensions` is unchanged. Level: unit.
- **AC-6** (FR-6) Given two added extensions, when the maintainer runs `nio extensions list`, then each is shown with its source, version and the steps, cards and hooks it adds. [agent]
  Observable: the output has one entry per extension with those five facts. Level: integration.
- **AC-7** (FR-7) Given an added extension, when the maintainer runs `nio extensions remove` with its name, then it is gone from `.nio/extensions` and from the flow of efforts that haven't reached its step. [agent]
  Observable: the folder is gone; `nio flow status` of an effort before its spot no longer lists the step. Level: integration.
- **AC-8** (FR-8) Given an extension that exists only in NIO's shipped set, when no one has added it, then no effort's flow has its step. [human]
  Observable: `nio flow status` lists no e2e step on a project that didn't add it. Level: integration.

### US-2 The flow runs an extension step at its spot (P1) [human]
- **Why this priority:** a new step in the flow is the reason extensions exist (#9 decision 1); cards and hooks alone were already possible.
- **Independent test:** add an extension with one step after `plan_jury` whose check is `true`, run an effort through it, and see the step named next, passed and recorded.

- **AC-9** (FR-9, FR-13) Given an added extension step with `after: plan_jury` whose trigger rule applies, when the plan gate is approved, then `nio flow next` names the extension step's skill, not tasking. [human]
  Observable: `nio flow next` prints the extension step's skill; the effort's stage is the extension step. Level: integration.
- **AC-10** (FR-10) Given two extensions whose steps both name `after: plan_jury`, when the plan gate is approved, then their steps run in extension-name order, then tasking. [human]
  Observable: the history shows the alphabetically first extension's step passing before the second's, and tasking after both. Level: integration.
- **AC-11** (FR-11) Given a manifest whose step names in `after` a step that is neither built in nor in an added extension, when it is added, then the add is refused and names the unknown step. [agent]
  Observable: non-zero exit; the message names the unknown step; nothing is copied. Level: unit.
- **AC-12** (FR-12) Given an extension step whose trigger rule doesn't apply to the effort, when the flow reaches it, then it is skipped on the record with the trigger rule as the reason, and the flow moves on. [human]
  Observable: a history line marks the step skipped with the trigger text; the next stage is the built-in step that follows. Level: integration.
- **AC-13** (FR-14) Given an extension step whose trigger rule is "the spec has an AC at `Level: e2e`", when the spec has no such AC, then the step is skipped on the record; when it has one, the step runs. [human]
  Observable: two efforts, one per spec; one history shows the skip, the other the step as next. Level: integration.
- **AC-14** (FR-15) Given an extension step whose trigger rule is "the plan touches files under a path", when the plan names no file under that path, then the step is skipped on the record; when it names one, the step runs. [human]
  Observable: two efforts, one per plan; one history shows the skip, the other the step as next. Level: integration.
- **AC-15** (FR-16) Given an extension step whose check command exits 0, when the driver calls `nio flow done` on it, then the step passes and the flow moves on. [human]
  Observable: a pass line for the step in the history; the next stage is set. Level: integration.
- **AC-16** (FR-16, FR-17) Given an extension step whose check command exits non-zero, when the driver calls `nio flow done` on it, then the effort stays at the step and the exit code and the tail of the output are recorded. [human]
  Observable: the stage is unchanged; the recorded result holds the exit code and output tail. Level: integration.
- **AC-17** (FR-16) Given an extension step placed where its inputs don't exist yet, when the flow reaches it and it is called done, then it fails at its own check, not at add. [human]
  Observable: the add succeeds; `nio flow done` on the step exits non-zero with the check's output. Level: integration.
- **AC-18** (FR-18) Given an effort past an extension step, when `nio flow status` and the status pane show the effort, then the step appears at its spot, named with its extension, as passed or skipped. [agent]
  Observable: the stage list in `nio flow status` holds the step, labelled with the extension and step names, between the step it follows and the next one. Level: integration.
- **AC-19** (FR-19) Given an effort under auto at an extension gate, when the gate's jury approves, then the driver's `nio flow done` passes it; when the jury's outcome is `human` or a finding is held, then the flow waits for the human at that step. [agent]
  Observable: case one, a pass line by the driver naming the auto grant; case two, the status is waiting on the human at the extension step and no pass line by an agent. Level: integration.

### US-3 Built-in steps and gates can't be removed or skipped (P1) [human]
- **Why this priority:** gates are where autonomy is earned; an extension that skips one would undo the jury (#162 decision 6, "Done when").
- **Independent test:** try to add one extension per forbidden change and see each refused; hand-edit an added one and see the flow refuse to move.

- **AC-20** (FR-20) Given manifests that remove, reorder, skip or replace a built-in step or gate, when each is added, then every add is refused and names what it tried. [human]
  Observable: one test per kind of change; each exits non-zero, names the step or gate, and leaves `.nio/extensions` unchanged. Level: unit.
- **AC-21** (FR-21) Given an added extension edited by hand to skip a built-in gate, when the flow reads it, then the flow refuses to move any effort and names the extension. [agent]
  Observable: `nio flow next` exits non-zero naming the extension; no stage changes. Level: integration.
- **AC-22** (FR-22) Given an extension with a card named like a shipped card, when it is added, then the add is refused and names the card. [agent]
  Observable: non-zero exit; the message names the card; nothing is copied. Level: unit.

### US-4 An extension step can have its own jury gate (P2) [human]
- **Why this priority:** a step that writes artefacts the build rests on needs review like the built-in ones, but a check command alone covers many steps.
- **Independent test:** add an extension whose step declares a gate with one lens card, run an effort to it, and see the gate need approval before the flow moves on.

- **AC-23** (FR-23) Given an extension step that declares a jury gate with its lens cards, when its check passes, then the gate's jury runs with those lenses and the flow moves on only once the gate is approved like a built-in gate. [human]
  Observable: a jury ledger for the extension gate exists; the flow waits until its approval is recorded, then moves on. Level: integration.
- **AC-24** (FR-23) Given an extension gate rejected by its jury, when the flow reads the rejection, then the effort goes back to the extension step. [agent]
  Observable: the stage after the rejection is the extension step. Level: integration.

### US-5 Extension agent cards and hooks on NIO events (P2) [human]
- **Why this priority:** steps need their own cards, and hooks let a project run linters or notifiers on events; both are smaller than a new step.
- **Independent test:** add an extension with one card and one hook on `gate-approved`, sync the cards, approve a gate, and see the card rendered and the hook run.

- **AC-25** (FR-24) Given an added extension with an agent card, when `nio agents sync` runs, then the card is rendered for each host like a shipped card. [human]
  Observable: the rendered card file exists for each configured host. Level: integration.
- **AC-26** (FR-25, FR-27) Given an added extension with a hook on `gate-approved`, when a gate is approved, then the hook's command runs once and its exit code is recorded. [human]
  Observable: the hook's side effect (a file it writes) exists; the effort's record holds the hook's exit code. Level: integration.
- **AC-27** (FR-25) Given two extensions with hooks on the same event, when the event fires, then the hooks run in extension-name order. [agent]
  Observable: the hooks' side effects carry the order of their runs. Level: integration.
- **AC-28** (FR-26) Given a manifest with a hook on an event NIO doesn't fire, when it is added, then the add is refused and names the event and the known ones. [agent]
  Observable: non-zero exit; the message lists the known events. Level: unit.

### US-6 The shipped e2e tester (P2) [human]
- **Why this priority:** it is the first real extension and proves the format; it needs US-1 to US-3 first.
- **Independent test:** in a sample frontend project, add the e2e extension, run a spec with one e2e AC to the implement stage, and see a failing e2e test written, then passing after implement.

- **AC-29** (FR-28, FR-29) Given a project that added the e2e extension and a spec with ACs at `Level: e2e`, when the plan gate is approved, then the e2e tester writes one browser e2e test per such AC, each naming its AC. [human]
  Observable: one test per e2e AC exists, each citing its AC ID. Level: e2e.
- **AC-30** (FR-30) Given the e2e tests just written, when the e2e step's check runs before any implementation, then it passes only if every e2e AC has a test and every test fails because the feature is missing. [human]
  Observable: the check exits 0 with all tests failing on assertions; it exits non-zero when one AC has no test or one test passes. Level: integration.
- **AC-31** (FR-30, FR-32) Given an e2e run where the app doesn't start, when the check runs, then it fails as a setup error, not as a failing test. [agent]
  Observable: the check's output says the app didn't start; the run isn't counted as a failing test. Level: integration.
- **AC-32** (FR-31) Given the approved tasks after the e2e step, when an epic covers an e2e AC, then its tasks name that AC's e2e test, so the epic's test run includes it. [human]
  Observable: `tasks.md` lists the e2e test under the task covering the AC; the epic's closing run includes it. Level: integration.
- **AC-33** (FR-31) Given an epic whose e2e test fails, when the agent hands it back as done, then the epic stays open as with any failing test. [human]
  Observable: the epic is not closed; the recorded result names the e2e test. Level: integration.
- **AC-34** (FR-32) Given the project's Playwright config naming the app's start command and ready address, when an e2e run starts, then the app is started, the run waits until it answers, and the app is stopped afterwards, pass or fail. [agent]
  Observable: no app process is left running after the run. Level: integration.
- **AC-35** (FR-33) Given a failing e2e test, when the run ends, then its trace and screenshots are kept in the runner's output folder and the output says where. [agent]
  Observable: the named trace and screenshot files exist under the runner's output folder; the e2e extension adds no committed file for them. Level: integration.
- **AC-36** (FR-34) Given an effort with e2e tests at the pr gate, when the pr jury gets its evidence, then the e2e run's result is in it. [agent]
  Observable: the pr gate's evidence lists the e2e tests and their results. Level: integration.
- **AC-37** (FR-35) Given the NIO code and the shipped e2e extension, when they are searched, then no NIO code names the e2e extension, and its manifest passes the same checks as any user's. [human]
  Observable: a test finds no reference to the e2e extension outside its folder and its own tests; `nio extensions add e2e` runs the user-facing checks. Level: unit.
- **AC-38** (FR-36) Given every shipped extension skill, when they are checked, then they name no host-only tool and carry the "Talking to the human" block. [agent]
  Observable: `tests/test_talk.py` covers extension skills; a check finds none of the host-only tool names. Level: unit.
- **AC-39** (FR-37) Given an extension whose manifest has a check command and a hook, when it is added, then neither command runs and the output lists both. [agent]
  Observable: a file each command would write doesn't exist after the add; the add's output holds both commands. Level: integration.
- **AC-41** (FR-38) Given an added extension whose check command is edited by hand after the add, when the flow reads it, then the flow refuses to move any effort, names the extension and says to add it again. [agent]
  Observable: `nio flow next` exits non-zero naming the extension; no stage changes; after `nio extensions add` again it moves. Level: integration.
- **AC-42** (FR-39) Given extension B whose step follows a step of extension A, when the maintainer removes A or adds a version of A without that step, then it is refused and names B's step; given a manifest whose step or card name another added extension already uses, when it is added, then it is refused and names it. [agent]
  Observable: non-zero exit naming the step or card; `.nio/extensions` unchanged. Level: unit.
- **AC-43** (FR-40) Given a manifest whose step has the trigger "the plan touches files under a path" and `after: spec_jury`, when it is added, then the add is refused and names the trigger and the step; with `after: plan_jury` it is copied. [agent]
  Observable: non-zero exit naming both in the first case; the extension in `.nio/extensions` in the second. Level: unit.
- **AC-44** (FR-7) Given an effort sitting at an extension's step, when the maintainer removes the extension, then the remove is refused and names the effort; given an effort past the step, when the extension is removed or replaced by a version without the step, then the effort's stage and its history lines are unchanged. [agent]
  Observable: case one, non-zero exit naming the effort and the folder still there; case two, `state.json` stage and `history.jsonl` byte-equal before and after. Level: integration.
- **AC-45** (FR-41) Given e2e tests that fail on a Playwright web-first assertion (`expect(page)` or `expect(locator)`) with the app started, when the e2e check runs, then they count as failing because the feature is missing; given a test with a syntax error, an import error, a timeout outside an assertion, or a failing assertion that reads no page (such as `expect(true).toBe(false)`), then the check fails and names that test. [agent]
  Observable: one fixture per case; the first exits 0, each other exits non-zero naming the test and its reason. Level: integration.
- **AC-46** (FR-18) For NFR-1: given three added extensions each with a step, a card and a hook, when `NIO_PERF=1 uv run python tests/test_flow.py` runs, then it passes the same limit as with none. [agent]
  Observable: the perf check exits 0 with the three extensions in place. Level: integration.
- **AC-47** (FR-16, FR-27) For NFR-2: given a hook and a check command with a manifest timeout of 1 second that each run `sleep 5`, when they run, then each is stopped and recorded as failed with "timed out"; given a timeout that isn't a whole number of seconds of at least 1, when the manifest is added, then the add is refused naming the field. [agent]
  Observable: each record says timed out within 5 seconds; no command still running; the add of the bad timeout exits non-zero naming it. Level: integration.
- **AC-48** (FR-8) For NFR-3: given a project with no extensions added, when the existing flow tests run, then they pass unchanged. [agent]
  Observable: `uv run python tests/test_flow.py` passes with no edit to its expected stages, history or status output. Level: integration.
- **AC-40** (FR-27) Given an added extension whose hook on `step-passed` exits non-zero, when a step passes, then the failure is recorded and the effort moves on. [agent]
  Observable: the effort's record holds the hook's non-zero exit code; the next stage is set as without the hook. Level: integration.

## Functional requirements
- **FR-1** WHEN `nio extensions add` is given a folder path holding a valid extension THE SYSTEM SHALL copy it into the project's `.nio/extensions` and record its source and version. [human]
- **FR-2** WHEN `nio extensions add` is given a git URL THE SYSTEM SHALL fetch the extension from it, copy it into `.nio/extensions`, and record the URL and the fetched version. [human]
- **FR-3** WHEN `nio extensions add` is given the name of a shipped extension THE SYSTEM SHALL copy the shipped extension into `.nio/extensions` and record it as shipped with NIO's version. [human] A name found in the person's `~/.nio/extensions` is copied from there first, and recorded with that folder as its source. [agent]
- **FR-4** WHEN an extension already in `.nio/extensions` is added again THE SYSTEM SHALL replace the old copy and record the new source and version. [human]
- **FR-5** IF an extension's manifest is missing, unreadable, or lacks a required field THEN THE SYSTEM SHALL refuse the add, name the field, and copy nothing. [agent]
- **FR-6** WHEN `nio extensions list` runs THE SYSTEM SHALL print each added extension with its source, version, and the steps, cards and hooks it adds. [agent]
- **FR-7** WHEN `nio extensions remove` is given an added extension's name THE SYSTEM SHALL delete it from `.nio/extensions`, so efforts that haven't reached its step no longer have it; it refuses the remove, naming the effort, while an effort sits at one of its steps; history lines of the removed step stay as written, and an effort past a removed or replaced step is not sent back. [agent]
- **FR-8** THE SYSTEM SHALL treat an extension as active only once it is in the project's `.nio/extensions`; a shipped extension stays off until added. [human]
- **FR-9** WHEN the flow passes the step an active extension step names in `after` THE SYSTEM SHALL make that extension step the next stage, before the step that would follow without it. [human]
- **FR-10** WHEN two or more extension steps name the same `after` step THE SYSTEM SHALL run them in extension-name order, and the steps of one extension in manifest order. [human]
- **FR-11** IF a manifest's step names in `after` a step that is neither built in nor a step of an added extension THEN THE SYSTEM SHALL refuse the add and name that step. [agent]
- **FR-12** WHEN the flow reaches an extension step whose trigger rule doesn't apply to the effort THE SYSTEM SHALL skip it on the record with the trigger rule as the reason and move to the next stage. [human]
- **FR-13** WHEN the flow reaches an extension step whose trigger rule applies THE SYSTEM SHALL name the step's skill as the next thing to run. [human]
- **FR-14** THE SYSTEM SHALL support the trigger rule "the spec has an AC at a named `Level`". [human]
- **FR-15** THE SYSTEM SHALL support the trigger rule "the plan touches files under a named path". [human]
- **FR-16** WHEN `nio flow done` is called on an extension step THE SYSTEM SHALL run the step's check command and pass the step only when it exits 0. [human]
- **FR-17** IF an extension step's check command exits non-zero THEN THE SYSTEM SHALL keep the effort at that step and record the exit code and the tail of its output. [agent]
- **FR-18** WHEN `nio flow status`, `nio flow next` or the status pane show an effort THE SYSTEM SHALL show each extension step at its spot, labelled with its extension and step names, and its state. [agent]
- **FR-19** WHILE an effort is under auto THE SYSTEM SHALL apply the same stop rules to extension steps and gates as to built-in ones, so an extension gate is treated as the spec, plan and tasks gates are: the driver's `nio flow done` approves it once its jury approved, and the flow waits for the human when its jury's outcome is `human` or a finding is held. [agent]
- **FR-20** IF a manifest removes, reorders, skips or replaces a built-in step or gate THEN THE SYSTEM SHALL refuse the add and name the step or gate. [human]
- **FR-21** IF an extension in `.nio/extensions` breaks the add-only rule when the flow reads it THEN THE SYSTEM SHALL refuse to move any effort and name the extension. [agent]
- **FR-22** IF an extension's agent card has the name of a shipped card THEN THE SYSTEM SHALL refuse the add and name the card. [agent]
- **FR-23** WHEN an extension step that declares a jury gate passes its check THE SYSTEM SHALL run that gate with the extension's lens cards and move on only once the gate is approved as the built-in gates are; a rejection sends the effort back to the step. [human]
- **FR-24** WHEN `nio agents sync` runs THE SYSTEM SHALL render the agent cards of every added extension for each host, as it does shipped cards. [human]
- **FR-25** WHEN a NIO event fires THE SYSTEM SHALL run each shell hook that added extensions register on it, in extension-name order. [human]
- **FR-26** THE SYSTEM SHALL fire the events `step-passed`, `step-skipped`, `gate-approved`, `gate-rejected`, `epic-closed`, `waiting-on-human` and `effort-done`, and refuse a manifest hook on any other. [agent]
- **FR-27** WHEN a hook runs THE SYSTEM SHALL record its extension, event, exit code and the tail of its output in the effort's record; a failing hook never stops or blocks the flow. [agent]
- **FR-28** THE SYSTEM SHALL ship an e2e extension whose step comes after `plan_jury` and whose trigger rule is "the spec has an AC at `Level: e2e`". [human]
- **FR-29** WHEN the e2e step runs THE SYSTEM SHALL have the e2e tester write one browser e2e test per AC at `Level: e2e`, each naming its AC. [human]
- **FR-30** WHEN the e2e step's check runs THE SYSTEM SHALL pass only if every e2e AC has a test and every such test fails on its assertions, not on setup. [human]
- **FR-31** WHEN tasks are written after the e2e step THE SYSTEM SHALL require each task covering an e2e AC to name that AC's e2e test, so the implement stage makes it pass. [human]
- **FR-32** WHEN an e2e run starts THE SYSTEM SHALL run the tests with Playwright, whose config in the project names the app's start command and ready address, so the app is started, waited for until it answers, and stopped whatever the result. [agent]
- **FR-33** WHEN an e2e test fails THE SYSTEM SHALL keep its trace and screenshots in the runner's output folder, uncommitted and replaced by the next run, and print where they are. [agent]
- **FR-34** WHEN the pr gate's evidence is gathered for an effort with e2e tests THE SYSTEM SHALL include the e2e run's results. [agent]
- **FR-35** THE SYSTEM SHALL build the shipped e2e extension only from the user-facing extension format, with no NIO code that names it. [human]
- **FR-36** THE SYSTEM SHALL keep every shipped extension's skill plain markdown that names no host-only tool and carries the "Talking to the human" block. [agent]
- **FR-37** WHEN `nio extensions add` copies an extension THE SYSTEM SHALL run none of its commands and print every check and hook command it brings. [agent]
- **FR-38** IF an added extension's files differ from what `nio extensions add` recorded THEN THE SYSTEM SHALL refuse to move any effort, name the extension and say to add it again, so a hand edit is reviewed like an add. [agent]
- **FR-39** IF removing or replacing an extension would take away a step another added extension's step names in `after`, or a manifest's step or card name is already used by another added extension, THEN THE SYSTEM SHALL refuse it and name that step or card. [agent]
- **FR-40** IF a step's trigger rule reads an input that doesn't exist yet at its `after` step (the plan before `plan_jury` has passed) THEN THE SYSTEM SHALL refuse the add and name the trigger and the step. [agent]
- **FR-41** THE SYSTEM SHALL count an e2e test as failing because the feature is missing only when Playwright reports it failed on a web-first assertion (`expect(page)` or `expect(locator)`) with the app started; any other failure is a setup error that fails the e2e check and names the test. [agent]

## Rules
### State table: Extension step (start: reached; final: passed, skipped)
| State | trigger applies | trigger doesn't apply | flow done | check exits 0 | check exits non-zero | gate approved | gate rejected | Src |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reached | → active | → skipped | reject: the trigger rule isn't checked yet | ignore | ignore | ignore | ignore | [human] |
| active | ignore | ignore | → checking | ignore | ignore | ignore | ignore | [human] |
| checking | ignore | ignore | ignore | → judging | → active | ignore | ignore | [human] |
| judging | ignore | ignore | ignore | ignore | ignore | → passed | → active | [human] |
| passed | ignore | ignore | ignore | ignore | ignore | ignore | ignore | [human] |
| skipped | ignore | ignore | ignore | ignore | ignore | ignore | ignore | [human] |

`judging` passes through at once to `passed` for a step that declares no jury gate. [human]

### Decision table: Extension step outcome
| trigger applies (yes, no) | check passes (yes, no) | declares gate (yes, no) | gate approved (yes, no) | → outcome | Src |
| --- | --- | --- | --- | --- | --- |
| no | - | - | - | skipped on the record | [human] |
| yes | no | - | - | stays at the step, check output recorded | [human] |
| yes | yes | no | - | passed | [human] |
| yes | yes | yes | yes | passed | [human] |
| yes | yes | yes | no | back to the step | [agent] |

### Decision table: Add refused
| manifest valid (yes, no) | touches a built-in step or gate (yes, no) | after names a known step (yes, no) | card, step or hook clashes (yes, no) | → add | Src |
| --- | --- | --- | --- | --- | --- |
| no | - | - | - | refused, names the field | [agent] |
| yes | yes | - | - | refused, names the step or gate | [human] |
| yes | no | no | - | refused, names the unknown step | [agent] |
| yes | no | yes | yes | refused, names the card, step or event | [agent] |
| yes | no | yes | no | copied and recorded | [human] |

## Key entities
- **Extension**: a folder with a manifest, a skill per step, agent cards and templates; lives in NIO's shipped set, `~/.nio/extensions` or the project's `.nio/extensions`. [human]
- **Manifest**: the extension's JSON description: name, version, steps, cards and hooks, in the same style as `.nio/config.json`. [research: RF-12]
- **Extension step**: a step an extension adds: its skill, agent card, output file, `after` step, trigger rule, check command and optional jury gate with lens cards. [human]
- **Trigger rule**: when an extension step applies to an effort; otherwise it is skipped on the record. [human]
- **Hook**: a shell command an extension runs on a NIO event. [human]
- **Extension record**: the source (path, git URL or shipped) and version of each added extension. [human] It also holds a hash of the copied files (FR-38). [agent]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL keep `nio flow status` within its current speed limit (the `NIO_PERF=1` check) with three extensions added. [agent]
- **NFR-2** THE SYSTEM SHALL stop a hook or check command that runs longer than its timeout, 300 seconds unless the manifest sets another, and record it as failed. [agent]
- **NFR-3** THE SYSTEM SHALL leave the flow, history and status of an effort unchanged in a project with no extensions added. [agent]

## Success criteria
- **SC-1** A project adds, lists and removes an extension, and an effort runs an extension step at its spot, skipped on the record when its trigger rule doesn't apply and guarded by its check (and jury, if declared). [human]
- **SC-2** The shipped e2e extension writes failing e2e tests from a spec's e2e ACs after the plan gate, and implement makes them pass, on a sample frontend project. [human]
- **SC-3** A test proves no extension can remove or skip a built-in gate. [human]
- **SC-4** An author writes a working extension step without changing any file under `src/nio/`. [agent]

## Non-goals
- Removing, reordering, skipping or replacing built-in steps or gates; that needs a change to NIO itself. [human]
- Overriding a shipped agent card through an extension; a project still does that by name in `.nio/agents` (#24). [human]
- Host plugins as the extension format; they would tie extensions to one host. [human]
- An extension catalog or registry; extensions come from a path, a git URL, the person's `~/.nio/extensions` or NIO's shipped set. [agent]
- Cypress or other browser runners beyond Playwright. [agent]
- A frontend worker card or design inputs (designs, components) for frontend tasks (#61). [agent]

## Glossary
- **Extension**: a folder that adds flow steps, agent cards and hooks to NIO without changing it. Never "add-on".
- **Extension step**: a flow step an extension adds after a named step. Never "custom stage".
- **Trigger rule**: when an extension step applies to an effort. Never "precondition".
- **Hook**: a shell command an extension runs on a NIO event. Never "callback". Not the git hooks `nio hooks` installs; where both could be meant, say "event hook".

## Decisions
- Implementation is per epic, with the flow running the epic's tests at its end and no per-task red/green: D-261115-cf65 (grill, 2026-11-15).
- Delegated grill (2026-11-15, the human: "take recommended answers for all questions"): every call below is the agent's, tagged [agent], for the human's review at the spec gate (grill.md Q1 to Q8).
- `nio extensions add` runs nothing and prints every command an extension brings; the commit is the review; a failing hook only reports (FR-27, FR-37): D-261115-ggt2 (grill Q1, Q2).
- `~/.nio/extensions` is only a source for `nio extensions add`; only `.nio/extensions` is active (FR-3, FR-8) (grill Q3).
- Removing or replacing an extension leaves past history lines as written and sends no effort back; it is refused while an effort sits at its step or another extension's step follows one it takes away (FR-7, FR-39) (grill Q4; spec jury round 1).
- E2E runs use Playwright only; its own config starts, waits for and stops the app, and its output folder keeps traces, uncommitted (FR-32, FR-33) (grill Q5, Q6, Q7).
- Under auto an extension gate is approved like the spec, plan and tasks gates, and waits for the human when its jury does (FR-19) (grill Q8).
- One spec, not an epic of slices: the intake's "Done when" asks for the format and the shipped e2e extension together, since the e2e extension proves the format; the tasks stage orders the work as epics (US-1 to US-3 first, then US-4 and US-5, then US-6) (spec jury round 1, J-16; delegated by the human, 2026-11-15, recommended option).

## Open points

---
slug: 2026-10-28-plan-jury
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [FR-7, OP-1, OP-4, OP-9, OP-10, OP-7, OP-11, OP-5, OP-6, OP-2, OP-12, OP-3, OP-8]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-10-28-plan-jury` checks all of this. -->
# Plan jury: build the plan gate, with test-proof and architecture-fit lenses, `nio check plan` as its precondition, a `Like:` line on new contracts and a plan-fix disposition

## Summary
The plan stage shipped, but its gate can't run: `nio jury plan <slug> plan` refuses because only the spec gate is
built, and the tasks stage needs an approved plan before it starts. This builds the plan gate (#57): `nio check plan
--gate` as its precondition, two new core lenses (test-proof: would each planned test fail if its AC broke;
architecture fit: does the plan fit the existing code, its rules and the architecture), the triggered lenses, a
`Like:` line that ties each new contract to the existing code it copies, a `plan-fix` disposition with spec-rooted
findings sent back to the spec as change requests, and a `nio: approve plan` that the tasks stage reads. [human]

## Actors and journeys
- **A-1 Human**: owns the project; asks for the plan jury after `@nio:plan`, settles what the jury can't, and approves the plan. [human]
- **A-2 Jury skill**: the agent running `@nio:jury`; plans the gate with `nio jury plan`, starts the jurors and the refuter, and applies dispositions. [research: RF-1]
- **A-3 Plan-gate juror**: a lens subagent (test-proof, architecture fit, or a triggered lens) that reads its pack in a fresh context and returns at most 5 findings. [human]
- **A-4 Tasks stage**: the next stage, which may start only on an approved plan. [human]

**UJ-1 Judge a plan before tasks** (A-1, A-2, A-3) [research: RF-2]
1. `@nio:plan` finishes and says the next stage is the plan jury.
2. The jury skill runs `nio jury plan <slug> plan`, which runs `nio check plan <slug> --gate` and lists the lenses with the reason each runs.
3. The jurors review the four plan files; the refuter checks their findings; the CLI composes the outcome.
4. Findings are fixed in the plan, or sent back to the spec; once the gate approves, the human records `nio: approve plan`.
- Misuse: the plan's own author reviews it in the same session and calls that the gate; or a juror reads only `plan.md`.
- Evidence: issue #57 and its research comment (spec-kit, BMAD, GSD, cc-sdd).

**UJ-2 A plan finding comes from the spec** (A-1, A-2) [human]
1. A juror's finding is rooted in the approved spec, not in the plan.
2. The jury skill proposes it as spec-rooted; once the human confirms, it becomes a change request: the spec is edited and the spec jury re-checks only the changed items.
3. The plan jury resumes.
- Misuse: the plan fills the spec's gap with detail of its own instead of going back to the spec.
- Evidence: issue #57, decision 2 (cc-sdd's rule).

## User stories

### US-1 Plan and run the plan gate (P1) [human]
- **Why this priority:** without it the plan stage has no gate and the tasks stage can never start on a plan.
- **Independent test:** run `nio jury plan <slug> plan` on fixture plans with and without state, risk flags and a passing check, and read the lens list.

- **AC-1** (FR-1, FR-3) Given a spec with no risk flags whose plan passes `nio check plan --gate` and has no contract with a `State:` line and no `## Data model` section, when `nio jury plan <slug> plan` runs, then it plans the two core lenses. [human]
  Observable: exit 0; the lens line lists `test-proof (core)` and `architecture-fit (core)` and nothing else; no "only the spec gate" error. Level: unit.
- **AC-2** (FR-2) Given a plan that fails `nio check plan <slug> --gate`, when `nio jury plan <slug> plan` runs, then no lens is planned. [human]
  Observable: non-zero exit; the output names `nio check plan <slug> --gate` and its error count, and lists no lens. Level: unit.
- **AC-3** (FR-2) Given a spec that fails `nio check spec --gate` but a plan that passes `nio check plan --gate`, when the plan gate is planned, then the spec check is not what decides it. [derived: FR-2]
  Observable: the output holds no line about `nio check spec`; the lenses are planned. Level: unit.
- **AC-4** (FR-4, FR-8) Given a plan where CT-2 has a `State:` line, when the plan gate is planned, then logic runs with its reason. [research: RF-6]
  Observable: the lens line holds `logic` with a reason naming state. Level: unit.
- **AC-5** (FR-4) Given a plan where no contract has a `State:` line, when the plan gate is planned, then logic does not run. [research: RF-6]
  Observable: `logic` is not in the lens line. Level: unit.
- **AC-6** (FR-5, FR-8) Given a spec with `risk: [pii]`, when the plan gate is planned, then security runs with its reason. [derived: FR-5]
  Observable: the lens line holds `security (risk: pii)`. Level: unit.
- **AC-46** (FR-44, FR-40) Given the shipped agent cards, when they are listed, then `risk-rollback` exists with an `## At plan` section. [human]
  Observable: `src/nio/agents/risk-rollback.md` passes the card check, has `tier: max` and `effort: med`, and has the heading `## At plan`. Level: unit.
- **AC-47** (FR-45) Given the shipped security card, when it is read, then it has an `## At plan` section next to `## At spec`. [human]
  Observable: both headings are in `src/nio/agents/security.md`; the card passes the card check. Level: unit.
- **AC-48** (FR-6, FR-8) Given a spec with no risk flags whose `contracts.md` has a `## Data model` section, when the plan gate is planned, then risk-rollback runs with its reason. [human]
  Observable: the lens line holds `risk-rollback` with a reason naming the data model. Level: unit.
- **AC-53** (FR-5, FR-8) Given a spec with `risk: [auth]`, when the plan gate is planned, then security runs with its reason. [derived: FR-5]
  Observable: the lens line holds `security (risk: auth)`. Level: unit.
- **AC-54** (FR-6, FR-8) Given a spec with `risk: [data-deletion]`, when the plan gate is planned, then risk-rollback runs with its reason. [derived: FR-6]
  Observable: the lens line holds `risk-rollback (risk: data-deletion)`. Level: unit.
- **AC-7** (FR-6, FR-9) Given a spec with `risk: [migration]` and no risk-rollback card, when the plan gate is planned, then the gate is blocked naming the missing card. [human]
  Observable: non-zero exit; the output lists the risk-rollback lens with `risk: migration` and says the gate is blocked until its card exists. Level: unit.
- **AC-8** (FR-11) Given a plan gate that has run, when its ledger is read, then it is the plan gate's own ledger. [research: RF-8]
  Observable: `.nio/specs/<slug>/jury/plan.json` and `plan.md` exist; `.nio/specs/<slug>/jury/spec.json` is unchanged. Level: integration.
- **AC-9** (FR-10) Given a plan-gate juror's pack, when it is built, then it holds all four plan files. [human]
  Observable: the pack holds `plan.md`, `contracts.md`, `tests.md` and `quickstart.md`. Level: unit.
- **AC-44** (FR-42) Given a plan-gate finding quoting a line of the file CT-2 binds, and another quoting a file no contract binds, when they are collected, then the first is kept and the second dropped. [human]
  Observable: the ledger holds the first finding; the collect output names the second as not grounded. Level: unit.
- **AC-45** (FR-43) Given a plan whose contracts bind `src/a.py` and name `src/b.py` on a `Like:` line, when the plan gate's juror files are listed, then they hold the plan files, the spec, CLAUDE.md, `src/a.py` and `src/b.py`. [derived: FR-43, FR-42]
  Observable: the listed files are exactly those, plus `architecture.md` when it exists. Level: unit.
- **AC-10** (FR-12) Given a plan-gate lens output with 6 findings, when it is collected, then it is invalid, as at the spec gate. [human]
  Observable: the collect error says a lens returns at most 5 findings. Level: unit.
- **AC-11** (FR-13) Given `@nio:plan` has finished and the human asks for the plan jury, when the jury skill starts, then it runs the plan gate. [derived: FR-1, RF-1]
  Observable: the skill runs `nio jury plan <slug> plan`, not the spec gate. Level: e2e.

### US-2 The test-proof lens asks whether each planned test would catch a broken AC (P1) [human]
- **Why this priority:** a core lens; no tool reviewed checks this, and a plan whose tests can't fail proves nothing.
- **Independent test:** run the test-proof juror on fixture plans with known weak tests and read its findings.

- **AC-12** (FR-14, FR-15, FR-40) Given the shipped agent cards, when they are listed, then `test-proof` exists with an `## At plan` section. [human]
  Observable: `src/nio/agents/test-proof.md` passes the card check, has `tier: max` and `effort: med`, and has the heading `## At plan`. Level: unit.
- **AC-13** (FR-15) Given a plan with TC-1 whose `Assert:` checks an exact returned value, when test-proof reviews it, then its reasoning names a concrete bug for AC-1 and the `Assert:` line that fails on it. [human]
  Observable: the lens output's reasoning for TC-1 names one changed line of the code TC-1's contract binds (e.g. a flipped condition) and quotes TC-1's `Assert:` line. Level: e2e.
- **AC-14** (FR-16) Given TC-2 whose `Assert:` only checks that the command didn't throw, when test-proof reviews it, then it raises a finding on TC-2. [human]
  Observable: one finding citing TC-2 and its AC, kind `untestable`, quoting the `Assert:` line. Level: e2e.
- **AC-15** (FR-16) Given TC-3 that mocks away the integration its AC is about, when test-proof reviews it, then it raises a finding on TC-3. [human]
  Observable: one finding citing TC-3, quoting its `Setup:` or `Action:` line naming the mock. Level: e2e.
- **AC-16** (FR-17) Given TC-4 whose expected value is computed the same way as the code under test, when test-proof reviews it, then it raises a finding on TC-4. [human]
  Observable: one finding citing TC-4 that says the expected value has no independent source. Level: e2e.
- **AC-17** (FR-18) Given TC-5 whose AC already holds on today's code (the bound function already returns the expected value), when test-proof reviews it, then it raises a finding that TC-5 would pass before any work, without running any test. [human]
  Observable: one finding citing TC-5 and quoting the bound code; the test-proof card's tools are read-only (`tools: [read]`), so it can't run a test. Level: e2e.
- **AC-18** (FR-19) Given TC-6, filed under US-1's build-order entry, whose AC only US-2's contracts can satisfy, when test-proof reviews it, then it raises a finding on TC-6. [human]
  Observable: one finding citing TC-6 and naming US-2. Level: e2e.
- **AC-19** (FR-20) Given an AC whose test exists in the repo but isn't listed in `tests.md`, when test-proof reviews the plan, then it raises no "test missing" finding without having searched the repo. [human]
  Observable: any finding saying a test is missing names where it searched; none is raised for the AC whose test exists. Level: e2e.

### US-3 The architecture-fit lens asks whether the plan fits the code and its rules (P1) [human]
- **Why this priority:** a core lens; a plan that contradicts the existing code or the project's rules costs most to undo once tasks are cut.
- **Independent test:** run the architecture-fit juror on fixture plans with known misfits and read its findings.

- **AC-20** (FR-21, FR-22, FR-40) Given the shipped agent cards, when they are listed, then `architecture-fit` exists with an `## At plan` section. [human]
  Observable: `src/nio/agents/architecture-fit.md` passes the card check, has `tier: max` and `effort: med`, and has the heading `## At plan`. Level: unit.
- **AC-21** (FR-22) Given new contract CT-3 whose `Like:` names `src/nio/jury.py:plan` but whose shape follows a different pattern, when architecture-fit reviews it, then it raises a finding on CT-3. [human]
  Observable: one finding citing CT-3 and quoting its `Like:` line. Level: e2e.
- **AC-22** (FR-23) Given a project rule "Never commit without the human asking" and a contract that commits on its own, when architecture-fit reviews the plan, then it raises a finding quoting that rule. [human]
  Observable: one finding citing the contract, kind `contradiction`, quoting the rule word for word. Level: e2e.
- **AC-23** (FR-24) Given a new contract that a build-order entry delivers and that cites an FR, but that no other contract and no existing code calls, when architecture-fit reviews it, then it raises a finding that the component is an orphan. [derived: FR-24, RF-5]
  Observable: one finding citing the contract. Level: e2e.
- **AC-24** (FR-25) Given a new module whose contract cites FR-2, which doesn't need it, and no row in `## Complexity tracking`, when architecture-fit reviews the plan, then it raises a finding on it. [derived: FR-25, RF-5]
  Observable: one finding citing the contract and FR-2, kind `scope`. Level: e2e.
- **AC-25** (FR-26) Given a build-order entry for US-2 with nothing that can be shown when it is done, when architecture-fit reviews the plan, then it raises a finding on US-2. [human]
  Observable: one finding citing US-2 that asks what can be shown when it is done. Level: e2e.
- **AC-26** (FR-27) Given two contracts that give the same input different limits, when architecture-fit reviews the plan, then it raises a finding citing both. [human]
  Observable: one finding, kind `inconsistency`, citing both CT IDs. Level: e2e.

### US-4 New contracts name the existing code they copy (P1) [human]
- **Why this priority:** it turns "fits the existing code" into something checked for free, and gives architecture fit a concrete thing to judge.
- **Independent test:** run `nio check plan` on fixture contracts with and without `Like:` lines.

- **AC-27** (FR-28, FR-29) Given CT-2 bound `(new)` with no `Like:` line, when `nio check plan` runs, then it fails naming CT-2. [derived: FR-28]
  Observable: non-zero exit; the error names CT-2 and `Like`. Level: unit.
- **AC-49** (FR-28) Given CT-5 bound `(new)` with `Like: none: first HTTP endpoint in the project`, and CT-6 with `Like: none` and no reason, when `nio check plan` runs, then only CT-6 is an error. [human]
  Observable: one error, naming CT-6 and the missing reason. Level: unit.
- **AC-50** (FR-46) Given CT-5 with `Like: none: first parser` while the repo already has a parser, when architecture-fit reviews it, then it raises a finding naming the existing parser. [human]
  Observable: one finding citing CT-5, quoting its `Like:` line and naming the existing file. Level: e2e.
- **AC-28** (FR-30) Given CT-2 with `Like: src/nio/nope.py:thing` and no such file, when `nio check plan` runs, then it fails. [human]
  Observable: non-zero exit; the error names CT-2 and `src/nio/nope.py`. Level: unit.
- **AC-29** (FR-30) Given CT-2 with `Like: src/nio/jury.py:no_such_symbol`, when `nio check plan` runs, then it fails. [human]
  Observable: non-zero exit; the error names CT-2 and `no_such_symbol`. Level: unit.
- **AC-30** (FR-28, FR-30) Given CT-2 with `Like: src/nio/jury.py:plan`, when `nio check plan` runs with no network and no model, then CT-2 raises no error. [human]
  Observable: no error naming CT-2; no model or network call is made (NFR-1). Level: unit.
- **AC-31** (FR-28) Given CT-4 bound `(existing)` with no `Like:` line, when `nio check plan` runs, then CT-4 raises no error. [derived: FR-28]
  Observable: no error naming CT-4. Level: unit.
- **AC-32** (FR-31) Given a build-order entry `### US-2` with no `Scenario:` line, when `nio check plan` runs, then it raises no error for it. [human]
  Observable: no error naming US-2 or `Scenario`. Level: unit.

### US-5 A plan finding is fixed in the plan, or sent back to the spec (P1) [human]
- **Why this priority:** without a plan-side fix type the gate's findings can't be closed, and filling spec gaps in the plan hides them from the spec jury.
- **Independent test:** dispose fixture plan-gate findings both ways and read the ledgers.

- **AC-33** (FR-32) Given confirmed plan-gate finding J-2, when it is disposed `plan-fix` and the plan files are changed, then the ledger records it. [human]
  Observable: `nio jury dispose <slug> plan J-2 plan-fix` exits 0; `jury/plan.json` shows J-2 as `plan-fix`. Level: unit.
- **AC-34** (FR-33) Given spec-gate finding J-1, when it is disposed `plan-fix`, then the disposition is refused. [derived: FR-33]
  Observable: non-zero exit; the error says `plan-fix` belongs to the plan gate. Level: unit.
- **AC-35** (FR-34, FR-35) Given confirmed plan-gate finding J-3 rooted in the approved spec, when it is handled, then a change request on the spec is written and the plan gate waits. [human]
  Observable: a change record naming J-3 and the spec items it changes; no further plan-gate round is collected until the spec gate re-approves. Level: integration.
- **AC-36** (FR-35) Given the change request for J-3 edits FR-4 only, when the spec jury re-checks, then only FR-4 and the items around it are in its pack, and the plan jury resumes once the spec is re-approved. [human]
  Observable: the fix-check pack names FR-4 and no unchanged FR; after re-approval the next plan-gate round can be collected. Level: integration.
- **AC-37** (FR-36) Given a finding that the spec leaves a limit unstated, when it is fixed, then the plan does not state its own limit for it. [human]
  Observable: the ledger shows the finding as `spec-change`; no `plan-fix` is recorded for it; the plan files are unchanged until the spec is re-approved. Level: integration.
- **AC-43** (FR-41) Given confirmed plan-gate finding J-3 that the human confirmed as spec-rooted, when it is disposed, then the ledger records it with its change request. [derived: FR-41, FR-34]
  Observable: `jury/plan.json` shows J-3 as `spec-change` with the change record's ID. Level: unit.
- **AC-38** (FR-12) Given plan-gate finding J-2 the human accepted as risk in an earlier round, when a lens's fix-check pack is built for the next round, then it tells the juror not to raise J-2 again. [human]
  Observable: `nio jury fixcheck <slug> plan --lens test-proof` lists J-2 under "Settled by the human: don't raise these again". Level: unit.
- **AC-51** (FR-12) Given a plan-gate round whose lenses raise major finding J-1, when it is collected, then J-1 goes to the refuter before any outcome. [derived: FR-12]
  Observable: collect prints a refuter batch holding J-1; `nio jury check <slug> plan` says `pending` until the refuter answers. Level: unit.
- **AC-52** (FR-12) Given the plan gate's first review is done and only confirmed majors remain, when `nio jury check <slug> plan --record` runs, then no new round is asked for and the majors go to the human as one list. [derived: FR-12]
  Observable: outcome `human`, listing every remaining major in one list; no `rerun`. Level: unit.

### US-6 The plan is approved and the tasks stage reads the approval (P2) [human]
- **Why this priority:** the tasks stage needs it, but the gate's review is useful before the tasks stage is built.
- **Independent test:** approve a fixture plan, then start the tasks stage before and after.

- **AC-39** (FR-37) Given the plan gate's outcome is approved, when the approval is recorded, then one `nio: approve plan` commit holds the plan files and the plan verdict. [human]
  Observable: the latest commit's message is `nio: approve plan` and it touches the four plan files and the plan gate's verdict record. Level: integration.
- **AC-40** (FR-38) Given a spec with a `plan.md` whose plan gate is not approved, when the tasks stage is asked to start, then it refuses. [human]
  Observable: no `tasks.md` is written; the message says the plan must be approved first. Level: integration.
- **AC-55** (FR-38) Given a full spec with no `plan.md`, when the tasks stage is asked to start, then it refuses; given a bug-fix spec with no `plan.md`, it proceeds. [human]
  Observable: the first exits non-zero saying the plan must be approved first and writes no `tasks.md`; the second starts the tasks drafter. Level: integration.
- **AC-56** (FR-47) Given an approved plan whose CT-2 cites FR-4, when a change request edits FR-4 and the spec is re-approved, then the plan gate is no longer approved and its next pack covers CT-2. [human]
  Observable: the tasks stage refuses, saying the plan must be approved first; the plan gate's fix-check pack names CT-2 and the changed FR-4. Level: integration.
- **AC-57** (FR-48) Given the plan gate waits on change request C-1 for J-3, when J-6 is confirmed spec-rooted, then J-6 joins C-1. [human]
  Observable: the ledger shows J-6 as `spec-change` naming C-1; no second change record is written; the gate still waits. Level: integration.
- **AC-58** (FR-49) Given the plan gate waits on change request C-1 for J-3, when the human drops C-1, then the plan jury resumes and J-3 is open again for the human. [human]
  Observable: `nio jury check <slug> plan` no longer says the gate is paused; J-3 is listed for the human with fix in the plan or accept as risk. Level: integration.
- **AC-59** (FR-50, FR-39) Given the plan gate was handed to the human with majors J-2 and J-4 open, when a new round is collected before the human rules, then it is refused, and the tasks stage refuses too. [human]
  Observable: collect exits non-zero saying the gate waits on the human's ruling; the tasks stage says the plan must be approved first. Level: integration.
- **AC-41** (FR-38) Given a spec with a `nio: approve plan` commit, when the tasks stage is asked to start, then it proceeds. [human]
  Observable: no refusal; the tasks drafter is started. Level: integration.
- **AC-42** (FR-39) Given a plan gate the human closed with a reason, when the tasks stage is asked to start, then it proceeds; given a plan gate handed to the human but not closed, it refuses. [research: RF-9]
  Observable: the first proceeds; the second exits non-zero saying the plan must be approved first. Level: integration.

## Functional requirements
- **FR-1** WHEN `nio jury plan <slug> plan` runs THE SYSTEM SHALL plan the plan gate instead of refusing it as not built. [human]
- **FR-2** IF `nio check plan <slug> --gate` fails THEN THE SYSTEM SHALL refuse to plan the plan gate, naming that check and its error count, in place of the spec gate's `nio check spec --gate` precondition. [human]
- **FR-3** THE SYSTEM SHALL run test-proof and architecture-fit as the plan gate's core lenses on every plan; the spec gate's testability lens does not run at the plan gate. [human]
- **FR-4** WHEN any contract in `contracts.md` has a `State:` line THE SYSTEM SHALL add the logic lens to the plan gate. [research: RF-6]
- **FR-5** WHEN the spec's risk flags include auth or pii THE SYSTEM SHALL add the security lens to the plan gate. [human]
- **FR-44** THE SYSTEM SHALL ship a `risk-rollback` lens card with an `## At plan` section that asks how each migration or deletion the plan makes is rolled back or recovered. [human]
- **FR-45** THE SYSTEM SHALL add an `## At plan` section to the security card that asks, per contract, who may call it and what data it exposes or keeps. [human]
- **FR-6** WHEN the spec's risk flags include migration or data-deletion, or `contracts.md` has a `## Data model` section, THE SYSTEM SHALL add the risk-rollback lens to the plan gate. [human]
- **FR-8** THE SYSTEM SHALL compute every plan-gate lens and the reason it runs in the CLI, as at the spec gate, and print each lens with its reason. [human]
- **FR-9** IF a lens the plan gate needs has no card THEN THE SYSTEM SHALL block the gate and name the missing card. [research: RF-7]
- **FR-10** THE SYSTEM SHALL give every plan-gate juror all four plan files: `plan.md`, `contracts.md`, `tests.md` and `quickstart.md`. [human]
- **FR-42** THE SYSTEM SHALL accept a plan-gate finding's quote only when it is found word for word in the four plan files, the spec, the project's CLAUDE.md, `architecture.md`, a file a contract binds or a file a `Like:` line names, or the human's own words. [human]
- **FR-43** THE SYSTEM SHALL have the CLI list the files a plan-gate juror is given, and give every juror the same files FR-42 accepts quotes from. [agent]
- **FR-11** THE SYSTEM SHALL keep the plan gate's findings in its own ledger, `.nio/specs/<slug>/jury/plan.json` and `.md`, apart from the spec gate's. [research: RF-8]
- **FR-12** THE SYSTEM SHALL run the plan gate with the spec gate's rules (D-261026-r52z): each juror in a fresh context with only its pack, at most 5 findings per lens, the refuter on every blocker and major, after the first review only a blocker the refuter confirms starts another round while the rest go to the human as one list, one final fix check, and no re-raising of a finding the human accepted as risk or ruled out of scope. [human]
- **FR-13** WHEN the human asks for the plan jury after `@nio:plan` THE SYSTEM SHALL have the jury skill run the plan gate. [derived: FR-1, RF-1]
- **FR-14** THE SYSTEM SHALL ship a `test-proof` lens card with an `## At plan` section. [human]
- **FR-15** THE SYSTEM SHALL have test-proof name, for each `TC-n`, the smallest realistic bug that breaks its AC (a flipped condition, a dropped default, a missing field) and the line in its `Assert:` that would fail because of it. [human]
- **FR-16** THE SYSTEM SHALL have test-proof flag a test whose only asserts don't count: "it succeeded", "it didn't throw", snapshot-only, a mock or log was called, the integration under test is mocked away, or a tautology. [human]
- **FR-17** THE SYSTEM SHALL have test-proof flag a test whose expected value does not come from an independent source. [human]
- **FR-18** THE SYSTEM SHALL have test-proof flag a test whose AC is already true on today's code, judged by reading the code each contract binds, without running anything. [human]
- **FR-19** THE SYSTEM SHALL have test-proof flag an AC that only another story's work can satisfy. [human]
- **FR-20** THE SYSTEM SHALL have test-proof search the repo before saying a test is missing. [human]
- **FR-21** THE SYSTEM SHALL ship an `architecture-fit` lens card with an `## At plan` section. [human]
- **FR-22** THE SYSTEM SHALL have architecture-fit judge whether each `new` contract really follows the code its `Like:` line names. [human]
- **FR-23** THE SYSTEM SHALL have architecture-fit check the plan against each rule in the project's CLAUDE.md, one by one, and against the project's principles once #26 exists. [human]
- **FR-24** THE SYSTEM SHALL have architecture-fit flag a contract that contradicts the existing code or `architecture.md`, and a component nothing uses; that every contract is delivered and cites an FR is left to `nio check plan`. [human]
- **FR-25** THE SYSTEM SHALL have architecture-fit flag anything no requirement needs that `## Complexity tracking` does not justify. [human]
- **FR-26** THE SYSTEM SHALL have architecture-fit ask, for each user story, what can be shown when it is done, and flag a story with no answer. [human]
- **FR-27** THE SYSTEM SHALL have architecture-fit flag contracts that are incomplete or inconsistent with each other. [human]
- **FR-28** THE SYSTEM SHALL require each contract bound `new` in `contracts.md` to carry a `Like: <file>:<symbol>` line naming the existing code it follows, or `Like: none: <reason>` when no existing code is like it. [human]
- **FR-46** THE SYSTEM SHALL have architecture-fit judge each `Like: none` reason, and flag it when similar existing code was missed. [human]
- **FR-29** IF a contract bound `new` has no `Like:` line THEN THE SYSTEM SHALL fail `nio check plan`, naming the contract. [derived: FR-28]
- **FR-30** IF a `Like:` line names a file that doesn't exist or a symbol not in it THEN THE SYSTEM SHALL fail `nio check plan`, naming the contract and the missing file or symbol. [human]
- **FR-31** THE SYSTEM SHALL not require a `Scenario:` line on a build-order story entry. [human]
- **FR-32** THE SYSTEM SHALL accept a `plan-fix` disposition at the plan gate, meaning the finding is fixed in the plan files; the jury skill settles a plan-fix that changes no behaviour itself, and hands the human the rest, as with `spec-fix` at the spec gate. [human]
- **FR-33** IF `plan-fix` is given at a gate other than the plan gate THEN THE SYSTEM SHALL refuse it. [agent]
- **FR-34** WHEN a confirmed plan-gate finding's cause is in the approved spec THE SYSTEM SHALL have the jury skill propose it as spec-rooted with a draft change request, and reopen the spec only once the human confirms; it is never a plan fix. [human]
- **FR-41** THE SYSTEM SHALL record a spec-rooted finding in the plan gate's ledger with a `spec-change` disposition naming its change request. [agent]
- **FR-35** WHEN a change request from the plan gate has edited the spec THE SYSTEM SHALL reopen the approved spec gate and have the spec jury re-check only the changed items, from the fix-check pack, and resume the plan jury once the spec is re-approved. [human]
- **FR-36** THE SYSTEM SHALL never fill a gap in the approved spec with detail of the plan's own. [human]
- **FR-37** WHEN the plan gate's outcome is approved THE SYSTEM SHALL record the approval as a `nio: approve plan` commit. [human]
- **FR-38** IF a full spec has no approved plan, including when it has no `plan.md`, THEN THE SYSTEM SHALL refuse to start the tasks stage on it; a bug-fix spec, which has no plan stage, is not refused for lacking one. [human]
- **FR-47** WHEN the spec is re-approved after a change request while its plan gate is approved or closed by the human THE SYSTEM SHALL withdraw that approval and have the plan jury re-check only the plan items tied to the changed spec items before the plan is approved again. [human]
- **FR-48** WHILE the plan gate waits on a spec change THE SYSTEM SHALL add a further confirmed spec-rooted finding to the same open change request, so one spec re-check covers both. [human]
- **FR-49** WHEN the human drops the change request the plan gate waits on THE SYSTEM SHALL resume the plan jury and hand each of its findings back to the human, to fix in the plan or accept as a risk. [human]
- **FR-50** WHILE the plan gate is with the human THE SYSTEM SHALL run no plan-gate round until the human settles the list with fixes, which leads to the one final fix check, or closes the gate with a reason. [human]
- **FR-39** THE SYSTEM SHALL count a plan gate the human closed with a reason as approved for FR-38, and a gate handed to the human but not closed as not approved. [research: RF-9]
- **FR-40** THE SYSTEM SHALL ship the test-proof, architecture-fit and risk-rollback cards with tier max and effort med. [human]

## Rules
### Decision table: plan-gate lenses
| trigger (always, a contract has a `State:` line, risk auth or pii, risk migration or data-deletion, a `## Data model` section) | → lens added | Src |
| --- | --- | --- |
| always | test-proof and architecture-fit (core) | [human] |
| a contract has a `State:` line | logic | [research: RF-6] |
| risk auth or pii | security | [human] |
| risk migration or data-deletion | risk-rollback | [human] |
| a `## Data model` section | risk-rollback | [human] |

### Decision table: where a plan finding is fixed
| cause (the plan, the approved spec) | → what happens | Src |
| --- | --- | --- |
| the plan | `plan-fix`: fixed in the plan files | [human] |
| the approved spec | change request: the spec is edited, the spec jury re-checks only the changed items, then the plan jury resumes | [human] |

### State table: plan gate (start: open; final: approved, closed-by-human)
| State | round approved | round rejected | handed to the human | spec-rooted finding confirmed | spec re-approved | spec change dropped | human settles with fixes | human closes | Src |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open | → approved | → open | → with-human | → waiting-on-spec | ignore | ignore | reject: nothing is with the human | → closed-by-human | [human] |
| waiting-on-spec | reject: plan jury paused | reject: plan jury paused | reject: plan jury paused | → waiting-on-spec | → open | → open | reject: plan jury paused | reject: finish the spec change first | [human] |
| with-human | reject: waiting on the human's ruling | reject: waiting on the human's ruling | ignore | → waiting-on-spec | ignore | ignore | → open | → closed-by-human | [human] |
| approved | ignore | ignore | ignore | reject: no round runs on an approved plan; a change request carries the problem | → open | ignore | ignore | ignore | [human] |
| closed-by-human | ignore | ignore | ignore | reject: no round runs on a closed gate; a change request carries the problem | → open | ignore | ignore | ignore | [human] |

`approved` and `closed-by-human` end the gate; the one way out of either is "spec re-approved" (FR-47), which reopens it on what changed.

## Key entities
- **Plan gate ledger**: `.nio/specs/<slug>/jury/plan.json`, with `plan.md` next to it, regenerated from it; the plan gate's rounds, findings and dispositions. [research: RF-8]
- **`Like:` line**: on a `new` contract in `contracts.md`, `Like: <file>:<symbol>`, the existing code the contract follows, or `Like: none: <reason>`. [human]
- **`plan-fix`**: a disposition meaning a finding is fixed in the plan files. [human]
- **Change request**: a record asking to change the approved spec, raised by a plan finding rooted in the spec. [human]
- **Plan approval**: the `nio: approve plan` commit the tasks stage reads. [human]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL run `nio jury plan <slug> plan` and the `Like:` check in `nio check plan` with zero model calls. [research: RF-10]

## Success criteria
- **SC-1** The first spec planned after this ships goes through the plan gate to an outcome, with no "only the spec gate" error. [agent]
- **SC-2** On that first plan gate, every test-proof finding names a concrete bug and the `Assert:` line that would catch it, or says that no line would. [agent]

## Non-goals
- Running tests during the plan gate; test-proof judges by reading, and the red-first test and the implementation jury's check of it (#29) come later. [human]
- Requiring a `Scenario:` on every story entry. [human]
- The tasks gate's lenses beyond what the tasks stage spec defines. [agent]
- Project principles (#26); architecture-fit uses them once they exist. [human]
- Mutation testing of planned tests; Meta ACH is prior art only. [derived: FR-18]

## Glossary
- **Plan gate**: the jury gate between the plan stage and the tasks stage, over the four plan files. Never "plan review".
- **Lens**: one juror's angle of review, with its own card. Never "reviewer type".
- **Core lens**: a lens that runs on every plan. **Triggered lens**: one the CLI adds when its trigger holds.
- **Test-proof**: the lens that asks whether each planned test would fail if its AC broke. Unlike testability, which judges whether a spec's ACs can be tested, it judges the planned tests themselves.
- **Architecture fit**: the lens that asks whether the plan fits the existing code, the project's rules and `architecture.md`.
- **Spec-rooted finding**: a plan-gate finding whose cause is in the approved spec, not the plan.

## Risks and evidence against
- Test-proof judges "already true on today's code" by reading, so it can be wrong both ways; the red-first test catches what it misses. [human]
- Reviewers drift into warnings only (GSD names this); a gate with only minor findings may pass weak plans. [human]
- Counting verify commands instead of asking whether they'd fail (GSD's "Nyquist" check) is the trap test-proof must avoid. [human]
- A `Like:` line can name code that exists but is a poor model; only the lens catches that. [human]
- There is no convergence guarantee in looping review (Pocock); the round cap and the human handoff are the stop. [human]
- A long juror report fed back into the main conversation froze sessions in spec-kit (#2511, #3188). [human]

## Decisions
- A spec-rooted plan finding is proposed by the jury skill and reopens the spec only once the human confirms (grill Q1, 2026-10-28).
- A plan-gate finding may quote the plan files, the spec, CLAUDE.md, `architecture.md` and every file a contract or `Like:` line names (grill Q2, 2026-10-28).
- This spec writes the plan-gate questions for both risk lenses: a new risk-rollback card and a plan section on the security card (grill Q3, 2026-10-28).
- Risk-rollback also runs when the plan's contracts have a data-model section, not only on the migration and data-deletion flags (grill Q4, 2026-10-28).
- A new contract with nothing like it in the code writes `Like: none: <reason>`, and architecture-fit judges the reason (grill Q5, 2026-10-28).
- The three new plan reviews (test-proof, architecture-fit, risk-rollback) run on the max model with medium effort (grill Q6, 2026-10-28).
- While a spec-rooted finding is with the spec, the plan jury pauses; once the plan is approved or closed, changes go through a change request (grill Q7, 2026-10-28).
- The plan gate stops rounds the way the spec gate does: after the first review only a confirmed blocker starts another round: D-261026-r52z (memory, 2026-10-26).
- A full spec needs an approved plan before tasks; a bug-fix spec goes straight to tasks (grill Q8, 2026-10-28).
- When the spec changes under an approved plan, the plan's approval is withdrawn and the plan jury re-checks what changed (grill Q9, 2026-10-28).
- A dropped spec change resumes the plan jury and hands its findings back to the human; a second spec-rooted finding joins the open change request (grill Q10, 2026-10-28).
- A plan gate handed to the human waits in its own state until the human settles it with fixes or closes it (grill Q11, 2026-10-28).
- `tests.md` entries cite ACs, but test code carries no spec IDs; the conformance lens, not test-proof, matches test code to ACs: D-261027-b44u (memory, 2026-10-27).

## Open points

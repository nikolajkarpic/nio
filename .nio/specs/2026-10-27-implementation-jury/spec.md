---
slug: 2026-10-27-implementation-jury
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [external-input]           # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, OP-10, OP-11, OP-12, OP-13, OP-14, OP-15, OP-16, OP-17]  # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-10-27-implementation-jury` checks all of this. -->
# Implementation jury: judge each implemented epic against its spec, with conformance and correctness always and security, adversary, consistency and risk lenses when triggered

## Summary
Today nothing checks that an implemented epic does what its spec says: a finished task is trusted on its checkbox.
This adds a jury gate that runs on each epic once the implement stage has finished its tasks. The CLI first collects
observed evidence for free (tests and scripted attacks run, per-AC evidence, phantom completion, test tampering, lint
and type checks); then read-only lenses judge the code: conformance and correctness always, security, adversary,
consistency and risk and rollback when triggered. Findings become fix tasks appended to the epic, or change requests
when the spec is the stale side, so the human gets an implementation that has been checked, not claimed. [human]

## Actors and journeys
- **A-1 Human**: owns the project and its specs; picks which lens runs go ahead when an epic's plan is over the cap, settles the findings the jury hands over, and decides change requests. [human]
- **A-2 Jury skill agent**: the agent running @nio:jury on an implemented epic; plans the lenses, builds their packs, drives the CLI and disposes of findings within its authority. [research: RF-6]
- **A-3 Lens juror**: an independent, read-only lens subagent (conformance, correctness, security, adversary, consistency, risk and rollback) that judges the epic's code from its pack and may ask for a specific run. [human]
- **A-4 Refuter**: validates blocker and major findings against the code before they reach the human. [human]
- **A-5 Implementer**: the implement stage (#43) that works the epic's tasks, including fix tasks the gate appends. [research: RF-2]

**UJ-1 Jury an implemented epic** (A-2, A-3, A-4) [research: RF-1]
1. The implement stage finishes every task of an epic.
2. The CLI runs the tests, the scripted attacks and the lint and type checks, and collects per-AC evidence, phantom-completion and test-tampering results.
3. The agent plans the core and triggered lenses and gives each its pack: the diff, the ACs, FRs and contracts it touches, and the run results.
4. Each lens reads the code and writes findings with a gap type; the refuter validates the blockers and majors.
5. The CLI composes the outcome.
- Misuse: the agent juries an epic whose tasks aren't finished, or a lens takes a task's "done" status as proof the code exists.
- Evidence: issue #29 and its comments; spec-kit `converge` and `verify-tasks`.

**UJ-2 A rejected epic goes back to implement** (A-2, A-5) [research: RF-3]
1. The outcome is rejected.
2. Fix tasks are appended to the epic with new IDs; the old tasks stay as they were.
3. The implement stage works the fix tasks and the gate runs again.
- Misuse: the agent rewrites or renumbers an old task instead of appending a new one, or deletes code a lens called unrequested.
- Evidence: issue #29 (converge's append-only gap model).

**UJ-3 The code is right and the spec is stale** (A-1, A-2) [research: RF-4]
1. A lens finds the code contradicts the spec, and the code is the right side.
2. A change request goes to the human; the spec is not edited.
3. The human accepts or rejects the change request.
- Misuse: the agent edits the spec to match the code without a change request.
- Evidence: issue #29 (spec-kit#4940).

**UJ-4 The lens plan is over the cap** (A-1, A-2) [research: RF-5]
1. The epic's risk flags and diff trigger more than 6 lens runs.
2. The human sees the planned runs, each with its model tier.
3. The human picks: run all, or choose (dropping the lowest-hit-rate lenses once hit rates are recorded).
- Misuse: the agent drops a lens on its own to stay under the cap.
- Evidence: issue #29, #47.

## User stories

### US-1 The gate runs only on an implemented epic (P1) [human]
- **Why this priority:** the subject of the gate is a real epic whose tasks are done; without it there is nothing to
  append fix tasks to.
- **Independent test:** ask for the gate on an epic with one unfinished task and on one with all tasks finished; only
  the second starts.

- **AC-1** (FR-1) Given an epic from the tasks stage whose tasks the implement stage has all finished, when the gate is asked to run on it, then it starts. [human]
  Observable: exit status 0; the gate's plan for the epic lists conformance and correctness. Level: integration.
- **AC-2** (FR-2) Given an epic with one task not finished, when the gate is asked to run on it, then it refuses. [derived: FR-2]
  Observable: non-zero exit; the message names the unfinished task's ID; no ledger is written. Level: unit.
- **AC-3** (FR-2) Given a spec and a git range but no epic, when the gate is asked to run on them, then it refuses. [human]
  Observable: non-zero exit; the message says the subject must be an epic; no ledger is written. Level: unit.

### US-2 The CLI collects observed evidence before any lens runs (P1) [human]
- **Why this priority:** it is free, deterministic and catches what a lens would otherwise have to guess: the code that
  is not built and the code that is falsely marked built.
- **Independent test:** run the CLI checks on a fixture epic with one AC lacking a test, one phantom file and one
  deleted test; each shows up in the results.

- **AC-4** (FR-3, FR-4) Given an epic covering AC-1 and AC-2, each exercised by a passing test whose name and description say what it checks and carry no spec IDs, and a fixed conformance lens output matching each AC to its test, when it is collected, then the results list each AC with that test's file and line and the result passed. [human]
  Observable: two entries, each with the AC ID, a `file:line` and `passed`, while the tests' source holds no AC IDs; the lens's own matching is judged by the lens card's evaluation, not this test. Level: integration.
- **AC-5** (FR-5) Given an AC the epic covers has no test, and a fixed conformance lens output saying so, when it is collected, then a missing-evidence finding is recorded for it. [human]
  Observable: one finding citing that AC with gap type missing and severity blocker. Level: unit.
- **AC-6** (FR-5) Given an AC's test fails, and a fixed conformance lens output matching that test, when it is collected, then a missing-evidence finding is recorded for it. [human]
  Observable: one finding citing the AC, naming the failing test, with severity blocker. Level: unit.
- **AC-7** (FR-6, FR-7, FR-8) Given a task marked done names a file that doesn't exist, when the gate starts, then the task is flagged as phantom completion despite its status. [human]
  Observable: a finding naming the task and the missing file. Level: unit.
- **AC-8** (FR-8) Given a task names a file that exists but isn't in the epic's diff, when the gate starts, then it is flagged. [human]
  Observable: a finding naming the task and the file. Level: unit.
- **AC-9** (FR-8) Given a symbol defined in the diff is referenced nowhere but its own definition, when the gate starts, then it is flagged as dead code. [human]
  Observable: a finding naming the symbol and its file. Level: unit.
- **AC-10** (FR-9) Given a function in the diff whose body is empty or only a TODO, when the gate starts, then it is flagged as a possible stub, marked interpretive. [human]
  Observable: a hint naming the function, marked interpretive, in every lens pack, and no ledger finding for it. Level: unit.
- **AC-11** (FR-10) Given the diff deletes a test, when the gate starts, then it is flagged as test tampering. [human]
  Observable: a test-tampering finding at severity major naming the deleted test. Level: unit.
- **AC-12** (FR-10) Given the diff adds a skip to an existing test, when the gate starts, then it is flagged as test tampering. [human]
  Observable: a test-tampering finding at severity major naming the skipped test. Level: unit.
- **AC-13** (FR-10, FR-36) Given the diff removes an assertion from an existing test and a fixed correctness lens output saying the test got weaker, when it is collected, then it is recorded as test tampering. [human]
  Observable: a test-tampering finding at severity major naming the test and the removed assertion. Level: unit.
- **AC-43** (FR-36) Given the diff changes the expected value in an assertion of an existing test, when the gate starts, then the CLI flags the assertion, and the correctness lens's output says whether the test got weaker. [human]
  Observable: a flag naming the test and the changed assertion line, and a correctness-lens entry on that flag. Level: integration.
- **AC-14** (FR-11) Given the type check reports an error in a file of the diff, when the gate starts, then the results record the failed check and its output. [human]
  Observable: the type-check entry shows failed with the error's file and line. Level: integration.
- **AC-15** (FR-12) Given the spec has a misuse line and quickstart.md a journey run, when the gate starts, then both are run and their results are recorded. [human]
  Observable: one result for the misuse line and one for the journey run, each passed or failed with its output. Level: integration.
- **AC-16** (FR-13) Given a symbol the CLI can't tell is referenced (it is only called dynamically), when the gate starts, then it is flagged, not passed. [human]
  Observable: a hint naming the symbol and saying the check was uncertain, in every lens pack, and no ledger finding for it. Level: unit.
- **AC-17** (FR-3, FR-12) Given a test run that crashes before any test runs, when the conformance lens has run, then every AC is recorded without passing evidence; the CLI only records the crash. [derived: FR-3, FR-5]
  Observable: one missing-evidence finding per AC of the epic; the crash output is in the results. Level: integration.

### US-3 The lens plan has two core lenses, triggered lenses and a cap (P2) [human]
- **Why this priority:** it decides what is judged and what it costs; the CLI evidence in US-2 already has value
  without it.
- **Independent test:** plan the gate for epics with different risk flags and diffs, and compare the planned lenses.

- **AC-18** (FR-14) Given a spec with no risk flags and an epic that only adds new files, when the gate is planned, then the plan holds conformance and correctness only. [human]
  Observable: the planned lenses are exactly conformance and correctness. Level: unit.
- **AC-19** (FR-15) Given a spec flagged auth and migration, when the gate is planned, then security and risk and rollback are added. [human]
  Observable: the plan lists conformance, correctness, security and risk and rollback. Level: unit.
- **AC-20** (FR-15) Given a spec flagged external-input, when the gate is planned, then the adversary is added. [human]
  Observable: the plan lists the adversary. Level: unit.
- **AC-21** (FR-15) Given an epic whose diff changes a module that existed before the epic, when the gate is planned, then consistency is added. [human]
  Observable: the plan lists consistency. Level: unit.
- **AC-22** (FR-16) Given `jury.max_runs` set to 4 and a plan of 5 lens runs, when the gate is planned, then no lens runs until the human picks, and the human sees each planned run and its model tier. [human]
  Observable: the plan output lists 5 runs, each with its tier, and the choices run all or pick (no hit rates recorded yet); no lens output is collected before a pick. Level: integration.
- **AC-23** (FR-16) Given `jury.max_runs` set to 4, a plan of 5 runs, and the human picks a set without one triggered lens, when the gate runs, then the dropped lens is named in the verdict. [human]
  Observable: the verdict names each dropped lens, and conformance and correctness are not among them. Level: integration.

### US-4 Jurors read a focused pack and never run code (P1) [human]
- **Why this priority:** the pack is what every lens judges; read-only jurors keep the gate free of a sandbox.
- **Independent test:** build a pack for a fixture epic and check what it holds; ask for a run in a finding and see its
  result in the next round's pack.

- **AC-24** (FR-17) Given an epic whose diff touches the code for AC-3, FR-2 and CT-1, when a lens's pack is built, then it holds the diff, the text of AC-3, FR-2 and CT-1 and the run results. [human]
  Observable: the pack holds the diff, those three items' text and the results, and no text of an AC, FR or CT the diff doesn't touch. Level: integration.
- **AC-25** (FR-18, FR-19) Given any lens at the implementation gate, when it runs, then it can open any project file and can't write files or run commands. [human]
  Observable: each implementation lens card's tools are read-only (read, grep, glob). Level: unit.
- **AC-26** (FR-20) Given a round-1 finding asks for a specific run, when the round-2 packs are built, then they hold that run's result. [human]
  Observable: the round-2 pack holds the requested run and its output. Level: integration.
- **AC-27** (FR-20) Given a finding asks for a run that can't start, when the next packs are built, then they say the run couldn't start and why. [agent]
  Observable: the next pack holds the request with "couldn't run" and the error. Level: unit.
- **AC-44** (FR-20) Given a finding asks the CLI to run a command that is not one of the project's tests or the spec's attacks, when the next packs are built, then the command is not run and is listed for the human. [human]
  Observable: no process started for that command; the human's list names the request and the finding. Level: integration.
- **AC-45** (FR-20) Given four valid run requests in one round, when the next packs are built, then only 3 are run and the fourth is listed for the human. [human]
  Observable: exactly 3 run results in the packs; the fourth request on the human's list. Level: unit.

### US-5 Findings carry a gap type and are grounded in the code (P1) [human]
- **Why this priority:** a finding without a gap type can't be turned into a task, and an ungrounded one wastes a round.
- **Independent test:** collect lens outputs with a missing gap type, an undefined ID and a paraphrased code quote.

- **AC-28** (FR-21) Given a lens output with a finding that has no gap type, when it is collected, then the output is invalid. [human]
  Observable: collect prints `INVALID` naming the finding's missing gap type. Level: unit.
- **AC-29** (FR-22) Given a finding cites FR-99, which the spec doesn't define, when it is collected, then it is dropped as ungrounded. [human]
  Observable: the finding's status is dropped and the reason names FR-99. Level: unit.
- **AC-30** (FR-23) Given a finding quotes code abbreviated with "…" and paraphrased, when it is collected, then it is kept. [human]
  Observable: the finding's status is open, not dropped. Level: unit.
- **AC-31** (FR-24) Given a major finding, when the gate composes its outcome, then the finding goes to the refuter before the human sees it. [human]
  Observable: the finding is in the refuter batch; the outcome waits on the refuter. Level: unit.
- **AC-47** (FR-21) Given a lens output with a finding that cites no AC, FR or CT, or names no file or area as evidence, when it is collected, then the output is invalid. [derived: FR-21]
  Observable: collect prints `INVALID` naming the missing field. Level: unit.
- **AC-48** (FR-24) Given a major finding the refuter refutes, when the outcome is composed, then it is not open and no fix task is written for it. [derived: FR-24, FR-26]
  Observable: the finding's status is refuted; the epic's task file has no task citing it. Level: unit.
- **AC-49** (FR-38) Given a planned lens with no output, or an invalid one, when the outcome is composed, then it is rerun and never approved; after a second invalid output it is human. [derived: FR-32]
  Observable: outcome `rerun` naming the lens; after the second failure, outcome `human`. Level: unit.
- **AC-50** (FR-26) Given a rejected outcome composed twice for the same round, when fix tasks are appended, then each finding has exactly one fix task. [derived: FR-26]
  Observable: one task per finding ID in the epic. Level: unit.
- **AC-51** (FR-4, FR-39) Given a new test named for an AC whose body has no assertion, when the gate runs, then the packs hold a hint naming it, and a conformance lens output that matches it is not accepted as evidence. [human]
  Observable: a no-assertion hint naming the test in every lens pack; the AC ends with a missing-evidence finding. Level: integration.
- **AC-52** (FR-40) Given a test that never ends, when the gate runs it, then it is stopped at the time limit, recorded as failed, and the gate goes on. [human]
  Observable: the test's result is `failed` with "timed out after" and the limit; the gate reaches its outcome. Level: integration.
- **AC-53** (FR-40) Given a test that deletes files, when the gate runs it, then only the throwaway copy is touched. [human]
  Observable: the human's working tree is byte-for-byte unchanged after the run. Level: integration.
- **AC-54** (FR-42) Given the epic's type check fails, when the gate starts, then a major finding names the check and its first errors. [human]
  Observable: one finding with severity major naming the type check. Level: unit.
- **AC-55** (FR-41) Given a run that prints 1 MB, when its result is recorded, then the result holds its first and last 100 KB and says how much was cut. [agent]
  Observable: result size about 200 KB with a "cut N bytes" line. Level: unit.
- **AC-56** (FR-43) Given one confirmed major and one minor in the first review, when the outcome is composed, then it is rejected, one fix task is appended for the major and none for the minor. [human]
  Observable: outcome `rejected`; exactly one new task, citing the major. Level: unit.
- **AC-57** (FR-10, FR-36) Given the diff changes an assertion and a fixed correctness lens output saying the test did not get weaker, when it is collected, then no tampering finding is recorded. [human]
  Observable: the hint is in the packs; no test-tampering finding for that assertion. Level: unit.
- **AC-58** (FR-44) Given the only open major is a contradicts finding where the code is right, when the outcome is composed, then the epic waits on the change request and no fix task is appended. [human]
  Observable: the epic's state is waiting on change; no new task. Level: unit.
- **AC-59** (FR-44) Given an epic waiting on change and the human rejects the change request, when the ruling is recorded, then a fix task citing the finding is appended and the epic goes back to implementing. [human]
  Observable: one new task citing the finding; the epic's state is implementing. Level: unit.
- **AC-60** (FR-45) Given a spec with `risk: [secrets]` and an epic of it, when the implementation gate is planned, then the plan holds the security lens. [human]
  Observable: the plan lists security with the reason "risk: secrets". Level: unit.
- **AC-61** (FR-46) Given a spec with `risk: [secrets]`, when `nio check spec` runs, then the security lens is listed. [agent]
  Observable: the lenses line includes security. Level: unit.

### US-6 Findings become appended tasks or change requests, and the outcome follows the spec jury (P1) [human]
- **Why this priority:** it closes the loop: a rejected epic gets concrete work, and nothing already planned is rewritten.
- **Independent test:** reject a fixture epic with one missing and one unrequested finding; two tasks are appended and
  the old tasks are unchanged.

- **AC-32** (FR-25, FR-26) Given the first review raised one confirmed major with gap type missing, when the outcome is composed, then it is rejected and a fix task is appended to the epic. [human]
  Observable: outcome `rejected`; the epic gains one task citing the finding; the epic is back with the implement stage. Level: integration.
- **AC-33** (FR-27) Given an epic with four tasks, one of them an earlier fix task, when another round appends a fix task, then the four tasks are unchanged and the new one has the next free ID. [human]
  Observable: the four tasks' text and IDs are byte-for-byte unchanged; one new task with an ID not used before. Level: unit.
- **AC-34** (FR-28) Given a gate with no findings, when the outcome is composed, then it is approved and no task is written. [human]
  Observable: outcome `approved`; the epic's task file is unchanged. Level: unit.
- **AC-35** (FR-29) Given a confirmed finding with gap type unrequested, when the outcome is composed, then a "justify or remove" task is appended and the code is not touched. [human]
  Observable: one appended task whose text says justify or remove; the diff of the code it names is unchanged. Level: unit.
- **AC-36** (FR-30) Given a contradicts finding where the code is the right side, when it is disposed of, then a change request is raised and spec.md is unchanged. [human]
  Observable: one change request citing the finding and the spec item; spec.md's text is unchanged. Level: integration.
- **AC-37** (FR-31) Given two minor findings and nothing else open, when the outcome is composed, then it is approved and the verdict lists both. [human]
  Observable: outcome `approved`; the verdict names both findings. Level: unit.
- **AC-38** (FR-25, FR-32) Given a re-review that raises a new major and no blocker, when the outcome is composed, then it is human, not rejected, as at the spec gate. [human]
  Observable: outcome `human`; the new major is shown as a note. Level: unit.
- **AC-39** (FR-33) Given a gate that ends approved, when the verdict is recorded, then the record names the epic, the outcome and the round. [derived: FR-25, RF-20]
  Observable: one verdict record with the epic's ID, `approved` and the round number. Level: unit.
- **AC-40** (FR-1, FR-26, FR-32) Given a rejected epic whose fix tasks the implement stage has finished, when the gate runs again, then that round is a re-review of the open findings. [human]
  Observable: the round number rose by 1 and each lens pack is a fix check of its findings. Level: integration.
- **AC-46** (FR-37) Given the human chooses fix for a major on the end-of-review list, when the choice is recorded, then a fix task for it is appended to the epic and the final fix check waits until that task is finished. [human]
  Observable: a new task citing the finding in the epic; the gate's state shows the final fix check pending until the task is done. Level: integration.

### US-7 Lens cards know the implementation gate (P2) [human]
- **Why this priority:** the gate can run with the CLI evidence alone; the cards make the lenses judge code rather than
  a spec.
- **Independent test:** read the shipped cards.

- **AC-41** (FR-34) Given the shipped lens cards, when they are listed, then conformance, correctness and risk and rollback cards exist, each saying what it judges at the implementation gate. [human]
  Observable: the three card files exist in `src/nio/agents/`, each with an `## At implementation` section. Level: unit.
- **AC-42** (FR-35) Given the existing lens cards the implementation gate uses, when they are read, then each has an `## At implementation` section. [human]
  Observable: `security.md`, `adversary.md` and `consistency.md` each have an `## At implementation` heading. Level: unit.

## Functional requirements
- **FR-1** WHEN asked to jury an epic from the tasks stage whose tasks the implement stage has all finished THE SYSTEM SHALL start the implementation gate on that epic. [human]
- **FR-2** IF the subject is not an epic from the tasks stage, or any of its tasks is not finished, THEN THE SYSTEM SHALL refuse to start the gate and name what is missing. [research: RF-7]
- **FR-3** WHEN the gate starts THE SYSTEM SHALL run the project's tests and record, for each test, whether it ran and passed. [human]
- **FR-4** WHEN the conformance lens runs THE SYSTEM SHALL have it match every AC the epic covers to the tests that prove it, by file and line, judging each test by its name and description and confirming from its body that it really exercises the AC, with the test's result from FR-3; tests never need to carry spec IDs. [human]
- **FR-5** IF the conformance lens finds an AC the epic covers with no matching test, or whose test did not run or did not pass, THEN THE SYSTEM SHALL record a missing-evidence finding for that AC at severity blocker. [human]
- **FR-6** THE SYSTEM SHALL take as evidence only what it observed (a run it made, code it read), never a task's status or a worker's claim. [human]
- **FR-7** WHEN the gate starts THE SYSTEM SHALL re-check every task of the epic, whatever its status. [human]
- **FR-8** WHEN the gate starts THE SYSTEM SHALL check, for each file and symbol the epic's tasks name, that the file exists and is in the epic's diff and that the symbol is defined and referenced outside its own definition. [human]
- **FR-9** WHEN a symbol in the diff has an empty body or only a TODO THE SYSTEM SHALL flag it as a possible stub, marked interpretive, as a hint in every lens pack, not as a ledger finding; a lens that confirms it raises the finding. [human]
- **FR-39** WHEN a test in the epic's diff has no assertion THE SYSTEM SHALL flag it with zero model calls, as a hint in every lens pack, not as a ledger finding. [human]
- **FR-40** WHEN the CLI runs the epic's tests, lint and type checks, attacks, journey runs or a juror's requested run THE SYSTEM SHALL run it in a throwaway copy of the repo at the epic's final commit, stop it after a time limit (10 minutes by default, `jury.run_timeout` in config) and record a run that times out as failed. [human]
- **FR-41** WHEN a run's output exceeds 200 KB THE SYSTEM SHALL keep its first and last 100 KB in the results and say how much was cut. [agent]
- **FR-42** IF the epic's lint or type check fails THEN THE SYSTEM SHALL record a finding at severity major naming the failing check and its first errors. [human]
- **FR-10** IF the epic's diff deletes or skips a test, or the correctness lens confirms an FR-36 flag weakened a test, THEN THE SYSTEM SHALL record it as test tampering at severity major, whatever reason is given; only the human may accept it as risk, with a reason. [human]
- **FR-36** IF the epic's diff changes or removes an assertion line in an existing test THEN THE SYSTEM SHALL flag it with zero model calls, as a hint in every lens pack, and the correctness lens SHALL judge whether the change weakened the test; only a confirmed weakening is tampering (FR-10). [human]
- **FR-11** WHEN the gate starts THE SYSTEM SHALL run the project's lint and type checks and record their results. [human]
- **FR-12** WHEN the gate starts THE SYSTEM SHALL run the spec's misuse lines as scripted attacks and the per-journey runs in quickstart.md, and record their results. [human]
- **FR-13** IF a check can't tell whether something is complete THEN THE SYSTEM SHALL flag it rather than pass it, as a hint in every lens pack, not as a ledger finding; a lens that confirms it raises the finding. [human]
- **FR-14** THE SYSTEM SHALL run the conformance and correctness lenses on every epic at the implementation gate. [human]
- **FR-15** WHEN a spec risk flag or the epic's diff triggers security, adversary, consistency or risk and rollback (see Rules) THE SYSTEM SHALL add that lens to the epic's plan. [human]
- **FR-16** IF an epic's planned lens runs exceed the cap (6, or `jury.max_runs`) THEN THE SYSTEM SHALL show the human the planned runs, each with its lens card's model tier (cheap, medium or strong) as its cost, and run only what the human picks: all, or a chosen set, plus all but the lowest-hit-rate lenses once NIO records hit rates per lens; the drop and the choice apply to triggered lenses only, and the two core lenses always run. [human]
- **FR-17** WHEN a lens runs THE SYSTEM SHALL give it a pack holding the epic's diff, the ACs, FRs and contracts the diff touches, and the run results. [human]
- **FR-18** THE SYSTEM SHALL let a juror open any file of the project to read it. [human]
- **FR-19** THE SYSTEM SHALL give jurors no way to run code or change files. [human]
- **FR-20** WHEN a finding asks for a specific run THE SYSTEM SHALL make that run and put its result in the next round's packs, only if it names one of the project's tests or the spec's attacks, and at most 3 runs per round across all jurors; any other request is not run and is listed for the human. [human]
- **FR-21** THE SYSTEM SHALL require every finding at the implementation gate to carry a gap type, in its own field beside the lens output's `kind` (missing, partial, contradicts or unrequested), the AC, FR or CT it traces to, and its evidence as a file or area. [human]
- **FR-22** IF a finding cites an AC, FR or CT that the spec or its contracts don't define THEN THE SYSTEM SHALL drop it as ungrounded. [human]
- **FR-23** WHEN a finding quotes code THE SYSTEM SHALL accept a paraphrased or abbreviated quote without a word-for-word check. [human]
- **FR-24** WHEN a lens raises a blocker or a major THE SYSTEM SHALL have the refuter validate it against the code before it reaches the human; a finding the CLI-first checks make goes to the ledger as confirmed, with no refuter. [human]
- **FR-25** THE SYSTEM SHALL compose the gate's outcome from the spec jury's set: approved, rejected, rerun, pending or human. [human]
- **FR-26** WHEN the outcome is rejected THE SYSTEM SHALL append one fix task per open blocker or major finding that the decision table routes to a task (where a confirmed finding goes), each citing exactly that finding, with new IDs, never a second task for a finding that already has one, and send the epic back to the implement stage. [human]
- **FR-27** THE SYSTEM SHALL never rewrite, renumber or remove an existing task of the epic. [human]
- **FR-28** WHEN the gate finds nothing wrong THE SYSTEM SHALL write no task. [human]
- **FR-29** WHEN a finding's gap type is unrequested THE SYSTEM SHALL append a "justify or remove" task and never delete the code itself. [human]
- **FR-30** IF a finding shows the code is right and the spec is stale THEN THE SYSTEM SHALL raise a change request and never edit the spec. [human]
- **FR-31** WHEN the outcome is approved THE SYSTEM SHALL list the minor findings in the approved verdict. [human]
- **FR-32** THE SYSTEM SHALL apply the spec jury's convergence rules (#52) to the implementation gate's rounds unchanged, except that minor findings are handled by FR-43 and a new major raised in a re-review goes to the human (AC-38). [human]
- **FR-37** WHEN the human chooses fix for an item on the end-of-review list THE SYSTEM SHALL append it to the epic as a fix task for the implement stage, and run the one final fix check once those tasks are finished; code never changes outside a task. [human]
- **FR-38** IF a planned lens has delivered no valid output THEN THE SYSTEM SHALL compose rerun, never approved, and human after its second invalid output, as at the spec gate. [derived: FR-32]
- **FR-44** WHEN the outcome is rejected and every open blocker or major finding went to a change request THE SYSTEM SHALL hold the epic until the human rules on each change request: accepted, the finding is settled and the gate composes again; rejected, the finding becomes a fix task and the epic goes back to the implement stage. [human]
- **FR-45** THE SYSTEM SHALL add `secrets` to the spec's risk flags, set when the work stores, sends or shows tokens, keys, passwords or other secrets; permission changes stay under `auth`. [human]
- **FR-46** WHEN a spec carries the `secrets` flag THE SYSTEM SHALL bring in the security lens at the spec gate too, as it does for `auth`. [agent]
- **FR-43** THE SYSTEM SHALL never let a minor finding make the outcome rejected or human, nor append a task for it; minors are only listed in the verdict (FR-31). [human]
- **FR-33** WHEN an epic's gate ends THE SYSTEM SHALL write a verdict record naming the epic, the outcome and the round, listing its minor findings when approved. [derived: FR-25, RF-20]
- **FR-34** THE SYSTEM SHALL ship conformance, correctness and risk and rollback lens cards for the implementation gate. [human]
- **FR-35** THE SYSTEM SHALL give each existing lens card the implementation gate uses an `## At implementation` section. [human]

## Rules
### State table: epic at the implementation gate (start: implementing; final: approved)
| State | tasks finished | gate starts | outcome approved | outcome rejected, a fix task | outcome human | outcome rerun or pending | human settles, any fix | human settles, all accepted | outcome rejected, only change requests | change request accepted | change request rejected | Src |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| implementing | → implemented | reject: tasks unfinished | reject: no gate running | reject: no gate running | reject: no gate running | reject: no gate running | ignore | ignore | reject: no gate running | ignore | ignore | [human] |
| implemented | ignore | → in jury | reject: no gate running | reject: no gate running | reject: no gate running | reject: no gate running | ignore | ignore | reject: no gate running | ignore | ignore | [derived: FR-1, FR-2] |
| in jury | ignore | ignore | → approved | → implementing | → with human | ignore | ignore | ignore | → waiting on change | ignore | ignore | [human] |
| with human | ignore | reject: the human's list is open | reject: the human's list is open | reject: the human's list is open | reject: the human's list is open | reject: the human's list is open | → implementing | → approved | reject: the human's list is open | ignore | ignore | [derived: FR-32, FR-37] |
| approved | ignore | reject: the epic is approved | ignore | ignore | ignore | ignore | ignore | ignore | ignore | ignore | ignore | [derived: FR-25] |
| waiting on change | ignore | reject: a change request is open | reject: a change request is open | reject: a change request is open | reject: a change request is open | reject: a change request is open | ignore | ignore | reject: a change request is open | → in jury | → implementing | [human] |

### Decision table: where a confirmed finding goes
| gap (missing, partial, contradicts, unrequested) | right side (spec, code) | → result | Src |
| --- | --- | --- | --- |
| missing | - | fix task appended to the epic | [human] |
| partial | - | fix task appended to the epic | [human] |
| contradicts | spec | fix task appended to the epic | [human] |
| contradicts | code | change request; the spec is not edited | [human] |
| unrequested | - | "justify or remove" task appended; the code is not deleted | [human] |

### Decision table: lens a trigger adds
| trigger (auth, pii, external-input, public-api, migration, data-deletion, existing module changed, money, multi-party, secrets) | → lens | Src |
| --- | --- | --- |
| auth | security | [human] |
| pii | security | [human] |
| secrets | security | [human] |
| external-input | adversary | [human] |
| public-api | adversary | [human] |
| multi-party | adversary | [human] |
| migration | risk and rollback | [human] |
| data-deletion | risk and rollback | [human] |
| existing module changed | consistency | [human] |
| money | none: the lenses judge it like any other request | [human] |

## Key entities
- **Epic**: a slice of work from the tasks stage (#42) with its tasks; the gate's subject. [human]
- **Task**: one unit of an epic, with an ID that never changes; fix tasks are appended after the highest ID. [human]
- **Run results**: what the CLI observed: each test's result, the scripted attacks, the journey runs, lint and type checks, per-AC evidence, phantom-completion and test-tampering flags. [human]
- **Finding**: a lens's claim about the code, with a gap type, the AC, FR or CT it cites, its evidence, a severity and optionally a run it asks for. [human]
- **Change request**: a proposal to change the spec because the code is right and the spec is stale; the human decides it. [human]
- **Verdict record**: the gate's result for one epic and round, listing its minor findings when approved. [derived: FR-25, RF-20]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL make the CLI-first checks (FR-3, FR-6 to FR-13, FR-39 to FR-42) with zero model calls; matching ACs to tests (FR-4, FR-5) is the conformance lens's job. [human]

## Success criteria
- **SC-1** On the first epic juried, every AC the epic covers ends with either observed evidence or a finding. [derived: FR-4, FR-5]
- **SC-2** Across all rounds of an epic's gate, no existing task is rewritten, renumbered or removed. [derived: FR-27]

## Non-goals
- Jurying anything but a real epic: no stand-in subject such as a spec plus a git range. [human]
- Building the tasks stage (#42) or the implement stage (#43); this gate depends on both. [human]
- Jurors running code, tests or attacks themselves, or needing a sandbox. [human]
- A separate warn outcome, or spec-kit-evaluator's pass, warn, iterate, clarify and block set. [human]
- A word-for-word check of code quotes. [human]
- Changing the convergence rules of #52 or the lenses of the spec, plan and tasks gates. [research: RF-26]

## Glossary
- **Existing module changed**: the epic's diff modifies a file that existed before the epic started. It brings in the consistency lens.
- **Gap type**: how a finding's code falls short: missing (absent), partial (present but not enough), contradicts (conflicts with the spec, plan or principles) or unrequested (code nothing asked for).
- **Phantom completion**: a task marked done whose file, diff entry, symbol or reference isn't really there.
- **Test tampering**: a test deleted or skipped in the epic's diff, or an edited assertion the correctness lens confirms made a test weaker.
- **Observed evidence**: something the CLI ran or read itself, as opposed to a claim a worker or a checkbox makes.
- **Fix task**: a task the gate appends to an epic from a confirmed finding, with a new ID.
- **Lens run**: one juror running one lens on one epic. The cap counts these, escalation jurors included; it is 6 unless `jury.max_runs` sets another.

## Risks and evidence against
- The gate can't be built or tested until the tasks (#42) and implement (#43) stages exist. [research: RF-25]
- Loose code quotes let a lens describe code that isn't there; only blockers and majors go through the refuter, so a wrong minor reaches the approved verdict unchecked. [research: RF-24]
- A juror's run request is model output that the code under review can steer; FR-20 runs only named tests and attacks, at most 3 per round, so a steered request can at worst pick the wrong test. [derived: FR-20]
- Flagging every edited assertion and every changed pre-existing file is deliberately broad: refactors bring more flags and more consistency runs, which costs the human reading time and the epic runs. [derived: FR-36]

- The CLI's runs have no network isolation: an attack in the epic's code could still reach the network. [human]

## Decisions
- The #52 convergence rules apply unchanged at the implementation gate (after the first review only confirmed blockers start rounds, plus one final fix check): D-261026-r52z (memory, 2026-10-26).
- Task IDs stay free-form strings until the tasks stage's template fixes them, so appended fix tasks follow whatever format #42 sets: D-261024-4xsd (memory, 2026-10-24).
- Minor findings never block an epic or get fix tasks, unlike the spec gate where the first review sends them to be fixed too (grill Q16, 2026-10-27).
- Tests prove ACs by what their name and description say, never by spec IDs in the test; the conformance lens matches them, so per-AC matching costs model calls rather than being a free CLI check: D-261027-b44u (grill Q2, Q3, 2026-10-27).

## Open points

## Deferred
- **DF-1** (from OP-2) How the tasks stage (#42) and implement stage (#43) define an epic, a task, a task's status and "finished", and where their files live. Deferred: not decided in #42, #43 or #45 yet (RF-16, RF-17, RF-18); the human chose to wait on them rather than pre-decide.
- **DF-2** (from OP-3) How an epic and its rounds fit the jury ledger, which today is one file per spec and gate with no epic (RF-19). Deferred: depends on #42 and #45's folder layout, still open.
- **DF-3** (from OP-4) In what runnable form the misuse lines and `quickstart.md` exist (today prose only and no template, RF-21, RF-22). Deferred: open in #38 and #48.
- **DF-4** (from OP-5) How a target project tells nio its test, lint and type-check commands (no mechanism today, RF-23). Deferred: open in #49.

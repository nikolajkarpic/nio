# Grill: 2026-10-29-implement-stage

Session 1 (2026-10-29): delegated to the agent by the human. Permissions, deletion and irreversible steps still go to the human.

## Q1 · OP-2 · 2026-10-29
Question: Who reports red and green to the CLI, when the flow-state spec says a worker never touches flow state?
Facet: actors
Options:
1. Two phases (recommended): a test-phase worker writes the test and names its command; the orchestrator reports red; a fresh code-phase worker writes the code; the orchestrator reports green. The worker never runs `nio flow`. Costs a second subagent run per task.
2. The worker reports red and green itself: one run per task, but it breaks the flow-state rule that only the orchestrator writes flow state, and needs a change request against that spec.
3. The orchestrator reports both after one worker run: red can't be proven, since the code already exists by then.
Answer: 1. Two phases: a test-phase worker writes the test and names its command; the orchestrator reports red; a fresh code-phase worker writes the code; the orchestrator reports green; the worker never runs `nio flow`. [agent]
Reason: the only option that proves red before the code exists and keeps the flow-state spec's single writer (RF-1); it also runs on every host, since no host needs to resume a subagent.
Patched: A-3, UJ-1, FR-5, AC-2, Handoff, glossary (Worker, Test phase, Code phase); retired OP-2

## Q2 · OP-17 · 2026-10-29
Question: What does red freeze, when every planned test lives in one shared test file?
Facet: data
Options:
1. Every file the test phase changed, frozen only until the task is done (recommended): later tasks can add to the shared file; no per-language parsing.
2. Only the task's named test functions: precise, but needs a parser per language to hash one function.
3. The whole test file for the rest of the effort: simple, but blocks every later task that shares the file (RF-5).
Answer: 1. Freeze every file the test phase changed since the claim, until the task is done. [agent]
Reason: RF-5 shows one shared file per spec, so option 3 blocks the stage; option 1 needs no language parsing and fits the two phases from Q1.
Patched: FR-10, Frozen test file, AC-33; retired OP-17

## Q3 · OP-14 · 2026-10-29
Question: Does the worker pack also carry the text of the ACs the task serves?
Facet: meaning
Options:
1. Yes (recommended): a few lines more; the worker can see what "done" means and spot where the spec and code disagree (US-3).
2. No, the four parts only: smallest pack, but the worker can't compare the spec to the code it finds.
3. The whole spec: everything at hand, but it is exactly what the issue rules out ("never the whole spec folder").
Answer: 1. Yes, the pack carries the text of each AC the task serves. [agent]
Reason: a worker can't report a spec problem (UJ-2) without seeing the spec's words; the issue's first draft asked for it, and it is a few lines.
Patched: FR-4, AC-1, SC-2, Worker pack; retired OP-14

## Q4 · OP-19 · 2026-10-29
Question: How does a worker run on the model its task's tier names, when only Claude Code picks a model per call (RF-7)?
Facet: change
Options:
1. One `nio-worker-<tier>` card per tier and host (recommended): works on every host as cards are rendered today (RF-8); four files per host.
2. Pass the model per call where the host allows it: one card, but Codex and Gemini CLI would ignore the tier.
3. Run every worker on one model: simplest, but drops the tier rating the tasks stage already does.
Answer: 1. One `nio-worker-<tier>` card per tier, rendered for each host with the model the tier maps to there; effort is passed per call only where the host takes it. [agent]
Reason: the only option that honours the tier on every host; it reuses `nio agents sync` as is.
Patched: FR-6, FR-7, AC-2, AC-3; retired OP-19

## Q5 · OP-18 · 2026-10-29
Question: Which test runners go on the known list?
Facet: verification
Options:
1. The eight research confirmed from docs or a probe run: pytest, unittest, jest, vitest, mocha, go test, cargo test, rspec (recommended). Maven and Gradle stay unknown (forum-only markers).
2. Python only (pytest, unittest): less to keep up, but every JS, Go and Rust project falls back to the exit code.
3. All nine with JUnit: wider, but its markers rest on forums, not docs.
Answer: 1. Ship built-in markers for pytest, unittest, jest, vitest, mocha, go test, cargo test and rspec; Maven and Gradle are unknown runners. [agent]
Reason: RF-6 already has verified markers for those eight; built in, they need no project setup.
Patched: FR-34, AC-38; retired OP-18

## Q6 · OP-3 · 2026-10-29
Question: Where does the command that runs the full test suite come from?
Facet: data
Options:
1. A project setting, `tests.suite` in NIO's config; if it's missing the effort waits for the human (recommended). The human names the one command NIO runs on the whole repo.
2. Guessed from the repo (pyproject, package.json): no setup, but a wrong guess runs the wrong thing with the human's rights.
3. Named by each worker: no setup, but the suite could differ from task to task, so the baseline means nothing.
Answer: 1. The project's NIO config names it as `tests.suite`; when it isn't set, the effort waits for the human before the baseline. [agent]
Reason: one fixed command makes baseline and review comparable, and the human, not a model, picks what runs on the whole repo.
Patched: FR-35, AC-34; retired OP-3

## Q7 · OP-4 · 2026-10-29
Question: How is "no new failures" judged when the suite's runner can't be read test by test?
Facet: verification
Options:
1. An unknown runner needs a green baseline; then any non-zero suite exit at review is a new failure (recommended). If the baseline fails, the effort waits for the human.
2. Compare the failure counts: works for any runner that prints a count, but one fixed and one broken test look like no change.
3. Skip the check for unknown runners: never blocks, but new failures slip through unseen.
Answer: 1. With an unknown runner the baseline must exit 0, the effort waits for the human when it doesn't, and any non-zero exit at review is a new failure. [agent]
Reason: the only option that never lets a new failure through without per-test names.
Patched: FR-36, AC-35; retired OP-4

## Q8 · OP-6 · 2026-10-29
Question: What counts as one attempt?
Facet: failure
Options:
1. Each refused red or green and each failed review (recommended): every one is a CLI event, so the count can't be gamed by a worker's report.
2. Each worker run that ends without moving the task on: closer to "a try", but the CLI can't see when a worker run ends.
3. Each new claim: simple, but a task can loop forever inside one claim.
Answer: 1. One attempt is each red or green its guard refuses and each failed review; a task blocked by a spec problem uses none. [agent]
Reason: the CLI only knows what it runs (FR-33), so the count has to rest on its own refusals.
Patched: FR-37, Attempt, AC-37; retired OP-6

## Q9 · OP-7 · 2026-10-29
Question: Does the 3-attempt cap apply when the effort's auto flag is off?
Facet: failure
Options:
1. Yes, always (recommended): a looping task stops whoever is driving; costs nothing.
2. Only in auto mode, like the flow's stop list (RF-11): matches it, but a manual run can loop on one task.
3. Configurable: flexible, a setting nobody asked for.
Answer: 1. Yes, the cap applies whether or not the auto flag is on. [agent]
Reason: the loop costs model runs either way; FR-26 already states it without a condition.
Patched: none (FR-26 as written); retired OP-7

## Q10 · OP-8 · 2026-10-29
Question: What happens when a green task's review fails?
Facet: state
Options:
1. Back to red (recommended): the frozen test stays, and a fresh code phase tries again; one attempt used.
2. Back to claimed (the tasks-stage table): the test is thrown away and written again, losing a test that was already proven red.
3. Blocked at once: safe, but one flaky failure costs the human a stop.
Answer: 1. A failed review sends the task back to red with its frozen files kept; a red report on a green task is refused while its review is pending. [agent]
Reason: the test was already proven; only the code needs another try. This settles the tasks-stage spec's DF-1.
Patched: state table Task (green row), AC-37; retired OP-8

## Q11 · OP-9 · 2026-10-29
Question: How does the human unblock a task, and does its attempt count reset?
Facet: actors
Options:
1. `nio flow unblock <slug> T-n --human`: the task is ready, attempts reset to 0, frozen files dropped (recommended).
2. Unblock but keep the count: the next failure blocks it again at once.
3. The human edits the task back: no command, but nothing records who unblocked it.
Answer: 1. `nio flow unblock <slug> T-n --human` sets the task ready, resets its attempts to 0 and drops its frozen files. [agent]
Reason: the human unblocks after changing something, so a fresh start is what they expect; `--human` follows the existing rule that only the human gives it. Who may unblock (the human) comes from A-1 as the human stated it.
Patched: FR-38, AC-36, state table Task (blocked row); retired OP-9

## Call · FR-20 · 2026-10-29
The effort branch is `nio/<slug>`, created from the current commit when missing. No to all five: it changes no one's abilities or data beyond the branch the human already chose to have (A6). [agent]
Patched: FR-20, Effort branch

## Call · FR-22 · 2026-10-29
A claim is refused while there are uncommitted changes outside the effort folder, so each task commit holds only its own work. No to all five. [agent]
Patched: FR-22, AC-7

## Call · FR-25 · 2026-10-29
A review fails when a task touched the spec, plan or tasks files: the check behind the worker card's rule (FR-23). No to all five. [agent]
Patched: FR-25, AC-18, decision table Review row 1

## Call · FR-30 · 2026-10-29
After the last epic the effort moves to done, replacing the flow-state "implement not built" wait. No to all five. [agent]
Patched: FR-30, AC-31

## Call · FR-32 · 2026-10-29
A step the task's state doesn't allow is refused, names the state and records nothing. No to all five. [agent]
Patched: FR-32, AC-22

## Call · Risks · 2026-10-29
The risks of NIO committing per task and of skipping the epic gate are stated correctly; the human already chose both (A6, A12). [agent]
Patched: Risks (two lines)

## Research-backed · 2026-10-29
FR-2 and AC-6 [research: RF-9]; FR-33 and AC-21 [research: RF-4]; the notify non-goal [research: RF-3]; the routes non-goal [research: RF-10].

## Asked · Q12 · OP-10 · 2026-10-29
Question: When a worker's spec problem sends the effort back to the grill, what happens to tasks already done and committed on the effort branch?
Context: Accepting a change to the spec sends the whole effort back through the grill, plan and tasks reviews (per the flow-state spec). The done tasks' commits sit on the effort branch, not main. This is the only point that could throw away finished work, so it's yours to decide.
Options: 1. Keep them (Recommended): commits and done tasks stay; when the effort returns, only tasks the re-approved task list changes run again, as new tasks. 2. Roll the branch back to before the first task: a clean start, but all finished work is lost. 3. No rule: the effort waits and you decide each time.
Refs: OP-10, FR-24, flow-state FR-35, FR-19, FR-21

## Asked · Q13 · Risks · 2026-10-29
Question: Should nio run whatever test command the worker names, with your rights?
Context: To prove a test fails, nio runs the command the worker wrote down (for example `pytest tests/test_x.py`). A bad or hostile command would run as you. But the worker already writes code that runs whenever tests run, so this adds little new power. Every command is recorded in history.
Options: 1. Accept it as a known risk (Recommended): nothing changes; every command is logged. 2. Only allow commands that start with a known test runner or the suite's runner: blocks odd commands, but a task in a project with an unknown runner can't prove red at all. 3. You approve each task's command: safest, but an unattended run stops at every task.
Refs: Risks (`--run`), FR-8, FR-12, risk flag external-input

## Q12 · OP-10 · 2026-10-29
Question: When a worker's spec problem sends the effort back to the grill, what happens to tasks already done and committed on the effort branch?
Options:
1. Keep them (recommended): commits and done tasks stay; when the effort returns, only tasks the re-approved task list changes run again, as new tasks.
2. Roll the branch back to before the first task: a clean start, but all finished work is lost.
3. No rule: the effort waits and you decide each time.
Answer: 1. Keep them: commits and done tasks stay; when the effort comes back to implementing, only tasks the re-approved task list changes run again, as new tasks. Nothing finished is lost, but a done task that the spec change made wrong stays until a new task replaces it. [human]
Patched: FR-39, AC-39; retired OP-10

## Q13 · Risks · 2026-10-29
Question: Should nio run whatever test command the worker names, with your rights?
Options:
1. Accept it as a known risk (recommended): nothing changes; every command is logged.
2. Only allow commands that start with a known test runner or the suite's runner.
3. You approve each task's command.
Answer: 1. Accept the risk: nothing changes; nio runs the named command and logs it. Costs nothing, and the worker's code already runs with your rights when tests run. [human]
Patched: Risks (`--run` line)

## Overturned · Q1 · 2026-10-29
The human, reviewing the agent answers: "1 needs to be configurable where we can do it with one agent and sometimes we might not need Tdd this needs to be evaluated in the tasks evaluation stage where it suggests the complexity of the taks. Others are fine". Q2–Q11 and the calls stand [human]. Q1 reopens as Q14–Q15.

## Asked · Q14 · Q1 · 2026-10-29
Question: Which ways of working a task should the task evaluator choose between?
Context: You want a task worked by one agent or two, and without test-first when it isn't needed, picked when the tasks are rated. The evaluator already rates each task's model level and effort; this adds a third rating with a reason. It adds a line to every task, so the approved tasks-stage spec needs a change request.
Options: 1. Three ways (Recommended): two workers with test-first; one worker with test-first; one worker without test-first (nio only checks the task's tests pass and nothing new fails). A project setting can force one. 2. Two ways: test-first (one or two workers, chosen by a project setting) or no test-first. 3. Only test-first or not; always one worker.
Refs: Q1, FR-5, evaluator card, tasks-stage non-goal "Changing the tasks.md format"

## Asked · Q15 · Q1 · 2026-10-29
Question: With one worker and test-first, how does nio prove the test failed before the code was written?
Context: The flow rules say a worker never touches nio's progress state; only the main agent reports to nio. With two workers the main agent reports in between. With one worker, nobody is there at the midpoint.
Options: 1. Let the worker call nio's fail and pass checks itself, in one-worker mode only (Recommended): nio still runs every command and writes every line; only who triggers it changes. Needs a change request to the flow-state rule. 2. The worker runs a record-only check that saves evidence to a file; the main agent reports later from it: keeps the flow rule, but the worker could edit that file. 3. No failing proof in one-worker mode: nio only checks that the tests pass at the end.
Refs: Q1, FR-5, FR-33, flow-state A-3, FR-14

## Asked · Q16 · new scope · 2026-10-29
Question: Where should frontend work and browser end-to-end testing (a script opens the app and clicks through it) go?
Context: You asked for frontend implementation support and e2e tests that drive a real browser to confirm the app behaves. A browser test is still a command nio can run, so it fits the fail/pass checks, but recording evidence (screenshots, video) and knowing browser test runners is new. This spec is already 39 requirements.
Options: 1. Its own issue, built right after this (Recommended): this spec stays its size; the issue covers browser test runners, screenshot/video evidence and a frontend worker. 2. Add it to this spec: one effort, but it grows a lot and the scope review will likely ask to split it. 3. Put it in the epic review (#29) as an end-to-end check run once per epic.
Refs: Non-goals (workers' methods), FR-8, FR-34, #29

## Q14 · Q1 · 2026-10-29
Question: Which ways of working a task should the task evaluator choose between?
Options:
1. Three ways (recommended): two workers with test-first; one worker with test-first; one worker without test-first. A project setting can force one.
2. Two ways: test-first or not per task; one or two workers by a project setting.
3. Only test-first or not; always one worker.
Answer: 1. Three ways: two workers with test-first; one worker with test-first; one worker without test-first (nio only checks the task's tests pass and nothing new fails). The evaluator picks per task with a reason; a project setting can force one. Most flexible; costs a change request to the tasks spec. [human]
Patched: A-3, UJ-1, FR-5, FR-40, FR-41, AC-40, AC-41, state table Task (claimed row), non-goal on the tasks.md format, glossary (Mode); C-261029-4cev; D-261029-rkpb rewritten

## Q15 · Q1 · 2026-10-29
Question: With one worker and test-first, how does nio prove the test failed before the code was written?
Options:
1. Let the worker call nio's fail and pass checks itself, in one-worker mode only (recommended).
2. A record-only evidence file the main agent reports from later.
3. No failing proof in one-worker mode.
Answer: 1. Worker calls nio: in one-worker mode only, the worker runs nio's fail and pass checks itself. nio still runs every command and writes every line; only who triggers it changes. Needs a change request to the flow-state rule. [human]
Patched: FR-5, FR-42, AC-42; C-261029-rmbs

## Q16 · new scope · 2026-10-29
Question: Where should frontend work and browser end-to-end testing go?
Options:
1. Its own issue, built right after this (recommended).
2. Add it to this spec.
3. Put it in the epic review (#29).
Answer: 1. Own issue, next: this spec stays its size and goes to the jury; a new issue covers browser test runners, screenshot/video evidence and a frontend worker, built right after. [human]
Patched: Non-goals (frontend and browser e2e)

## Confirmed · Q2–Q11 and calls · 2026-10-29
The human, reviewing the agent answers: "Others are fine". Every remaining [agent] tag in spec.md became [human].

Session 2 (2026-10-29): the spec jury's round-1 findings that change behaviour, asked of the human.

## Asked · Q17 · J-1 · 2026-10-29
Question: Should nio check that the worker's test command actually runs the planned test?
Context: The worker names the command. Nothing stops it naming one that runs no test at all, such as a file-exists check or pytest with a filter matching nothing; that "proves" fail and then pass with no real test (abuse review, confirmed).
Options: 1. Refuse "no tests ran" and require the planned test file (Recommended): a known runner that runs no test is refused, and the command must name the test file from the task's planned test; an unknown runner still trusts the command as written. 2. Only refuse "no tests ran". 3. Accept as a known risk.
Refs: J-1, FR-8, FR-34, Decision table Red

## Asked · Q18 · J-2 · 2026-10-29
Question: When does a task's whole-suite check fail?
Context: Today only a failing test the baseline doesn't list fails the check. A change that breaks an import elsewhere, or deletes or skips tests, passes (abuse review, confirmed).
Options: 1. New failure, collection error, or fewer tests (Recommended). 2. New failure or collection error. 3. Keep as is.
Refs: J-2, FR-14, FR-17, Decision table Review

## Asked · Q19 · J-3 · 2026-10-29
Question: How should nio handle a worker writing nio's progress files or running the unblock command itself?
Context: A worker has a shell. It could append a pass line to nio's history or run the unblock command, and nio can't tell a worker from you; today only the worker's instructions forbid it (abuse review, confirmed).
Options: 1. Check what it can, accept the rest (Recommended): a task also fails its check if it changed the contracts or planned tests; forged progress files or unblocks are a known risk, caught when you review the branch's commits. 2. Same check, but hold the spec until `--human` can't be forged. 3. Accept it all as a known risk.
Refs: J-3, FR-5, FR-18, FR-25, FR-38

## Asked · Q20 · J-4 · 2026-10-29
Question: How should nio guard the branch and a failed commit?
Context: The branch is checked only when the stage starts, so a later checkout of main could get a task commit. A commit can also fail (a hook rejects it) after the task is marked done (abuse review, confirmed).
Options: 1. Check every time, and a failed commit keeps the task open (Recommended). 2. Check every time, and the agent retries a failed commit. 3. Keep as is.
Refs: J-4, FR-19, FR-20, AC-26, AC-27

## Asked · Q21 · J-5 · 2026-10-29
Question: What happens when a worker files a spec problem?
Context: Today the task blocks, but you aren't told and nothing pauses. Filing costs no try, so a stuck worker could file instead of failing (abuse review, confirmed).
Options: 1. The effort waits for you (Recommended). 2. Other tasks continue, you're notified. 3. Filing counts as a try.
Refs: J-5, FR-24, FR-37, UJ-2

## Asked · Q22 · J-7 · 2026-10-29
Question: In no-test-first mode, where does a task go when its check fails?
Context: The state table sends a failed check back to the failing-test step, but no-test-first tasks have none, so the task can't move and burns its tries (logic review, confirmed). The table also needs the per-mode rules the requirements already state.
Options: 1. Back to claimed (Recommended). 2. Blocked at once. 3. Record its pass command as its test command.
Refs: J-7, J-13, FR-41, FR-12, state table Task

## Asked · Q23 · J-12 · 2026-10-29
Question: How does a finished task that the re-approved task list changed run again?
Context: You chose to keep finished work when a spec problem sends the effort back, and to rerun only changed tasks. But a done task can never be claimed again under its number (logic review, confirmed).
Options: 1. A new task number (Recommended). 2. Same number, reopened by version. 3. Same number, history reset.
Refs: J-12, FR-39, AC-39, state table Task

## Asked · Q24 · J-14 · 2026-10-29
Question: What exactly is frozen when the failing test is proven?
Context: "Every file changed since the claim" also catches the code when the failure is proven again after code exists, and nio's own bookkeeping files. Either makes the task fail its checks forever (logic review, confirmed).
Options: 1. What the test step changed before the first proof (Recommended). 2. Only files that look like tests. 3. Every changed file minus nio's own.
Refs: J-14, FR-10, FR-11, FR-13

## Asked · Q25 · J-22 · 2026-10-29
Question: How long may a test command run?
Context: nio runs the worker's command and the whole suite with no time limit, so a hanging test stalls nio forever; a missing program isn't covered either (testability review, confirmed).
Options: 1. 10 minutes, changeable (Recommended). 2. 30 minutes, fixed. 3. No limit.
Refs: J-22, FR-8, FR-12, FR-14, FR-16

## Q17 · J-1 · 2026-10-29
Question: Should nio check that the worker's test command actually runs the planned test?
Answer: 1. Refuse no-test runs: a known runner that reports no tests ran is refused, and the command must name the test file from the task's planned test. Catches the cheap tricks; an unknown runner still trusts the command as written. [human]
Patched: FR-8, FR-43, Decision table Red, AC-43

## Q18 · J-2 · 2026-10-29
Question: When does a task's whole-suite check fail?
Answer: 1. Failure, error, or fewer: fails on a new failing test, a collection or import error in the output, or fewer tests collected than the baseline. Catches broken imports and deleted tests; a task that rightly removes a test will need you. [human]
Patched: FR-14, Decision table Review, AC-44

## Q19 · J-3 · 2026-10-29
Question: How should nio handle a worker writing nio's progress files or running the unblock command itself?
Answer: 1. Check some, accept rest: a task also fails its check if it changed the contracts or planned tests, not just spec, plan or tasks. Forged progress files or unblocks are a known risk, caught when you review the branch's commits before merging. [human]
Patched: FR-25, AC-45, Risks (forged state)

## Q20 · J-4 · 2026-10-29
Question: How should nio guard the branch and a failed commit?
Answer: 1. Check always, keep open: nio checks it's on the effort branch at every claim and before every commit, refusing otherwise. The done record and the commit go together; if the commit fails, the task stays open and the effort waits for you with git's error. [human]
Patched: FR-19, FR-20, state table Task (commit fails), AC-46, AC-47

## Q21 · J-5 · 2026-10-29
Question: What happens when a worker files a spec problem?
Answer: 1. Effort waits for you: the effort pauses, naming the task and the change request; filing the same report twice makes no second record. Every filing reaches you, so a worker can't dodge the 3-try limit unseen. Costs a stop each time. [human]
Patched: FR-24, AC-48

## Q22 · J-7 · 2026-10-29
Question: In no-test-first mode, where does a task go when its check fails?
Answer: 1. Back to claimed: the next worker reports the pass again with its command; uses one try. The table gets the per-mode rules. [human]
Patched: FR-45, state table Task (direct review fails, modes note), AC-50

## Q23 · J-12 · 2026-10-29
Question: How does a finished task that the re-approved task list changed run again?
Answer: 1. New task number: the changed task comes back under the next free number and the old one stays done in history. Done stays final and the history reads clearly; the task list shows the old and new numbers. [human]
Patched: FR-39, AC-39

## Q24 · J-14 · 2026-10-29
Question: What exactly is frozen when the failing test is proven?
Answer: 1. Test step's files: whatever the test step changed before the first proof, outside nio's effort folder. Proving the failure again rechecks that same set and never adds code files. Works for any language. [human]
Patched: FR-10, FR-11, Frozen test file

## Q25 · J-22 · 2026-10-29
Question: How long may a test command run?
Answer: 1. 10 min, changeable: each command gets 10 minutes, changeable in project settings. A timeout or a missing program counts as a refused proof (or a failed suite check) and costs a try. [human]
Patched: FR-44, AC-49

## Q26 · J-24 · 2026-10-29
Question: Should the spec prove that nio makes no model calls with a direct check?
Answer: 1. Fix it: the check also asserts that nio loads no model or web client while running those steps. [human]
Patched: NFR-1

## Q27 · architecture note · 2026-10-29
Question: Approve the architecture note for the implement stage?
Answer: 1. Approve: the plan builds on it, and the plan jury checks the plan against it. [human]
Patched: architecture.md approved; plan.md architecture: approved

Session 3 (2026-10-29): plan jury round-1 findings that change behaviour, asked of the human.

## Asked · Q28 · J-13 · 2026-10-29
Question: What happens to a blocked task's unfinished edits?
Context: When a task is blocked (3 failed tries or a spec problem), its test and code edits sit uncommitted, and nio refuses the next task while the tree is dirty. The plan never says whether they're kept or thrown away (rollback review, confirmed).
Options: 1. Save as a patch, clean the tree (Recommended). 2. Leave them; you clean up. 3. Discard them.
Refs: J-13, CT-5, CT-10, CT-11, CT-12, FR-22, FR-38

## Asked · Q29 · J-8 · 2026-10-29
Question: What if the test suite is already broken (a module fails to import) before the first task?
Context: The spec fails a task's check on any collection or import error, with no allowance for one that was there from the start, so every task would fail and block (logic review, confirmed). Fixing it changes a spec rule, so it needs a small change request and a quick spec-jury recheck of that one change.
Options: 1. Pause at the start (Recommended). 2. Count only new broken modules. 3. Leave as is.
Refs: J-8, FR-14, FR-16, FR-36, CT-3, CT-5

## Asked · Q30 · J-12 · 2026-10-29
Question: How should task lists approved before the mode line existed be treated?
Context: Once every task needs a mode line, older approved task lists fail the tasks check, and adding the line counts as editing an approved list (rollback review, confirmed). The flow-state effort's list is one of them.
Options: 1. Missing mode means two workers (Recommended). 2. Re-approve old lists. 3. Use the project setting, else refuse.
Refs: J-12, CT-16, CT-4, FR-40, C-261029-4cev

## Q28 · J-13 · 2026-10-29
Question: What happens to a blocked task's unfinished edits?
Answer: 1. Save as patch: nio saves the task's unfinished changes as a patch file in the run folder, then restores a clean tree so the next task can start. Nothing is lost; you can apply the patch by hand. [human]
Patched: CT-10, CT-11, TC-23, TC-36

## Q29 · J-8 · 2026-10-29
Question: What if the test suite is already broken (a module fails to import) before the first task?
Answer: 1. Pause at the start: like an unknown runner with failing tests, the stage waits for you before the first task, naming the broken module. You fix the suite, then it starts. [human]
Patched: C-261029-kubi (against spec.md); CT-5

## Q30 · J-12 · 2026-10-29
Question: How should task lists approved before the mode line existed be treated?
Answer: 1. Missing mode = two workers: a task with no mode line runs with two workers and test-first. The check requires the line only on lists approved after this is built; the accepted tasks-spec change request gets a small amendment. [human]
Patched: C-261029-nbrg (supersedes C-261029-4cev); CT-4, CT-16

## Patched · C-261029-kubi · 2026-10-29
Applied the accepted change request from Q29: FR-46, AC-51, a Decisions line. [human]

## Patched · J-26 · 2026-10-29
AC-7 now carries the memory-record exemption of C-261029-xttl (spec jury note J-26). [human]

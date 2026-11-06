# Decisions: 2026-11-06-faster-checks

Every design choice of this effort, made by the orchestrator under the human's standing delegation (take the recommended option). Grill = `grill.md`, plan = `plan.md`.

| Decision | Options considered | Chosen | Why | Consequence |
| --- | --- | --- | --- | --- |
| Fold #75 into this effort (coordinator, during the grill) | fold in; leave for later | fold in | the spec wasn't past its gate; same code as #71 | #75 joins the PR's Closes line |
| How much of #75 (grill Q6) | through #71's reuse; also re-run only what the fix diff touched; leave out | through #71's reuse (FR-13) | a fix task closing an epic runs the suite at the fix commit (RF-10), so reuse removes the round's big cost with no new mechanism | lint, type checks, misuse tests and non-test journeys still re-run in a fix-check round (none are used in this repo) |
| Parallel files at once (grill Q1, D-261106-qo2r) | 8 fixed; core count; unbounded | 8 fixed | the issue's example; leaves cores for the tests' own git and Python subprocesses | on a smaller machine 8 may oversubscribe; change one number in `.nio/config.json` |
| Failure behaviour of the parallel suite (grill Q2) | run all, non-zero if any failed; stop at first; first file's code | run all, non-zero if any failed | every failing file shows in one run; `xargs` does it for free | a failing run takes as long as a passing one |
| Inline field slips (grill Q3, D-261106-opl2) | template shows gap/where + case-insensitive labels; default missing fields; parse several pairs per bullet | template + case-insensitive labels | the rejected outputs omitted the fields because the template has no line for them (RF-6) | a finding still missing gap/where stays invalid and is re-emitted |
| `None.` under Findings (FR-9) | accept any case with trailing punctuation; keep strict | accept | the human asked for it in #74 | none, NONE!, None. all mean no findings |
| When evidence reuses the review's suite run (grill Q4, D-261106-grjt) | same commit + configured suite + exit 0; any result with output stored; never | same commit + configured suite + exit 0 | a passing run needs no parsing, so the review line only carries command and exit code | a failing or `tests.epic` run still re-runs the suite in the copy |
| Which journey counts as covered (grill Q5) | suite's own per-file command with nothing added, suite passed; any command naming a test file; a config list | the suite's own per-file command | never skips a run that differs (e.g. `NIO_E2E=1`) | a journey with an extra flag still runs |

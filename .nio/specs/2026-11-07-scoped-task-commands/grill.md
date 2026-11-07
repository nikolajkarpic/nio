# Grill: 2026-11-07-scoped-task-commands

Session 1 (2026-11-07): delegated to the agent (orchestrator / claude-code / claude-opus-5-5) by the human, with standing authority to take the recommended option. Permissions, deletion and irreversible steps would still go to the human; none came up.

## Lookup · OP-1, OP-2, OP-3, OP-4, OP-7 · 2026-11-07
Facet: meaning, actors, data, change, verification
Found: RF-1 to RF-9 in research.md. Retired OP-1, OP-2, OP-3, OP-4, OP-7. RF-3 shows FR-3 already holds for a command naming the file followed by test names; the #84 refusals came from `python -c` workarounds, so #84 is closed by FR-1.

## Asked · Q1 · OP-5 · 2026-11-07
Question: Should the worker pack name the test functions to scope to, or should the worker choose them?
Context: Each TC entry already names its test function in its `File:` line, and the pack carries the task's TC entries whole (RF-5).
Options: 1. Use the names the TC entries already give (recommended): no new pack field; the card says where to find them. 2. Add a "Command" line to the pack: one more generated field to keep right. 3. Let the worker choose: it may scope to the wrong tests.
Refs: OP-5 · FR-6 · RF-5

## Q1 · OP-5 · 2026-11-07
Question: Should the worker pack name the test functions to scope to, or should the worker choose them?
Facet: meaning
Options:
1. Use the names the TC entries already give (recommended)
2. Add a Command line to the pack
3. Let the worker choose
Answer: 1. Use the names the TC entries already give: no new pack field; the card says where to find them. [agent]
Patched: FR-6; retired OP-5

## Asked · Q2 · OP-6 · 2026-11-07
Question: Should the gate file one "suite red" fix task when the only failures are outside the epic's test files?
Context: The per-AC fix tasks came from ACs with no passing test (RF-8). With per-test results, another file's failure leaves the epic's own tests passed, so no AC finding is filed.
Options: 1. Leave it out (recommended): per-test results already remove the per-AC fix tasks; nothing new to build. 2. Build it: a new finding kind for a suite failure outside the epic. 3. Fail the gate on any suite failure: blocks on flakes in unrelated files.
Refs: OP-6 · US-3, FR-8 · RF-8 · issue #88

## Q2 · OP-6 · 2026-11-07
Question: Should the gate file one "suite red" fix task when the only failures are outside the epic's test files?
Facet: failure
Options:
1. Leave it out (recommended)
2. Build it
3. Fail the gate on any suite failure
Answer: 1. Leave it out: per-test results already remove the per-AC fix tasks; nothing new to build. [agent]
Patched: Decisions; retired OP-6

## Asked · Q3 · FR-7 · 2026-11-07
Question: How should red's output reach the code-phase worker?
Context: The pack is written once at claim, before red runs, and red keeps only a hash of its output (RF-7).
Options: 1. Red prints the last 20 lines; the orchestrator passes them on with the pack (recommended): no change to the pack format. 2. Red appends a section to the pack file: the pack's five-part shape changes. 3. Store the output in history: history grows by every red's output.
Refs: FR-7, AC-8 · RF-7 · issue #70 comment

## Q3 · FR-7 · 2026-11-07
Question: How should red's output reach the code-phase worker?
Facet: data
Options:
1. Red prints the last 20 lines; the orchestrator passes them on (recommended)
2. Red appends a section to the pack file
3. Store the output in history
Answer: 1. Red prints the last 20 lines; the orchestrator passes them on with the pack: no change to the pack format. [agent]
Patched: FR-7, AC-8, UJ-1, US-2

## Asked · Q4 · FR-4 · 2026-11-07
Question: Should red refuse a scoped command that runs no test?
Context: A test name that matches nothing would make the script fail or pass without testing anything; the issue says "probably yes" (issue #70).
Options: 1. Refuse it as "no tests ran" (recommended): red can't be vacuous; a typo costs one attempt. 2. Accept it: a typo'd name proves nothing. 3. Warn only: the record still shows a red that proved nothing.
Refs: FR-4, AC-5 · decision table "red outcome" · issue #70

## Q4 · FR-4 · 2026-11-07
Question: Should red refuse a scoped command that runs no test?
Facet: verification
Options:
1. Refuse it as "no tests ran" (recommended)
2. Accept it
3. Warn only
Answer: 1. Refuse it as "no tests ran": red can't be vacuous; a typo costs one attempt. [agent]
Patched: FR-4, AC-5, decision table

## Call · NFR-1, AC-10, Non-goals · 2026-11-07
Below the bar: the 15 s limit per red and green is measured on the same machine as RF-4; a file that crashes before printing a line reads as failed or didn't run, never passed; the non-goals keep scope to what the issues name. Changes what a user can do: no; sees: no; who: no; data: no; cost: no. [agent]

## Finish · 2026-11-07
Fidelity re-read: FR-4, FR-6, FR-7, AC-5, AC-8, AC-10, NFR-1 match their answers. Delegated session: finish confirmed by the agent.

Session 2 (2026-11-07): the spec jury's round findings, delegated to the agent as session 1.

## Q5 · J-1, J-2, J-11 · 2026-11-07
Question: How does red tell a self-check run that ran no test, and what does a script do with a name it doesn't define?
Facet: verification
Options:
1. The script prints a last line `ran <n> tests, <m> failed`; an unknown name runs nothing, prints `ran 0 tests` and exits non-zero; red refuses `ran 0 tests` whatever the exit code, checked first (recommended)
2. Red counts ok/FAIL lines: a crash with no lines reads as zero tests too, but red then can't tell a crash from a typo
3. An unknown name prints a FAIL line: a typo counts as a failing test, so red accepts it
Answer: 1. The script prints a last line `ran <n> tests, <m> failed`; an unknown name runs nothing, prints `ran 0 tests` and exits non-zero; red refuses `ran 0 tests` whatever the exit code, checked first. [agent]
Patched: FR-1, FR-2, FR-4, AC-1, AC-5, decision table "red outcome"

## Q6 · J-15 · 2026-11-07
Question: How does a result line name its file?
Facet: data
Options:
1. `ok <file>::<name>`, the file relative to the working directory, as pytest names tests (recommended)
2. Require test names unique across the suite: a check to keep
3. Leave lines bare: same-named tests in two files collide
Answer: 1. `ok <file>::<name>`, the file relative to the working directory, as pytest names tests. [agent]
Patched: FR-2, AC-1, AC-3, FR-8

## Q7 · J-10, J-7, J-12 · 2026-11-07
Question: How is a test recorded when its file crashes before printing a line for it?
Facet: failure
Options:
1. `failed` when the suite exits non-zero, as C-261030-gk3z keeps for unreadable runs; at red, a crash before the `ran` line reads as a runner red can't read, as today (recommended)
2. `didn't run`: a new value the join treats like failed anyway
3. Add a crash marker red refuses: a new marker for a case the worker sees in the output anyway
Answer: 1. `failed` when the suite exits non-zero, as C-261030-gk3z keeps for unreadable runs; at red, a crash before the `ran` line reads as a runner red can't read, as today. [agent]
Patched: FR-8, AC-10, decision table, Non-goals, Decisions

## Call · J-5 · 2026-11-07
The Summary now gives #70's 75–120 s as the number before the in-process CLI and RF-4's 11–94 s as today's; NFR-1 names `tests/test_implement.py`, one run each, on RF-4's machine (56 s whole file). Changes what a user can do: no; sees: no; who: no; data: no; cost: no. [agent]

## Call · J-16 · 2026-11-07
"Never poll with sleep" applies to test runs; the short wait on `try again` stays. Changes what a user can do: no; sees: no; who: no; data: no; cost: no. [agent]

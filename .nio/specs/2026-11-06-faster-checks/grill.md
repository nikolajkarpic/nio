# Grill: 2026-11-06-faster-checks

Session 1 (2026-11-06): delegated to the agent (orchestrator / claude-code / claude-opus-5-5) by the human, with standing authority to take the recommended option. Permissions, deletion and irreversible steps would still go to the human; none came up.

## Lookup · OP-1, OP-2, OP-3, OP-4, OP-7, OP-8, OP-9 · 2026-11-06
Facet: meaning, actors, data, change
Found: RF-1 to RF-10 in research.md. Retired OP-1, OP-2, OP-3, OP-4, OP-7, OP-8, OP-9.

## Asked · Q1 · OP-5 · 2026-11-06
Question: How many test files should the parallel suite run at once?
Context: The machine has 12 cores; the issue's example is `xargs -P8`. Files make their fixtures in their own temp folder (RF-4).
Options: 1. Eight, fixed (recommended): the issue's example, simple, leaves cores for the subprocesses the tests start. 2. The core count (`nproc`): more parallel on a big machine, but oversubscribes, since each file starts git and Python subprocesses. 3. Unbounded: fastest start, but the slowest file gets the least CPU.
Refs: OP-5 · FR-3 · RF-4 · issue #72

## Q1 · OP-5 · 2026-11-06
Question: How many test files should the parallel suite run at once?
Facet: cost
Options:
1. Eight, fixed (recommended)
2. The core count
3. Unbounded
Answer: 1. Eight, fixed: the issue's example, simple, leaves cores for the subprocesses the tests start. [agent]
Patched: FR-3, US-2; retired OP-5

## Asked · Q2 · OP-6 · 2026-11-06
Question: When one file fails, should the parallel suite still run every other file?
Context: The serial suite stops at the first failure (`|| exit 1`). `xargs` runs every input and exits 123 when any failed.
Options: 1. Run all, exit non-zero if any failed (recommended): every failing file shows in one run; no extra code. 2. Stop at the first failure: matches the serial suite, but needs a wrapper to kill the others and hides later failures. 3. Run all, exit with the first failing file's code: more detail, more shell.
Refs: OP-6 · FR-4 · AC-6

## Q2 · OP-6 · 2026-11-06
Question: When one file fails, should the parallel suite still run every other file?
Facet: failure
Options:
1. Run all, exit non-zero if any failed (recommended)
2. Stop at the first failure
3. Run all, exit with the first failing file's code
Answer: 1. Run all, exit non-zero if any failed: every failing file shows in one run; no extra code. [agent]
Patched: FR-3, FR-4, AC-6; retired OP-6

## Asked · Q3 · OP-7 · 2026-11-06
Question: Which "inline" field forms should the jury parser accept?
Context: The rejected E-1 outputs left out `gap` and `where` entirely (RF-6): the cards name them only in a prose sentence and the printed template has no line for them. `None.` under Findings is the other slip.
Options: 1. Fix the root (recommended): the template shows `gap` and `where` lines for the implementation gate, and the parser reads field labels in any case; a finding still missing them stays invalid. 2. Default a missing `gap`/`where` from the other fields: no re-emit, but the ledger gets guessed values. 3. Parse several `field: value` pairs on one bullet: handles a form nobody wrote yet.
Refs: OP-7 · FR-10, FR-11 · RF-6 · src/nio/agents/conformance.md:29

## Q3 · OP-7 · 2026-11-06
Question: Which "inline" field forms should the jury parser accept?
Facet: meaning
Options:
1. Fix the root (recommended)
2. Default a missing gap/where
3. Parse several pairs on one bullet
Answer: 1. Fix the root: the template shows `gap` and `where` lines for the implementation gate, and the parser reads field labels in any case; a finding still missing them stays invalid. [agent]
Patched: FR-10, FR-12, AC-13, AC-15, Non-goals; retired OP-7

## Asked · Q4 · OP-8 · 2026-11-06
Question: When may evidence reuse the epic-close review's suite result?
Context: The review line keeps only the failing tests (RF-7); the task commit stages every changed path the tests can see (RF-8). With `tests.epic` set, the review may run a quicker command than the suite.
Options: 1. Same commit, the configured suite, exit 0 (recommended): a passing full run needs no output parsing, so storing the command and exit code is enough. 2. Any result of the configured suite, its output stored too: also reuses failing runs, but history grows by the whole output. 3. Never reuse, only skip covered journeys: safest, loses about 6 min per evidence run.
Refs: OP-8 · FR-7, FR-8, AC-9, AC-10 · RF-7, RF-8

## Q4 · OP-8 · 2026-11-06
Question: When may evidence reuse the epic-close review's suite result?
Facet: data
Options:
1. Same commit, the configured suite, exit 0 (recommended)
2. Any result, output stored
3. Never reuse
Answer: 1. Same commit, the configured suite, exit 0: a passing full run needs no output parsing, so storing the command and exit code is enough. [agent]
Patched: FR-7, FR-8, AC-9, AC-10, decision table; retired OP-8

## Asked · Q5 · FR-6 · 2026-11-06
Question: Which journey step counts as "a test file the suite already ran"?
Context: Journeys here are commands like `uv run python tests/test_implement.py`; some add `NIO_E2E=1` or `-v`, which change what runs.
Options: 1. The suite's own per-file command on a file the suite runs, nothing added, and the suite passed (recommended): exact, never skips a run that differs. 2. Any command naming a test file: skips more, but also `NIO_E2E=1` runs that the suite never made. 3. A list in the config: explicit, one more setting to keep.
Refs: FR-6, AC-8, AC-11 · issue #71

## Q5 · FR-6 · 2026-11-06
Question: Which journey step counts as "a test file the suite already ran"?
Facet: verification
Options:
1. The suite's own per-file command, nothing added, suite passed (recommended)
2. Any command naming a test file
3. A list in the config
Answer: 1. The suite's own per-file command on a file the suite runs, nothing added, and the suite passed: exact, never skips a run that differs. [agent]
Patched: FR-6, AC-8

## Asked · Q6 · #75 · 2026-11-06
Question: How much of #75 (fix-check round re-collects all evidence) goes into this effort?
Context: A fix task closing an epic is reviewed with the suite at the fix commit (RF-10), so FR-6 and FR-7 already drop the suite and covered journeys from the fix-check round; what remains is lint, type checks, misuse tests and non-test journeys, none configured or used in this repo.
Options: 1. Fold it in through FR-6/FR-7 and record the source (recommended): the round's big cost goes with no new mechanism. 2. Also re-run only what the fix diff touched: closer to the issue's proposal, a new diff-to-journey mapping. 3. Leave #75 out: the second evidence run stays about 12 min.
Refs: FR-13, AC-16 · RF-10 · issue #75

## Q6 · #75 · 2026-11-06
Question: How much of #75 goes into this effort?
Facet: change
Options:
1. Fold it in through FR-6/FR-7 (recommended)
2. Also re-run only what the fix diff touched
3. Leave #75 out
Answer: 1. Fold it in through FR-6/FR-7 and record the source: the round's big cost goes with no new mechanism. [agent]
Patched: US-5, FR-13, AC-16, Non-goals

## Call · AC-2, AC-3, FR-8, AC-10, AC-11, Non-goals · 2026-11-06
Below the bar: the in-process helper returns what the subprocess did and restores cwd and env; anything not reusable runs as before; non-goals bound the scope. Changes what a user can do: no; sees: no; who: no; data: no; cost: no. [agent]

Session 2 (2026-11-06): the spec jury's round-1 findings, delegated to the agent as session 1.

## Q7 · J-2, J-22 · 2026-11-06
Question: What counts as a failing file in the parallel suite, and how many failing files must the test show?
Facet: failure
Options:
1. A non-zero exit or a kill by signal; a hung file is stopped by the existing `tests.timeout`; the test uses two failing files and one killed (recommended)
2. Also a file that ran zero tests: needs per-file output parsing the shell suite doesn't have
3. Keep one failing file in the test
Answer: 1. A non-zero exit or a kill by signal; a hung file is stopped by the existing `tests.timeout`; the test uses two failing files and one killed. [agent]
Patched: FR-4, AC-6

## Q8 · J-3 · 2026-11-06
Question: What process state must the in-process helper restore?
Facet: data
Options:
1. Working directory, environment and `sys.argv`, also after a non-zero exit or an exception, and no flow lock left behind (recommended): nio keeps no module cache (no `lru_cache` in src/nio)
2. Also reload every nio module per call: closer to a subprocess, gives back most of the time saved
3. Only cwd and env
Answer: 1. Working directory, environment and `sys.argv`, also after a non-zero exit or an exception, and no flow lock left behind. [agent]
Patched: AC-3

## Q9 · J-4, J-19, J-12 · 2026-11-06
Question: Exactly which `none` forms are accepted, and where is `gap` required?
Facet: meaning
Options:
1. The section is exactly one line, `none` in any case plus at most one `.` or `!`; `None, but see F1`, `none yet` and `None.` followed by a finding stay invalid; `gap`/`where` are required at the implementation gate only, as today (recommended)
2. Any line starting with `none`: also swallows `None, but see F1`
3. Any trailing punctuation: `none?` and `none...` pass too
Answer: 1. The section is exactly one line, `none` in any case plus at most one `.` or `!`; the other forms stay invalid; `gap`/`where` are required at the implementation gate only. [agent]
Patched: FR-9, AC-12, AC-14, Non-goals

## Q10 · J-6, J-20, J-21 · 2026-11-06
Question: Which suite run makes a journey covered, and what happens to a journey that isn't?
Facet: verification
Options:
1. The suite result evidence uses at that commit, reused under FR-7 or run in the copy, must have passed; anything not fully covered runs in full in the copy as before (recommended)
2. Only a reused review result covers journeys: a suite run in the copy would still be followed by the same files again
3. Skip covered steps of a mixed journey: partial journeys are harder to read
Answer: 1. The suite result evidence uses at that commit, reused under FR-7 or run in the copy, must have passed; anything not fully covered runs in full in the copy as before. [agent]
Patched: FR-6, AC-8, AC-11

## Q11 · J-10, J-11, J-18 · 2026-11-06
Question: What does the parallel suite promise about its output and its speed?
Facet: verification
Options:
1. Only the exit code is read, as today; wall-clock at most 1.5 times the slowest file run alone (recommended): measurable, allows for queueing at eight at a time
2. Wall-clock at most the slowest file plus 30 s: tighter, but CPU sharing with the slow files' own subprocesses can break it
3. No number: untestable
Answer: 1. Only the exit code is read, as today; wall-clock at most 1.5 times the slowest file run alone. [agent]
Patched: AC-5, AC-7, SC-2

## Q12 · J-14, J-15 · 2026-11-06
Question: Keep the template change and the narrowed #75?
Facet: change
Options:
1. Keep both, add SC-3 (recommended): the template lines are the root fix for the observed slip (RF-6); #75's cost is the suite and test-file journeys, which reuse removes (RF-10); SC-3 measures it
2. Drop the template change: the observed slip (missing gap/where) stays
3. Also re-run only what the fix diff touched: new diff-to-journey mapping, no use in this repo
Answer: 1. Keep both, add SC-3. [agent]
Patched: SC-3

## Call · J-1 · 2026-11-06
The review's suite runs in the working tree; a git-ignored file could make it pass where a fresh copy fails. Accepted as a risk (delegated by the human): ignored files are the environment (`.venv`, caches) every run here already depends on, and the configured suite runs in a copy at any other commit. [agent]

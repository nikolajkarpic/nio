---
slug: 2026-11-07-scoped-task-commands
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: scope each task's test command to its own tests

## Contracts

### CT-1 Self-check runner (FR-1, FR-2) [agent]
- Binding: `tests/selfcheck.py:main` (new)
- Like: none: nothing runs tests in this repo; it replaces each script's own `__main__` loop, such as the one at tests/test_flow.py:2392
- Kind: function
- Shape: `main(tests)`, called as the last line of a script's `if __name__ == "__main__":` block
- Accepts: `tests`, the script's test functions in the order it runs them; the test names come from `sys.argv[1:]` (no names: every test in `tests`).
- Returns: never. Two deliberate changes from the loop it replaces: it goes on after a failing test, and it prints the result lines itself (tests' own bare `ok` prints stay, research RF-13). It prints, for each test run, `ok <file>::<name>` or, when it raises, its traceback then `FAIL <file>::<name>`, and goes on to the next test; then `ran <n> tests, <m> failed`. `<file>` is the path of the file defining the first test, relative to the working directory; `<name>` is the function's `__name__`. Exits 0 when n > 0 and m = 0, else 1.
- Fails: a name in `sys.argv[1:]` that is no test's `__name__` → prints `no test named <name>`, runs no test, prints `ran 0 tests, 0 failed`, exits 1. "given a name the file does not define, it runs no test, prints `ran 0 tests, 0 failed` and exits non-zero" (FR-1)
- Rules: "one `ok <file>::<name>` or `FAIL <file>::<name>` line per test a self-check script runs, `<file>` being the script's path relative to the working directory, then one last line `ran <n> tests, <m> failed`" (FR-2). The file is not named `test_*.py`, so the suite's glob doesn't run it (research RF-13).

### CT-2 Every self-check script runs through CT-1 (FR-1, FR-2) [agent]
- Binding: `tests/test_flow.py` (existing)
- Kind: file
- Shape: the same change in every `tests/test_*.py` `__main__` block (the binding names one; the task's `Files:` lists all 17), the `NIO_E2E` scripts `test_lenses.py` and `test_tasks_e2e.py` included: a script that loops over `globals()` passes `[f for n, f in list(globals().items()) if n.startswith("test_") and callable(f)]`; a script with a fixed list passes that list, in its order (research RF-10); `test_index.py` and `test_records.py` keep `test` first, `test_talk.py` passes `[check]`. A `--demo` branch stays before the call.
- Rules: "with no names run every test in the file" (FR-1).

### CT-3 Red reads self-check output (FR-3, FR-4, FR-5, FR-7) [agent]
- Binding: `src/nio/implement.py:red` (existing)
- Kind: function
- Shape: `red(...)` and `review(...)` unchanged in signature; they read the runner through CT-7.
- Rules: red picks the runner after the run (`runner(command, out)`) and checks "no tests ran" before the exit code: "IF a red command's output ends its run with `ran 0 tests` THEN THE SYSTEM SHALL refuse red with the reason \"no tests ran\", whatever the exit code" (FR-4). The file-naming check stays a substring check (research RF-3, FR-3). On acceptance red prints, after `frozen:`, `output:` and "the last 20 lines of its output" (FR-7), each indented two spaces. Green is unchanged: it runs the red line's command only (research RF-9, FR-5). `review()` of the task closing an epic fails, with the reason `the suite exits <code> and names no failing test`, when its suite's runner is `self-check`, it exits non-zero and `failing` is empty (a file that crashed before its lines), as an unknown runner's non-zero suite fails it today.
- State: follows the spec's decision table "red outcome"

### CT-4 Evidence reads self-check results per test (FR-8) [agent]
- Binding: `src/nio/evidence.py:collect` (existing)
- Kind: function
- Shape: as today
- Returns: the runner is `implement.runner(suite command, suite output)`. A failing-test entry of the form `<file>::<name>` matches a test only when both its file and its name match (pytest entries have the same form); any other entry matches by name as today (research RF-12). For a self-check run: a test is `passed` when an `ok <file>::<name>` line names it, `failed` when a `FAIL` line does, and with no line `failed` when the suite exits non-zero (it is not run alone, since the suite's runner can't be addressed per test), `didn't run` when it exits 0 or the test has no `def` line.
- Rules: `crashed` is not set by one file's `ran 0 tests` line in a self-check suite: results are read per test. "record a test `passed` when an `ok` line names its file and name, `failed` when a `FAIL` line does, and, with no line for it, `failed` when the suite exits non-zero" (FR-8). A suite with no self-check line keeps today's unreadable-runner reading (C-261030-gk3z).

### CT-5 Worker card (FR-6) [agent]
- Binding: `src/nio/agents/worker.md` (existing)
- Kind: file
- Shape: the card's Job section gains: run a test command scoped to the task's own tests, `<test file> <test name> ...`, the names taken from the `File:` lines of the pack's `## Tests` entries; iterate with it and hand off that command; run it in the foreground, never in the background and never polled with sleep (the short wait on `try again` stays, research RF-14); in the code phase, read red's output the orchestrator passes on and make the first edit before running the tests.
- Rules: "to iterate with and hand off a command scoped to its own tests (the test names its pack's TC entries give in their `File:` lines), to run it in the foreground without polling it with sleep (the short wait on `try again` stays), and not to re-run the tests before its first edit" (FR-6).

### CT-6 Implement skill passes red's tail on (FR-7) [agent]
- Binding: `skills/implement/SKILL.md` (existing)
- Kind: file
- Shape: the split-mode step gains the sentence: "Give the code-phase worker the `output:` lines `nio flow red` printed, with the pack."
- Rules: "for the orchestrator to hand to the code-phase worker with the pack" (FR-7).

### CT-7 The runner reads self-check output (FR-4, FR-8) [agent]
- Binding: `src/nio/implement.py:runner` (existing)
- Kind: function
- Shape: `runner(command, output="") -> name | None`, with `RUNNERS` and `SUMMARY` in the same file
- Accepts: the command, and once it ran, its output.
- Returns: the runner the command's words name (as today); else `"self-check"` when the output has a line matching `^ran \d+ tests?, \d+ failed$` (re.M); else None. `RUNNERS["self-check"]` is `{"match": r"(?!)", "error": [], "none": ["ran 0 tests"]}`, plain substrings like every other entry, read by `wrong_reason` unchanged; `SUMMARY["self-check"]` is `(r"^FAIL (\S+)", r"^ran (\d+) tests?")`. `suite()` passes its output to `runner` and sums every count line's number (the suite prints one per file), so `collected` is the suite's total.
- Rules: "\"none\" is a `ran 0 tests` line (FR-4)" (spec, decision table "red outcome").

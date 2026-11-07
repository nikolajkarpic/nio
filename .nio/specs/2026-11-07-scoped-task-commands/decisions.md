# Decisions: 2026-11-07-scoped-task-commands

Every design choice of this effort, made by the orchestrator under the human's standing delegation (take the recommended option). Grill = `grill.md`, plan = `plan.md`, research = `research.md`.

| Decision | Options considered | Chosen | Why | Consequence |
| --- | --- | --- | --- | --- |
| #84: how red finds the test file in a single-test command (grill lookup, RF-3) | parse the first `tests/*.py` token; leave red as is and let the scripts take names | leave red as is | red already matches the file path as a substring; the refusals came from `python -c` workarounds the scripts forced | no CLI change for #84; it closes with FR-1 |
| Where the worker gets the test names (grill Q1) | names in the TC entries' `File:` lines; a new pack "Command" line; the worker chooses | TC `File:` lines | the pack already carries them (RF-5) | no pack format change; the card points at them |
| #88's single "suite red" fix task (grill Q2) | leave out; build a new finding kind; fail the gate on any suite failure | leave out | per-test results already stop the per-AC fix tasks (RF-8) | a suite failure outside the epic files raises no finding; the suite result still shows in evidence |
| How red's output reaches the code-phase worker (grill Q3) | red prints the last 20 lines; append a section to the pack; store output in history | red prints | the pack is written at claim, before red (RF-7) | the orchestrator passes the tail on; pack and history unchanged |
| A scoped command that runs no test (grill Q4) | refuse "no tests ran"; accept; warn | refuse | a typo'd name must not make red vacuous | a typo costs one attempt |
| Speed target (NFR-1, call) | under 15 s per red and green; none; under 5 s | under 15 s | uv start plus one test; RF-4 has 11–94 s per file | measured before and after for the PR |
| Spec jury fix: how red tells zero tests (grill Q5) | a last `ran <n> tests, <m> failed` line, checked before the exit code; count ok/FAIL lines; unknown name prints FAIL | `ran` line, checked first | one line red and evidence both read; a typo can't pass as red | a crash before the `ran` line reads as an unreadable runner at red, as today |
| Spec jury fix: result line names its file (grill Q6) | `ok <file>::<name>`; require unique names; bare names | `<file>::<name>` | pytest's own form; same-named tests in two files don't collide | evidence matches file and name |
| Spec jury fix: a crashed file's tests (grill Q7) | `failed` on a non-zero suite; new `didn't run` value; a red crash marker | `failed` | keeps C-261030-gk3z's rule for what printed no line | no new result value |
| Where the runner helper lives (plan) | `tests/selfcheck.py`; a `nio` module; copy into every file | `tests/selfcheck.py` | test-only code, outside the suite glob, importable from every script | one new file; target projects copy it if they want per-test lines |
| How a script hands its tests over (plan, RF-10) | the script's own list; definition order from `globals()` | the script's own list | 8 of 9 fixed lists differ from definition order | each `__main__` keeps its order, smallest diff |
| How red knows the runner (plan, RF-11) | from the output's `ran` line, after the run; from the command (`python tests/…`); a config key | from the output | a plain script command names no runner; no new config | `runner()` takes an optional output |
| Failing-entry match (plan, RF-12) | file and name when the entry has `::`; name only | file and name | fixes cross-file collisions for pytest too, one line | — |

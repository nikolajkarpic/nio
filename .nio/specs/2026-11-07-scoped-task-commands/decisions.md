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

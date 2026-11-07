---
slug: 2026-11-05-implement-followups
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: Implement follow-ups

## Contracts

### CT-1 `nio flow block` files a change record the memory check accepts (FR-1, FR-2, FR-16) [derived: FR-1, FR-2, FR-16, RF-1, RF-2]
- Binding: `src/nio/implement.py:block` (existing)
- Kind: cli
- Shape: `nio flow block <slug> T-n --handoff <file> --by "<role> / <host> / <model>"`
- Accepts: a handoff with `status: blocked` and a `change_request` holding `spec_says`, `code_shows` and `smallest_change`, each non-empty, with no line that starts with `## ` or is `---`.
- Returns: a new pending `C-` record, or the pending one holding `Handoff: <sha256>`, whose body is `## What is wrong` (the text `The spec says: <spec_says>`, a blank line, `The code shows: <code_shows>`), `## Proposed change` (`<smallest_change>` and the `Handoff:` line) and `## Human decision` (`Pending.`).
- Fails: an empty text → `error: handoff is not blocked with a change_request`, exit 1, nothing filed; a text with a `## ` or `---` line → `error: the handoff's <key> holds the line "<line>"`, exit 1, nothing filed, task status unchanged.
- Rules: "the first two under `## What is wrong`, the third under `## Proposed change`" (FR-2); "name the line or the empty text, and file no record" (FR-16)

### CT-2 A task's own TC IDs (FR-3) [derived: FR-3, RF-7]
- Binding: `src/nio/tasks.py:own` (new)
- Like: `src/nio/tasks.py:ids`
- Kind: function
- Shape: `own(test_line: str) -> list[str]`
- Accepts: a task's `Test:` value.
- Returns: the TC IDs of the line, in order, without those that appear only in a `;`-separated part holding "proved later".
- Rules: "a TC ID is the task's own unless it appears only in the part of the `Test:` line that says a later task proves it" (FR-3)

### CT-3 Red's file check reads own TC IDs (FR-3, FR-4, FR-5) [derived: FR-3, FR-4, FR-5, RF-5, RF-6]
- Binding: `src/nio/implement.py:test_files` (existing)
- Also: `src/nio/implement.py:tasks_of` gains `own` per task.
- Kind: function
- Shape: `test_files(root, slug, task) -> list[str]`, the files of `task["own"]`'s TC entries; `red` refuses when the list is non-empty and the command names none of them.
- Returns: the `File:` paths of the task's own TC IDs only; `task["tests"]` stays every TC ID on the line, for the pack.
- Fails: a command naming none of the files → refused `the command doesn't name <file> or <file>`, a `refused` line, an attempt used.
- Rules: "require it to name at least one file of the task's own TC IDs" (FR-3); "name only those files in the refusal" (FR-4)

### CT-4 Tasks added under Fixes since the judged version (FR-6, FR-7, FR-8) [derived: FR-6, FR-7, FR-8, RF-9, RF-19]
- Binding: `src/nio/jury.py:fixes_added` (new)
- Like: `src/nio/jury.py:diff`
- Kind: function
- Shape: `fixes_added(root, slug, gate) -> list[str]`
- Also: `src/nio/jury.py:collect` records, next to each round's judged version, the IDs of the tasks under `#### Fixes` in `tasks.md` at that moment, as `led["fixes"][<round>]`; the judged version itself stays the planned text, so approval and `changed` are untouched.
- Returns: at the tasks gate, the IDs of tasks under `#### Fixes` in the current `tasks.md` that are not in `led["fixes"]` of the last collected round (a ledger without that key counts as none recorded); `[]` at every other gate.
- Rules: "without naming a lens to re-run for them" (FR-7); `changed`'s IDs and lenses to re-run are computed as today, so a fix task never re-runs a lens or withdraws an approval (FR-8).

### CT-5 The fix-check pack shows added fix tasks (FR-6) [derived: FR-6]
- Binding: `src/nio/jury.py:fixcheck` (existing)
- Kind: function
- Shape: when `fixes_added` is non-empty, the pack gains `## Tasks added under Fixes (current text)` holding each one's block from `tasks.show`; otherwise the pack is unchanged.

### CT-6 `nio jury changed` lists added fix tasks (FR-7) [derived: FR-7]
- Binding: `src/nio/cli.py:main` (existing)
- Kind: cli
- Shape: `nio jury changed <slug> <gate>` prints, after its four lines, `added under Fixes: <T-n, ...>` when `fixes_added` is non-empty; nothing more otherwise. That line is the list of added fix tasks FR-7 asks for; the `changed:` line keeps only judged IDs, so no lens re-runs for a fix task.

### CT-7 `nio check tasks --rated-from` (FR-9) [derived: FR-9]
- Binding: `src/nio/tasks.py:rated_from` (new)
- Also: `src/nio/cli.py:main` gains `--rated-from <copy>` on `nio check`.
- Like: `src/nio/tasks.py:check`
- Kind: cli
- Shape: `nio check tasks <slug> --rated-from <copy>`; `rated_from(root, slug, copy) -> list[str]` errors
- Accepts: a copy of `tasks.md` taken before rating.
- Returns: exit 0 when every differing line pair is a `- Tier:`, `- Effort:` or `- Mode:` line and none reads `to be rated`.
- Fails: a non-rating line differs, or the line counts differ → `<path>:<line>: not a rating line: "<line>"`; a rating line reads `to be rated` → `<path>:<line>: not rated`.
- Rules: `--rated-from` adds `rated_from`'s errors to `tasks.check`'s; the CLI prints them through the existing `ERROR <error>` lines and the `N errors` total, and exits 1 when there is any.

### CT-8 The evaluator edits in place only (FR-10) [derived: FR-10, RF-10, RF-21]
- Binding: `src/nio/agents/evaluator.md` (existing)
- Also: `src/nio/agents.py:TOOLS` gains `patch: ["Edit"]`.
- Kind: config
- Shape: the card's `tools: [read, patch]`, and in `## How to rate` the line "Edit each task's `Tier:`, `Effort:` and `Mode:` lines in place, one edit per line; never write `tasks.md` whole."

### CT-9 The test runner strips `NIO_PERF` (FR-11) [derived: FR-11, RF-20]
- Binding: `src/nio/implement.py:run` (existing)
- Kind: function
- Shape: `run(root, command, limit)` runs the command with the caller's environment minus `NIO_PERF`.

### CT-10 The status-speed test (FR-15) [derived: FR-15]
- Binding: `tests/test_flow.py:status_speed` (new)
- Like: `tests/test_flow.py:test_nfr3_status_speed`
- Also: `test_nfr3_status_speed` calls it.
- Kind: function
- Shape: `status_speed(clock=time.perf_counter) -> str`, returning status's output after checking exit 0 and 20 lines
- Rules: "check status's output for the 20 efforts, and assert the 2-second limit only when `NIO_PERF=1` is set" (FR-15)
- Fails: with `NIO_PERF=1` and more than 2 seconds → `AssertionError` whose message names "2 seconds".

### CT-11 The tasks skill checks the evaluator's diff (FR-17) [derived: FR-17]
- Binding: `skills/tasks/SKILL.md` (existing)
- Kind: file
- Shape: step 3 starts a run with `nio run`, copies `tasks.md` to `.nio/runs/<run>/tasks.before.md` before the evaluator, and runs `nio check tasks <slug> --rated-from <copy>` after it, sending a failure back to the evaluator once.

### CT-12 The status-speed self-check is listed (FR-18) [derived: FR-18]
- Binding: `CLAUDE.md` (existing)
- Kind: file
- Shape: the line "`NIO_PERF=1 uv run python tests/test_flow.py` asserts the status-speed limit; run it after a change to `nio flow status`."

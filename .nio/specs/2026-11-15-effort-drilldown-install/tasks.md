---
slug: 2026-11-15-effort-drilldown-install
retired: [T-4]                      # task IDs removed from this file; never reused
---
# Tasks: Effort drill-down in the NIO pane, and @nio:install installs the Claude Code mods

## E-1 Drill-down shell: `flow show`, which `nio` the pane runs, and the pane's drill-down (Foundation)

### T-1 Add `nio flow show <slug> --json` and `flow.show` with its error cases; each of the five section keys is an empty placeholder (`[]`, cost `"-"`) until its own task fills it
- Files: `src/nio/cli.py`, `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-1, AC-29
- Test: TC-26
- Depends on: none
- Parallel: yes
- Tier: strong: new CLI command with error cases and section placeholders, clear tests
- Effort: med
- Mode: split: behaviour a test can lead

### T-2 Pane picks its `nio` (`nioFor`) and the pane types gain `path` and `drill`
- Files: `tools/claude-mods/nio-status-pane/hooks/register.tsx`, `tools/claude-mods/nio-status-pane/types/index.d.ts`, `tools/claude-mods/nio-status-pane/hooks/register.test.tsx`
- Serves: AC-1, AC-24
- Test: TC-29
- Depends on: none
- Parallel: yes
- Tier: strong: pane logic choosing a binary, clear test
- Effort: low
- Mode: split: behaviour a test can lead

### T-3 Pane drill-down: select a row (including a broken one), draw the timeline rows, Back, errors, old-nio message, no actions (the one task that draws the timeline)
- Files: `tools/claude-mods/nio-status-pane/hooks/register.tsx`, `tools/claude-mods/nio-status-pane/types/index.d.ts`, `tools/claude-mods/nio-status-pane/hooks/register.test.tsx`
- Serves: AC-1, AC-4, AC-5, AC-29, AC-30
- Test: TC-2, TC-6, TC-27, TC-28, TC-35, TC-37
- Depends on: T-1, T-2
- Parallel: no
- Tier: strong: UI state and several error paths, clear tests
- Effort: med
- Mode: split: behaviour a test can lead

#### Fixes

### T-16 Fix: land T-4's pane tests as regression guards (T-4 retired, already delivered by T-3)
- From: C-261115-duou
- Files: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx`
- Serves: AC-9, AC-11, AC-13, AC-16, AC-17
- Test: TC-10, TC-12, TC-15, TC-18, TC-19
- Depends on: none
- Parallel: no
- Tier: cheap: tests over existing behaviour
- Effort: low
- Mode: direct: the behaviour exists; the tests guard it

## E-2 Select an effort and see its timeline (US-1)

### T-5 Build the timeline section from history (stage changes, failed reviews, `-` for missing fields) and wire it into `show`
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-1, AC-2, AC-3, AC-4
- Test: TC-1, TC-3, TC-4
- Depends on: T-1, T-3
- Parallel: no
- Tier: strong: history parsing with clear tests
- Effort: low
- Mode: split: behaviour a test can lead

### T-6 Pane shows a failed review's reasons under its timeline row, and the drill-down tests run on T-5's real `flow show` output shape (T-3's timeline drawing, Back, error and old-nio rows are reused, not redrawn)
- Files: `tools/claude-mods/nio-status-pane/hooks/register.tsx`, `tools/claude-mods/nio-status-pane/hooks/register.test.tsx`
- Serves: AC-1, AC-5, AC-24, AC-29, AC-30
- Test: TC-2
- Depends on: T-16, T-5
- Parallel: no
- Tier: strong: rendering real output, follows existing pane pattern
- Effort: low
- Mode: split: behaviour a test can lead

## E-3 See the effort's juries (US-2)

### T-7 Build the juries section from the committed ledgers (rounds, lenses, verdicts, findings, fix tasks) and wire it into `show`
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-6, AC-7, AC-8, AC-9
- Test: TC-7, TC-8, TC-9, TC-38
- Depends on: T-16, T-5
- Parallel: no
- Tier: strong: ledger parsing across rounds and lenses, clear tests
- Effort: med
- Mode: split: behaviour a test can lead

## E-4 See the effort's tasks (US-3)

### T-8 Build the tasks section per epic with status and attempts and wire it into `show`
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-10, AC-11
- Test: TC-11, TC-39
- Depends on: T-16, T-7
- Parallel: no
- Tier: strong: ordinary section build with clear tests
- Effort: low
- Mode: split: behaviour a test can lead

## E-6 See the effort's memory and context use (US-5)

### T-11 Build the memory section from front matter and wire it into `show`
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-15, AC-16, AC-17
- Test: TC-17
- Depends on: T-16, T-8
- Parallel: no
- Tier: strong: front-matter reading with a clear test
- Effort: low
- Mode: split: behaviour a test can lead

## E-5 See the cost so far (US-4)

### T-9 Add `usage.so_far`: tokens and seconds per stage window and per jury, unattributed, total, `-` when nothing recorded
- Files: `src/nio/usage.py`, `tests/test_usage.py`
- Serves: AC-12, AC-14, AC-28
- Test: TC-13, TC-14, TC-16
- Depends on: T-1
- Parallel: yes
- Tier: strong: time-window attribution logic with clear tests
- Effort: med
- Mode: split: behaviour a test can lead

### T-10 Wire the cost section into `show`; check no file is written and the 5-second limit
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-13, AC-23
- Test: TC-5, TC-25, TC-33, TC-34
- Depends on: T-16, T-8, T-9, T-11
- Parallel: no
- Tier: strong: wiring plus no-write and speed checks, clear tests
- Effort: low
- Mode: split: behaviour a test can lead

## E-7 @nio:install installs the mods on Claude Code (US-6)

### T-12 Ship the mods in the wheel and add `hooks.mods_dir`
- Files: `src/nio/hooks.py`, `pyproject.toml`, `tests/test_hooks.py`
- Serves: AC-25
- Test: TC-30
- Depends on: none
- Parallel: yes
- Tier: cheap: packaging config and a small path helper
- Effort: low
- Mode: single: tiny change, one worker proves red and green

### T-13 Add `hooks.mods_install` and the `nio mods install [--skip]` command
- Files: `src/nio/hooks.py`, `src/nio/cli.py`, `tests/test_hooks.py`
- Serves: AC-18, AC-19, AC-20, AC-21, AC-26
- Test: TC-20, TC-21, TC-22, TC-23, TC-36
- Depends on: T-12
- Parallel: no
- Tier: strong: file copying into user config with skip and failure paths, clear tests
- Effort: med
- Mode: split: behaviour a test can lead

### T-14 Add the mods step to the install skill, on Claude Code only, with one question
- Files: `skills/install/SKILL.md`, `tests/test_hooks.py`
- Serves: AC-22, AC-26
- Test: TC-24, TC-31
- Depends on: T-13
- Parallel: no
- Tier: cheap: one skill step following the existing skill format
- Effort: low
- Mode: single: text edit plus a check on it, one worker

### T-15 Describe the mods as optional in the READMEs and the project docs
- Files: `README.md`, `tools/claude-mods/README.md`, `tools/claude-mods/nio-status-pane/README.md`, `tools/claude-mods/background-nio-commands/README.md`, `.nio/project/architecture.md`, `.nio/project/stack.md`, `tests/test_hooks.py`
- Serves: AC-27
- Test: TC-32
- Depends on: T-13
- Parallel: yes
- Tier: cheap: docs wording only
- Effort: low
- Mode: direct: docs, no test first


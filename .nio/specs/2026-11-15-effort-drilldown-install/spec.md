---
slug: 2026-11-15-effort-drilldown-install
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, OP-10, OP-11, OP-12, OP-13]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-15-effort-drilldown-install` checks all of this. -->
# Effort drill-down in the NIO pane, and @nio:install installs the Claude Code mods

## Summary
Finding out how an effort ran, what it cost and how many juries it took means reading `state.json`, `history.jsonl`,
`.nio/runs/` and `nio usage` by hand, or spending a model turn on it. This spec adds a drill-down to the
`nio-status-pane` effort pane: pick one effort and see its timeline, juries, tasks, cost so far, the memory that
applies to it and, where the host exposes it, the session's context use, with no model turn. It also makes
`@nio:install` on Claude Code install the NIO Claude Code mods (`background-nio-commands`, `nio-status-pane`), so
nobody has to add the marketplace and install them by hand, which is easy to miss. [human]

## Actors and journeys
- **A-1 Effort owner**: a developer driving efforts through NIO in Claude Code with the pane open; wants to see how an effort ran and what it cost without reading files or spending a model turn. P-1. [research: RF-1]
- **A-2 Teammate**: a developer reviewing an effort someone else started; wants the same view of its history and juries. P-2. [research: RF-1]
- **A-3 Maintainer**: whoever runs `@nio:install` in a repo on Claude Code; wants the mods set up without manual `claude plugin` commands. P-3. [research: RF-1]

**UJ-1 Inspect how an effort ran** (A-1, A-2) [research: RF-6]
1. The pane lists the active efforts, one row each.
2. The human selects one effort.
3. The pane shows its timeline, juries, tasks, cost so far, memory and (if available) context use.
4. The human goes back to the list.
- Misuse: expecting the drill-down to change the effort (approve, retry, abandon); it only reads.
- A teammate (A-2) sees only the efforts whose files are in their own clone's worktrees, as the pane lists them today; an effort not there is not listed. [agent]
- Evidence: issue #142.

**UJ-2 Install NIO with the mods** (A-3) [research: RF-2]
1. The maintainer runs `@nio:install` in a repo on Claude Code.
2. Install asks once whether to install the mods, and installs both unless the maintainer skips them.
3. The closing message says which mods were installed or skipped.
- Trade-off: the mods install for one clone only, so each teammate's clone runs `@nio:install` once (or `nio mods install`) to get them; nothing is committed for the team. [agent]
- Misuse: running install on a host other than Claude Code and expecting the mods.
- Evidence: issue #142; the pane was left out of the marketplace until a fix PR.

## User stories

### US-1 Select an effort and see its timeline (P1) [human]
- **Why this priority:** the timeline is the backbone of "how did it run"; every other section hangs off the same selection.
- **Independent test:** with an effort whose `history.jsonl` holds several stage changes and one failed review, select it in the pane and read each change and the failed review's reason, with no model turn.

- **AC-1** (FR-1, FR-2) Given an active effort with three stage changes in its history, when the human selects its row in the pane, then the drill-down lists the three changes in order, each with from, to, role, host, model and time. [human]
  Observable: the rendered drill-down holds three timeline rows matching the history entries field by field, and no model call is made. Level: integration.
- **AC-2** (FR-3) Given a history with a `review` entry whose `evidence.passed` is false, when the drill-down is shown, then that review appears in the timeline with its reasons; a failed review with no reasons shows `-`. [human]
  Observable: the timeline row for the failed review contains each text of `evidence.reasons`, or `-` when the list is empty. Level: integration.
- **AC-3** (FR-12) Given a history entry without a host or model, when the drill-down is shown, then those fields read `-`. [agent]
  Observable: the row shows `-` in the host and model fields. Level: unit.
- **AC-4** (FR-13) Given an effort whose `history.jsonl` has an unreadable line, when the drill-down is shown, then the timeline names the error and the other sections still render. [agent]
  Observable: the timeline section holds an error line; the juries, tasks, cost and memory sections are present. Level: integration.
- **AC-5** (FR-14) Given the drill-down is open, when the human goes back, then the effort list is shown again. [agent]
  Observable: the pane renders the list rows after the back action. Level: integration.

### US-2 See the effort's juries (P1) [human]
- **Why this priority:** "how many juries it took" is one of the two questions the issue names as costly today.
- **Independent test:** with an effort that ran two rounds of a spec jury with one confirmed finding that led to a fix task, select it and read both rounds, their lenses, verdicts, the finding and its fix task.

- **AC-6** (FR-4) Given an effort with a spec gate jury of two rounds, when the drill-down is shown, then the juries section lists that gate with both rounds, each round's lenses and their verdicts. [human]
  Observable: the section names the gate, two rounds, and each lens with its verdict as recorded in the run files. Level: integration.
- **AC-7** (FR-5) Given a round with one finding raised and confirmed by the refuter and one refuted, when the drill-down is shown, then both findings appear, marked raised and confirmed or refuted, and the confirmed one names the fix task it led to. [human]
  Observable: two finding rows; the confirmed one carries the fix task's ID. Level: integration.
- **AC-8** (FR-4) Given an effort that ran several gates, when the drill-down is shown, then each gate's runs are listed under that gate. [human]
  Observable: one group per gate, each holding only its own runs. Level: integration.
- **AC-9** (FR-12) Given an effort with no jury run yet, when the drill-down is shown, then the juries section says there are none. [agent]
  Observable: the section holds a "no juries yet" line and no error. Level: unit.

### US-3 See the effort's tasks (P2) [human]
- **Why this priority:** useful once an effort is implementing; earlier stages have no tasks.
- **Independent test:** with an effort in `implementing` with one task done, one claimed and one failing, read each with its status and attempts grouped by epic.

- **AC-10** (FR-6) Given an implementing effort with two epics, when the drill-down is shown, then the tasks are grouped by epic, each marked done, claimed or failing, with its attempts from `state.json`. [human]
  Observable: each task row's status and attempt count equal the values in `state.json`. Level: integration.
- **AC-11** (FR-12) Given an effort with no tasks yet, when the drill-down is shown, then the tasks section says there are none. [agent]
  Observable: the section holds a "no tasks yet" line. Level: unit.

### US-4 See the cost so far (P1) [human]
- **Why this priority:** "what it cost" is the other costly question, and it needs a new live figure before the pane can show it.
- **Independent test:** in an effort still running with recorded usage events, ask the `nio` CLI for the cost so far, and see the same figures in the drill-down.

- **AC-12** (FR-7, FR-8) Given an unfinished effort with usage recorded in two finished stages, the open current stage and one jury, when the `nio` CLI is asked for its cost so far, then it reports tokens and time per stage and per jury, without writing the effort's `usage.json`. [human]
  Observable: the output holds one figure per stage, the open stage's counted up to the call, and per jury; `usage.json` is absent after the call. Level: integration.
- **AC-28** (FR-7) Given an effort that entered `implementing` twice and has usage events before its first history entry, when its cost so far is asked for, then `implementing` shows the sum of both visits, the early events show under `unattributed`, and the stage figures add up to the total. [agent]
  Observable: the `implementing` figure equals the events of both windows; an `unattributed` row holds the early events; the stages plus `unattributed` equal the total; the jury figures are not added to it again. Level: integration.
- **AC-13** (FR-9) Given that live figure, when the drill-down is shown, then its cost section shows the same tokens and time per stage and per jury. [human]
  Observable: the pane's figures equal the CLI's. Level: integration.
- **AC-14** (FR-12) Given an effort with no usage recorded, when the cost is asked for, then each figure reads `-` rather than zero. [agent]
  Observable: the cost section shows `-` for tokens and time. Level: unit.

### US-5 See the effort's memory and context use (P3) [human]
- **Why this priority:** context for the effort rather than its history; the context figure depends on what the host exposes.
- **Independent test:** select an effort that has applying memory records and read their IDs and titles in the drill-down.

- **AC-15** (FR-10) Given an effort with memory records that apply to it, when the drill-down is shown, then the memory section lists those records with their ID, kind, standing and title. [human]
  Observable: the listed IDs equal the records whose front matter `paths` name a file under `.nio/specs/<slug>/` or whose `against` names the slug, and no record outside that set is listed. Level: integration.
- **AC-16** (FR-11) Given the host exposes the session's context use, when the drill-down is shown, then it shows that figure. [human]
  Observable: the context line holds the host's value. Level: integration.
- **AC-17** (FR-11) Given the host does not expose context use, when the drill-down is shown, then no context section is shown and nothing else is affected. [agent]
  Observable: no context line; the other sections render. Level: unit.

### US-6 @nio:install installs the mods on Claude Code (P1) [human]
- **Why this priority:** without the mods installed, nobody sees the pane or the drill-down.
- **Independent test:** run `@nio:install` in a fresh repo on Claude Code and find both mods installed and named in the closing message.

- **AC-18** (FR-15, FR-17) Given a repo on Claude Code without the mods, when `@nio:install` runs and the human does not skip them, then both mods are installed and the closing message names each as installed. [human]
  Observable: Claude Code lists both mods as installed; the closing message names both. Level: e2e.
- **AC-19** (FR-16, FR-17) Given the human chooses to skip the mods, when install finishes, then neither mod is installed and the closing message says they were skipped. [human]
  Observable: neither mod is listed as installed; the closing message names both as skipped. Level: e2e.
- **AC-20** (FR-18) Given the mods are already installed, when `@nio:install` runs again, then they are not installed twice and the closing message says they were already installed. [agent]
  Observable: one install entry per mod; the closing message says "already installed". Level: e2e.
- **AC-21** (FR-19, FR-29) Given a fake `claude` on PATH that fails for one mod, when `nio mods install` runs, then the other mod is still installed and the failed one's line names it and its error, and the command exits 0. [agent]
  Observable: the command's output holds `failed` with the mod's name and the error text, and an `installed` line for the other mod; exit code 0. Level: integration.
- **AC-22** (FR-20) Given the `@nio:install` skill text, when read, then its mods step is conditioned on Claude Code, and the skill's other steps never mention the mods. [agent]
  Observable: a test reading `skills/install/SKILL.md` finds the mods step under a Claude Code condition and no other step naming the mods. Level: unit.

- **AC-23** (FR-21) Given an unfinished effort with history, a jury ledger, tasks and usage events, when `nio flow show <slug> --json` runs, then it prints one JSON object with the keys timeline, juries, tasks, cost and memory, and no file outside `.nio/cache/` changes. [agent]
  Observable: the output parses as JSON with those five keys; `git status --porcelain` is unchanged (`.nio/cache/` is ignored) and `usage.json` is absent. Level: integration.
- **AC-29** (FR-27) Given a slug that is unknown or of a finished effort, when `nio flow show <slug> --json` runs, then it prints `{"error": ...}` naming the reason and exits 1, and the pane shows that reason with a Back button. [agent]
  Observable: exit code 1; the output parses as JSON with an `error` key; the pane's drill-down holds the reason. Level: integration.
- **AC-30** (FR-28) Given the `nio` the pane runs exits with an unknown-command error for `flow show`, when an effort is selected, then the drill-down reads `this nio has no flow show: update nio`. [agent]
  Observable: that line and a Back button in the drill-down. Level: unit.
- **AC-24** (FR-23) Given a worktree with no `.venv/bin/nio` and a `nio` on PATH, when the pane refreshes, then it lists that worktree's efforts from the PATH `nio`; with neither, the row reads `nio not found`. [agent]
  Observable: the pane's rows for that worktree; the process run names the PATH `nio`. Level: unit.
- **AC-25** (FR-22) Given the `nio` package built as a wheel, when its contents are listed, then both mods' plugin folders and the marketplace file are in it. [agent]
  Observable: the wheel holds `nio/mods/.claude-plugin/marketplace.json` and both mods' `.claude-plugin/plugin.json`. Level: integration.
- **AC-26** (FR-24, FR-25, FR-29) Given a fake `claude` on PATH, when `nio mods install` runs, then each mod is installed with `--scope local` from the package's mods folder; and the `@nio:install` skill text holds exactly one question about the mods. [agent]
  Observable: the fake `claude` records `--scope local` and the package's mods path for each mod; a test reading `skills/install/SKILL.md` finds one mods question. Level: integration.

- **AC-27** (FR-26) Given the README and both mods' READMEs, when read, then each describes the mods as an optional Claude Code part of NIO that the skills do not need, and none calls them dev tooling only. [agent]
  Observable: no "not part of the NIO product" line remains; each README holds the optional wording. Level: unit.

## Functional requirements
- **FR-1** WHEN the human selects one of the active efforts the pane lists THE SYSTEM SHALL show that effort's drill-down without a model turn. [human]
- **FR-2** WHEN the drill-down is shown THE SYSTEM SHALL list each stage change from the effort's `history.jsonl` in order, with from, to, role, host, model and time. [human]
- **FR-3** WHEN the effort's history holds a failed review (a `review` entry whose `evidence.passed` is false, RF-9) THE SYSTEM SHALL show it in the timeline with its `evidence.reasons`, or `-` when none are recorded. [human]
- **FR-4** WHEN the drill-down is shown THE SYSTEM SHALL list, per gate, every jury run with its rounds, lenses and verdicts. [human]
- **FR-5** WHEN a jury round raised findings THE SYSTEM SHALL show each finding, whether the refuter confirmed it, and the fix task it led to. [human]
- **FR-6** WHEN the drill-down is shown THE SYSTEM SHALL list the effort's tasks per epic as done, claimed or failing, with their attempts from `state.json`. [human]
- **FR-7** WHEN asked for an unfinished effort's cost so far THE SYSTEM SHALL report the tokens used so far per stage and per jury, a stage's share being the events between each entry into it and the next stage change in `history.jsonl`, summed over every visit, the open current stage counted up to now; events in no stage window show as `unattributed`; a jury's share is the juror and refuter agents whose run belongs to that gate, shown as a breakdown inside its stage and never added to the total again. [human]
- **FR-8** WHEN asked for an unfinished effort's cost so far THE SYSTEM SHALL report the time spent so far per stage and per jury. [human]
- **FR-9** WHEN the drill-down is shown THE SYSTEM SHALL show the effort's cost so far from the live figure of FR-7 and FR-8. [human]
- **FR-10** WHEN the drill-down is shown THE SYSTEM SHALL list the memory records that apply to the effort: those whose `paths` name a file under the effort's spec folder or whose `against` names the effort, read from the records' front matter without loading the embedding model (not `nio pack` / `nio query`, which rank by relevance and load the model, RF-7). [agent]
- **FR-11** IF the host exposes the session's context use THEN THE SYSTEM SHALL show it in the drill-down; on Claude Code it is the context window's fill in percent, which the pane reads from the host (`$.session.usage()`, RF-5), not from `nio`. [human]
- **FR-12** IF a field or section has nothing recorded THEN THE SYSTEM SHALL show `-` for the field or a "no ... yet" line naming the section ("no juries yet", "no tasks yet", "no memory yet"). [agent]
- **FR-13** IF a source file of one section cannot be read THEN THE SYSTEM SHALL show the error in that section and still show the other sections. [agent]
- **FR-14** WHEN the human leaves the drill-down THE SYSTEM SHALL show the effort list again. [agent]
- **FR-15** WHEN `@nio:install` runs on Claude Code THE SYSTEM SHALL install the `background-nio-commands` and `nio-status-pane` mods unless the human chose to skip them. [human]
- **FR-16** IF the human chose to skip the mods THEN THE SYSTEM SHALL install neither. [human]
- **FR-17** WHEN `@nio:install` finishes on Claude Code THE SYSTEM SHALL say in its closing message, for each mod, whether it was installed, skipped, already installed or failed. [human]
- **FR-18** IF a mod is already installed THEN THE SYSTEM SHALL leave it as it is. [agent]
- **FR-19** IF a mod fails to install THEN THE SYSTEM SHALL finish the rest of the install and report the failure. [agent]
- **FR-20** WHILE `@nio:install` runs on a host other than Claude Code THE SYSTEM SHALL not install or offer the mods. [agent]
- **FR-21** WHEN asked with `nio flow show <slug> --json` THE SYSTEM SHALL print, as one JSON object, the effort's timeline, juries, tasks, cost so far and memory, writing no file except the caches NFR-2 allows; the pane draws those five sections from that output only. [agent]
- **FR-27** IF `nio flow show <slug> --json` is asked for a slug that is not an active effort THEN THE SYSTEM SHALL print one JSON object whose `error` key names the reason, and exit 1, and the pane shows that reason in the drill-down with its Back button. [agent]
- **FR-28** IF the `nio` the pane runs has no `flow show` command THEN THE SYSTEM SHALL show `this nio has no flow show: update nio` in the drill-down, with its Back button. [agent]
- **FR-22** THE SYSTEM SHALL ship the mods inside the installed `nio` package, so a project with an installed `nio` and no NIO checkout can install them. [agent]
- **FR-23** IF a worktree has no `.venv/bin/nio` THEN THE SYSTEM SHALL have the pane run the `nio` found on PATH, and show `nio not found` only when neither exists. [agent]
- **FR-24** WHEN `@nio:install` runs on Claude Code THE SYSTEM SHALL ask once whether to install the mods, offering install (recommended) and skip, each saying what happens. [agent]
- **FR-25** WHEN the mods are installed THE SYSTEM SHALL install them for this clone only (Claude Code's `local` scope), changing no file to commit. [agent]
- **FR-29** WHEN `nio mods install [--skip]` runs THE SYSTEM SHALL install each mod not already installed through `claude plugin install`, and print one line per mod with its outcome (installed, skipped, already installed, failed with the error), exiting 0; `@nio:install` runs it after the mods question and quotes its lines in the closing message. [agent]
- **FR-26** THE SYSTEM SHALL describe the mods in the README and their own READMEs as an optional Claude Code part of NIO, with the skills working the same without them. [agent]

## Rules
### Decision table: mod outcome at install
| Host (claude, other) | Human choice (install, skip) | Already installed (yes, no) | Install result (ok, error) | → Outcome in closing message | Src |
| --- | --- | --- | --- | --- | --- |
| other | - | - | - | → not mentioned, nothing installed | [agent] |
| claude | skip | yes | - | → already installed (left as is) | [agent] |
| claude | skip | no | - | → skipped | [human] |
| claude | install | yes | - | → already installed | [agent] |
| claude | install | no | ok | → installed | [human] |
| claude | install | no | error | → failed, with the error; rest of install unaffected | [agent] |

## Key entities
- **Drill-down**: the per-effort view in the pane, with sections timeline, juries, tasks, cost, memory and context. [human]
- **Timeline entry**: one stage change: from, to, role, host, model, time, and a failed review's reason. [human]
- **Jury run**: one gate's run: rounds, lenses, verdicts, findings (raised, confirmed or refuted) and the fix tasks they led to. [human]
- **Cost so far**: tokens and time per stage and per jury for an unfinished effort, from the `nio` CLI. [human]
- **NIO Claude Code mods**: `background-nio-commands` and `nio-status-pane`, under `tools/claude-mods/` and shipped inside the `nio` package. [human]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL show the drill-down of an effort with 200 history entries and 10 jury runs within 5 seconds of the selection, the cost so far taking the most of it (1.4 s on a real effort, RF-4). [agent]
- **NFR-2** THE SYSTEM SHALL write no file when showing the drill-down or reporting cost so far, other than the caches the CLI already keeps under `.nio/cache/`. [agent]

## Success criteria
- **SC-1** In the pane, selecting an effort shows its timeline, juries, tasks, cost so far and memory, with no model turn. [human]
- **SC-2** `@nio:install` on Claude Code leaves both mods installed, or skipped by the human's choice, and says so in its closing message. [human]

## Non-goals
- Acting on an effort from the drill-down (approve, retry, park, abandon); it only reads. [agent]
- Installing the mods on hosts other than Claude Code. [agent]
- Changing when `usage.json` is written for a finished effort. [agent]

## Glossary
- **Pane**: the `nio-status-pane` side pane listing active efforts. Never "sidebar".
- **Mod**: an optional Claude Code plugin NIO ships, kept under `tools/claude-mods/` and in the installed `nio` package. Never "extension".
- **Cost so far**: tokens and time an unfinished effort has used. Never "live usage".

## Decisions
- The mods become an optional Claude Code part of the product; skills stay host-neutral (Q1). This rests on decision D-261115-e6nx, still uncommitted; if it changes, FR-22, FR-26 and the Mod glossary entry are re-checked. [agent]
- Target projects install the mods from a copy shipped inside the `nio` package; the pane falls back to the `nio` on PATH (Q2). [agent]
- Install asks once, install recommended, like the permissions question (Q3). [agent]
- The mods install for this clone only, the `local` scope (Q4): each teammate's clone runs install once; nothing is committed for the team (Q7). [agent]
- The memory section filters records by front matter, not through `nio pack` / `nio query` (Q8). [agent]
- Cost so far sums every visit to a stage, counts the open stage up to now, shows events outside any stage as `unattributed`, and shows jury cost as a breakdown inside its stage (Q9). [agent]
- The mod install runs as one CLI step, `nio mods install`, so its outcomes are testable; the skill asks the question and quotes the lines (Q10). [agent]
- The drill-down reads one new `nio flow show <slug> --json` command, not the files (Q5). [agent]
- The drill-down covers the active efforts the pane lists only (Q6). [agent]

---
slug: 2026-11-14-nio-status-pane
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-14-nio-status-pane` checks all of this. -->
# NIO effort pane, status line and /nio command (Claude Code mod)

## Summary
A Claude Code mod for whoever develops NIO: a side pane listing each active effort across the nio worktrees (stage
and status, jury round, claimed task, running jurors), a one-line version in the mod's status line, and a `/nio` slash
command that prints `nio flow status` for every nio worktree. Finding out where an effort stands today means asking a
model, which costs a turn and tokens; this mod answers with no model turn. It is dev tooling, Claude-only, and not
part of the NIO product. Cost so far, asked for in #131, is left out: no per-effort figure is recorded while an effort
runs (RF-6). [human]

## Actors and journeys
- **A-1 NIO developer**: runs several NIO efforts in parallel worktrees (six today) from Claude Code and wants to see where each stands without spending a model turn; fluent with git, Claude Code and the `nio` CLI. [research: RF-1]

**UJ-1 Glance at the pane** (A-1) [agent]
1. Opens Claude Code in any nio worktree; the side pane lists each active effort across the worktrees.
2. Works as usual; the pane and the status line refresh on their own.
3. Sees an effort reach a gate or wait for the human, and switches to that worktree.
- Misuse: reads a stale pane as live after a worktree is removed or a refresh fails.
- Evidence: issue #131.

**UJ-2 Ask with /nio** (A-1) [agent]
1. Types `/nio`.
2. Reads each worktree's effort state, printed by the mod, with no model turn.
- Misuse: expects `/nio` to change flow state (it only reads).
- Evidence: issue #132.

## User stories

### US-1 See every active effort in a side pane (P1) [human]
- **Why this priority:** it is the core of #131 and its done-when: knowing where efforts stand without a model turn.
- **Independent test:** with three efforts running in three worktrees, open the pane and see all three rows update as their flow state changes, with no model turn in the transcript.

- **AC-1** (FR-1, FR-2, FR-3) Given efforts #123, #49 and #122 active in their worktrees, when the pane is open, then it shows one row per effort with its stage and status, jury round, claimed task and running jurors. [human]
  Observable: the pane lists the three efforts' slugs, each with the four fields. Level: e2e.
- **AC-2** (FR-4) Given the pane is open, when an effort's flow state changes, then the pane shows the new state within one refresh interval, with no model turn. [human]
  Observable: the row changes within the interval; the session's token usage is unchanged. Level: e2e.
- **AC-3** (FR-5) Given a worktree whose effort is done or abandoned, when the pane refreshes, then that effort is not listed. [agent]
  Observable: the effort's slug is absent from the pane. Level: integration.
- **AC-4** (FR-6) Given one worktree where `nio flow status` fails or reports a broken effort, when the pane refreshes, then that worktree shows the error on its row and the other worktrees are still listed. [agent]
  Observable: an error row for the failing worktree and normal rows for the rest. Level: integration.
- **AC-5** (FR-7) Given a field the effort's files don't record (no open jury, no claimed task, no juror without output), when the pane refreshes, then that field shows `-` instead of a stale or invented value. [agent]
  Observable: the cell reads `-`. Level: integration.
- **AC-14** (FR-13) Given an effort with a claimed task and an open jury round of the gate of its current stage, in which one juror has written its output and another has not, when the pane refreshes, then its row shows that task, that round and only the juror without output. [agent]
  Observable: the row's claimed task equals `claims.task` in state.json, its round is one more than the gate ledger's `round` (1 when the gate has no ledger yet), and its running jurors list exactly the lens with no output file. Level: integration.

### US-2 One-line summary in the status line (P2) [human]
- **Why this priority:** a cheaper glance than the pane, but secondary to it in #131.
- **Independent test:** with efforts running, the mod's status line under the prompt shows the one-line summary and it updates when an effort's state changes.

- **AC-6** (FR-8) Given active efforts, when the status line renders, then it shows a one-line summary of them. [human]
  Observable: the status line text names the active efforts' count and their stages. Level: e2e.
- **AC-7** (FR-8, FR-5) Given no active effort in any worktree, when the status line renders, then it shows that no effort is active. [agent]
  Observable: the status line reads a fixed "no active effort" text. Level: integration.

### US-3 /nio prints flow status for every worktree (P1) [human]
- **Why this priority:** it is #132's done-when and the on-demand counterpart to the pane.
- **Independent test:** type `/nio` and get each worktree's effort state printed in under 2 seconds with no tokens used.

- **AC-8** (FR-9) Given several nio worktrees, when the developer types `/nio`, then the mod prints `nio flow status` for each worktree, grouped by worktree, in under 2 seconds. [human]
  Observable: the output has one block per worktree; the elapsed time is under 2 s. Level: e2e.
- **AC-9** (FR-9) Given `/nio` is typed, when it answers, then no model turn runs and no tokens are used. [human]
  Observable: the session's token usage before and after `/nio` is equal. Level: e2e.
- **AC-10** (FR-6) Given one worktree where `nio flow status` fails, when `/nio` runs, then that worktree's block shows the error and the other blocks print normally. [agent]
  Observable: an error block for the failing worktree and normal blocks for the rest. Level: integration.
- **AC-11** (FR-10) Given the developer types `/nio` or the pane refreshes, when it finishes, then no file in any worktree has changed. [agent]
  Observable: `git status` and the file list under `.nio/` in each worktree are identical before and after. Level: integration.
- **AC-12** (FR-11) Given the mod is installed, when Claude Code starts in a nio worktree, then the pane, the status line and `/nio` are all available from that one mod. [human]
  Observable: the three surfaces are present after installing only this mod. Level: e2e.
- **AC-13** (FR-12) Given the mod is committed, when a maintainer reads its folder, then its README says how to turn it on per person, and the repo's settings files don't load it. [agent]
  Observable: `tools/claude-mods/nio-status-pane/README.md` exists and says how to turn it on; no `.claude/settings*.json` in the repo references the folder. Level: unit.

## Functional requirements
- **FR-1** THE SYSTEM SHALL find every worktree `git worktree list` reports for the repository the session is in. [research: RF-8]
- **FR-2** WHILE the pane is open THE SYSTEM SHALL list each active effort across the nio worktrees, one row per effort. [human]
- **FR-3** THE SYSTEM SHALL show, for each listed effort, its stage and status as `nio flow status` prints them, its jury round, its claimed task and its running jurors, each read only from that effort's worktree. [derived: RF-2, RF-3, RF-4, RF-5]
- **FR-4** WHEN the refresh timer fires THE SYSTEM SHALL re-read the effort state from `nio flow status` and update the pane and the status line, without a model turn. [human]
- **FR-5** THE SYSTEM SHALL treat a `nio flow status` row as an active effort unless its stage is done, its status is abandoned, or the row is not an effort (a legacy or unsupported folder). [agent]
- **FR-6** IF reading one worktree's state fails THEN THE SYSTEM SHALL show that worktree's error and keep showing the other worktrees. [agent]
- **FR-7** IF the effort's files don't record a field THEN THE SYSTEM SHALL show `-` for it. [agent]
- **FR-8** THE SYSTEM SHALL show a one-line summary of the active efforts in the mod's status line under the prompt. [research: RF-7]
- **FR-9** WHEN the developer types `/nio` THE SYSTEM SHALL print `nio flow status` for every nio worktree, answered by the mod with no model turn. [human]
- **FR-10** THE SYSTEM SHALL only read flow state and never write to any worktree. [agent]
- **FR-11** THE SYSTEM SHALL ship the pane, the status line and `/nio` as one mod. [human]
- **FR-12** THE SYSTEM SHALL live in this repo at `tools/claude-mods/nio-status-pane/`, be turned on per person, and change no settings itself. [agent]
- **FR-13** THE SYSTEM SHALL read the fields of FR-3 as follows: a jury round is open when a jury run's packs, for the gate of the effort's current stage (`spec_jury`: spec, `plan_jury`: plan, `tasks_jury`: tasks, `implementing`: an epic's implementation gate; no other stage has one), were written at the round that gate's ledger still records (0 when the gate has no ledger yet) and at least one of its lenses has a pack and no output; the jury round is that recorded round plus one; the claimed task is the effort's current claim; the running jurors are the lenses of that open round whose pack is written and whose output is not. [research: RF-4]

## Key entities
- **Worktree**: a git worktree of the nio repository, as `git worktree list` reports it; its path and branch. [research: RF-8]
- **Effort row**: one active effort in one worktree; slug, stage and status, jury round, claimed task, running jurors. [derived: RF-2, RF-3, RF-4, RF-5]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL print `/nio` output in under 2 seconds. [human]
- **NFR-2** THE SYSTEM SHALL use 0 model tokens for the pane, the status line and `/nio`. [human]
- **NFR-3** THE SYSTEM SHALL refresh the pane and the status line every 30 seconds. [research: RF-9]

## Success criteria
- **SC-1** The pane shows the three 2026-11-08 efforts (#123, #49, #122) live, with no model turn. [human]
- **SC-2** `/nio` prints each effort's state in under 2 seconds and uses no tokens. [human]

## Non-goals
- Any change to the NIO product or its skills; this is Claude-only dev tooling. [human]
- Acting on efforts from the pane or `/nio` (advancing, approving, abandoning). [agent]
- Hosts other than Claude Code. [human]
- Showing an effort's cost so far: no per-effort figure is recorded while an effort runs. [research: RF-6]

## Glossary
- **Mod**: a Claude Code extension under the repo's dev tooling, not shipped with NIO. Never "plugin".
- **Active effort**: an effort whose stage is not done and that is not abandoned.
- **Running juror**: a lens of an effort's open jury round whose pack is written and whose output is not yet.

## Decisions
- The mod adds no product change: stage and status come from `nio flow status` run in each worktree, and jury round, claimed task and running jurors are read from the effort's `.nio/` files; a field not recorded shows `-` (grill Q1, [agent]).
- Cost so far is dropped: tokens are only recorded as hook events joined to Claude Code transcripts, and a per-effort figure is written only when an effort finishes (RF-6).
- The worktrees are read in parallel to fit `/nio` in 2 seconds (RF-9).
- The refresh is every 30 seconds, not every 5: one pass over six worktrees takes about 8 CPU-seconds (RF-9).
- The mod is committed at `tools/claude-mods/nio-status-pane/` and turned on per person, like the background-commands mod (grill call, [agent]).

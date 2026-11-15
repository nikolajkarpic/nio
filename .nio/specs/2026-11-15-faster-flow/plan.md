---
slug: 2026-11-15-faster-flow
architecture: none               # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: Faster flow

## Build order
### US-2 A task can't depend on a later epic
- Delivers: CT-7
- Tests: TC-12, TC-13

### US-1 One agent implements a whole epic, and the flow runs its tests at the end
- Depends on: US-2
- Delivers: CT-1, CT-2, CT-3, CT-4, CT-5, CT-6, CT-8, CT-9, CT-10
- Tests: TC-1, TC-2, TC-3, TC-4, TC-5, TC-6, TC-7, TC-8, TC-9, TC-10, TC-11, TC-41, TC-42, TC-43, TC-45, TC-48, TC-49, TC-50, TC-52, TC-57, TC-58
- Scenario: QS-1

### US-7 What the closed issues still need keeps working
- Depends on: US-1
- Delivers: CT-26, CT-27, CT-28, CT-29, CT-30, CT-31, CT-32
- Tests: TC-34, TC-35, TC-36, TC-37, TC-38, TC-39, TC-40, TC-44, TC-51

### US-5 Jury gates don't drop, re-send or blow up findings
- Depends on: US-7
- Delivers: CT-14, CT-15, CT-16, CT-17, CT-18, CT-19, CT-20, CT-21
- Tests: TC-22, TC-23, TC-24, TC-25, TC-26, TC-27, TC-28, TC-29

### US-6 Claims, indexes and hand-offs don't break the run
- Depends on: US-1
- Delivers: CT-22, CT-23, CT-24, CT-25
- Tests: TC-30, TC-31, TC-32, TC-33

### US-3 Long commands run in the background in every effort session
- Depends on: US-1
- Delivers: CT-11, CT-12, CT-13
- Tests: TC-14, TC-15, TC-16, TC-56
- Scenario: QS-3

### US-4 The full-auto run drives the effort to the end, with one agent fixing all findings
- Depends on: US-1, US-5
- Delivers: CT-33, CT-34, CT-35, CT-36, CT-37, CT-38, CT-39, CT-40, CT-41
- Tests: TC-17, TC-18, TC-19, TC-20, TC-21, TC-46, TC-47, TC-53, TC-54, TC-55
- Scenario: QS-2

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1 | TC-1 |
| FR-2 | CT-1, CT-9 | TC-1 |
| FR-3 | CT-2 | TC-2, TC-3, TC-4 |
| FR-4 | CT-2 | TC-3, TC-45 |
| FR-5 | CT-5, CT-9 | TC-5 |
| FR-6 | CT-2 | TC-6 |
| FR-7 | CT-6 | TC-7 |
| FR-8 | CT-8, CT-10 | TC-8 |
| FR-9 | CT-1 | TC-9 |
| FR-10 | CT-2 | TC-10 |
| FR-11 | CT-3 | TC-11 |
| FR-12 | CT-7 | TC-12, TC-13 |
| FR-13 | CT-11 | TC-14 |
| FR-14 | CT-12 | TC-15 |
| FR-15 | CT-13 | TC-16 |
| FR-16 | CT-33 | TC-17 |
| FR-17 | CT-34, CT-39 | TC-18 |
| FR-18 | CT-8, CT-39 | TC-19 |
| FR-19 | CT-37, CT-38, CT-39 | TC-20 |
| FR-22 | CT-35, CT-39, CT-40, CT-41 | TC-21 |
| FR-23 | CT-14 | TC-22 |
| FR-24 | CT-15 | TC-23 |
| FR-25 | CT-16 | TC-24 |
| FR-26 | CT-17 | TC-25 |
| FR-27 | CT-18 | TC-26 |
| FR-28 | CT-19 | TC-27 |
| FR-29 | CT-20 | TC-28 |
| FR-30 | CT-21 | TC-29 |
| FR-31 | CT-23 | TC-30 |
| FR-32 | CT-24 | TC-31 |
| FR-33 | CT-22 | TC-32 |
| FR-34 | CT-25 | TC-33 |
| FR-35 | CT-26 | TC-34 |
| FR-36 | CT-26 | TC-35 |
| FR-37 | CT-27 | TC-36 |
| FR-38 | CT-28 | TC-37 |
| FR-39 | CT-29 | TC-38 |
| FR-40 | CT-30 | TC-39 |
| FR-41 | CT-31 | TC-40 |
| FR-42 | CT-2, CT-4, CT-8 | TC-41, TC-45 |
| FR-43 | CT-1, CT-8 | TC-42 |
| FR-44 | CT-1, CT-2, CT-4 | TC-43, TC-57, TC-58 |
| FR-45 | CT-32 | TC-44 |
| FR-46 | CT-35 | TC-46 |
| FR-47 | CT-4, CT-36 | TC-47 |
| AC-1 | CT-1, CT-9 | TC-1 |
| AC-2 | CT-2 | TC-2 |
| AC-3 | CT-2 | TC-3 |
| AC-4 | CT-2 | TC-4 |
| AC-5 | CT-5, CT-9 | TC-5 |
| AC-6 | CT-2 | TC-6 |
| AC-7 | CT-6 | TC-7 |
| AC-8 | CT-8, CT-10 | TC-8 |
| AC-9 | CT-1 | TC-9 |
| AC-10 | CT-2 | TC-10 |
| AC-11 | CT-3 | TC-11 |
| AC-12 | CT-7 | TC-12 |
| AC-13 | CT-7 | TC-13 |
| AC-14 | CT-11 | TC-14 |
| AC-15 | CT-12 | TC-15 |
| AC-16 | CT-13 | TC-16 |
| AC-17 | CT-33 | TC-17 |
| AC-18 | CT-34, CT-39 | TC-18 |
| AC-19 | CT-8, CT-39 | TC-19 |
| AC-20 | CT-37, CT-38, CT-39 | TC-20 |
| AC-23 | CT-35, CT-39, CT-40, CT-41 | TC-21 |
| AC-24 | CT-14 | TC-22 |
| AC-25 | CT-15 | TC-23 |
| AC-26 | CT-16 | TC-24 |
| AC-27 | CT-17 | TC-25 |
| AC-28 | CT-18 | TC-26 |
| AC-29 | CT-19 | TC-27 |
| AC-30 | CT-20 | TC-28 |
| AC-31 | CT-21 | TC-29 |
| AC-32 | CT-23 | TC-30 |
| AC-33 | CT-24 | TC-31 |
| AC-34 | CT-22 | TC-32 |
| AC-35 | CT-25 | TC-33 |
| AC-36 | CT-26 | TC-34 |
| AC-37 | CT-26 | TC-35 |
| AC-38 | CT-27 | TC-36 |
| AC-39 | CT-28 | TC-37 |
| AC-40 | CT-29 | TC-38 |
| AC-41 | CT-30 | TC-39 |
| AC-42 | CT-31 | TC-40 |
| AC-43 | CT-2, CT-4, CT-8 | TC-41 |
| AC-44 | CT-1, CT-8 | TC-42 |
| AC-45 | CT-1, CT-2, CT-4 | TC-43, TC-57, TC-58 |
| AC-46 | CT-32 | TC-44 |
| AC-47 | CT-2, CT-4, CT-8 | TC-45 |
| AC-48 | CT-35 | TC-46 |
| AC-49 | CT-4, CT-36 | TC-47 |
| NFR-1 | CT-2 | TC-48 |
| NFR-2 | CT-1 | TC-49 |

## Decisions
- [agent] Epic state is read from history (`claim`, `epic_test`, `blocked`, `unblock`, `task_done`) and the existing `claims`/`attempts` keys, with one new history kind, `epic_test`: no new state key or file, as the task states are today (RF-23, RF-26).
- [agent] The hand-back is a new `nio flow finish <slug> E-n`, not a reused `green`: FR-5 removes `green`, and the mod matches the new name (CT-2, CT-11).
- [agent] The epic test command is `--run` or built from the TCs through `evidence.one_test`, and must name every TC file, as red checks today (RF-25, CT-2).
- [agent] The 30-minute limit is a module constant, `EPIC_LIMIT`, that a test lowers; no new config key (FR-4, AC-47).
- [agent] One commit per epic, `E-n: <heading>`, staging tracked changes plus the untracked paths its tasks list (FR-11, CT-3).
- [agent] Tier and effort move to a `- Tier:`/`- Effort:` line under each `## E-n`; an epic approved before the change takes its tasks' highest (FR-7, CT-6).
- [agent] The driver loop and the fix agent are sections of the existing jury and implement skills, run as fresh general-purpose agents: no `skills/auto/` folder and no fixer card, so no new module (CT-39). #122's architecture placed them in new files; that design isn't approved for this effort.
- [agent] At the pr gate the one fix agent is the implementation agent of the closing `PR fixes` epic (CT-37).
- [agent] #122's code is carried by a no-commit cherry-pick of its nine code commits, leaving out its effort folder; `bc1f267` is already on `main` (RF-37, CT-34).
- [agent] Revoking auto is `nio flow manual --by human` (#122's CT-3) without its restore lines and judged-version refs, which nothing here needs (CT-33).
- [agent] `jury.publish` sets the run report as the pull request's body; there is no separate `nio flow pr`, since the pr gate already opens the PR and only the human approves it (RF-39, CT-40).
- [agent] The mod-off warning reads Claude Code's settings files for the installed mod; a mod loaded with `--plugin-dir` can't be seen, so the warning says to ignore it then (RF-31, CT-13).
- [agent] FR-14 is met by #142's install step; this branch merges `main` after #142 lands, before US-3 is built (RF-32, CT-12).
- [agent] FR-25's ruling is a new `reopen` disposition, human only, on a dropped finding (CT-16).
- [agent] FR-40's reused file is marked `(unchanged)` after its path in `Files:` (CT-30).
- [agent] Rollback (migration flag), in this order: (1) revert only while no effort has a live epic claim or a blocked epic: `nio flow status` shows none, else finish the epic (`nio flow finish`) or have the human unblock it first; (2) `git revert` the merge; (3) epics closed under the new flow keep their commits and `task_done` lines, which the old `implement.status` reads as done (TC-58), and it ignores `epic_test` lines; (4) a tasks.md approved after the change has per-epic tiers the old check rejects: re-run the evaluator on it (one card run) and re-approve the tasks gate before its next claim.
- [agent] An in-flight effort with a live old task or wave claim converts at its next claim: the claim is read as its epic's, and `nio flow finish` lands any old wave worktree before the run, so no uncommitted work is left behind (CT-1, CT-2, TC-57).

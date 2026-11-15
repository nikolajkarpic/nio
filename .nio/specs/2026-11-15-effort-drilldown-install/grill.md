# Grill: 2026-11-15-effort-drilldown-install

Session delegated by the human: "in grill take recommended options, and just work trough this task to implementation". Every answer below is the recommended option, tagged [agent].

## Lookup · OP-1, OP-3, OP-8, OP-9, OP-10, OP-11, OP-13 · 2026-11-15
Facet: meaning, actors, data, verification (drill-down); meaning, change (install)
Found: RF-1 to RF-9 in research.md. Retired OP-1, OP-3, OP-8, OP-9, OP-10, OP-11, OP-13.

## Asked · Q1 · OP-2 · 2026-11-15
Question: Should the Claude Code mods become part of the product that @nio:install offers in any project?
Context: Today they are documented as dev tooling for the NIO repo only. The north star keeps skills host-neutral and host features optional, which an offered, skippable mod respects.
Options: 1. Optional Claude Code part of the product (Recommended): offered by install, skills never need them. 2. Keep as repo dev tooling: target projects never get the pane. 3. Required on Claude Code: breaks the host-neutral rule.
Refs: OP-2 · US-6 · NORTH_STAR.md

## Q1 · OP-2 · 2026-11-15
Facet: actors
Question: Should the Claude Code mods become part of the product that @nio:install offers in any project?
Options:
1. Optional Claude Code part of the product (recommended)
2. Keep as repo dev tooling
3. Required on Claude Code
Answer: 1. Optional Claude Code part of the product: install offers them, skills never need them, READMEs say so. [agent]
Patched: FR-26, AC-27, Glossary (Mod); retired OP-2; decision D-261115-e6nx

## Asked · Q2 · OP-4 · 2026-11-15
Question: Where should a target project install the mods from, and how does the pane find nio there?
Context: The marketplace exists only in a NIO checkout and the installed wheel ships src/nio only (RF-3); the pane runs each worktree's .venv/bin/nio, which an installed-nio project lacks.
Options: 1. Ship them inside the nio package; pane falls back to nio on PATH (Recommended): same version as the CLI, works offline. 2. Install from the GitHub repo: private repo, version drift. 3. Only from a NIO checkout: most projects can't.
Refs: OP-4 · RF-2, RF-3 · register.tsx:10

## Q2 · OP-4 · 2026-11-15
Facet: data
Question: Where should a target project install the mods from, and how does the pane find nio there?
Options:
1. Ship inside the nio package, pane falls back to PATH nio (recommended)
2. Install from the GitHub repo
3. Only from a NIO checkout
Answer: 1. Ship the mods inside the installed nio package and install from there; the pane runs the worktree's .venv/bin/nio, else the nio on PATH, else shows `nio not found`. [agent]
Patched: FR-22, FR-23, AC-24, AC-25; retired OP-3, OP-4

## Asked · Q3 · OP-5 · 2026-11-15
Question: Should install ask before installing the mods, or install them by default?
Context: Installing changes the person's Claude Code setup; the permissions step already asks once in the same shape.
Options: 1. Ask once, install recommended (Recommended): one more question, nothing installed unasked. 2. Install by default with a skip flag: silent change to their setup. 3. Never install, print the commands: the gap the issue reports stays.
Refs: OP-5 · FR-15 · skills/install/SKILL.md

## Q3 · OP-5 · 2026-11-15
Facet: failure
Question: Should install ask before installing the mods, or install them by default?
Options:
1. Ask once, install recommended (recommended)
2. Install by default with a skip flag
3. Never install, print the commands
Answer: 1. Ask once, in the shape of the permissions question, install first and recommended, skip second. [agent]
Patched: FR-24, AC-26, UJ-2; retired OP-5

## Asked · Q4 · OP-6 · 2026-11-15
Question: Should the mods be installed for this clone only, for every project of the person, or for the whole team?
Context: Claude Code installs at user, project (committed) or local scope (RF-2). The permissions step recommends "just me" for the same reason.
Options: 1. This clone only, local scope (Recommended): nothing to commit, other projects untouched. 2. User scope: the pane loads in every project, NIO or not. 3. Project scope: a committed file turns them on for teammates who didn't choose.
Refs: OP-6 · RF-2

## Q4 · OP-6 · 2026-11-15
Facet: change
Question: Should the mods be installed for this clone only, for every project of the person, or for the whole team?
Options:
1. This clone only, local scope (recommended)
2. User scope
3. Project scope
Answer: 1. This clone only (Claude Code's local scope), no file to commit. [agent]
Patched: FR-25, AC-26; retired OP-6

## Asked · Q5 · OP-7 · 2026-11-15
Question: Should the drill-down read through a new nio JSON command or read the effort's files directly?
Context: The cost so far needs Python anyway (RF-4); the other sections parse files the CLI already understands.
Options: 1. One `nio flow show <slug> --json` (Recommended): one reader of the files, reusable by other hosts. 2. Read files in the pane: a second parser in TypeScript to keep in step. 3. Several JSON commands: more surface for the same data.
Refs: OP-7 · RF-4, RF-9

## Q5 · OP-7 · 2026-11-15
Facet: verification
Question: Should the drill-down read through a new nio JSON command or read the effort's files directly?
Options:
1. One `nio flow show <slug> --json` (recommended)
2. Read files in the pane
3. Several JSON commands
Answer: 1. One read-only `nio flow show <slug> --json` gives timeline, juries, tasks, cost and memory; the pane only draws it. [agent]
Patched: FR-21, AC-23; retired OP-7

## Asked · Q6 · OP-12 · 2026-11-15
Question: Should the drill-down cover only the active efforts the pane lists, or finished ones too?
Context: The pane lists active efforts only; finished ones already have usage.json and their files.
Options: 1. Active only (Recommended): no new list to build. 2. Also finished and abandoned: a second list in the pane.
Refs: OP-12 · FR-1

## Q6 · OP-12 · 2026-11-15
Facet: meaning
Question: Should the drill-down cover only the active efforts the pane lists, or finished ones too?
Options:
1. Active only (recommended)
2. Also finished and abandoned
Answer: 1. Active only: the drill-down opens from the rows the pane already lists. [agent]
Patched: FR-1; retired OP-12

## Call · defaults · 2026-11-15
Every remaining [default] (AC-3, AC-4, AC-5, AC-9, AC-11, AC-14, AC-17, AC-20, AC-21, AC-22, FR-12, FR-13, FR-14, FR-18, FR-19, FR-20, decision-table rows, non-goals, NFR-2) taken as proposed [agent]. NFR-1 raised from 2 s to 5 s because the cost so far alone takes 1.4 s on a real effort (RF-4). Delegated session.

## Finish · 2026-11-15
`nio check spec --gate` passes. Delegated: finish confirmed by the agent; every [agent] answer is listed in the gate notes for the human.

## Q7 · spec jury J-12 · 2026-11-15
Facet: actors
Question: The mods install for one clone only; should a teammate's clone get them without running install itself?
Options:
1. Keep this clone only, and say each clone runs install once (recommended)
2. Project scope, committed for the whole team
Answer: 1. Keep the local scope; UJ-2 and Decisions state that each teammate's clone runs install once and nothing is committed. [agent]
Patched: UJ-2, Decisions

## Q8 · spec jury J-13 · 2026-11-15
Facet: data
Question: Which memory records does the drill-down list for an effort?
Options:
1. Records whose front matter `paths` or `against` point at the effort, read without the embedding model (recommended)
2. Whatever `nio pack` returns for the effort (loads the model, about 15 s)
Answer: 1. Front-matter filter; AC-15 checks against that filter, not `nio pack` / `nio query`. [agent]
Patched: FR-10, AC-15, Decisions

## Q9 · spec jury J-8, J-16 · 2026-11-15
Facet: data
Question: How is cost so far split per stage and per jury?
Options:
1. Sum every visit to a stage, count the open stage up to now, show events outside any stage as `unattributed`, show jury cost inside its stage without adding it again (recommended)
2. Last visit only, open stage left out
Answer: 1. As recommended. [agent]
Patched: FR-7, AC-12, AC-28, Decisions

## Q10 · spec jury J-18, J-9 · 2026-11-15
Facet: verification
Question: How are the mod install outcomes made testable?
Options:
1. One CLI step `nio mods install [--skip]` that prints one line per mod; the skill asks the question and quotes the lines; skill text checked by a unit test (recommended)
2. Keep it in the skill and check by e2e transcript
Answer: 1. As recommended; skipping an already installed mod reports "already installed (left as is)". [agent]
Patched: FR-29, AC-21, AC-22, AC-26, decision table, Decisions

## Q11 · spec jury J-17, J-6, J-19, J-10 · 2026-11-15
Facet: failure
Question: What do the drill-down's edge cases show?
Options:
1. Failed review = `review` entry with `evidence.passed` false, reasons or `-`; context from the host, not nio; unknown or finished slug gives a JSON error, exit 1, shown with Back; an old nio without `flow show` shows "update nio" (recommended)
2. Leave them unstated
Answer: 1. As recommended. [agent]
Patched: FR-3, AC-2, FR-11, FR-21, FR-27, FR-28, AC-29, AC-30

## Q12 · spec jury J-15 · 2026-11-15
Facet: verification
Question: Keep the 5-second drill-down target for an effort with 200 history entries and 10 jury runs?
Options:
1. Keep it (recommended): grounded on the 1.4 s cost timing (RF-4), confirmed in the defaults call above
2. Drop it
Answer: 1. Keep NFR-1 as written. [agent]
Patched: none

## Lookup · plan · 2026-11-15
Facet: data, verification
Found: RF-10 to RF-21 in research.md. No stop-list item: `nio flow show` lands in flow.py and cli.py, cost so far in usage.py, `nio mods install` in hooks.py and cli.py, the mods ship through pyproject.toml's wheel settings, the pane in its existing files; no new module, dependency or stored data.

## Contradiction · plan · 2026-11-15
Facet: change
Question: The project architecture doc says the mods are dev tooling outside the product (RF-19); the approved spec's Q1 makes them an optional part of it. Which holds for this plan?
Options:
1. The approved spec (recommended): plan follows Q1; the project doc is reconciled after the effort (@nio:reconcile-onboarding), not edited by the plan
2. The project doc: send the spec back through the spec jury
Answer: 1. As recommended; D-261115-e6nx carries it. [agent]
Patched: plan.md Decisions

## Call · plan · 2026-11-15
Delegated session: each call below the grill's bar takes the recommended option. [agent]
- Timeline rows: history lines whose `from` differs from `to`, plus failed reviews; other same-stage lines left out (CT-3).
- Juries come from the committed ledgers only, never `.nio/runs/` (gitignored, a teammate lacks it); a round's lenses from finding sources and jurors of that round; the last round's verdicts from `jury.votes`, earlier rounds `block` on a confirmed blocker or major, else `approve` (CT-4).
- A jury's cost: the agents whose transcript's first line names an `R-<id>/jury` run with a step.json; its gate is that file's (CT-7, RF-12).
- Cost figures: tokens are the sum of the four token counts; a stage's seconds are its windows' length, a jury's the covered span of its agents; whole seconds; no events reads `-` (CT-7).
- Task status: `implement.status`'s state, `failing` when the task's last line is a failed review, attempts from `state.json` or `-` (CT-5).
- Memory standing from the index, `-` for a record not in it (CT-6).
- `--json` is required on `nio flow show`; an unknown, done or abandoned effort is a JSON error with exit 1; a damaged history fails only the timeline and cost sections (CT-1, CT-2).
- `flow show` is not added to `nio allow`: only the pane runs it (CT-1).
- Mods already installed: `claude plugin list --json` lists `<mod>@nio-mods`; outcome lines `<mod>: installed | skipped | already installed | already installed (left as is) | failed: <error>`; no `claude` on PATH is `failed: claude not found` (CT-10).
- The mods folder: the package's `nio/mods`, else the checkout's `tools/claude-mods` (CT-8).
- Pane: a Button per effort row, a Back Button and nothing else; the PATH `nio` when a worktree has no venv, `nio not found` when that run fails; `invalid choice` on exit 2 means an old nio; context line only when the host gives a number (CT-12, CT-13). This replaces the pane's earlier `no .venv: run uv sync` row (RF-20).
- The install skill's mods step is a new step 3 with one question, install first (CT-15).
- AC-18 to AC-20 run against the real `claude` with `CLAUDE_CONFIG_DIR` in a temp folder, only with `NIO_E2E=1`; NFR-1's time is asserted only with `NIO_PERF=1` (TC-20 to TC-22, TC-33).

## Call · plan · 2026-11-15 (plan jury, round 1)
Delegated session: each plan-fix below takes the finding's recommended fix. [agent]
- A broken effort's error row in the pane is a Button too, opening the same drill-down, so its timeline error shows beside the sections that still build (CT-12, CT-14, TC-37; J-1).
- The two project-doc lines that call the mods dev tooling outside the product are updated in this effort to the new boundary, citing D-261115-e6nx, instead of after it (CT-17, TC-32; J-3).
- The install skill's Inputs and Outputs name the second question and the installed mods (CT-15; J-4).

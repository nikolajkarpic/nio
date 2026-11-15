---
slug: 2026-11-15-effort-drilldown-install
retired: []                      # CT IDs removed from this plan; never reused
---
<!-- Contracts template: the interfaces this spec needs and where each lives in code. Derived from the approved spec,
architecture.md when it exists, and the code; never invented. Every item ends with its provenance, as in spec.md:
[human] (the human decided it), [agent] (a call below the grill's bar), [research: RF-n] (the code or research shows
it), [derived: <IDs>] (it follows from settled items) or [default] (your proposal; the plan jury judges it). IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in
`retired`. Remove a section or line that doesn't apply; never write N/A. Never restate the spec: cite its IDs, and
quote a constraint word for word when a builder needs it here. Open questions go in plan.md's Open points. -->
# Contracts: Effort drill-down in the NIO pane, and @nio:install installs the Claude Code mods

## Contracts

### CT-1 `nio flow show` command (FR-21, FR-27, NFR-2) [derived: FR-21, FR-27]
- Binding: `src/nio/cli.py:main` (existing)
- Like: `src/nio/cli.py:main`
- Kind: cli
- Shape: `nio flow show <slug> --json`
- Accepts: `slug`, a folder name under `.nio/specs/`; `--json` is required (the only output form); argparse refuses the call without it. [agent]
- Returns: stdout is exactly one line, the JSON object CT-2 returns, and the exit code CT-2 returns. No text before or after it.
- Fails: CT-2 returns code 1 with `{"error": ...}` → that line on stdout, exit 1. The `flow` branch's `error: ...` on stderr is never reached for `show`: CT-2 catches its own errors (RF-15). [research: RF-15]
- Rules: "writing no file except the caches NFR-2 allows" (FR-21); "other than the caches the CLI already keeps under `.nio/cache/`" (NFR-2). `flow show` is not added to `nio allow`'s list: only the pane runs it, outside the agent's prompts. [agent]

### CT-2 Effort drill-down data (FR-2, FR-3, FR-4, FR-5, FR-6, FR-10, FR-12, FR-13, FR-21, FR-27) [derived: FR-21]
- Binding: `src/nio/flow.py:show` (new)
- Like: `src/nio/flow.py:brief`
- Kind: function
- Shape: `show(root, slug, now=None) -> (code, [line])`; `line` is `json.dumps(obj)` on one line
- Accepts: `slug`; `now`, the time the open stage is counted up to (default: the current UTC time; tests pass a fixed one).
- Returns: code 0 and `{"slug", "stage", "timeline", "juries", "tasks", "cost", "memory"}`. `stage` is `where(...)["stage"]`. Each of the five section keys holds the value of CT-3, CT-4, CT-5, CT-6 or CT-7, or `{"error": "<text>"}` when building that section raised (FR-13): one section's failure never stops the others. [agent]
- Fails: no folder `.nio/specs/<slug>/`, or `kind(root, slug)` not `effort` → code 1, `{"error": "no effort <slug>"}`; the effort's stage is `done` → code 1, `{"error": "<slug> is done"}`; its state's `abandon` is set → code 1, `{"error": "<slug> is abandoned"}` (the pane lists neither, RF-18). A `Broken` from `load` is not a failure of the call: `stage` reads `"-"` and the sections go on as the Rules say (FR-13). [agent]
- Rules: "the pane draws those five sections from that output only" (FR-21). Never locks, never calls `record`, `write` or `usage.write`; reads `state.json` and `history.jsonl` through `load` only. Each of CT-3 to CT-6 reads its own files inside its own `try`, so a damaged `history.jsonl` (a `Broken` from `load`) fails `timeline` and `cost` only, each `{"error": "<slug>: history.jsonl, line <n>"}`: the juries, tasks and memory sections are built without the history (tasks then read `-` for status). [agent]

### CT-3 Timeline section (FR-2, FR-3, FR-12) [agent]
- Binding: `src/nio/flow.py:timeline` (new)
- Like: `src/nio/usage.py:attempts`
- Kind: function
- Shape: `timeline(lines) -> [{"kind", "from", "to", "role", "host", "model", "at", "reasons"}]`
- Accepts: the history lines `load` returns, oldest first.
- Returns: one row per line whose `from` differs from its `to` (a stage change, RF-10), and one per `review` line whose `evidence.passed` is false (FR-3), in history order. `role`, `host`, `model` come from `who`; `at` is the line's `at` as recorded. `reasons` is present on failed reviews only: `evidence.reasons`, or `"-"` when that list is empty or missing. Any field missing or empty in the line reads `"-"` (FR-12). Other same-stage lines (claim, red, green, a passed review, epic) are left out. [agent]
- Fails: never; a missing field reads `"-"`.
- Rules: "with from, to, role, host, model and time" (FR-2); "a `review` entry whose `evidence.passed` is false" (FR-3).

### CT-4 Juries section (FR-4, FR-5, FR-12) [agent]
- Binding: `src/nio/flow.py:juries` (new)
- Like: `src/nio/flow.py:brief`
- Kind: function
- Shape: `juries(root, slug) -> [{"gate", "outcome", "rounds": [{"round", "lenses": [{"lens", "verdict"}], "findings": [{"id", "title", "severity", "validation", "fix_tasks"}]}]}]`
- Accepts: the effort; reads each `.nio/specs/<slug>/jury/<gate>.json` through `jury.load(root, slug, gate)`, gates in file-name order. Reads the committed ledgers only, never `.nio/runs/` (gitignored, absent in a teammate's clone, RF-11).
- Returns: one entry per ledger; `outcome` is the ledger's `outcome`, or `"-"` when empty. Rounds 1 to the ledger's `round`. A round's lenses: every lens named in a finding source with that `round`, plus every juror whose ledger `round` is that round. A lens's verdict: in the ledger's last round, its vote from `jury.votes(led)` (a lens with several jurors shows `block` if any blocks, else the first vote); in an earlier round, `block` when a finding it raised in that round has `validation` `confirmed` and severity other than `minor`, else `approve`. A round's findings: those whose `first_round` is that round, each with `validation` as recorded (`confirmed`, `grounded`, `refuted`, `merged`, `pending`), and `fix_tasks`: the IDs `tasks.fixes_of(root, slug, gate, id)` returns when `tasks.md` exists, else `[]`. Empty list when the effort has no ledger (the pane then shows "no juries yet"). [agent]
- Fails: a ledger that isn't JSON → this section's `{"error": ...}` through CT-2.
- Rules: "list, per gate, every jury run with its rounds, lenses and verdicts" (FR-4); "whether the refuter confirmed it, and the fix task it led to" (FR-5).

### CT-5 Tasks section (FR-6, FR-12) [agent]
- Binding: `src/nio/flow.py:task_rows` (new)
- Like: `src/nio/flow.py:brief`
- Kind: function
- Shape: `task_rows(root, slug, state, lines) -> [{"epic", "tasks": [{"id", "title", "status", "attempts"}]}]`
- Accepts: the effort, its state and history lines (`None` when `load` failed).
- Returns: `[]` when `tasks.md` is missing. Else one entry per epic in `implement.tasks_of` order; `status` is `implement.status(...)[id]`, except `failing` when the task's last history line naming it is a `review` with `evidence.passed` false, and `"-"` when `lines` is `None`; `attempts` is `state["attempts"][id]`, or `"-"` when absent (FR-12). [agent]
- Fails: a `tasks.md` that doesn't parse → this section's `{"error": ...}` through CT-2.
- Rules: "as done, claimed or failing, with their attempts from `state.json`" (FR-6).

### CT-6 Memory section (FR-10, FR-12) [research: RF-14]
- Binding: `src/nio/flow.py:memory` (new)
- Like: `src/nio/pack.py:build`
- Kind: function
- Shape: `memory(root, slug) -> [{"id", "kind", "standing", "title"}]`
- Accepts: the effort; reads records with `index.load(root)` (front matter through `records.parse`, no embedding model) and standings from `index.connect(root)`'s `nodes` table.
- Returns: the records whose `paths` hold an entry starting with `.nio/specs/<slug>/`, or whose `against` equals the slug, sorted by ID; `kind` is the front matter `type`; `standing` is the index's, or `"-"` when the record isn't in the index. `[]` when none (the pane shows "no memory yet").
- Fails: never loads the model; an index that can't be opened gives `"-"` standings, not an error. [agent]
- Rules: "read from the records' front matter without loading the embedding model (not `nio pack` / `nio query`, which rank by relevance and load the model, RF-7)" (FR-10).

### CT-7 Cost so far (FR-7, FR-8, FR-12, NFR-1, NFR-2) [derived: FR-7, FR-8]
- Binding: `src/nio/usage.py:so_far` (new)
- Like: `src/nio/usage.py:report`
- Kind: function
- Shape: `so_far(root, slug, lines, now) -> {"stages": [{"stage", "tokens", "seconds", "juries": [{"gate", "tokens", "seconds"}]}], "unattributed": {"tokens", "seconds"}, "total": {"tokens", "seconds"}}`
- Accepts: the effort, its history lines, and `now` (an aware UTC datetime).
- Returns: from `own(read(root), slug)`. Windows: each line whose `from` differs from its `to` opens a window for its `to` stage that closes at the next such line, the last one at `now`. A stage's figure sums all its windows, stages in order of first entry. An agent counts in the window its `agent_start` falls in, with the tokens of its `agent_stop` log (`tokens(log)`); the orchestrator's tokens count per window through `tokens(transcript, start, end)` for each session transcript. `seconds`: a stage's is its windows' length; a jury's is `covered()` of its agents' spans. `tokens` is the sum of the four counts in `TOKENS`. Events before the first window are `unattributed`, and its `seconds` is `covered()` of its agent and shell spans. A jury's agents: those whose log's first line names a run as `R-<id>/jury` with a `.nio/runs/<run>/jury/packs/step.json`; the gate is that file's `gate`, listed inside the stage the agent ran in (RF-12). `total` is the stages plus `unattributed`; jury figures are never added to it. No events for the effort → `stages: []` and every figure `"-"` (FR-12, AC-14). Seconds are whole numbers. [agent]
- Fails: an unreadable log counts zero tokens, as `tokens` already does.
- Rules: "summed over every visit, the open current stage counted up to now; events in no stage window show as `unattributed`" and "shown as a breakdown inside its stage and never added to the total again" (FR-7). Never calls `write`: "without writing the effort's `usage.json`" (AC-12).

### CT-8 Where the mods are (FR-22) [research: RF-17]
- Binding: `src/nio/hooks.py:mods_dir` (new)
- Like: `src/nio/cli.py:main`
- Kind: function
- Shape: `mods_dir() -> Path`
- Returns: `resources.files("nio") / "mods"` when that folder exists (an installed wheel), else the checkout's `tools/claude-mods` (`Path(__file__).parents[2] / "tools/claude-mods"`, an editable install).
- Fails: neither exists → `ValueError("no NIO mods in this nio install")`.

### CT-9 Ship the mods in the package (FR-22) [derived: FR-22]
- Binding: `pyproject.toml` (existing)
- Like: none: the project has no wheel settings yet (RF-17)
- Kind: config
- Shape: `[tool.hatch.build.targets.wheel.force-include]` with `"tools/claude-mods" = "nio/mods"`
- Rules: "ship the mods inside the installed `nio` package, so a project with an installed `nio` and no NIO checkout can install them" (FR-22). No dependency is added.

### CT-10 Install the mods (FR-15, FR-16, FR-18, FR-19, FR-25, FR-29) [derived: FR-29]
- Binding: `src/nio/hooks.py:mods_install` (new)
- Like: `src/nio/hooks.py:allow`
- Kind: function
- Shape: `mods_install(root, skip=False, claude="claude") -> [line]`
- Accepts: the repo root; `skip`; `claude`, the command (tests pass a fake's path).
- Returns: one line per mod, in marketplace order (`background-nio-commands`, then `nio-status-pane`): `<mod>: installed`, `<mod>: skipped`, `<mod>: already installed`, `<mod>: already installed (left as is)` (skip chosen, mod present) or `<mod>: failed: <error>`. Already installed: `<claude> plugin list --json`, run in `root`, lists an entry whose `id` is `<mod>@nio-mods` (RF-16). Install: `<claude> plugin install <mod> --marketplace <mods_dir()> --scope local --json`, run in `root` (the `--marketplace <path>` form `claude plugin install --help` documents, RF-2; it adds the marketplace and installs in one call, replacing the README's two-step `marketplace add` then `install <mod>@nio-mods`); a non-zero exit is `failed` with the last line of its stderr, else of its stdout. `mods_dir()` is inside the `nio` tool's own environment, whose path a reinstall of `nio` keeps; a mod listed as installed is left as is (the decision table), even if its marketplace folder has since moved. [research: RF-2]
- Fails: `claude` not on PATH → each mod `failed: claude not found` (or `skipped` when `skip`); a `plugin list` that fails or isn't JSON counts as nothing installed; a failure on one mod never stops the other (FR-19). Never raises. [agent]
- Rules: decision table "mod outcome at install"; "for this clone only (Claude Code's `local` scope), changing no file to commit" (FR-25).

### CT-11 `nio mods install` command (FR-29) [derived: FR-29]
- Binding: `src/nio/cli.py:main` (existing)
- Like: `src/nio/cli.py:main`
- Kind: cli
- Shape: `nio mods install [--skip]`
- Returns: CT-10's lines on stdout, exit 0 always.
- Rules: "print one line per mod with its outcome (installed, skipped, already installed, failed with the error), exiting 0" (FR-29).

### CT-12 Pane drill-down (FR-1, FR-9, FR-11, FR-12, FR-13, FR-14, FR-27, FR-28) [derived: FR-1, FR-21]
- Binding: `tools/claude-mods/nio-status-pane/hooks/register.tsx:register` (existing)
- Like: `tools/claude-mods/nio-status-pane/hooks/register.tsx:register`
- Kind: event
- Shape: each effort row, and each error row that names a slug (a broken effort, `<slug> · broken: ...` from `flow status`), is a `Button` with `key` = the slug, so a broken effort opens the same drill-down and its sections show the error beside the ones that still build (AC-4); `onPress` stores `{ slug, path }` in a `drill` atom and runs `<nio> flow show <slug> --json` (CT-13's `nio`, `cwd` the row's worktree path, `ENV`); while open the Pane draws the drill-down and a `Button` `key="back"` labelled `Back`, whose `onPress` clears `drill` and shows the list again. No other Button. [agent]
- Accepts: CT-1's JSON line.
- Returns: sections in order timeline, juries, tasks, cost, memory, context. Rows: a stage change `<from> → <to> · <role> · <host> · <model> · <at>`; a failed review `review <from> · <at> · <reasons joined by "; ", or ->`; a gate `<gate> · <outcome>`, each round `round <n>: <lens> <verdict>, ...` and each finding `<id> <severity> <validation>: <title>` plus ` → <fix tasks>` when it has any; a task `<id> <status> · attempts <attempts> · <title>` under its epic; a record `<id> <kind> <standing>: <title>`. A list section that is `[]` draws `no juries yet`, `no tasks yet`, `no memory yet` (and `no timeline yet`); a section that is `{"error": e}` draws `error: <e>`; `"-"` values are drawn as given. Cost draws `<stage>: <tokens> tokens · <seconds>s` per stage, its juries indented under it, then `unattributed` and `total` lines, the numbers exactly as the JSON holds them (FR-9). Context: `context: <percent>%` from `(await $.session.usage()).context.percent`; no line at all when that call throws or `percent` is not a number (FR-11). [agent]
- Fails: exit 1 with an `error` key → the drill-down holds that text and Back (FR-27); exit 2 with `invalid choice` in stderr → `this nio has no flow show: update nio` and Back (FR-28); any other failure → the stderr's last line and Back. [agent]
- Rules: "the pane draws those five sections from that output only" (FR-21); never writes a file and never makes a model call.

### CT-13 Which `nio` the pane runs (FR-23) [derived: FR-23]
- Binding: `tools/claude-mods/nio-status-pane/hooks/register.tsx:nioFor` (new)
- Like: `tools/claude-mods/nio-status-pane/hooks/register.tsx:flowStatus`
- Kind: function
- Shape: `nioFor($, cwd) -> Promise<string>`
- Returns: `<cwd>/.venv/bin/nio` when it exists, else `nio` (resolved by the process run from PATH). `flowStatus` and CT-12 both use it. A run of `nio` that throws (no such program) reads `nio not found` in the worktree's row or the drill-down. [agent]
- Rules: "show `nio not found` only when neither exists" (FR-23). Never runs `uv` (it would create `.venv`, RF-3).

### CT-14 Pane row and state types (FR-1, FR-14) [agent]
- Binding: `tools/claude-mods/nio-status-pane/types/index.d.ts` (existing)
- Like: `tools/claude-mods/nio-status-pane/types/index.d.ts:NioRow`
- Kind: config
- Shape: an effort row, and an error row with a non-empty `slug`, gains `path: string` (the worktree's full path, the `cwd` CT-12 runs in); `PluginState['nio-status-pane']` gains `drill: { slug: string; path: string; shown: NioShow | { error: string } | null; context: number | null } | null`, with `NioShow` typing CT-2's object.

### CT-15 Install skill's mods step (FR-15, FR-16, FR-17, FR-20, FR-24, FR-29) [derived: FR-24, FR-29]
- Binding: `skills/install/SKILL.md` (existing)
- Like: `skills/install/SKILL.md`
- Kind: file
- Shape: a new step 3, "On Claude Code" only: ask once, in the shape of "Talking to the human", with two options, **Install the mods (recommended)** → `nio mods install`, and **Skip** → `nio mods install --skip`, each saying what happens; elsewhere skip the step and say nothing about mods. The closing message quotes each line the command printed. "When to stop" becomes "Stop after step 3". `## Inputs and outputs` changes with it: Input "the repo, and the human's answers to one question (two on Claude Code)"; Outputs add "on Claude Code, the mods the human chose, installed for this clone (local scope, nothing to commit)". No other step names the mods; the "Talking to the human" block stays word for word (tests/test_talk.py). [agent]
- Rules: "ask once whether to install the mods, offering install (recommended) and skip, each saying what happens" (FR-24); "not install or offer the mods" on another host (FR-20).

### CT-16 Mods described as optional (FR-26) [derived: FR-26]
- Binding: `tools/claude-mods/README.md` (existing)
- Like: `README.md`
- Kind: file
- Shape: `README.md`, `tools/claude-mods/README.md`, `tools/claude-mods/background-nio-commands/README.md` and `tools/claude-mods/nio-status-pane/README.md` each say the mods are "an optional Claude Code part of NIO" that "the skills work the same without", and that `@nio:install` (or `nio mods install`) installs them for this clone. The phrases "not part of the NIO product" and "dev tooling" are removed.
- Rules: "as an optional Claude Code part of NIO, with the skills working the same without them" (FR-26).

### CT-17 Project docs state the new boundary (FR-26) [derived: FR-26]
- Binding: `.nio/project/architecture.md` (existing)
- Like: `.nio/project/stack.md`
- Kind: file
- Shape: `.nio/project/architecture.md`'s Boundaries line on `tools/claude-mods/` and `.nio/project/stack.md`'s TypeScript line each say the mods are "an optional Claude Code part of NIO, shipped in the `nio` package and offered by `@nio:install`" instead of "dev tooling, outside the product" / "not part of the NIO product", each ending `(source: dev, D-261115-e6nx)`. No other line of either doc changes. [agent]
- Rules: "as an optional Claude Code part of NIO, with the skills working the same without them" (FR-26); each line keeps a source record `src/nio/onboard.py`'s check accepts (`DEV_SOURCE`).

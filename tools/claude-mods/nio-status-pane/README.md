# nio-status-pane

An optional Claude Code part of NIO, shipped in the `nio` package and offered by `@nio:install`; the skills work the same without it. It shows where
every NIO effort stands across this repo's git worktrees, with no model turn (issues #131, #132):

- a side pane, **NIO efforts**: one row per active effort, with its stage and status, jury round,
  claimed task and running jurors, and the worktree it runs in. A field the effort's files don't
  record reads `-`. A worktree whose `nio flow status` fails, or a broken effort, shows its error;
  the rest are still listed;
- pressing an effort (or its number, `1`–`9`) opens its drill-down in tabs: **overview** (task progress,
  each jury's outcome, the last three moves, total cost), **history**, **juries** (a gate opens to its rounds
  and findings; gates not yet approved start open), **tasks** (per epic, `done/total`), **cost**, **memory**.
  Tabs answer `1`–`6`, `b` goes back;
- a status line under the prompt: `nio: 3 active (implementing x2, spec_jury)`, or `nio: no active effort`;
- `/nio`: prints `nio flow status` for every worktree, one block each, run in parallel.

The pane and the status line refresh every 30 seconds; the pane's first line says when it last did.
An effort is active unless it is done or abandoned; legacy and unsupported folders are left out. An
effort folder copied into several worktrees is listed once, from the copy with the newest activity (so a
stale copy of a finished effort is not listed).

It only reads: `git worktree list`, each worktree's own `.venv/bin/nio flow status` (no bytecode written;
never `uv`, which would create a `.venv`), and the effort's `state.json`, jury ledgers and
`.nio/runs/*/jury/` files. A worktree with no `.venv` shows `no .venv: run uv sync` and runs nothing.

The pane opens by itself only where the terminal is wide enough for a sidebar (144 columns);
`/nio` opens it at any width.

## Turning it on

It is opt-in, per person; no repo settings file loads it. From the repo root, either:

```sh
claude --plugin-dir tools/claude-mods/nio-status-pane
```

or set the variable in your own shell profile (several mods: separate the paths with `:`):

```sh
export CLAUDE_CODE_PLUGIN_DIRS=/path/to/nio/tools/claude-mods/nio-status-pane
```

Leave it out to get today's behaviour.

## Checks

```sh
claude plugin validate tools/claude-mods/nio-status-pane
claude plugin test tools/claude-mods/nio-status-pane
```

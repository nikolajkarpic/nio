# Intake

## Human's words

> what about other mods?

> yes for 131 and 132

(Agreed plan: #131 and #132 ship as one mod.)

## Source: https://github.com/nikolajkarpic/nio/issues/131

# Mod: NIO effort pane and status line

Claude Code mod (dev tooling, Claude-only, not part of the NIO product).

**Problem.** Finding out where an effort stands means asking a model, which costs a turn and tokens.

**Mod.** A side pane that lists each active effort across the worktrees, with its gate, jury round, claimed task, running jurors and cost so far. It refreshes on a `$.clock` timer from `nio flow status`. A one-line version goes in the status line.

**Done when.** The pane shows all three 2026-11-08 efforts (#123, #49, #122) live, with no model turn.


## Source: https://github.com/nikolajkarpic/nio/issues/132

# Mod: /nio slash command for flow status without a model turn

Claude Code mod (dev tooling, Claude-only, not part of the NIO product).

**Mod.** A `/nio` slash command that prints `nio flow status` for every nio worktree, answered by the mod with no model turn. It fits naturally into the status pane mod, so it can ship in the same mod.

**Done when.** `/nio` prints each effort's state in under 2 seconds and uses no tokens.



# Claude Code mods for developing NIO

Claude-only dev tooling for working on this repo. They are not part of the NIO product.

| Mod | What it does |
| --- | --- |
| [background-nio-commands](background-nio-commands/) | Runs `nio jury evidence`, `nio flow finish` and the test suite in the background, so agents stop polling (#130) |
| [nio-status-pane](nio-status-pane/) | A side pane, a status line and `/nio` showing where every effort in the repo's worktrees stands, with no model turn (#131, #132) |

## Install (once)

```
claude plugin marketplace add ~/nio/tools/claude-mods
claude plugin install background-nio-commands@nio-mods
claude plugin install nio-status-pane@nio-mods
```

Use the path of your own checkout. Claude Code reads the mods straight from this folder, so after a `git pull` run `/reload-plugins` in a session to pick up changes.

When a new mod is added to `.claude-plugin/marketplace.json`, run `claude plugin install <mod>@nio-mods` for it.

To try a mod for one session only, without installing it: `claude --plugin-dir tools/claude-mods/<mod>`.

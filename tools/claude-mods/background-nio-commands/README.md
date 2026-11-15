# background-nio-commands

An optional Claude Code part of NIO, shipped in the `nio` package and offered by `@nio:install`; the skills work the same without it. It turns
foreground Bash calls that run a long nio command into background runs, so the harness wakes the
agent when the command exits instead of the agent sitting in a `sleep`/poll wait loop (issue #130).

Long commands:

- `nio jury evidence …` and `nio flow finish …`, also as `uv run nio …` and after `cd <dir> &&`;
- the exact `tests.suite` command from `.nio/config.json` (also after `cd <dir> &&`).

It only sets `run_in_background: true` and adds no text. A call that already sets
`run_in_background` (true or false) is left alone, as is every other command, a single test file,
and a command that only mentions a long command as text. With no readable config only the two nio
commands are matched, and if the hook fails the call runs as issued.

## Turning it on

It is opt-in, per person; no repo settings file loads it. From the repo root, either:

```sh
claude --plugin-dir tools/claude-mods/background-nio-commands
```

or set the variable in your own shell profile:

```sh
export CLAUDE_CODE_PLUGIN_DIRS=/path/to/nio/tools/claude-mods/background-nio-commands
```

Leave it out to get today's behaviour. Don't turn it on in a target project: NIO must behave the
same on every host.

## Checks

```sh
claude plugin validate tools/claude-mods/background-nio-commands
claude plugin test tools/claude-mods/background-nio-commands
```

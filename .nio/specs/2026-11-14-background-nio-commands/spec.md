---
slug: 2026-11-14-background-nio-commands
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-14-background-nio-commands` checks all of this. -->
# Run long nio commands in the background instead of polling

## Summary
A Claude Code mod for working on NIO itself: a hook on the Bash tool that turns long nio commands (`nio jury run`,
`nio flow green`, the configured test-suite command) into background runs. The harness then wakes the session when the
command exits, so agents stop sitting in `sleep`/poll wait loops that cost about 267 minutes on 2026-11-08. It is dev
tooling, Claude-only, and not part of the NIO product. [human]

## Actors and journeys
- **A-1 Agent driving an effort**: a Claude Code session (main session or subagent, such as an orchestrator or driver) running NIO stages that call long nio commands; wants the result as soon as the command exits, without spending turns polling. [research: RF-1]
- **A-2 NIO maintainer**: the human developing NIO in this repo with Claude Code; wants onboarding and full-auto runs to finish sooner. [agent]

**UJ-1 Long command without a wait loop** (A-1) [agent]
1. The agent issues a Bash call for `nio jury run …` without setting `run_in_background`.
2. The mod rewrites the call to run in the background.
3. The agent carries on or ends its turn; the harness holds it and wakes it when the command exits.
4. The agent reads the command's output and continues the effort.
- Misuse: the agent still writes a `sleep`/poll loop around the background command out of habit.
- Evidence: issue #130; onboarding (#49) and full-auto (#122) transcripts of 2026-11-08 (RF-1).

**UJ-2 Turning the mod on** (A-2) [agent]
1. The maintainer starts Claude Code with the mod's folder in this repo (`tools/claude-mods/background-nio-commands/`), by the `--plugin-dir` flag or the `CLAUDE_CODE_PLUGIN_DIRS` variable, as the mod's README says.
2. The next effort's long commands run in the background with no change to skills, agent cards or settings.
- Misuse: enabling it in a target project where the NIO product is expected to behave the same on every host.
- Evidence: domain.

## User stories

### US-1 Long nio commands run in the background (P1) [human]
- **Why this priority:** it is the whole value of the mod: the only mod idea that saves wall-clock time.
- **Independent test:** issue each long command as a foreground Bash call with the mod on and check the call the harness receives is a background one.

- **AC-1** (FR-1) Given the mod is on, when an agent issues a foreground Bash call running `nio jury run`, then the call runs in the background. [human]
  Observable: the tool input the hook returns has `run_in_background: true`. Level: unit.
- **AC-2** (FR-1) Given the mod is on, when an agent issues a foreground Bash call running `nio flow green`, then the call runs in the background. [human]
  Observable: the tool input the hook returns has `run_in_background: true`. Level: unit.
- **AC-3** (FR-1) Given the mod is on and a test-suite command is configured, when an agent issues a foreground Bash call running exactly that command, then the call runs in the background. [human]
  Observable: the tool input the hook returns has `run_in_background: true`. Level: unit.
- **AC-4** (FR-2) Given the mod is on, when a long nio command is invoked through a wrapper or prefix (`uv run nio …`, `cd <dir> && nio …`), then the call runs in the background. [agent]
  Observable: the tool input the hook returns has `run_in_background: true` for each form. Level: unit.
- **AC-5** (FR-1, FR-3) Given the mod is on, when a Bash call is rewritten, then every other field of the call (the command text, the description, the timeout) is unchanged and no text is added to the call. [agent]
  Observable: the returned tool input equals the original apart from `run_in_background`. Level: unit.

### US-2 An effort finishes a jury run with no wait loop (P1) [human]
- **Why this priority:** it is the issue's "done when"; without it the rewrite may happen yet agents keep polling.
- **Independent test:** run one effort's jury with the mod on and search the transcript for wait loops.

- **AC-6** (FR-1, FR-4) Given the mod is on, when a jury run during an effort finishes, then the transcript holds no `sleep` or poll loop waiting for it. [human]
  Observable: the effort transcript has no Bash call matching `sleep` or a repeated status/output check between the jury run's start and its exit notification. Level: e2e.
- **AC-7** (FR-4) Given a long command was backgrounded, when it exits, then the session that issued it is woken with its exit status and output available. [human]
  Observable: the transcript shows the exit notification, followed by the agent reading the output. Level: e2e.

### US-3 Everything else is left alone (P1) [agent]
- **Why this priority:** a mod that changes other calls would slow or break the commands agents rely on for quick answers.
- **Independent test:** feed the hook a set of non-matching Bash calls and check each comes back unchanged.

- **AC-8** (FR-5) Given the mod is on, when an agent issues a Bash call for a short nio command (`nio flow status`, `nio check spec …`), a single test file (`uv run python tests/test_x.py`) or any non-nio command, then the call is passed through unchanged. [agent]
  Observable: the hook returns no modification for each call. Level: unit.
- **AC-9** (FR-5) Given the mod is on, when a command only mentions a long command as text (`echo "nio jury run"`, `grep "nio flow green" file`), then the call is passed through unchanged. [agent]
  Observable: the hook returns no modification. Level: unit.
- **AC-10** (FR-6) Given the mod is on, when a Bash call for a long command already sets `run_in_background`, to `true` or to `false`, then the call is passed through unchanged. [agent]
  Observable: the hook returns no modification for both values. Level: unit.
- **AC-11** (FR-7) Given the mod is on, when no test-suite command is configured or the configuration can't be read, then `nio jury run` and `nio flow green` are still backgrounded and nothing else is. [agent]
  Observable: with the config missing or malformed, the hook rewrites AC-1/AC-2 calls and returns no modification for a test-runner call. Level: unit.
- **AC-12** (FR-8) Given the mod is on, when the hook itself fails (bad input, crash), then the Bash call runs as the agent issued it. [agent]
  Observable: with malformed hook input the hook exits without blocking and returns no modification. Level: unit.
- **AC-13** (FR-9) Given the mod is off, when an agent issues a long nio command, then it runs in the foreground as today. [agent]
  Observable: with the mod's hook not registered, the call reaches the harness with no `run_in_background` set by NIO. Level: integration.
- **AC-14** (FR-10) Given the mod is committed, when a maintainer reads its folder, then its README says how to turn it on per person, and the repo's settings files don't load it. [agent]
  Observable: `tools/claude-mods/background-nio-commands/README.md` names `--plugin-dir` and `CLAUDE_CODE_PLUGIN_DIRS`; no `.claude/settings*.json` in the repo references the folder. Level: unit.

## Functional requirements
- **FR-1** WHEN an agent issues a Bash call that runs `nio jury run`, `nio flow green` or the configured test-suite command THE SYSTEM SHALL make the call run in the background. [human]
- **FR-2** WHEN a long nio command is invoked through `uv run nio` or after a prefix such as `cd <dir> &&` THE SYSTEM SHALL treat it as that long command. [agent]
- **FR-3** WHEN THE SYSTEM rewrites a Bash call THE SYSTEM SHALL change only whether it runs in the background, adding no text to the call. [agent]
- **FR-4** WHEN a backgrounded long command exits THE SYSTEM SHALL rely on the harness to wake the issuing session, with no wait loop in the agent. [human]
- **FR-5** IF a Bash call doesn't run a long command THEN THE SYSTEM SHALL pass it through unchanged. [agent]
- **FR-6** IF a Bash call already sets `run_in_background`, to `true` or to `false` THEN THE SYSTEM SHALL pass it through unchanged. [agent]
- **FR-7** IF no test-suite command is configured or the configuration can't be read THEN THE SYSTEM SHALL still background `nio jury run` and `nio flow green`. [agent]
- **FR-8** IF the hook fails THEN THE SYSTEM SHALL let the Bash call run as issued. [agent]
- **FR-9** THE SYSTEM SHALL keep the mod out of the NIO product: no skill or agent card depends on it. [human]
- **FR-10** THE SYSTEM SHALL live in this repo at `tools/claude-mods/background-nio-commands/`, be turned on per person, and change no settings itself. [agent]

## Rules
### Decision table: rewrite a Bash call
| Runs a long command (yes, no) | `run_in_background` set by the agent (yes, no) | Hook succeeds (yes, no) | → output | Src |
| --- | --- | --- | --- | --- |
| yes | no | yes | → rewrite to background | [human] |
| yes | yes | yes | → pass through unchanged | [agent] |
| no | - | yes | → pass through unchanged | [agent] |
| - | - | no | → pass through unchanged | [agent] |

## Key entities
- **Long command**: a Bash call running `nio jury run`, `nio flow green` or the configured test-suite command. [human]
- **Test-suite command**: the command the repo configures for running its test suite, `tests.suite` in `.nio/config.json`; running a single test file is not it. [research: RF-5]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL add no more than 200 ms to any Bash call it inspects. [agent]

## Success criteria
- **SC-1** A jury run during an effort finishes with no `sleep`/poll loop in the transcript. [human]
- **SC-2** Over the next onboarding or full-auto run, time spent in wait loops for long nio commands is zero minutes, against about 267 minutes on 2026-11-08. [agent]

## Non-goals
- Making the mod part of the NIO product or available on hosts other than Claude Code. [human]
- Backgrounding any command other than `nio jury run`, `nio flow green` and the configured test-suite command. [agent]
- Making the long commands themselves faster. [agent]
- Running this work through NIO's own implementation stages; once the spec is done it is implemented with normal Claude Code. [human]

## Glossary
- **Mod**: a Claude Code-only addition used while developing NIO, outside the shipped product. Never "plugin".
- **Wait loop**: an agent's repeated `sleep` or status/output checks while a command runs. Never "polling loop".
- **Long command**: see Key entities. Never "slow command".

## Decisions
- An explicit `run_in_background: false` is respected as the escape hatch; only an unset flag is rewritten (grill Q1, [agent], RF-2).
- The mod is committed at `tools/claude-mods/background-nio-commands/` and turned on per person by `--plugin-dir` or `CLAUDE_CODE_PLUGIN_DIRS`; it changes no settings, and its README says how to turn it on (grill Q2, [agent]).
- The rewrite alone is enough: Claude Code's background result already tells the agent it will be notified, so the mod adds no prompt text (grill Q3, [agent], RF-3).
- Single test files are not long commands; only `tests.suite` is (RF-5).

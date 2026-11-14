# Intake

## Human's words

> can we run spec for #130 and then we implement ith with normal claude implementation?

## Source: https://github.com/nikolajkarpic/nio/issues/130

# Mod: run long nio commands in the background instead of polling

Claude Code mod (dev tooling, Claude-only, not part of the NIO product).

**Problem.** Foreground nio commands get backgrounded after about 3 minutes, so agents sit in polling wait loops. Those loops took about 267 minutes of onboarding (#49) and full-auto (#122) time on 2026-11-08.

**Mod.** A `tool.call` hook on Bash that rewrites long nio commands (`nio jury run`, `nio flow green`, the configured test-suite command) to `run_in_background: true`. The harness then wakes the session when the command exits, so no wait loop is needed.

**Done when.** A jury run during an effort finishes with no `sleep`/poll loop in the transcript.

**Priority.** High: the only mod idea that saves wall-clock time.


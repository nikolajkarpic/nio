# Intake

## Human's words

specifyu this task  https://github.com/nikolajkarpic/nio/issues/142 and continue with nio flow, in grill take recommended options, and just work trough this task to implementation

## Source: https://github.com/nikolajkarpic/nio/issues/142

# Effort drill-down in the NIO pane, and @nio:install installs the Claude Code mods

## What

Two parts:

1. **Drill-down in the effort pane.** `nio-status-pane` (#131, #132, PR #136) lists active efforts, one row each. Add a way to pick one effort and see how it ran:
   - **Timeline:** each stage change from `history.jsonl`: from → to, who (role, host, model), when, and failed reviews with their reasons.
   - **Juries:** every run per gate, its rounds, lenses, verdicts, findings raised and confirmed by the refuter, and the fix tasks they led to.
   - **Tasks:** per epic, which are done, claimed or failing, with attempts from `state.json`.
   - **Cost:** tokens (and time) so far, per stage and per jury. Today `usage.json` is written only when an effort finishes (#131 spec, RF-6), so this needs a live figure from the `nio` CLI first.
   - **Memory:** the records that apply to the effort (`nio pack` / `nio query`).
   - **Context:** the session's context use, if the mod API exposes it.
2. **`@nio:install` installs the mods.** On Claude Code, setting NIO up in a repo also installs the NIO Claude Code mods (`tools/claude-mods/`: `background-nio-commands`, `nio-status-pane`), so nobody has to run `claude plugin marketplace add` / `plugin install` by hand.

## Why

Finding out how an effort ran, what it cost and how many juries it took means reading `state.json`, `history.jsonl`, `.nio/runs/` and `nio usage` by hand, or spending a model turn on it. Installing the mods by hand is easy to miss: the pane was left out of the marketplace until the fix PR for it.

## Open questions (for the grill)

- The mods are documented as Claude-only dev tooling for this repo, not the product. Installing them through `@nio:install` in any project makes them part of the product. Is that the intent, and does that conflict with `NORTH_STAR.md` (host-neutral skills; host features optional)?
- Where do target projects get the mods from? Today the marketplace is `tools/claude-mods` inside a NIO checkout, and the pane runs each worktree's `.venv/bin/nio`. A project with `uv tool install`-ed `nio` has neither.
- Should install ask first (like `nio allow`), or install by default with a way to skip?
- Should the drill-down read through new `nio … --json` commands (other hosts can reuse them) or read the files directly as the pane does today?

## Done when

- In the pane, selecting an effort shows its timeline, juries, tasks, cost so far and memory, with no model turn.
- `@nio:install` on Claude Code leaves both mods installed (or skipped by the human's choice), and says so in its closing message.


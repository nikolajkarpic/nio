# NIO

**Ni(kolaj) Orchestrator / New & Improved Orchestrator.** NIO is a set of agent-agnostic
skills that make agent-built software trustworthy and cheaper to build.

> Status: **vision / brainstorming**. No skills are built yet.

## What it does

- **Grills you** one question at a time until spec, plan and tasks leave no room for
  hallucination: user stories, *given / when / then*, edge cases, no vague or
  contradictory requirements.
- **Runs a gated pipeline:**
  `spec → research/contracts/personas/plan → effort → epics → tasks → implement → test`.
  `@nio:lite` handles small fixes.
- **Byzantine jury review.**
  - Autonomous decisions and stage gates are reviewed by independent jurors on different
    models, for example 2 Claude jurors and 1 Antigravity juror.
  - Reviews escalate from 1 cheap juror up to 3, so tokens are spent in proportion to risk.
  - DB scripts, secrets, breaking changes, irreversible actions and anything that costs
    money always go to you.
- **Any host in any role.** Claude Code, Antigravity, Cursor, Codex and others can each
  orchestrate, judge or build. They call each other in headless mode and hand off through
  md files.
- **Traceable memory.** Every decision is recorded with who made it, why and when, and is
  linked to its requirement, task, diff and verdict.

## Docs

- [NORTH_STAR.md](NORTH_STAR.md): the vision, principles and design.
- [ISSUES.md](ISSUES.md): open decisions and the backlog.
- [CLAUDE.md](CLAUDE.md): instructions for agents working in this repo.

# Product

## What it does

- Agent-agnostic skills, plus a `nio` CLI, that make agent-built software trustworthy and cheaper to build. (source: README.md@f72a1897d4ff)
- Grill: asks one question at a time until spec, plan and tasks leave no room for guessing. (source: README.md@f72a1897d4ff)
- Jury: independent jurors review each gate, escalating from one cheap juror to three so tokens track risk; money, secrets, DB scripts and anything irreversible always go to the human. (source: README.md@f72a1897d4ff)
- Memory: every decision is recorded with who, why and when, linked requirement → task → diff → verdict, in plain files in git. (source: README.md@f72a1897d4ff)

## Users

- Solo developers and small teams who build software with coding agents (Claude Code first, Antigravity next). (source: dev, 2026-11-15)
- Team features are in scope now: several people may share one repo's memory, specs and approvals. (source: dev, 2026-11-15)

## Main flows

- Per repo: install (git hooks, agent files, permission choice), then onboard (six project docs under `.nio/project/`). (source: README.md@f72a1897d4ff)
- Per change, the full route: spec → grill → spec jury → plan → plan jury → tasks → tasks jury → implement (red → green, parallel waves) → pr gate on the whole effort diff. (source: README.md@f72a1897d4ff)
- Per bug fix, the lite route: a grilled spec straight to tasks, with no spec jury and no plan; it offers the full route if the fix outgrows one module. (source: README.md@f72a1897d4ff)
- `nio flow next <slug>` names the next skill to run, and a stage moves on only when its guard passes. (source: README.md@f72a1897d4ff)
- Explain: turns an approved plan, or any topic, into a short Mermaid explainer. (source: README.md@f72a1897d4ff)

## Non-goals

- Dry-run mode (low priority). (source: NORTH_STAR.md@70371da8a313)
- A hosted service or UI. (source: NORTH_STAR.md@70371da8a313)
- Hosts beyond Claude Code and Antigravity until both work well. (source: NORTH_STAR.md@70371da8a313)

## Glossary

- Effort: one spec's whole journey, from spec to pr gate, in `.nio/specs/<YYYY-MM-DD>-<name>/`. (source: README.md@f72a1897d4ff)
- Route: `full` (spec → plan → tasks), `lite` (a bug fix: no spec jury, no plan) or `epic` (split into slices). (source: README.md@f72a1897d4ff)
- Gate: a point where the jury must approve before the effort moves on: spec, plan, tasks and pr. (source: README.md@f72a1897d4ff)
- Lens: one juror's angle (logic, testability, security, conformance…); each runs as its own agent. (source: README.md@f72a1897d4ff)
- Refuter: an agent that tries to disprove each blocker and major finding before the human sees it. (source: README.md@f72a1897d4ff)
- Red / green: a task's test proven failing before the code, then passing after it. (source: README.md@f72a1897d4ff)
- Wave: tasks with no dependency between them, built in parallel. (source: README.md@f72a1897d4ff)
- Tier: the model class a task or agent runs on (cheap, strong, frontier, max), mapped to real models in config. (source: README.md@f72a1897d4ff)
- Pack: the only context a worker or juror gets: its task or lens, the cited spec items and the memory that applies. (source: README.md@f72a1897d4ff)
- Standing: how far to trust a memory record: `current`, `approved`, `drifted`, `challenged`, `conflict`, `superseded`. (source: README.md@f72a1897d4ff)

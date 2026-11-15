# Architecture

## Modules

- `skills/<name>/SKILL.md`: the product, one folder per skill, plain markdown any agent can follow. (source: CLAUDE.md@b0e3cba2321c)
- `src/nio/`: the `nio` Python CLI, for what skills can't do reliably. (source: CLAUDE.md@b0e3cba2321c)
- `src/nio/agents/*.md`: the shipped agent cards, rendered per host by `nio agents sync`. (source: CLAUDE.md@b0e3cba2321c)
- `src/nio/cli.py`: the CLI entry point; it imports every other module. (source: src/nio/cli.py@f704aa46ad30)
- `src/nio/records.py`: memory records: parse, lint and create files under `.nio/memory/<area>/`. (source: src/nio/records.py@a187d34e776d)
- `src/nio/index.py`: builds `.nio/cache/index.db` (graph, FTS5, int8 vectors) and `INDEX.md` from the committed records. (source: src/nio/index.py@9e6282ccdfd4)
- `src/nio/query.py`: finds records by hybrid full-text and vector search, files they touch, graph walks, and a grep fallback. (source: src/nio/query.py@b8fb0107e10c)
- `src/nio/pack.py`: context packs, the memory that applies to a piece of work, as markdown an agent reads before it starts. (source: src/nio/pack.py@70d488cda840)
- `src/nio/spec.py`: creates `.nio/specs/<slug>/spec.md` from a template and runs its mechanical checks. (source: src/nio/spec.py@9a1ba6d5476a)
- `src/nio/plan.py`: creates the plan files next to an approved spec and runs their mechanical checks. (source: src/nio/plan.py@658970c8aec4)
- `src/nio/tasks.py`: creates `tasks.md`, runs its checks, prints the estimate and says whether implement may start. (source: src/nio/tasks.py@b633b38779f3)
- `src/nio/flow.py`: where an effort is, moving it on only when deterministic guards pass. (source: src/nio/flow.py@b2e603fe96ff)
- `src/nio/implement.py`: the implement stage: timed command runs, known test runners, full-suite runs and each task's status from history. (source: src/nio/implement.py@d6987bac184b)
- `src/nio/jury.py`: jury gates: the findings ledger, refuter results, dispositions and the gate outcome. (source: src/nio/jury.py@05f0bfb6aa9d)
- `src/nio/evidence.py`: the jury's evidence, from commands run in a throwaway copy of the repo. (source: src/nio/evidence.py@0d61b5c52146)
- `src/nio/agents.py`: loads agent cards, resolves tier and effort through config, renders them per host, and verifies the model each run used. (source: src/nio/agents.py@6328f0915e5d)
- `src/nio/hooks.py`: git hooks that refresh the index, re-render agent cards and run the memory check before commits and pushes. (source: src/nio/hooks.py@4924e8047fc8)
- `src/nio/usage.py`: records each agent and shell call to `.nio/runs/events.jsonl` and a finished effort's `usage.json`. (source: src/nio/usage.py@4bb829587c74)
- `src/nio/explain.py`: helpers for the explainer: its sections, diagram node IDs and rendering one Mermaid block. (source: src/nio/explain.py@85917a451556)
- `src/nio/onboard.py`: onboarding: the repo scan, the project docs' progress, and which went stale. (source: README.md@f72a1897d4ff)

## Boundaries

- `records.py` is the base layer: every other module imports it, and it imports none of them. (source: src/nio/records.py@a187d34e776d)
- Skills hold the instructions; the CLI holds only what instructions can't be followed reliably for. (source: CLAUDE.md@b0e3cba2321c)
- Skills must not depend on Claude-only tools; a host-specific feature is noted as optional. (source: CLAUDE.md@b0e3cba2321c)
- Only `nio flow` writes an effort's `state.json` and `history.jsonl`. (source: skills/onboard/SKILL.md@622c005a8ef1)
- The Claude Code mods under `tools/claude-mods/` are dev tooling, outside the product. (source: tools/claude-mods/README.md@975e0d334c44)

## Data flow

- Files in git are the truth: memory records live as markdown under `.nio/memory/`, and records are never edited; a new record supersedes the old one. (source: README.md@f72a1897d4ff)
- Agents leave memory candidates in `runs/<run>/promote.md`; one memory writer promotes them into records. (source: README.md@f72a1897d4ff)
- The index `.nio/cache/index.db` is a cache rebuilt from the records; deleting it loses nothing. (source: README.md@f72a1897d4ff)
- Each effort's artifacts (spec, plan, tasks, jury ledgers, usage) live in `.nio/specs/<YYYY-MM-DD>-<name>/`. (source: README.md@f72a1897d4ff)
- A worker or juror gets only its pack: its task or lens, the cited spec items and the memory that applies. (source: README.md@f72a1897d4ff)
- The jury ledger's data is `.nio/specs/<slug>/jury/<gate>.json`, and `<gate>.md` is regenerated from it on every change; both are committed. (source: src/nio/jury.py@05f0bfb6aa9d)

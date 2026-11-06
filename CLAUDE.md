# NIO — agent instructions

Read `NORTH_STAR.md` first. Any change must serve it, and ideas that don't go to a GitHub issue (labelled `type:*` and `area:*`).

## Repo layout

- `skills/<name>/SKILL.md`: the product. One folder per skill (`remember` writes memory, `recall` reads it).
- `src/nio/`: the `nio` Python CLI (`uv run nio ...`), for what skills can't do reliably.
  Self-checks: `uv run python tests/test_records.py`, `uv run python tests/test_index.py`, `uv run python tests/test_pack.py` (`-v` prints each pack), `uv run python tests/test_hooks.py`, `uv run python tests/test_usage.py`, `uv run python tests/test_agents.py`, `uv run python tests/test_jury.py`, `uv run python tests/test_spec.py`, `uv run python tests/test_plan.py`, `uv run python tests/test_tasks.py`, `uv run python tests/test_flow.py` and `uv run python tests/test_talk.py`.
  `NIO_PERF=1 uv run python tests/test_flow.py` asserts the status-speed limit; run it after a change to `nio flow status`.
  `NIO_E2E=1 uv run python tests/test_lenses.py` and `tests/test_tasks_e2e.py` run the cards on real models (costly; after changing a card).
- `src/nio/agents/*.md`: the shipped agent cards (#24, #36), rendered per host by `nio agents sync`.
- `.claude-plugin/plugin.json`: a thin Claude Code wrapper, added once the first skill exists.
- `NORTH_STAR.md`: the vision. GitHub issues: the backlog of open decisions and deferred ideas.

## Rules for writing skills

- Write in plain markdown that any agent can follow. Don't depend on Claude-only tools
  inside a skill. If a host-specific feature helps, note it as optional.
- Each skill does one job, states its inputs and outputs (files under `.nio/`), and says
  when to stop.
- Prefer instructions over scripts. Add a script only when instructions can't be followed
  reliably.
- Every message to the human follows the shape in `NORTH_STAR.md` → "Talking to the human", and every
  skill carries that block word for word (`tests/test_talk.py` checks the copies).

## Artifacts that NIO produces in a target project

They live under `.nio/` (memory layout in `MEMORY_NORTH_STAR.md`). The artifacts are: onboarding notes,
spec, research, contracts, bindings, personas, plan, efforts/epics/tasks, jury verdicts,
change requests, and budget/usage.

## Working in this repo

- Remote: private GitHub repo `nikolajkarpic/nio` (repo-local credential helper uses that gh account).
- Make small commits with imperative messages. Stage approvals use the message form
  `nio: approve <stage>`.
- Never commit without the human asking.

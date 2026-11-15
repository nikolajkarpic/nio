# Stack

## Languages

- Python 3.11 or newer for the `nio` CLI under `src/nio/`. (source: pyproject.toml@4faabd2fb0e6)
- Skills and agent cards are plain markdown: `skills/<name>/SKILL.md` and `src/nio/agents/*.md`. (source: CLAUDE.md@b0e3cba2321c)
- TypeScript for the optional Claude Code part of NIO under `tools/claude-mods/`, shipped in the `nio` package and offered by `@nio:install`. (source: dev, D-261115-e6nx)

## Dependencies

- `fastembed>=0.9.0`. (source: pyproject.toml@4faabd2fb0e6)
- `ruamel.yaml>=0.18`. (source: pyproject.toml@4faabd2fb0e6)
- `sqlite-vec>=0.1.9`. (source: pyproject.toml@4faabd2fb0e6)
- Build backend: `hatchling`. (source: pyproject.toml@4faabd2fb0e6)
- The CLI entry point is `nio = "nio.cli:main"`. (source: pyproject.toml@4faabd2fb0e6)

## Commands

- Run the CLI in this repo: `uv run nio ...`. (source: CLAUDE.md@b0e3cba2321c)
- Install the CLI elsewhere: `uv tool install .`. (source: README.md@f72a1897d4ff)
- Self-checks: each `tests/test_*.py` runs on its own, e.g. `uv run python tests/test_flow.py`. (source: CLAUDE.md@b0e3cba2321c)
- Status-speed limit after a change to `nio flow status`: `NIO_PERF=1 uv run python tests/test_flow.py`. (source: CLAUDE.md@b0e3cba2321c)
- Real-model card tests, costly, after changing a card: `NIO_E2E=1 uv run python tests/test_lenses.py`, `tests/test_tasks_e2e.py` and `tests/test_explain_e2e.py`. (source: CLAUDE.md@b0e3cba2321c)

## CI

- One GitHub Actions workflow, `memory`, runs on pull requests: `uv run nio index --check --base origin/<base branch>`. (source: .github/workflows/memory.yml@41c42cdbd058)
- The test suites do not run in CI; they run locally. (source: dev, 2026-11-15)

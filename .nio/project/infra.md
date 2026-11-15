# Infra

## Cloud provider

- None: NIO runs locally on the developer's machine and in GitHub Actions. (source: dev, 2026-11-15)

## Deployables

- A Claude Code plugin, `nio`, version 0.0.1. (source: .claude-plugin/plugin.json@35e195210457)
- The `nio` CLI, installed with `uv tool install .` or run in the repo with `uv run nio`. (source: README.md@f72a1897d4ff)

## Eventing and queues

- None. (source: dev, 2026-11-15)

## Storage

- Plain files in git under `.nio/` are the state, with no database of record and no daemon. (source: README.md@f72a1897d4ff)
- The memory index `.nio/cache/index.db` is a local SQLite cache, rebuilt from the records. (source: README.md@f72a1897d4ff)
- The embedding model is cached under `$XDG_CACHE_HOME/nio/fastembed`, by default `~/.cache/nio/fastembed`. (source: src/nio/index.py@9e6282ccdfd4)

## Secrets

- None: the CI workflow uses no secrets. (source: .github/workflows/memory.yml@41c42cdbd058)

## Environments

- None beyond each developer's clone and CI on pull requests. (source: dev, 2026-11-15)

## Deploys

- No releases: users clone the private repo, run `uv tool install .`, and load the plugin from the checkout. (source: dev, 2026-11-15)

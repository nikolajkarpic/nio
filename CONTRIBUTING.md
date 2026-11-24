# Contributing to NIO

Read [NORTH_STAR.md](NORTH_STAR.md) first. Every change must serve it.

## Submitting an issue

1. Go to **Issues → New issue** and pick a template:
   - **Bug**: something in a skill or the `nio` CLI doesn't work. Include steps to reproduce.
   - **Idea**: something that doesn't serve the current path yet.
   - **Decision**: an open choice that needs to be made and recorded.
   - **Design**: something that needs deep design before it can be built.
2. Search the existing issues first, to avoid duplicates.
3. A maintainer adds the `type:*` and `area:*` labels.

## Submitting a pull request

1. Open an issue first for anything bigger than a small fix, so the approach is agreed before you build it.
2. Fork the repo and branch from `main`.
3. Make small commits with imperative messages ("Add X", not "Added X").
4. Run the self-checks listed in [CLAUDE.md](CLAUDE.md) under *Repo layout* (`uv run python tests/test_*.py`).
5. Open the PR against `main`, link the issue (`Closes #123`), and fill in the template.

## License of contributions

NIO is [MIT](LICENSE)-licensed. By opening a pull request, you agree that your contribution is licensed under the MIT License too.

## After you open the PR

`main` is protected: a PR merges only after CI passes (the memory check and the gitleaks secret scan) and a maintainer approves it.
Never commit secrets. The gitleaks scan fails the PR if it finds one.

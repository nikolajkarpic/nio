---
id: D-261024-jpst
type: decision
title: "Git hooks refresh the index in the background, installed by nio hooks"
status: human
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/hooks.py", ".github/workflows/memory.yml"]
tags: ["hooks", "git", "ci"]
supersedes: []            # IDs of records this replaces
---
## Decision
`nio hooks` adds a marked block to `post-merge`, `post-checkout` (branch switches only) and `post-rewrite` that starts `nio index` in the background, keeping whatever the hooks already do. The block calls `nio` by the absolute path it was installed with and ends with `true`. `post-merge` also prints `nio check` errors. `pre-commit` and `pre-push` run the CI check (`nio index --check` against `HEAD` and against the remote's default branch) and stop git on errors, unless `nio` is missing or `--no-verify` is given. CI runs `nio index --check` on every pull request against its base branch.
## Why
Git must never wait on memory: loading the model takes seconds and a first build minutes. Hooks run with a different PATH than the shell (GUIs, `uv run` venvs), so a path saved at install works where a PATH lookup would not. A `post-checkout` hook's status becomes git's, so a skipped step must not fail the checkout. Two branches superseding the same decision both edit the old record's `outdated_by` line, so git stops there and the merge ends in `git commit`, which fires no `post-merge`; CI is what blocks that case, the hook only helps on merges that went through.
Catching a broken record before commit or push is cheaper than a failed PR; the checks stay skippable so memory never traps code.
## Rejected alternatives
- A hook manager such as the pre-commit framework: a new dependency for three short scripts.
- Indexing in the foreground: blocks every pull and checkout.
- A path filter on the CI workflow: a PR that moves code would skip the check, and the filter would not fit other projects.
## Reuse
Rerun `nio hooks` after moving the repo or reinstalling `nio`; it adds nothing twice.

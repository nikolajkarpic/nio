---
slug: 2026-11-08-project-onboarding
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: project onboarding

## Prerequisites
- `uv sync` in the NIO repo; `git --version` prints a version.
- A scratch repo: `git init demo && cd demo`, run every command below inside it as `uv run --project <nio repo> nio ...` (written `nio` below).

## Scenarios

### QS-1 Onboard an existing repo (UJ-1; manual) [agent]
- Needs: the scratch repo holds README.md (`# Shop: sells tea`), pyproject.toml (`dependencies = ["flask"]`), a git-ignored `.env` with `KEY=s3cret` and `main.tf`; a person plays the dev.

1. `nio onboard scan`
   Expected:
   ```
   contains: product-docs README.md
   contains: manifests pyproject.toml
   contains: iac main.tf
   contains: secrets .env
   ```
2. Run `/nio:onboard`, answer two docs' questions, then say stop; run it again and finish.
   Expected:
   ```
   contains: next: stack
   ```
3. `cat .nio/project/onboarding.json`
   Expected:
   ```
   contains: "state": "done"
   ```
- Pass when: every step matched; the second run's first question is about stack.md; `s3cret` appears in no file under `.nio/project/`.

### QS-2 Onboard an empty repo (UJ-2; manual) [agent]
1. In a scratch repo with only `.gitignore`, run `/nio:onboard` and answer product, personas and principles.
   Expected:
   ```
   contains: done
   ```
2. `grep -c "NEEDS CLARIFICATION" .nio/project/stack.md`
   Expected:
   ```
   contains: 4
   ```
- Pass when: no question asked about stack, architecture or infra.

### QS-3 Reconcile after a change outside NIO (UJ-3; manual) [agent]
- Needs: QS-1 finished.

1. `echo '# extra' >> pyproject.toml && nio status`
   Expected:
   ```
   contains: stale: stack.md (pyproject.toml changed)
   ```
2. Run `/nio:reconcile-onboarding`, decline the proposed edit; then `nio status`.
   Expected:
   ```
   contains: onboarding: done
   ```
- Pass when: the second status prints no `stale:` line.

### QS-4 A stage reads the docs (UJ-4; auto) [agent]
- Needs: a scratch repo with `nio onboard start`, then the six docs copied from `src/nio/templates/project/` into `.nio/project/` and each confirmed with `nio onboard confirm <doc>`.

1. `nio pack "add a refund button" --reader worker`
   Expected:
   ```
   contains: ## Project docs
   contains: ### stack.md
   contains: ### principles.md
   ```
2. `nio pack "add a refund button" --reader spec`
   Expected:
   ```
   contains: ### product.md
   contains: ### personas.md
   ```
- Pass when: both steps matched and the worker pack holds no `### product.md`.

---
id: C-261115-lkci
type: change
title: "Code is right, spec is stale: J-2 at pr"
answers: why              # why | reuse | jury
date: 2026-11-15
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-15-effort-drilldown-install/spec.md"
outcome: rejected          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
J-2 at pr says the code contradicts CT-8, FR-22, AC-25, and the code is the right side: The mods folder has no checkout fallback.
- situation (consistency): CT-8 says `mods_dir()` returns the package's `mods` folder when it exists, otherwise the checkout's `tools/claude-mods`, and raises `ValueError("no NIO mods in this nio install")` when neither exists. The code returns only `Path(__file__).parent / "mods"`. In a NIO checkout installed in editable mode (`uv sync`), the wheel's force-include is not copied, so `src/nio/mods` does not exist. `nio mods install` then passes that missing path to `claude plugin install --marketplace`, and each mod's outcome line reads `failed`. The checkout is the case CT-8 keeps working.
- situation (correctness): nio runs from an editable install or a checkout. `src/nio/mods` is absent, so `mods_dir()` points at a missing folder and `claude plugin install ... --marketplace <missing>` fails for both mods. CT-8 says to return `tools/claude-mods` when `nio/mods` doesn't exist, and to raise `ValueError` when neither exists.
## Proposed change
Change CT-8, FR-22, AC-25 in spec.md to match the code. Reject it and a fix task changes the code instead.
## Human decision
Pending.

## Human decision
Rejected by the human on 2026-11-15 in the orchestrator session: "Fix the code: reject the change request; a fix task adds the checkout fallback the spec asks for, so install works from a checkout and from an installed package."

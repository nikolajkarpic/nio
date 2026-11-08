---
id: C-261108-unxo
type: change
title: "Onboarding architecture note: jury packs append the docs directly; progress keeps the seen files"
answers: why              # why | reuse | jury
date: 2026-11-08
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-08-project-onboarding/architecture.md"               # the spec, plan or record that is wrong
outcome: accepted          # pending | accepted | rejected
paths: [".nio/specs/2026-11-08-project-onboarding/architecture.md"]
tags: ["onboarding", "architecture"]
supersedes: []
---
## What is wrong
The plan jury (2026-11-08-project-onboarding, J-1, J-4, J-6) found that the architecture note says the jury's scope and architecture-fit packs call `pack.build`, while the plan appends `onboard.docs_for` directly (calling `pack.build` would also add memory records to those lens packs), that a lens could not quote those docs, and that reconcile cannot tell a new file without a record of the files already seen.
## Proposed change
The note says the worker pack goes through `pack.build`, the two lens packs append `onboard.docs_for` and `jury.sources` lists those docs; `onboarding.json` gains `seen`, and `nio onboard` gains `changed` with no ref and `reconciled`.
## Human decision
Accepted 2026-11-08 by the orchestrator under the human's standing grant (orchestrator / claude-code / claude-opus-5-5, delegated by human) to take the recommended option; the human can reject it.

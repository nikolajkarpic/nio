---
id: C-261030-fohc
type: change
title: "Implementation-jury spec: the CLI's own findings skip the refuter, and a new major in a re-review goes to the human"
answers: why              # why | reuse | jury
date: 2026-10-30
by: "human"                # role / host / model, or human
run: "R-261030-n5zc"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-27-implementation-jury/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: [".nio/specs/2026-10-27-implementation-jury/spec.md", ".nio/specs/2026-10-27-implementation-jury/contracts.md", ".nio/specs/2026-10-27-implementation-jury/architecture.md"]
tags: []
supersedes: []
---
## What is wrong
The plan jury found two places the approved spec can't be built as written.
1. FR-24 sends every blocker and major to the refuter, but FR-10 says only the human may accept test tampering. A refuter that refutes a deleted test breaks FR-10, and the CLI's other findings are observations, not opinions (J-3, J-6).
2. AC-38 says a new major in a re-review gives human, but FR-32 applies the spec jury's rules unchanged, and those note it and approve (J-17).
## Proposed change
1. FR-24: only a lens's blockers and majors go to the refuter; a finding the CLI-first checks make goes to the ledger as confirmed.
2. FR-32: add the exception that a new major raised in a re-review goes to the human (AC-38).
3. architecture.md, not the spec: the throwaway copy becomes a local clone instead of a worktree, which shares refs and config with the human's repo (J-11).
## Human decision
Accepted 2026-10-30 in grill Q25, Q27 and Q29: "Skip checker", "Local clone", "Comes to you".

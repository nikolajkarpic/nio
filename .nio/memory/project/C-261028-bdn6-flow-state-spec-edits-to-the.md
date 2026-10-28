---
id: C-261028-bdn6
type: change
title: "Flow-state spec: edits to the research notes don't send an effort back"
answers: why              # why | reuse | jury
date: 2026-10-28
by: "agent / claude-code / opus"                # role / host / model, or human
run: "R-261028-hlh3"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-28-flow-state/spec.md"# the spec, plan or record that is wrong
outcome: accepted         # pending | accepted | rejected
paths: [".nio/specs/2026-10-28-flow-state/spec.md", "src/nio/flow.py"]
tags: [flow-state, owning-stage]
supersedes: []
---
## What is wrong
The Owning stage table sends an effort back to grilling when `research.md` is edited after its gate approved it. But the plan skill appends its own research notes (RF-n) to `research.md` by design, and no jury judges that file (RF-2), so every planned effort lands back in grilling. Found by running `nio flow status` on this repo after the build (2026-10-28).
## Proposed change
The `research.md` row's "edited after its gate approved it" column becomes `ignore`, as for `intake.md` and `architecture.md`. A pending change request against `research.md` still sends the effort to grilling.
## Human decision
Accepted by the human (2026-10-28, flow-state grill Q26).

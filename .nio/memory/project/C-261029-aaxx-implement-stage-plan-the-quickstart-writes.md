---
id: C-261029-aaxx
type: change
title: "Implement-stage plan: the quickstart writes the test after the claim and settles a spec problem before unblocking"
answers: why              # why | reuse | jury
date: 2026-10-29
by: "human"                # role / host / model, or human
run: "R-261029-ksbo"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-29-implement-stage/quickstart.md"               # the spec, plan or record that is wrong
outcome: accepted          # pending | accepted | rejected
paths: [".nio/specs/2026-10-29-implement-stage/quickstart.md", "tests/test_implement.py"]
tags: [implement-stage, quickstart]
supersedes: []
---
## What is wrong
Walking the quickstart on the built stage showed two scenarios that can't pass as written:
- QS-1: the claim refuses a dirty tree, and no step writes T-1's test, so the demo had to commit the test before the claim, and red then freezes nothing (step 2 expects `tests/test_refund.py`).
- QS-3: a pending change request against `spec.md` sends the effort back to grilling (flow-state FR-35), so the claim right after unblocking is refused until the human decides the record.
## Proposed change
1. QS-1 gains a step after the claim where the test phase writes `tests/test_refund.py`; the demo helper no longer commits a test.
2. QS-3 gains a first step where the human decides QS-2's change record (sets `outcome: rejected`, the spec standing), then unblocks and claims.
## Human decision
Accepted after the build, 2026-10-29: "commit it and do the change requests".

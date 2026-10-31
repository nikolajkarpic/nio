---
id: C-261030-aemp
type: change
title: "Spec problem in T-9: TC-41 (AC-53), Assert: 'the human's working tree, refs, config and `git worktree list` are unchanged, after a normal run and after a timeout.' tests/test_evidence.py:snapshot enforces this over the whole tree except `.nio/runs`, and it also compares `git status`. CT-3 says collect 'sends the findings of CT-4, CT-6 and a failed check to CT-20', and FR-40/AC-52 record a timed-out run as failed."
answers: why              # why | reuse | jury
date: 2026-10-30
by: "orchestrator / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-10-27-implementation-jury/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The plan says: TC-41 (AC-53), Assert: 'the human's working tree, refs, config and `git worktree list` are unchanged, after a normal run and after a timeout.' tests/test_evidence.py:snapshot enforces this over the whole tree except `.nio/runs`, and it also compares `git status`. CT-3 says collect 'sends the findings of CT-4, CT-6 and a failed check to CT-20', and FR-40/AC-52 record a timed-out run as failed.

The code shows: tests/test_evidence.py:429-434 (test_only_the_throwaway_copy_is_touched) runs a lint that times out, so it is a failed check. FR-42 then requires a finding, and `record_cli` writes `.nio/specs/s/jury/implementation-E-1.{json,md}`. Those two new files and the `status` entry `?? .nio/specs/s/jury/` are the only differences from the snapshot; refs, config, worktrees and existing files are unchanged. TC-42's `ledger()` reads that same path through `jury.load`, so the ledger can't move.
## Proposed change
Narrow TC-41's check so the gate's own ledger doesn't count as the human's tree: `snapshot` also skips `.nio/specs/<slug>/jury/`, and the `status` comparison ignores it. Only a test edit fixes this, and the test file is frozen in this phase, so someone has to decide on it.
Handoff: 848cafd65a60962af5186484837c2d6074a7d781ebfb2c2cd3eb0b14d9b2913d
## Human decision
Accepted 2026-10-30: "Allow that one folder". The test skips only `.nio/specs/<slug>/jury/`.

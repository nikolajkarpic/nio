---
id: C-261107-bk6v
type: change
title: "Spec problem in T-4: CT-5: `tools:` becomes `[read, write]` for each of the 13 juror cards, and `TOOLS` gains `\"write\": [\"Write\"]`. Its Rules say the card's sentence is the limit."
answers: why              # why | reuse | jury
date: 2026-11-07
by: "orchestrator / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-07-fewer-gate-turns/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: CT-5: `tools:` becomes `[read, write]` for each of the 13 juror cards, and `TOOLS` gains `"write": ["Write"]`. Its Rules say the card's sentence is the limit.

The code shows: tests/test_agents.py:66 (test_sync) asserts `'tools: "Read, Grep, Glob"' in logic`, but the logic card now renders `tools: "Read, Grep, Glob, Write"`. tests/test_agents.py:124 (test_ac12_test_proof_exists_with_an_at_plan_section) asserts `meta["tools"] == ["read"]` for test-proof, but the card now reads `tools: [read, write]`. Both older assertions pin the old tool list, and the test file is frozen.
## Proposed change
Update the two frozen assertions to the CT-5 tool list: test_sync expects `tools: "Read, Grep, Glob, Write"` for logic, and test_ac12 expects `["read", "write"]` for test-proof. This needs a change to the frozen test file, so I did not make it.

Handoff: ed774256610525a5eb25e5345bc4a4f8a41a31cf3ad79f1442499568b133af25
## Human decision
Accepted (delegated to the orchestrator by the human): the two older assertions in tests/test_agents.py that pin the old read-only tool list are updated to CT-5's `[read, write]` in T-4's test phase. No spec or plan change: CT-5 already says the cards gain the write tool.

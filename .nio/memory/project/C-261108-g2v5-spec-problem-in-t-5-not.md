---
id: C-261108-g2v5
type: change
title: "Spec problem in T-5: Not a spec conflict. The review failure comes from T-3 (commit fb860f6), which made spec.new refuse full and epic specs until onboarding is done or skipped, and did not update tests/test_spec.py."
answers: why              # why | reuse | jury
date: 2026-11-08
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-08-project-onboarding/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: Not a spec conflict. The review failure comes from T-3 (commit fb860f6), which made spec.new refuse full and epic specs until onboarding is done or skipped, and did not update tests/test_spec.py.

The code shows: tests/test_spec.py:51 calls spec.new(root, f"new-{route}", route) on a fresh repo with onboarding not started; src/nio/spec.py:55 raises 'onboarding is not started'. Traceback: ValueError at src/nio/spec.py:55.
## Proposed change
Outside T-5's Files. Either T-3's follow-up updates tests/test_spec.py:test_templates_need_filling to mark onboarding skipped (nio onboard skip) before the loop, or the test passes route lite. Owner should decide which.

Handoff: c54064593957d261fcc0784baeeb854164c9a5e701b0e8c92cb6868fc15d0021
## Human decision
Accepted (human, 2026-11-08): test_templates_need_filling marks onboarding skipped before creating specs, keeping its full and epic coverage. Fixed in tests/test_spec.py.

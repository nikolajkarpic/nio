---
id: C-261115-b3lo
type: change
title: "Spec problem in T-38: J-48 (T-36 listed src/nio/implement.py but no commit changed it); the pack's TC-6 must fail first"
answers: why              # why | reuse | jury
date: 2026-11-15
by: "driver / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-15-effort-drilldown-install/tasks.md"
outcome: accepted         # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The tasks say: T-38 / J-48 (T-36 listed src/nio/implement.py but no commit changed it); the pack's TC-6 must fail first.

The code shows: TC-6 passes on arrival (`uv run python tests/test_pane.py`: 26 pass), so red cannot fail on it. The real small gap in src/nio/implement.py stands: the self-check reader in `SUMMARY` (implement.py:74) reads failures with `^FAIL (\S+)`, so a failing self-check name with a space (e.g. a path holding a space) is cut at the space in the suite's `failing` list.
## Proposed change
Apply the pass-on-arrival standing rule (#49): retire T-38 and add one direct-mode fix task under E-8 (Files: src/nio/implement.py, tests/test_implement.py) whose new test proves a failing self-check name with spaces is reported whole, plus the fix in implement.py's self-check reader.
## Human decision
Accepted under the human's standing pass-on-arrival rule (#49; precedents C-261115-duou, C-261115-lncp, C-261115-hkrz) on 2026-11-15: retire T-38 (TC-6 passes on arrival) and add a direct-mode fix task (src/nio/implement.py, tests/test_implement.py) with a test that a failing self-check name with spaces is reported whole.

---
id: C-261107-bff2
type: change
title: "Spec problem in T-2: CT-4: `git(root, *args, full=False, raw=False)`, and `land` and `shelve` call `records.git(..., raw=True)`."
answers: why              # why | reuse | jury
date: 2026-11-07
by: "orchestrator / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-07-review-fixes/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: CT-4: `git(root, *args, full=False, raw=False)`, and `land` and `shelve` call `records.git(..., raw=True)`.

The code shows: The frozen fakes at tests/test_waves.py:72, :354 and :379 are `def fake(r, *args, full=False)`. They replace `records.git` and forward `full=full` only. `land` calling `records.git(..., raw=True)` therefore raises `TypeError: fake() got an unexpected keyword argument 'raw'`. That fails test_ac9_failed_commit_restores_and_retry_lands and test_ac9_raising_commit_restores_the_main_tree (26 tests, 2 failed).
## Proposed change
Either change those three fakes to accept `**kw` and forward it, or have CT-4 put the raw read in a separate function, for example `records.git_raw(root, *args)`. `land` and `shelve` would call that function, and `git()` would stay untouched.

Handoff: bc8e1dfae84caf54e6c668be2184dd2249dd5059845770928095c30bd27aa142
## Human decision
Accepted (delegated to the orchestrator by the human): the three older fakes in tests/test_waves.py (lines 72, 354, 379) that replace `records.git` take and forward `**kw`, so `raw=True` reaches the real `git`. No spec or plan change: CT-4 stays as written. The test phase makes that edit; the code phase keeps CT-4.

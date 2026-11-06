---
id: C-261106-mao2
type: change
title: "Spec problem in T-15: QS-5 step 1 in .nio/specs/2026-11-05-implement-followups/quickstart.md:50: `NIO_PERF=1 uv run python tests/test_implement.py && uv run python tests/test_flow.py && echo ok`"
answers: why              # why | reuse | jury
date: 2026-11-06
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-05-implement-followups/spec.md"
outcome: rejected          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: QS-5 step 1 in .nio/specs/2026-11-05-implement-followups/quickstart.md:50: `NIO_PERF=1 uv run python tests/test_implement.py && uv run python tests/test_flow.py && echo ok`

The code shows: tests/test_flow.py:1357-1415 already gates the 2-second limit on NIO_PERF (status_speed, test_nfr3_status_speed and test_ac18_status_speed_gated, which is TC-15). The only defect is in the quickstart command. The shell applies the inline `NIO_PERF=1` to `test_implement.py`, which does not read it. `tests/test_flow.py` therefore runs with NIO_PERF unset, and the limit is never checked.
## Proposed change
Edit quickstart.md:50 to `uv run python tests/test_implement.py && NIO_PERF=1 uv run python tests/test_flow.py && echo ok`.

Handoff: b85a7cbaaa9a32f09a21345009982e0cae1f3b8c042051cdbd8bc29dfcf4952d
## Human decision
Rejected (by the orchestrator under the human's standing delegation, 2026-11-06). QS-5 serves UJ-5, "a task's review runs the full suite on a loaded machine": its job is to show that `NIO_PERF=1` in the caller's environment doesn't fail the run. Moving `NIO_PERF=1` onto `tests/test_flow.py` would make the journey assert the 2-second limit on every evidence run, which fails under load and is what US-5 removes. The limit stays a manual self-check (FR-15, FR-18, CLAUDE.md). T-15 is retired.

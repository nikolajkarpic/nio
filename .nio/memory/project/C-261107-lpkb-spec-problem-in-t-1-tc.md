---
id: C-261107-lpkb
type: change
title: "Spec problem in T-1: TC-1 Action: before `done grilling`, with `[default]` left in the spec, `tasks.may_start(root, S)` is `(False, \"the bug-fix spec must pass nio check spec --gate first (the grill)\")`"
answers: why              # why | reuse | jury
date: 2026-11-07
by: "orchestrator / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-07-lite-path/spec.md"
outcome: rejected         # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: TC-1 Action: before `done grilling`, with `[default]` left in the spec, `tasks.may_start(root, S)` is `(False, "the bug-fix spec must pass nio check spec --gate first (the grill)")`

The code shows: tests/test_flow.py:1392 builds the spec from tests/fixtures/spec/spec-bugfix.md, which has no `[default]` and no open points (grep -c default = 0). `spec.check(root, S, gate=True)` returns no errors on it, so CT-3's `may_start` correctly returns (True, ...) and the assertion at line 1392 fails.
## Proposed change
In test_lite_route_stages, add a `[default]` marker to the written spec.md before the first `may_start` assertion (for example append `- Refunds to a different payment method. [default]` under Non-goals/Expected behaviour), then remove it before `done grilling`. Alternatively change the fixture. The production code needs no change.

Handoff: 855b0af9e37330d8e9efee6336ffc4474c836df65f1868d7898e03a9143ba7e6
## Human decision
Rejected (delegated: orchestrator under the human's standing authority, 2026-11-07). The spec and plan are right: TC-1 says the spec still holds a `[default]` before the grill, and the test-phase worker built it from a fixture with none. The fix is in T-1's own test, and in `tests/test_tasks.py:test_ac59`, an older test pinning the spec-jury rule for lite (#97): T-1 is re-run with both in its scope.

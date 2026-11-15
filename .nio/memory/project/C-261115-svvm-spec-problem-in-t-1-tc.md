---
id: C-261115-svvm
type: change
title: "Spec problem in T-1: TC-26 (tests.md): Setup `effort(\"done\")`; `run_main(root, \"flow\", \"show\", S, \"--json\")` asserts exit 1 and stdout `{\"error\": f\"{S} is done\"}`. CT-2: the effort's stage is `done` → code 1, `{\"error\": \"<slug> is done\"}`."
answers: why              # why | reuse | jury
date: 2026-11-15
by: "driver / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-15-effort-drilldown-install/tests.md"
outcome: accepted         # pending | accepted | rejected
paths: [".nio/specs/2026-11-15-effort-drilldown-install/tests.md"]
tags: []
supersedes: []
---
## What is wrong
The spec says: TC-26 (tests.md): Setup `effort("done")`; `run_main(root, "flow", "show", S, "--json")` asserts exit 1 and stdout `{"error": f"{S} is done"}`. CT-2: the effort's stage is `done` → code 1, `{"error": "<slug> is done"}`.

The code shows: tests/test_flow.py:49-82 `effort(stage)` brings an effort only up to `stage`, and its docstring says that stage's own guard doesn't pass. The fixture ends with an approved tasks gate and no history.jsonl. So `effort("done")` leaves the effort at stage `implementing`, not `done`. I checked this: `flow.where(root, S)["stage"]` is `implementing` (src/nio/flow.py:684-780), and no `show` that follows CT-2 can report `is done` for it. `where` only returns `done` after a pass/override history line to `done` (see test_flow.py:1757).
## Proposed change
Change TC-26's setup to build a finished effort, i.e. `effort("done")` followed by `history(root, S, {"kind": "override", "from": "implementing", "to": "done", "reason": "shipped by hand"})`, or any other fixture whose `where(...)["stage"]` is `done`. The test file is frozen, so the test phase has to fix this.

Handoff: 4f023640178498ca46307f2d08589c5bdbca2f82a16f6c329d2b6de6e75a2ce7
## Human decision
Accepted by the human on 2026-11-15 in the orchestrator session: "Fix the setup: accept the change request: the test's setup also writes a history line that moves the effort to done, the test is rewritten, and the build resumes. Behaviour unchanged." TC-26's Setup now runs `shipped(root, S)` after `effort("done")`.

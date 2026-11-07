---
id: V-261106-vk5s
type: verdict
title: "implementation-E-4 gate for 2026-11-06-faster-checks: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-4:2026-11-06-faster-checks"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-06-faster-checks/jury/implementation-E-4.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-4 jury ruled **rejected** for `2026-11-06-faster-checks` in round 1 (1 disposed, 6 open, 5 refuted). Ledger: `.nio/specs/2026-11-06-faster-checks/jury/implementation-E-4.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | approve |
| conformance | claude-code | claude-sonnet-5-5 | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | claude-sonnet-5-5 | approve |
## Reasons
- unresolved: J-12
- J-12 [blocker/gap] AC-1 has no passing evidence: disposed fix-task
- J-2 [minor/risk] Ctrl-C is swallowed as exit code 1: open
- J-3 [minor/gap] AC-3 restore covers only four things, not the other state a shared process keeps: open
- J-4 [minor/risk] AC-1's 60 s and "results unchanged" claim has no observed evidence: open
- J-7 [minor/gap] The AC-4 test reads source text and does not show a subprocess starts: open
- J-10 [minor/untestable] The 60-second limit on test_implement.py is not shown anywhere in the pack: open
- J-11 [minor/risk] The AC-4 test reads source text and does not show a subprocess starts: open
## What was rejected
- J-1 Output from child processes escapes the in-process capture: refuted (implement.py:18 starts the test command with stdout=PIPE, so the CLI reads and prints the child's output itself and run_main captures it. `tests/test_implement.py:nio` is only called for `check tasks` (lines 591, 596). CT-1 keeps `tests/test_flow.py:nio` as a subprocess for the commands that spawn heavy children.)
- J-5 No test measures the under-60-s runtime: refuted (Plan.md:69 maps NFR-1 to "none" tests, and plan.md:77 says a test file can't time itself, so QS-1 is the measurement. TC-1 explicitly leaves "the time limit itself (under 60 s)" to QS-1. The tasks jury already refuted the same point (tasks J-3).)
- J-6 The once-per-process model cache has no test: refuted (Plan.md:69 maps NFR-1/CT-2 to no test, and the tasks jury already refuted the same request (jury/tasks.md J-3). CT-2 fixes the cache key as (model, cache folder), which is what `functools.cache` on `_model(model, cache)` (index.py:46) does.)
- J-8 Process-isolation tests now run the CLI in-process: refuted (`test_ac49_time_limit` uses the shared `flow` helper, not its own `subprocess.run`, so it is not one of the RF-2 and TC-4 tests. Its timeout and process group belong to the test command that `implement.run` spawns in a child (implement.py:18), which stays a subprocess when the CLI runs in-process. FR-1 requires the shared helper to go in-process.)
- J-9 A lock held by another pid is tested in-process: refuted (`test_ac56_stale_lock` goes through the shared `cli` helper, and CT-1 says `cli` calls `run_main` with no caller changes. The dead pid is a separate process the test itself starts. RF-3 says the lock check works in-process and only the pid-and-host check differs, and TC-4 lists the isolated tests, which do not include this one.)

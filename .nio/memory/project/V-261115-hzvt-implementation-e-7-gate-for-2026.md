---
id: V-261115-hzvt
type: verdict
title: "implementation-E-7 gate for 2026-11-08-explainer: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-15
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-7:2026-11-08-explainer"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-08-explainer/jury/implementation-E-7.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-7 jury ruled **rejected** for `2026-11-08-explainer` in round 1 (14 disposed, 5 open, 2 refuted). Ledger: `.nio/specs/2026-11-08-explainer/jury/implementation-E-7.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | block |
| conformance | claude-code | sonnet | approve |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | sonnet | approve |
## Reasons
- unresolved: J-1, J-2, J-3, J-4, J-5, J-6, J-7, J-8, J-9, J-16, J-17, J-18, J-19, J-20
- J-1 [major/gap] test tampering: test_ac16_new_failure_only in tests/test_implement.py is deleted: disposed fix-task
- J-2 [major/gap] test tampering: test_ac35_unknown_runner_review in tests/test_implement.py is deleted: disposed fix-task
- J-3 [major/gap] test tampering: test_ac44_broken_or_fewer in tests/test_implement.py is deleted: disposed fix-task
- J-4 [major/gap] test tampering: test_full_suite_waits_for_the_epic_to_close in tests/test_implement.py is deleted: disposed fix-task
- J-5 [major/gap] test tampering: test_tests_epic_replaces_the_suite_until_the_last_epic in tests/test_implement.py is deleted: disposed fix-task
- J-6 [major/gap] test tampering: test_review_fails_a_crashed_self_check_suite in tests/test_implement.py is deleted: disposed fix-task
- J-7 [major/gap] test tampering: test_review_fails_a_crash_beside_a_baseline_failure in tests/test_implement.py is deleted: disposed fix-task
- J-8 [major/gap] test tampering: test_ac15_review_still_fails in tests/test_implement.py is deleted: disposed fix-task
- J-10 [minor/risk] An unreadable file at a candidate path crashes the command instead of being skipped or refused: open
- J-11 [minor/risk] Two runs of the same new topic get the same path, and the second overwrites the first with no warning: open
- J-14 [minor/risk] Missing-file error can raise on an unresolved root: open
- J-15 [minor/gap] Topic-mode check test never makes the check fail: open
- J-21 [minor/inconsistency] TC-26 is claimed by T-13 but its test is not delivered in E-7: open
## What was rejected
- J-12 No test for AC-34 (same topic continues its file): refuted (tasks.md gives TC-26 (`test_ac34_same_topic` in tests/test_explain_e2e.py) to T-15 in epic E-8 as well as T-13. T-30, the only E-7 e2e task, lists TC-23, TC-24 and TC-27 and serves AC-18, AC-19 and AC-35, not AC-34. `explain.topic`'s `continue:` and `-2` behaviour is already unit-tested in `test_ct6_topic` (tests/test_explain.py). The e2e test is planned for the next epic, so it is not missing from the plan.)
- J-13 AC-18, AC-19 and AC-35 are proved only by tests that skipped: refuted (history.jsonl records `NIO_E2E=1 uv run python tests/test_explain_e2e.py test_ac18_topic_path test_ac19_no_research_skill test_ac35_clash` with `"code": 0` in the T-30 evidence (run R-261115-52ya). The skipped output the finding quotes comes from a run without the env var, and a real passing run is on record. I did not check the line's output text beyond the exit code.)

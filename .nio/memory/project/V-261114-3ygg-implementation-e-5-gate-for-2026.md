---
id: V-261114-3ygg
type: verdict
title: "implementation-E-5 gate for 2026-11-08-project-onboarding: approved (round 6)"
answers: jury             # why | reuse | jury
date: 2026-11-14
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-5:2026-11-08-project-onboarding"
outcome: approved
tier: medium
paths: [".nio/specs/2026-11-08-project-onboarding/jury/implementation-E-5.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-5 jury ruled **approved** for `2026-11-08-project-onboarding` in round 6 (1 fixed, 1 merged, 7 open, 3 refuted). Ledger: `.nio/specs/2026-11-08-project-onboarding/jury/implementation-E-5.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | approve |
| adversary | claude-code | sonnet | approve |
| adversary | claude-code | sonnet | approve |
| conformance | claude-code | sonnet | approve |
| conformance | claude-code | sonnet | approve |
| conformance | claude-code | sonnet | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | sonnet | approve |
| correctness | claude-code | sonnet | approve |
| correctness | claude-code | sonnet | approve |
| security | claude-code | sonnet | approve |
| security | claude-code | sonnet | approve |
| security | claude-code | sonnet | approve |
## Reasons
- J-2 [minor/risk] Free-text answer written in place of NEEDS CLARIFICATION is not contained: open
- J-5 [minor/inconsistency] The grill's outputs and provenance lists do not cover the new project-doc writes: open
- J-6 [minor/inconsistency] Delegated answers to blank tech fields are recorded as the dev's own: open
- J-8 [minor/untestable] test_ac14 can pass while most of the step fails: open
- J-10 [minor/untestable] The AC-13 "no stack question" check can pass without catching anything: open
- J-11 [minor/risk] Two grills filling the same blank field overwrite each other silently: open
- J-12 [minor/gap] AC-14 test checks only stack.md: open
## What was rejected
- J-3 AC-14 e2e covers only one of three docs and one field: refuted (The finding describes a test that no longer exists. tests/test_onboard_e2e.py:328-352 scripts one answer each for stack (Python 3.12), architecture (shop) and infra (AWS). For each doc it asserts the answer is present, `NEEDS CLARIFICATION` is gone from that body, the `(source: dev, <slug> grill Q<n>)` form is present and no `@<hash>` appears. It also asserts the unanswered Storage field stays blank. skills/grill/SKILL.md:73-75 now defines the repo-found form `(source: <path>@<hash>)`, so the provenance gap is closed. The "result unknown" point is the same one J-4 raised, and the ledger refutes it with a recorded NIO_E2E run. A lite-spec negative case is still untested, but AC-14 does not require one.)
- J-4 AC-13 test has no recorded passing run: refuted (history.jsonl line 253 records a `green` event for T-67 with command `NIO_E2E=1 uv run python tests/test_onboard_e2e.py test_ac13_empty_repo` (run R-261114-vhwo). The finding's premise, that only a skipped run exists, is wrong, because the e2e run with the env var is already recorded as evidence.)
- J-7 A dev answer is written into the doc with no rule for its shape: refuted (skills/grill/SKILL.md:73-76 already says "Fields the human doesn't know stay `NEEDS CLARIFICATION`", so the "don't know" case is settled. Re-asking an unknown field on each full spec is the intended behaviour ("Run this before finishing"). The heading, secret and multi-line answer cases are speculative, and nothing in the spec or AC-14 requires an answer-shape rule.)

---
id: V-261106-heal
type: verdict
title: "spec gate for 2026-11-06-faster-checks: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:2026-11-06-faster-checks"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-06-faster-checks/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **rejected** for `2026-11-06-faster-checks` in round 1 (21 open, 1 refuted). Ledger: `.nio/specs/2026-11-06-faster-checks/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| logic | claude-code | sonnet | block |
| scope | claude-code | claude-haiku-5-5 | block |
| testability | claude-code | claude-sonnet-5-5 | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-4, J-6, J-7, J-8, J-9, J-10, J-11, J-12, J-13, J-14, J-15, J-16, J-17, J-18, J-19, J-20, J-21, J-22
- J-1 [major/risk] Reuse and "covered" can pass what the copy would fail: open
- J-2 [major/gap] A lost or crashed file can leave the parallel suite at exit 0: open
- J-3 [major/gap] In-process isolation covers only cwd and env: open
- J-4 [major/risk] A lenient `none` can discard real findings: open
- J-6 [major/gap] FR-6 reuses a suite pass without the clean-tree condition that UJ-2 names as misuse: open
- J-10 [major/contradiction] AC-7 requires failing tests to be named and also says only the exit code is read: open
- J-12 [major/contradiction] A finding without `gap` is both invalid and valid at the spec gate: open
- J-14 [major/scope] FR-12 changes the lens text every juror sees, which the parser fix does not need: open
- J-7 [minor/gap] FR-8 leaves out the failed-review row that the decision table gives: open
- J-8 [minor/gap] The exit-0 reuse rule cites a decision with no record ID: open
- J-9 [minor/inconsistency] The `retired` list uses the plan's OP prefix in a spec: open
- J-11 [minor/inconsistency] "Roughly as long as its slowest file" contradicts "eight at a time": open
- J-13 [minor/inconsistency] FR-8 does not cover the failed-review and other-command rows of the decision table: open
- J-16 [minor/inconsistency] Spec uses a provenance tag the template does not define: open
- J-17 [minor/inconsistency] The reuse rule's decision has no real ID, so FR-7's boundary cannot be traced: open
- J-21 [minor/gap] Covered-journey rule has no case for mixed or partly matching steps: open
- J-22 [minor/gap] Only a single failing file is tested, so hidden or interleaved failures are not caught: open
## What was rejected
- J-5 Fix-check reuse (AC-16) leaves out the same-commit, clean-tree and command checks: refuted (FR-13 reuses the suite result "under FR-6 and FR-7", which brings in the same-commit, clean-tree, exit-0 and configured-suite conditions (`tests.epic` is excluded in FR-7). FR-8 and AC-10 describe the general evidence run ("when evidence collects", "as before"), and they apply to the fix-check round too. The decision table covers a review that ran a non-configured command in its "no" row. AC-16 is shorter than FR-7, but nothing in it contradicts FR-7.)

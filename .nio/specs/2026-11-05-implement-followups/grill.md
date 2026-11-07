# Grill: 2026-11-05-implement-followups

Delegated session: the human asked to run the whole flow on the recommended answers (2026-11-05). Every answer below is the agent's recommendation, tagged `[agent]`.

## Fact · OP-1, OP-4, OP-5, OP-7, OP-9, OP-10, OP-12, OP-13 · 2026-11-05
Facet: meaning, change, verification
Found: RF-1 to RF-16 in research.md. Patched: A-1 to A-5, UJ-1 to UJ-5, AC-10, FR-8, decision tables, non-goal; retired OP-1, OP-4, OP-5, OP-7, OP-9, OP-10, OP-12, OP-13

## Q1 · OP-2 · 2026-11-05
Question: Is a blocked handoff's record made to pass by changing what `nio flow block` writes, or which headings the memory check accepts?
Facet: data
Options:
1. Change what `nio flow block` writes (recommended): the jury and the template already write the required sections (RF-3), so only one writer is wrong.
2. Widen the memory check to accept both heading sets: every reader of change records then has two shapes to handle.
3. Change both to a new shared shape: the most churn for no new behaviour.
Answer: 1. Change what `nio flow block` writes: the spec's and the code's texts go under `## What is wrong`, the smallest change under `## Proposed change`. [agent]
Patched: FR-2, AC-2; retired OP-2

## Q2 · OP-3 · 2026-11-05
Question: When `nio flow block` reuses a pending record with the old headings, is it rewritten or left for the human?
Facet: failure
Options:
1. Neither is needed: no such record is pending (RF-4); reuse keeps the record as it was written (recommended).
2. Rewrite old records on reuse: code for a case that doesn't exist.
3. Refuse to reuse an old record: same, and it blocks the task.
Answer: 1. No pending record has the old headings, so reuse needs no rewrite. [agent]
Patched: AC-3, non-goal; retired OP-3

## Q3 · OP-6 · 2026-11-05
Question: How does a `Test:` line mark a deferred TC ID, and does one a later task proves only in part still need its file at red?
Facet: meaning
Options:
1. Keep the shape every `tasks.md` already uses ("proved later by T-n" in its own `;` part), state it in the drafter card, and have `nio check tasks` check the named task proves it; a partly deferred TC counts as deferred (recommended): no new syntax, and the check keeps a deferral from losing its test.
2. A new marker such as `(later: T-n)`: cleaner to parse, but every existing `tasks.md` reads differently.
3. Leave it free prose and only drop the red check for TC IDs near "later": the misread risk stays.
Answer: 1. Keep the existing shape, state it in the drafter card, check it in `nio check tasks`; a partly deferred TC counts as deferred. [agent]
Patched: FR-3, FR-12, FR-13, AC-16, AC-19, Test line entity, glossary, risk; retired OP-6

## Call · FR-14 · 2026-11-05
Facet: verification
The worker pack reads a task's TC IDs too (RF-8); it shows only the task's own TC entries, so the worker doesn't build what a later task proves. Changes what a user can do: no. Sees: no (agents only). Who may: no. Data: no. Cost: no. [agent]
Patched: FR-14, AC-17

## Q4 · OP-8 · 2026-11-05
Question: Does a task added under `#### Fixes` count as a change that makes lenses re-run, or is it listed only so the juror sees where moved work went?
Facet: state
Options:
1. Listed only, for the juror to see; it doesn't start a re-run or withdraw an approval (recommended): keeps today's rule that Fixes work never reopens an approved gate (RF-9).
2. It counts as a change and starts a re-run: more rounds and cost for work that already has its source finding.
3. Show it only in the fix-check pack, not in `changed`: `changed` keeps hiding it, so the orchestrator still can't see it.
Answer: 1. Listed only, for the juror; no re-run on its own and no withdrawn approval. [agent]
Patched: FR-7, AC-11; retired OP-8

## Call · FR-10 · 2026-11-05
Facet: change
The evaluator's card already says not to change other lines, but its tools include a whole-file write (RF-10); the card is given an edit tool only. Changes what a user can do: no. Sees: no. Who may: no. Data: no. Cost: no. [agent]
Patched: FR-10, AC-12

## Q5 · OP-11, OP-13 · 2026-11-05
Question: What becomes of the status-speed test (flow-state NFR-3) inside a task's review?
Facet: verification
Options:
1. Assert speed limits only when `NIO_PERF=1` is set, like `NIO_E2E=1`; the test still checks the output every run; file a change record against flow-state's tests (recommended): a busy machine can't fail a review, and the limit is still checkable on request.
2. Loosen the limit to 10 seconds: still load-sensitive, just less often.
3. Retry once on a timing failure: doubles a slow test and still fails under sustained load.
Answer: 1. Speed limits are asserted only with `NIO_PERF=1`; output is checked every run; C-261105-6rme records the change against flow-state's TC-67. [agent]
Patched: FR-15, AC-18, risk, Decisions; retired OP-11, OP-13

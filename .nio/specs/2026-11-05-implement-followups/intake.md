# Intake

## Human

lets do #65

Scope decided (2026-11-05): "Bugs only": fix items 1, 2, 3, 5 and 9 only. Item 4 (a task blocked until a later epic) gets its own issue (#69), item 7 (one test file per story) moves to #59, item 6 is #59 and item 8 was done in #66.

## Source: https://github.com/nikolajkarpic/nio/issues/65

Found while building #29. Each is small; none blocks that build.

1. `nio flow block` writes a change record with `## What the spec says`, `## What the code shows` and `## Smallest change`, but the memory check requires `## What is wrong` and `## Proposed change`. The next gate commit fails until the record is hand-edited (C-261030-abpr).
2. `nio flow red` requires the command to name a test file for every TC ID in the task's `Test:` line, even one the line says a later task proves. T-2 lost an attempt to this (`src/nio/implement.py:426`).
3. `nio jury fixcheck` at the tasks gate shows removed tasks but not tasks added under `#### Fixes`, so the reviewer raised two false blockers saying the moved work had no task. The refuter caught them. `nio jury changed` omits them too.
4. No check catches a task that blocks the build itself: a rule enforced from an early epic whose only way to clear it is in a later epic. T-4 and T-27 passed the plan jury and the tasks jury this way, and C-261030-abpr fixed it by hand.
5. `nio-evaluator` rewrote `tasks.md` whole and lost epic headings. The check caught it, but the card should edit only the rating lines.

From the #29 build, on build time:

6. `Parallel: yes` is only a label: `nio flow claim` refuses while another task is claimed. A real parallel mode would use separate worktrees.
7. One shared test file blocks parallel work, because it's frozen after each test phase. The tasks drafter could use one test file per story.
8. The review runs the full suite after every task. Running the task's own tests and leaving the full suite to the end of the epic would be faster, but a break would surface later.

9. `tests/test_flow.py:test_nfr3_status_speed` asserts status takes under 2 seconds. It failed at 2.46s and 2.69s in full-suite runs under load during the #29 build and passes alone, on the changed code and on the commit before it. A failure used one of T-19's three attempts for no real reason. A wall-clock limit shouldn't be able to fail a task's review.

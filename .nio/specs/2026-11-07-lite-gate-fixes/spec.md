---
slug: 2026-11-07-lite-gate-fixes
route: lite
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3]
---
<!-- Bugfix spec (Kiro's three sections). Unchanged behaviour is never empty: it is the regression guard.
Each EB-n has an AC that is the test written first (it fails before the fix); each UB-n has a regression AC. -->
# Lite gate fixes: bug-fix epic treated as foundational, no test evidence on a lite spec

## Summary
Two defects block every lite (bug-fix) effort at its gates; both were found dogfooding the lite path (#44) on #91 and
are fixed in the #44 PR. [human] First, `nio check tasks` applies the foundational-epic rule (#42 FR-45) to a bug fix's
one epic when it is headed `## E-1 <title>` with no `(US-n)` suffix, as the template and card write it, so every AC fails
with "T-n serves AC-n, which no task depending on it serves"; the tests missed it because their fixtures head the epic
`(US-1)`. [human] Second, on a lite spec, which has no tests.md, `nio jury evidence` lists no tests (`results.json`
`tests: []`), so every AC of the implementation gate reads "no passing evidence" and files a pointless fix task. [human]
Repro: (1) draft tasks.md for a lite spec with one epic headed `## E-1 <title>` and run `nio check tasks <slug>`; (2) run
`nio jury evidence` for an implementation gate of a lite spec and read `tests` in `results.json`. [research: RF-1]

## Current behaviour
- **CB-1** WHEN a lite spec's tasks.md heads its one epic `## E-1 <title>` with no `(US-n)` suffix THEN the system reports each AC served by the epic's last task as served by no task depending on it, and `nio check tasks` fails. [human]
- **CB-2** WHEN `nio jury evidence` runs for an implementation gate of a lite spec (no tests.md) THEN the system lists no tests, and every AC reads "no passing evidence". [human]

## Expected behaviour
- **EB-1** WHEN a lite spec's tasks.md heads its one epic with no `(US-n)` suffix THE SYSTEM SHALL NOT apply the foundational-epic rule to that epic. [human]
- **EB-2** WHEN `nio jury evidence` runs for an implementation gate of a lite spec THE SYSTEM SHALL list each test function the epic's commits add to a test file (one under a `tests` or `test` folder or named `test_*`), with its result. [agent]

## Unchanged behaviour
- **UB-1** WHEN a full spec's tasks.md has a `(Foundation)` epic whose task serves an AC no dependent task serves THE SYSTEM SHALL CONTINUE TO report that task and AC, and `nio check tasks` fails. [derived: EB-1, RF-3]
- **UB-2** WHEN `nio jury evidence` runs for an implementation gate of a full spec THE SYSTEM SHALL CONTINUE TO list the tests that tests.md names. [derived: EB-2, RF-1]

## Acceptance criteria
- **AC-1** (EB-1) Given a lite spec whose tasks.md has one epic headed `## E-1 <title>` with no suffix and whose last task serves an AC, when `nio check tasks <slug>` runs, then it reports no "which no task depending on it serves" error and passes. [human]
  Observable: the check's error list is empty. Level: unit. (written first; fails before the fix)
- **AC-2** (UB-1) Given a full spec whose `(Foundation)` epic has a task serving an AC that no dependent task serves, when `nio check tasks <slug>` runs, then it reports "serves AC-n, which no task depending on it serves" for that task. [derived: EB-1, RF-3]
  Observable: the error is in the check's error list. Level: unit.
- **AC-3** (EB-2) Given a lite spec with no tests.md whose epic's commit adds a passing test function to a test file, when `nio jury evidence` runs for its implementation gate, then `results.json` lists that test with its result. [derived: EB-2, RF-1]
  Observable: `tests` in `results.json` is not empty and holds the named test. Level: integration. (written first; fails before the fix)
- **AC-4** (UB-2) Given a full spec with a tests.md naming a test, when `nio jury evidence` runs for its implementation gate, then `results.json` lists that test. [derived: EB-2, RF-1]
  Observable: `tests` in `results.json` holds the test tests.md names. Level: integration.

## Decisions
- The foundational rule is skipped on a lite spec only; full specs are unchanged (grill Q1, [agent]).
- A lite epic's tests are the test functions its commits add to test files (grill Q2, [agent], RF-1, RF-2).

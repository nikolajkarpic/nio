---
slug: <slug>
route: lite
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
apps: []                       # the apps this spec touches, when the project has docs per app
retired: []
---
<!-- Bugfix spec (Kiro's three sections). Unchanged behaviour is never empty: it is the regression guard.
Each EB-n has an AC that is the test written first (it fails before the fix); each UB-n has a regression AC. -->
# <title>

## Summary
<What is broken, who hits it, how it was found.> [default]
Repro: <steps that show the bug>

## Current behaviour
- **CB-1** WHEN <condition> THEN the system <wrong behaviour>. [default]

## Expected behaviour
- **EB-1** WHEN <condition> THE SYSTEM SHALL <right behaviour>. [default]

## Unchanged behaviour
- **UB-1** WHEN <condition> THE SYSTEM SHALL CONTINUE TO <existing behaviour>. [default]

## Acceptance criteria
- **AC-1** (EB-1) Given <context>, when <action>, then <outcome>. [default]
  Observable: <what the test asserts>. Level: <unit | integration | e2e>. (written first; fails before the fix)
- **AC-2** (UB-1) Given <context>, when <action>, then <outcome>. [default]
  Observable: <what the test asserts>. Level: <unit | integration | e2e>.

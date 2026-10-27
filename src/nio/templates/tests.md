---
slug: <slug>
retired: []                      # TC IDs removed from this plan; never reused
---
<!-- Tests template: one concrete test per acceptance criterion, at that AC's Level, plus tests for measurable
NFRs and for the misuse each journey names. A test writer must be able to write the test from its entry alone.
Provenance, permanent IDs and `retired` work as in contracts.md. Open questions go in plan.md's Open points. -->
# Tests: <title>

## Acceptance tests

### TC-1 <what it proves> (AC-1; <unit | integration | e2e>) [default]
- File: `<test file>:<test name>` (new | existing)
- Covers: CT-1
- Setup: <the state before the action, with concrete values>
- Action: <the one call, command or request>
- Assert: <the AC's Observable, with the exact values checked>

## Quality tests
<!-- Only for NFRs a test can measure. -->
### TC-2 <what it measures> (NFR-1; <level>) [default]
- File: `<test file>:<test name>` (new | existing)
- Covers: CT-1
- Setup: <load, data size or environment>
- Action: <what is run>
- Assert: <the NFR's number and how it is measured>

## Misuse tests
<!-- One per journey Misuse line in the spec that the system must handle. -->
### TC-3 <what the misuse is> (UJ-1 misuse; <level>) [default]
- File: `<test file>:<test name>` (new | existing)
- Covers: CT-1
- Setup: <the state before the misuse>
- Action: <what the careless or hostile actor does>
- Assert: <what the system does instead, observable>

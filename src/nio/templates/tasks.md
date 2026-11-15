---
slug: <slug>
retired: []                      # task IDs removed from this file; never reused
---
<!-- Tasks template: the spec's work, one epic per user story (a full spec: one per entry of the plan's build order, in
its order; a bug-fix spec: one epic, E-1). A foundational epic, when there is shared setup, comes first. Task IDs run
across the whole spec and are never renumbered or reused. No status or checkbox here: a task's status lives in the CLI's
state. Work added after approval goes under the epic's `#### Fixes` heading, with the next free ID and a `From:` line.
`nio check tasks <slug>` checks all of this and prints the estimate. Remove what doesn't apply; never write N/A. -->
# Tasks: <title>

## E-1 <what this epic delivers> (Foundation)
- Tier: strong: <why this model class>   <!-- per epic: one agent implements the whole epic -->
- Effort: med

### T-1 <what the task does>
- Files: `<file>`, `<file>`
- Serves: AC-1
- Test: TC-1                     <!-- full spec: the plan's TC-n; bug-fix spec: what the test checks, in words -->
- Depends on: none
- Parallel: no

## E-2 <what this story delivers> (US-1)
- Tier: cheap: <why>
- Effort: low

### T-2 <what the task does>
- Files: `<file>`
- Serves: AC-2
- Test: TC-2
- Depends on: T-1
- Parallel: yes

#### Fixes
<!-- Tasks added after approval: an implementation-jury finding, a "justify or remove" task, or a change request. -->
### T-3 <what the fix does>
- From: J-1 (implementation-E-2, round 1)
- Files: `<file>`
- Serves: J-1
- Test: <what the test checks>
- Depends on: T-2
- Parallel: no

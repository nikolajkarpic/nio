---
id: C-261028-7njg
type: change
title: "Tasks-stage spec: build on the plan stage and the plan jury"
answers: why              # why | reuse | jury
date: 2026-10-28
by: "agent / claude-code / opus"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-10-27-tasks-stage/spec.md"
outcome: accepted         # pending | accepted | rejected
paths: [".nio/specs/2026-10-27-tasks-stage/spec.md", "src/nio/plan.py", "src/nio/jury.py"]
tags: [tasks-stage, plan, plan-jury]
supersedes: []
---
## What is wrong
The tasks-stage spec (approved 2026-10-27) assumed the plan stage didn't exist yet. The plan stage (cb9e315) and the plan jury (83b0580, #57) now exist, and four of the spec's assumptions no longer hold:
- It branches on "a plan.md exists" (FR-20, FR-21, AC-5, AC-6). Now only a full spec has a plan stage, and a full spec always has one; a bug-fix spec never does (src/nio/plan.py `full_spec`). Its non-goal "The plan stage (#41)" and the risk "design choices are made at task time" are out of date.
- FR-2 starts the tasks stage once the spec is approved. A full spec now also needs its plan approved, and `nio check plan <slug> --approved` is what answers that (plan-jury FR-38, delivered but not wired in).
- FR-22 and AC-7 let the drafter make design choices. A full spec's design is settled by the plan, and the plan's stop list sends new design to the architecture stage.
- Epics are one per user story plus a foundational epic (FR-4, FR-5). The plan's build order already gives that cut: `Foundation`, then `US-n` entries with their own `Depends on:`, which can be story-to-story.

## Proposed change
1. FR-20 and AC-5 apply to full specs, FR-21 and AC-6 to bug-fix specs. Drop the non-goal on #41 and the "design choices at task time" risk.
2. FR-2: a full spec starts the tasks stage only when `nio check plan <slug> --approved` exits 0. A bug-fix spec needs only its spec approved.
3. FR-22 and AC-7: on a full spec the drafter makes no design choice; a gap goes back to the plan or the spec through a change request. Keep FR-22 for bug-fix specs only, or drop it (the human decides).
4. FR-4 and FR-5: on a full spec, epics follow the plan's build order: the Foundation entry becomes the foundational epic, each `US-n` entry an epic in build order, with the entry's `Depends on:` as the epic's.
5. AC-5 becomes a free check in `nio check tasks`. Every contract a build-order entry delivers names its bound file in a `Files:` line of that entry's epic, and every `TC-n` the entry lists is cited by one of the epic's tasks.
6. The `Test:` line on a full spec cites the plan's `TC-n`. This reopens D-261027-b44u's rejected alternative ("the plan's test list plus task citations"), rejected then only because the format wasn't fixed. Test code still carries no spec IDs. The human decides.
7. The tasks gate's artefact holds `tasks.md` plus the plan files and the spec, as the plan gate's holds the spec, so an approved spec or plan that later changes withdraws the tasks approval (FR-50).

## Human decision
Accepted by the human (2026-10-28). Points 3 and 6 are settled in the tasks-stage grill (session 2).

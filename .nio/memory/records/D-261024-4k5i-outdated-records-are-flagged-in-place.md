---
id: D-261024-4k5i
type: decision
title: "Outdated records are flagged in place with outdated_by"
status: human          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/records.py", "src/nio/index.py"]
tags: ["record-format", "index", "staleness"]
supersedes: ["D-261024-g5lm"]
---
## Decision
When a record is superseded or challenged, the old record gets `outdated_by: [<new ID>]`, written in the same change. Committed records may change only `paths` and `outdated_by`, and `outdated_by` only grows. The index derives each record's `standing`: current, approved, rejected, escalated, superseded, challenged, conflict, uncommitted, or drifted (30% of its touched lines changed since it was written or last given a verdict).
## Why
Under D-261024-g5lm, a decision that was outdated looked current to anyone reading its file or grepping frontmatter, because only the index knew it was outdated. Code can also drift from a decision with no new record written at all. The flag makes an outdated record visible in the file itself. Drift catches silent changes, and a fresh verdict confirms the record still holds.
## Rejected alternatives
- A bare `stale: true`: it says nothing about why, or what to use instead.
- Only deriving it in the index: the grep fallback and people browsing the folder never see it.
- Fully frozen records (D-261024-hkog): avoided one merge conflict, but hid staleness.
## Reuse
When superseding or challenging a record, add the new ID to the old record's `outdated_by` in the same commit. To clear a `drifted` standing, recheck the decision against the code and write a verdict, or supersede it.

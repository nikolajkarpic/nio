---
id: D-261106-uom5
type: decision
title: "Wave tasks land by patch, apply and a byte-snapshot restore"
status: human          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-06
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: ["AC-7", "AC-8", "AC-9", "AC-13"]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/implement.py"]                 # files or globs it touches
tags: ["flow", "implement", "waves", "git"]
supersedes: []            # IDs of records this replaces
---
## Decision
At green a wave task's worktree is staged (`git add -A`) and diffed against its claim commit into `.nio/runs/<run>/T-n.patch`, applied to the main tree with `git apply` (leaving out the effort's state.json and history.jsonl), reviewed there and committed. A failed apply blocks only that task; a failed or raising review or commit restores a byte snapshot taken just before the apply. Green refuses on a dirty main tree first.
## Why
No 3-way merge (spec non-goal); a snapshot never touches the human's own uncommitted edits, unlike a checkout of HEAD (plan jury J-9, implementation jury E-2 J-2 to J-4).
## Rejected alternatives
- Restore by `git checkout HEAD`: wipes uncommitted effort-folder edits.
- Merge worktree commits: needs commits in the worktree and conflict handling.
## Reuse
Any future "work elsewhere, land here" path (cross-host workers). Accepted risks: file modes are not restored; a crash mid-land needs `git apply -R <patch>`.

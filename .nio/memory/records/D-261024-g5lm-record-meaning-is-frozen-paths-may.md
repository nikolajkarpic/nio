---
id: D-261024-g5lm
type: decision
title: "Record meaning is frozen; paths may be repointed"
status: human          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/records.py", "src/nio/index.py"]
tags: ["record-format", "merge", "index"]
supersedes: ["D-261024-hkog"]
outdated_by: ["D-261024-4k5i"]
---
## Decision
A committed record's meaning never changes: every field except `paths`, and the whole body. `paths` may be repointed. `nio check --base <ref>` rejects any other edit to a record committed at `<ref>`. The index follows `paths` through git renames on its own, so a repoint is needed only when git cannot follow, such as a split file.
## Why
Under D-261024-hkog, a record's links to code silently broke whenever a file was renamed, and nothing could repair them. Renames are common, and "why was X done this way?" is asked most about old code. Following renames in the index fixes most cases with no effort from anyone. Editable `paths` covers the rest. Freezing everything else keeps what hkog protected: history stays honest, and status flips can never conflict in a merge.
## Rejected alternatives
- Fully immutable records with rename following only: split or rewritten files lose their link forever.
- Editable records: history could be rewritten silently, and status edits would conflict across branches again.
- Superseding a record just to update paths: a rename is not a decision, so it only adds noise.
## Reuse
To fix a stale-path warning, repoint `paths` if the code moved, or supersede the record if the decision changed.

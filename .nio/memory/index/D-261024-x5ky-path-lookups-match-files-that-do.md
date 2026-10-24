---
id: D-261024-x5ky
type: decision
title: "Path lookups match files that do not exist yet"
status: human
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/query.py"]
tags: ["query", "paths", "pack"]
supersedes: []            # IDs of records this replaces
---
## Decision
`nio query --path` and `nio pack` match each given file against every record's `paths` globs directly, in addition to the index's `touches` edges. The grep fallback does the same.
## Why
`touches` edges are built against `git ls-files`, so a file the task will create had no edges: a task creating `src/session/store.ts` missed a decision on `src/session/**`. Matching the globs directly costs one pass over the record files, which the index build already makes. The edges stay because they also follow git renames.
## Rejected alternatives
- Matching globs only for paths missing from the index: one more branch for the same result.
- Leaving it to text search: a record on the exact files is tier A and must not depend on wording.
## Reuse
Any lookup by file should match globs, not only existing files.

---
id: D-261024-aqpe
type: decision
title: "Record paths must exist when written; stale paths only warn later"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["lint"]
supersedes: []
outdated_by: ["D-261024-6tkp"]
---
## Decision
Lint requires every `paths` glob to match a tracked file when the record is written. Afterwards, an unmatched path is a warning, not an error.
## Why
Records can never be edited, so once a file is renamed or deleted an old record could never be fixed and `--check` would fail forever.
## Rejected alternatives
- Always rejecting unmatched paths: permanently failing CI after any rename.
## Reuse
Treat a stale-path warning as a hint that a superseding record may be due.

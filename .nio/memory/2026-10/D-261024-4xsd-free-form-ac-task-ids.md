---
id: D-261024-4xsd
type: decision
title: "AC and task IDs are free-form strings until templates exist"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["traceability"]
supersedes: []
---
## Decision
`serves` and `task` take any string for now. The format is fixed later, with the spec and task templates.
## Why
The templates that mint AC and task IDs are not written, and memory should not block on them. Free-form strings keep the traceability fields usable now.
## Rejected alternatives
- Inventing an ID format inside the memory spec: the templates own it.
## Reuse
When the templates fix the format, add it to the lint; old records stay as written.

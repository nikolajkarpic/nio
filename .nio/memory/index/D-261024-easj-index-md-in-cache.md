---
id: D-261024-easj
type: decision
title: "INDEX.md is generated into the cache and never committed"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md", ".gitignore"]
tags: ["index", "merge"]
supersedes: []
---
## Decision
`INDEX.md` is written to `.nio/cache/` and gitignored. The grep fallback reads record frontmatter directly.
## Why
A committed generated file changes on every new record, so it would conflict on nearly every merge. Nothing needs it in git: it can always be regenerated, and frontmatter is greppable.
## Rejected alternatives
- Committing `INDEX.md` and regenerating on conflict: a manual step on every merge.
## Reuse
Never commit generated files under `.nio/`.

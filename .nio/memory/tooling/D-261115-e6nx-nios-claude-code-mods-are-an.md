---
id: D-261115-e6nx
type: decision
title: "NIO's Claude Code mods are an optional part of the product, shipped in the nio package"
status: proposed          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-15
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: "R-261115-msx7"              # run ID; empty when written by hand
serves: ["AC-25", "AC-26", "AC-27"]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["tools/claude-mods/README.md", "skills/install/SKILL.md", "pyproject.toml", ".nio/specs/2026-11-15-effort-drilldown-install/spec.md"]                 # files or globs it touches
tags: ["mods", "install", "hosts"]
supersedes: []            # IDs of records this replaces
---
## Decision
The Claude Code mods (`background-nio-commands`, `nio-status-pane`) are an optional Claude Code part of NIO: shipped inside the `nio` package, offered once by `@nio:install` and installed for the clone only (local scope). Skills never depend on them.
## Why
Installing them by hand was easy to miss (issue #142), and a project with an installed `nio` had no checkout to install them from. NORTH_STAR keeps skills host-neutral and host features optional, which an offered, skippable mod respects.
## Rejected alternatives
- Keep them as NIO-repo dev tooling: target projects never get the pane or the drill-down.
- Install from the GitHub repo as a marketplace: the repo is private and the version could drift from the installed CLI.
- User scope: the pane would load in every Claude Code project, NIO or not.
## Reuse
Any further host-specific extra: ship it in the package, offer it at install, never make a skill need it.

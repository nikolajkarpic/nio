# Issues / backlog

## Needs deep design
- [x] **Memory and traceability.** Designed in `MEMORY_NORTH_STAR.md` (v0 scope and open
  items there). Still open: the AC and task ID format, decided with the templates.
- [ ] **Code context and search.** Compare codegraph, graphify, Obsidian and RAG on
  how many tokens they keep out of context. Decide what NIO ships or recommends.

- [ ] **Cross-host adapter and handoff format.** Define:
  - the context pack and the handoff md schema
  - sync versus background runs
  - timeouts (`agy -p` defaults to 5 minutes; `--print-timeout` raises it)
  - auth (`agy` needs one interactive login first)
  - quota awareness (the Argon weekly quota on AI Pro)

  Verify the flags with `agy --help`; `agy` is not installed yet.

- [ ] **Config schema (JSON).** Define: hosts, role→agent mapping, panel makeup, model
  escalation rules, budgets, extensions. Decide the merge rules across the
  global → team → local layers (deep merge? do arrays replace?). Ship a JSON Schema for
  validation and editor autocomplete.
- [ ] **Install flow (`nio install` + `@nio:install`).** Ask which subscriptions you have
  → check each CLI and its auth → write the global config. Then, per repo, set up the team
  config. Covers `agy` install and login.

## Open decisions
- [x] **Artifact location.** `.nio/` (decided 2026-10-24).
- [ ] **Notification channel.** Decide how "always notify" reaches the human.
- [ ] **Templates.** Write the spec template (based on spec-kit) and the plan document
  templates, each with a required-fields checklist.
- [ ] **Extension format.** Decide how users register skills, commands, rules, workers and
  juror lenses, plus their triggers and hooks. Ship linter and formatter by default.
- [ ] **Flagged verdicts.** When the small checker flags a verdict, re-run one tier up, or
  send it to the human?
- [ ] **Lite vs full routing.** Decide the criteria the evaluator uses.
- [ ] **Cross-host support.** Check what each host (Claude Code, Antigravity, Cursor,
  Codex, Grok) supports: skills format, subagents, hooks. Find the lowest common
  denominator.

## Deferred
- [ ] **Juror reputation.** Weight votes by each juror's past agreement with the human.
- [ ] **Calibration.** Compare estimated with actual usage after each epic.
- [ ] **Replay.** Rerun past jury decisions on cheaper models to find where they're safe.
- [ ] **Usage estimate.** Nice-to-have, mainly useful with API pricing.
- [ ] **Dry-run mode.** Low priority.

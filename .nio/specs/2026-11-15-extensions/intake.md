# Intake

## The human's words

> can we do the next big thing called extensions? where user can do extensions to the alreadyu implemented stuff, like adding a new step in architecture flow in FE for example with E2E tester writing e2e tests based on spec?

> write a issue for it on gh and then run full nio flow for this in auto mode from spec to impleementation

> and take recomemded ansers for all questions

## Source: https://github.com/nikolajkarpic/nio/issues/162

### What

An extension system: a user adds a **new step** to NIO's flow, plus its own agent cards and event hooks, without changing NIO. The first extension is a frontend **e2e tester**: after the plan is approved it writes browser e2e tests from the spec's ACs (`Level: e2e`). The implement stage then makes those tests pass.

Today only agent cards are extendable (#24: shipped → `~/.nio/agents` → `.nio/agents`, override by name or `<name>.append.md`). Flow stages are a fixed table in `src/nio/flow.py` (`STAGES`), so a new step has nowhere to go.

### Decided (2026-11-15, grill on #9)

1. **Scope:** an extension can add flow **steps** (its own skill, agent card, output file, optional jury check), **agent cards**, and **shell hooks** on NIO events (`after-task-green`, `gate-approved`, ... per #9's research comment).
2. **Placement:** a step goes **after any named step** (`after: plan_jury`). Two extensions on the same spot run in name order. A misplaced step fails at its own check.
3. **Triggers:** each step has a **trigger rule** (e.g. the plan touches files under a path, or the spec has an AC with `Level: e2e`). When it doesn't apply, the step is **skipped on the record**, like the lite route's skips.
4. **Check:** each step names a **check command** (exit 0 = pass). An extension may also declare a **jury gate** with its own lens cards, approved like the built-in gates.
5. **Packaging:** an extension is a **folder** (manifest, skill, cards, templates) in the same three layers as cards. `nio extensions add <path or git URL>` copies it into `.nio/extensions` (committed) and records source + version.
6. **Limits:** **add only.** Never remove, reorder or skip built-in steps or gates; `nio extensions add` refuses one that tries.
7. **E2E tester:** a **shipped extension, off by default** (`nio extensions add e2e`). It uses exactly the user-facing format, so it proves the format works. (Recommended option, taken on the human's instruction.)

### Open for the grill (to take recommended answers on the human's instruction)

- Manifest format and fields (JSON, matching `.nio/config.json`?).
- Exact hook event list, and whether a hook failure blocks.
- E2E details from #61: runner (Playwright first?), starting and stopping the app, evidence (screenshots/trace) and where it's stored, how the implement stage and PR jury see the e2e tests.
- How `nio flow next`/`status`/the status pane show an extension step.
- Cross-host: extension skills must stay plain markdown (no Claude-only tools).

### Done when

- A project can add, list and remove extensions; the flow runs an extension step at its spot, skips it on the record when its trigger doesn't apply, and guards it with its check command (and jury, if declared).
- The shipped e2e extension writes failing e2e tests from a spec's e2e ACs after the plan gate, and implement makes them pass.
- Built-in gates can't be removed or skipped by any extension (a test proves it).

Refs: #9 (decisions in its comments) · #61 · #24 · #5 · #12 · `src/nio/flow.py` STAGES · `src/nio/agents.py`


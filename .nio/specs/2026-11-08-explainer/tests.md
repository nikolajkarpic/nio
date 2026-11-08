---
slug: 2026-11-08-explainer
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: explainer

Shared setup. `tests/test_explain.py` builds its repos with `test_jury.plan_repo()` (the checkout-refunds spec and plan,
contracts CT-1 and CT-2) and approves the plan gate with `test_jury.approve_plan(root)`. A fake `npx` script, put first
on `PATH` in a temp folder, stands in for the renderer: it writes `<svg/>` to its `-o` path and exits 0; when its
input holds `BROKEN` it prints `Error: Parse error on line 2` and exits 1; with `FAKE_NPX=down` it prints
`npm ERR! network` and exits 1. "No Node" is a `PATH` holding only a temp folder with a link to `git`. `GOOD` below is an explainer
with `## Component map` (a Mermaid flowchart `a["CT-1 refund"] --> b["CT-2 pay back"]`) and `## Build order` (a
Mermaid flowchart `f["Foundation"] --> u1["US-1"]`), each followed by the walk-through `Refunds call the payments
client once.` `tests/test_explain_e2e.py` runs the skill on a real model with `test_lenses.e2e` (only under
`NIO_E2E=1`), on the same approved fixture, and reads the files it leaves.

## Acceptance tests

### TC-1 A plan explainer holds both core diagrams with walk-throughs (AC-1; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac1_core_diagrams` (new)
- Covers: CT-11, CT-1
- Setup: the approved fixture.
- Action: run `@nio:explain checkout-refunds`.
- Assert: `.nio/specs/checkout-refunds/explainer.md` exists; `explain.sections` holds a section titled `Component map` and one titled `Build order`, each with a fenced block and a `walk` of 1 to 120 words.

### TC-2 One flow per journey and one state diagram (AC-2; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac2_flows_and_state` (new)
- Covers: CT-11
- Setup: the approved fixture with a second journey `**UJ-2 Support looks a refund up** (A-1) [human]` added to the spec; the spec has one state table, `order`.
- Action: run `@nio:explain checkout-refunds`.
- Assert: exactly two sections whose title starts `Flow: `, one naming `UJ-1` and one `UJ-2`, each with a fenced block; exactly one section whose title starts `State: ` and names `order`.

### TC-3 No state table, no state diagram, check passes (AC-3; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac3_no_state_table` (new)
- Covers: CT-11, CT-4
- Setup: the approved fixture with the `### State table: order` subsection removed from spec.md before the plan is approved.
- Action: run `@nio:explain checkout-refunds`, then `nio check explainer checkout-refunds`.
- Assert: no section title starts `State: `; the check exits 0.

### TC-4 One "Read first" line at the top of quickstart, after two runs (AC-4; integration) [agent]
- File: `tests/test_explain.py:test_ac4_read_first_once` (new)
- Covers: CT-5, CT-10
- Setup: the approved fixture with `GOOD` written to explainer.md; the fake `npx`.
- Action: `nio explain finish .nio/specs/checkout-refunds/explainer.md`, twice.
- Assert: the first line after quickstart.md's front matter is `Read first: [explainer.md](explainer.md)`, and the file holds that line exactly once.

### TC-5 The node cap of 20 (AC-5; integration) [agent]
- File: `tests/test_explain.py:test_ac5_node_cap` (new)
- Covers: CT-2, CT-4
- Setup: `GOOD` with a third section `## Calls` whose Mermaid flowchart chains `n1 --> n2 --> … --> n21` (21 IDs) and a one-line walk-through; a copy with the chain cut at `n20`.
- Action: `nio check explainer checkout-refunds` on each.
- Assert: 21 IDs: exit 1 and the output holds `ERROR too many nodes: Calls (21 > 20)`; 20 IDs: exit 0 and no `too many nodes` line; `explain.nodes` of the `Calls` block returns 21 IDs.

### TC-6 The 120-word walk-through limit (AC-36; integration) [agent]
- File: `tests/test_explain.py:test_ac36_walk_limit` (new)
- Covers: CT-1, CT-4
- Setup: `GOOD` with the build order walk-through replaced by 121 words (`word ` × 121); a copy with 120.
- Action: `nio check explainer checkout-refunds` on each.
- Assert: 121: exit 1 with `ERROR walk-through too long: Build order (121 words)`; 120: exit 0.

### TC-7 The skill carries its cheat-sheet, rules and credits (AC-29; unit) [agent]
- File: `tests/test_explain.py:test_ac29_skill_text` (new)
- Covers: CT-11
- Setup: the repo's own `skills/explain/SKILL.md`.
- Action: read it.
- Assert: it has a heading containing `Mermaid cheat-sheet`, a heading containing `Diagram rules` whose text holds `one question` and `20`, and at least one line starting `Credit:` holding `https://`; `tests/test_talk.py`'s `problems` names no problem for it.

### TC-8 Plan mode refused while the plan gate is open (AC-30; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac30_refused_open_gate` (new)
- Covers: CT-11, CT-5
- Setup: the fixture with no plan gate verdict.
- Action: run `@nio:explain checkout-refunds`.
- Assert: no `explainer.md` in the spec folder; the final reply holds `plan jury` and offers a topic (`topic`).

### TC-9 A re-run keeps and marks the drill-down (AC-32; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac32_rerun_keeps_drill` (new)
- Covers: CT-11, CT-5
- Setup: the approved fixture with an explainer from a first run plus a section `## Drill-down: refund retries` (text `Retries reuse one key.`); then contracts.md gains `### CT-3 Refund list (FR-1) [agent]` with its fields, so the component map has to change, and the plan gate is approved again.
- Action: run `@nio:explain checkout-refunds`.
- Assert: the heading is `## Drill-down: refund retries (written for an earlier plan)` and its text is unchanged; the three source lines hold `implement.digest(...)[:12]` of today's spec.md, plan.md and contracts.md.

### TC-10 A re-run deletes only its own orphan images (AC-33; integration) [agent]
- File: `tests/test_explain.py:test_ac33_safe_delete` (new)
- Covers: CT-5
- Setup: the approved fixture; the spec folder holds `explainer-flow-uj-2.svg`, `explainer-drill-1.svg`, `notes.svg` and `other.svg`, and the setup writes `.nio/README.md` (what `../../README.md` names from the spec folder); explainer.md is `GOOD` plus `## Drill-down: one` (a Mermaid block, a walk-through and the link `![one](explainer-drill-1.svg)`), the drill-downs line `(drill-downs: Drill-down: one)` and the images line `(images: explainer-flow-uj-2.svg, explainer-drill-1.svg, other.svg, ../../README.md)`; the fake `npx`.
- Action: `nio explain finish .nio/specs/checkout-refunds/explainer.md`.
- Assert: exit 0; `explainer-flow-uj-2.svg` is gone; `explainer-drill-1.svg`, `notes.svg`, `other.svg` and `.nio/README.md` are byte-unchanged; the new images line names `explainer-drill-1.svg`; the output holds `deleted: explainer-flow-uj-2.svg`, `warning: ignored other.svg: not this explainer's own image` and `warning: ignored ../../README.md: not this explainer's own image`, and no other `deleted:` line.

### TC-11 A complete explainer passes (AC-6; integration) [agent]
- File: `tests/test_explain.py:test_ac6_passes` (new)
- Covers: CT-4, CT-10
- Setup: the approved fixture with `GOOD`; the fake `npx`.
- Action: `nio check explainer checkout-refunds`.
- Assert: exit 0; last line `0 errors`.

### TC-12 A contract missing from the map is named (AC-7; integration) [agent]
- File: `tests/test_explain.py:test_ac7_missing_contract` (new)
- Covers: CT-4
- Setup: contracts.md gains `### CT-3 Refund list (FR-1) [agent]` with its fields; `GOOD`, whose node labels name CT-1 and CT-2 only, with `CT-3 comes later.` added to the component map's walk-through.
- Action: `nio check explainer checkout-refunds`.
- Assert: exit 1; `ERROR component map misses CT-3`; no line names CT-1 or CT-2.

### TC-13 A missing build order is named (AC-8; integration) [agent]
- File: `tests/test_explain.py:test_ac8_missing_build_order` (new)
- Covers: CT-1, CT-4
- Setup: `GOOD` without its `## Build order` section.
- Action: `nio check explainer checkout-refunds`.
- Assert: exit 1; `ERROR missing core diagram: build order`.

### TC-14 A broken block is named (AC-9; integration) [agent]
- File: `tests/test_explain.py:test_ac9_broken_block` (new)
- Covers: CT-3, CT-4
- Setup: `GOOD` whose build order block gains a line `BROKEN -->`; the fake `npx`.
- Action: `nio check explainer checkout-refunds`.
- Assert: exit 1; `ERROR broken diagram: Build order`; no error names Component map.

### TC-15 No Node: render skipped, the rest still checked (AC-10; integration) [agent]
- File: `tests/test_explain.py:test_ac10_no_node` (new)
- Covers: CT-3, CT-4
- Setup: `GOOD`; no Node on `PATH`.
- Action: `nio check explainer checkout-refunds`; then again with `CT-2` removed from the component map.
- Assert: first: exit 0 and the output holds `render skipped: Node is not installed`; second: exit 1 with `ERROR component map misses CT-2`.

### TC-16 A missing explainer is named (AC-11; integration) [agent]
- File: `tests/test_explain.py:test_ac11_missing` (new)
- Covers: CT-4
- Setup: the approved fixture, no explainer.md.
- Action: `nio check explainer checkout-refunds`.
- Assert: exit 1; `ERROR explainer missing: .nio/specs/checkout-refunds/explainer.md`.

### TC-17 One SVG per block, each shown (AC-12; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac12_svgs` (new)
- Covers: CT-11, CT-5, CT-3
- Setup: the approved fixture with two journeys (as TC-2) on a machine with Node; the real renderer.
- Action: run `@nio:explain checkout-refunds`.
- Assert: the number of `explainer-*.svg` files in the spec folder equals the number of Mermaid sections, at least four; each is named in an `![` line of explainer.md and in its images line.

### TC-18 One broken block flagged, the others rendered (AC-13; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac13_one_broken` (new)
- Covers: CT-5, CT-3
- Setup: the explainer TC-17 leaves, its build order block given an unclosed `[` on a new line; the real renderer.
- Action: `nio explain finish .nio/specs/checkout-refunds/explainer.md`.
- Assert: the build order section holds a line starting `> Broken diagram:`; every other Mermaid section has its `![` line and its SVG exists.

### TC-19 Text only, with the reason, without Node or renderer (AC-14; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac14_text_only` (new)
- Covers: CT-11, CT-5, CT-3
- Setup: the approved fixture; run one with every folder holding `npx` removed from `PATH` (`uv`, `git` and the host CLI stay on it); run two with the fake `npx` and `FAKE_NPX=down`.
- Action: run `@nio:explain checkout-refunds` in each.
- Assert: no `.svg` in the spec folder; run one's explainer holds `> Images not rendered: Node is not installed.`, run two's `> Images not rendered: the renderer could not be fetched.`

### TC-20 Three items offered: a component, a flow, a decision (AC-15; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac15_three_offers` (new)
- Covers: CT-12
- Setup: a repo with no spec; script: ask to explain `git hooks in this repo`, then `stop` at the first offer.
- Action: run `@nio:explain` on that topic.
- Assert: the message after the overview lists three items, labelled component, flow and decision.

### TC-21 A pick appends one section and offers three again (AC-16; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac16_pick_appends` (new)
- Covers: CT-12
- Setup: as TC-20; script: pick the first offered item, then `stop`.
- Action: run `@nio:explain` on that topic.
- Assert: `.nio/research/` holds one explainer file; it gained exactly one `## Drill-down: ` section named after the picked item; the reply after the pick lists three new items.

### TC-22 Stop ends the offers (AC-17; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac17_stop` (new)
- Covers: CT-12
- Setup: as TC-21.
- Action: run it; the script says `stop` after the first pick.
- Assert: the final reply offers no item; the file's last section is the drill-down section.

### TC-23 A topic explainer at its path, and the slug rule (AC-18; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac18_topic_path` (new)
- Covers: CT-11, CT-6
- Setup: a repo with no spec; script: `stop` at the first offer.
- Action: run `@nio:explain` on `git hooks`; call `nio explain topic "../Auth / Tokens!"` and `nio explain topic "//"`.
- Assert: `.nio/research/<today>-git-hooks-explainer.md` exists and every SVG it names sits in `.nio/research/`; the first call prints `new: .nio/research/<today>-auth-tokens-explainer.md`; the second exits 1 with `error: the topic "//" gives an empty file name`.

### TC-24 Topic mode works without a research skill (AC-19; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac19_no_research_skill` (new)
- Covers: CT-11
- Setup: a repo whose skills folder holds only `explain`.
- Action: run `@nio:explain` on `git hooks`, script `stop`.
- Assert: the topic explainer exists.

### TC-25 A topic explainer is checked for rendering only (AC-20; integration) [agent]
- File: `tests/test_explain.py:test_ac20_topic_render_only` (new)
- Covers: CT-4
- Setup: `.nio/research/2026-11-08-hooks-explainer.md` with `## Overview` (a Mermaid flowchart naming no `CT-`) and a one-line walk-through; the fake `npx`.
- Action: `nio check explainer .nio/research/2026-11-08-hooks-explainer.md`.
- Assert: exit 0; no line holds `core diagram` or `CT-`.

### TC-26 The same topic continues its file (AC-34; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac34_same_topic` (new)
- Covers: CT-12, CT-6
- Setup: TC-21's file for `git hooks`, from today; script: pick the first offer, then `stop`.
- Action: run `@nio:explain` on `git hooks`.
- Assert: `.nio/research/` holds one explainer for it; its earlier sections are byte-equal; it has one more `## Drill-down: ` section.

### TC-27 A clashing topic gets the next name (AC-35; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac35_clash` (new)
- Covers: CT-11, CT-6
- Setup: today's `auth-tokens-explainer.md` holding `(topic: Auth tokens)`.
- Action: run `@nio:explain` on `auth/tokens`, script `stop`.
- Assert: `auth-tokens-explainer-2.md` exists holding `(topic: auth/tokens)`; the first file is byte-equal; the reply names `auth-tokens-explainer-2.md`.

### TC-28 A changed plan prints the stale line (AC-21; integration) [agent]
- File: `tests/test_explain.py:test_ac21_stale` (new)
- Covers: CT-7, CT-10
- Setup: the approved fixture with `GOOD`, after `nio explain finish` (no Node); then `plan.md` gains a line.
- Action: `nio status`.
- Assert: exit 0; the output holds `stale: explainer.md (spec, plan or contracts changed)` and, on the next line, `  in .nio/specs/checkout-refunds/: re-run @nio:explain`.

### TC-29 A re-run clears the stale line (AC-22; integration) [agent]
- File: `tests/test_explain.py:test_ac22_rerun_clears` (new)
- Covers: CT-7, CT-5
- Setup: TC-28's state, then the component map's block gains the line `b --> c["CT-2 retry"]` (the redraw).
- Action: `nio explain finish .nio/specs/checkout-refunds/explainer.md`, then `nio status`.
- Assert: no output line holds `stale: explainer.md`; the source line for plan.md holds plan.md's hash now.

### TC-30 A stale or missing explainer blocks nothing (AC-23; integration) [agent]
- File: `tests/test_flow.py:test_ac23_explainer_never_blocks` (new)
- Covers: CT-8, CT-9
- Setup: a flow effort on the fixture at `tasking` with the plan gate approved and committed; three states: no explainer.md; explainer.md present; explainer.md present and stale with the `Read first` line added to quickstart.md.
- Action: `nio flow next checkout-refunds` in each; `nio check plan checkout-refunds --approved` in the third.
- Assert: the outputs are equal once a `suggest:` line is dropped; the third has no `back` line and `state: tasking`; `--approved` exits 0; `jury.GATES`, `flow.SKILL` and `flow.EXIT` hold no `explain`.

### TC-31 Only spec, plan and contracts make it stale (AC-31; integration) [agent]
- File: `tests/test_explain.py:test_ac31_sources` (new)
- Covers: CT-7, CT-5
- Setup: TC-28's setup before the plan edit, four fresh copies.
- Action: copy 1: append a line to quickstart.md, `nio status`, then to tests.md, `nio status`, then to contracts.md, `nio status`; copy 2: append to spec.md; copy 3: delete contracts.md; `nio status` each.
- Assert: copy 1: no stale line after the quickstart and tests edits, the stale line after the contracts edit; copies 2 and 3: the stale line.

### TC-32 Flow next suggests the explainer once the plan is approved (AC-24; integration) [agent]
- File: `tests/test_flow.py:test_ac24_suggests_explain` (new)
- Covers: CT-8
- Setup: a flow effort on the fixture whose plan gate was just approved and committed (`test_flow.approve(root, slug, "plan")`), no explainer.md.
- Action: `nio flow next checkout-refunds`.
- Assert: one line starts `suggest:` and holds `nio:explain` and `checkout-refunds`.

### TC-33 No suggestion while the plan gate is open (AC-25; integration) [agent]
- File: `tests/test_flow.py:test_ac25_no_suggestion_open_gate` (new)
- Covers: CT-8
- Setup: the same effort at `plan_jury`, gate not approved.
- Action: `nio flow next checkout-refunds`.
- Assert: no output line holds `nio:explain`.

### TC-34 Mermaid by default (AC-26; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac26_mermaid_default` (new)
- Covers: CT-13
- Setup: the approved fixture; `.nio/config.json` has no `explain` key.
- Action: run `@nio:explain checkout-refunds`.
- Assert: every diagram section's `fence` is `mermaid`.

### TC-35 A host skill format skips rendering only (AC-27; integration) [agent]
- File: `tests/test_explain.py:test_ac27_host_format` (new)
- Covers: CT-4, CT-1
- Setup: `.nio/config.json` sets `{"explain": {"format": "excalidraw"}}`; explainer.md has `## Component map` and `## Build order`, each holding `![map](map.png)` and a walk-through, the component map's text naming CT-1 and CT-2; the fake `npx`.
- Action: `nio check explainer checkout-refunds`; then with `CT-2` removed from the component map's text.
- Assert: first: exit 0 with `render skipped: diagrams drawn with excalidraw`; second: exit 1 with `ERROR component map misses CT-2`.

### TC-36 A missing host skill falls back to Mermaid (AC-28; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_ac28_fallback` (new)
- Covers: CT-13
- Setup: the approved fixture; `.nio/config.json` sets `{"explain": {"format": "no-such-skill"}}`.
- Action: run `@nio:explain checkout-refunds`.
- Assert: every diagram section's `fence` is `mermaid`; the reply or the explainer names `no-such-skill`.

### TC-43 A dropped drill-down stops finish before anything is deleted (AC-33; integration) [agent]
- File: `tests/test_explain.py:test_ac33_dropped_drill_down` (new)
- Covers: CT-5
- Setup: TC-10's setup, finished once; then the `## Drill-down: one` section is cut from explainer.md and `explainer-flow-uj-2.svg` is written again and added to the images line.
- Action: `nio explain finish .nio/specs/checkout-refunds/explainer.md`.
- Assert: exit 1; the output holds `error: drill-down sections missing: Drill-down: one`; explainer.md, quickstart.md, `explainer-drill-1.svg` and `explainer-flow-uj-2.svg` are byte-unchanged.

### TC-44 Finishing without a redraw keeps the stale line (AC-21; integration) [agent]
- File: `tests/test_explain.py:test_ac21_finish_alone_keeps_stale` (new)
- Covers: CT-5, CT-7
- Setup: TC-28's state (plan.md changed, no diagram touched).
- Action: `nio explain finish .nio/specs/checkout-refunds/explainer.md`, then `nio status`.
- Assert: finish exits 0 and prints `still stale: no diagram changed since the last finish; redraw the diagrams to clear the stale line`; the source lines are byte-unchanged; `nio status` still prints `stale: explainer.md (spec, plan or contracts changed)`.

### TC-45 A missing listed image and a stopped run don't break the next finish (AC-33; integration) [agent]
- File: `tests/test_explain.py:test_ac33_rerun_after_partial` (new)
- Covers: CT-5, CT-3
- Setup: `GOOD` with the images line `(images: explainer-x.svg)` and no `explainer-x.svg` on disk; `explain.TIMEOUT` set to 1 and a fake `npx` that sleeps 5 s (`FAKE_NPX=hang`).
- Action: `nio explain finish …/explainer.md` with the hanging `npx`; then again with the plain fake `npx`.
- Assert: first run exits 0, prints no `deleted:` line and writes `> Images not rendered: the renderer could not be fetched.`; second run exits 0, prints no `deleted:` line, and the explainer links one SVG per Mermaid section, each existing.

### TC-46 Image names never collide (AC-33; integration) [agent]
- File: `tests/test_explain.py:test_ac33_unique_names` (new)
- Covers: CT-5
- Setup: `.nio/research/2026-11-08-x-explainer.md` with sections `## Overview` and `## 2 Overview`, and `.nio/research/2026-11-08-x-explainer-2.md` with `## Overview`, each with a Mermaid block and a walk-through; the fake `npx`.
- Action: `nio explain finish` on the `-2` file, then on the first.
- Assert: three distinct SVG files exist in `.nio/research/`: `2026-11-08-x-explainer-2--overview.svg`, `2026-11-08-x-explainer--overview.svg`, `2026-11-08-x-explainer--2-overview.svg`; the `-2` file's SVG is byte-unchanged after the second finish; and a plan explainer with two sections titled `Calls` and `calls!` gets `explainer--calls.svg` and `explainer--calls-2.svg`.

## Quality tests
### TC-37 Every diagram the skill draws stays within 20 nodes (NFR-1; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_nfr1_node_cap` (new)
- Covers: CT-2, CT-11
- Setup: the approved fixture with two journeys (as TC-2).
- Action: run `@nio:explain checkout-refunds`.
- Assert: `len(explain.nodes(s["block"])) <= 20` for every section with a block.

### TC-38 A Mermaid explainer needs no tool but nio (NFR-2; integration) [agent]
- File: `tests/test_explain.py:test_nfr2_no_tools` (new)
- Covers: CT-4, CT-5
- Setup: `GOOD`; no Node on `PATH`.
- Action: `nio explain finish .nio/specs/checkout-refunds/explainer.md`, then `nio check explainer checkout-refunds`.
- Assert: both exit 0; the explainer holds `> Images not rendered: Node is not installed.`; no `.svg` was written.

## Misuse tests
### TC-39 One huge diagram is refused (UJ-1 misuse; integration) [agent]
- File: `tests/test_explain.py:test_uj1_huge_diagram` (new)
- Covers: CT-2, CT-4
- Setup: `GOOD` whose component map holds 30 nodes `c1` to `c30` in one flowchart.
- Action: `nio check explainer checkout-refunds`.
- Assert: exit 1 with `ERROR too many nodes: Component map (30 > 20)`.

### TC-40 An outgrown explainer is flagged where the developer looks (UJ-1 misuse; integration) [agent]
- File: `tests/test_explain.py:test_uj1_outgrown` (new)
- Covers: CT-7
- Setup: TC-28's state: the plan changed after the explainer was written.
- Action: `nio status`, twice.
- Assert: both outputs hold the stale line; the explainer file is byte-unchanged (it is flagged, never rewritten).

### TC-41 Offers never repeat an item already drilled into (UJ-2 misuse; e2e) [agent]
- File: `tests/test_explain_e2e.py:test_uj2_no_repeat` (new)
- Covers: CT-12
- Setup: a repo with no spec; script: pick the first offered item twice in a row, then `stop`.
- Action: run `@nio:explain` on `git hooks`.
- Assert: the second offer's three items don't include the first pick; the file holds two `## Drill-down: ` sections with different titles.

### TC-42 A topic explainer is never taken for a plan's (UJ-3 misuse; integration) [agent]
- File: `tests/test_explain.py:test_uj3_topic_not_plan` (new)
- Covers: CT-7, CT-8, CT-4
- Setup: the approved fixture at `tasking` with no explainer.md, and `.nio/research/2026-11-08-checkout-refunds-explainer.md` holding `GOOD` plus the line `(source: .nio/specs/checkout-refunds/plan.md@000000000000)`, a hash that never matches.
- Action: `nio flow next checkout-refunds`; `nio check explainer checkout-refunds`; `nio status`.
- Assert: flow next still prints the `suggest:` line; the check exits 1 with `explainer missing`; `nio status` prints no stale line.

### TC-47 Re-finishing a stale explainer marks a drill-down once, and only on a change (UJ-4 misuse; integration) [agent]
- File: `tests/test_explain.py:test_uj4_marker_once` (new)
- Covers: CT-5
- Setup: `GOOD` plus `## Drill-down: one`, finished once; the fake `npx`.
- Action: `nio explain finish …/explainer.md` with no source changed; then append a line to spec.md and run finish twice.
- Assert: after the first run the heading is `## Drill-down: one`; after the last two the file holds exactly one `(written for an earlier plan)`, on that heading.

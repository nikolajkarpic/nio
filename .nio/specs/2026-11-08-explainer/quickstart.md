---
slug: 2026-11-08-explainer
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: explainer

## Prerequisites
- This repo with this spec's plan gate approved, cloned to a scratch folder so the demo changes nothing real: `git clone --local . ../nio-demo && cd ../nio-demo && uv sync`. Every command below runs there; `nio` means `uv run nio`.
- Node with `npx` for the images: `npx --version` prints a version. Without it the scenarios still pass, text only.

## Scenarios

### QS-1 Explain an approved plan (UJ-1; manual) [agent]
- Needs: an agent host with the NIO skills installed; a person starts the skill.

1. `nio flow next 2026-11-08-explainer`
   Expected:
   ```
   contains: suggest:
   contains: nio:explain
   ```
2. Run `/nio:explain 2026-11-08-explainer`, then `nio check explainer 2026-11-08-explainer`
   Expected:
   ```
   contains: 0 errors
   ```
3. `head -6 .nio/specs/2026-11-08-explainer/quickstart.md`
   Expected:
   ```
   contains: Read first: [explainer.md](explainer.md)
   ```
4. `nio flow next 2026-11-08-explainer`
   Expected:
   ```
   contains: state: tasking
   ```
- Pass when: every step matched; step 4 holds no `suggest:` line; the component map names every contract, CT-1 to CT-13, and the build order diagram names Foundation and US-1 to US-8 in plan.md's order (SC-1).

### QS-2 Drill down (UJ-2; manual) [agent]
- Needs: QS-1 finished; a person picks.

1. Ask the agent to drill into the explainer of `2026-11-08-explainer`; pick the offered flow, then say stop.
   Expected:
   ```
   contains: Drill-down:
   ```
2. `grep -c "^## Drill-down: " .nio/specs/2026-11-08-explainer/explainer.md`
   Expected:
   ```
   1
   ```
- Pass when: the first offer listed one component, one flow and one decision; the second offer listed three other items; after stop nothing more was offered.

### QS-3 Explain a topic (UJ-3; manual) [agent]
- Needs: a person asks and picks.

1. Ask `/nio:explain` to explain `git hooks`; pick one item, then say stop. Then `ls .nio/research/ | grep git-hooks-explainer`
   Expected:
   ```
   contains: -git-hooks-explainer.md
   ```
2. `nio explain topic "git hooks"`
   Expected:
   ```
   contains: continue: .nio/research/
   ```
3. `nio check explainer .nio/research/$(ls .nio/research/ | grep git-hooks-explainer.md | head -1)`
   Expected:
   ```
   contains: 0 errors
   ```
- Pass when: every step matched; the check output names no core diagram and no contract.

### QS-4 Notice a stale explainer (UJ-4; manual) [agent]
- Needs: QS-1 finished; a person starts the skill in step 3.

1. `echo "" >> .nio/specs/2026-11-08-explainer/plan.md && nio status`
   Expected:
   ```
   contains: stale: explainer.md (spec, plan or contracts changed)
   contains:   in .nio/specs/2026-11-08-explainer/: re-run @nio:explain
   ```
2. `nio explain finish .nio/specs/2026-11-08-explainer/explainer.md && nio status`
   Expected:
   ```
   contains: still stale: no diagram changed since the last finish; redraw the diagrams to clear the stale line
   contains: stale: explainer.md (spec, plan or contracts changed)
   ```
3. Run `/nio:explain 2026-11-08-explainer`, then `nio status | grep -c "stale: explainer.md"`
   Expected:
   ```
   0
   ```
- Pass when: every step matched; step 3's run redrew at least one diagram.

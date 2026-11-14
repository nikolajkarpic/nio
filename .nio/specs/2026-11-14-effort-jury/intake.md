# Intake: effort-jury

## The human's words (2026-11-14)

> can we do these 3 with specs and then pass them off to agent to implement the spec?

Answer to the follow-up question (which three): "Speed-up: 1 spec + re-measure" — one spec that replaces the per-epic implementation juries with one jury on the whole effort diff before the PR (#77 lever 10 + #100); an agent implements it; the re-measure is done separately by running an effort.

## Source: https://github.com/nikolajkarpic/nio/issues/77 (lever 10, from .nio/research/2026-11-06-speedup.md)

| # | Lever | Evidence (numbers) | Est. min saved / effort | Risk to quality | Effort | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | One implementation jury per effort instead of per epic | Per epic gate today: evidence 10–14 min (×2) + jury about 2 min + orchestrator. After 2+3, about 5–7 min per epic | 50–70 today; 20–28 after 2+3 | Medium–high: E-2 alone had 13 confirmed majors; bigger diffs give jurors limited context (conformance was already "limited" on E-1), and findings land after later epics have built on the code | M | **defer**: re-measure after 2, 3, 7 |

Measured 2026-11-08 (three efforts): per-epic implementation gates ran 2, 2, 3, 2, 7, 3, 2, 2 rounds; between-task time (gates, fix loops, orchestration) was 55–69% of implementing time.

## Source: https://github.com/nikolajkarpic/nio/issues/100

### PR gate: an independent jury on the whole effort diff before merge

## Problem
Every effort is juried per epic, by the same orchestrator that built it, and under delegation it approves its own gates. Nobody judges the whole change: cross-epic fit, duplicated helpers, dead code, or commits made outside the flow (merge resolutions, hand fixes). The five speed-up PRs (#81 #87 #89 #93 #99) merged with no review of the full diff; one real bug (wave patch in the wrong run folder) was found only by chance while stacking.

## Proposal
- A final `pr` gate after the last implementation gate: the existing implementation lenses (correctness, conformance, adversary, consistency) plus the refuter, on the full `main...HEAD` diff, so out-of-flow commits are covered.
- One new lens, **integration**: cross-epic fit, duplication, dead code, needless complexity across the diff.
- Driven by a fresh agent that did not build the effort; its outcome goes to the human. It is the one gate delegation can't approve.
- Later, re-measure: with a `pr` gate, per-epic juries may get lighter (conformance only).

Data to shape the lens: the independent review of the merged speed-up PRs (findings to be linked here).

Refs: #77, .nio/research/2026-11-06-speedup.md

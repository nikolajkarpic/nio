write a spec for it first

## Source: https://github.com/nikolajkarpic/nio/issues/52

# Jury convergence: re-review rounds that keep finding new issues

Found by dogfooding the spec jury on the grill spec (2026-10-25). Each re-review round's logic lens found new problems, about half of them interactions created by the previous round's fixes:

| Round | Logic findings | Caused by the last fixes |
|---|---|---|
| 1 | 3 | — |
| 2 | 5 | 3 |
| 3 | 5 | 3 |

That's about 16 juror and refuter runs in total. On a large behavioural spec (about 30 FRs), the jury doesn't converge on its own, and the 2-failed-rounds rule doesn't help, because each round's findings are new rather than repeated.

The human closed this one by accepting the edge cases as risk (#51), with `nio jury check --human "<reason>"`, which records outcome `human`.

**To decide:**
- A convergence rule: after round 2, new findings from a re-review go straight to the human (fix or accept as risk) instead of starting another round? Or only blockers start a new round?
- Should a re-review judge only the changed items and their neighbours, not the whole spec?
- Size: should specs this large be split before the jury (the scope lens's J-10 said so; FR-15 suggests an epic at the first pause)?

Refs #27, #47, #51.

### Comment

Second case: the `grill-checks` spec jury (grilling/R-2), 2026-10-25/26.

- Round 1: 14 findings (5 major). Round 2: 13 (7 major). Round 3: 13 (5 major, 3 after merges). Round 4: 13 (3 major, 2 after the refuter).
- Every earlier fix held each round (fixed J-1..J-39). The new findings were almost all wording and ACs over code that never changed after round 1.
- Most majors came from the previous round's fixes: rewording FR-16 (round 2) and SC-1 (rounds 3 and 4) each spawned the next round's majors.
- Ended like the grill spec: the human chose to fix round 4's findings and close the gate (`--human`) rather than run round 5.

Pattern worth designing for: a fix that rewords a requirement is itself new text, so the next round judges it fresh. Options include re-reviewing only the reworded lines against the finding that motivated them, or stopping once a round raises no finding that a lens would rate above minor against the *code*.

### Comment

**Decided (brainstorm, 2026-10-26)**

1. **Stop rule: only blockers start another round.** After round 1, only a blocker the refuter confirms starts a new round. New majors and minors go to the human in one list, and each is fixed or accepted as risk. Cost: a fix to a major isn't re-reviewed. On both dogfood runs (the grill spec and grill-checks), this would have stopped after round 2.
2. **Re-review is a fix check with neighbours.** A re-review lens gets each finding with the before and after text of the items it changed, plus the items that cite them or that they cite. For each finding it answers fixed or not fixed, and it may raise only blockers. It doesn't re-review the whole spec. Cost: a clash with a distant, unrelated item can slip through to the plan or code.
3. **Size: no new rule.** The scope lens already suggests a split above 8 FRs. That suggestion reaches the human as an ordinary finding.

Touches: `skills/jury/SKILL.md` steps 6 and 8, `nio jury check` (outcome after round 1 when there are no confirmed blockers), `nio jury changed` (neighbour IDs), the re-review pack and lens format (fixed / not-fixed verdicts), and `tests/test_jury.py`.


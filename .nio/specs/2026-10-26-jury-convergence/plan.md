# Plan: jury-convergence

Derived from the approved spec (`spec.md`, gate closed by the human, V-261026-lkas), research.md (RF-1–RF-9) and
the code as of `de125ba`. NIO's plan stage isn't built yet (#41, #48), so this is a single document with no
template, plan gate or plan jury. One decision was new here and the human settled it: **P1** below.

## Decisions taken while planning

- **P1** A new command, `nio jury fixcheck`, prints each re-review lens's exact pack. Collect validates verdicts
  against the same list, so the pack and the check can't disagree (the human, 2026-10-26; the hand-built final
  check in this spec's own jury missed the outcome table, J-14).
- **P2** (agent) The phase is derived from what the ledger already holds (`recorded`) plus one new field, `list`,
  written when the jury hands the human the one list. No other ledger field. Old ledgers have neither, so they load
  as first review or re-review by `recorded` alone (FR-17).
- **P3** (agent) A new major or minor in a re-review gets status `noted`: a closed status, like `refuted`, so it never
  needs a disposition and never counts toward the outcome (FR-12).

## Contracts

### Ledger (`.nio/specs/<slug>/jury/spec.json`)
- `recorded`: unchanged, `[[round, outcome], …]`. The first `[r, "rejected"]` ends the first review (FR-19).
- `list` (new, optional): `{"round": r, "ids": [...], "final": null | r2, "flagged": [...]}`.
  - Written by `check --record` when it records `human` for the one list (FR-2).
  - `final` is set by the first collect after the list was recorded, and that round starts the final fix check (FR-24).
  - `flagged` holds what the final check sent to the human (FR-21).
- Finding `status` gains `noted` (P3). `rounds` rises at most once per round (FR-11).

### Phase (`jury.phase(led)`, new)
| condition | phase |
| --- | --- |
| no `rejected` in `recorded` | first |
| `list.final` set and `round >= list.final` | final |
| `list` set, a listed finding fixed, `list.final` unset | final-owed |
| otherwise | re-review |

### Lens output: `## Verdicts` (new section, re-review and final only)
```
## Verdicts
- J-2: fixed — FR-7 now names the neighbours
- J-5: not fixed — AC-9 still asserts presence only
```
- Rules (FR-8, FR-9): exactly one line per finding in the lens's fixcheck pack. A missing, doubled or unknown ID
  makes the whole output invalid.
- Escalation jurors (`spec-<lens>-2.md`, `-3.md`) give no verdicts and judge only the blocker they were given (FR-13).
- `## Findings` stays. In a re-review, a new blocker is a finding as today; a new major or minor becomes `noted`.

### `nio jury changed <slug> spec` (extended)
- It compares whole item blocks, continuation lines included (an AC's Observable line). Today it compares the first
  line only, so AC-4's and AC-9's Observable fixes went unseen in this spec's own jury.
- It also reports changed unnumbered text per section (table rows, the Summary, a note above a table).
- It prints `neighbours:`, the items that cite a changed item and the items a changed item cites, one step (FR-14).

### `nio jury fixcheck <slug> spec --lens <lens> [--blocker J-n]` (new, P1)
It prints the pack, and nothing else of the spec (FR-7):
- the instructions;
- the lens's findings disposed as spec-fix since the version it last judged;
- the findings the human accepted as risk or ruled out of scope, named, with no verdict asked (FR-15);
- each changed item before and after, and changed tables and unnumbered text by section;
- the neighbours' current text;
- the verdict format.

With `--blocker`, it prints the escalation pack instead: the same material plus that blocker, and no verdicts asked.

### `nio jury check` outcomes (compose, in order)
1. `rerun` when nothing has been collected, or a lens must retry (unchanged).
2. Phase `final-owed`: `rerun`, naming the fixes the final check must cover (FR-22).
3. The artefact changed since the judged version: `approved` in two cases, each naming the fixes no lens judged:
   the list was settled with no fix (AC-24), or what the final check flagged is settled (FR-23). Otherwise `rerun`.
4. `pending`, then majority and split handling (unchanged).
5. Phase first or re-review: a finding that failed two rounds gives `human` (FR-16; never in the final phase).
6. A confirmed open blocker: `rejected` in first or re-review (FR-1), `human` with `flagged` in final (FR-21).
7. Open findings: `rejected` in first (FR-6); in re-review `human` with the one list (FR-2), recorded into `list`;
   in final `human` with `flagged` (FR-21).
8. `approved`, with reasons naming each fix no lens judged (FR-5).
9. Notes are printed under `notes:`; they never change the outcome (FR-12).

## Bindings: requirement → code

| Spec item | Where |
| --- | --- |
| FR-1, FR-2, FR-5, FR-6, FR-16, FR-21, FR-22, FR-23 | `jury.compose`, `jury.check` (records `list`) |
| FR-19, FR-24 | `jury.phase` (new); `jury.collect` sets `list.final` |
| FR-8, FR-9, FR-10, FR-11, FR-25 | `jury.parse_lens` (verdicts), `jury.merge` (apply verdicts; no silence rule outside the first review) |
| FR-12 | `jury.add` (new sub-blocker finding in re-review → `noted`), `CLOSED` |
| FR-13 | `jury.fixcheck --blocker`; `merge` skips verdict checks for `-2`/`-3` jurors |
| FR-11 (refuter on not-fixed blocker) | `merge` sets `validation: pending`, so the existing refuter batch picks it up |
| FR-7, FR-14, FR-15 | `jury.changed` (blocks, sections, neighbours), `jury.fixcheck` (new), `cli.py` |
| FR-17 | `jury.load` defaults; `phase` copes with no `list` |
| FR-3, FR-4 | `skills/jury/SKILL.md` step 6 (one message, fix or accept as risk via `nio jury dispose`); `phase` → final-owed |
| FR-18 | `skills/jury/SKILL.md` steps 6 and 8 |
| FR-20 | `src/nio/agents/{adversary,consistency,logic,scope,security,testability}.md` (`## Re-review`), `templates/lens-output.md` (`## Verdicts`) |

## Tests: acceptance criterion → test (`tests/test_jury.py`)

| Test | ACs |
| --- | --- |
| `test_stop_rule` | AC-1, AC-2, AC-3, AC-4, AC-6, AC-7 |
| `test_final_check` | AC-5, AC-21, AC-24, AC-25, AC-26, AC-27 |
| `test_fix_verdicts` | AC-10, AC-11, AC-12, AC-13, AC-20, AC-22, AC-23 |
| `test_changed_and_fixcheck` | AC-8, AC-9, AC-14 |
| `test_phases` | AC-18 (plain-talk ledger shape) |
| `test_old_ledgers` | AC-15, AC-28 (copies of the grill and grill-checks ledgers in `tests/fixtures/jury/`) |
| `test_skill_and_cards` | AC-16, AC-17, AC-19 (phrase checks) |

AC-28 replays each ledger as of round 2. Each open round-2 major or minor is fed back as a not-fixed verdict, and
the test asserts `human`, not `rejected`. The existing tests stay green, and SC-3 is the whole file passing.

## Order of work
1. `phase` and the `list` field, with `test_phases` and `test_old_ledgers` (AC-15).
2. `changed`: whole blocks, sections and neighbours, then `fixcheck` and its CLI.
3. Verdicts: the template, `parse_lens`, `merge` (FR-25 silence rule), `noted` in `add`.
4. `compose` and `check`: the stop rule, the final check and the notes. Then the remaining tests.
5. The skill's steps 6 and 8, and the six lens cards. Then `nio agents sync`.
6. Run every self-check in CLAUDE.md, and dogfood one re-review on a spec.

## Not in this plan
- The bulleted-situation bug in `collect` (a finding's situation written as a list is dropped). It's a separate
  issue, not filed yet.
- The plan and tasks gates (spec non-goal).

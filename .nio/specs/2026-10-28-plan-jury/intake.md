# Intake: 2026-10-28-plan-jury

## The human's words (2026-10-28)

> okey i see we need plan jury first, do we have a task for that? and should we have plan jury or should we have jury that checks everything at the end from sepc to plan to tasks?

> okey open a n issue for plan jury, and then do a deep research on how to do it, check how speckit repo does it if it does, check how matt peacock does it if he does

> write the spec for #57

## Source: https://github.com/nikolajkarpic/nio/issues/57

### Plan jury: build the plan gate (test-proof and architecture-fit cards, CORE["plan"], nio check plan as its precondition)

### What needs designing

The plan stage shipped (054483c), but its gate can't run. `@nio:plan` ends with "the next stage is the plan jury", and the tasks stage needs an approved plan before it starts (see the #42 follow-up). Today:

- `jury.CORE` only has `spec` (`src/nio/jury.py:24`), so `nio jury plan <slug> plan` fails with "only the spec gate is built so far" (`src/nio/jury.py:160`).
- `nio jury plan` runs `nio check spec --gate` as its precondition (`src/nio/jury.py:162`). The plan gate needs `nio check plan <slug> --gate` instead.
- The plan gate's core lenses, decided in #47, have no cards: **test-proof** (would each test in `tests.md` fail if its AC broke?) and **architecture fit** (fits the existing code and `architecture.md`, contracts complete and consistent, principles #26, simplicity and Complexity tracking).
- Its triggered lenses aren't wired: **logic** when contracts carry state (the card's `## At plan` section exists), **risk and rollback** (migration, schema change, data deletion, deploy config; no card), **security** (`## At plan`).
- The jurors' packs: which files each lens reads (#48 decision 4, `files:` isn't in `agents.FIELDS`).

### What the design must define

- What triggers each plan-gate lens, computed by the CLI as at the spec gate.
- What each new card asks, and what stays a free CLI check in `nio check plan` (#50).
- How a plan finding is fixed: a plan fix, or a spec-fix that sends the spec back through its jury.
- What approval looks like (`nio: approve plan`), and that the tasks stage reads it.

Refs: #28 (umbrella), #41, #47, #48, #50, #42


### Comment (2026-10-28T10:38:27Z)

## Research (2026-10-28)

**Short version:** no tool has an automatic reviewer for the plan, and nobody checks whether a planned (not yet written) test would actually catch a broken requirement. Our design already has the right order: free CLI checks first, then fresh-context lenses, at most 5 findings each, a refuter, and the human after 2 failed rounds. That matches the best tools found. The research fills in what the two new lens cards should ask.

### What each tool does
| Tool | Plan review before tasks | Who runs it | Can it stop the plan? |
|---|---|---|---|
| spec-kit (main @ `222a973`) | Its "Constitution Check" gates are instructions only. `/analyze` runs only **after** tasks exist, reads only `plan.md` (never contracts, data model or quickstart) and finds coverage by keyword | The same agent, in the same session | No. The optional workflow has a human approve/reject step. Real plan review exists only in community extensions (`critique`, `agentstandards`, `plan-review-gate`, `adrkit`) |
| Matt Pocock ([mattpocock/skills](https://github.com/mattpocock/skills)) | `to-tickets` quizzes the human: "Does the granularity feel right?", "Are the blocking edges correct". Separate agents review only the code, after it's written (`code-review`) | The human, through the same agent | Yes, the human: "Nothing reaches the tracker until you approve" |
| BMAD ([reviewer-gate.md](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/skills/bmad-architecture/references/reviewer-gate.md)) | A linter first, then parallel reviewers that each start fresh: always-on "floor" lenses plus optional ones | Separate subagents. "An inline self-check does not count" | Findings are sorted into autofix, discuss, defer or ignore |
| GSD ([gsd-plan-checker](https://github.com/gsd-build/get-shit-done)) | 12 dimensions, worked backward from the goal. Each dimension says why when it's skipped | A separate agent that only reads | BLOCKER or WARNING. At most 3 rounds, and it goes to the human early if the issue count doesn't fall |
| cc-sdd | The author checks its own design before writing it, then an optional `validate-design` (GO/NO-GO, max 3 concerns) | The same agent, then an optional separate one | Yes |
| Kiro, Tessl, OpenSpec | A human checklist only. Tessl's `[@test]` links only check that the file exists | Human | The human. OpenSpec says people skip it |

Known weaknesses: spec-kit#4164 (a clean `/analyze` result proves nothing, because "it only reports what the model loaded"). spec-kit PRs #2511 and #3188 (/analyze run in a separate subagent was reverted, because its 300–500-line report fed back into the main conversation and froze long sessions).

### What to take

1. **The test-proof lens.** New ground. Adapted from BMAD's `review-prompts/verification-gap.md` and Pocock's `to-tickets` docs, for each `TC-n` the lens:
   - names the smallest realistic bug that breaks the AC (a flipped condition, a dropped default, a missing field) and the line in `Assert:` that would fail because of it;
   - lists asserts that don't count: "it succeeded", "it didn't throw", snapshot-only, checking that a mock or log was called, tests that mock away the integration under test, and tautologies like `expect(x ?? D).toBe(D)`;
   - flags expected values that don't come from an independent source (Pocock `tdd`);
   - flags an AC that's already true on today's code, or that only another story's work can satisfy (Pocock `to-tickets`);
   - must search the repo before saying a test is missing.

   Mutation-first prior art: Meta ACH, https://arxiv.org/abs/2501.12862.
2. **The architecture-fit lens.**
   - **The nearest existing code.** For each `new` contract, name the closest existing file it copies (GSD `gsd-pattern-mapper` and `PATTERNS.md`). A cheap version: a `Like: file:symbol` line on new contracts in `contracts.md`. `nio check plan` then confirms that file exists for free, and the lens judges whether the contract really follows it.
   - **Project rules, one by one.** Check the plan against each rule in CLAUDE.md, and against project principles once #26 exists (GSD Dimension 10).
   - **Agree with the existing code.** BMAD's rule is that the design "ratifies rather than contradicts a brownfield codebase". cc-sdd adds "No orphan components" and "Existing Architecture Alignment (Critical)".
3. **How a plan finding gets fixed.** The jury's fix types only know `spec-fix` (`src/nio/jury.py:17`). The plan gate needs a plan fix, plus cc-sdd's rule: a gap that comes from the spec goes back to the spec stage instead of being filled in with invented detail in the plan.
4. **The demo question:** "what can I demo when this is done?" (Pocock). A free check: every `US-n` entry in the build order lists a `Scenario:`. Today that line is optional.
5. **Already in our design, and confirmed by this research:** each lens starts in a fresh context; a linter runs before the lenses; always-on lenses plus triggered ones; a cap on rounds plus going to the human when fixes stall; a refuter; declined findings aren't raised again (BMAD: "Do not re-raise suggestions declined in a `Decision:` line"); jurors return a short verdict, not a long report.

### Traps the research confirmed
- **Reviewing only `plan.md`** (spec-kit). Our plan gate reads all four files.
- **The same agent reviewing its own work, called a gate** (spec-kit's gates, cc-sdd's self-check).
- **Finding coverage by keyword** (spec-kit#4164). `nio check plan` uses IDs instead.
- **Reviewers that drift into warnings only.** GSD names this explicitly.
- **Capping the review at 3 concerns** (cc-sdd). It can hide blockers.
- **Counting verify commands instead of asking whether they'd fail.** GSD's "Nyquist" check does this.
- **Looping review until it comes back clean.** Pocock: "There is no convergence guarantee".

### Open decisions
1. Add a `Like: file:symbol` line on new contracts (checked for free), or leave the nearest-existing-code check to the lens?
2. What the plan-fix type is called, and how a finding that comes from the spec goes back to the spec jury.
3. Should test-proof check "the AC is already true on today's code", or leave that to the implementation jury's red-first evidence (#29)?
4. Require `Scenario:` on every story entry in the build order?

Refs: src/nio/jury.py:17 · src/nio/jury.py:24 · src/nio/jury.py:160 · src/nio/plan.py · #28 · #41 · #47 · #48 · #50 · #52


### Comment (2026-10-28T10:48:29Z)

## Decided (2026-10-28)

1. **New contracts name the existing code they copy, and the lens judges the fit.** Each `new` contract in `contracts.md` gets a `Like: file:symbol` line naming the existing code it follows. `nio check plan` confirms that code exists, for free. The architecture-fit lens judges whether the contract really follows it.
2. **A plan finding is fixed in the plan, unless its cause is in the spec.** A new disposition, `plan-fix`, means the finding is fixed in the plan files. A finding rooted in the approved spec becomes a change request: the spec is edited, the spec jury re-checks only the changed items, and then the plan jury resumes. The plan never fills a spec gap with detail of its own (cc-sdd's rule).
3. **Test-proof flags a requirement that's already true on today's code.** The lens reads the code each contract binds and flags a test that would pass before any work is done. It judges by reading; it doesn't run anything. The red test the worker writes first, and the implementation jury's check of it (#29), still apply later.
4. **The demo question is asked by a lens, with no hard rule.** The architecture-fit lens asks "what can be shown when this story is done?" and flags a story with no answer. `nio check plan` doesn't require a `Scenario:` on every story entry, because scenarios are written one per journey and a spec can have fewer journeys than stories.

All four open decisions are settled.



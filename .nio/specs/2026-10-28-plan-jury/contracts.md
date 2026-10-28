---
slug: 2026-10-28-plan-jury
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: the plan gate's jury

## Contracts

### CT-1 Plan-gate core lenses (FR-1, FR-3) [research: RF-11]
- Binding: `src/nio/jury.py:CORE` (existing)
- Kind: config
- Shape: `CORE = {"spec": ["testability", "logic"], "plan": ["test-proof", "architecture-fit"]}`
- Rules: "the spec gate's testability lens does not run at the plan gate" (FR-3)

### CT-2 Plan the plan gate (FR-1, FR-2, FR-4, FR-5, FR-6, FR-8, FR-9, NFR-1) [research: RF-11]
- Binding: `src/nio/jury.py:plan` (existing)
- Kind: cli
- Shape: `nio jury plan <slug> plan [--add "<lens>:<reason>"]` → lines `tier: …`, `lenses: <lens> (<reason>), …`, `runs: n of cap`
- Accepts: a slug whose spec is full route; `plan` as the gate
- Returns: exit 0 and the lens line: `test-proof (core)`, `architecture-fit (core)`, then `logic (state: CT-n)` when a contract has a `State:` line, `security (risk: auth|pii)`, `risk-rollback (risk: migration|data-deletion)` or `risk-rollback (data model)`
- Fails: `nio check plan <slug> --gate` has errors → exit 1, "`nio check plan <slug> --gate` fails (`<n>` errors): finish the plan first", no lens line; a lens with no card → exit 1, "missing cards: `<lens>` — the gate is blocked until they exist"
- Rules: "with zero model calls" (NFR-1); the spec check is not run for the plan gate (FR-2)

### CT-3 The plan gate's versioned artefact (FR-11, FR-47) [default]
- Binding: `src/nio/jury.py:GATES` (existing)
- Kind: config
- Shape: `GATES["plan"] = ["plan.md", "contracts.md", "tests.md", "quickstart.md", "spec.md", "architecture.md"]`
- Rules: the spec and `architecture.md` are part of the text a plan round judges, so a re-approved spec change makes `nio jury check <slug> plan` say `rerun` and withdraws the plan's approval (FR-47); the ledger stays `jury/plan.json` and `.md`, built from the gate name

### CT-4 Plan-gate juror files and grounding sources (FR-10, FR-42, FR-43) [default]
- Binding: `src/nio/jury.py:sources` (new)
- Like: `src/nio/jury.py:human_words`
- Kind: function
- Shape: `sources(root, slug, gate) -> list[Path]`; CLI `nio jury files <slug> <gate>` prints one repo-relative path per line
- Accepts: a slug and a gate; for `plan`, reads `contracts.md` for `Binding:` and `Like:` files
- Returns: for `plan`: the four plan files, `spec.md`, `CLAUDE.md` when it exists, `architecture.md` when it exists, every file a contract binds that exists, and every file a `Like:` line names; for other gates, the gate's own files
- Rules: "give every juror the same files FR-42 accepts quotes from" (FR-43); `grounded` checks quotes against these files' text plus the human's words

### CT-5 Collect a plan-gate round (FR-12, FR-42, FR-50) [default]
- Binding: `src/nio/jury.py:collect` (existing)
- Kind: cli
- Shape: `nio jury collect <slug> plan --run <run> --tier <tier> --expect <lens>…`
- Accepts: lens outputs `.nio/runs/<run>/jury/plan-<lens>.md`
- Returns: the merged findings and, for blockers and majors, the refuter batch, as at the spec gate
- Fails: the plan gate is with the human (CT-7) → exit 1, "the plan gate waits on the human's ruling"; it waits on a spec change → exit 1, "the plan jury is paused until the spec change is settled"
- Rules: "after the first review only a blocker the refuter confirms starts another round while the rest go to the human as one list" (FR-12); quotes are grounded against `sources()` (CT-4)

### CT-6 Dispose of a plan-gate finding (FR-32, FR-33, FR-34, FR-41, FR-48, FR-49) [default]
- Binding: `src/nio/jury.py:dispose` (existing)
- Kind: cli
- Shape: `nio jury dispose <slug> <gate> J-n <plan-fix|spec-change|…> --by <agent|grill|human> --note "<text>" [--change C-…]`
- Accepts: `plan-fix` and `spec-change` at the plan gate only; `spec-change` needs `--change` naming a change record whose `against` is the spec
- Returns: the finding as `disposed` with that disposition (and the change ID in its note)
- Fails: `plan-fix` or `spec-change` at another gate → exit 1, "`plan-fix` belongs to the plan gate"; `spec-change` without an existing change record → exit 1, naming the missing record
- Rules: "the jury skill settles a plan-fix that changes no behaviour itself, and hands the human the rest" (FR-32); a further spec-rooted finding joins the same open change request (FR-48)

### CT-7 The plan gate's state (FR-35, FR-39, FR-47, FR-49, FR-50) [default]
- Binding: `src/nio/jury.py:state` (new)
- Like: `src/nio/jury.py:phase`
- Kind: function
- Shape: `state(root, slug) -> ("open" | "waiting-on-spec" | "with-human" | "approved" | "closed-by-human", reason)`
- Accepts: the plan ledger, the change records its `spec-change` findings name, and the spec ledger
- Returns: `waiting-on-spec` while a named change record is `pending`, or is `accepted` and the spec gate hasn't approved or been closed on the current spec; `open` again once that holds, or once the record is `rejected`, with its findings reopened for the human; `with-human` while the ledger's one list or final-check flags are unsettled; `approved` and `closed-by-human` from the outcome and the closure on the current artefact
- State: follows the spec's state table "plan gate"
- Shape (CLI): `nio jury check <slug> plan` prints `state: <state>` with its reason, e.g. `state: waiting-on-spec (the plan jury is paused until C-1 is settled)`
- Rules: "the one way out of either is \"spec re-approved\" (FR-47), which reopens it on what changed"

### CT-8 Compose the plan gate's outcome (FR-12, FR-32) [research: RF-14]
- Binding: `src/nio/jury.py:compose` (existing)
- Kind: function
- Shape: `compose(led, current) -> (outcome, reasons, listed)`
- Rules: a `plan-fix` without a change to the plan is refused like a `spec-fix` without one; the stop rule is the spec gate's (D-261026-r52z), shared through `phase`

### CT-9 `Like:` check in `nio check plan` (FR-28, FR-29, FR-30, FR-31, NFR-1) [default]
- Binding: `src/nio/plan.py:check` (existing)
- Kind: cli
- Shape: `nio check plan <slug> [--gate]`
- Accepts: `- Like: <file>:<symbol>` or `- Like: none: <reason>` on each contract whose binding is `(new)`
- Returns: no error for a `(new)` contract whose `Like:` names an existing file holding the symbol, or `none` with a reason; none for an `(existing)` contract without one
- Fails: no `Like:` on a `(new)` contract → "CT-n: a new contract needs `- Like: <file>:<symbol>` or `- Like: none: <reason>`"; a missing file or symbol → "CT-n: `Like:` names `<file>`, which doesn't exist" / "… `<symbol>`, which isn't in `<file>`"; `none` with no reason → "CT-n: `Like: none` needs a reason"
- Rules: no `Scenario:` line is required on a build-order story entry (FR-31)

### CT-10 Contracts template carries `Like:` (FR-28) [derived: FR-28]
- Binding: `src/nio/templates/contracts.md` (existing)
- Kind: file
- Shape: a `- Like: <file>:<symbol>` line under `- Binding:`, with a comment that it is required for `(new)` and may be `none: <reason>`

### CT-11 Test-proof lens card (FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-40) [derived: FR-14, FR-40]
- Binding: `src/nio/agents/test-proof.md` (new)
- Like: `src/nio/agents/logic.md`
- Kind: file
- Shape: card with `tier: max`, `effort: med`, `tools: [read]`, sections Job, Inputs, `## At plan`, Output format, Stop when, Re-review
- Rules: per `TC-n`, "the smallest realistic bug that breaks its AC" and "the line in its `Assert:` that would fail because of it" (FR-15); flags the asserts FR-16 lists, an expected value with no independent source, an AC already true on today's code "judged by reading the code each contract binds, without running anything" (FR-18), an AC only another story can satisfy, and "search the repo before saying a test is missing" (FR-20)

### CT-12 Architecture-fit lens card (FR-21, FR-22, FR-23, FR-24, FR-25, FR-26, FR-27, FR-40, FR-46) [derived: FR-21, FR-40]
- Binding: `src/nio/agents/architecture-fit.md` (new)
- Like: `src/nio/agents/logic.md`
- Kind: file
- Shape: card with `tier: max`, `effort: med`, `tools: [read]`, sections Job, Inputs, `## At plan`, Output format, Stop when, Re-review
- Rules: judges each `Like:` line and each `Like: none` reason, each CLAUDE.md rule one by one, contradictions with the code or `architecture.md`, components nothing calls, anything `## Complexity tracking` doesn't justify, "what can be shown when it is done" per story, and contracts inconsistent with each other

### CT-13 Risk-rollback lens card (FR-40, FR-44) [derived: FR-44, FR-40]
- Binding: `src/nio/agents/risk-rollback.md` (new)
- Like: `src/nio/agents/logic.md`
- Kind: file
- Shape: card with `tier: max`, `effort: med`, `tools: [read]`, an `## At plan` section asking "how each migration or deletion the plan makes is rolled back or recovered"

### CT-14 Security card's plan-gate questions (FR-45) [derived: FR-45]
- Binding: `src/nio/agents/security.md` (existing)
- Kind: file
- Shape: a new `## At plan` section after `## At spec`, asking per contract "who may call it and what data it exposes or keeps"

### CT-15 The jury skill runs the plan gate (FR-13, FR-34, FR-36, FR-37) [default]
- Binding: `skills/jury/SKILL.md` (existing)
- Kind: file
- Shape: the steps take `<gate>` (`spec` or `plan`); for the plan gate, packs come from `nio jury files <slug> plan`, a finding the skill judges spec-rooted is proposed to the human with a draft change request and disposed `spec-change` only after they confirm, never fixed in the plan; an approved plan is recorded by one `nio: approve plan` commit holding the four plan files and the plan verdict when the human asks
- Rules: "never fill a gap in the approved spec with detail of the plan's own" (FR-36)

### CT-16 May the tasks stage start (FR-38, FR-39, FR-47, FR-50) [default]
- Binding: `src/nio/plan.py:approved` (new)
- Like: `src/nio/plan.py:full_spec`
- Kind: cli
- Shape: `approved(root, slug) -> (bool, reason)`; CLI `nio check plan <slug> --approved`
- Returns: exit 0 for a bug-fix spec ("a bug-fix spec has no plan stage"), and for a full spec whose plan gate state (CT-7) is `approved` or `closed-by-human`
- Fails: a full spec with no `plan.md`, or a plan gate in any other state → exit 1, "the plan must be approved first (`<state>`)"
- Rules: the tasks stage (#42) calls this before it drafts; "a bug-fix spec, which has no plan stage, is not refused for lacking one" (FR-38)

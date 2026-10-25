lets do the jury skill, deepdive first

## Source: https://github.com/nikolajkarpic/nio/issues/27

### What needs designing

The **jury verdict format**: what a juror lens returns, how lens outputs become one gate outcome, how findings are tracked to resolution, and what goes into memory. It applies at every gate (spec, plan, tasks; #28, #47). The lens catalog, triggers, budget and re-run policy are decided in #47.

Already decided (#47, #36):
- Each lens is an agent card and runs as an independent subagent with a fresh context pack.
- At most 5 findings per lens, each citing an ID.
- The 4-way disposition per finding (spec-fix, new open question, accepted risk, out of scope), gated by `unresolved: 0`.
- Fail-closed composition: the most severe outcome wins, and a missing verdict blocks.
- 3 jurors only for lenses with high-severity findings. Only the blocking lenses re-run after a fix.

## Research (2026-10-25)

Prior art was read from source: spec-kit-red-team, spec-kit-critique, agentstandards, multi-model-review, spec-kit-evaluator, spec-kit-verify-tasks, SARIF 2.1.0, Claude Code `/code-review` and security-review, CodeRabbit, Greptile, Copilot.

| Finding | Source | Consequence for NIO |
|---|---|---|
| Verbalized confidence clusters at 80–100 (ECE ≈ 0.4) | Xiong et al., ICLR 2024; RiskEval 2026 | A ≥ 70 filter cuts almost nothing. Ground findings instead. |
| Anthropic's `/code-review` replaced its confidence threshold with a validation pass per issue | anthropics/claude-code | Validate findings; don't trust the self-reported number |
| Evidence `observed | inferred | asserted`; observed is never downgraded by asserted | spec-kit-evaluator | Each finding quotes the artefact, and the CLI checks the quote |
| Strict JSON output hurts reasoning; free reasoning then fixed fields avoids it | Tam et al., EMNLP 2024 | Lens output: reasoning section first, findings in fixed fields after |
| Removing the explanation degrades verdicts by up to 52% for weaker models | arXiv 2512.16041 | Keep a reasoning section, even on cheap lenses |
| Fluent author rationale sways judges | ACL 2026 | The juror pack holds the artefact, not the author's reasoning |
| Self-preference bias tracks how well a model recognises its own text | Panickssery 2024; Wataoka 2024 | Juror model ≠ author model where possible (drafter is Opus, lenses Sonnet) |
| A panel of diverse models beats a single strong judge, at ~1/7 the cost | PoLL, Verga 2024 | Cross-host jurors (#4) later |
| Missing or invalid output blocks; human override is an appended record that keeps the original evidence | agentstandards, spec-kit-evaluator | Matches fail-closed; override = a new verdict, never an edit |
| `needs-full-package` → present findings, don't edit, stop | multi-model-review | `context: needs-more` never yields `approved` |
| Dedup: same location and same issue → merge, highest severity, credit all reviewers; contradictions kept, not resolved | wshobson multi-reviewer, spec-kit-evaluator | Deterministic key (cited ID, kind) |
| SARIF `baselineState` new / unchanged / absent | SARIF 2.1.0 | Re-review marks each finding, so fixed ones are visible and hit rate isn't double-counted |
| Red-team's gate is 4 grep checks, "an anti-sloppiness floor, not tamper-proofing" | spec-kit-red-team | The CLI checks structure; the validation pass checks substance |

## Decided (2026-10-25)

1. **Lens output** is markdown with fixed bullets. Reasoning comes first, findings after. There's no self-declared vote.
2. **Finding fields:** `cites`, `kind`, `severity`, `evidence` + `quote`, `situation`, `fix`. There's **no confidence number** (this amends #47). An `inferred` finding can't be a blocker.
3. **Validation:** the CLI grounds every finding (the cited IDs and quotes exist). Then **one refuter batch per gate** confirms or refutes each blocker and major finding. Refuted findings stay visible. Minors skip it.
4. **Dedup:** the CLI merges on the key (cited ID, kind), keeps the highest severity and credits every lens. The refuter may flag `same-as`. Different kinds on the same cite stay separate and are shown together.
5. **Storage:** raw output goes to `.nio/runs/<run>/jury/` (gitignored). The **ledger** `.nio/specs/<slug>/jury/<gate>.md` is committed. The **verdict record** `V-*` goes in `memory/project/` and points at the ledger.
6. **Disposition authority:**
   - the agent alone: a spec-fix that changes no behaviour, or a new open question;
   - through the grill: a spec-fix that changes behaviour;
   - the human only: accepted risk and out of scope;
   - agent dispositions are listed for the human at the gate.
7. **Composition:**
   - the CLI derives each lens's vote: block = a confirmed blocker or major;
   - missing, invalid or `needs-more` output gets one re-run, then goes to the human;
   - approved = all outputs valid and `unresolved: 0`;
   - rejected = unresolved findings remain;
   - human = no 2-of-3 majority, retries exhausted, or 2 failed rounds on one finding.
8. **Re-review:** one ledger per gate with permanent `J-<n>` IDs. Each re-run is matched by key: `new / unchanged / absent`, with a failed-round count. Status `open / disposed / fixed / refuted`.

### Formats

**Lens output**, `.nio/runs/<run>/jury/<gate>-<lens>[-<n>].md`:

```markdown
---
lens: logic
gate: spec
subject: checkout-refunds          # the spec slug
by: "juror / claude-code / sonnet"
context: sufficient                # sufficient | limited | needs-more
---
## Reasoning
Free text: what was checked and how.

## Findings
### F1 Shipped orders are both refundable and not
- cites: FR-1, FR-2
- kind: contradiction              # contradiction | gap | ambiguity | untestable | risk | scope | inconsistency
- severity: blocker                # blocker | major | minor
- evidence: observed               # observed | inferred
- quote: "Shipped orders can never be refunded"
- quote: "allowed while the order is paid or shipped"
- situation: an order is shipped and a refund arrives: FR-1 refunds it, FR-2 rejects it
- fix: keep one rule; if FR-2 holds, drop `shipped` from FR-1 and the table row
```

No findings: `## Findings` holds the single line `none`.

**Refuter output**, `<gate>-refuter.md`: one `### J<n>` block per blocker or major, with `- result: confirmed | refuted`, `- reason:` and an optional `- same-as: J<m>`.

**Ledger**, `.nio/specs/<slug>/jury/<gate>.md` (the CLI writes it, nobody edits it by hand):
- frontmatter: `gate`, `subject`, `round`, `outcome`;
- a table: `ID | Severity | Kind | Cites | Lenses | Validation | Status | Disposition (by) | Rounds`;
- then one `### J<n>` section per finding with its situations, quotes, fix and disposition note.

**Verdict record:** the existing `verdict` type, `subject: <gate>:<slug>`, `paths: [<ledger>]`. The Jurors table lists lens, host, model and vote (derived). Reasons and What was rejected summarise the ledger.

### Implementation plan

1. `nio jury collect <slug> <gate> --run R`: parse every lens output in the run, check the format, ground the cites and quotes against the gate's artefacts (spec: `spec.md`; plan: `plan.md`, `contracts.md`, `tests.md`, `architecture.md`; tasks: `tasks.md`), merge into the ledger with baseline matching, and print the refuter batch. Run it again after the refuter output exists to apply its results.
2. `nio jury dispose <slug> <gate> J<n> <disposition> --by agent|human --note "…"`: enforces the authority rules. `accepted-risk` and `out-of-scope` need `--by human`.
3. `nio jury check <slug> <gate>`: composes the outcome (approved / rejected / human) and the unresolved count, with exit code 0 only on approved. Writes the `V-*` record via `records.new`.
4. The `refuter` card (#36), and the `logic` card's Output format pointed at this format.
5. `tests/test_jury.py`.

Not in this issue: the jury skill that picks lenses and builds packs (needs the Risk flags from #20 and the triggers from #47), cross-host jurors (#4), and the flow guards (#45) that call `nio jury check`.



## Source: https://github.com/nikolajkarpic/nio/issues/47

### What needs designing

Which juror lenses run at which gate (spec, plan, tasks), how they judge, and how to keep tokens bounded. Lenses are agent cards (#36), and the verdict schema is #27.

Requirements from the human (2026-10-25):
1. The spec must be translatable into specific tests (unit, integration or e2e), to prove it was actually implemented.
2. Logical correctness must be checked.
3. Don't run lenses into oblivion for marginal gains.

## Decided (2026-10-25)

| Gate | CLI first (free) | Core lenses | Triggered |
|---|---|---|---|
| Spec | template, G/W/T, Observable and Level on every AC, state and decision tables complete, Risk flags present | testability, logic | adversary, security, scope, consistency |
| Plan | coverage matrix; every AC has a named test in `tests.md` | test-proof, architecture fit | logic (contracts with state), risk and rollback, security |
| Tasks | coverage, orphans, cycles, parallel file conflicts | executability (cheap) | none |

That's about 5 core lens runs per effort. The user advocate already walks the journeys before the grill (#37), so it doesn't run again at the jury.

**Test chain**
- Every AC has Given/When/Then, an **Observable** (exactly what a test asserts) and a **Level** (`unit` / `integration` / `e2e`). The CLI checks both are present, and the testability lens judges whether they're real.
- The plan's `tests.md` names the concrete test per AC (file, setup, assertion). The test-proof lens asks whether that test would fail if the AC broke.
- Tasks write a red test per AC. The epic evaluation (#29) proves the test ran, passed and wasn't tampered with.

**Logic**
- If a spec has states or conditional rules, it includes a **state table** and/or a **decision table** (the grill fills them in).
- The CLI checks every state × event and every condition combination has an outcome.
- The logic lens (strong / high, 1 juror) checks contradictions, broken invariants, unreachable states, and prose that disagrees with the tables. 3 jurors only via the ladder.

**Triggers**
- The spec has a **Risk flags** list (auth, PII, money, external input, data deletion, migration, multi-party, public API), confirmed in the grill.
- The CLI maps flags plus counts to lenses deterministically:
  - adversary: external input, multi-party, public API
  - security: auth, permissions, secrets, PII
  - scope: more than ~8 FRs, a new dependency, or an FR not traceable to the intake
  - consistency: memory returned related decisions or verdicts, or the spec touches existing modules
  - risk and rollback (plan): migration, schema change, data deletion, deploy config
  - logic (plan): contracts with state
- Triage (cheap) only picks the ladder rung. It may add a lens with a reason and never removes one.

**Cards**
- One card per concern, with `## At <gate>` question sections. The jury skill passes only the current gate's section.
- Hit rate is tracked per lens and per gate.

**Frugality**
- Each lens returns at most 5 findings, each with confidence ≥ 70 and an ID cited.
- Config caps lens runs per gate (default 6, counting each juror). The 3-juror escalation applies only to lenses with high-severity findings.
- Over the cap: `nio flow` shows the planned runs and their cost, and the human chooses: run all, drop the lowest-hit-rate lenses, or pick. Nothing is skipped silently.

**Re-runs after a fix**
- The CLI checks re-run in full.
- Only the blocking lenses re-run, on the changed sections plus their findings. A lens that approved re-runs only if the fix touched IDs it cited.
- After 2 failed rounds on the same finding, it goes to the human.

Impacts: #20 (template fields), #21 (CLI checks), #27 and #28 (lens lists), #36 (logic card in v1).


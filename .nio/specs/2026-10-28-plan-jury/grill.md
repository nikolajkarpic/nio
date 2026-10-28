# Grill log: 2026-10-28-plan-jury

Append-only. One entry per question, below-the-bar call or derived item.

## Session 1 · 2026-10-28 · @nio:grill, the human answers one at a time

## Facts · OP-1, OP-4, OP-9, OP-10 · 2026-10-28
Facet: actors (OP-1), change (OP-4, OP-9, OP-10)
Found: RF-1 to RF-5 (research.md). The security card has no plan-gate questions (RF-3), raised as OP-12. Nothing reopens an approved gate for a change request, but the fix-check pack can be reused (RF-4). `nio check plan` already proves each contract is delivered and cites an FR (RF-5).
Patched: A-2, UJ-1, AC-23, AC-24, FR-24, FR-35; added OP-12; retired OP-1, OP-4, OP-9, OP-10; retired FR-7 (a number the draft skipped)

## Asked · Q1 · OP-7, OP-11 · 2026-10-28
Question: Pick one: when a plan-jury finding's real cause is in the approved spec, who decides that and sends it back to the spec?
Context: Sending a finding back reopens a spec you already approved and pauses the plan jury until the spec jury re-checks the change. Today the jury skill settles findings itself when no behaviour changes, and hands you the rest (per the jury skill). A change request always stops work and tells you (per the remember skill).
Options: 1. The jury skill proposes, you confirm (Recommended): the skill marks the finding as rooted in the spec and writes a draft change request, but the spec is reopened only after you say yes. One stop per such finding. A plan-only fix with no behaviour change is still settled by the agent, as at the spec gate. 2. The juror and refuter decide: the juror marks it, the refuter confirms, and the spec reopens automatically. No stop for you, but an agent reopens an approved spec. 3. You decide every finding: every confirmed plan-jury finding comes to you, plan-only or spec-rooted. The most control, and the most of your time.
Refs: OP-7, OP-11 · FR-32, FR-34 · RF-4 · skills/jury/SKILL.md · skills/remember/SKILL.md:98-100

## Q1 · OP-7, OP-11 · 2026-10-28
Facet: actors
Question: When a plan-jury finding's real cause is in the approved spec, who decides that and sends it back to the spec?
Options:
1. The jury skill proposes, you confirm (recommended)
2. The juror and refuter decide
3. You decide every finding
Answer: 1. The jury skill proposes, you confirm: the skill marks the finding as rooted in the spec and drafts the change request, but the spec is reopened only after you say yes. One stop per such finding. A plan-only fix with no behaviour change is still settled by the agent, as at the spec gate. [human]
Patched: FR-32, FR-34, UJ-2; added FR-41; retired OP-7, OP-11

## Call · FR-41 · 2026-10-28
The ledger needs a name for a spec-rooted finding's disposition: `spec-change`, naming its change request. It is below the bar: it changes no user ability, nothing the user sees beyond a ledger label, no permission, no data kept, no cost. [agent]

## Asked · Q2 · OP-6 · 2026-10-28
Question: Pick one: which sources may a plan-jury finding quote as its evidence?
Context: A finding is dropped unless its quote is found word for word in an allowed source. Today only the judged files and your words count (per the jury code). Plan jurors need to quote the spec, the code a contract binds, the code its `Like:` line names, and CLAUDE.md, so they'd lose most real findings.
Options: 1. The plan files plus what the juror was given (Recommended): the four plan files, the spec, CLAUDE.md, `architecture.md` and every file a contract or `Like:` line binds. Real findings survive, and quotes stay checkable for free. 2. The plan files plus the spec only: simpler, but architecture-fit and test-proof findings about the code are dropped. 3. Any file in the repo: nothing real is dropped, but a juror can ground a finding in unrelated code.
Refs: OP-6 · FR-12 · src/nio/jury.py (grounding in collect)

## Q2 · OP-6 · 2026-10-28
Facet: verification
Question: Which sources may a plan-jury finding quote as its evidence?
Options:
1. The plan files plus what the juror was given (recommended)
2. The plan files plus the spec only
3. Any file in the repo
Answer: 1. The plan files plus what the juror was given: the four plan files, the spec, CLAUDE.md, `architecture.md` and every file a contract or `Like:` line binds. Real findings survive, and quotes stay checkable for free. [human]
Patched: added FR-42, AC-44; retired OP-6

## Call · FR-43 (OP-5) · 2026-10-28
How a juror gets its extra files (a card field or the skill's pack rules) is how, not what. Call: the CLI lists the plan-gate juror files, and that list is the same one grounding accepts (FR-42), so the two can't drift. Below the bar: no change to what a user can do or sees, who may do it, what data is kept, or cost (the files are the ones Q2 already allows). [agent]
Patched: added FR-43, AC-45; retired OP-5

## Asked · Q3 · OP-2, OP-12 · 2026-10-28
Question: Pick one: does this spec write the questions for the two lenses that only run on risky plans, risk-and-rollback and security?
Context: Risk-and-rollback runs when a spec is flagged for a migration or data deletion. It has no card, so such a plan's jury would be blocked (per the agent cards folder). Security runs on auth or personal-data specs. Its card has no plan-gate questions, so it would run with nothing to ask (per research).
Options: 1. Write both here (Recommended): a risky plan can be judged as soon as this ships. Costs two more pieces of card text to write and review. 2. Neither, for now: risky plans stay blocked at the plan jury until a later spec adds them, and security is left off the plan gate. Less work now, but the riskiest plans can't pass. 3. Security only: auth and personal-data plans pass, but migration and data-deletion plans stay blocked.
Refs: OP-2, OP-12 · FR-5, FR-6, FR-9 · RF-3 · src/nio/agents/

## Q3 · OP-2, OP-12 · 2026-10-28
Facet: failure
Question: Does this spec write the questions for the two lenses that only run on risky plans, risk-and-rollback and security?
Options:
1. Write both here (recommended)
2. Neither, for now
3. Security only
Answer: 1. Write both here: a risky plan can be judged as soon as this ships. Costs two more pieces of card text to write and review. [human]
Patched: FR-5, decision-table row (security); added FR-44, FR-45, AC-46, AC-47; retired OP-2, OP-12

## Asked · Q4 · OP-3 · 2026-10-28
Question: Pick one: besides the migration and data-deletion flags, what else should make the risk-and-rollback lens run on a plan?
Context: The flags are set on the spec and confirmed in the grill (per the spec template). A plan can still change stored data the flags missed. The plan's contracts file has a data-model section that's present only when the plan stores or changes data (per the contracts template), so it's a free signal. Each extra run costs one strong-model review.
Options: 1. The flags, or a data-model section in the contracts (Recommended): catches data changes the flags missed, checked for free; costs a review on plans that only add a field. 2. The flags only: cheapest and predictable, but a data change nobody flagged gets no rollback review. 3. Always run it: nothing slips, but every plan pays for a review most don't need.
Refs: OP-3 · FR-6 · src/nio/templates/contracts.md (## Data model) · src/nio/spec.py:21-22

## Q4 · OP-3 · 2026-10-28
Facet: data
Question: Besides the migration and data-deletion flags, what else should make the risk-and-rollback lens run on a plan?
Options:
1. The flags, or a data-model section in the contracts (recommended)
2. The flags only
3. Always run it
Answer: 1. The flags, or a data-model section in the contracts: catches data changes the flags missed, checked for free; costs a review on plans that only add a field. [human]
Patched: FR-6, decision table (plan-gate lenses); added AC-48; retired OP-3

## Asked · Q5 · OP-8, FR-29 · 2026-10-28
Question: Pick one: what does a new interface write on its "copies this code" line when nothing in the codebase is like it?
Context: You decided each new interface names the existing code it copies, and the free check confirms that code exists (decision 1 on the issue). A first-of-its-kind interface (the first HTTP endpoint, the first parser) has nothing to name. Leaving the line out today would be an error.
Options: 1. Write `Like: none` with a reason (Recommended): the free check accepts it, and the architecture lens judges whether the reason holds or similar code was missed. Nothing goes unexplained. 2. Always name the closest thing: no exception to check, but the plan may name a poor model just to pass, which misleads the builder. 3. Leave the line out: less to write, but a missing line can't be told apart from a forgotten one.
Refs: OP-8 · FR-28, FR-29, FR-22 · issue #57 decision 1

## Q5 · OP-8, FR-29 · 2026-10-28
Facet: meaning
Question: What does a new interface write on its "copies this code" line when nothing in the codebase is like it?
Options:
1. Write `Like: none` with a reason (recommended)
2. Always name the closest thing
3. Leave the line out
Answer: 1. Write `Like: none` with a reason: the free check accepts it, and the architecture lens judges whether the reason holds or similar code was missed. Nothing goes unexplained. [human]
Patched: FR-28, FR-29 (derived), AC-27 (derived), Key entities (`Like:` line); added FR-46, AC-49, AC-50; retired OP-8

## Facts · FR-4, FR-9, FR-11, FR-39 · 2026-10-28
Facet: change
Found: RF-6 to RF-9 (research.md). #47 already decided logic's trigger (RF-6). The CLI already blocks a gate with a missing card (RF-7) and keeps one ledger per gate (RF-8). The tasks-stage spec already counts a gate the human closed as approved (RF-9).
Patched: FR-4, AC-4, AC-5, the logic row, FR-9, FR-11, AC-8, Key entity (plan gate ledger), FR-39, AC-42

## Derived · AC-3, AC-6, AC-11, AC-27, AC-31, AC-34, FR-13, non-goal (mutation testing) · 2026-10-28
AC-3 from FR-2 (the plan check, not the spec check, gates the plan jury). AC-6 from FR-5. FR-13 and AC-11 from FR-1 and RF-1. AC-27 and AC-31 from FR-28 (only `new` contracts need `Like:`). AC-34 from FR-33. Mutation testing is out because FR-18 judges by reading and runs nothing.

## Call · FR-33 · 2026-10-28
`plan-fix` is refused at any gate but the plan gate. Below the bar: it guards a label and changes no user ability, nothing the user sees, no permission, no data kept, no cost. [agent]

## Call · SC-1, SC-2 · 2026-10-28
These are success measures, kept as drafted. Below the bar: they change no behaviour, permission, data or cost. [agent]

## Call · non-goal (tasks gate lenses) · 2026-10-28
The tasks gate's lenses stay with the tasks-stage spec. Below the bar: the scope boundary is already set by that approved spec, and it changes no behaviour, permission, data or cost here. [agent]

## Asked · Q6 · FR-40 · 2026-10-28
Question: Pick one: which model class and effort should the three new plan reviews run on (test-proof, architecture-fit, risk-and-rollback)?
Context: Every plan pays for test-proof and architecture-fit. Risk-and-rollback runs only on data changes. Today the logic, security and adversary reviews run strong with high effort, and testability runs strong with medium effort (per the agent cards). Test-proof has to invent a concrete bug for every planned test, which is the hardest reasoning of the three.
Options: 1. All three strong, high effort (Recommended): matches the logic and security reviews, at the same cost per run. 2. Test-proof on the max model, the other two strong and high: better bug-finding where it's hardest, but every plan pays for a max-model run. 3. All three strong, medium effort: cheapest, but test-proof may stop at shallow bugs.
Refs: FR-40, FR-44 · src/nio/agents/*.md (tier, effort)

## Q6 · FR-40 · 2026-10-28
Facet: verification
Question: Which model class and effort should the three new plan reviews run on (test-proof, architecture-fit, risk-and-rollback)?
Options:
1. All three strong, high effort (recommended)
2. Test-proof on the max model, the other two strong and high
3. All three strong, medium effort
Answer: free-form: "we can run opus level models on medium for this i think". Read as all three on the max tier (Opus on Claude), effort med. [human]
Patched: FR-40, AC-12, AC-20, AC-46

## Asked · Q7 · state table (plan gate) · 2026-10-28
Question: Pick one: while a finding is back with the spec, what happens to the plan jury, and can a finding still go back to the spec once the plan is approved?
Context: You decided a spec-rooted finding reopens the spec only after you confirm (Q1). The spec jury then re-checks only what changed. The draft adds a waiting state: the plan jury is paused until the spec is re-approved. Once the plan is approved or you've closed its jury, a new problem needs a change request instead.
Options: 1. Pause the plan jury, and after approval go through a change request (Recommended): no plan round runs on a spec that's mid-change, and an approved plan is only changed through a change request, which you see. A spec change stops the plan jury until it's done. 2. Keep the plan jury running on the other findings: faster, but later plan fixes may build on spec text that's about to change. 3. Pause, but let the jury still reopen an approved plan by itself: fewer change requests, but an approved plan can change without you seeing a request.
Refs: state table "plan gate" · FR-34, FR-35, FR-41 · grill Q1

## Q7 · state table (plan gate) · 2026-10-28
Facet: data
Question: While a finding is back with the spec, what happens to the plan jury, and can a finding still go back to the spec once the plan is approved?
Options:
1. Pause the plan jury, and after approval go through a change request (recommended)
2. Keep the plan jury running on the other findings
3. Pause, but let the jury still reopen an approved plan by itself
Answer: 1. Pause the plan jury, and after approval go through a change request: no plan round runs on a spec that's mid-change, and an approved plan is only changed through a change request, which you see. A spec change stops the plan jury until it's done. [human]
Patched: state table "plan gate" (all four rows)

## Finish · 2026-10-28
Fidelity: re-read FR-5, FR-6, FR-28, FR-32, FR-34, FR-40 to FR-46 and the plan-gate state table against Q1 to Q7; none drifted. Passivity: the human pushed back on Q6, so no prompt was needed. The notes (agent calls FR-33, FR-41, FR-43, SC-1, SC-2, one non-goal; derived items) were shown. Answer: Finish. [human]

## Session 2 · 2026-10-28 · @nio:grill on the spec jury's round-1 findings that change behaviour (J-5 to J-8)

## Asked · Q8 · J-7 · 2026-10-28
Question: Pick one: should the tasks stage refuse a spec that has no plan at all?
Context: As written, the tasks stage refuses only a spec that has a plan the jury hasn't approved. A spec that skipped the plan stage gets through (per the logic review). But a bug-fix spec never has a plan stage, by design (per the plan code), so a blanket refusal would block every bug fix.
Options: 1. Refuse a full spec with no approved plan; bug fixes go straight to tasks (Recommended): no full spec skips the plan, and bug fixes keep working. 2. Refuse any spec with no approved plan: strictest, but bug fixes can never reach tasks until they get a plan stage. 3. Keep it as written: nothing to change, but a full spec can skip the plan and its jury.
Refs: J-7 · FR-38, A-4, AC-40 · src/nio/plan.py full_spec()

## Q8 · J-7 · 2026-10-28
Question: Should the tasks stage refuse a spec that has no plan at all?
Options:
1. Refuse a full spec with no approved plan; bug fixes go straight to tasks (recommended)
2. Refuse any spec with no approved plan
3. Keep it as written
Answer: 1. Refuse a full spec with no approved plan; bug fixes go straight to tasks: no full spec skips the plan, and bug fixes keep working. [human]
Patched: FR-38; added AC-55

## Asked · Q9 · J-8 · 2026-10-28
Question: Pick one: when the spec changes after the plan was approved, what happens to the plan's approval?
Context: After approval, a problem rooted in the spec goes through a change request (you said in Q7). As written, the plan stays approved even after the spec under it changes, so the tasks stage could start on a plan nobody checked against the new spec (per the logic review).
Options: 1. The plan jury reopens on what changed (Recommended): once the spec is re-approved, the plan's approval is withdrawn and the plan jury re-checks only the parts tied to the changed spec items, then approves again. Tasks wait for that. 2. A full new plan jury: safest, but every spec change costs a full review of the plan. 3. Keep the approval: no extra cost, but tasks can start on a plan that no longer matches the spec.
Refs: J-8 · state table rows approved and closed-by-human · FR-35, FR-38 · grill Q7

## Q9 · J-8 · 2026-10-28
Question: When the spec changes after the plan was approved, what happens to the plan's approval?
Options:
1. The plan jury reopens on what changed (recommended)
2. A full new plan jury
3. Keep the approval
Answer: 1. The plan jury reopens on what changed: once the spec is re-approved, the plan's approval is withdrawn and the plan jury re-checks only the parts tied to the changed spec items, then approves again. Tasks wait for that. [human]
Patched: state table rows approved and closed-by-human; added FR-47, AC-56

## Asked · Q10 · J-5 · 2026-10-28
Question: Pick one: while the plan jury waits on a spec change, what if the change fails or is dropped, and what if a second problem rooted in the spec turns up?
Context: As written, the paused plan jury resumes only when the spec is re-approved. If you drop the change, or the spec jury can't settle it, the plan jury stays paused for good. A second problem rooted in the spec is silently ignored (per the logic review).
Options: 1. A dropped change resumes the plan jury, and a second problem joins the open change (Recommended): if you drop the change, the finding comes back to you to fix in the plan or accept as a risk. A second problem is added to the same change request, so one spec re-check covers both. 2. A dropped change closes the plan jury: simpler, but you lose the plan jury's remaining review. 3. A second problem waits until the first change is done: one change at a time, but two spec re-checks and a longer pause.
Refs: J-5 · state table row waiting-on-spec · FR-34, FR-35

## Q10 · J-5 · 2026-10-28
Question: While the plan jury waits on a spec change, what if the change fails or is dropped, and what if a second problem rooted in the spec turns up?
Options:
1. A dropped change resumes the plan jury, and a second problem joins the open change (recommended)
2. A dropped change closes the plan jury
3. A second problem waits until the first change is done
Answer: 1. A dropped change resumes the plan jury, and a second problem joins the open change: if you drop the change, the finding comes back to you to fix in the plan or accept as a risk. A second problem is added to the same change request, so one spec re-check covers both. [human]
Patched: state table (new event "spec change dropped"; waiting-on-spec row); added FR-48, FR-49, AC-57, AC-58

## Asked · Q11 · J-6 · 2026-10-28
Question: Pick one: when the plan jury hands its open findings to you, what state is the gate in until you act?
Context: The jury hands the gate to you when only majors remain after the first review, or when the final fix check flags something (per the jury's stop rule). Then you either settle the list with fixes, which earns one final check, or close the gate with a reason. The state table has no state for "with you", so it can't say whether a later round could approve a gate you're still holding (per the logic review).
Options: 1. Add a "with you" state (Recommended): the tasks stage refuses while the gate is there, and only your ruling moves it. Settling with fixes leads to the one final check, and closing with a reason closes it. 2. Treat it as still open: no new state, but a later round could approve a gate you haven't ruled on. 3. Handing it to you closes it: fewer steps, but a plan with open findings reaches tasks without your say.
Refs: J-6 · FR-12, FR-39, AC-42 · state table plan gate · D-261026-r52z

## Q11 · J-6 · 2026-10-28
Question: When the plan jury hands its open findings to you, what state is the gate in until you act?
Options:
1. Add a "with you" state (recommended)
2. Treat it as still open
3. Handing it to you closes it
Answer: 1. Add a "with you" state: the tasks stage refuses while the gate is there, and only your ruling moves it. Settling with fixes leads to the one final check, and closing with a reason closes it. [human]
Patched: state table (new state with-human; new events "handed to the human" and "human settles with fixes"); added FR-50, AC-59

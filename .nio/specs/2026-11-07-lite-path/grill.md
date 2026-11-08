# Grill: 2026-11-07-lite-path

Session 1 (2026-11-07): delegated to the agent (orchestrator / claude-code / claude-opus-5-5) by the human, with standing authority to take the recommended option. Permissions, deletion and irreversible steps would still go to the human; none came up.

## Lookup · OP-1, OP-3, OP-6, OP-7, OP-8, OP-9 · 2026-11-07
Facet: meaning, actors, change, verification
Found: RF-1 to RF-17 in research.md. Retired OP-1 (RF-1, RF-2), OP-3 (RF-3 to RF-5, RF-8, RF-9), OP-6 (RF-6: FR-5 and AC-7 already hold), OP-7 (RF-12, RF-16), OP-8 (RF-15), OP-9 (RF-13, RF-14). AC-3 retired: green already proves the after-fix pass, and AC-4 proves the before-fix fail (RF-5).

## Asked · Q1 · FR-2 · 2026-11-07
Question: Which stages does a lite effort run, given that implementing claims its work from `tasks.md`?
Context: The intake skips "plan and tasks", but the implement stage only starts after a `nio: approve tasks` commit and builds each worker's pack from `tasks.md` (RF-9); the tasks stage already makes one epic for a bug fix (RF-8). The spec jury is the other gate lite could drop (#44: "a bugfix has no spec gate worth a lens run").
Options: 1. Skip the spec jury, plan and plan jury; keep tasks and the tasks jury as the human's one approval before code (recommended): saves about 8–14 min of plan and 5–10 of spec gate (RF-2); no change to implement. 2. Skip only the plan and plan jury: smallest change, saves less, two approvals remain. 3. Skip tasks too and generate `tasks.md`: needs new code to pick files, tiers and modes, which is the drafter's judgement.
Refs: FR-1, FR-2 · RF-2, RF-8, RF-9 · #44

## Q1 · FR-2 · 2026-11-07
Question: Which stages does a lite effort run, given that implementing claims its work from `tasks.md`?
Facet: change
Options:
1. Skip spec jury, plan, plan jury; keep tasks and the tasks jury (recommended)
2. Skip only plan and plan jury
3. Skip tasks too, generate tasks.md
Answer: 1. Skip the spec jury, plan and plan jury; keep tasks and the tasks jury as the human's one approval before code: saves about 8–14 min of plan and 5–10 of spec gate; no change to implement. [agent]
Patched: Summary, FR-1, FR-2, AC-1, UJ-1, state table "Lite effort"

## Asked · Q2 · OP-2 · 2026-11-07
Question: Which lenses review a lite fix at the implementation jury?
Context: The implementation gate always runs conformance and correctness, plus risk-flag lenses (RF-10); #44 proposed correctness alone. Every lens still finds issues only it raises, and dropping one saves under a minute (RF-11).
Options: 1. Keep the gate's usual lenses (recommended): no code, both run in parallel. 2. Correctness alone: needs a lite branch in the lens plan; loses conformance's AC-to-test matching. 3. Add the spec gate's lenses too: brings back the cost lite removes.
Refs: OP-2 · FR-13 · RF-10, RF-11

## Q2 · OP-2 · 2026-11-07
Question: Which lenses review a lite fix at the implementation jury?
Facet: verification
Options:
1. Keep the gate's usual lenses (recommended)
2. Correctness alone
3. Add the spec gate's lenses
Answer: 1. Keep the gate's usual lenses: no code, both run in parallel. [agent]
Patched: FR-13, AC-5; retired OP-2

## Asked · Q3 · OP-5 · 2026-11-07
Question: Does the human approve the bugfix spec separately before the fix starts?
Context: With the spec jury skipped (Q1), the tasks gate's approval commit is the one approval; its estimate shows the tests and tasks built from the spec.
Options: 1. No: one approval, at the tasks gate (recommended): one human stop instead of two. 2. Yes, a separate spec approval: one more stop, about 2 min of the human's time. 3. No approval at all: nothing stops before code is written.
Refs: OP-5 · FR-1

## Q3 · OP-5 · 2026-11-07
Question: Does the human approve the bugfix spec separately before the fix starts?
Facet: actors
Options:
1. One approval, at the tasks gate (recommended)
2. A separate spec approval
3. No approval
Answer: 1. No: one approval, at the tasks gate: one human stop instead of two. [agent]
Patched: UJ-1; retired OP-5

## Asked · Q4 · OP-4 · 2026-11-07
Question: What happens when the human declines the switch to the full flow?
Context: Escalation is an offer; the human may know the change is small despite the trigger.
Options: 1. Continue on lite and log the call with the trigger it overrides (recommended): the human's judgement stands and is traceable. 2. Pause the effort: the human must restart it, for no new information. 3. Abandon it: loses the settled spec.
Refs: OP-4 · FR-11

## Q4 · OP-4 · 2026-11-07
Question: What happens when the human declines the switch to the full flow?
Facet: failure
Options:
1. Continue on lite, logged (recommended)
2. Pause
3. Abandon
Answer: 1. Continue on lite and log the call with the trigger it overrides: the human's judgement stands and is traceable. [agent]
Patched: FR-11, AC-12; retired OP-4

## Asked · Q5 · FR-9 · 2026-11-07
Question: Is "the expected behaviour needs a decision with two or more real options" its own escalation trigger?
Context: The grill already asks every point over its bar (FR-3); what makes such a decision too big for lite is that it changes an interface, stored data or a dependency, which FR-8 lists.
Options: 1. Fold it into FR-8's list and the grill's bar; retire FR-9 and AC-10 (recommended): one trigger list. 2. Keep it separate: every lite grill question would offer escalation. 3. Drop it without folding: a contract change found in the grill goes unflagged.
Refs: FR-9, AC-10, FR-8 · RF-12

## Q5 · FR-9 · 2026-11-07
Question: Is "the expected behaviour needs a decision with two or more real options" its own escalation trigger?
Facet: meaning
Options:
1. Fold into FR-8 and the grill's bar (recommended)
2. Keep separate
3. Drop
Answer: 1. Fold it into FR-8's list and the grill's bar; retire FR-9 and AC-10: one trigger list. [agent]
Patched: FR-8, AC-16; retired FR-9, AC-10

## Asked · Q6 · FR-8 · 2026-11-07
Question: How is "more than one module" checked?
Context: Each task's `Files:` line names what it changes, and `nio check tasks` parses it (RF-16). A new dependency or an interface change can't be read from file names.
Options: 1. `nio check tasks` fails a lite tasks list whose non-test files sit in more than one folder; the other triggers stay with the agent, from the skills (recommended): one deterministic check, before any code. 2. Count from the diff at the implementation jury: found only after the work is done. 3. All triggers by the agent's judgement: no check at all.
Refs: FR-8, AC-9 · RF-16, RF-12

## Q6 · FR-8 · 2026-11-07
Question: How is "more than one module" checked?
Facet: data
Options:
1. `nio check tasks` on folders of non-test files; other triggers by the agent (recommended)
2. Count from the diff at the jury
3. Agent's judgement only
Answer: 1. `nio check tasks` fails a lite tasks list whose non-test files sit in more than one folder; the other triggers stay with the agent, from the skills: one deterministic check, before any code. [agent]
Patched: FR-8, AC-9, AC-16, Glossary "Module", Non-goals

## Asked · Q7 · FR-7 · 2026-11-07
Question: How does an unchanged-behaviour test prove it passes both before and after the fix?
Context: Red refuses a test that passes, so a preservation test can't go through red; a `direct` task has no red, only green (RF-17), and the epic's suite runs at its close.
Options: 1. Each unchanged-behaviour test is its own `direct` task the fix's task depends on: its green runs before the fix, the suite after (recommended): no code, a card line. 2. A new "passes before" check in red: new code for one case. 3. Only after the fix: misses a test that never passed.
Refs: FR-7, AC-8 · RF-17

## Q7 · FR-7 · 2026-11-07
Question: How does an unchanged-behaviour test prove it passes both before and after the fix?
Facet: verification
Options:
1. Own `direct` task before the fix (recommended)
2. New check in red
3. Only after
Answer: 1. Each unchanged-behaviour test is its own `direct` task the fix's task depends on: its green runs before the fix, the suite after: no code, a card line. [agent]
Patched: FR-7, AC-8

## Asked · Q8 · FR-10 · OP-9 · 2026-11-07
Question: How does an escalated lite effort continue on the full route?
Context: The flow places an effort from its files, so a spec rewritten as `route: full` is re-placed at the first full stage not passed (RF-13); a full spec can't keep CB, EB or UB IDs (RF-14).
Options: 1. Rewrite the same effort's spec on the full template, each current, expected and unchanged item becoming an FR with its AC and keeping its tag (recommended): same folder, branch and history; nothing re-asked. 2. Start a new full spec with the lite spec as its intake: a second folder; the lite one must be abandoned by the human. 3. A new CLI command that converts the spec: code for a rare event.
Refs: FR-10, AC-11 · RF-13, RF-14

## Q8 · FR-10 · OP-9 · 2026-11-07
Question: How does an escalated lite effort continue on the full route?
Facet: data
Options:
1. Rewrite the same effort's spec on the full template (recommended)
2. New full spec, lite one abandoned
3. New CLI command
Answer: 1. Rewrite the same effort's spec on the full template, each current, expected and unchanged item becoming an FR with its AC and keeping its tag: same folder, branch and history; nothing re-asked. [agent]
Patched: FR-10, AC-11, UJ-2, state table "Lite effort"; retired OP-9

## Asked · Q9 · OP-8 · 2026-11-07
Question: Where do the routing criteria (#11) live?
Context: The route is picked by the spec skill at intake (RF-15); #11 proposed four checkable rules and no model router.
Options: 1. In the spec skill's routing step, the four rules and a one-line proposal (recommended): no code; escalation catches a wrong call. 2. A CLI check refusing a lite spec with a risky flag: breaks today's bugfix fixtures carrying `money`. 3. A model router: needs labelled history NIO doesn't have.
Refs: FR-12, FR-14, AC-13, AC-14, AC-15 · RF-15 · #11

## Q9 · OP-8 · 2026-11-07
Question: Where do the routing criteria (#11) live?
Facet: actors
Options:
1. Spec skill's routing step (recommended)
2. CLI check
3. Model router
Answer: 1. In the spec skill's routing step, the four rules and a one-line proposal: no code; escalation catches a wrong call. [agent]
Patched: AC-13, AC-14, AC-15; retired OP-8

## Call · UJ-1, UJ-2, A-2
Below the bar (no change to what a user can do or sees, who may do it, data kept, or cost): journeys rewritten to match Q1 and Q8. [agent]

## Finish · 2026-11-07
`nio check spec --gate` passes. Fidelity re-read: FR-1, FR-2, FR-8, FR-10, FR-11, FR-13, AC-1, AC-8, AC-9, AC-11 match their answers. Delegated session: finish confirmed by the agent; every [agent] answer above is shown to the human in the decision matrix.

## Session 2 (2026-11-07): spec jury round 1 findings, delegated as session 1

## Asked · Q10 · J-5, J-9 · 2026-11-07
Question: Should the folder trigger in `nio check tasks` be an error or a note, and how is a folder counted?
Context: The spec jury found a declined switch can't go on when the check fails (J-5), and the folder count unclear (J-9).
Options: 1. A note (`escalate:`) the tasks skill stops on; a folder is a non-test file's direct parent, the root counting as one; a test file sits under `tests`/`test` or starts `test_` (recommended): a decline goes on, one exact rule. 2. An error with an override field in tasks.md: one more field to keep. 3. Top-level folder only: misses a two-package change under `src/`.
Refs: J-5, J-9 · FR-8, AC-9, Glossary "Module"

## Q10 · J-5, J-9 · 2026-11-07
Question: Should the folder trigger in `nio check tasks` be an error or a note, and how is a folder counted?
Facet: failure
Options:
1. Note; direct parent folder; test-file pattern (recommended)
2. Error with an override field
3. Top-level folder only
Answer: 1. A note (`escalate:`) the tasks skill stops on; a folder is a non-test file's direct parent, the root counting as one; a test file sits under `tests`/`test` or starts `test_`: a decline goes on, one exact rule. [agent]
Patched: FR-8, AC-9, Glossary "Module", Key entities "Escalation trigger"

## Asked · Q11 · J-1 · 2026-11-07
Question: Where does an escalated effort stand once its spec is rewritten on the full route?
Context: Lite records skip lines for the spec jury and plan; the flow places an effort from files and approval commits (RF-13), so a gate passes only with its `nio: approve` commit.
Options: 1. A skip line never counts as a gate's pass: spec_jury when the rewritten spec passes the gate check, grilling when it doesn't (recommended): the full spec is judged before planning. 2. Count skips as passed: the full spec would go to planning unjudged. 3. Always restart at drafting: re-asks settled items.
Refs: J-1 · FR-10, AC-11 · RF-13

## Q11 · J-1 · 2026-11-07
Question: Where does an escalated effort stand once its spec is rewritten on the full route?
Facet: change
Options:
1. Skips never count as a gate's pass (recommended)
2. Skips count as passed
3. Restart at drafting
Answer: 1. A skip line never counts as a gate's pass: spec_jury when the rewritten spec passes the gate check, grilling when it doesn't: the full spec is judged before planning. [agent]
Patched: FR-10, AC-11

## Asked · Q12 · J-8 · 2026-11-07
Question: May a defect flagged external-input, multi-party or public-api take the lite route?
Context: #11's rule names five flags (auth, money, data-deletion, migration, pii); the implementation gate still plans lenses from risk flags (RF-10).
Options: 1. Yes, their lenses run at the implementation gate as usual (recommended): #11's rule unchanged. 2. No, all eight flags force full: fewer fixes get lite. 3. Only public-api forces full: a rule nobody asked for.
Refs: J-8 · FR-12 · RF-10 · #11

## Q12 · J-8 · 2026-11-07
Question: May a defect flagged external-input, multi-party or public-api take the lite route?
Facet: actors
Options:
1. Yes, lenses run as usual (recommended)
2. All eight force full
3. Only public-api forces full
Answer: 1. Yes, their lenses run at the implementation gate as usual: #11's rule unchanged. [agent]
Patched: FR-12

## Asked · Q13 · J-12, J-10 · 2026-11-07
Question: How are the time saving and the before-and-after preservation test held to account?
Context: One dogfood run can't prove a 15-minute margin (J-12); a card sentence can't prove a drafter follows it (J-10).
Options: 1. NFR-2 becomes a reported measure against RF-2's stage times; FR-7 and AC-8 say what the card instructs, judged at the tasks jury (recommended): honest about what a test can show. 2. Repeat runs until a median exists: hours for one number. 3. A check that a UB task is direct and precedes the fix: code for a rule the jury already sees.
Refs: J-12, J-10 · NFR-2, FR-7, AC-8 · RF-2

## Q13 · J-12, J-10 · 2026-11-07
Question: How are the time saving and the before-and-after preservation test held to account?
Facet: verification
Options:
1. Reported measure; card instruction judged at the tasks jury (recommended)
2. Repeat runs
3. A new check
Answer: 1. NFR-2 becomes a reported measure against RF-2's stage times; FR-7 and AC-8 say what the card instructs, judged at the tasks jury: honest about what a test can show. [agent]
Patched: NFR-2, FR-7, AC-8

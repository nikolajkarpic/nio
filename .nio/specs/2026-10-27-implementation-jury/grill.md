# Grill log: 2026-10-27-implementation-jury

Append-only. One entry per question, below-the-bar call or derived item.

## Session 1 · 2026-10-27 · @nio:grill, the human answers

## Facts · OP-1, OP-6, OP-7, OP-8 · 2026-10-27
Facet: actors (OP-1), cost (OP-6), change (OP-7), verification (OP-8)
Found: RF-1 to RF-26 (research.md).
Patched: A-2, A-5, UJ-1, UJ-2, UJ-3, UJ-4, FR-2, a non-goal and two risks to [research]; retired OP-1, OP-6, OP-7, OP-8

## Asked · Q1 · OP-2, OP-3, OP-4, OP-5 · 2026-10-27
Question: How should the grill handle the four facts research couldn't settle?
Context: They depend on the tasks stage, the implement stage and the test-commands design, none decided yet (#42, #43, #45, #38, #48, #49).
Options: 1. Defer them, grill the rest (recommended): marked as waiting on those issues; nothing guessed, spec can't be built until they settle. 2. Decide them now: complete today, but pre-decides parts of #42, #43, #49. 3. Pause and design #42 and #43 first.
Refs: OP-2, OP-3, OP-4, OP-5, RF-16–RF-23, #42, #43, #49

## Q1 · OP-2, OP-3, OP-4, OP-5 · 2026-10-27
Question: How should the grill handle the four facts research couldn't settle?
Options:
1. Defer them, grill the rest (recommended)
2. Decide them now in the grill
3. Pause, design #42 and #43 first
Answer: 1. Defer them, grill the rest: mark the four as waiting on #42, #43 and #49 and grill the decisions that don't depend on them; nothing is guessed, but the spec can't be built until those issues settle. [human]
Patched: DF-1 to DF-4; retired OP-2, OP-3, OP-4, OP-5

## Asked · Q2 · OP-10 · 2026-10-27
Question: How does the tool know which test proves which requirement, and which code implements it?
Context: Every later check rests on this link: "no test for this requirement" is only as good as the matching. Task files don't have a fixed format yet (#42), and the plan's test list names a test per requirement (#47).
Options: 1. Tests name the requirement IDs (recommended): each test carries the IDs it proves (a comment or test name); the tool matches by grep, free and exact; the code side is left to the conformance lens. Lost: tests must follow a naming rule, and an untagged test counts as no evidence. 2. Use the plan's test list and task citations: the tool reads which test the plan named and which files each task touched. Lost: depends on formats #42 and #48 haven't fixed, and a renamed test breaks the link silently. 3. Let the conformance lens judge: no tagging rule; the lens reads tests and code and decides. Lost: the check costs model calls, can't be free, and two runs may disagree.
Refs: OP-10, FR-4, FR-5, NFR-1, #42, #47, #48

## Q2 · OP-10 · 2026-10-27
Question: How does the tool know which test proves which requirement, and which code implements it?
Options:
1. Tests name requirement IDs (recommended)
2. Plan's test list + task citations
3. Conformance lens judges
Answer: free-form: "i do not want tests to have spec stuff in them like whtever we should judge what the test is for based on the description and then match them by lense" [human]
Patched: none yet; contradicts the earlier decision that per-AC evidence is a free CLI check (#29 table, FR-4, FR-5, NFR-1). Raised as Q3.

## Asked · Q3 · OP-10 (contradiction) · 2026-10-27
Question: Matching tests to requirements by lens contradicts "per-requirement evidence is a free tool check". Which way?
Context: Earlier today the per-requirement evidence sat in the free tool column (#29 table; FR-4, FR-5, NFR-1). Q2's answer moves the matching to a lens reading each test's description.
Options: 1. Tool runs, lens matches (recommended): the tool still runs all tests and lists results for free; the conformance lens matches each requirement to the tests that prove it, and raises missing evidence. Lost: matching costs model calls and can vary between runs. 2. Keep it fully free: back to a mechanical link. Lost: needs spec IDs in tests, which Q2 rejected. 3. A separate cheap matcher before the lenses: a small model pass does only the matching and hands lenses the table. Lost: one more run per epic, counted in the cap of 6.
Refs: OP-10, FR-3, FR-4, FR-5, NFR-1, #29

## Q3 · OP-10 (contradiction) · 2026-10-27
Question: Matching tests to requirements by lens contradicts "per-requirement evidence is a free tool check". Which way?
Options:
1. Tool runs, lens matches (recommended)
2. Separate cheap matcher first
3. Keep it fully free
Answer: 1. Tool runs, lens matches: the tool still runs every test and lists the results for free; the conformance lens matches each requirement to the tests that prove it and raises "no evidence" findings. Lost: matching now costs model calls and can differ between runs. [human]
Patched: FR-4, FR-5, AC-4, AC-5, AC-6, NFR-1; Decisions (D-261027-b44u); retired OP-10

## Asked · Q4 · OP-9 · 2026-10-27
Question: How serious is a requirement the lens finds no passing test for?
Context: Under the jury's stop rule (#52), after the first review only blockers start new rounds; majors go to the human on one list. So this choice decides whether "unproven" stops the epic by itself or lands on your list. #29's first draft said "block on no evidence".
Options: 1. Blocker (recommended): an unproven requirement always rejects the epic and gets a fix task; nothing ships unproven. Lost: a wrong match by the lens can block a good epic until the refuter clears it. 2. Major: rejected in the first review, but in later rounds it goes on your list instead of looping. Lost: an unproven requirement can be accepted as risk and ship. 3. Blocker if the test is missing or failing, major if the lens is unsure of the match: Lost: one more rule for the lens to apply.
Refs: OP-9, FR-5, AC-5, AC-6, D-261026-r52z, #29

## Q4 · OP-9 · 2026-10-27
Question: How serious is a requirement the lens finds no passing test for?
Options:
1. Blocker (recommended)
2. Major
3. Depends on certainty
Answer: 1. Blocker: an unproven requirement always rejects the epic and gets a fix task; nothing ships unproven. Lost: if the lens matches wrongly, a good epic is blocked until the refuter clears the finding. [human]
Patched: FR-5, AC-5, AC-6; retired OP-9

## Asked · Q5 · OP-11 · 2026-10-27
Question: Which kinds of weakened tests should the tool catch by itself, for free?
Context: Deleted and skipped tests are already caught for free (per the spec). "Weakened" is fuzzier: a removed assertion, a loosened expected value, a wider tolerance. A script is free but crude; the correctness lens understands intent but costs a model call and can miss things.
Options: 1. Tool flags any edited assertion, lens judges (recommended): every changed or removed assertion line in an existing test is flagged for free, and the correctness lens says whether it really weakened the test. Lost: noisy on refactors; you read more flags. 2. Tool flags only removed assertions: less noise; loosened values and tolerances are left to the lens alone. Lost: a quietly loosened check can slip past if the lens misses it. 3. All weakening left to the lens: no script, no noise. Lost: the cheapest, surest catch becomes a model judgement.
Refs: OP-11, FR-10, AC-13, NFR-1

## Q5 · OP-11 · 2026-10-27
Question: Which kinds of weakened tests should the tool catch by itself, for free?
Options:
1. Flag any edited assertion (recommended)
2. Flag only removed assertions
3. All weakening left to the lens
Answer: 1. Flag any edited assertion: every changed or removed assertion in an existing test is flagged for free, and the correctness lens says whether the test really got weaker. Lost: noisy on refactors, so you read more flags. [human]
Patched: new FR-36, AC-43; retired OP-11

## Asked · Q6 · OP-12 · 2026-10-27
Question: Can you accept a deliberate test change, and how serious is tampering?
Context: Sometimes a test is rightly removed (the feature it tested was removed too). The spec flags tampering "whatever reason is given". Only you may accept a risk (per the jury code). Under the stop rule, blockers keep the epic looping; majors come to you on one list.
Options: 1. Major, you may accept it (recommended): tampering rejects the epic in the first review; after that it lands on your list, where you can accept a deliberate change with a reason. Lost: a bad change you accept by mistake ships. 2. Blocker, never acceptable: any tampering always rejects until the test is restored. Lost: legitimate removals need a change request to the spec first. 3. Blocker, you may accept it: always stops the epic, and you can override it with a reason. Lost: every legitimate removal costs a full extra round before you see it.
Refs: OP-12, FR-10, AC-11–AC-13, jury.py:18 (HUMAN_ONLY)

## Q6 · OP-12 · 2026-10-27
Question: Can you accept a deliberate test change, and how serious is tampering?
Options:
1. Major, you may accept (recommended)
2. Blocker, never acceptable
3. Blocker, you may override
Answer: 1. Major, you may accept: tampering rejects the epic in the first review; after that it lands on your list, where you can accept a deliberate change with a reason. Lost: a bad change you accept by mistake ships. [human]
Patched: FR-10; retired OP-12

## Asked · Q7 · OP-13 (money, multi-party) · 2026-10-27
Question: Which lenses should the money and several-parties risk flags bring in when an epic is reviewed?
Context: At the spec gate both bring in the attack-minded adversary lens (per the spec checker). This spec's trigger table leaves them out at the implementation gate, so an epic handling payments or several users' data would get only the two core lenses.
Options: 1. Adversary and security (recommended): money and several parties bring in both: abuse of payments and one party reaching another's data are attack and permission problems in code. Lost: up to 2 more runs, so such epics hit the cap of 6 sooner. 2. Adversary only, as at the spec gate: same rule everywhere. Lost: permission bugs in code that moves money or shares data rely on the core lenses. 3. Nothing extra: the core lenses cover it. Lost: the riskiest epics get the same review as the safest.
Refs: OP-13, Rules (lens a trigger adds), spec.py:19-21, FR-15

## Q7 · OP-13 (money, multi-party) · 2026-10-27
Question: Which lenses should the money and several-parties risk flags bring in when an epic is reviewed?
Options:
1. Adversary and security (recommended)
2. Adversary only
3. Nothing extra
Answer: free-form: "whats up with money? you've mentioned money mutiple times now, do not fixate on it, it's as any other request you judge te severity..." [human]
Patched: Rules (money adds no lens; judged like any other request). OP-13 narrowed to multi-party and "existing module changed".

## Asked · Q8 · OP-13 (multi-party) · 2026-10-27
Question: Should the several-parties risk flag bring in a lens when an epic is reviewed?
Context: At the spec gate it brings in the adversary lens (per the spec checker). The implementation trigger table leaves it out.
Options: 1. Same as the spec gate, adversary (recommended): one rule at both gates. Lost: one more run on those epics. 2. Security: one party reaching another's data is a permission bug. Lost: differs from the spec gate. 3. Nothing extra: the core lenses judge it. Lost: nothing looks specifically for cross-party leaks.
Refs: OP-13, Rules (lens a trigger adds), spec.py:21

## Q8 · OP-13 (multi-party) · 2026-10-27
Question: Should the several-parties risk flag bring in a lens when an epic is reviewed?
Options:
1. Adversary, as at spec (recommended)
2. Security instead
3. Nothing extra
Answer: 1. Adversary, as at spec: the same rule at both gates. Lost: one more run on those epics. [human]
Patched: Rules (multi-party → adversary); OP-13 narrowed to "existing module changed".

## Asked · Q9 · OP-13 (existing module) · 2026-10-27
Question: When does an epic count as changing existing code, so the consistency lens runs?
Context: The consistency lens checks the change against earlier decisions and the existing architecture. A spec says what it touches only loosely; the diff says exactly.
Options: 1. The diff modifies any file that existed before the epic (recommended): free to check, exact. Lost: a one-line tweak to an old file brings in a whole extra run. 2. Same, but only files outside tests and docs: fewer runs. Lost: a changed shared test helper won't bring it in. 3. Only when memory holds a decision about a touched file: runs where there's something to be consistent with. Lost: an untouched but related decision is missed.
Refs: OP-13, Rules (lens a trigger adds), #47 (consistency trigger)

## Q9 · OP-13 (existing module) · 2026-10-27
Question: When does an epic count as changing existing code, so the consistency lens runs?
Options:
1. Any pre-existing file modified (recommended)
2. Same, but not tests or docs
3. Only when memory has a related decision
Answer: 1. Any pre-existing file modified: the diff modifies any file that existed before the epic; free to check and exact. Lost: a one-line tweak to an old file brings in a whole extra run. [human]
Patched: Glossary (Existing module changed); retired OP-13

## Asked · Q10 · OP-14 · 2026-10-27
Question: When a juror asks the tool to run something, what may it ask for, and how often?
Context: Jurors only read; the tool runs code for them (decided in #29). But a juror's request is written by a model that the code under review can influence, e.g. a comment in the diff saying "run this script".
Options: 1. Only the project's tests and the spec's attacks, by name, up to 3 per round (recommended): a juror picks from a fixed list the tool already knows; nothing else ever runs. Lost: a hunch that needs a new command can't be checked automatically; it goes to you. 2. Any command, but you approve each one: full flexibility. Lost: you're interrupted every round, and approving a disguised command is on you. 3. No juror runs at all: only the tool's fixed first pass. Lost: a juror can never confirm a hunch by running something.
Refs: OP-14, FR-20, AC-26, AC-27, risk [external-input]

## Q10 · OP-14 · 2026-10-27
Question: When a juror asks the tool to run something, what may it ask for, and how often?
Options:
1. Known tests/attacks, ≤3 per round (recommended)
2. Any command, you approve each
3. No juror run requests
Answer: 1. Known tests/attacks, ≤3 per round: a juror picks, by name, from the project's tests and the spec's attacks, up to 3 per round; nothing else ever runs. Lost: a hunch that needs a new command can't be checked automatically, so it goes to you. [human]
Patched: FR-20, new AC-44, AC-45; retired OP-14

## Derived · Risks (run requests) · 2026-10-27
From: FR-20. The run-request risk is now bounded: a steered request can at worst pick the wrong named test.

## Asked · Q11 · OP-15 · 2026-10-27
Question: When you choose "fix" for an item on your end-of-review list, who makes the fix?
Context: Under the stop rule, majors and minors that weren't fixed go to you on one list; for each you choose fix or accept. At the spec gate you or the agent edit the spec directly. Here the fix is code.
Options: 1. It becomes a fix task, implemented by the implement stage, then the one final fix check (recommended): code only ever changes through tasks, and the check reviews it. Lost: a small fix still takes a task round trip. 2. You fix the code yourself, then the final fix check: fastest for small fixes. Lost: code changes outside the task trail, so the epic's history doesn't show them. 3. You choose per item: flexible. Lost: two paths to build and test.
Refs: OP-15, FR-26, FR-32, AC-40, D-261026-r52z

## Q11 · OP-15 · 2026-10-27
Question: When you choose "fix" for an item on your end-of-review list, who makes the fix?
Options:
1. Fix task, then final check (recommended)
2. You fix it, then final check
3. You choose per item
Answer: 1. Fix task, then final check: it becomes a fix task for the implement stage, followed by the one final fix check; code only ever changes through tasks, and the check reviews it. Lost: even a small fix takes a task round trip. [human]
Patched: new FR-37, AC-46; retired OP-15

## Asked · Q12 · OP-16 · 2026-10-27
Question: When the tool spots a possible stub (an empty function, a lone TODO) or can't tell if something is finished, what happens to it?
Context: These are flagged by script, "when in doubt, flag" (per #29). Findings in the ledger have a severity and need a decision; a hint in the pack only steers the lenses.
Options: 1. Hint to the lenses, which decide (recommended): the flag goes into every pack; a lens that confirms it raises a real finding with a severity. Lost: if every lens ignores the hint, it disappears. 2. Finding at minor: always recorded and shown in the verdict. Lost: false positives (abstract methods, dynamic calls) pile up as noise. 3. Finding at major: always reaches you. Lost: every false positive costs you a decision.
Refs: OP-16, FR-9, FR-13, AC-10, AC-16

## Q12 · OP-16 · 2026-10-27
Question: When the tool spots a possible stub or can't tell whether something is finished, what happens to it?
Options:
1. Hint; lenses decide (recommended)
2. Finding at minor
3. Finding at major
Answer: 1. Hint; lenses decide: the flag goes into every juror's pack, and a lens that confirms it raises a real finding with a severity. Lost: if every lens ignores the hint, it disappears. [human]
Patched: FR-9, FR-13, AC-10, AC-16; retired OP-16

## Asked · Q13 · OP-17 · 2026-10-27
Question: When a review finds problems, how are they grouped into fix tasks?
Context: Fix tasks are appended to the epic and never rewrite old ones (per #29). Several findings often hit the same file or task.
Options: 1. One fix task per finding (recommended): each task cites exactly one finding, so the re-review checks each fix against its own finding. Lost: more, smaller tasks; one file may be touched by several. 2. One per original task the findings touch: fewer tasks, mirrors the epic. Lost: a task mixes several findings, so the re-review is harder to read. 3. One per file: fewest tasks. Lost: a finding spanning files is split, and findings about missing code have no file.
Refs: OP-17, FR-26, FR-27, D-261026-r52z

## Q13 · OP-17 · 2026-10-27
Question: When a review finds problems, how are they grouped into fix tasks?
Options:
1. One per finding (recommended)
2. One per original task
3. One per file
Answer: 1. One per finding: each task cites exactly one finding, so the re-review checks each fix against its own finding. Lost: more, smaller tasks, and one file may be touched by several of them. [human]
Patched: FR-26; retired OP-17

## Call · AC-27 · 2026-10-27
A run a juror asked for that can't start is reported in the next packs as "couldn't run" with the error. [agent]
Below the bar: changes what a user can do: no; sees: no (only jurors read packs); who may: no; data kept: no; cost: no.

## Derived · AC-2, AC-17, AC-39, FR-33, Verdict record, SC-1, SC-2, Risks (broad flags), state table rows implemented / with human / approved · 2026-10-27
From: FR-1, FR-2, FR-3, FR-4, FR-5, FR-25, FR-27, FR-32, FR-36, FR-37, RF-20. The "with human" row splits "human settles" into two events: any item chosen as fix → implementing (FR-37); all accepted → approved (FR-32, the #52 stop rule).

## Finish gate · 2026-10-27
`nio check spec --gate`: 0 errors. Fidelity re-read of FR-4, FR-5, FR-9, FR-10, FR-13, FR-20, FR-26, FR-36, FR-37 against Q2–Q13: numbers (≤3 runs, severities blocker/major) and negatives (no spec IDs in tests, never runs other commands, code never changes outside a task) match the answers.
Human chose: finish. Next stage: spec jury.

## Session 2 · 2026-10-27 · jury round 1 findings that change behaviour, the human answers

## Asked · Q14 · J-1 · 2026-10-27
Question: How do we stop a fake test (right name, checks nothing) from counting as proof?
Context: The conformance lens matches tests to requirements by name and description (your earlier answer). A new test named for a requirement whose body only does `assert True` passes and counts as proof. The edited-assertion check only looks at tests that already existed.
Options: 1. Lens reads the body, tool hints empty tests (recommended): the lens must confirm the test body really exercises the requirement; the tool adds a free hint for any test with no assertion. Lost: a little more reading per match. 2. Lens reads the body only: no extra tool check. Lost: relies on the lens alone to notice. 3. Accept the gap: names are trusted. Lost: a fake test ships an unproven requirement.
Refs: J-1, FR-4, FR-9, AC-4, SC-1

## Q14 · J-1 · 2026-10-27
Question: How do we stop a fake test (right name, but it checks nothing) from counting as proof?
Options:
1. Lens reads body + hint (recommended)
2. Lens reads the body only
3. Accept the gap
Answer: 1. Lens reads body + hint: the lens must confirm the test body really exercises the requirement, and the tool adds a free hint for any test with no assertion. Lost: a little more reading per match. [human]
Patched: FR-4, NFR-1, new FR-39, AC-51

## Asked · Q15 · J-3, J-21 · 2026-10-27
Question: What limits apply when the tool runs the epic's tests, checks and attacks?
Context: The tool runs the epic's own code, which may be buggy or hostile: a hung test leaves the epic stuck in review; nothing bounds time, output size or what an attack may touch. It's also unstated whether a failed lint or type check becomes a finding.
Options: 1. Timeout, output cap, throwaway copy; failed checks become findings (recommended): each run gets a time limit (default 10 minutes, set in config) and an output cap; runs happen in a throwaway copy of the repo at the epic's commit; a run that times out counts as failed; a failed lint or type check becomes a major finding. Lost: no network isolation, so an attack could still reach the network. 2. Same, plus no network: safer. Lost: needs per-OS sandboxing; tests that need the network fail. 3. Timeout and output cap only, in the working tree: simplest. Lost: a destructive test can damage your working copy.
Refs: J-3, J-21, FR-3, FR-11, FR-12, FR-20, AC-17

## Q15 · J-3, J-21 · 2026-10-27
Question: What limits apply when the tool runs the epic's tests, checks and attacks?
Options:
1. Limits + throwaway copy (recommended)
2. Same, plus no network
3. Time and output limits only
Answer: 1. Limits + throwaway copy: each run gets a time limit (10 minutes by default, set in config) and an output cap, inside a throwaway copy of the repo at the epic's commit; a timeout counts as a failure, and a failed lint or type check becomes a major finding. Lost: no network isolation, so an attack could still reach the network. [human]
Patched: new FR-40, FR-42, AC-52, AC-53, AC-54; Risks (no network isolation); NFR-1

## Call · FR-41, AC-55 · 2026-10-27
Output cap: 200 KB per run, keeping the first and last 100 KB. [agent] Below the bar: only jurors read run output; what a user can do, sees, who may, data kept: no; cost: bounds it.

## Asked · Q16 · J-5, J-11 (minors) · 2026-10-27
Question: When an epic is rejected, do its minor findings get fix tasks too?
Context: The spec jury, which this gate copies, treats every open finding the same in the first review: any open one, minors included, means rejected and must be dealt with (per the jury code). But the spec also says two minors alone end approved, with the minors listed. These disagree.
Options: 1. Minors never block and never get tasks (recommended): minors are listed in the verdict; only blockers and majors reject and get fix tasks. Lost: differs from the spec gate, where minors are fixed too; small issues may pile up. 2. Minors get tasks only when the epic is rejected anyway: they ride along with a real rejection; minors alone still approve. Lost: more tasks per rejection. 3. Same as the spec gate: any open minor rejects and gets a task. Lost: an epic can bounce on a typo-level issue.
Refs: J-5, J-11, FR-26, FR-31, AC-37, jury.py compose

## Q16 · J-5, J-11 (minors) · 2026-10-27
Question: When an epic is rejected, do its minor findings get fix tasks too?
Options:
1. Minors never block (recommended)
2. Minors ride along
3. Same as the spec gate
Answer: 1. Minors never block: minors are listed in the verdict; only blockers and majors reject the epic and get fix tasks. Lost: this differs from the spec gate, where minors are fixed too, so small issues may pile up. [human]
Patched: FR-26, FR-32, new FR-43, AC-56, Decisions

## Asked · Q17 · J-12, J-18 · 2026-10-27
Question: When a test's assertion is removed or changed, who decides it's tampering?
Context: Two rules overlap: one says a weakened test is major tampering whatever the reason; the other (your answer earlier) flags every edited assertion for free and lets the correctness lens judge whether the test got weaker. If the lens says "not weaker", the rules disagree.
Options: 1. Deleted and skipped are always tampering; edited assertions are tampering only if the lens says weaker (recommended): the free checks stay exact; the lens settles the fuzzy case, and a confirmed weakening is major like any tampering. Lost: a lens that misjudges lets a weakened assertion through. 2. Any removed assertion is always tampering; only changed values go to the lens: removal is never cleared. Lost: legit refactors that drop a redundant assertion always land on your list. 3. Every edited assertion is tampering until you accept it: nothing cleared without you. Lost: every refactor of a test costs you a decision.
Refs: J-12, J-18, FR-10, FR-36, AC-11–AC-13, AC-43

## Q17 · J-12, J-18 · 2026-10-27
Question: When a test's assertion is removed or changed, who decides it's tampering?
Options:
1. Lens settles edits (recommended)
2. Removal always tampering
3. You decide every edit
Answer: 1. Lens settles edits: deleted and skipped tests are always tampering; an edited or removed assertion is tampering only if the lens says the test got weaker, and then it's major like any tampering. Lost: a lens that misjudges lets a weakened assertion through. [human]
Patched: FR-10, FR-36, AC-11, AC-12, AC-13, new AC-57, Glossary (Test tampering)

## Asked · Q18 · J-14 · 2026-10-27
Question: What happens when an epic is rejected only because the spec is wrong (the code is right)?
Context: Then the finding becomes a change request, not a fix task, so the epic goes back to be implemented with nothing to do, and the gate can't restart. It's also unstated what happens if you reject the change request.
Options: 1. The epic waits for your ruling on the change request (recommended): accepted → the spec is updated through its own flow and the finding is settled; rejected → the finding becomes a fix task (the code must match the spec after all). Lost: the epic is held until you rule. 2. The finding is approved as a note, the change request follows on its own: the epic isn't held. Lost: the epic ships while its spec is known to be wrong. 3. Treat it as a fix task right away: always change the code to match the spec. Lost: correct code gets changed to match a stale spec.
Refs: J-14, FR-26, FR-30, UJ-3, state table row "in jury"

## Q18 · J-14 · 2026-10-27
Question: What happens when an epic is rejected only because the spec is wrong (the code is right)?
Options:
1. Wait for your ruling (recommended)
2. Approve, request follows
3. Always fix the code
Answer: 1. Wait for your ruling: the epic waits for your ruling on the change request; accepted, the spec is updated through its own flow and the finding is settled; rejected, the finding becomes a fix task, since the code must match the spec after all. Lost: the epic is held until you rule. [human]
Patched: new FR-44, AC-58, AC-59; state table (new state "waiting on change", columns for its events)

## Asked · Q19 · J-16 · 2026-10-27
Question: Should changing permission checks or handling secrets bring in the security lens, even without the auth or personal-data flags?
Context: Your first draft of this gate listed security for auth, permissions, secrets and personal data. The spec only maps the auth and personal-data flags; there's no flag for permissions or secrets, so an epic touching them gets no security review.
Options: 1. Fold them into the auth flag (recommended): the auth flag's meaning widens to "auth, permissions or secrets", which the grill confirms with you per spec. No new flag. Lost: one flag covers more ground, so it's set more often. 2. Add a new risk flag "secrets": a separate flag for secrets; permissions stay under auth. Lost: one more flag every spec must consider. 3. Leave as is: security for auth and personal data only. Lost: secrets handling may go without a security review.
Refs: J-16, FR-15, Rules (lens a trigger adds), intake (#29 draft row)

## Q19 · J-16 · 2026-10-27
Question: Should changing permission checks or handling secrets bring in the security lens, even without the auth or personal-data flags?
Options:
1. Fold into the auth flag (recommended)
2. New 'secrets' flag
3. Leave as is
Answer: 2. New 'secrets' flag: a separate flag for secrets, while permissions stay under auth. Lost: one more flag every spec must consider. [human]
Patched: new FR-45, AC-60; Rules (secrets → security)

## Call · FR-46, AC-61 · 2026-10-27
The new `secrets` flag also brings in security at the spec gate, as auth does. [agent] Shown to the human for overturn: it adds a security run at the spec gate for specs that set it (cost).

## Asked · Q20 · J-19 · 2026-10-27
Question: When an epic's planned reviews go over the cap, what "cost" do you see, and how is "drop the least useful" decided with no history?
Context: The over-cap choice shows each review's cost and offers to drop the lowest-hit-rate reviews, but NIO records no hit rates and has no cost estimate yet (per research), and a first epic has no history.
Options: 1. Show runs and model tier as the cost; offer "drop" only once hit rates exist (recommended): you see each planned review with its model tier (cheap, medium, strong); until hit rates are recorded the choice is run all or pick. Lost: no token or money estimate until usage tracking exists. 2. Estimate tokens per review from pack size: a number per review. Lost: a rough estimate that needs building now. 3. Drop the cost and hit-rate parts: just run all or pick. Lost: you choose without any cost signal.
Refs: J-19, FR-16, AC-22, AC-23, RF-8, RF-9

## Q20 · J-19 · 2026-10-27
Question: When an epic's planned reviews go over the cap, what "cost" do you see, and how is "drop the least useful" decided with no history?
Options:
1. Tier as cost; drop later (recommended)
2. Estimate tokens
3. No cost, no drop
Answer: 1. Tier as cost; drop later: you see each planned review with its model tier (cheap, medium, strong); until hit rates are recorded, the choice is run all or pick. Lost: no token or money estimate until usage tracking exists. [human]
Patched: FR-16, AC-22, AC-23, UJ-4

## Asked · Q21 · J-9, J-22–J-25 · 2026-10-27
Question: How should the jury treat the four points waiting on other issues, and the not-yet-committed "no spec IDs in tests" decision?
Context: Four points were deferred in the grill because the tasks stage, implement stage, attack scripts and test-command design aren't decided (#42, #43, #38, #48, #49). Only you may accept something as a known risk. Separately, the "tests carry no spec IDs" decision is saved in memory but not yet committed.
Options: 1. Accept the four as known risks, commit the decision with the spec (recommended): the spec can be approved now, with the four marked as waiting on those issues; nothing gets built until they settle; the memory decision is committed together with the spec when you ask for a commit. Lost: the approved spec has four known holes. 2. Hold approval until those issues settle: no holes. Lost: this spec waits on four other designs. 3. Mark them out of scope for this spec: they're handled entirely in those issues. Lost: this spec stops tracking them, so nothing reminds you to come back.
Refs: J-9, J-22, J-23, J-24, J-25, DF-1–DF-4, D-261027-b44u

## Q21 · J-9, J-22–J-25 · 2026-10-27
Question: How should the jury treat the four points waiting on other issues, and the not-yet-committed "no spec IDs in tests" decision?
Options:
1. Accept as risks, commit later (recommended)
2. Hold approval
3. Mark out of scope
Answer: 1. Accept as risks, commit later: the spec can be approved now, with the four marked as waiting on those issues; nothing gets built until they settle; the memory decision is committed with the spec when you ask for a commit. Lost: the approved spec has four known holes. [human]
Patched: none (jury dispositions accepted-risk by the human)

Session (2026-10-30): the plan's questions that nothing upstream settled.

## Q22 · epic order · 2026-10-30
Question: When an epic's tasks are finished, should work on the next epic wait for that epic's check to finish?
Answer: 1. Wait for the check: `nio flow claim` refuses the next epic until the check is approved or the human closes it. [human]
Patched: architecture.md

## Q23 · lint and type-check commands · 2026-10-30
Question: What should the epic check do when a project hasn't named a lint or type-check command?
Answer: 1. Note it and go on: an unset command is reported to the human and shown to every reviewer as not configured, and the check continues. [human]
Patched: architecture.md

## Q24 · architecture note · 2026-10-30
Question: Approve the architecture note for the implementation jury?
Answer: 1. Approve: the plan builds on it, and the plan jury checks the plan against it. [human]
Patched: architecture.md approved; plan.md architecture: approved

Session (2026-10-30): the plan jury's questions the spec didn't settle.

## Q25 · the CLI's own findings · 2026-10-30
Question: Should a finding that NIO's own checks made (a deleted test, a missing file, a failed lint) also go through the checker that tries to disprove findings?
Answer: 1. Skip checker: NIO's own findings go straight to the record as confirmed, and a deleted test can't be dismissed by a model. [human]
Patched: spec.md FR-24; contracts.md CT-20

## Q26 · which side is right · 2026-10-30
Question: When a reviewer says the code and the spec disagree, who decides which one is right?
Answer: 1. Reviewer says, default spec: the reviewer states it and the checker tests the claim; if it says nothing, the spec wins and a fix task is written. [human]
Patched: contracts.md CT-12, CT-14, CT-15

## Q27 · where tests run · 2026-10-30
Question: Where should the epic's tests and attacks run, given a linked git worktree was approved earlier?
Answer: 1. Local clone: a separate clone at the epic's commit in a temp folder, deleted after the run. [human]
Patched: architecture.md; contracts.md CT-2

## Q28 · epics already skipped · 2026-10-30
Question: What should happen to epics the implement stage already closed as skipped?
Answer: 1. Stay closed, say so: `nio flow next` names the epics that were never reviewed. [human]
Patched: architecture.md; contracts.md CT-17

## Q29 · a new problem in a re-review · 2026-10-30
Question: If a re-review of an epic's code finds a new serious problem, and nothing else is open, what should happen?
Answer: 1. Comes to you: the epic waits for the human's ruling, fix it or accept the risk. [human]
Patched: spec.md FR-32; contracts.md CT-13

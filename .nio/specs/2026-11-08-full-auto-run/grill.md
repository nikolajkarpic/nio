# Grill: 2026-11-08-full-auto-run

Session 1 (2026-11-08): answered by the human, in rounds. Facts researched first.

## Lookup · OP-1, OP-10, OP-11, OP-12, OP-13 · 2026-11-08
Found: RF-1 to RF-5. Patched UJ-1, FR-13. Retired OP-1, OP-10, OP-12, OP-13. RF-3 contradicts FR-27's default ("the way the skills already do"): it is the round's first question. OP-11 stays open under that question.

## Asked · Q1 · FR-27; contradiction · 2026-11-08
Question: How should the driver wait on a long jury or test run the host has moved to the background?
Context: I set this default saying the skills already know how. Research shows they don't: issue #85 is still open, and orchestrators improvise wait loops that cost turns.
Options: 1. The driver skill states the rule itself: start long commands in the background, wait for the completion notice, never poll (recommended). Fixes it for auto runs, #85 stays open for manual runs. 2. Fold #85 in: also add the rule to the implement and jury skills. Fixes both, a slightly bigger spec. 3. Leave it to each host. Nothing to write, but auto runs burn turns or stall.
Refs: FR-27, AC-10 · RF-3 · #85

## Asked · Q2 · OP-2 · 2026-11-08
Question: Who may switch an effort to auto?
Context: Auto means the jury approves gates in your place and the run commits to the repo without asking. Today only the human may approve a gate, and a hand-edited auto flag is refused.
Options: 1. Only you, with a command that carries --by human (recommended). An agent can't grant itself autonomy; an orchestrator you asked has to hand you the command. 2. You, or an orchestrator you delegated to in the session, recorded as delegated. Fewer hand-offs, but an agent's word that you asked is the only proof. 3. Any agent. Fully hands-off, but nothing stops a run from granting itself.
Refs: OP-2 · FR-1, FR-3 · flow-state AC-58

## Asked · Q3 · OP-3 · 2026-11-08
Question: Besides when the spec draft is written, can you switch auto on at a later stage too?
Context: You chose to grant it when the spec is written. The same start command could just as well work at plan or tasks, for an effort you began by hand.
Options: 1. Yes, at any stage from the draft on (recommended). You can review the spec by hand, then let the rest run. Costs nothing extra, one rule. 2. Only when the draft is written. One entry point, but a hand-started effort can never go auto. 3. Only at the draft or right after a human-approved gate. More precise, but more rules to test.
Refs: OP-3 · FR-1, FR-2

## Asked · Q4 · OP-4 · 2026-11-08
Question: Can you switch auto off during a run, and what happens to a fix already under way?
Context: Without an off switch, the only way to take back control is to abandon or park the effort.
Options: 1. Yes, with a command. A fix under way finishes its edits, then the next round waits for you (recommended). You regain control within one step and never get half-edited files. 2. Yes, and it stops at once, even mid-fix. Fastest, but it can leave half-edited files to clean up. 3. No off switch; park the effort instead. Nothing new, but parking loses the auto grant's meaning.
Refs: OP-4 · FR-26

## Asked · Q5 · OP-5 · 2026-11-08
Question: Should a `nio:auto` label on a GitHub issue also switch an effort to auto?
Context: The earlier flow spec mentioned the label as one possible switch. You picked the command when the spec is written.
Options: 1. Drop it (recommended). One way to grant: the command, which history records. 2. Keep it as a second way. Handy from GitHub, but anyone who can label the issue grants autonomy. 3. Keep it only as a marker that shows on the issue, without granting. Visible on GitHub, but one more thing to keep in sync.
Refs: OP-5 · FR-1

## Asked · Q6 · OP-6 · 2026-11-08
Question: Before the tasks exist, how many jury rounds may the spec, plan and tasks gates spend together?
Context: You chose 2 rounds per gate, counted once the tasks are known. Before that, the number of epics is unknown.
Options: 1. 6: 2 per gate for those 3 gates, then 2 per epic is added once the tasks exist (recommended). Same rule as yours, applied early. 2. No cap until the tasks exist; each gate's own 3-round limit stops it. Never stops early, but can spend up to 9. 3. A fixed 4. Cheapest, but one hard spec can use it all up.
Refs: OP-6 · FR-18, AC-25

## Asked · Q7 · OP-7 · 2026-11-08
Question: Should auto also cap how many subagents one run may start?
Context: Jury rounds are the costly part, and you already capped those. Workers, fixers and stage subagents add up too, and the earlier flow spec reserved a budgets.subagents setting.
Options: 1. No default cap; you can set one in config (recommended). The jury cap and the stuck check stop runaway runs, so a big effort never stops just for being big. 2. 3 per task plus 2 per gate. Bounds cost, but a large effort may stop near the end. 3. A fixed 50. Simple, but wrong for both small and large efforts.
Refs: OP-7 · FR-18, flow-state FR-40

## Asked · Q8 · OP-8 · 2026-11-08
Question: How does a gate close under auto when the jury leaves minors, refuted findings or final-check warnings that today only you can accept as risk?
Context: Today you accept those by hand. With auto on, nobody is there, so either the grant counts as acceptance or every gate waits for you.
Options: 1. Minors and refuted findings are accepted and listed in the report. A final-check warning that a fix didn't hold pauses for you (recommended). Runs finish, and real unresolved problems still come to you. 2. Everything left over is accepted and listed. Never stops, but an unfixed confirmed problem can reach the PR. 3. Any leftover pauses for you. Safest, but most gates will stop.
Refs: OP-8 · FR-17 · decision table: Fixer action

## Asked · Q9 · OP-9 · 2026-11-08
Question: Should auto also drive bug fixes on the lite route?
Context: The lite route has fewer stages (spec, grill, tasks, tasks jury, implementation, its jury), and the same flow engine runs it.
Options: 1. Yes, same driver, fewer stages (recommended). Small fixes go hands-off too, at no extra cost. 2. Full route only. Small fixes keep a human at every gate, which costs you time on the cheapest work. 3. Lite only at first. Tests auto mode on small risk first, but the big efforts you asked for wait.
Refs: OP-9 · FR-5 · D-261107-7egd
## Q1 · FR-27 · 2026-11-08
Question: see `## Asked · Q1`
Options: as asked; option 1 recommended
Answer: 1. The driver skill states the rule itself: start long commands in the background, wait for the completion notice, never poll; #85 stays open for manual runs. [human]
Patched: FR-27, AC-10; retired OP-11

## Q2 · OP-2 · 2026-11-08
Question: see `## Asked · Q2`
Options: as asked; option 1 recommended
Answer: 1. Only the human, with a command carrying --by human; an agent can't grant itself autonomy, an orchestrator has to hand the human the command. [human]
Patched: FR-1; added FR-30, AC-29; retired OP-2

## Q3 · OP-3 · 2026-11-08
Question: see `## Asked · Q3`
Options: as asked; option 1 recommended
Answer: 1. Yes, at any stage from the draft on; the human can review the spec by hand and let the rest run. [human]
Patched: added FR-31, AC-30; retired OP-3

## Q4 · OP-4 · 2026-11-08
Question: see `## Asked · Q4`
Options: as asked; option 1 recommended
Answer: 1. Yes, with a command; a fix under way finishes its edits, then the next round waits for the human. [human]
Patched: added FR-32, AC-31, state table column `switched off`; retired OP-4

## Q5 · OP-5 · 2026-11-08
Question: see `## Asked · Q5`
Options: as asked; option 1 recommended
Answer: 1. Drop the nio:auto label; one way to grant: the command, recorded in history. [human]
Patched: added non-goal; retired OP-5

## Q6 · OP-6 · 2026-11-08
Question: see `## Asked · Q6`
Options: as asked; option 1 recommended
Answer: 1. 6 (2 per gate for spec, plan, tasks), then 2 per epic added once the tasks exist. [human]
Patched: FR-18; added AC-32; retired OP-6

## Q7 · OP-7 · 2026-11-08
Question: see `## Asked · Q7`
Options: as asked; option 1 recommended
Answer: 1. No default subagent cap; config can set one. The jury cap and the stuck check stop runaway runs. [human]
Patched: added FR-33, AC-33; retired OP-7

## Q8 · OP-8 · 2026-11-08
Question: see `## Asked · Q8`
Options: as asked; option 1 recommended
Answer: 1. Minors and refuted findings are accepted and listed in the report; a final-check warning that a fix didn't hold pauses for the human. [human]
Patched: FR-17, AC-21, decision table rows refuted/minor; added FR-34, AC-34; retired OP-8

## Q9 · OP-9 · 2026-11-08
Question: see `## Asked · Q9`
Options: as asked; option 1 recommended
Answer: 1. Yes, auto drives the lite route too: same driver, fewer stages. [human]
Patched: added FR-35, AC-35; retired OP-9

## Call · A-4, FR-25, FR-29, NFR-2, state table rows, non-goal CLI loop, risk line · 2026-11-08
Each is below the bar: it changes none of (1) what a user can do, (2) what a user sees, (3) who may do it, (4) what data is kept or changed, (5) what it costs, beyond what an answered item already fixes. A-4 restates the jury as today. FR-25 follows the "Talking to the human" block. FR-29 guards against two drivers on one effort; RF-5 shows the lock doesn't do it today, so it must be built. NFR-2 follows D-261028-4kji: the stage is derived from files, so a new driver resumes from `nio flow next`. The state table restates FR-1, FR-20, FR-32 and the flow-state stop list. The CLI loop non-goal is a how. The risk line names a known residual risk. [agent]

## Derived · UJ-2, AC-3, AC-5, AC-8, AC-9, AC-11, AC-15, AC-28, FR-4, FR-8, FR-12, FR-26, SC-1, SC-2, non-goals stop list and notify · 2026-11-08
FR-4 from FR-31 (a draft failing its check hasn't ended drafting). FR-8 from FR-7, AC-16. FR-12 from FR-10 (it checks the same rule after the round). FR-26 from FR-32 (only the explicit switch turns auto off). SC-1 from FR-5, FR-20. SC-2 from FR-22. The ACs follow their FRs. The stop-list non-goal from FR-28, the notify non-goal from FR-22.

## Asked · Q10 · FR-14 · 2026-11-08
Question: If you switch auto off, what happens to the defaults the run chose for you?
Context: Under auto, open points become [auto] defaults that only the jury checked. Once you take control back, the spec gate today refuses any unconfirmed default.
Options: 1. They count as unconfirmed: the spec gate refuses them until you confirm each (recommended). You review every choice made without you, at the cost of a few questions. 2. They stay accepted, since the jury judged them. No extra questions, but choices you never saw stay in force. 3. They're dropped and become open points again. Clean, but the jury's work on them is lost.
Refs: FR-14, AC-17, AC-18, FR-32

## Asked · Q11 · FR-23 · 2026-11-08
Question: Should the PR report link every auto approval, fix and default to the record that allowed it?
Context: NORTH_STAR asks that you can read why every autonomous decision was allowed. Linking costs a longer PR body.
Options: 1. Yes, each item names its verdict or history line (recommended). Every decision is traceable in one click, the body runs longer. 2. Only approvals and fixes, not defaults. Shorter, but the defaults (most likely to surprise you) are untraced. 3. No links, a plain summary. Shortest, but checking a decision means digging through files.
Refs: FR-23, SC-2, AC-23

## Asked · Q12 · FR-24 · 2026-11-08
Question: If the run reaches the end but can't open the PR (no remote, no GitHub login), what then?
Context: The work is committed on its own branch either way. Nothing is merged.
Options: 1. Pause for you and print the full report (recommended). You open the PR yourself with the report in hand; nothing is lost. 2. Mark the effort done anyway and leave the report in a file. Finishes cleanly, but you may not notice there's no PR. 3. Retry a few times, then pause. Recovers from a blip, but slower to tell you about a real problem.
Refs: FR-24, AC-24, RF-4

## Asked · Q13 · NFR-1 · 2026-11-08
Question: How much may the driver's own conversation grow per stage?
Context: The driver runs every stage of a long effort in one session; each stage runs in a subagent and only its summary comes back. A tight limit keeps a long run from filling its context and losing track; the cost is terser hand-backs.
Options: 1. At most about 3,000 tokens per stage (recommended). A 10-epic run stays well inside one session. 2. No limit, rely on the host compacting the conversation. Richer hand-backs, but compaction can drop where the run stands. 3. At most about 1,000 tokens. Lean, but hand-backs may drop what the next stage needs.
Refs: NFR-1, FR-6

## Q10 · FR-14 · 2026-11-08
Question: see `## Asked · Q10`
Options: 1. count as unconfirmed (recommended) 2. stay accepted 3. dropped, reopened
Answer: 2. Stay accepted: the jury judged them, so they stay when auto is switched off; no extra questions, but choices the human never saw stay in force. [human]
Patched: FR-14, AC-17, AC-18; FR-8 now also settles `[default]` items under auto (derived)

## Q11 · FR-23 · 2026-11-08
Question: see `## Asked · Q11`
Options: 1. link everything (recommended) 2. approvals and fixes only 3. no links
Answer: 1. Link everything: each item names the verdict or history line behind it. [human]
Patched: FR-23

## Q12 · FR-24 · 2026-11-08
Question: see `## Asked · Q12`
Options: 1. pause, print report (recommended) 2. done, report in a file 3. retry, then pause
Answer: 1. Pause for the human and print the full report; the human opens the PR; nothing is lost. [human]
Patched: FR-24, AC-24

## Q13 · NFR-1 · 2026-11-08
Question: see `## Asked · Q13`
Options: 1. ~3,000 tokens per stage (recommended) 2. no limit 3. ~1,000 tokens per stage
Answer: 2. No limit: rely on the host compacting the conversation; richer hand-backs, at the risk that compaction drops where the run stands. [human]
Patched: removed NFR-1 (retired)

## Finish · 2026-11-08
Fidelity: re-read FR-1, FR-14, FR-17, FR-18, FR-23, FR-24, FR-27, FR-30 to FR-35 against Q1 to Q13; none drifted. Passivity: the human overrode the recommendation on Q10 and Q13. Notes shown (agent calls and derived items). Answer: finish. [human]

Session 2 (2026-11-08): spec jury round 1 findings that change behaviour, asked in one round.

## Asked · Q14 · J-1, J-14 · 2026-11-08
Question: How is a grant proven to be yours, when any agent can type `--by human`?
Context: The jury points out that the human-only rule rests on a label anyone can write. Gate approval with --commit already rests on the same label today, and the history records the host and model of every call.
Options: 1. Same trust as gate approvals: skills forbid an agent from writing --by human, the history line records who ran it, and the spec names this as a known limit (recommended). Nothing new to build; a rogue agent could still lie, and you'd see it in history. 2. The grant asks for a typed confirmation in an interactive terminal. Stops casual misuse, but an agent driving a terminal can still answer it, and it breaks scripted use. 3. The grant must be a commit you sign. Strong proof, but needs signing set up on every machine.
Refs: J-1, J-14 · FR-1, FR-2, FR-30 · src/nio/flow.py:983

## Asked · Q15 · J-2 · 2026-11-08
Question: What if a fix edits the spec's risk flags (money, auth, migration, data deletion)?
Context: Those flags make every gate wait for you. Nothing stops the fixer from removing one, which would silently turn off that stop.
Options: 1. Any change to the risk flags pauses for you, like a change to your own lines (recommended). One small check, closes the hole. 2. The run keeps reading the flags as they were when you granted auto; later edits count only after you approve. Same safety, a little more to build. 3. Nothing; trust the jury to catch it. Nothing to build, but the stop can vanish unnoticed.
Refs: J-2 · FR-10, FR-12, FR-28

## Asked · Q16 · J-3, J-17 · 2026-11-08
Question: How does a second driver tell a running driver from a dead one?
Context: The spec says a second driver is refused, and also that a new driver takes over after a crash. Without a rule, a crash can lock the effort forever, or two drivers can run at once. The flow lock already treats a lock as dead when its process is gone, or when it's from another machine and over a minute old.
Options: 1. A driver holds a claim naming its process and machine, refreshed each stage; it's dead when its process is gone, or it is older than 30 minutes (recommended). Same rule as the flow lock, and a crash frees the effort within 30 minutes at worst. 2. Same claim, but only you can clear a stale one. No accidental takeover, but every crash waits for you. 3. Drop the one-driver rule; the flow lock already stops two calls writing at once. Nothing to build, but two drivers can each run a jury round, paying twice.
Refs: J-3, J-17 · FR-29, NFR-2, AC-9, AC-11 · RF-5

## Asked · Q17 · J-4 · 2026-11-08
Question: What if the refuter crashes or returns nothing for a finding?
Context: Under auto, refuted findings are accepted as risk. A refuter that fails silently could look like "not confirmed" and wave a blocker through.
Options: 1. No verdict pauses for you; a refuted blocker is accepted but listed first in the report (recommended). Silent failure can't pass anything, and serious rejections stand out. 2. No verdict pauses, and a refuted blocker also pauses. Safer, but blockers the refuter rightly threw out still stop the run. 3. No verdict means rerun the refuter once, then pause. Rides out a blip, slightly slower to stop.
Refs: J-4 · FR-17 · decision table: Fixer action

## Asked · Q18 · J-5 · 2026-11-08
Question: What counts as cutting scope, the thing the fixer must stop for?
Context: Right now the fixer decides for itself. The jury asks for a rule that a check can apply.
Options: 1. Any requirement, acceptance criterion or story removed, or anything added to the non-goals, compared with the previous round (recommended). A check catches it, the same way it catches edits to your lines; a loosened wording isn't caught. 2. Option 1 plus any number made looser or "must" softened to "may", judged by the refuter. Catches softening too, but rests on a model's judgement. 3. Leave it to the fixer. Nothing to build, but it marks its own homework.
Refs: J-5 · FR-11, AC-14

## Asked · Q19 · J-11 · 2026-11-08
Question: When you resume a run that stopped at its jury cap or got stuck, what does it get?
Context: Today, resuming hits the same limit again at once, so you'd have to edit the config.
Options: 1. Resuming gives the stopped gate a fresh allowance of 2 rounds; the effort's total cap goes up by 2 (recommended). One command to continue, and every extra round is one you allowed. 2. Resuming needs you to raise budgets.juries first. Explicit, but one more step every time. 3. Resuming clears the cap entirely. Never stops again, but a bad run can then burn unlimited rounds.
Refs: J-11 · FR-18, FR-26, AC-8 · flow-state FR-40, FR-41

## Q14 · J-1, J-14 · 2026-11-08
Answer: 1. Same trust as gate approvals: skills forbid an agent from writing --by human, the history records who ran it, and the spec names it as a known limit. [human]
Patched: FR-30, Risks; added AC-42

## Q15 · J-2 · 2026-11-08
Answer: 1. Any change to the risk flags pauses for the human, like a change to their own lines. [human]
Patched: added FR-36, AC-36

## Q16 · J-3, J-17 · 2026-11-08
Answer: 1. A driver claim naming its process and machine, refreshed each stage; dead when its process is gone or older than 30 minutes. FR-29 kept, now confirmed. [human]
Patched: FR-29 ([human]); added FR-38, AC-38

## Q17 · J-4 · 2026-11-08
Answer: 1. No refuter verdict pauses for the human; a refuted blocker is accepted but listed first in the report. [human]
Patched: decision table (refuter `none` rows, refuted blocker listed first); added FR-39, AC-39, AC-40

## Q18 · J-5 · 2026-11-08
Answer: 1. Scope cut = any FR, AC or story removed, or a Non-goals entry added, compared with the previous round; loosened wording isn't caught. [human]
Patched: FR-11; added FR-37, AC-37

## Q19 · J-11 · 2026-11-08
Answer: 1. Resuming gives the stopped gate 2 more rounds and raises the effort's jury cap by 2. [human]
Patched: added FR-40, AC-41

## Q20 · J-1, J-3, J-5, J-10 · 2026-11-08
Question: spec jury round 2 left four findings: fix or accept each as risk?
Answer: J-1 accept as risk: same trust as gate approvals, named in Risks, history shows who ran each grant. J-3 fix: atomic claim, refreshed at least every 10 minutes while waiting, test for two drivers starting together. J-5 accept as risk: mechanical scope check only; softened wording can slip, the PR report lists every fix. J-10 fix: resuming after a failed PR only retries opening the PR, running no stage. [human]
Patched: FR-38; added FR-41, AC-43, AC-44, AC-45, state table row pr_pending

Session 3 (2026-11-08): plan stage.

## Call · plan: CT-12, CT-16, CT-17 · 2026-11-08
An epic's gate gets no fixer: its confirmed findings already become fix tasks the implement stage runs (FR-16). Under auto, minors are left out of what holds a gate, as the epic gate already does, instead of the fixer disposing each one (FR-17). Both are below the bar: neither changes what a user can do or sees, who may do it, what data is kept, or what it costs, beyond what FR-16 and FR-17 already fix. [agent]

## Change · C-261108-mplt · 2026-11-08
The human chose a driver claim that goes stale on its refresh time alone (architecture.md). That contradicts FR-38 and AC-38's "process gone" case, so it went to change request C-261108-mplt against the spec (pending); the spec is not patched until the human settles it. The grant's model is `unknown` when it can't be detected, which keeps AC-42 as written. [human]

## Q21 · C-261108-mplt · 2026-11-08
Question: accept the change request: a driver claim goes stale on its refresh time alone?
Answer: 1. Accept: FR-38 and AC-38 drop the process test; Risks names the 30-minute hold. [human]
Patched: FR-38, AC-38, Risks

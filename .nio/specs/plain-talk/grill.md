# Grill log: plain-talk

Append-only. One entry per question, below-the-bar call or derived item.

## Session 1 · 2026-10-26 · the human answers

## Facts · OP-1, OP-8, OP-9, OP-10 · 2026-10-26
Facet: verification (OP-1), data (OP-8), change (OP-9, OP-10)
Found: RF-1 (IDs appear mostly in jury-driven questions), RF-2 (scope lens reads only the first Question line), RF-3 (about 20 more human-facing places), RF-4 (CLI output 1-41 lines), RF-5 (no SKILL.md heading parsers).
Patched: retired OP-1, OP-8, OP-9, OP-10; raised OP-13, OP-14, OP-15 (contradiction)

## Q1 · OP-6 · 2026-10-26
Facet: meaning
Question: Which NIO words can a message use without explaining them?
Options: 1. Stage names are fine; describe everything in the middle group (recommended) 2. Stage names plus a short list of allowed words in the shared block 3. Describe everything, stage names included
Answer: 1. Stage names are fine; describe everything in the middle group: the agent's one test is "does the human start this by name?"; spec, grill, jury and plan are plain, while open point, deferred point, finding, disposition, verdict, lens, refuter, the severities and the provenance tags are described by what they do. No word list to maintain; messages run a few words longer. [human]
Patched: FR-3 [human]; Decisions; retired OP-6

## Q2 · OP-11 · 2026-10-26
Facet: change
Question: When the agent asks through a click-to-answer box, where does the Refs: line go?
Options: 1. Last line of question (recommended) 2. Text first, then box 3. Log only
Answer: 1. Last line of question: the question text holds the first line, the context and Refs. It's one message, nothing is lost and the log matches what you saw; the question box gets longer. [human]
Patched: FR-24, AC-24 (new); retired OP-11

## Q3 · OP-12 · 2026-10-26
Facet: meaning
Question: When the grill asks several questions at once, does the batch get one 'what's needed' line, or does each question get its own?
Options: 1. One line, each Q full (recommended) 2. Each keeps own line 3. One line + shared Refs
Answer: 1. One line, each Q full: the round opens with 'Answer 5 questions, by number', and each question keeps its own context, options and Refs. Logs stay clean; questions in a round don't start with 'Pick one:'. [human]
Patched: FR-25, AC-25 (new); retired OP-12

## Q4 · OP-5 · 2026-10-26
Facet: verification
Question: How does the drift test know which skills must carry the 'Talking to the human' block?
Options: 1. Every skill (recommended) 2. Fixed list of five 3. Marker in each skill
Answer: 1. Every skill: every folder in skills/ must have the block, with no list or marker, so a new skill fails until it has it. A future skill that never talks to you would need an exception added then. [human]
Patched: FR-11; retired OP-5

## Q5 · OP-15 · 2026-10-26
Facet: change
Question: When a skill passes along output from a nio command, what goes in the Refs: line?
Options: 1. Command + IDs (recommended) 2. Short whole, long as command 3. Always full output
Answer: 1. Command + IDs: Refs holds the command and the IDs it cites, and you rerun the command to see the raw text. It stays one line and everything is still checkable. [human]
Patched: FR-16; retired OP-15 (contradiction with RF-4 resolved)

## Derived · AC-5 · 2026-10-26
From: FR-16 (Q5)
Patched: AC-5 and its Observable: Refs holds the command and cited IDs, not the raw output

## Q6 · OP-13 · 2026-10-26
Facet: change
Question: Should the ~20 other places where the skills talk to you also be rewritten, or only the ones the issue lists?
Options: 1. Rewrite all (recommended) 2. Only listed places 3. Listed now, rest later
Answer: 1. Rewrite all: no old wording such as 'show the file:line' is left contradicting the block in the same file. It's roughly double the edits, all small wording changes in five files. [human]
Patched: FR-17, FR-18, FR-20, FR-21, FR-22; retired OP-13

## Derived · AC-18 · 2026-10-26
From: FR-17, FR-18, FR-20, FR-21, FR-22 (Q6)
Patched: AC-18 now covers every point those FRs list

## Q7 · OP-7 · 2026-10-26
Facet: data
Question: When the grill logs a question that came from a jury finding, does the log also keep the finding's raw form?
Options: 1. No, header ID enough (recommended) 2. Yes, add Finding: line 3. Only behaviour changes
Answer: 1. No, header ID enough: the log shows what you saw, and the raw finding is looked up by ID in the jury's record. Nothing is duplicated; it takes one lookup to see the original wording. [human]
Patched: FR-14; retired OP-7

## Q8 · OP-14 · 2026-10-26
Facet: data
Question: How is a multi-line question written into the grill log so the jury can still read it?
Options: 1. Labelled line per part (recommended) 2. Reader takes multi-line 3. Verbatim block + summary
Answer: 1. Labelled line per part: the log has Question: (the line you saw), then Context:, Options: and Refs:. It needs no code change and still matches what you saw. The reviewer doesn't get the context, which it doesn't need. [human]
Patched: FR-13; retired OP-14

## Q9 · OP-4 · 2026-10-26
Facet: meaning
Question: When a review list has more behaviour changes than fit at a glance (say 12), how many are shown?
Options: 1. Show all of them (recommended) 2. Top 5, count the rest 3. Above 5, ask first
Answer: 1. Show all of them: you never approve an unseen product change, and a long list signals the spec should be split. The occasional message runs to about 12 lines. [human]
Patched: FR-7; retired OP-4

## Q10 · OP-2 · 2026-10-26
Facet: meaning
Question: Is the context limit 'at most 3 lines' or 'about 3 lines'?
Options: 1. At most 3 (recommended) 2. About 3 3. At most 3, unless asked
Answer: 2. About 3: room for the rare complex case, but 'about' tends to grow over time. [human]
Patched: none yet (follow-up Q11)

## Q11 · OP-2 · 2026-10-26
Facet: verification
Question: What's the most 'about 3 lines' may stretch to before the agent has to rewrite?
Options: 1. Aim 3, max 5 (recommended) 2. Aim 3, max 4 3. No ceiling, you judge
Answer: 3. No ceiling, you judge: the agent aims for about 3, and the check is your judgement in the next session. Nothing is automated. [human]
Patched: FR-2, AC-2, decision table row "context"; retired OP-2

## Q12 · OP-3 · 2026-10-26
Facet: meaning
Question: Does a message with nothing to reference still end with a Refs: line?
Options: 1. Omit when nothing (recommended) 2. Always, 'Refs: none' 3. Only questions/decisions
Answer: 1. Omit when nothing: there are no empty lines, but any message resting on a file, ID or command must still cite it. The self-check becomes 'if it rests on something, cite it'. [human]
Patched: FR-5; retired OP-3

## Derived · AC-3, AC-9, AC-19, AC-20, AC-21, AC-23, A-3, UJ-1, UJ-2, UJ-3, SC-2, table row "raw CLI output" · 2026-10-26
From: AC-3 from FR-1, FR-5 (Q12: no Refs line when nothing is cited; rewritten). AC-9 from FR-7. AC-19, AC-20, AC-21 are FR-1/3/4/5 applied to FR-20, FR-21, FR-22. AC-23 from FR-13 (Q8) and RF-2. A-3, UJ-3 from US-3. UJ-1 from FR-1..FR-5. UJ-2 from FR-7. SC-2 from FR-3 and SC-1. Table row from FR-16 (Q5; rewritten).
Patched: those items

## Call · AC-13, AC-14, NFR-1, risk "plain words can bend a finding" · 2026-10-26
Taken as recommended [agent]: drift-test failure details (name the differing line; fail when NORTH_STAR has no block), stdlib-only and under 2 s like the other self-checks, and the risk note. No to all five: none changes what a user can do, sees, who may do it, what data is kept, or what it costs.
Patched: AC-13, AC-14, NFR-1, the risk line

## Q13 · FR-23 · 2026-10-26
Facet: actors
Question: When you need to run a command, is the command shown in the message itself, or only in Refs:?
Options: 1. Body and Refs (recommended) 2. Body only 3. Refs only
Answer: 1. Body and Refs: 'Run this command' comes first, with the command right under it, ready to copy. Nothing is hidden, and the command appears twice. [human]
Patched: FR-23 [human]; AC-4 and table row "command the human must run" [derived: FR-1, FR-23]

## Q14 · Non-goals · 2026-10-26
Facet: failure
Question: Are the existing grill logs from earlier specs rewritten into the new plain format?
Options: 1. Leave as they are (recommended) 2. Rewrite them 3. Leave + note at top
Answer: 1. Leave as they are: logs record what you saw at the time, and rewriting would make them false. The jury reads both shapes. Old and new logs look different. [human]
Patched: non-goal "Rewriting entries in existing grill.md logs" [human]

## Finish · 2026-10-26
Gate: `nio check spec plain-talk --gate` passes. Passivity: 13 of 14 recommendations accepted, Q10 went against it; not flagged. Fidelity: patched items re-read against Q1-Q14.
Answer: finish [human]

## Session 2 · 2026-10-26 · jury round 1 findings, the human answers

## Q15 · J-2 · 2026-10-26
Facet: change
Question: Should each fact in a question still say where it comes from, right next to it?
Options: 1. Plain source beside fact (recommended) 2. Only in Refs 3. Numbered footnotes
Answer: 1. Plain source beside fact: '…per the jury code' goes beside each fact, with the IDs in Refs. Both rules hold and nothing old is reversed. Costs a few words per fact. [human]
Patched: FR-17, AC-17

## Q16 · J-10 · 2026-10-26
Facet: change
Question: Ship this as one change, or split it into slices?
Options: 1. One change (recommended) 2. Two slices 3. One slice per skill
Answer: 1. One change: the block, the test and the rewrites land together, so no skill is ever half-converted. It's mostly wording, so the risk is low. One bigger review. [human]
Patched: Decisions

## Q17 · J-8 · 2026-10-26
Facet: cost
Question: Keep the drift-test speed rule (standard library only, offline, under 2 seconds)?
Options: 1. Keep it (recommended) 2. Drop it 3. Keep stdlib, drop time
Answer: 1. Keep it: free to meet and matches the other self-checks. It stops a future dependency or network call, and a test checks it. [human]
Patched: NFR-1 [human]

## Q18 · jury round 3 · 2026-10-26
Facet: cost
Question: Run a third jury round on the fixes, or stop here?
Options: 1. Run round 3 (recommended) 2. Close the gate now 3. Pause and commit
Answer: 2. Close the gate now: go to the plan and implementation, with the last fixes unverified. The record shows the gate closed by you, not approved by the jury. [human]
Patched: none; gate closed with `nio jury check --record --human`

# Intake: jury-round-cap

## The human's words (2026-11-14)

> the reason im asking is that we're calling jury too many times and impleemntation is takint too long, implemenitg a feature takes like 8 hours ande eats up tokes

> and timewise would it be quicker with those 4 fixes?

> yes file all four as issues, and then do them, but no need to go through nio flow to implement them, just write specs with nio and then we can implement them wiht normal agents? what do you think?

> yes

(Agreed in conversation: this spec covers two of the four fixes, #129 and #126; #128 and #85 get their own spec.)

## Source: https://github.com/nikolajkarpic/nio/issues/129

## Problem
After the convergence work the target is 2 rounds per gate (review + one fix check). On 2026-11-08 the gates ran:

| Effort | spec | plan | tasks | impl E-1 | impl E-2 | impl E-3 |
|---|---|---|---|---|---|---|
| #123 explainer | 3 | 2 | 4 | 3 | 2 | 3 |
| #49 onboarding | 3 | 3 | 2 | 2 | **7** | – |
| #122 full-auto | 4 | 3 | 4 | 2 | 2 | – |

That's 17 rounds over the target across three efforts. At 10–20 min per extra round (fix, re-run, fix check, 15–40 orchestrator turns on a 170–430k context), that's roughly 1–2 h of wall time per effort. 3 of the gates were closed by a human override anyway.

## Proposal
- After round 2, `nio jury next` does not start round 3. It prints every finding still open, in one batch, for the human to rule on: accept as risk, fix as a task, or start one more round.
- Escalation jurors (#105) join their round and don't count as a new one.
- The cap goes in config (`jury.max_rounds`, default 2).

Refs: #105, #125, #126

## Source: https://github.com/nikolajkarpic/nio/issues/126

Seen on 2026-11-08-full-auto-run E-1 (runs R-261108-…, rounds 1–2):
- J-2 said `/SKILL.md` doesn't exist because a task's `skills/*/SKILL.md` Files glob was never expanded.
- J-15–J-17 asked for evidence of ACs owned by a later epic's task (T-4 in E-2, T-23 in E-7).
- Each became a fix task (T-30, T-32–T-34). After the human retired them (C-261108-5stc), the findings stayed `fix-task` and round 2 re-created them as T-35–T-37.
- Each retirement edits tasks.md, which moves the effort back to tasks_jury and needs another human `--commit`.

Ideas:
- Expand globs in Files before the jury cites them.
- The conformance lens skips ACs whose serving task sits in a later epic.
- Retiring a fix task closes its finding.
- Retiring a fix task (an append-only change under `#### Fixes`) doesn't send tasks back through the gate.

### Comment on #126 (2026-11-14)

More data from 2026-11-08 (#123, #49, #122):
- Fix tasks were 11/27, 11/35 and 8/29 of all tasks. 13 tasks were retired, 10 of them on #122.
- The effort went back to `tasks_jury` 2× (#123) and 4× (#122). Each time cost a juror run, 15–40 orchestrator turns on a 170–430k context, and a commit; about 20–60 min per effort in total.
- Proposal (one of four fixes picked from this analysis): an approved tasks.md accepts appended fix tasks, and retirements of them, without reopening the tasks gate. A finding owned by a later epic is disposed `out-of-scope` before a task is ever made.

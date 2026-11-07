# Intake

## The human's words (via the delegating orchestrator session)

Dogfood: pick one small open bug from the backlog and run it through the new lite path end to end, timing it.

## Source: https://github.com/nikolajkarpic/nio/issues/91

# Red accepts a self-check run that crashed before its `ran` line (a SyntaxError counts as red)

## Problem
In the #70 effort, T-3's worker ran `nio flow red` on `tests/test_selfcheck.py` while the file had a SyntaxError. Red was accepted: a plain script has no known runner, and a crash before the `ran <n> tests, <m> failed` line reads as a runner red can't read (a non-goal of the #70 spec). The worker then had to re-prove red, which cost two of the task's three attempts.

## Proposal
When the command names a test file that calls `selfcheck.main(` (or any self-check file) and the output has no `ran` line, refuse red as "collection, import or syntax error". Or: treat a Python `SyntaxError`/`ModuleNotFoundError` traceback with no result line as a wrong reason for any plain `python` command.

Refs: #70 (non-goal: crash before the `ran` line), `src/nio/implement.py:wrong_reason`

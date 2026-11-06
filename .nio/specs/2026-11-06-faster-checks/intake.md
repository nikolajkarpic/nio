# Intake

The human (Nikolaj), through the orchestrator brief:

> Goal: one NIO effort that implements GitHub issues #73, #72, #71 and #74.
>
> Why: the test suite is the main time sink of every NIO run (suite 346 s serial; test_implement.py 178 s, 169 s of it subprocess startup of the nio CLI; jury evidence re-runs files the suite already ran; jurors' outputs get rejected over format slips). Priority order is #73 (in-process CLI in tests), #72 (run test files in parallel in tests.suite), #71 (evidence reuses suite results), #74 (lenient jury parser). Measure before/after wall-clock of the suite and test_implement.py and put the numbers in the PR body.
>
> Lazy and minimal: smallest diff that works; the suite must still fail when any file fails.

## Source: https://github.com/nikolajkarpic/nio/issues/73

### Make test_implement.py fast: call the nio CLI in-process in tests

## Problem
cProfile: 169 of the 178 s that tests/test_implement.py takes go to 237 `nio flow` subprocess calls at 0.71 s each (`tests/test_flow.py` `cli` starts a fresh Python and imports `nio.cli` every time). Workers, red and green run this file about 4 times per task.

## Proposal
Call the CLI's `main()` in-process from the test helper, capturing stdout, stderr and the exit code, and chdir/env the way the subprocess did. Keep a subprocess only where a test needs process isolation (locks held by another pid, timeouts, process groups). Target: test_implement.py under 60 s.


## Source: https://github.com/nikolajkarpic/nio/issues/72

### Run the suite's test files in parallel

## Problem
The whole suite runs serially in 346 s (test_implement 176 s, test_evidence 114 s, test_flow 29 s, every other file under 9 s), even though the machine has 12 cores. The suite runs about 20 times per effort: the baseline at the first claim (6m10s), every epic close, every evidence run and every fix round.

## Proposal
Run the test files in parallel in `tests.suite`, e.g. `ls tests/test_*.py | xargs -P8 -n1 uv run python`, once it's verified that the files share no state (fixtures use mkdtemp). It must still exit non-zero when any file fails, and the runner detection and failing-test parsing must still read the output correctly. The time then drops to roughly the slowest file. That saves about 2.8 min per run, or about 55 min per effort.


## Source: https://github.com/nikolajkarpic/nio/issues/71

### Jury evidence repeats the suite and whole test files the epic-close review already ran

## Problem
In implement-followups E-1, `nio jury evidence` took 14m21s and hit the 600 s tool timeout. It runs the suite in a fresh copy (about 6 min), then 5 quickstart journeys (about 8 min). Those journeys re-run whole test files that the suite has just run: test_implement.py 3 times, plus test_jury, test_tasks+agents and test_flow. The epic-close review had already run the same suite at the same commit. A one-line fix task then started a second evidence run. That's about 12 min per run and about 2 runs per epic, so 1.5–2 h per 5-epic effort.

## Proposal
- Skip an auto journey whose command is a test file the suite already ran at that commit, and record it as covered by the suite run.
- Reuse the epic-close review's suite result when the commit is the same and the tree was clean, instead of running the suite again in the copy.

Size S (~30 lines) in `src/nio/evidence.py` `collect` and `src/nio/implement.py` `review`.


## Source: https://github.com/nikolajkarpic/nio/issues/74

### Jury parser: accept small format slips (None., inline gap/where/fix)

## Problem
Juror outputs are rejected as INVALID over small format slips, which costs a re-emit round and a second refuter pass:
- Spec round 2 of implement-followups: all 5 lenses were INVALID only because they wrote `None.` instead of `none` under `## Findings`.
- All 3 implementation lenses were INVALID over inline `gap` / `where` / `fix:` fields.

## Proposal
Make the `src/nio/jury.py` parser tolerant of these slips: accept `none`/`None`/`None.` case-insensitively with trailing punctuation, and accept the known inline field forms. It should still reject output that is actually malformed. Saves about 3–5 min per effort, and it removes a common source of failed rounds.



The human's coordinator, during the grill:

> the research agent filed #75 ("Implementation fix check re-collects the whole epic's evidence for a one-line fix"): the fix-check round should reuse round-1 evidence and re-run only what the fix touched. It's in the same code as #71 (src/nio/evidence.py collect). If your spec isn't approved yet, fold #75 into this effort, add it to the PR's Closes line and log the choice in decisions.md. Recommended order from the research: #74 → #71 → #75 → #73 → #72.

## Source: https://github.com/nikolajkarpic/nio/issues/75

### Implementation fix check re-collects the whole epic's evidence for a one-line fix

## Problem
After a fix task, the implementation gate's fix check runs `nio jury evidence` again for the whole epic, even though only one juror re-checks one finding against a small diff.

From implement-followups E-1 (transcript of session 322a1614, 2026-11-05):
- Round 1 evidence: 10 min (602 s). Four jurors and the refuter then took about 2 min in total.
- The refuter confirmed one major (J-1), fixed by T-14 in 11 min. T-14's green had already run its own tests.
- Round 2: evidence for the whole epic ran again, 22:05 to 23:10 (65 min; another session was running tests at the same time, so about 12–14 min without that). Then a single adversary fix-check juror answered in 30 s.

So about 95% of round 2's time went to evidence that the fix check barely reads. Every implementation gate so far had a fix-check round: E-2 (3 rounds), E-8 (2), E-1 (2). At 5 epics per effort, that's about 1 h per effort, and more when anything else is running.

#71 removes duplicate work inside one evidence run. It doesn't remove this second run.

## Proposal
- In a fix-check round (`nio jury changed` names only fix-check lenses), have `nio jury evidence` reuse the round-1 `results.json` and re-run only the tests of the fix tasks appended under `#### Fixes` (the commands their green already accepted), plus any journey whose files the fix diff touches. Record which results were reused and from which commit.
- `nio jury pack` for a fix check then carries the fix diff and those fresh results, which is what the fix-check pack asks the juror to judge.
- The full suite still runs once when the effort's last epic closes, so a regression a fix causes elsewhere is still caught before merge.

Size S–M, in `src/nio/evidence.py` and `src/nio/jury.py` (`pack`, `changed`).

Refs: #71 · .nio/research/2026-11-06-speedup.md


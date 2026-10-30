# Architecture: implementation jury

Settles only what the plan skill's stop list sends here. Each item follows from the approved spec, the human's answers
in `grill.md`, or the existing code, and this file records where. It adds no design of its own. Read-only to the plan;
changing it takes a change request.

## New modules and folders (stop list 2)
- `src/nio/evidence.py`: the CLI-first checks with zero model calls (NFR-1): the throwaway copy and its runs (FR-3,
  FR-11, FR-12, FR-40, FR-41), phantom completion (FR-7, FR-8), and the stub, no-assertion, assertion-change and
  uncertain hints (FR-9, FR-13, FR-36, FR-39). One module per concern, like `implement.py`. It runs commands through
  `implement.run` and reaches git through `records.git(..., full=True)`.
- `src/nio/agents/conformance.md`, `src/nio/agents/correctness.md`: the two core cards, read-only like every lens
  (FR-14, FR-19, FR-34). `risk-rollback.md` already exists and gains its section (FR-35).
- `tests/test_evidence.py`: this spec's tests, a plain script like the others.

## Stored data (stop list 3)
- `.nio/specs/<slug>/jury/implementation-E-n.json`: one ledger per epic, in the existing ledger format, with one more
  finding field, `gap` (FR-21, DF-2). Rounds, votes and convergence stay as they are (FR-32).
- `.nio/runs/<run>/results.json`: the run results, gitignored like the rest of a run. Each finding that rests on a run
  quotes what it needs, so the committed ledger stands alone. Output is cut as FR-41 says.
- `.nio/specs/<slug>/tasks.md`: fix tasks are appended under the epic's `#### Fixes`, the place `tasks.parse` already
  reads (FR-26, FR-27). One finding, one task: the `From:` line is what makes a second append a no-op (AC-50).
- `history.jsonl`: `epic` lines keep their kind. `reason` becomes the gate's outcome instead of `skipped: not built`,
  and the line is written only when the gate is approved or the human closes it, by `nio flow done implementation-E-n`,
  which after the last epic also writes the `pass` line. `left` keeps reading it. Old `skipped: not built` lines stay
  closed and are reported as never reviewed (grill Q28).
- Config, read through `records.config`:
  - `tests.lint`, `tests.typecheck`: unset means the check is reported as not configured, to the human and in every
    pack, and the gate goes on (grill Q23, FR-11, DF-4);
  - `tests.setup`: optional, run first in the throwaway copy, because a fresh copy has no gitignored dependencies such
    as `node_modules` (follows from FR-40);
  - `jury.run_timeout` (FR-40) and `jury.max_runs` (exists).
- The `secrets` risk flag joins the existing list (FR-45, FR-46).

## Interfaces used outside this feature (stop list 4)
- The gate's name is `implementation-E-n` wherever `nio jury` takes a gate, so ledger paths and verdict subjects
  (`<gate>:<slug>`) name the epic with no new field (FR-33, AC-39). A bare `implementation`, or an epic `tasks.md`
  doesn't have, is refused (FR-2, AC-3).
- New: `nio jury evidence <slug> E-n --run <run>`: starts the gate and prints the results' path. It refuses when a task
  is unfinished (FR-2). It takes no command: it runs only what config, `tests.md` and `quickstart.md` name, so
  `nio allow` can allow it, unlike `nio flow red` and `green`.
- `nio jury check --record` on this gate also appends the fix tasks, writes change requests (FR-26, FR-30) and commits
  them with the ledger and verdict. The CLI's own findings enter the ledger as confirmed (grill Q25, FR-24).
- Lens outputs at this gate need `gap` (FR-21). Other gates' formats don't change. The word-for-word quote check is off
  at this gate only (FR-23).
- `nio flow next` names `@nio:jury` while an epic's gate is open. `nio flow claim` refuses the next epic until that
  epic's `epic` line exists (grill Q22). This replaces the implement stage's temporary skip (implement FR-28), whose
  test changes with it.

## Choices the spec left open (stop list 5)
- **One epic at a time** (grill Q22): the next epic waits for this one's gate. So an epic's commits are contiguous, and
  its diff is the range from the parent of its first `T-n:` commit to its last.
- **Throwaway copy** (grill Q27, replacing the worktree): a local `git clone` in a temporary folder, detached at the
  epic's last commit and removed after the runs. It needs nothing installed and shares no refs, config or hooks with the
  human's repo (FR-40, AC-53).
- **Misuse lines and journey runs** (DF-3): the misuse lines are the `## Misuse tests` entries of `tests.md`, and the
  journey runs are the `auto` scenarios of `quickstart.md`, compared the way its template says. `manual` scenarios go
  to the human as a checklist. A misuse line with no test is a hint in every pack (FR-13).
- **Test results** (FR-3): one full-suite run, read with the runners `implement.py` already knows. On a runner it can't
  read, the results keep the exit code and output and every pack says per-test results are unknown (FR-13).
- **A juror's requested run** (FR-20): it names a `TC-n` from `tests.md`, and nothing else is accepted, so no command
  text from a model ever reaches a shell. A runner with no known way to run one test gives "couldn't run" (AC-27).
- **Symbols** (FR-8, FR-13): a word-boundary search of the tracked files, in any language. No single-language parser.
  Anything it can't decide is a hint, never a pass.

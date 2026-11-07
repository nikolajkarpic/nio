# Decisions: 2026-11-07-refuter-batch-forge (#113, lite)

Orchestrator: claude-code / claude-opus-5-5, delegated by the human (Nikolaj). Wall clock 15:34Z (`nio new spec`) to 15:56Z (done): about 22 minutes.

- Built on `nio/2026-11-07-lite-path` (#112), not #110's branch: #110 has no lite path. #110 stays as is; #112 carries the #113 fix.
- Route lite with risk `[multi-party]` (the drafter's flag): a defect, one module (`src/nio/`), no risky flag.
- Grill Q1: clear the run's refuter batch once a refuter output is applied (`led["asked"].pop(run)`), the smallest correct option. Keying by an echoed counter or hash would change the refuter card; refusing a refuter file that is new with lens outputs is not needed once the batch is cleared.
- Grill Q2: a refuter file that changes with no batch outstanding refuses the collect (the existing "refuter output before its batch" error).
- Grill Q3: `land` returns a failed `git diff` as git's error (blocks the task), not a raise; a raise would leave the claim and worktree dangling (RF-3).
- Jury round 1 (implementation-E-1) rejected: J-1 (major, confirmed) a failed diff force-removed the worktree with no patch. Fixed by T-3: the worktree is kept and named when no patch was saved.
- J-7, J-8 (CLI: AC-4, AC-5 no passing evidence) accepted as risk: existing tests prove both, but lite evidence lists only added tests, and a fix task's red refuses an already-passing test. Filed #115. The gate was closed by the delegated human and the effort overridden to done, as in #111's dogfood.
- Minors left open (not fixed): J-2 (`land` ignores `git add` / name-only errors), J-3 (a byte-identical refuter answer to a new batch is never read; pre-existing), J-4 (a forged refuter file is still accepted for IDs of an outstanding batch; the #109 host guard's job), J-5, J-6 (test strength).
- The kept worktree after a failed diff is not cleaned up on unblock; it is removed by hand after recovery (rare: `since` is the claim commit).
- Juror outputs are saved verbatim under `.nio/runs/R-261107-tzcf/jury/` (tasks) and `.nio/runs/R-261107-kdbp/jury/` (implementation), git-ignored; copies in the orchestrator's scratchpad `n113/jurors-113/`.

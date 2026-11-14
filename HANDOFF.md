# Handoff: explainer effort (2026-11-08-explainer)

## Goal
Build `@nio:explain` (GitHub issue #123): a skill + `nio` commands that turn an approved plan (or any topic) into
`explainer.md` with Mermaid diagrams (rendered to SVG via pinned `npx @mermaid-js/mermaid-cli@11.4.2`) and short
walk-throughs, linked from quickstart. Spec, plan and tasks are approved; we are in the implement stage.

## Authority
The human said (2026-11-08): "I give you full autonomy to run these I approve all your future commands and I chose all
recommend options please just finish this." So: take the recommended option at every decision, run `--by human`
approvals/unblocks yourself (say so in the reason), but **never merge** and stop before anything destructive.
Then they interrupted and asked for this handoff — confirm they still want autonomy before resuming.

## Where things are
- Branch: `nio/2026-11-08-explainer` (never merge; the human does). Spec folder: `.nio/specs/2026-11-08-explainer/`.
- Code: `src/nio/explain.py` (sections, nodes, render, check, finish), `src/nio/cli.py` (`nio check explainer`,
  `nio explain finish|topic` — `topic` still a stub until T-13), `src/nio/jury.py`/`flow.py` (plan gate ignores the
  quickstart `Read first` line), `skills/explain/SKILL.md`, tests in `tests/test_explain.py` (24 pass),
  `tests/test_explain_e2e.py` (new, skips without NIO_E2E=1).
- Epics: E-1, E-2, E-3 approved. E-4 = T-7 ✔, T-8 ✔, **T-9 in progress**. Then E-5..E-9 (T-10..T-16) still to build.

## Exact current state (uncommitted, T-9 claimed)
`nio flow green ... T-9` was run once and its review **failed**: the epic-closing full suite found 2 new failures in
`tests/test_flow.py` caused by the new skill:
- `test_uj3_override_shown`: every SKILL.md must carry the flow-state RULE line (copied from skills/plan/SKILL.md:15).
- `test_ac11_no_hand_edit_instruction`: hard-coded count of skill/agent files `== 26` → now 27.

I already fixed both in the working tree (not committed):
- `skills/explain/SKILL.md`: added the RULE line after "Run the CLI as …", and removed two sections the T-8 worker had
  wrongly copied from NORTH_STAR ("Non-goals (for now)" and "Success looks like").
- `tests/test_flow.py:869`: `26` → `27`.
- `tests/test_explain_e2e.py`: T-9's own file (untracked, the worker's output).
Verified: those 2 flow tests, test_talk.py and test_explain.py pass.

**Next command** (attempt 2 of 3 for T-9; it was the call the human interrupted):
```
uv run nio flow green 2026-11-08-explainer T-9 --run "uv run python tests/test_explain_e2e.py" --by "orchestrator / claude-code / <model>"
```
It runs the full suite (slow, several minutes). Expect "outside the task's files" notes for SKILL.md and test_flow.py —
those are recorded, not failures. On `done:` it closes E-4 and says to run `@nio:jury on implementation-E-4`.

## The loop (per skills/implement + skills/jury)
1. `nio flow claim 2026-11-08-explainer --by "orchestrator / …"` → task, mode, card, pack.
2. split: test worker (nio-worker-<tier>) → `nio flow red … --run "<cmd>"` → fresh code worker → `nio flow green`.
   single: one worker runs red then green itself. direct: worker codes, you run `nio flow green … --run "<cmd>"`.
3. Epic end: `nio jury next <slug> implementation-E-n` → `nio jury evidence <slug> E-n --run R` →
   `nio jury next … --run R` → run listed jurors in parallel (tell them their scope is that epic only) →
   `nio jury next … --run R` → refuter when asked → dispose/fix tasks → fix-check → `nio flow done implementation-E-n`.

## Lessons (cost us blocked tasks)
- **Commit tasks.md before claiming** a fix task you add by hand; an uncommitted tasks.md edit fails the task's review.
- Workers must run **red before writing code** and must not edit the test after red ("changed since red" → refusals).
- Fix tasks the jury auto-makes can be wrong: J-14/E-1 (AC served by a later task), J-10/E-2 and J-9/E-3 (evidence
  can't see a test whose name isn't in tests.md, or the juror cited the wrong line). Recovery used: accept the finding
  as risk (`--by human`, reason), remove the task from tasks.md + add its ID to `retired:`, rerun the tasks jury
  (`nio jury next <slug> tasks`, one executability juror), then `nio flow done tasks_jury --commit … --by human`.
  A wrong `Test:` line on a fix task: block it (3 refusals), fix the line (must cite a TC-n on a full spec), commit,
  unblock, re-claim.
- A blocked task's changes are saved in `.nio/runs/<run>/T-n.patch`; after unblock + claim, `git apply --include=<test
  file>` → red → apply the rest → green.
- Juror output must start with front matter; if `INVALID`, SendMessage the juror to rewrite it.

## Accepted risks / follow-ups already filed
- Issue #127: count diagram nodes from the rendered SVG (rare Mermaid forms undercount); also CT-2 (`end` whole-word)
  and CT-3 (`broken` vs `unreachable`) wording lags the code — fix at the next plan change.
- Fix tasks retired: T-24, T-28. Two task-test gaps accepted at the tasks gate (J-2, J-5, J-3 there).
- Should file a NIO issue: evidence matching ignores tests not named in tests.md / off-by-line juror citations, and
  hand-added fix tasks after a claim trip the review.

## After all tasks
`nio flow next` says done → tell the human to merge `nio/2026-11-08-explainer` (never merge yourself). Remaining
manual quickstart scenarios QS-1..QS-4 need a person.

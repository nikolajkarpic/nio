# Intake

## Human

Goal: one NIO bugfix effort fixing the defects an independent review found in the just-merged speed-up PRs.
- #101 (major, safety): a juror with the Write tool can forge `<gate>-refuter.md`, and collect / `nio jury next` applies it with no refuter batch, approving the gate. Reviewer's cheapest fix: accept the refuter file only after `next` wrote the refuter batch, and only for the IDs in that batch. Also consider recording git HEAD/status when jurors start and refusing the next step if anything outside the run's jury folder changed (jurors could edit the spec they judge). Decide, record the choice, and keep it minimal.
- #102 (major, data loss): `land` and `shelve` move the wave patch through text-mode git (`records.py:48`, `implement.py` around 368-370 and 454-457), so CRLF changes don't apply and a latin-1 file crashes `land`. Use bytes end to end.
- #103 (major): `nio jury next` loops forever on `rerun` when no lens has a fix to check (`jury.py` around 1417 and 1451).
- #104 (minor, three items): `test_pack.py -v` runs 0 tests; `evidence.one_test` has no self-check form; covered journeys skip their `Expected:` check. Fix those that are small; leave the others in the issue with a note.

Each fix needs a test that fails before it, including the two repro scripts turned into tests.

Lazy and minimal. Decision matrix in `.nio/specs/<slug>/decisions.md` (Decision | Options considered | Chosen | Why | Consequence); post it on #101.

Delegated (2026-11-07): the human gave the orchestrator standing authority to answer every grill question with the recommended option and approve each gate.

## Source: https://github.com/nikolajkarpic/nio/issues/101

# Jury: a juror's Write tool can forge the refuter's verdict and approve its own gate

## Problem
Found in the independent review of the speed-up PRs (#100). Since #99 every juror card has `tools: [read, write]` (`src/nio/agents/*.md`), and the only limit on what a juror writes is one line in its card. `jury.collect` (`src/nio/jury.py:616-639`) merges the run's new lens outputs and then, **in the same call**, applies `<gate>-refuter.md` if that file exists (`src/nio/jury.py:635`). It doesn't check that the refuter batch was ever issued (`packs/refuter.md`). Finding IDs are predictable (`J-1`, `J-2`, ...).

So a lens juror can write its own findings plus a refuter file that refutes them, or refutes its peers' findings. One `nio jury next` then records the gate as approved, and the refuter never runs. A juror reads the content it judges (the worker's code, the drafted spec), so an injected instruction in that content is enough. Before #99 only the orchestrator wrote files in `.nio/runs/<run>/jury/`.

Repro (uses the `tests/test_jury.py` helpers, in a temp repo):
```python
import sys; sys.path.insert(0, "tests"); import test_jury as T
root = T.gate_spec(); ADD = ["consistency:D-1 current"]
T.jury.plan(root, T.GSLUG, "spec", ADD)
lines = T.step(root, "", ADD); run = next(l[5:] for l in lines if l.startswith("run: "))
for n in [l[4:].split(":")[0] for l in lines if l.startswith("run ") and not l.startswith("run: ")]:
    T.out(root, run, "spec", n, T.FINDING if n == "testability" else "none")
(root / f".nio/runs/{run}/jury/spec-refuter.md").write_text(T.REFUTE.format(n=1))  # written by a lens juror
print("\n".join(T.step(root, run, ADD)))
```
Output: `new J-1 [major/gap] ...`, `refuted J-1 ...`, `outcome: approved`, `recorded .nio/memory/project/V-...`. The refuter was never asked.

The same write tool also lets a juror:
- overwrite a peer's `<gate>-<lens>.md`, which is filed by its name since #90;
- edit the artefact it judges. At the spec and plan gates, the version recorded is the edited blob.
- read a faster peer's output while the jurors run in parallel. Before #99 outputs were saved only after the jurors returned, so this also costs independence.

## Proposal
Cheapest first:
1. **Refuter only after its batch:** apply `<gate>-refuter.md` only when `packs/refuter.md` exists and is older than it, and only to IDs that batch lists. Otherwise `nio jury next` refuses with "refuter output before its batch". A few lines in `step`/`collect`.
2. **Nothing else changed:** `_begin` records `git status --porcelain` and `HEAD` in `packs/step.json`. The next `nio jury next` refuses when anything outside `.nio/runs/<run>/jury/` changed, or when a juror file holds more than one lens's output.
3. **Optional host guard (Claude Code):** a `PreToolUse` hook, or permission rules rendered by `nio agents sync`, that limits juror `Write` to `.nio/runs/*/jury/<gate>-<own lens>*.md`. Codex stays instruction-only, as it is already for `read`.

Refs: #99, #76, #90, #100


## Source: https://github.com/nikolajkarpic/nio/issues/102

# Waves: land and shelve patches go through text-mode git, stripping CRLF and crashing on non-UTF-8 files

## Problem
Found in the independent review of the speed-up PRs (#100). `records.git` runs git with `text=True` (`src/nio/records.py:48`), which decodes as strict UTF-8 and turns `\r\n` into `\n`. The wave code (#87) builds its patches from that decoded text and writes them back with `write_text`. These are `land` (`src/nio/implement.py:368-370`) and `shelve` (`src/nio/implement.py:454-457`), which a wave task now also uses.

The results:
- **CRLF file edited by a wave task:** the patch lost its `\r`, so `git apply` fails. The task is blocked "its changes don't apply", and its worktree is force-removed (`implement.py:750`). The only kept copy is the patch, and it lacks the CRs, so it doesn't apply by hand either.
- **New CRLF file:** applies cleanly with LF endings. The committed file differs from what the worker wrote and green proved.
- **Non-UTF-8 text file (latin-1):** `land` raises `UnicodeDecodeError` after `git add -A` in the worktree. Every `nio flow green` of that task crashes the same way.
- **`shelve` (attempt cap or `nio flow block`):** writes the same lossy patch, then restores the paths and removes the worktree. The patch is the only copy of the work.

Repro (temp repo, `implement.land` called directly):
```
win.txt committed as b'a\r\nb\r\n'; worktree edits it to b'a\r\nB\r\n'; worktree adds added.txt = b'new\r\nfile\r\n'
land(...) -> ('.nio/runs/R-1/T-1.patch', ..., 'error: patch failed: win.txt:1 ... patch does not apply')
patch has CR: False
(without the win.txt edit) added.txt in main: b'new\nfile\n', worktree: b'new\r\nfile\r\n'
(with latin.txt = b'caf\xe9\n') UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9
```

## Proposal
Treat patches as bytes. Give `records.git` a `raw=True` (bytes, no newline translation) option for `land` and `shelve`, and write with `write_bytes`. One test: a wave task that edits a CRLF file and adds a latin-1 file lands byte for byte.

Refs: #87, #59, #100


## Source: https://github.com/nikolajkarpic/nio/issues/103

# Jury: nio jury next loops forever when a rerun has no lens to re-run

## Problem
Found in the independent review of the speed-up PRs (#100). When a gate's outcome is `rerun` but `jury.changed()` names no lens to re-run, `nio jury next` gets stuck. It starts a run with no jurors (`src/nio/jury.py:1451`, and `:1417` on a call without `--run`) and prints `next: run each juror above in parallel, then nio jury next ...`, but no juror is listed above. No outputs ever arrive, so each later call takes the `not outputs` branch, calls `_begin` again on the same run and prints the same line. The skill tells the orchestrator to keep doing what `next:` says, so it loops.

A common way in: round 1 is rejected, and the human accepts the finding as risk (or puts it out of scope), so no FIXES disposition exists and `pack_ids` is empty. The agent also touches the spec, so `current != judged` and the outcome is `rerun`. The old skill would have seen `re-run: nothing` from `nio jury changed`.

Repro (`tests/test_jury.py` helpers): first review with one major from testability, confirmed by the refuter. Then `dispose J-1 accepted-risk --by human` and a one-word spec edit. Then `nio jury next` three times:
```
0 ['outcome: rerun', 'run: R-...-qdco', 'next: run each juror above in parallel, then nio jury next ... --run R-...-qdco']
1 ['run: R-...-qdco', 'next: run each juror above in parallel, ...']
2 ['run: R-...-qdco', 'next: run each juror above in parallel, ...']
```

## Proposal
In `_begin`, when `lenses` is empty, never print "run each juror". Either re-run every lens that voted on the changed IDs' neighbours (like the approved-gate branch of `changed`), or end with `next: show the human: the <gate> changed but no lens has a fix to check` and outcome `human`. One test: the repro above ends in a `next:` that is not a juror run.

Refs: #99, #76, #100


## Source: https://github.com/nikolajkarpic/nio/issues/104

# Review of the speed-up PRs: minor findings

Minor findings from the independent review of #81 #87 #89 #93 #99 (see #100). Each one was checked against the code on `main` (548eacb).

## 1. `tests/test_pack.py -v` runs no tests
**Problem:** `selfcheck.main` (`tests/selfcheck.py:8-12`) reads every `sys.argv[1:]` word as a test name. `test_pack.py` still reads `-v` itself (`tests/test_pack.py:12`), and CLAUDE.md documents `-v` ("prints each pack"). Now `uv run python tests/test_pack.py -v` prints `no test named -v` / `ran 0 tests, 0 failed` and exits 1.
**Proposal:** have selfcheck skip words that start with `-`, or take `-v` out of test_pack and CLAUDE.md.

## 2. Evidence never runs misuse tests on a self-check suite
**Problem:** `evidence.one_test` (`src/nio/evidence.py:110`) knows only unittest and pytest, so for this repo's suite it returns `None`. Every misuse test then becomes `attacks: not configured` and an "attack not run" hint, and `rest` drops it from the per-test results. #93 made one test addressable (`uv run python tests/test_x.py test_name`), but evidence wasn't wired to it. Checked: `one_test(<the configured suite>, "tests/test_jury.py", "test_x")` returns `None`.
**Proposal:** a self-check branch in `one_test` that returns `uv run python <file> <name>` (the suite's per-file prefix, which `_runs` already finds), or read misuse results from the suite's `ok`/`FAIL` lines.

## 3. A "covered" journey skips its `Expected:` check
**Problem:** when every step of a journey is the suite's per-file command, `collect` records it `passed` (`src/nio/evidence.py:467`) without calling `matched(expected, output)`. A journey that expects particular output, such as a count or a `contains:` line, passes on the suite's exit 0 alone. Under suite reuse no output exists to match.
**Proposal:** count a journey as covered only when its `Expected:` is empty, or holds `contains:` lines the suite's own output (not reused) has.

Refs: #100


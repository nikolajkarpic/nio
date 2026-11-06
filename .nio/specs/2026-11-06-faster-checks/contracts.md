---
slug: 2026-11-06-faster-checks
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: faster checks

## Contracts

### CT-1 In-process CLI test helper (FR-1, FR-2) [agent]
- Binding: `tests/test_flow.py:run_main` (new)
- Like: `tests/test_flow.py:cli`
- Kind: function
- Shape: `run_main(root, *args) -> (code, stdout, stderr)`
- Accepts: a fixture repo path and the CLI's words, e.g. `("flow", "claim", S, "--by", BY)`.
- Returns: the exit code `main()` ends with (0 when it returns or exits with None; `SystemExit.code` when an int; 1 with the message on stderr when a string, as Python itself does), and what it printed to `sys.stdout` and `sys.stderr`. An uncaught exception gives 1 and its traceback on stderr.
- Fails: never raises; restores the working directory, `os.environ` and `sys.argv` in a `finally`.
- Rules: "with the working directory and environment the subprocess had" (FR-1). `tests/test_flow.py:cli` and `tests/test_implement.py:nio` (existing) call it instead of `subprocess.run`. `tests/test_flow.py:nio` stays a subprocess: it runs `nio run` and other commands that can build a pack and load the embedding model, which `test_nfr2_offline` checks never lands in test_flow's own process. Tests that need their own process keep their own `subprocess.run` (FR-2, research RF-2). `cli`'s signature and return value don't change, so no caller changes.

### CT-2 One embedding model per process (NFR-1) [agent]
- Binding: `src/nio/index.py:embed` (existing)
- Like: `src/nio/index.py:embed`
- Kind: function
- Shape: `embed(model, texts) -> [bytes]`, unchanged
- Accepts: as today.
- Returns: as today; through a `functools.cache`d model constructor, the `TextEmbedding` for a (model, cache folder) pair is built once per process instead of on every call (research RF-11).
- Rules: "THE SYSTEM SHALL run tests/test_implement.py in under 60 s" (NFR-1).

### CT-3 Parallel suite command (FR-3, FR-4, FR-5) [agent]
- Binding: `.nio/config.json` (existing)
- Like: `.nio/config.json`
- Kind: config
- Shape: `tests.suite` becomes `printf '%s\n' tests/test_*.py | xargs -P8 -I{} sh -c 'uv run python {} || exit 1'`
- Accepts: every `tests/test_*.py`.
- Returns: exit 0 when every file exits 0; else 123. `|| exit 1` turns a file killed by a signal into exit 1, so `xargs` goes on with the other files (research RF-12).
- Rules: "each file to its end even when another failed" (FR-3); "exit the suite non-zero once every file has run" (FR-4). `implement.runner` reads the command as an unknown runner, as it reads the serial one (research RF-5).

### CT-4 The review line records the suite it ran (FR-7) [agent]
- Binding: `src/nio/implement.py:review` (existing)
- Like: `src/nio/implement.py:review`
- Kind: function
- Shape: the `review` history line gains `suite: {"command": <str>, "code": <int or null>}` when the task closes its epic and the review ran a suite command; the key is absent otherwise.
- Returns: as today otherwise.
- Rules: only what FR-7 needs, the command and the exit code (decision D-261106-grjt).

### CT-5 Evidence reuses the review's suite and skips covered journeys (FR-6, FR-7, FR-8, FR-13) [agent]
- Binding: `src/nio/evidence.py:collect` (existing)
- Like: `src/nio/evidence.py:journeys`
- Kind: function
- Shape: two new helpers in the same file, `reused_suite(root, slug, commit, suite) -> dict or None` and `covered(step, suite) -> bool`; `collect` keeps its signature
- Accepts: `reused_suite` reads `.nio/specs/<slug>/history.jsonl` as committed at `commit` (`git show <commit>:<path>`) and the commit's subject.
- Returns: `reused_suite` gives `{"command": suite, "result": "passed", "output": "reused: the review of T-n ran this suite at <sha8> and it exited 0", "cut": 0, "reused": {"task": "T-n", "commit": <sha>}}` when all of these hold: the last `review` line in that history is the task's whose `T-n: <title>` commit `commit` is, has `passed: true`, `suite.command` equal to `tests.suite` and `suite.code` 0. Else None, and `collect` runs the suite in the copy as today. `commit` is `commits_of(...)[0]`, the epic's newest task commit (only `T-n:` commits of the epic's tasks count), so evidence and the reuse look at the same commit; it is the flow's own task commit, which stages every changed path the tests can see (research RF-8): that is the clean tree. `covered(step, suite)` is true when the step's shell words are a prefix plus one path, the path matches a glob word of the suite command (`tests/test_*.py`), and the suite command holds the prefix followed by a space and `{}`, `"$f"` or `$1` (`uv run python {}`). A journey whose every step is covered, while the suite entry `collect` uses passed, is not run and is recorded `{"command": <steps joined by " && ">, "result": "passed", "output": "covered by the suite run at <sha8>", "cut": 0, "covered": true}`; any other journey runs as today, without `covered`.
- Rules: the decision table "evidence suite result"; FR-6, FR-7, FR-8. A fix-check round needs nothing more: a fix task closing the epic gives the same `T-n` commit and review line (FR-13, research RF-10).

### CT-6 Lens parser accepts the two slips (FR-9, FR-10, FR-11) [agent]
- Binding: `src/nio/jury.py:parse_lens` (existing)
- Like: `src/nio/jury.py:parse_lens`
- Kind: function
- Shape: unchanged; `blocks` (its field reader) changes with it
- Accepts: a field bullet `- <Label>: value` whose label is in any case, read as its lower-case field; a `## Findings` section whose whole text is one line matching `none[.!]?` in any case.
- Fails: as today otherwise; also the error "`## Findings` holds none and findings" when the text before the first `### ` is such a none line and findings follow.
- Rules: "exactly one line, `none` in any case optionally followed by one `.` or `!`" (FR-9).

### CT-7 Lens output template shows gap and where (FR-12) [agent]
- Binding: `src/nio/templates/lens-output.md` (existing)
- Like: `src/nio/templates/lens-output.md`
- Kind: file
- Shape: printed by `nio jury template`; after the `- fix:` line, `- gap: missing                # implementation gate only: missing | partial | contradicts | unrequested` and `- where: src/app.py           # implementation gate only: the file or area`.
- Rules: "marked as for that gate only" (FR-12). The parser ignores fields outside its list at the spec, plan and tasks gates.

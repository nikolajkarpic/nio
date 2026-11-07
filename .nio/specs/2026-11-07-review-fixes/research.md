# Research: 2026-11-07-review-fixes

Facts the grill looked up instead of asking.

## Grill session 1 (2026-11-07)

- **RF-1** `collect` merges the run's new lens outputs and, in the same call, applies `<gate>-refuter.md` whenever the file exists and was not collected yet; nothing checks that a batch was asked for. Source: src/nio/jury.py:633-637: "refuter = jury / f\"{gate}-refuter.md\"\n    if refuter.exists():"
- **RF-2** The refuter batch is printed by `collect` itself (so by both `nio jury next` and `nio jury collect`); `nio jury next` also writes it to `packs/refuter.md`. Source: src/nio/jury.py:647-649: "if pending:\n        out += [\"\", f\"## Refuter batch: confirm or refute each, in"
- **RF-3** When the jurors start, `packs/step.json` already records the version they judge (the artefact's blob, or the epic's commit at the implementation gate). Source: src/nio/jury.py:1350-1351: "sj.write_text(json.dumps({\"gate\": gate, \"round\": led[\"round\"], \"version\": version_now(root, slug, gate),"
- **RF-4** `records.git` decodes git's output as text (strict UTF-8, universal newlines); `land` and `shelve` take the patch from it and write it with `write_text`. Source: src/nio/records.py:48: "r = subprocess.run([\"git\", *args], cwd=root, capture_output=True, text=True)"
- **RF-5** No other caller writes git output back as a patch or file: the other `diff`/`show`/`cat-file` callers read names or NIO's own text files. Source: src/nio/implement.py:368: "diff = records.git(tree, \"diff\", \"--cached\", \"--binary\", \"--no-renames\", since, full=True)[1]"
- **RF-6** After a rejected round only lenses with a fix to check re-run; when none has one, `_begin` still prints "run each juror" with no juror listed, and the outcome stays `rerun`. Source: src/nio/jury.py:450-451: "if any(o == \"rejected\" for _, o in led[\"recorded\"]):  # a re-review or the final check is next\n        rerun = {lens for lens in lenses if pack_ids(led, lens)}"
- **RF-7** An approved or closed gate whose artefact changed already re-runs every lens that voted, on fix-check packs. Source: src/nio/jury.py:455-458: "an approved or closed gate whose artefact changed since (a change request, #57 FR-35, FR-47): every lens that"
- **RF-8** `selfcheck.main` reads every argument as a test name, while `test_pack.py` reads `-v` itself and CLAUDE.md documents it. Source: tests/selfcheck.py:8: "names = sys.argv[1:]"
- **RF-9** Every quickstart step parsed by `journeys` has an `Expected:` block, and the covered-journey test expects `contains: ok` to count as covered. Source: tests/test_evidence.py:412: "Expected:\n   ```\n   contains: ok"
- **RF-10** `one_test` knows only unittest and pytest; a self-check suite is run per file through `xargs`/`sh -c`, so a per-test command needs the suite's per-file prefix parsed out and a rule for which runners take names. Source: src/nio/evidence.py:110-116: "if m := re.match(r\"(.*\\bunittest)\\b\", suite or \"\"):"
- **RF-11** The orchestrator does what each `next:` line of `nio jury next` says, then calls it again. Source: skills/jury/SKILL.md:61: "prints its results and ends in a `next:` line; do what that line says, then call again"
- **RF-12** The maintainer runs the self-checks by file, `test_pack.py` with `-v`. Source: CLAUDE.md:9: "`uv run python tests/test_pack.py` (`-v` prints each pack)"

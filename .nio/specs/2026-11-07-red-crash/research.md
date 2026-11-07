# Research: 2026-11-07-red-crash

## Grill session 1 (2026-11-07)

- **RF-1** Red names the self-check runner only from its `ran N tests, M failed` line in the output, so a run that crashed before that line has no known runner, and an unknown runner has no wrong reason. Source: src/nio/implement.py:52: "return found or (\"self-check\" if re.search(r\"^ran \d+ tests?, \d+ failed$\", output, re.M) else None)"
- **RF-2** `wrong_reason` returns no reason for a runner it doesn't know. Source: src/nio/implement.py:59: "if not r:\n        return \"\""
- **RF-3** The self-check runner always ends with its `ran` line once `main` runs; a SyntaxError or failed import in the test file stops Python before `main` runs, with a traceback whose last line names the error. Source: tests/selfcheck.py:24: "print(f\"ran {len(run)} tests, {failed} failed\")"

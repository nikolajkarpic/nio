# Architecture: extensions

Settles only what the plan skill's stop list sends here. Each item follows from the approved spec, its decisions, or
the existing code, and this file records where. It adds no design of its own. The architecture stage is not built
(`arch_grilling` skipped on the record), so the plan driver wrote it under the human's delegation (2026-11-15:
"take recommended answers for all questions"), as `2026-11-08-project-onboarding` did; the plan jury judges it with
the plan. Read-only to the plan; changing it takes a change request.

## New modules and folders (stop list 2)
- `src/nio/extensions.py`: add, list and remove (FR-1 to FR-7, FR-37, FR-39), manifest checks (FR-5, FR-11, FR-20,
  FR-22, FR-26, FR-40, NFR-2), the extension record and its hash (FR-8, FR-21, FR-38), trigger rules (FR-12, FR-14,
  FR-15) and hooks (FR-25 to FR-27). One module per concern, as `agents.py` holds the cards and `hooks.py` the git
  hooks. It imports `records` and `implement` (for `implement.run`, the timed command runner); `flow`, `jury` and
  `agents` import it, never the other way, except that firing a hook appends its line through `flow.record`
  (imported inside the function, as `plan.approved` imports `jury`).
- `src/nio/shipped/<name>/`: NIO's shipped extensions, package data read through `importlib.resources` like
  `src/nio/agents` (RF-8). The folder is not named `extensions/`, which would shadow the module's name for readers.
  The first one is `src/nio/shipped/e2e/` (FR-28, FR-35): `manifest.json`, `skills/e2e/SKILL.md`,
  `agents/e2e-tester.md` and `check.py`, the extension's own check script.
- `tests/test_extensions.py`: the self-check for the module and the flow with extensions; `tests/test_extensions_e2e.py`
  runs real Playwright and a real model only with `NIO_E2E=1`, as `tests/test_auto_e2e.py` does.

## New stored data (stop list 3)
- `.nio/extensions/<name>/`: the copied extension, committed (FR-1, FR-8; #162 decision 5).
- `.nio/extensions/record.json`: `{name: {"source", "version", "hash"}}`, the spec's Extension record (Key entities),
  committed; JSON like `.nio/config.json` (RF-12).
- `manifest.json` in each extension: the spec's Manifest, JSON (RF-12).
- New history line kinds in `history.jsonl`, written only through `flow.record`: `hook` (FR-27); an extension step's
  failed check is a `fail` line (FR-17), the kind the flow already writes.
- An extension gate's ledger is `jury/<extension>.<step>.json`, the ledger every gate already has.

## Interfaces used outside this feature (stop list 4)
- New `nio extensions add <path | git URL | name>`, `nio extensions list`, `nio extensions remove <name>`, registered
  in `cli.py` like the other command groups.
- The flow's stage table becomes per project: `flow.table(root)` returns the built-in `STAGES`, `GATES`, `SKILL`,
  `INPUTS` and `EXIT` with the active extensions' stages spliced in; every reader in `flow.py` and `cli.py` uses it.
  With no extension it returns the built-in tables unchanged (NFR-3).
- `nio flow done`, `nio flow next` and `nio jury ... <gate>` accept extension stage and gate names: a step is
  `<extension>.<step>`, its gate stage `<extension>.<step>.jury`, its jury gate `<extension>.<step>`.
- `agents.layers` gains the active extensions' `agents/` folders between the shipped and the personal layer (FR-24).
- `evidence.one_test` and `implement.RUNNERS` learn Playwright (RF-7), by test file, so one epic run and the pr
  evidence can mix runners.

## No new dependency (stop list 1)
Git URLs are fetched with the `git` CLI through `records.git`; copying uses `shutil`, hashes `hashlib`, commands
`implement.run`. Playwright is the target project's dependency, run through `npx`; NIO doesn't depend on it.

## Approaches with trade-offs (stop list 5)
None left open: the spec and its decisions settle add-only steps after a named step (FR-9), JSON manifests (RF-12),
shell hooks that only report (D-261115-ggt2) and Playwright only (grill Q5).

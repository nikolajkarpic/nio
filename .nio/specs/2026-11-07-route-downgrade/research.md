# Research: 2026-11-07-route-downgrade

## Grill session 1 (2026-11-07)

- **RF-1** The flow reads spec.md's route in two places: `skips` (which stages are skipped) and `kind` (which folders the flow drives; every writing command calls `refuse`, which uses it). Source: src/nio/flow.py:701: "Legacy and unsupported folders are never written (FR-29, FR-50)."
- **RF-2** `plan.py`, `tasks.py` and `spec.py` read the header to pick a template and its rules; they move no stage, so the flow's guard covers them. Source: src/nio/tasks.py:32: "return records.parse(spec.path(root, slug))[0].get(\"route\")"
- **RF-3** A history line's `evidence` takes any extra key, so the route can ride on the first line written without a new line kind. Source: src/nio/flow.py:149: "\"evidence\": {\"paths\": [], \"verdict\": \"\", \"output\": \"\", **(e.get(\"evidence\") or {})}"
- **RF-4** The history file is created by the first `record` call, which `nio flow start` or the first `nio flow done` makes. Source: src/nio/flow.py:121: "def record(root, slug, entries, state, who, run, at=None):"
- **RF-5** A spec-jury round is kept in the spec gate's ledger as its `round`, which only a full route reaches. Source: src/nio/jury.py:617: "led[\"round\"] += 1"

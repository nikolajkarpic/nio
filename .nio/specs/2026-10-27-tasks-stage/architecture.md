# Architecture: tasks stage

Settles only what the plan skill's stop list sends here. Each item is already decided elsewhere, and this file records
where. It adds no new design. Read-only to the plan; changing it takes a change request.

## New modules and folders (stop list 2)
- `skills/tasks/SKILL.md`: the `@nio:tasks` skill, one folder per skill as CLAUDE.md's repo layout says
  ("`skills/<name>/SKILL.md`: the product. One folder per skill").
- `src/nio/tasks.py`: the tasks stage's CLI checks (`nio new tasks`, `nio check tasks`, `nio task show`), one module per
  stage as `spec.py` and `plan.py` already are, wired into `src/nio/cli.py` the same way.
- `src/nio/templates/tasks.md`: the `tasks.md` template, next to `plan.md` and the other plan templates.
- `src/nio/agents/tasks-drafter.md`, `evaluator.md`, `executability.md`: agent cards in the existing cards folder
  (spec FR-41, FR-43; #36 and #47 named them).

## Stored data (stop list 3)
- `tasks.md`, one per spec, is a spec artefact like `plan.md`: plain markdown under `.nio/specs/<slug>/`, no schema.
- Each epic's implementation-jury ledger, `jury/implementation-E-n.json` and `.md`, uses the existing ledger format.
  Its path and verdict subject come from the gate name, as `jury.folder` and `jury.verdict` already build them
  (spec FR-31).
- Task status stays out of scope: it lives in the CLI's state (#45), not built here (spec FR-23, Non-goals).

## Interfaces used outside this feature (stop list 4)
- Model tiers: `agents.TIERS` gains `frontier` above `max`. Each host maps tiers to models in config (Claude: Haiku,
  Sonnet, Opus, Fable). A host with no model for a tier uses the nearest lower one it maps, with a warning, for every
  card and task. Decided in the spec's grill, decision D-261027-vi67 (spec FR-17, FR-52).
- The jury: `jury.CORE["tasks"] = ["executability"]` (#47). `jury.GATES["tasks"]` holds `tasks.md` plus the plan's
  four files and the spec, so a later plan or spec change withdraws the tasks approval, as the plan gate holds the
  spec (spec FR-56; plan-jury FR-47).
- The tasks stage reads the plan's approval only through `nio check plan <slug> --approved` (spec FR-2; plan-jury
  CT-16).

## No new dependency (stop list 1)
Nothing beyond the Python standard library and `ruamel.yaml`, which the CLI already uses.

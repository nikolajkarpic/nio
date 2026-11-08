# Architecture: explainer

Settles only what the plan skill's stop list sends here. Each item follows from the approved spec, the decisions it
cites, or the existing code, and this file records where. It adds no design of its own. Read-only to the plan; changing
it takes a change request.

## New modules and folders (stop list 2)
- `src/nio/explain.py`: `nio check explainer` (FR-6, FR-7, FR-8, FR-11, FR-15, FR-20), the staleness of a plan
  explainer (FR-16, FR-24) and the one exact mermaid-cli version `nio` names (FR-9). One module per stage family, as
  `spec.py`, `plan.py` and `tasks.py` are, each with its own `check(root, slug, gate, base)` returning (errors, notes)
  (RF-6, RF-15). It reuses what exists: contract IDs through `implement.defs` (RF-14), hashes through `flow.sha`
  (RF-12), the config through `records.config` (RF-11). Not inside `plan.py`: that module checks the plan files the
  jury judges, and the explainer is neither judged nor gated (FR-17).
- `skills/explain/SKILL.md`: the skill the spec's Summary names, with its Mermaid cheat-sheet and credits (FR-22). One
  folder per skill is the repo's layout (CLAUDE.md, "Repo layout"); nothing registers it, and `tests/test_talk.py`
  picks it up for the "Talking to the human" block (RF-16). The README's skill table gains its row.
- `tests/test_explain.py` and `tests/fixtures/explain/`: one self-check script per module, fixtures beside the others
  (RF-15; `tests/fixtures/plan/` is the precedent).

## New stored data (stop list 3)
- `.nio/specs/<slug>/explainer.md` (Key entity Plan explainer). Besides the diagrams and walk-throughs it stores, in
  the file itself and in no side file:
  - one source line per input, spec.md, plan.md and contracts.md, as `path@<first 12 hex of its SHA-256>` (FR-24),
    in the onboarding plan's form `(source: <path>@<hash>)` with the path relative to the repo root, so one pattern
    reads both kinds of source record (RF-1; `.nio/specs/2026-11-08-project-onboarding/contracts.md` CT-7). No code is
    shared with `onboard.py`, which doesn't exist yet;
  - the list of SVGs this run wrote (FR-26);
  - the marker on a drill-down section written for an earlier plan (FR-25), and the note when images weren't rendered
    or a block is broken (FR-10, FR-11).
  The exact line shapes are the contracts' to state.
- `.nio/specs/<slug>/explainer-<name>.svg`: one per rendered block, committed beside the explainer (FR-9). The
  `explainer-` prefix is what FR-26 lets a re-run delete.
- `.nio/research/<date>-<topic>-explainer.md`, or `-explainer-<n>.md` from 2 (FR-14, FR-27), with its SVGs beside it
  and the topic text as typed stored in the file (FR-27). The folder exists already.
- `explain.format` in the config (FR-19, Key entity explain.format), default `mermaid`. Read with
  `records.config(root)`, so any of the three layers may set it; no config schema exists to extend (RF-11).

## Interfaces used outside this feature (stop list 4)
- `nio check explainer <slug | path to a topic explainer>`: `explainer` joins the `check` choices in `cli.py` and its
  dispatch map (RF-6). A path runs the render check alone (FR-15). `--gate` and `--base` change nothing for it.
- `nio status` appends `explain.stale` lines after the index lines it prints today: one
  `stale: explainer.md (spec, plan or contracts changed)` per stale plan explainer, with the re-run suggestion (FR-16,
  RF-7). Its exit status doesn't change (AC-21).
- `nio flow next` adds one suggestion line for `@nio:explain` once the plan gate has closed as approved (FR-18). The
  stage map, the guards and the gates stay as they are (FR-17, AC-23; RF-8).
- `nio explain finish <explainer path>` and `nio explain topic "<text>"`: one new command group in `cli.py`, run by the
  skill, so the mechanics a model can't do the same way on every host live in code (the human, Q13): the source
  hashes and the drill-down marker (FR-24, FR-25), rendering with the pinned mermaid-cli (FR-9, FR-10, FR-11),
  deleting only its own old images (FR-26), the "Read first" line in quickstart.md (FR-5) and the topic file name
  (FR-14, FR-27). The skill writes the diagrams and the prose and calls these.
- The plan gate reads quickstart.md without its single `Read first: explainer.md` line, as it already reads tasks.md
  without its Fixes sections: `jury.planned` drops that line, the gate's artefact reads every file through it, and the
  flow's change scan compares quickstart.md through it as it does tasks.md. So `@nio:explain` writing the line (FR-5)
  neither withdraws the plan's approval nor sends the effort back (FR-17; the human, Q12; RF-9, RF-10). A quickstart
  without the line reads as it does today, so versions judged before this change compare equal.
- `nio flow next` shows its suggestion only while the spec folder has no `explainer.md` (the human, Q14).

## New dependency (stop list 1)
- `@mermaid-js/mermaid-cli`, pinned to one exact version (11.4.2, the one measured in RF-3), run through
  `npx -y @mermaid-js/mermaid-cli@<version>` (FR-9). Not a Python dependency: `pyproject.toml` is unchanged. It is
  optional at run time: without `npx` on the PATH, found with `shutil.which` as `agents.hosts` finds CLIs (RF-13), the
  explainer is text only and the check skips rendering with a note (FR-11, NFR-2). A run that fails without a
  `Parse error` is the renderer that couldn't be fetched; one with it is a broken block (RF-3, FR-11).
- The check renders each block on its own, into a temporary folder, so it can name the broken one (FR-8). The cost,
  about 3 s a block once cached, is the risk the spec accepted ("Risks and evidence against", RF-3, RF-4).
- Everything else is the standard library: `hashlib` through `flow.sha`, `subprocess`, `shutil`, `tempfile`, `re`.

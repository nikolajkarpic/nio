# Research: 2026-11-07-refuter-batch-forge

## Grill session 1 (2026-11-07)

- **RF-1** The refuter file is applied in `collect`, shared by every gate (spec, plan, tasks and the implementation gates), after all new lens outputs of the call are merged; retry jurors, fix-check lenses and escalation jurors all write lens outputs into the same run. Source: src/nio/jury.py:654: "refuter = jury / f\"{gate}-refuter.md\""
- **RF-2** A batch is recorded in two places, both through `ask_refuter`: `collect` when it prints the batch (ask=True) and `refuter_pack` when `nio jury next` writes the refuter's pack. Source: src/nio/jury.py:1394: "ask_refuter(root, slug, gate, run, re.findall(r\"^### (J-\\d+)\""
- **RF-3** `land`'s only caller turns a returned error into a blocked task (worktree removed, claim released, patch kept); an exception would escape `green` with the claim and worktree left as they were. Source: src/nio/implement.py:752: "if err: records.git(root, \"worktree\", \"remove\", \"--force\", str(tree), full=True)"

# Architecture: full-auto run

Settles only what the plan skill's stop list sends here (RF-6 to RF-14). Each item follows from the approved spec, the
human's calls on this note (2026-11-08) or the existing code, and this file records where. Items marked "(agent call)"
are the smallest glue the agent chose to make a human call work; the human approves them with this note. Read-only to
the plan; changing it takes a change request.

## New modules and folders (stop list 2)
- `skills/auto/SKILL.md`: the `@nio:auto` driver (FR-5, FR-6, FR-25, FR-27, FR-35). It loops `nio flow drive`,
  `nio flow next`, the skill `next` names (in a fresh subagent when the host has them), and `nio flow done`, until
  the effort pauses, is suspended or is done; at done it runs `nio flow pr`. It starts long jury and test runs in the
  background and waits for the completion notice, never polling. One folder per skill, as `skills/tasks/` and
  `skills/implement/` were added (RF-6). No new CLI loop (spec non-goal).
- `src/nio/agents/fixer.md`: the one `nio-fixer` card, rendered by `nio agents sync` like every other card (FR-9 to
  FR-12, FR-36, FR-37). It runs in a fresh context per round, edits only the gate's files for refuter-confirmed
  blockers and majors, and disposes each fix `--by auto`. When a fix would change a `[human]` line, drop or remove an
  FR, AC or story, add a Non-goal or change `risk:`, it edits nothing for that finding and disposes it `held`. At an
  epic's gate there is no fixer: confirmed findings already become fix tasks that `@nio:implement` runs (FR-16).
  Rejected: the fixer as driver instructions, since the driver would then fix and judge in one growing context.
- No new Python module: the code lands in `flow.py`, `jury.py`, `spec.py` and `cli.py`, as each FR's existing home.
  Tests go in the existing `tests/test_flow.py`, `test_jury.py`, `test_spec.py` and `test_agents.py`.

## Stored data (stop list 3)
- `.nio/specs/<slug>/driver.lock`: the driver claim (FR-29, FR-38). Git-ignored by adding `driver.lock` to the lines
  `flow.lock` already writes into the effort's `.gitignore`. JSON `{by, host, at}`, created with `O_EXCL` so of
  two drivers exactly one gets it, taken over the way `flow.lock` is (rename, re-check, create) once `at` is over 30
  minutes old. There is no process test: every `nio` call is a short-lived process, so the claim has none to name
  (the human's call, 2026-11-08; change request C-261108-mplt against FR-38 and AC-38). A refresh rewrites `at` and writes no history line (RF-7). Rejected:
  `state.json`'s `claims`, since each write there needs a history line.
- `.nio/specs/<slug>/state.json`: no new key. `auto` already exists (RF-11).
- `.nio/specs/<slug>/history.jsonl`: three new line kinds, written by `flow.record` like every other (RF-8):
  - `grant`: auto switched on; `from`/`to` the stage, `who` the human, and `evidence.ran_in: {host, model}` read from
    the environment of the call, `unknown` for what it can't detect (the human's call, 2026-11-08) (FR-3, FR-30, AC-42);
  - `switch_off`: auto switched off by the human (FR-32);
  - `raise`: on resuming a cap or stuck suspension, `evidence: {gate, rounds: 2, cap: 2}` (FR-40).
  A pull request that can't be opened writes the existing `pause` kind with `waiting.why` starting `pull request:`
  (FR-24) (agent call).
- The jury ledger `jury/<gate>.json`: `by` may be `auto`, and a finding may be disposed `held` (only `--by auto`), its
  note naming the `[human]` line, the cut or the risk change (FR-10, FR-11) (agent call: the fixer's only way to say
  "this one is the human's" without touching the file). No other field.
- No new config key: `budgets.juries` and `budgets.subagents` already exist (flow-state FR-40, RF-12).

## Interfaces used outside this feature (stop list 4)
- `nio flow start <slug> --auto --by human` and `nio flow done drafting <slug> --auto --by human` grant auto (FR-1,
  FR-2, FR-31). Refused for any `--by` but `human` (FR-30) and while `nio check spec` fails, naming the check (FR-4).
- `nio flow manual <slug> --by human`: switches auto off with a `switch_off` line; refused for any other `--by`
  (FR-32, D-261108-txqj). A fix under way finishes; the next jury round waits, since `done` and the stop list read
  `auto: false`.
- `nio flow drive <slug> --by "<role> / <host> / <model>"`: takes or refreshes the driver claim and prints
  `driving: <slug>`; refused, naming the running driver, when a claim under 30 minutes old names another (FR-29, FR-38).
  `--release` drops it when the driver stops. Writes no history.
- `nio flow pr <slug> --by "<...>"`: at `done` under auto, builds the run report, pushes `nio/<slug>` and opens the
  pull request with `gh pr create`, never merging (FR-20 to FR-23). When one is open already it prints its URL and
  does nothing (FR-41). On failure it records the `pause` above and prints the report (FR-24). `gh` is an external
  tool like `git`, called through `subprocess`; no Python dependency.
- `[auto]` joins `spec.TAG` and `spec.TAGS`, so `nio check spec`, `plan` and `tasks` accept it; the spec gate treats
  it like `[human]` whatever the flag (FR-13, FR-14, D-261108-fgeo). The spec jury's packs list the `[auto]` IDs for
  judging (FR-15).
- `jury.BY` gains `auto`; `nio jury dispose --by auto` is refused unless the effort's auto flag is on. `jury.check`
  passes the flag to `composed`, which under auto (FR-9, FR-17, FR-34, FR-39):
  - leaves minors out of what blocks or hands over, at every gate, as it already does at an epic's gate; open minors and
    refuted findings are listed in the report as accepted;
  - composes `rejected`, not one list for the human, while a confirmed blocker or major is open, so the fixer acts;
  - composes `human` for a `held` finding, for a blocker or major still pending after the refuter's output for its
    round was collected, for what the final fix check flagged, and when the round check below hits.
- Round check, in `jury.py`: compares the gate's artefact now with the version its last round judged (git keeps it,
  `jury.blob(..., write=True)`), by item ID: a `[human]` item changed or gone, an FR, AC or story gone, a Non-goals
  entry added, or `risk:` changed. A hit makes the outcome `human`, naming each, before any new round starts (FR-12,
  FR-36, FR-37). It is the CLI's word, never the fixer's.
- The stop list (`flow.stops`), under auto: pauses when the gate's ledger composed `human` (once per gate and round, as
  its round pause is today); counts the epics' ledgers in `used`; caps juries at `budgets.juries` or else 2 × the
  route's gates (spec, plan, tasks on the full route, tasks on lite, plus one per epic once `tasks.md` has epics); adds
  2 to the cap and to the stopped gate's 3-round limit per `raise` line (FR-18, FR-19, FR-40, RF-12). `nio flow start`
  writes the `raise` line when it resumes a cap or stuck suspension of an auto effort.
- Skills and agent cards: the shared "Flow state:" line in every skill and card that has it gains "Never pass
  `--by human`: only the human grants or revokes auto, or approves a gate." (FR-30). `@nio:grill` under auto settles
  each open point and `[default]` as `[auto]` and asks nothing, logging an `## Auto` entry in `grill.md` (FR-7, FR-8).
  The "Talking to the human" block is unchanged.

## No new dependency (stop list 1)
Nothing beyond the Python standard library and `ruamel.yaml`. `gh` and `git` are tools on the human's machine, as
pull requests are opened with `gh` by hand today (RF-4, RF-14).

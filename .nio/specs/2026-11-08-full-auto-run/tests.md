---
slug: 2026-11-08-full-auto-run
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: full-auto run

Shared setup, named below: `effort(stage)` and `approve()` are `tests/test_flow.py`'s fixture helpers (refunds spec
`S`, a git repo); `grant(root)` is `flow.start(root, S, "human", auto=True)`; `first_review()`, `fix()`, `CONFIRM`,
`REFUTE`, `MAJOR`, `MINOR` are `tests/test_jury.py`'s. "The fixer acts" means the test does what CT-17 says the card
does: edit the file, then `nio jury dispose ... --by auto`. The e2e tests live in `tests/test_auto_e2e.py`, run only
with `NIO_E2E=1` like `tests/test_tasks_e2e.py`, on a copy of the refunds fixture, driving
`claude -p "/nio:auto <S>"` with `gh` replaced on `PATH` by a stub that appends its argv to `gh.log` and prints
`https://example.test/pr/1`, and a bare local repo as `origin`.

## Acceptance tests

### TC-1 Start grants auto, only with --by human (AC-1; unit) [agent]
- File: `tests/test_flow.py:test_auto_grant_on_start` (new)
- Covers: CT-1, CT-4
- Setup: `effort("grilling")` (draft passes `nio check spec`).
- Action: `nio flow start S --auto` with no `--by`; then `nio flow start S --auto --by human`.
- Assert: the first exits non-zero and `state.json` has `auto: false` with no new history line; the second exits 0, `auto: true`, and the last history line is `kind: grant`, `who.role: human`, `from` and `to` `grilling`.

### TC-2 Done drafting grants auto (AC-2; unit) [agent]
- File: `tests/test_flow.py:test_auto_grant_on_done_drafting` (new)
- Covers: CT-2, CT-4
- Setup: `effort("drafting")` with a draft that passes `nio check spec`; a second copy.
- Action: `nio flow done drafting S --auto --by human`; on the copy `nio flow done drafting S --auto --by "orchestrator / test / test"`.
- Assert: first: `auto: true`, history ends with the `pass` drafting → researching, its skips, then a `grant` line; copy: non-zero exit, `auto: false`, no `pass` and no `grant` line added.

### TC-3 A failing draft can't go auto (AC-3; unit) [agent]
- File: `tests/test_flow.py:test_auto_refused_on_failing_draft` (new)
- Covers: CT-1
- Setup: `effort("drafting")` with `## Summary` emptied in `spec.md`.
- Action: `nio flow start S --auto --by human`.
- Assert: non-zero exit, output holds `nio check spec` and `Summary`; `auto: false`; history line count unchanged.

### TC-4 The driver runs every stage (AC-4; e2e) [agent]
- File: `tests/test_auto_e2e.py:test_driver_reaches_done` (new)
- Covers: CT-16, CT-6
- Setup: refunds fixture at spec_jury with a spec the lenses approve (the `tests/test_lenses.py` clean spec), granted.
- Action: run the driver once.
- Assert: history has, after the `grant`, a `pass` line for spec_jury, planning, plan_jury, tasking, tasks_jury and implementing in that order, and no line whose `who.role` is `human`.

### TC-5 The plan gate's third round pauses the driver: regression guard (AC-5; integration) [agent]
- File: `tests/test_flow.py:test_auto_round_limit_pauses` (new)
- Covers: CT-6, CT-16
- Setup: `effort("plan_jury")`, granted; plan ledger at round 3, outcome rejected, one open major; no `budgets`.
- Action: `nio flow next S --by BY`.
- Assert: `state.json` `waiting.why` holds `plan jury ran 3 rounds`; no `pass` line after it; the output holds the reason and `nio flow start S --by human`; `skills/auto/SKILL.md` step 4 holds `waiting_for_human`, `suspended` and `Talking to the human`. The pause itself is today's code, so this guards it from regressing under auto; TC-56 checks the driver's last message.

### TC-6 Each stage runs in a fresh subagent (AC-6; e2e) [agent]
- File: `tests/test_auto_e2e.py:test_driver_reaches_done` (new)
- Covers: CT-16
- Setup: TC-4's run, with the usage hook installed (`nio usage install`).
- Action: read `usage.report(root, S)` after the run.
- Assert: one `agent_called` event per stage skill the history passed (spec_jury … implementing), each with the driver's session as parent.

### TC-7 Without subagents the driver still finishes (AC-7; e2e) [agent]
- File: `tests/test_auto_e2e.py:test_driver_without_subagents` (new)
- Covers: CT-16
- Setup: TC-4's fixture; `claude -p` run with the `Task`/`Agent` tool disallowed.
- Action: run the driver once.
- Assert: history ends with `implementing → done`; the run's usage has no `agent_called` event for a stage skill.

### TC-8 Resume keeps auto: regression guard (AC-8; unit) [agent]
- File: `tests/test_flow.py:test_auto_resume_keeps_auto` (new)
- Covers: CT-7, CT-3
- Setup: `effort("plan_jury")`, granted, then paused (a `pause` written through `stop_line`).
- Action: `nio flow start S --by human`; `nio flow next S`.
- Assert: `auto: true`; next prints `skill: @nio:jury`.

### TC-9 A second driver is refused (AC-9; integration) [agent]
- File: `tests/test_flow.py:test_auto_second_driver_refused` (new)
- Covers: CT-5
- Setup: granted effort; `nio flow drive S --by "driver / a / m"`.
- Action: `nio flow drive S --by "driver / b / m"` (no token).
- Assert: exit 1, output holds `driver / a / m`; `driver.lock` unchanged byte for byte; history line count unchanged.

### TC-10 The driver waits on the completion notice (AC-10; e2e) [agent]
- File: `tests/test_auto_e2e.py:test_driver_waits_without_polling` (new)
- Covers: CT-16
- Setup: TC-4's run with `--output-format stream-json` saved as the transcript.
- Action: read the transcript and the spec ledger.
- Assert: no `nio flow done spec_jury` command before the ledger's round closes (its verdict record's time); between each backgrounded `nio jury` command and its completion notice, no Bash call runs `nio flow`, `nio jury` or reads `jury/*.json`.

### TC-11 A new driver carries on with no gate twice (AC-11; integration) [agent]
- File: `tests/test_flow.py:test_auto_takeover_repeats_no_gate` (new)
- Covers: CT-5, CT-16
- Setup: granted effort with spec_jury passed (approval commit), at planning with plan files from `tests/fixtures/plan/`; `driver.lock` with `at` 31 minutes ago.
- Action: `nio flow drive S --by "driver / b / m"`; then `nio flow done planning`, the plan gate approved (`approve(root, S, "plan")`) and `nio flow done plan_jury` as the driver does.
- Assert: drive exits 0 naming `took over`; history has exactly one `pass` from spec_jury and one from plan_jury.

### TC-12 A confirmed major is fixed and the next round starts (AC-12; integration) [agent]
- File: `tests/test_jury.py:test_auto_fixer_starts_next_round` (new)
- Covers: CT-11, CT-12, CT-17
- Setup: `first_review(MAJOR, CONFIRM.format(n=1))` on an auto effort (granted state).
- Action: the fixer acts (edit `spec.md`, `nio jury dispose S spec J-1 spec-fix --by auto --note "FR-3 fixed"`); `nio jury next S spec`.
- Assert: `spec.md` blob changed; J-1 `disposition: spec-fix`, `by: auto`; the step asks for the fix check; after collecting it the ledger's `round` is 2.

### TC-13 A fix touching a [human] line pauses (AC-13; integration) [agent]
- File: `tests/test_jury.py:test_auto_held_human_line` (new)
- Covers: CT-11, CT-12, CT-6, CT-17
- Setup: auto effort, first review with a confirmed blocker J-1 whose fix is FR-1's wording (`[human]`).
- Action: the fixer acts: `nio jury dispose S spec J-1 held --by auto --note "[human] line FR-1"`; `nio jury check S spec --record`; `nio flow next S --by BY`.
- Assert: `spec.md` unchanged; outcome `human` with `held for the human: J-1: [human] line FR-1`; status `waiting_for_human` holding `J-1` and `FR-1`; the fixer card holds `held` and `[human]` in one line.

### TC-14 A fix dropping a story pauses (AC-14; integration) [agent]
- File: `tests/test_jury.py:test_auto_held_scope_cut` (new)
- Covers: CT-11, CT-12, CT-17
- Setup: as TC-13 with a confirmed major J-1 whose fix drops US-2.
- Action: `nio jury dispose S spec J-1 held --by auto --note "drops US-2"`; check `--record`; `nio flow next S --by BY`.
- Assert: status `waiting_for_human` holding `J-1` and `US-2`; `### US-2` still in `spec.md`; the card holds `user story` and `Non-goals` in its stop bullet.

### TC-15 A changed [human] line stops before the next round (AC-15; unit) [agent]
- File: `tests/test_jury.py:test_auto_round_check_human_line` (new)
- Covers: CT-13, CT-12
- Setup: auto effort, first review judged `spec.md`; then FR-1's text changed (it ends `[human]`) and J-1 disposed `spec-fix --by auto`.
- Action: `jury.cuts(root, S, "spec", led)`; `nio jury check S spec --record`.
- Assert: `cuts` returns `["[human] line changed: FR-1"]`; outcome `human` naming `FR-1`; ledger round unchanged; no fix-check pack written.

### TC-16 The grill under auto settles everything as [auto] (AC-16; integration) [agent]
- File: `tests/test_auto_e2e.py:test_grill_under_auto` (new)
- Covers: CT-18, CT-9
- Setup: `effort("grilling")` granted, its spec with OP-1, OP-2 and one `[default]` item FR-2.
- Action: run `@nio:grill` on it with `claude -p`.
- Assert: no `## Open points`; FR-2 ends `[auto]`; no `[default]` left; `retired` holds OP-1 and OP-2; two new items end `[auto]`; `grill.md` has an `## Auto ·` entry and no new `## Asked ·`; `skills/grill/SKILL.md` has `## Under auto`.

### TC-17 [auto] items pass the gate (AC-17; unit) [agent]
- File: `tests/test_spec.py:test_auto_tag_passes_gate` (new)
- Covers: CT-9
- Setup: `tests/fixtures/spec/spec.md` with OP-1 removed and each `[default]` replaced by `[auto]`; `state.json` `auto: true`.
- Action: `nio check spec <S> --gate`.
- Assert: exit 0.

### TC-18 [auto] items still pass after auto is off (AC-18; unit) [agent]
- File: `tests/test_spec.py:test_auto_tag_passes_gate` (new)
- Covers: CT-9, CT-3
- Setup: TC-17's spec; then `flow.manual(root, S, "human")`.
- Action: `nio check spec <S> --gate`.
- Assert: exit 0; output lists no `[auto]` item as a proposal or error.

### TC-19 The spec jury's packs list the [auto] items (AC-19; unit) [agent]
- File: `tests/test_jury.py:test_auto_defaults_in_packs` (new)
- Covers: CT-10
- Setup: TC-17's spec with FR-2 and AC-1 tagged `[auto]`.
- Action: `nio jury next S spec`; read every `packs/<lens>.md`.
- Assert: each holds `Defaults the run chose (judge each): AC-1, FR-2` (spec order: the stories come before the requirements).

### TC-20 E-1 is fixed and re-judged before E-2 starts (AC-20; integration) [agent]
- File: `tests/test_flow.py:test_auto_epic_fix_before_next_epic` (new)
- Covers: CT-12, CT-16
- Setup: an implementing effort (the implement fixtures of `tests/test_implement.py`) with E-1 and E-2, granted; E-1's tasks done; its first round confirms a major (CLI finding, confirmed).
- Action: `nio jury check S implementation-E-1 --record`; `nio flow next S`; finish the fix task; a second round approves; `nio flow done implementation-E-1`; `nio flow claim S`.
- Assert: the first check is `rejected` with a fix task appended; `next` names the fix task, not an E-2 task; E-1's ledger `round` is 2; E-1's `epic` line comes before the first `claim` of an E-2 task.

### TC-21 Minors and refuted findings close the gate unfixed (AC-21; integration) [agent]
- File: `tests/test_jury.py:test_auto_minor_and_refuted_accepted` (new)
- Covers: CT-12, CT-14
- Setup: auto effort; `first_review(MAJOR + MINOR, REFUTE.format(n=1))`.
- Action: `nio jury check S spec --record`; then `flow.report(root, S)`.
- Assert: outcome `approved`; `spec.md` unchanged; no finding has `by: auto`; the report's `## Accepted as risk` lists J-1 and J-2.

### TC-22 The run opens a pull request and never merges (AC-22; e2e) [agent]
- File: `tests/test_auto_e2e.py:test_driver_reaches_done` (new)
- Covers: CT-15, CT-16
- Setup: TC-4's run.
- Action: read `gh.log` and `git rev-parse main` before and after.
- Assert: `gh.log` holds exactly one `pr create --head nio/<S>` and no `merge`; `main`'s head unchanged.

### TC-23 The report links every item to its record (AC-23; integration) [agent]
- File: `tests/test_flow.py:test_auto_report_links` (new)
- Covers: CT-14
- Setup: a done effort whose history has spec, plan and tasks passes with verdict IDs and one `epic` line; spec ledger J-1 disposed `spec-fix --by auto`; spec FR-2 tagged `[auto]`.
- Action: `flow.report(root, S)`.
- Assert: every gate in history appears on a line with its `V-` ID or `history line <n>`; J-1 under `## Fixed by the run` with a `V-` ID; FR-2 under `## Defaults the run chose` with the spec verdict's ID.

### TC-24 No pull request means a pause and the report (AC-24; integration) [agent]
- File: `tests/test_flow.py:test_auto_pr_fails` (new)
- Covers: CT-15
- Setup: a done auto effort on `nio/<S>`, no `origin` remote, the `gh` stub.
- Action: `nio flow pr S --by BY`.
- Assert: exit 1; `waiting.why` starts `pull request:`; output holds `# Run report:`; `git log nio/<S>` unchanged.

### TC-25 Three epics give a cap of 12 (AC-25; unit) [agent]
- File: `tests/test_flow.py:test_auto_cap` (new)
- Covers: CT-6
- Setup: granted full effort whose `tasks.md` has E-1, E-2, E-3; no `budgets`.
- Action: `flow.cap(root, S)`.
- Assert: `12`.

### TC-26 A configured cap wins (AC-26; unit) [agent]
- File: `tests/test_flow.py:test_auto_cap` (new)
- Covers: CT-6
- Setup: TC-25's effort and `.nio/config.json` `{"budgets": {"juries": 5}}`.
- Action: `flow.cap(root, S)`.
- Assert: `5`.

### TC-27 A money spec waits for the human's commit (AC-27; integration) [agent]
- File: `tests/test_flow.py:test_auto_risky_waits` (new)
- Covers: CT-8, CT-16
- Setup: `effort("spec_jury", risk="[money]")`, granted, spec gate approved without a commit.
- Action: `nio flow done spec_jury S --by BY`.
- Assert: `git rev-parse HEAD` unchanged; output holds `nio flow done spec_jury --commit S --by human`; `skills/auto/SKILL.md` step 4 holds `--commit`.

### TC-28 After the human commits, the run goes on (AC-28; integration) [agent]
- File: `tests/test_flow.py:test_auto_risky_waits` (new)
- Covers: CT-8, CT-7
- Setup: TC-27's state.
- Action: `nio flow done spec_jury S --commit --by human`; `nio flow next S`.
- Assert: a `pass` spec_jury line by the human; next names `@nio:plan`; `auto: true`.

### TC-29 An orchestrator can't grant auto (AC-29; unit) [agent]
- File: `tests/test_flow.py:test_auto_grant_on_start` (new)
- Covers: CT-1
- Setup: `effort("grilling")`.
- Action: `nio flow start S --auto --by "orchestrator / test / test"`.
- Assert: non-zero exit; `auto: false`; history line count unchanged.

### TC-30 Auto granted at plan_jury carries on there (AC-30; unit) [agent]
- File: `tests/test_flow.py:test_auto_grant_mid_effort` (new)
- Covers: CT-1
- Setup: `effort("plan_jury")`, manual.
- Action: `nio flow start S --auto --by human`; `nio flow next S`.
- Assert: `auto: true`; the `grant` line's `from` is `plan_jury`; next prints `skill: @nio:jury`.

### TC-31 Switching off mid-fix stops the next round (AC-31; integration) [agent]
- File: `tests/test_flow.py:test_auto_switch_off` (new)
- Covers: CT-3, CT-11
- Setup: auto effort at spec_jury, round 1 rejected, J-1 confirmed; the fixer has edited `spec.md` but not disposed.
- Action: `nio flow manual S --by human`; the fixer's `nio jury dispose S spec J-1 spec-fix --by auto ...`; `nio flow manual S --by "orchestrator / test / test"`.
- Assert: `auto: false`; a `switch_off` line by the human; the spec edit is kept; the `--by auto` dispose is refused (auto off); the orchestrator's switch-off is refused; ledger `round` still 1; the switch-off output holds `restore spec as round 1 judged it: git cat-file -p refs/nio/S/spec/1`, and that command prints `spec.md` as it was before the fixer's edit.

### TC-32 Before tasks the cap is 6 (AC-32; unit) [agent]
- File: `tests/test_flow.py:test_auto_cap` (new)
- Covers: CT-6
- Setup: `effort("plan_jury")`, granted, no `tasks.md`, no `budgets`.
- Action: `flow.cap(root, S)`.
- Assert: `6`.

### TC-33 No subagent cap unless configured: regression guard (AC-33; unit) [agent]
- File: `tests/test_flow.py:test_auto_subagent_cap` (new)
- Covers: CT-6
- Setup: granted effort at plan_jury (ready fail) whose ledgers' `collected` hold 200 keys; a copy with `budgets.subagents: 3` and 3 keys.
- Action: `flow.stops(...)` on each via `nio flow next S --by BY`.
- Assert: first: `pause` null; copy: `pause` `{"kind": "suspended", "why": "cap"}`.

### TC-34 A fix that didn't hold pauses (AC-34; integration) [agent]
- File: `tests/test_jury.py:test_auto_final_check_flag_pauses` (new)
- Covers: CT-12, CT-6
- Setup: `test_final_check`'s ledger with the final fix check flagging J-1 `not fixed`, on an auto effort.
- Action: `nio jury check S spec --record`; `nio flow next S --by BY`.
- Assert: outcome `human`; status `waiting_for_human` holding `J-1`; no `pass` spec_jury line.

### TC-35 The lite route runs to a pull request (AC-35; e2e) [agent]
- File: `tests/test_auto_e2e.py:test_driver_lite_route` (new)
- Covers: CT-16, CT-6, CT-15
- Setup: a lite effort from `tests/fixtures/spec/spec-bugfix.md` at grilling, granted; `gh` stub.
- Action: run the driver once.
- Assert: `pass` lines for grilling, tasking, tasks_jury, implementing; no `pass` from planning or plan_jury; `gh.log` holds one `pr create`.

### TC-36 Removing a risk flag pauses (AC-36; unit) [agent]
- File: `tests/test_jury.py:test_auto_round_check_risk` (new)
- Covers: CT-13
- Setup: auto effort, `risk: [money]`, first review judged; then `risk: []`.
- Action: `jury.cuts(root, S, "spec", led)`; check `--record`; `nio flow next S --by BY`.
- Assert: `["risk changed: [money] → []"]`; status `waiting_for_human` holding `risk`; round unchanged.

### TC-37 Removing AC-4 and adding a non-goal pauses (AC-37; unit) [agent]
- File: `tests/test_jury.py:test_auto_round_check_scope` (new)
- Covers: CT-13
- Setup: auto effort, first review judged; then AC-4 deleted and `- Exports. [agent]` added under Non-goals.
- Action: `jury.cuts(...)`; check `--record`.
- Assert: `cuts` returns `removed: AC-4` and `non-goal added: Exports. [agent]`; outcome `human` naming both; round unchanged.

### TC-38 A stale claim is taken over, a fresh one refused (AC-38; unit) [agent]
- File: `tests/test_flow.py:test_auto_driver_claim` (new)
- Covers: CT-5
- Setup: `driver.lock` naming `driver / a / m` with `at` 31 minutes ago; a second with `at` 5 minutes ago (C-261108-mplt's wording; the "process gone" case is dropped with it).
- Action: `nio flow drive S --by "driver / b / m"` on each.
- Assert: first: exit 0, the claim names `driver / b / m` with a new token; second: exit 1 naming `driver / a / m`, the file unchanged; the effort's `.gitignore` holds `driver.lock*`.

### TC-39 No refuter verdict pauses (AC-39; unit) [agent]
- File: `tests/test_jury.py:test_auto_no_refuter_verdict` (new)
- Covers: CT-12
- Setup: auto effort, first review with MAJOR as J-2 asked of the refuter, the refuter output collected with no block for J-2.
- Action: `nio jury check S spec --record`; `nio flow next S --by BY`.
- Assert: outcome `human`, reason `no refuter verdict: J-2`; status `waiting_for_human` holding `J-2`; no `pass` line.

### TC-40 A refuted blocker is listed first (AC-40; unit) [agent]
- File: `tests/test_flow.py:test_auto_report_order` (new)
- Covers: CT-14
- Setup: a spec ledger with a refuted major J-1 and a refuted blocker J-2.
- Action: `flow.report(root, S)`.
- Assert: J-2's line comes before every other `J-` in the report.

### TC-41 Resume after the cap gives 2 more (AC-41; unit) [agent]
- File: `tests/test_flow.py:test_auto_cap_raise` (new)
- Covers: CT-7, CT-6
- Setup: granted effort at plan_jury, spec ledger round 4 approved, plan ledger round 2 rejected, `suspended: cap`.
- Action: `nio flow start S --by human`; `flow.cap(root, S)`; `nio flow next S`; plan ledger set to round 4 rejected; `stops`.
- Assert: a `raise` line `{gate: "plan", rounds: 2, cap: 2}`; cap 8; next prints `skill: @nio:jury`; at plan round 4 no round pause (limit 5).

### TC-42 The grant names host and model (AC-42; unit) [agent]
- File: `tests/test_flow.py:test_auto_grant_ran_in` (new)
- Covers: CT-1
- Setup: `effort("grilling")`; env `CLAUDECODE=1`, no `ANTHROPIC_MODEL`.
- Action: `nio flow start S --auto --by human`.
- Assert: the `grant` line's `who` is `{"role": "human", "host": "claude-code", "model": "unknown"}`.

### TC-43 Two drivers at once: one wins (AC-43; integration) [agent]
- File: `tests/test_flow.py:test_auto_driver_race` (new)
- Covers: CT-5
- Setup: granted effort, no claim.
- Action: two `nio flow drive S` processes started together (`subprocess.Popen` ×2, `--by` a and b).
- Assert: exactly one exits 0; `driver.lock` names that one; the other exits 1 naming it; history line count unchanged.

### TC-44 A long wait keeps the claim (AC-44; integration) [agent]
- File: `tests/test_flow.py:test_auto_driver_refresh` (new)
- Covers: CT-5, CT-16
- Setup: claim by `driver / a / m` created 45 minutes ago and refreshed (same token) 8 minutes ago.
- Action: `nio flow drive S --by "driver / b / m"`.
- Assert: exit 1 naming `driver / a / m`; the claim unchanged; `skills/auto/SKILL.md` holds `every 10 minutes`. The claim's age is set by the setup, so it isn't asserted: that the driver refreshes every 10 minutes is the skill's instruction, checked here by its text only.

### TC-45 Resume after a failed PR only opens it (AC-45; integration) [agent]
- File: `tests/test_flow.py:test_auto_pr_retry` (new)
- Covers: CT-15, CT-7
- Setup: TC-24's paused effort; then `origin` added (a bare repo).
- Action: `nio flow start S --by human`; `nio flow next S`; `nio flow pr S --by BY`.
- Assert: next says `done`; `gh.log` holds one `pr create`; history after the `resume` has no `pass`, jury or task line.

### TC-49 A new driver goes on after the jury approved (AC-11; integration) [agent]
- File: `tests/test_flow.py:test_auto_resume_after_approval` (new)
- Covers: CT-20, CT-5
- Setup: granted effort (no risk flag) at spec_jury, the spec ledger approved by a recorded round, no approval commit; a stale claim.
- Action: `nio flow drive S --by "driver / b / m"`; `nio flow next S`; the `done:` command it prints.
- Assert: next says `state: spec_jury (working)` and prints `done: nio flow done spec_jury S`; no `waiting_for_human: approve`; after done, one `pass` from spec_jury and a `nio: approve spec` commit. The same effort with `risk: [money]` still says `waiting_for_human: approve spec`.

### TC-50 The jury skill hands `rejected` to the fixer under auto (AC-12; integration) [agent]
- File: `tests/test_flow.py:test_auto_skill_texts` (new)
- Covers: CT-21, CT-16
- Setup: `skills/jury/SKILL.md` and `skills/auto/SKILL.md` as shipped.
- Action: read the jury skill's `## Under auto` section.
- Assert: it holds `rejected`, `nio-fixer`, `never disposes \`--by agent\`` and `never grills`; the driver skill holds `## Under auto` and `--token`.

### TC-51 Two drivers with the same --by: the second is refused (AC-9; integration) [agent]
- File: `tests/test_flow.py:test_auto_driver_same_by` (new)
- Covers: CT-5
- Setup: granted effort; `nio flow drive S --by "driver / claude-code / m"` prints `token: <t1>`.
- Action: `nio flow drive S --by "driver / claude-code / m"` (no token); then `nio flow drive S --by "driver / claude-code / m" --token wrong`; then `--token <t1>`.
- Assert: the first two exit 1 naming the driver, `driver.lock` unchanged; the third exits 0 and the claim keeps token `<t1>` with a newer `at`; no `driver.lock.*` file is left.

### TC-52 After the human resumes, a round-check hit lets the next round start (AC-15; unit) [agent]
- File: `tests/test_jury.py:test_auto_round_check_resume` (new)
- Covers: CT-12, CT-13
- Setup: TC-15's paused effort (`[human] line changed: FR-1`).
- Action: `nio flow start S --by human`; `nio jury check S spec --record`; `nio jury next S spec`.
- Assert: the resume line names gate `spec` and round 1; the outcome is `rerun`; the step writes the fix-check packs for round 2.

### TC-53 Auto commits land on the effort branch (AC-1; unit) [agent]
- File: `tests/test_flow.py:test_auto_grant_switches_branch` (new)
- Covers: CT-1, CT-2, CT-20
- Setup: `effort("spec_jury")` on `main`, spec ledger approved by a recorded round; a copy with an uncommitted change to `README.md`.
- Action: `nio flow start S --auto --by human`; `nio flow done spec_jury S --by BY`; on the copy, `nio flow start S --auto --by human`.
- Assert: `git rev-parse main` unchanged; the current branch is `nio/S`; the `nio: approve spec` commit is on `nio/S` and not on `main`; the copy exits non-zero naming `commit or stash`, stays on `main` with `auto: false`.

### TC-54 A held finding needs the human in every mode (AC-13; integration) [agent]
- File: `tests/test_jury.py:test_held_without_auto` (new)
- Covers: CT-11, CT-12, CT-3
- Setup: TC-13's ledger with J-1 held.
- Action: `nio flow manual S --by human`; `nio jury check S spec --record`.
- Assert: outcome `human` naming `held for the human: J-1`.

### TC-55 The fixer card acts on each row of the fixer table (AC-13; integration) [agent]
- File: `tests/test_auto_e2e.py:test_fixer_card_rows` (new)
- Covers: CT-17, CT-11
- Setup: an auto spec ledger with one finding per row of the decision table "Fixer action on a finding": confirmed blocker and confirmed major with fixes in an `[agent]` line; confirmed blocker whose fix rewrites FR-1 (`[human]`); confirmed major whose fix drops US-2; refuted blocker; refuted major; blocker and major left `pending` after the refuter; a minor.
- Action: run `nio-fixer` on them with `claude -p` (as `tests/test_tasks_e2e.py:run_card` does).
- Assert: the two fixable findings are disposed `spec-fix` `by: auto` and their lines changed; the FR-1 and US-2 findings are disposed `held` `by: auto`, FR-1 and US-2 unchanged in `spec.md`; the refuted, pending and minor findings have no disposition and their lines are unchanged.

### TC-56 The driver's last message after the round pause (AC-5; integration) [agent]
- File: `tests/test_auto_e2e.py:test_driver_stops_with_reason` (new)
- Covers: CT-16, CT-6
- Setup: TC-5's effort.
- Action: run the driver once.
- Assert: its last message holds `3 rounds` and `nio flow start S --by human`; no `pass` line after the pause.

### TC-57 A lost judged version pauses (AC-15; unit) [agent]
- File: `tests/test_jury.py:test_auto_round_check_missing_version` (new)
- Covers: CT-13, CT-22
- Setup: auto effort, first review judged; `refs/nio/S/spec/1` deleted and the blob's loose object removed; `spec.md` edited.
- Action: `jury.cuts(...)`; `nio jury check S spec --record`.
- Assert: `["judged version missing: <blob>"]`; outcome `human`.

### TC-58 A fix the human re-disposes is still in the report (AC-23; integration) [agent]
- File: `tests/test_flow.py:test_auto_report_keeps_fixer_record` (new)
- Covers: CT-11, CT-14
- Setup: TC-23's effort; J-1 then re-disposed `accepted-risk --by human`.
- Action: `flow.report(root, S)`.
- Assert: J-1's `was` is `{"disposition": "spec-fix", "by": "auto", ...}`; the report lists J-1 under `## Fixed by the run` with `then accepted-risk by the human`.

## Quality tests

### TC-46 No passed gate runs twice after any interruption (NFR-2; integration) [agent]
- File: `tests/test_flow.py:test_auto_takeover_repeats_no_gate` (new)
- Covers: CT-5, CT-16
- Setup: TC-11's effort; for each stage from spec_jury to tasks_jury, the driver's command sequence cut after each command (claim taken, `next`, `done`).
- Action: a new driver (`drive` after the claim goes stale) resumes from `nio flow next` and runs the sequence to done.
- Assert: for every cut point, history has at most one `pass` from each gate stage and reaches `done`.

## Misuse tests

### TC-47 The run can't grant itself auto or rewrite the human's lines (UJ-1 misuse; integration) [agent]
- File: `tests/test_flow.py:test_auto_misuse` (new)
- Covers: CT-1, CT-13, CT-19
- Setup: `effort("grilling")`; every `SKILL.md` and card.
- Action: `nio flow start S --auto --by "driver / test / test"`; TC-15's `[human]` edit under auto.
- Assert: the grant is refused; the edit composes `human`; every skill and card holds the flow-state line with `Never pass \`--by human\``.

### TC-48 The run never carries on past a stop silently (UJ-2 misuse; integration) [agent]
- File: `tests/test_flow.py:test_auto_misuse` (new)
- Covers: CT-6, CT-16
- Setup: TC-13's paused effort.
- Action: `nio flow done spec_jury S --by BY`.
- Assert: exit 1; the output holds the reason and `nio flow start S --by human`; no line added.

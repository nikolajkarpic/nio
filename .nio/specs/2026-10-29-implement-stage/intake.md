# Intake: 2026-10-29-implement-stage

## The human's words (2026-10-29)

> start the intake and spec for 43

## Source: https://github.com/nikolajkarpic/nio/issues/43

### Flow stage: implement per epic, with hand-offs to epic jury and evaluation

#### What needs designing

**The implement stage of the flow (#19), per epic.** Approved tasks go to workers. After each epic: the **epic jury** plus the **implementation evaluation** (#29).

This issue covers only the hand-offs that matter to the spec flow. The workers themselves (TDD, builder, test writer, adversarial tester, swarm) are probably an effort of their own later.

#### What the design must define

- What a worker gets: one task, its `nio pack`, and the spec, AC and contract excerpts. Never the whole spec folder. Spec-kit's implement degrades as the context fills (spec-kit#75, its `complex-features.md`).
- How a worker reports a spec problem. NORTH_STAR says stop and file a change request (#30) and never fix silently.
- The order within an epic: tasks → epic jury on the diff → implementation evaluation (#29) → tests. Findings become new tasks (append-only) or change requests.
- **When an epic is done:** the evaluation passes, the jury approves, and the human is notified.


### Comment, 2026-10-27

#### Research (2026-10-28)

**Dependencies now settled elsewhere.** #42 decided the task format (seven fields, `tasks.md`, fix tasks under `#### Fixes`). #45 holds task states (`claimed → red → green → review → done`). #29 decided the epic gate (conformance + correctness, the CLI runs tests, jurors read-only). This issue now only has the four hand-off points left.

**1. What a worker gets.** Per task:
- `nio pack "<task title>" --task T-n --path <each Files: entry> --ac <each Serves: AC>` (memory),
- the task block cut from `tasks.md`,
- the CT-n blocks it binds (`contracts.md`) and the TC-n tests it must make pass (`tests.md`),
- nothing else.

Evidence for keeping it small: Chroma's "context rot" study (2025) measured accuracy falling as input grows, even on simple retrieval, across 18 models. spec-kit's own `complex-features.md` tells users to split implementation for the same reason.

**2. How a worker reports a spec problem.** The worker writes its handoff with `status: blocked` and a `change_request:` block (what the spec or plan says, what the code shows, the smallest change it would need). It never edits the spec. The orchestrator runs `nio new change` (the `change` record type already exists, `src/nio/templates/change.md`) and sets the task to `blocked` (#45). Spec-kit's maintainers drew the same line when they closed spec-kit#4940 (2026-10): "Accepting an implementation discovery is a legitimate human decision, but that decision must be reflected in the intended contract before convergence can establish agreement."

**3. Order within an epic.** Tasks in dependency order → (all `done`) → epic CLI checks (tests, attacks, phantom completion, tampering) → epic jury → findings become `#### Fixes` tasks (append-only) or change requests → loop. Running the CLI checks **before** the lenses means a red test suite never costs a lens run.

**4. When an epic is done.** Every task is `done`, the epic jury outcome is `approved`, and the human is notified (#7). Matches #42 Q5.

**Workers (deferred).** For the later effort:
- Claude Code subagents can run in **isolated git worktrees** (`isolation: worktree` frontmatter), which NIO can pass through the card's `hosts.claude` block (#24). Codex has no per-agent worktree.
- Cross-host workers: `codex exec --sandbox workspace-write -o <file>` writes its last message to a file, and `agy -p` has `--print-timeout`. Details in #4.

Refs: #42 · #45 · #29 · #4 · src/nio/templates/change.md · [spec-kit#4940](https://github.com/github/spec-kit/issues/4940) · [Chroma: context rot](https://research.trychroma.com/context-rot)


### Comment, 2026-10-28

#### Brainstorm: open questions (2026-10-28)

The research comment settled the four hand-offs: what a worker gets, how it reports a spec problem, the order within an epic, and when an epic is done. #45 settled that tasks run one at a time. These questions are what's left before a spec. They'll be asked one at a time, and the answers posted here.

1. **Scope.** Should this effort be the implement stage alone, with the implementation jury (#29) as the next effort, or both together?
2. **Who the worker is.** A shipped `nio-worker` agent card that the host's orchestrator runs as a subagent, the orchestrator working each task itself, or an external CLI such as `codex exec`.
3. **What "red" and "green" run.** A task's `Test:` line is prose today, not a command. Where does the command the CLI runs come from?
4. **Proving red.** Is a failing test enough, or must it fail for the right reason (an assertion, not an import error)?
5. **The per-task review step** (`green → review → done`). Who reviews one task: a cheap reviewer subagent, CLI checks only, or nobody until the epic jury?
6. **Commits.** One commit per task, one per epic, or none, leaving it to the human?
7. **Files outside the task's `Files:` list.** Refuse it, allow it with a note, or treat it as a change request?
8. **Tests edited after red.** Freeze the task's test files at red, so a later change needs a change request, or only flag it for the epic jury?
9. **Attempts.** How many tries a task gets before it goes to the human.
10. **Tests already failing before the stage starts** (brownfield). Record them as a baseline that a task may not make worse, refuse to start, or ignore them?
11. **Where task status lives.** Derived from history lines, as the stage is, or stored in `state.json`.
12. **The epic gate while #29 isn't built.** Skip it (all tasks done and the suite green, then notify), or wait for the human?


### Comment, 2026-10-28

#### Brainstorm: answers (2026-10-28)

The human chose the recommended option on all 12.

1. **Scope:** the implement stage alone. The implementation jury (#29) is the next effort.
2. **Worker:** a new shipped `nio-worker` agent card. Each task runs in a fresh subagent with only its pack, on the model the task's tier names.
3. **Red/green command:** the worker names it at red (`--run "<command>"`). The CLI runs it, and green must run the same command. `tasks.md` doesn't change.
4. **Proving red:** the command must exit non-zero, and its output must not show a collection, import or syntax error. There's a short list of known patterns per test runner; an unknown runner falls back to the exit code alone.
5. **Per-task review:** CLI checks only.
   - which files changed
   - the red test is unchanged
   - the full suite has no new failures

   There's no model run per task. Judgment comes from the epic jury.
6. **Commits:** nio makes one commit per task, `T-n: <title>`, on an effort branch, never main. The human merges the branch.
7. **Files outside the task's list:** allowed. Each one is recorded in history and shown to the epic jury.
8. **Tests edited after red:** the test file is frozen at red. If it changed, green is refused until the worker runs red again, so the new test must fail first.
9. **Attempts:** 3, then the task is blocked and the run pauses for the human. This matches the round cap and the stuck rule from #45.
10. **Failing tests before the stage starts:** a baseline of failing tests is recorded before the first task. A task may not add new failures; the old ones are listed in the epic report.
11. **Task status:** read from history lines. Each line carries the command, its output hash and the frozen test file's hash. `state.json` keeps only the current claim and the attempt count.
12. **The epic gate while #29 isn't built:** skipped like any stage that isn't built yet. The CLI checks that every task is done and there are no new failures, records the skip, notifies the human, and moves on.

Next: intake and spec through the pipeline.


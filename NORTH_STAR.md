# NIO — North Star

NIO (Ni(kolaj) Orchestrator / New & Improved Orchestrator) is a set of skills and
practices that make agent-built software **trustworthy** and **cheaper to build**.

## The problem

Agents build fast but you can't tell what they decided, why, or whether it's right.
**Vague requirements are where agents start hallucinating.** Specs are thin, plans drift,
and agents make silent calls on their own. Making everything safe by brute force (always
running the biggest model, always reviewing everything) burns tokens.

## Pipeline

```
onboard → spec → research → contracts → bindings → personas → plan
        → effort/epics/tasks → evaluate → implement (per epic) → test
```
Every stage is **grilled** and uses a **template**. A jury reviews at the end of spec,
plan and tasks, and after each implemented epic.

### Entry: full or lite
An evaluator reads what the user asked for and routes it:
- **`@nio:lite`** for small fixes and issues: a short path with a repro, a failing test,
  the fix, and a jury.
- **The full pipeline** below for features and complex bugs.

### Onboard
- **New project:** this is the main path.
- **Existing project:** the human describes the project, what they want to do, and the
  configs and personas. NIO writes this down before any other stage runs.

### Grilling (every stage)
- One question at a time (or numbered rounds of independent questions, if configured).
  NIO offers 3 options (fewer only when no real alternative exists) with one recommended,
  and the human can always type their own instead.
- **Contradictions** are flagged and must be resolved before moving on.
- **Stop condition:** each template has a checklist of required fields. Grilling stops
  when every field is filled and nothing is vague or contradictory.
- **Vague requirements** are hunted down, because they are the main source of
  hallucination.
- The spec must cover **user stories**, **edge cases** and acceptance in the form
  *given / when / then*.

### Spec
The agent writes it from the human's answers, using a template similar to spec-kit's.

### Plan
The plan is a set of documents, each grilled and each following a template:
- `research.md`: docs looked up, MCPs available, and a map of the code (which classes
  and files matter).
- `requirements.md`
- `acceptance-criteria.md`
- `tests.md`: behavioural tests derived from the user personas.
- `personas.md`: **user personas**, meaning how a person will actually use the feature.
  Bug fixes skip this.
- `contracts.md`: interfaces and API contracts between components, plus **bindings**:
  how each contract maps to code.
- `plan.md`: the structure of what has to be built, written from all of the above.

**Agent personas** are a separate thing: the roles NIO's workers play (see Implement).

### Work breakdown
- **Effort:** the whole thing that needs to happen, and why.
- **Epic:** a large chunk of an effort, still too big to build in one go.
- **Task:** granular work, for example "implement this class from this interface",
  "extend this method", "add this event in this file".

### Evaluate and estimate
- A custom evaluator agent rates each task's difficulty.
- The tasks jury reviews those ratings too.
- The difficulties then become a **usage estimate** and an execution plan: model and
  worker per task, and which tasks run in parallel versus in sequence.
- The human sees the estimate before anything is spent.

### Implement
NIO has its own workers:
- TDD
- test writer
- builder
- adversarial evaluator
- adversarial tester
- swarm: one orchestrator and several workers, sized by effort and model

Work runs in parallel or in sequence. After each epic, a jury reviews the diff against
the tasks, and then tests run.

## Jury (Byzantine review)

- **Triage:** the spec's risk flags set the verdict's risk tier. A triage model that can add
  lenses comes later, if hit rates show lenses missing.
- **Escalation ladder:** each lens runs once, on its own card's model. A lens whose blocker
  the refuter confirmed is re-run with 3 independent jurors, and 2 of 3 decide.
- **Independence:** jurors don't see each other's reasoning and each gets a different
  lens. No single juror is trusted on its own.
- **Minimal context:** a juror gets a context pack (the diff, the task and its acceptance
  criteria), never the whole conversation. Model and effort are chosen by what is being
  judged.
- **When the jury runs:**
  - Stage gates: end of spec, end of plan, end of tasks, end of each epic.
  - Any of these, whenever they happen:
    - work outside the task's scope
    - a new dependency
    - an architecture change
    - deleting files or data
    - changing a test so it passes
    - anything the agent is unsure about
    - implementation diffs in general
- **Verdict:**
  - If the jury approves, the agent proceeds without asking, but the **human is always
    notified**.
  - If the jury rejects, the change is not applied.
  - If the jury can't agree, the decision goes to the human.
- **Jury results are evaluated too.** The smallest model checks each verdict for quality
  (verdicts should be good by default, so this is a cheap sanity check, not a re-review)
  and shows it to the human in a readable form.
- **Always goes to the human, never decided by the jury:**
  - DB scripts
  - secrets
  - breaking changes
  - anything irreversible
  - anything that can cost money
- **Never fix silently.** When implementation shows the spec or plan is wrong, work stops
  and a change request goes to the human.

## Traceability and memory

This is a core pillar. Its design is in `MEMORY_NORTH_STAR.md`, which wins where the two differ.
- **Every decision is recorded:** what was decided, by which agent, when, why, and which
  requirement or acceptance criterion it serves. Later you can go back and see why
  something was done that way.
- **IDs link the chain:** requirement → acceptance criterion → task → diff → verdict.
- **Memory agents can reach cheaply:** specs are part of memory, but agents also need fast
  lookup of past decisions. Calibration (estimated versus actual) and replay of past jury
  decisions live here too.
- **Team-shareable eventually:** memory must not be locked to one person's machine.
- **Questions memory must answer:**
  - Was this done before, and can I reuse the solution?
  - Why was X done this way?
  - Did the jury approve it, and what did it reject?
- **Working idea, two layers:**
  1. Decision records as files in git are the source of truth. Git makes them shareable
     with a team, they work on every host, and they can be traced through history.
  2. A search index on top that can be swapped out and rebuilt from the files at any time.
- **Decisions stay separate from code context.** Decision memory is about the *why*, and
  code context is about the *what/where*. They are indexed separately (leaning, not
  final).

## Code context

What goes into an agent's context is a major cost in tokens. NIO should give agents a way
to navigate code without reading whole files: a code graph, RAG, or a knowledge graph.
Candidates are codegraph, graphify and Obsidian. This needs research.

## Cross-host runs

**Any host can play any role:** orchestrator, juror or worker. Claude Code, Antigravity and
the others are peers. A host asks other hosts for second opinions or work:
- Claude Code starts a run and calls another agent's CLI in **headless mode**, for example
  `agy -p` (Antigravity, model Gemini 4 Argon), `codex exec` or `claude -p`.
- The other agent gets a **context pack file** and the relevant NIO skill. It writes a
  **handoff md** (a verdict or a result) that the orchestrator reads back.
- Every external agent is an **adapter**: a command template plus an input file and an
  output file. Adding a host means adding one adapter, not changing NIO.
- Cross-host jurors provide the real model diversity that Byzantine review needs, for
  example a 3-juror panel of 2 Claude jurors and 1 Antigravity juror.
- **Agents are defined by role** (juror lens, worker type) with a host, a model and an
  effort level. An external worker gets its own **git worktree** when it edits files.

## Setup and config

- **Install:** both `nio install` (shell, for a fresh machine) and `@nio:install` (skill)
  ask which subscriptions you have (Claude, Antigravity, Cursor, Codex…), check that each
  CLI is installed and logged in, and write the config.
- **Config is JSON, in three layers.** Later layers override earlier ones:
  1. **Global** `~/.nio/config.json`: your subscriptions, hosts and personal defaults.
  2. **Team** `.nio/config.json`: committed and shared repo-wide. Holds roles, jury panel,
     budgets, extensions and the human-only rules.
  3. **Local** `.nio/config.local.json`: gitignored, for your personal overrides in this
     repo.
- **What the config holds:**
  - which hosts and models fill which roles
  - the jury panel makeup
  - when to use expensive models (for example, Argon only for high-risk decisions and
    Flash otherwise)
  - budgets
  - extensions and their hooks

## Budgets

Runs are capped by **counts**: juries per run, subagents spawned, and model tier per role.
The test targets are a $100 Claude plan and a $20 Antigravity plan. A usage estimate
is a nice-to-have, since it's mainly useful with API pricing.

## Extensions

- Extensions are customizable: what they do, when they run, and which hook triggers them.
- Some come built in, such as linting and formatting hooks.
- Users can add their own skills, commands, rules, workers and juror lenses.

## Principles

- **Agent-agnostic.** Skills are plain `SKILL.md` markdown in the open Agent Skills
  format. Claude Code is the first host (packaged as a plugin). Antigravity, Cursor,
  Codex and Grok must be able to use the same skills unchanged.
- **Invoked as `@nio:<skill>`.** The skill set can be extended: users add their own
  skills, commands and rules next to NIO's.
- **Files and git are the state.** No database and no daemon. Everything a run decides is
  readable and diffable.
- **Human in the loop by default.** Autonomy is earned through the jury, never assumed.
- **Minimal.** A skill exists only if it's used.
- **Talking to the human.** Every message an agent sends the human is actionable at a glance,
  without opening a file. Every skill carries this block word for word:

### Talking to the human
Every message to the human (question, report, error or hand-off):
1. **First line: what you need from them**, in plain words: "Nothing needed", "Pick one",
   "Run this command", "Approve or push back". A round of questions gets one such line.
2. **Then about 3 lines:** what it is, why it matters, what it costs. Name things by what
   they do, never by an ID or a NIO term they don't start by name; only stage names (spec,
   grill, jury, plan) stay as they are. A fact names its source beside it in plain words.
3. **Options** say what happens if picked, including what's lost. The recommended one goes first.
4. **Long lists** (calls, dispositions, findings): show every item that changes what a user
   can do or sees, who may do it, what data is kept or changed, or what it costs, however
   many; count the rest in one line.
5. **Commands they must run** go in the body, quoted exactly, ready to copy.
6. **End with `Refs:`** when the message rests on anything: the IDs, files and commands it
   rests on, never raw command output. In a question tool, `Refs:` is the question text's
   last line, and each option's description says what happens.
Before sending, ask: could they act on this without opening a file? If not, rewrite it.

## Non-goals (for now)

- Multi-user or team features (NIO has a single user for now). The exception: the memory
  design must leave room for team sharing.
- Dry-run mode (low priority).
- Hosted service or UI.
- Hosts beyond Claude Code and Antigravity until both work well.

## Success looks like

- I can read why every autonomous decision was allowed.
- A NIO run fits within the $100 Claude and $20 Antigravity plans.
- Specs and tasks rarely need rework after implementation starts.

See the GitHub issues for open decisions and deferred ideas.

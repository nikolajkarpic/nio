# Intake

## The human's words (this conversation, 2026-11-08)

> do we have nio scan and nio install hooks flow? where we scan repo and set up nio?

> yes, start on #49 and and lest do brianstorming on it, we should look for claude md, agents md and skills and docs in the repo first, also acrhitetude md, notrhstar md or similar files, product md etc, we need to take in teh context and figure out what the repo does, next up we need to split those into product level docs and implementation level docs, what could we use what docs do you recomemnd we have

Answer on existing docs:
> we take tehse in and grill the user to set it up properlyt dothese make sense are they up t odate we go through all of it with the dev

Answer on where docs live: ".nio/project/ + offer fixes (Recommended)"

Answer on the doc set:
> 1 but we also need what we use for deploys, lets say a project is deploy do cloud run which kills the instance after no usage vs ec2 which runs allways, all of this needs to be also documented in additon so that we can understand, what do we use for eventing lets say is gcp/aws/azure stack etc

Answer on the infra doc: "Own doc: infra.md (Recommended)"
Answer on keeping docs current: "Effort delta + stale flag (Recommended)"
Answer on packaging: "New onboard skill, install hands off (Recommended)"
Answer on greenfield: "Product now, tech later (Recommended)"
Answer on the scanner: "`nio onboard scan` lists, agent reads (Recommended)"
Answer on who reads the docs: "pack maps stage → docs (Recommended)"

> we need reconsile-onboarding to update tehse docs on demand?

Answer on reconcile: "Separate reconcile-onboarding skill"

> run the flow for it start with spec

## Source: https://github.com/nikolajkarpic/nio/issues/49 (body and comments, which record the decisions above)

### What needs designing

**The project's Technical Context, written once at onboarding instead of in every feature's plan.** Decided in #41 (comment of 2026-10-25).

Spec-kit's `plan.md` fills in Language/Version, Primary Dependencies, Storage, Testing, Target Platform, Project Type, Performance Goals, Constraints and Scale for every feature. Most of that describes the project, not the feature, and asking for it each time conflicts with NIO's fact gate (look facts up, don't ask).

Decided:
- Onboarding writes one project-level file, and research fills it from the code (manifests, lockfiles, CI config, test runner).
- Anything it can't find is marked `NEEDS CLARIFICATION` and becomes a fact or a decision for the grill.
- A feature's `architecture.md` records only what it changes or adds (a new dependency, a new storage engine). A new dependency always goes to the human (#25, NORTH_STAR).

### What the design must define

- Where the file lives (`.nio/project.md`? project memory?) and its fields.
- How it is kept current: what refreshes it when a feature's change lands (the delta in `architecture.md` → the project file).
- How it relates to principles (#26): it holds facts about the code, while principles hold rules about how to build. Keep them in separate files.
- Greenfield projects: no code to read, so the architecture grill (#25) writes the first version.
- Who reads it: the architecture grill, the plan stage and the plan jury's architecture lens, via `nio pack`.

### Notes

Prior art: spec-kit `templates/plan-template.md` "Technical Context" @ `67e0f72`. Users report that spec-kit's `/plan` ignores the existing codebase (spec-kit#75).

## Research (2026-10-28)

**Current state.** Nothing is built. `nio:plan` reads tech facts from the code into the feature's `research.md` as RF-n (#41 decision of 2026-10-27), so this isn't blocking.

**How others store project-level tech context**
- **spec-kit:** each feature's `plan.md` has a "Technical Context" block (Language/Version, Primary Dependencies, Storage, Testing, Target Platform, Project Type, Performance Goals, Constraints, Scale/Scope). Then `update-agent-context` scripts copy "Active Technologies" into the agent file (CLAUDE.md / AGENTS.md). So spec-kit itself ends up with a project-level copy, just a derived one.
- **Kiro:** steering files `.kiro/steering/{product,tech,structure}.md`, generated once from the codebase ("Generate steering docs") and kept by hand afterwards. `tech.md` is exactly this issue's file: stack, libraries, common commands.
- **AGENTS.md convention** (Codex, Cursor, Gemini, Copilot): build/test commands and conventions in one root file that every agent reads.
- **OpenSpec:** `openspec/project.md` (project context, tech stack, conventions), filled by the agent on first use.

So the convergent pattern is **one small project file, generated from the code once, then edited as features change it.** Kiro's split (tech vs structure vs product) matches NIO's separation from principles (#26).

**Recommendations for the open points**
1. **Location and fields:** `.nio/project.md` (next to `config.json`, outside `specs/` because it isn't per feature). Use markdown with the same provenance tags as the spec. Fields: Language/version, Package manager and lockfile, Key dependencies (only ones a plan might touch), Storage, Test runner and command, Lint/type command, Build/run command, Target platform, Layout (top-level modules, one line each), Limits. Each line is tagged `[research: <file>]` or `NEEDS CLARIFICATION`.
2. **Keeping it current:** the cheapest reliable trigger is the **plan gate**. When `nio:plan` writes an RF-n that contradicts `project.md`, or `architecture.md` adds a dependency or storage, the plan's approval step proposes the one-line diff to `project.md`, and the human approves it with the plan. Plus a free CLI check: the test command in `project.md` still exists, and every listed dependency is still in the manifest. No background refresh.
3. **vs principles (#26):** separate files. `project.md` is what *is* (verifiable from code); principles are what *must be* (rules). Kiro and spec-kit both keep them apart.
4. **Greenfield:** `nio:architecture` (#25) writes the first version. Until then, every field is `NEEDS CLARIFICATION`, and those become grill questions.
5. **Readers:** via #48's card-file-list mechanism (an agent card lists `project.md` among its files), not a central table.

**Evidence the problem is real.** spec-kit#75 (closed, 26 comments), where `/plan` ignored the existing structure. The fix in the wild (Kiro steering, AGENTS.md) is "read the code once, persist it".

Refs: #41 · #25 · #26 · #48 · [Kiro steering](https://kiro.dev/docs/steering/) · [spec-kit#75](https://github.com/github/spec-kit/issues/75)

**Brainstorm 2026-11-08, decision 1: what onboarding does with the docs a repo already has**

Onboarding scans for agent instructions (CLAUDE.md, AGENTS.md, GEMINI.md, .cursor/rules, copilot-instructions, skills), product docs (README, NORTH_STAR/PRODUCT/VISION, docs/), implementation docs (ARCHITECTURE, CONTRIBUTING, ADRs) and code facts (manifests, lockfiles, CI, test and lint config).

Decided: it doesn't trust them as they are. It reads them all in, then grills the dev through each one: does it make sense, is it current, what's missing. Only confirmed content goes into NIO's project docs.

Proposed doc set (still open): product level is product.md and personas.md; implementation level is stack.md (this issue), architecture.md and principles.md (#26).
**Decision 2: where confirmed docs live.** They go in `.nio/project/`. When the grill finds that one of the repo's own docs is stale, NIO offers a patch to it and the dev says yes or no.

**Decision 3: which docs.** product.md (what it does, users, flows, non-goals, glossary), personas.md, stack.md (languages, deps, commands, CI), architecture.md (modules, boundaries, data flow) and principles.md (#26). On top of those, the infra and runtime picture must be documented too: where it deploys and how it runs (Cloud Run scales to zero, EC2 is always on), which cloud (GCP, AWS or Azure), and what it uses for eventing, queues, storage and secrets. Whether that's its own doc or part of stack.md is still open.
**Decisions 4–8 (brainstorm 2026-11-08)**

4. **Infra gets its own doc, `infra.md`**: cloud provider; each deployable (where it runs, scaling to zero or always on, cold starts); eventing and queues; managed storage; secrets; environments; how a deploy happens. Read by plan and the architecture lens for runtime limits. That makes the set: product.md, personas.md, stack.md, architecture.md, infra.md, principles.md (#26).
5. **Keeping current: effort delta plus a stale flag.** When an effort finishes, its changes are proposed as edits to the project docs and the dev approves them. Each fact also records its source file and that file's hash, so `nio status` flags a doc when its source changed outside NIO.
6. **Packaging: a new `@nio:onboard` skill.** `@nio:install` stays quick and ends with "run onboard next". Onboard grills one doc per round, saves progress so the dev can stop and resume, and spec refuses to start until onboarding is done or skipped on purpose.
7. **Greenfield: product now, tech later.** In an empty repo, onboard grills product.md, personas.md and principles.md if there are any. stack, architecture and infra start as NEEDS CLARIFICATION, and the first spec's architecture grill fills them in.
8. **Scanner: `nio onboard scan`.** The CLI lists every candidate file by category (agent docs, product docs, implementation docs, manifests, IaC, CI) with hashes. The agent reads them and runs the grill. The CLI doesn't parse facts.
9. **Who reads the docs: `nio pack` maps each stage to its docs.** spec and the scope lens get product + personas. plan and the architecture lens get stack + architecture + infra + principles. Workers get stack + principles.
**Decision 10: a separate `@nio:reconcile-onboarding` skill updates the docs on demand.** `@nio:onboard` runs only the first time. Reconcile is for when `nio status` flags a doc as stale, or after a change made outside NIO. It uses `nio onboard scan` to diff source hashes, grills only the changed or new sources and the docs they feed, and offers edits for the dev to approve. To keep the two skills from drifting apart, onboard and reconcile should share the per-doc grill steps (how is still open).

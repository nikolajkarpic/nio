---
slug: 2026-11-08-project-onboarding
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: project onboarding

## Contracts

### CT-1 The scan (FR-1, FR-2, FR-3, FR-24) [agent]
- Binding: `src/nio/onboard.py:scan` (new)
- Like: `src/nio/query.py:status`
- Kind: function
- Shape: `scan(root) -> list[tuple[str, str, str]]`, `(category, path, hash)` sorted by category then path; `hash` is the first 12 hex characters of the file's sha256, and `""` for a secrets entry. `CATEGORIES` maps each category (`agent-docs`, `product-docs`, `implementation-docs`, `manifests`, `iac`, `ci`) to `fnmatch` patterns matched against the path and its base name, at least: agent-docs `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursor/rules/*.mdc`, `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.windsurfrules`, `.clinerules`, `.kiro/steering/*` (RF-5); product-docs `README*`, `docs/*.md`; implementation-docs `ARCHITECTURE*`, `CONTRIBUTING*`, `docs/adr/*`; manifests `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `requirements*.txt`, `Gemfile`, `pom.xml`, `build.gradle*`; iac `*.tf`, `Pulumi.yaml`, `cdk.json`, `serverless.yml`, `cloudbuild.yaml`, `Dockerfile`, `docker-compose*.yml`, `Chart.yaml`, `fly.toml`, `vercel.json`, `app.yaml`; ci `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/config.yml` (RF-6). `SECRETS` is the list FR-24 quotes, matched against the base name.
- Accepts: a git work tree. Candidates are `git ls-files --cached --others --exclude-standard` (tracked and untracked, not ignored) plus, for the secrets check only, `git ls-files --others --ignored --exclude-standard`. A path under `.nio/`, a symlink, or anything that is not a regular file is left out.
- Returns: one entry per candidate whose name matches a category; a name matching `SECRETS` gets only `("secrets", path, "")`, whatever else it matches.
- Rules: "limit the scan's output to paths, categories and hashes, leaving reading and fact-finding to the agent" (FR-2). "leave out of the scan files git ignores, files under `.nio/`, and anything that is not a regular file inside the repo (a symlink is never listed or followed), except that files FR-24 lists appear git-ignored or not" (FR-3). "under a secrets category by path only and under no other category" (FR-24).

### CT-2 `nio onboard scan` (FR-1, FR-2) [agent]
- Binding: `src/nio/cli.py:main` (existing)
- Kind: cli
- Shape: `nio onboard scan` prints one line per entry, `<category> <path> <hash>` (a secrets line is `secrets <path>`), then `<n> candidate files`; with none it prints `no candidate files found` and exits 0.
- Fails: not inside a git work tree → exit 1, `nio onboard scan needs a git repository`.

### CT-3 Onboarding progress (FR-9, FR-10, FR-12, FR-15, FR-27) [agent]
- Binding: `src/nio/onboard.py:progress` (new)
- Like: `src/nio/flow.py:load`
- Kind: function
- Shape: `progress(root) -> dict` reads `.nio/project/onboarding.json` (see the data model); a missing file is `{"state": "not started", "reason": "", "empty": False, "apps": {}, "confirmed": [], "seen": []}`; a file that isn't valid JSON raises `ValueError(".nio/project/onboarding.json is not valid JSON: fix or restore it")`, never read as `not started`. `save(root, p)` writes a temp file next to it and `os.replace`s it, as `flow.record` does. `DOCS = ["product", "personas", "stack", "architecture", "infra", "principles"]`, the grill order (FR-9). `expected(p) -> list[str]`: the docs to confirm, `product`, `personas`, `principles` when `empty` (FR-12), else all six; with apps, each as `<app>/<doc>` for every app in order. `next_doc(p) -> str | None`: the first expected doc not in `confirmed`.
- Rules: "grill one project doc per round, in the order product, personas, stack, architecture, infra, principles (skipping docs the run does not grill)" (FR-9).
- State: follows the spec's state table Onboarding.

### CT-4 `nio onboard start|confirm|pause|skip` (FR-9, FR-10, FR-12, FR-15, FR-27, FR-32) [agent]
- Binding: `src/nio/onboard.py` (new)
- Like: `src/nio/flow.py:start`
- Kind: cli
- Shape: functions `start`, `confirm`, `pause` and `skip` in `onboard.py`, registered as `nio onboard` subcommands in `cli.py`. `nio onboard start [--empty] [--app <slug>=<path>[,<path>...]]...` → `in progress`, saves `empty` and `apps`, prints `next: <doc>` (the `next_doc`); a later start from `paused` or `skipped` keeps the saved `confirmed`, `empty` and `apps` and ignores new flags. `nio onboard confirm <doc> [--app <slug>]` adds the doc to `confirmed` and prints `next: <doc>`, or `done` and moves to `done` when none is left. `nio onboard pause` → `paused`. `nio onboard skip "<reason>"` → `skipped` with the reason. With `--empty`, `start` also writes `stack.md`, `architecture.md` and `infra.md` from their templates (every body `NEEDS CLARIFICATION`) when they don't exist (FR-12). When `confirm` moves the state to `done` it saves `seen`: the scan's paths outside the secrets category at that moment (CT-11 compares with it). `nio onboard reconciled` saves `seen` again from the current scan, run at the end of a reconcile.
- Accepts: `<doc>` one of `DOCS` and expected; `--app` required when apps exist, and must be one of them; an app slug matches `[a-z0-9]+(-[a-z0-9]+)*` and isn't a doc name; a reason is non-blank.
- Fails: only the table's `reject` cells exit 1: start on `done` → `onboarding is done; it runs once: use @nio:reconcile-onboarding`; skip on `done` → `onboarding is done already`. Input errors also exit 1 with nothing written: skip with a blank reason → `a skip needs a reason`; confirm in `in progress` when the doc file `.nio/project/[<app>/]<doc>.md` is missing or fails CT-12's check → naming what is missing; a doc that isn't expected, a missing or unknown `--app`, a bad app slug → naming the rule; an unreadable progress file (CT-3).
- Rules: "a later run of `@nio:onboard` starts onboarding normally" (FR-15); "IF `@nio:onboard` runs after onboarding finished THEN THE SYSTEM SHALL change nothing and point the dev to reconcile" (FR-10).
- State: follows the spec's state table Onboarding; `ignore` cells (confirm outside `in progress`, pause outside `in progress`, skip on `skipped`, start on `in progress`) exit 0, print `ignored: onboarding is <state>` and change nothing.

### CT-5 A full or epic spec waits for onboarding (FR-14) [agent]
- Binding: `src/nio/spec.py:new` (existing)
- Kind: function
- Shape: before creating the folder, for route `full` or `epic`, when `onboard.progress(root)["state"]` is not `done` or `skipped`, raise `ValueError("onboarding is <state>: run @nio:onboard first, or skip it on purpose with nio onboard skip \"<reason>\"")`. A `lite` spec is never refused.
- Rules: follows the spec's decision table May a spec start.

### CT-6 A spec names its apps (FR-28) [agent]
- Binding: `src/nio/spec.py:check` (existing)
- Kind: function
- Shape: the front matter of all three spec templates (`spec.md`, `spec-epic.md`, `spec-bugfix.md`) gains `apps: []                       # the apps this spec touches, when the project has docs per app`. When `onboard.progress(root)["apps"]` is not empty and the spec's front matter has an `apps` key (a spec written before this feature has none and is left as it is; its packs get every app), on every route, `check` adds `spec names no app; the project has apps: <a>, <b>` when `apps` is empty, and `app <x> has no project docs (.nio/project/<x>/)` for each named app without that folder.
- Rules: "refuse at `nio check spec` a spec that names no app or an app with no docs" (FR-28).

### CT-7 Source records and staleness (FR-7, FR-19, FR-20, FR-25) [agent]
- Binding: `src/nio/onboard.py:stale` (new)
- Like: `src/nio/query.py:status`
- Kind: function
- Shape: `SOURCE = re.compile(r"\(source: ([^@()\s]+)@([0-9a-f]{12})\)")`. `stale(root) -> list[tuple[str, str, str]]`, `(doc, source path, "changed" | "deleted")` for every project doc under `.nio/project/` (relative path, e.g. `stack.md` or `api/stack.md`) and every source record in it whose file is gone or whose current hash differs; each file is hashed once per call. A `(source: dev, …)` record has no hash and is never stale.
- Rules: "by hashing only the files the project docs record as sources and comparing with the recorded hashes: no model, no search of the code, the same result every time" (FR-25, C-261108-mk6n).
- State: follows the spec's state table Project doc freshness.

### CT-8 `nio status` shows onboarding and stale docs (FR-15, FR-19, FR-20, NFR-2) [agent]
- Binding: `src/nio/onboard.py:status_lines` (new)
- Like: `src/nio/query.py:status`
- Kind: cli
- Shape: `status_lines(root) -> list[str]`: `onboarding: <state>` (with `: <reason>` when skipped), then `stale: <doc> (<path> <changed|deleted>)` per CT-7 entry. `nio status` prints them after the index lines; without an index it still prints them.
- Rules: "flag that doc as stale in `nio status`, naming the file" (FR-19, FR-20); "show both in `nio status`" (FR-15).

### CT-9 The project docs a reader gets (FR-17, FR-18, FR-25, FR-28, FR-33) [agent]
- Binding: `src/nio/onboard.py:docs_for` (new)
- Like: `src/nio/pack.py:build`
- Kind: function
- Shape: `READERS = {"spec": ["product", "personas"], "scope": ["product", "personas"], "plan": ["stack", "architecture", "infra", "principles"], "architecture-fit": ["stack", "architecture", "infra", "principles"], "worker": ["stack", "principles"]}`. `docs_for(root, reader, slug="") -> str`, a markdown part `## Project docs` holding, per mapped doc that exists, `### <doc path>` and the doc's text with its headings nested two levels down; then one line per case: `stale: <doc> (<path> <changed|deleted>)`, `over 16 KB: <doc> (<n> KB)` for a doc over 16384 bytes, `missing: <doc>` for a mapped doc that doesn't exist once onboarding is `done`, and `onboarding: <state>` (`: <reason>` when skipped) while it isn't `done`. With apps: the apps are those the slug's spec names in `apps`; with no slug, a spec naming none, or a spec with no `apps` key, every reader gets every app; each doc path carries its app (`api/stack.md`). Returns `""` when onboarding is `not started` and no doc exists.
- Rules: "include each project doc the decision table Docs per reader maps to that reader that exists, and, while onboarding is not done, one line saying its state (with a skip's reason)" (FR-17); "IF onboarding is done and a project doc mapped to a reader is missing THEN THE SYSTEM SHALL build the pack anyway and name the missing doc in it" (FR-18); "SHALL NOT block the stage" (FR-25); "include it whole and add a line naming the doc and its size as over the limit" (FR-33).
- State: follows the spec's decision table Docs per reader.

### CT-10 Packs carry the project docs (FR-17, FR-28) [agent]
- Binding: `src/nio/pack.py:build` (existing)
- Kind: function
- Shape: `build(root, text, paths=(), acs=(), task="", diff=None, worker=True, reader="", slug="")`; with a reader it appends `onboard.docs_for(root, reader, slug)` before the closing instructions. `nio pack` in `cli.py` gains `--reader {spec,scope,plan,architecture-fit,worker}` and `--slug` and passes them on.
- Rules: every existing caller without `reader` gets the same output as before.

### CT-11 Changed sources at the end of an effort (FR-23) [agent]
- Binding: `src/nio/onboard.py:changed` (new)
- Like: `src/nio/query.py:status`
- Kind: function
- Shape: `changed(root, ref) -> list[tuple[str, list[str]]]`, `(path, docs it feeds)` for each file `git diff --name-only <ref>` lists that some project doc records as a source, sorted. `nio onboard changed <ref>` prints `<path>: <doc>, <doc>` per entry, or `no project doc source changed`. `to_reconcile(root) -> list[str]`: the stale sources (CT-7) as `<path> changed|deleted`, then each scan path outside the secrets category that is in neither `seen` nor any source record, as `<path> new`; `nio onboard changed` with no ref prints those, or `nothing to reconcile`. `close_lines(root, ref) -> list[str]`: one `project docs: <path> changed, feeds <docs>: propose edits with @nio:reconcile-onboarding` per `changed` entry. CT-20 prints it when an effort closes.
- Rules: "list each file the effort's diff changed that a project doc records as a source, propose edits to the docs it feeds, apply only those the dev approves, and record each listed file's new hash" (FR-23); the proposing, applying and recording are the reconcile skill's (CT-14).

### CT-12 The project doc templates (FR-5, FR-6, FR-7) [agent]
- Binding: `src/nio/onboard.py:HEADINGS` (new)
- Like: `src/nio/templates/spec.md`
- Kind: file
- Shape: six templates `src/nio/templates/project/<doc>.md` (product, personas, stack, architecture, infra, principles). Each is the doc's skeleton: a `# <Doc>` title and one `## <heading>` per heading Key entities names for it (personas: one `### P-1 <name>` entry with `Who`, `Wants`, `Allowed to`, `How often` lines), each body `NEEDS CLARIFICATION`, then an HTML comment listing the questions the grill asks for that doc and the source-record forms of CT-7. `HEADINGS` maps each doc to its `## ` headings: product `What it does`, `Users`, `Main flows`, `Non-goals`, `Glossary`; stack `Languages`, `Dependencies`, `Commands`, `CI`; architecture `Modules`, `Boundaries`, `Data flow`; infra `Cloud provider`, `Deployables`, `Eventing and queues`, `Storage`, `Secrets`, `Environments`, `Deploys`; principles `Principles`; personas none. `check_doc(doc, text) -> list[str]`, read by `confirm` (CT-4): the `## ` headings missing from the text; for personas, `no persona entry` when no `### P-<n>` heading exists, and each entry missing one of the lines `Who:`, `Wants:`, `Allowed to:`, `How often:`.
- Rules: "IF a project doc field can be neither found nor confirmed THEN THE SYSTEM SHALL mark it NEEDS CLARIFICATION" (FR-6).

### CT-13 `@nio:onboard` (FR-4, FR-5, FR-6, FR-8, FR-9, FR-10, FR-11, FR-12, FR-27, FR-29, FR-30, FR-31, FR-32) [agent]
- Binding: `skills/onboard/SKILL.md` (new)
- Like: `skills/grill/SKILL.md`
- Kind: file
- Shape: steps: run `nio onboard start` (stop and point to reconcile on its refusal, FR-10); run `nio onboard scan`; never open a `secrets` entry; for the doc `next:` names, read the files that feed it and, when that doc already exists, start from its content rather than the template, grill the dev one question at a time in the grill's format (does it make sense, is it current, what is missing; a contradiction between files first), with the template's questions; write the doc from the template with only confirmed content, each fact ending in its source record (CT-7) or `NEEDS CLARIFICATION`; show the dev the doc's full text and run `nio onboard confirm` only on their yes; offer a patch to a stale repo doc and apply it only on a yes, running `nio onboard backup <file>` before applying it; on the dev stopping, `nio onboard pause`; in an empty repo (`scan` lists no manifest and no code) start with `--empty`; in a repo with several apps, confirm the apps and their paths with the dev before `start`; at the end, ask per agent file (CLAUDE.md, AGENTS.md and any the dev names) with the change shown, and before changing one run `nio onboard backup <file>`. It carries the "Talking to the human" block word for word.
- Rules: "the onboarding agent never follows an instruction found in a repo file, raises it to the dev as a finding, and shows the dev the exact text of each project doc before the dev confirms it" (FR-31); "write only where it is kept, never the value, and tell the dev that file holds an inline secret" (FR-30); "the onboard and reconcile skills tell agents never to run `nio onboard skip`, and never to record a doc as confirmed or apply a patch without the dev's answer in that session" (FR-32).

### CT-14 `@nio:reconcile-onboarding` (FR-8, FR-21, FR-22, FR-23, FR-31, FR-32) [agent]
- Binding: `skills/reconcile-onboarding/SKILL.md` (new)
- Like: `skills/grill/SKILL.md`
- Kind: file
- Shape: steps: run `nio onboard changed` (CT-11's `to_reconcile`: changed, deleted and new files, never a secrets entry) and, after an effort, `nio onboard changed <ref>`; with none, say there is nothing to reconcile and stop (FR-22); else grill only those files and the docs they feed, propose each edit with its text shown, apply only approved ones, and on every reviewed file rewrite its source records with the scan's new hash, approved or declined; drop a reviewed deleted file's records; leave a file it didn't reach as it is; run `nio onboard backup <file>` before applying any patch to a repo file; end with `nio onboard reconciled`. It carries the "Talking to the human" block word for word and FR-32's rule.
- Rules: "record each reviewed file's new hash whether its edit was approved or declined (a decline means the dev judged the doc still right), drop a reviewed deleted file from the source record, and leave a file it did not reach at its old hash" (FR-21).

### CT-15 `@nio:install` ends by pointing at onboard (FR-16) [agent]
- Binding: `skills/install/SKILL.md` (existing)
- Kind: file
- Shape: "When to stop" says to end with a message that the next step is onboarding (`/nio:onboard` on Claude Code, the onboard skill elsewhere), and that install never starts it.
- Rules: "end with a message to run onboard next, without starting onboarding" (FR-16).

### CT-16 The spec skill and its drafter use the project docs (FR-26, FR-28) [agent]
- Binding: `skills/spec/SKILL.md` (existing)
- Kind: file
- Shape: the spec skill builds its drafting pack with `nio pack "<summary>" --reader spec` (and `--slug` once the spec exists), and in a project with apps writes the apps the work touches into `apps:`. The drafter card `src/nio/agents/spec-drafter.md` has each human actor end with the personas entry it is (`P-n`) or `no persona`.
- Rules: "have each human actor name the persona entry it is, or say that it matches none" (FR-26); "have each spec name in its front matter the one or more apps it touches" (FR-28).

### CT-21 The first full spec's grill fills blank tech fields (FR-13) [agent]
- Binding: `skills/grill/SKILL.md` (existing)
- Kind: file
- Shape: on a full spec while stack.md, architecture.md or infra.md hold `NEEDS CLARIFICATION`, the grill asks those fields as questions and writes each answer into its doc as a fact ending in `(source: dev, <slug> grill Q<n>)`.
- Rules: "have the next full spec's grill ask those fields (the architecture grill once it exists) and write the answers into those docs" (FR-13).
### CT-17 `nio onboard backup` (FR-29) [agent]
- Binding: `src/nio/onboard.py:backup` (new)
- Like: none: nothing in NIO copies a user's file yet
- Kind: cli
- Shape: `nio onboard backup <file>` copies the file, bytes unchanged, to `.nio/backup/<YYYY-MM-DD>/<file>` (today's date, the file's repo path) and prints that path. A second backup of the same file on the same day keeps the first copy and prints its path.
- Fails: the file doesn't exist, or lies outside the repo → exit 1 naming it; nothing written.
- Rules: "keep a copy of the original at `.nio/backup/<date>/<path>`, which NIO never deletes and the scan never lists; restoring is copying it back" (FR-29).

### CT-18 The jury's scope and architecture-fit packs carry the project docs (FR-17) [agent]
- Binding: `src/nio/jury.py:_pack_text` (existing)
- Kind: function
- Shape: appends `onboard.docs_for(root, "scope", slug)` to the scope lens's pack at the spec gate and `onboard.docs_for(root, "architecture-fit", slug)` to the architecture-fit lens's pack at the plan gate; other packs are unchanged. CT-22 lets their quotes ground.
- Rules: follows the spec's decision table Docs per reader.

### CT-19 The worker pack carries the project docs (FR-17, FR-28) [agent]
- Binding: `src/nio/implement.py:worker_pack` (existing)
- Kind: function
- Shape: calls `pack.build(..., reader="worker", slug=slug)`, so the docs sit inside its first part and the pack keeps exactly five `## ` parts.
- Rules: "put into every pack of that effort the mapped docs of each named app" (FR-28).

### CT-20 The effort's close names changed sources (FR-23) [agent]
- Binding: `src/nio/flow.py:epic_done` (existing)
- Kind: function
- Shape: when the last epic closes, after `merge:`, the lines of `onboard.close_lines(root, <merge base of main and nio/<slug>>)`, and nothing when there are none.
- Rules: "propose edits to the docs it feeds, apply only those the dev approves" (FR-23).

### CT-22 The project docs a lens reads can ground its quotes (FR-17) [agent]
- Binding: `src/nio/jury.py:sources` (existing)
- Kind: function
- Shape: `onboard.doc_paths(root, reader, slug) -> list[Path]`, the files `docs_for` carries; `sources` adds them, for the scope lens at the spec gate and the architecture-fit lens at the plan gate, so they are listed under "Files to read" and a quote from them grounds. Other lenses' sources are unchanged.
- Rules: follows the spec's decision table Docs per reader.

## Data model
- **Onboarding progress** (spec Key entity) in `src/nio/onboard.py:progress` (new) [agent]
  - stored as `.nio/project/onboarding.json`: `{"state": str, "reason": str, "empty": bool, "apps": {slug: [path]}, "confirmed": [str], "seen": [str]}`; `seen` holds the scan's non-secrets paths at the last done or reconcile. "one state for the whole project: not started, in progress, paused, done or skipped, with a skip's reason" (Key entities)
- **Source record** (spec Key entity) in `src/nio/onboard.py:SOURCE` (new) [agent]
  - text at the end of a fact line: `(source: <path>@<12 hex>)` or `(source: dev, <where answered>)`. "the file it came from and the hash of the bytes the agent read when the dev confirmed it" (FR-7)
- **App** (spec Key entity) in `src/nio/onboard.py:progress` (new) [agent]
  - a key of `apps`: "a lowercase slug (letters, digits, hyphens) with the repo paths it covers" (FR-27)
- **Candidate file** (spec Key entity) in `src/nio/onboard.py:scan` (new) [agent]
  - `(category, path, hash)`; hash `""` for secrets. "list every candidate file in the repo under its category" (FR-1)

# Architecture: project onboarding

Settles only what the plan skill's stop list sends here. Each item follows from the approved spec, the decisions and
change requests it cites, or the existing code, and this file records where. It adds no design of its own. Read-only to
the plan; changing it takes a change request.

## New modules and folders (stop list 2)
- `src/nio/onboard.py`: the scan (FR-1 to FR-3, FR-24), onboarding progress (state table Onboarding, FR-9, FR-12,
  FR-14, FR-15, FR-27), source records and staleness (FR-7, FR-19, FR-20, FR-25), and which project docs a reader gets
  (FR-17, FR-18, FR-28, FR-33). One module per stage family, as `spec.py`, `plan.py`, `tasks.py` and `implement.py`
  already are. It reaches git only through `records.git`, as the other modules do.
- `skills/onboard/SKILL.md` and `skills/reconcile-onboarding/SKILL.md`: the two skills the spec's Summary names. One
  folder per skill is the repo's layout (CLAUDE.md, "Repo layout").
- `src/nio/templates/project/`: one template per project doc (product, personas, stack, architecture, infra,
  principles), holding the headings Key entities names and the questions the grill asks for each. Both skills read
  the same templates, so onboard and reconcile ask the same questions per doc (the call the spec moved here, J-19).
  Templates already live in `src/nio/templates/`, read with `importlib.resources`.

## New stored data (stop list 3)
- `.nio/project/<doc>.md`, or `.nio/project/<app>/<doc>.md` when the dev confirmed more than one app (FR-5, FR-27).
  Plain markdown under the headings of Key entities. Each fact line ends with its source record (FR-7):
  `(source: <path>@<hash>)`, where `<hash>` is the first 12 hex characters of the file's sha256 as the scan prints it,
  or `(source: dev, <where answered>)` for a fact from the dev's answer, which carries no hash.
- `.nio/project/onboarding.json`: onboarding progress (Key entity Onboarding progress): `state` (`in progress`,
  `paused`, `done`, `skipped`; the file's absence is `not started`), `reason` (a skip's reason), `empty` (an empty repo,
  FR-12), `apps` (`{slug: [paths]}`, empty for one app), `confirmed` (the docs confirmed, as `<doc>` or
  `<app>/<doc>`) and `seen` (the scan's paths outside the secrets category at the last done or reconcile, so
  reconcile can tell a new file, C-261108-unxo). Written only by `nio onboard`, read by `onboard.py`.
- `.nio/backup/<YYYY-MM-DD>/<path>`: the copy of an agent file kept before it is changed (FR-29). Under `.nio/`, so
  the scan never lists it (FR-3).
- Spec front matter gains `apps: []`, the apps a spec touches (FR-28). The spec template carries it; `spec.check`
  reads it.

## Interfaces used outside this feature (stop list 4)
- New `nio onboard` subcommands, registered in `cli.py` like the other command groups:
  - `nio onboard scan` (FR-1);
  - `nio onboard start [--empty] [--app <slug>=<path>[,<path>...]]...` (state table Onboarding: dev starts onboard);
  - `nio onboard confirm <doc> [--app <slug>]` (dev confirms a doc; the last one makes it done);
  - `nio onboard pause` (dev stops);
  - `nio onboard skip "<reason>"` (FR-15);
  - `nio onboard backup <file>` (FR-29: copies an agent file to `.nio/backup/` and prints the copy's path);
  - `nio onboard changed [<ref>]` (FR-23: the files changed since `<ref>` that a project doc records as a source;
    with no ref, what reconcile has to review: changed, deleted and new files);
  - `nio onboard reconciled` (records the scan's paths as seen at the end of a reconcile).
- `nio new spec` refuses a full or epic spec while onboarding is neither done nor skipped (FR-14). `spec.new` is the
  one place a spec is created.
- `nio check spec` fails a spec in a project with several apps that names no app, or an app with no docs (FR-28).
- `nio pack` gains `--reader <spec|scope|plan|architecture-fit|worker>` and `--slug <slug>`; with a reader it appends
  the project docs that reader gets (FR-17). `pack.build` gains the same two keyword arguments, defaulting to none, so
  every existing caller is unchanged.
- The worker pack `nio flow claim` writes calls `pack.build` with its reader and slug; the jury's scope pack (spec
  gate) and architecture-fit pack (plan gate) append `onboard.docs_for` directly, and `jury.sources` lists those
  docs so a lens's quotes from them ground (FR-17; the plan jury's J-1 and J-4, C-261108-unxo). The worker pack keeps its
  five parts: the docs sit inside its memory part.
- `nio status` adds the onboarding state (with a skip's reason) and one `stale:` line per stale doc (FR-15, FR-19,
  FR-20).
- The closing of an effort's last epic (`flow.epic_done`) adds one line per changed source file, naming the docs it
  feeds and `@nio:reconcile-onboarding` (FR-23).
- `@nio:install`, `@nio:spec`, `@nio:grill` and the spec drafter card gain the steps FR-13, FR-16, FR-26 and FR-28
  name.

## No new dependency (stop list 1)
Hashes use `hashlib`, the scan uses `git ls-files` through `records.git` and `fnmatch` for names, the progress file
uses `json`. All are the standard library or already used here.

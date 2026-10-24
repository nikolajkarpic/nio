---
id: D-261024-zbne
type: decision
title: "Packs ask for memory-used and are saved per run and logged"
status: human
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/pack.py", "src/nio/cli.py"]
tags: ["pack", "usage-log", "jury"]
supersedes: []            # IDs of records this replaces
---
## Decision
The pack's instructions ask the worker to end its reply with `memory-used: <IDs>`. A pack always prints to stdout; with `--run` it is also saved to `.nio/runs/<run>/packs/<task ID or description slug>.md`. Every pack appends its IDs to `.nio/cache/usage.log`. Juror packs (`--diff <ref>`) ship with step 5: the diff's files join the scope and the instructions become the juror's check against approved and current records. Juror standings count drift only up to the diff's base, so the change under review never makes the record it is judged against read as drifted.
## Why
Comparing `memory-used` with the pack shows which records were useful and which were noise, the data any future limit needs. Asking in the pack works on every host today, with no worker skill. Saving only under a run keeps quick manual packs from scattering files, while a run's packs show exactly what an agent saw. Logging and juror mode are each a few lines on top of the same build, so they came in now rather than at steps 6 and 8.
## Rejected alternatives
- A worker skill asking for `memory-used`: none exists yet, so v0 would collect nothing.
- Saving every pack: files with no run to group them.
- Deferring juror packs and the log to steps 6 and 8: the human chose to add both now.
## Reuse
The usage log line is `time<TAB>kind<TAB>name<TAB>approx tokens<TAB>IDs`; `nio query` and `nio get` should log the same way in step 8.

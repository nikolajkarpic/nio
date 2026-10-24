---
id: D-261024-f7rs
type: decision
title: "nio query refreshes the index before answering"
status: proposed          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-24
by: "builder / claude-code / opus"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/query.py"]
tags: ["query", "freshness", "sync"]
supersedes: []            # IDs of records this replaces
---
## Decision
`nio query` runs the incremental `nio index` build before every search and graph walk. If that build fails, it warns and falls back to matching words and paths over the record files.
## Why
The writer's dedup must see a record written minutes ago, and a stale index would hide exactly the records most likely to be duplicated. With nothing changed, the build takes about 0.3 s; after a change it embeds only the changed records, and query needs the model loaded anyway. A failed build must not stop lookup, so the fallback keeps working with no index and no model.
## Rejected alternatives
- Trusting the index the git hook last built (step 7): it misses uncommitted records and anything written since the last pull.
- Failing when the index is stale: lookup would break in exactly the cases it is needed.
## Reuse
If the build gets slow on large repos, refresh only when `nio status` reports changes, and leave the full rebuild to the hook.

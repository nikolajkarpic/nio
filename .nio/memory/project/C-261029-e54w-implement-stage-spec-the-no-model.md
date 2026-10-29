---
id: C-261029-e54w
type: change
title: "Implement-stage spec: the no-model rule allows nio's local embedder; it forbids API model clients and outgoing connections"
answers: why              # why | reuse | jury
date: 2026-10-29
by: "human"                # role / host / model, or human
run: "R-261029-ksbo"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-29-implement-stage/spec.md"               # the spec, plan or record that is wrong
outcome: accepted          # pending | accepted | rejected
paths: [".nio/specs/2026-10-29-implement-stage/spec.md", ".nio/specs/2026-10-29-implement-stage/tests.md", "src/nio/query.py"]
tags: [implement-stage, nfr, memory]
supersedes: []
---
## What is wrong
NFR-1 says nio's own steps make no model calls, checked by asserting that no model or HTTP client module is loaded (TC-51). Building it showed that `nio flow claim` builds the worker's memory pack, whose search embeds the query with fastembed, a local model that imports `requests` and `httpx`. In a project with memory records the check can't hold. The build made TC-51 pass by giving its fixture no memory, and made `query.search` skip the embedding when the index has no vectors.
## Proposed change
1. NFR-1's check becomes: those steps run on fixture tests with network access blocked, no outgoing connection is attempted, and no API model client (`anthropic`, `openai`) is loaded. nio's local embedder may load.
2. TC-51 keeps memory records in its fixture and asserts exactly that.
To apply once the build is done, with one spec-jury recheck of NFR-1 and a plan-jury recheck of TC-51.
## Human decision
Accepted during the build, 2026-10-29: "Allow local embedder".

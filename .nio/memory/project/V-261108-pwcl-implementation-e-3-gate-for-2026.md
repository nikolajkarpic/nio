---
id: V-261108-pwcl
type: verdict
title: "implementation-E-3 gate for 2026-11-08-explainer: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-08
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-3:2026-11-08-explainer"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-08-explainer/jury/implementation-E-3.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-3 jury ruled **rejected** for `2026-11-08-explainer` in round 1 (4 disposed, 10 open). Ledger: `.nio/specs/2026-11-08-explainer/jury/implementation-E-3.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| conformance | claude-code | sonnet | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | sonnet | approve |
## Reasons
- unresolved: J-1, J-2, J-4, J-9
- J-1 [major/risk] A drill-down heading containing ", " locks finishing forever: disposed fix-task
- J-2 [major/risk] A quickstart with unusual front matter fails after explainer.md is already written and images deleted: disposed fix-task
- J-4 [major/risk] Step 6 strips every `> ` line and image line, not only the ones an earlier finish wrote: disposed fix-task
- J-9 [blocker/gap] AC-33 has no passing evidence: disposed fix-task
- J-3 [minor/gap] A stopped or broken render leaves old SVGs on disk that nothing tracks any more: open
- J-5 [minor/risk] The path argument is never checked: open
- J-6 [minor/gap] Every finish run adds blank lines to explainer.md: open
- J-7 [minor/gap] A missing path gives a traceback, not `error:`: open
- J-8 [minor/contradiction] Notes in a kept drill-down are removed: open
- J-10 [minor/inconsistency] Image names do not follow the CT-6 naming rule: open
- J-11 [minor/inconsistency] A section's first fenced block is not its first Mermaid block: open
- J-12 [minor/inconsistency] Old SVGs are deleted after rendering, not before: open
- J-13 [minor/risk] Every `> ` line is removed, not only the notes an earlier finish wrote: open
- J-14 [minor/gap] `nio explain finish` with no path, or a missing file, gives a traceback, not `error:`: open
## What was rejected
Nothing.

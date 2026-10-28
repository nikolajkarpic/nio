---
slug: 2026-10-28-flow-state
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: flow state

## Prerequisites
- `uv` installed: `uv run nio --help` prints the commands, `flow` among them.
- A scratch clone, so the demo effort and its history never land in the real repo: `git clone -q /home/work/nio ../nio-qs && cd ../nio-qs`. Every command below runs in it, in order, QS-1 first: each scenario carries on the demo effort the one before left.
- Writing commands carry `--by human`, the human running the demo (`--by` is required). Each command names the demo effort as `$(basename .nio/specs/*-qs-demo)`, the dated folder `nio new spec qs-demo` makes.

## Scenarios

### QS-1 Carry on after a compaction (UJ-1; auto) [default]
1. `uv run nio new spec qs-demo && uv run nio flow start $(basename .nio/specs/*-qs-demo) --by human`
   Expected:
   ```
   contains: started
   contains: at intake
   ```
2. `uv run nio flow next` (a fresh shell, no slug: the effort with the newest history line)
   Expected:
   ```
   contains: -qs-demo
   contains: state: intake
   contains: skill: @nio:spec
   contains: done: nio flow done intake
   ```
3. `echo "Demo the flow." > .nio/specs/*-qs-demo/intake.md && uv run nio flow done intake --by human`
   Expected:
   ```
   contains: intake → drafting
   ```
4. `uv run nio flow done drafting --by human`
   Expected:
   ```
   contains: ERROR
   ```
5. `uv run nio flow next`
   Expected:
   ```
   contains: state: drafting
   ```
- Pass when: every step matched; step 4 exits 1 and step 5 still names drafting, because the spec template isn't filled in.

### QS-2 See what every effort is doing (UJ-2; auto) [default]
1. `uv run nio flow status`
   Expected:
   ```
   contains: -qs-demo · drafting · manual · working ·
   contains: grilling · legacy
   ```
2. `uv run nio flow park $(basename .nio/specs/*-qs-demo) "trying the quickstart" --by human && uv run nio flow status`
   Expected:
   ```
   contains: parked: trying the quickstart
   ```
3. `uv run nio flow next $(basename .nio/specs/*-qs-demo) --by human >/dev/null && uv run nio flow status`
   Expected:
   ```
   contains: -qs-demo · drafting · manual · working ·
   ```
- Pass when: every step matched, and the demo effort's line is the first one in steps 1 and 3.

### QS-3 Push a stuck check through (UJ-3; auto) [default]
1. `uv run nio flow done drafting $(basename .nio/specs/*-qs-demo) --human "quickstart override" --by human`
   Expected:
   ```
   contains: drafting → researching
   contains: skipped researching (not built)
   contains: skipped advocate_walking (not built)
   ```
2. `uv run nio flow status`
   Expected:
   ```
   contains: override not seen: drafting: quickstart override
   ```
3. `uv run nio flow seen $(basename .nio/specs/*-qs-demo) --by human && uv run nio flow status | grep -c "override not seen"`
   Expected:
   ```
   contains: seen 1 overrides
   contains: 0
   ```
4. `tail -n 4 .nio/specs/*-qs-demo/history.jsonl`
   Expected:
   ```
   contains: "kind": "override"
   contains: "reason": "quickstart override"
   contains: "kind": "seen"
   ```
- Pass when: every step matched.

### QS-4 A change sends the effort back (UJ-4; auto) [default]
1. `C=$(uv run nio new change --area project --title "Demo change" | tail -n 1) && sed -i "s|^against: \"\"|against: \".nio/specs/$(basename .nio/specs/*-qs-demo)/intake.md\"|" $C && uv run nio flow next --by human`
   Expected:
   ```
   contains: waiting_for_human
   contains: Settle the change request
   contains: drafting
   ```
2. `grep -c '"kind": "back"' .nio/specs/*-qs-demo/history.jsonl && uv run nio flow next --by human >/dev/null && grep -c '"kind": "back"' .nio/specs/*-qs-demo/history.jsonl`
   Expected:
   ```
   1
   1
   ```
3. `sed -i "s|^outcome: pending|outcome: rejected|" .nio/memory/project/C-*-demo-change.md && uv run nio flow next --by human`
   Expected:
   ```
   contains: state: grilling
   ```
- Pass when: every step matched: the pending change sends the effort to drafting once, and once it is no longer pending the effort is back in grilling.

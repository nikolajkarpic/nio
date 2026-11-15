---
id: C-261115-s4kj
type: change
title: "Spec problem in T-41 and T-42: J-54 and J-55; their tests TC-32 and TC-30 pass on arrival"
answers: why              # why | reuse | jury
date: 2026-11-15
by: "driver / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-15-effort-drilldown-install/tasks.md"
outcome: accepted         # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The tasks say: T-41 / J-54 (the background mod's README tells target projects not to turn the mod on), test TC-32; T-42 / J-55 (the shipped marketplace.json still calls the mods "Claude Code mods for developing NIO"), test TC-30. Each pack's test must fail first.

The code shows: both pass on arrival (`tests/test_hooks.py`: `test_readmes_call_mods_optional` and `test_wheel_ships_mods` print ok), so red cannot fail on them. TC-32 never checks the "Don't turn it on in a target project" sentence, and TC-30 only checks that marketplace.json ships, not its description. The real gaps stand: tools/claude-mods/background-nio-commands/README.md:31 still says "Don't turn it on in a target project", and tools/claude-mods/.claude-plugin/marketplace.json:3 still reads "Claude Code mods for developing NIO", both contradicting D-261115-e6nx.
## Proposed change
Apply the pass-on-arrival standing rule (#49): retire T-41 and T-42 and add one direct-mode fix task under E-8 (Files: tools/claude-mods/background-nio-commands/README.md, tools/claude-mods/.claude-plugin/marketplace.json, tests/test_hooks.py) whose new test asserts the README no longer tells target projects to keep the mod off and the marketplace description no longer says the mods are for developing NIO, plus the two text fixes.
## Human decision
Accepted under the human's standing pass-on-arrival rule (#49; precedents C-261115-duou, C-261115-lncp, C-261115-hkrz, C-261115-b3lo) on 2026-11-15: retire T-41 (TC-32 passes on arrival) and T-42 (TC-30 passes on arrival) and add one direct-mode fix task (the background mod README, marketplace.json, tests/test_hooks.py) with a test that neither text still treats the mods as off-limits or dev-only.

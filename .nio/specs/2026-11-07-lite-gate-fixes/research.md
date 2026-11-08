# Research: 2026-11-07-lite-gate-fixes

## Grill session 1 (2026-11-07)

- **RF-1** Evidence takes its tests only from tests.md's `- File:` lines, which a lite spec doesn't have. Source: src/nio/evidence.py:99: "the `file:name` of tests.md's misuse tests, then of its other tests."
- **RF-2** A bug fix's tasks name their tests in words, not as `file:name`. Source: src/nio/templates/tasks.md:15: "full spec: the plan's TC-n; bug-fix spec: what the test checks, in words"
- **RF-3** No effort in this repo has an epic heading without a story suffix, so a full spec relies on no unsuffixed epic. Source: `grep -l "^## E-[0-9]* [^(]*$" .nio/specs/*/tasks.md` (no match before this effort's dogfood #91 workaround)

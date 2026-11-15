---
name: e2e
description: Write one Playwright browser test per acceptance criterion at `Level: e2e`, before any code exists. Use at the e2e step, after the plan gate is approved, when `nio flow next` names `e2e.tests`.
---

# @nio:e2e (e2e extension)

Writes the browser tests for a spec's e2e acceptance criteria, so the implementation has them to make pass. Writes no
app code.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`. Never pass `--by human`: only the human grants or revokes auto, or approves a gate.

## Inputs and outputs

- **Input:** the spec's acceptance criteria whose own `Level:` is `e2e`, and `tests.md`'s tests aimed at them.
- **Outputs:** one Playwright test per such criterion at its test's `File:`, `e2e.md` next to the spec listing them,
  and a `playwright.config` that names the app's `webServer`.

## Talking to the human
Every message to the human (question, report, error or hand-off):
1. **First line: what you need from them**, in plain words: "Nothing needed", "Pick one",
   "Run this command", "Approve or push back". A round of questions gets one such line.
2. **Then about 3 lines:** what it is, why it matters, what it costs. Name things by what
   they do, never by an ID or a NIO term they don't start by name; only stage names (spec,
   grill, jury, plan) stay as they are. A fact names its source beside it in plain words.
3. **Options** say what happens if picked, including what's lost. The recommended one goes first.
4. **Long lists** (calls, dispositions, findings): show every item that changes what a user
   can do or sees, who may do it, what data is kept or changed, or what it costs, however
   many; count the rest in one line.
5. **Commands they must run** go in the body, quoted exactly, ready to copy.
6. **End with `Refs:`** when the message rests on anything: the IDs, files and commands it
   rests on, never raw command output. In a question tool, `Refs:` is the question text's
   last line, and each option's description says what happens.
Before sending, ask: could they act on this without opening a file? If not, rewrite it.

## Steps

1. **Collect.** Read `spec.md` and `tests.md` of the effort. List each acceptance criterion at `Level: e2e` and the
   test aimed at it, with its `File: <file>:<name>`.
2. **Write.** Start the `e2e-tester` agent card once with that list. For each criterion it writes one Playwright test at
   the test's `File:`, titled `<AC-ID> <the File's test name>`, asserting the criterion's Observable with web-first
   assertions only (`expect(page)` or `expect(locator)`).
3. **Configure.** The card makes sure `playwright.config` has `webServer` (`command` and `url`), `use.trace:
   'retain-on-failure'` and `use.screenshot: 'only-on-failure'`. It adds only keys that are missing and never changes a
   value already set. An `outputDir` already set is kept, else it is `test-results`, and that folder is in `.gitignore`.
4. **List.** The card writes `e2e.md` next to the spec: one line per test, its criterion and file.
5. **Finish.** Run the `done:` command `nio flow next` printed. Stop when it passes, or hand its output back to the
   human in the shape above.

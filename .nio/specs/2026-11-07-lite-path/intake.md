# Intake

## The human's words (via the delegating orchestrator session)

Goal: one NIO effort that implements GitHub issue #44, the lite path of the flow (intake → mini bugfix spec → fact-gated grill → repro → failing test → fix → jury), for small fixes. Read #44, #19, #11 (routing criteria, still open: settle the minimum needed for lite with the recommended default and record it), #39-#45 as needed. Also read #77 (speed-up roadmap) and .nio/research/2026-11-06-speedup.md: lite is meant to save 15–30 min per small effort. Keep it minimal: reuse the existing stages, flow state machine and jury; lite should mostly be a route that skips stages plus a mini spec template and an escalation to the full flow.

Lazy and minimal: smallest diff that works. Skills stay plain markdown any agent can follow.

At the end, dogfood: pick one small open bug from the backlog and run it through the new lite path end to end, timing it, and report the wall-clock against a full-flow effort.

## Source: https://github.com/nikolajkarpic/nio/issues/44

# Flow: the lite path (mini bugfix spec, fact-gated grill, repro, fix, jury)

### What needs designing

**The lite path of the flow (#19)**, for small fixes and issues. #11 decides *when* work is lite; this issue is *what* lite runs.

Decided in #19:

```
intake → mini bugfix spec → grill only on real ambiguity → repro → failing test → fix → jury
```

- **Mini bugfix spec:** current behaviour, expected behaviour, unchanged behaviour (Kiro's bugfix spec). The same "no assumptions" rule applies.
- The grill is fact-gated, so it often asks zero questions.
- Skipped: research fan-out, Actors and journeys, user advocate walk, architecture grill, plan and tasks stages.

### What the design must define

- The mini spec template (a variant of #20).
- **Escalation:** if lite finds the change is bigger than expected (several modules, a new dependency, a contract change), it stops and offers to switch to the full flow, keeping what it has.
- Which jury tier lite uses by default.



## Research (2026-10-28)

**What exists.** `nio new spec --route lite` already creates a bugfix spec from `src/nio/templates/spec-bugfix.md`, and `spec.ROUTES` restricts the ID prefixes a lite spec may use. So the mini spec template is partly settled in code. Nothing else of the lite path is built (no repro, red, fix or jury wiring for lite).

**Prior art: Kiro bugfix specs** ([docs](https://kiro.dev/docs/specs/bugfix-specs/), shipped in Kiro IDE 0.10, Feb 2026).
- `bugfix.md` replaces requirements with three blocks: **current behaviour** (`WHEN … THEN the system <wrong thing>`), **expected behaviour** (`WHEN … THEN the system SHALL …`) and **unchanged behaviour** (`WHEN … THEN the system SHALL CONTINUE TO …`).
- The tasks it generates include **property-based tests for reproduction, for the fix, and for preserved behaviour**. That's three tests, not one.

**What NIO should take from it**
1. The template is right as decided. Add Kiro's `SHALL CONTINUE TO` phrasing to the unchanged block, so `nio check spec` can require at least one unchanged-behaviour item with an Observable (a regression test).
2. **Three tests, not one:** repro (fails before, passes after), fix (the expected behaviour), and preservation (passes before **and** after). The preservation test is what catches the fix that breaks something nearby, and it's free to verify: it must pass on the commit before the fix too.

**Escalation (open point).** Stop and offer the full flow when any of these hold. They are the same objective triggers `nio:plan` uses to stop for architecture (#41), so lite and plan share one list:
- the fix touches more than one module / top-level package (count from the diff);
- it needs a new dependency;
- it changes an interface used outside the bug's module, or stored data;
- the expected behaviour needs a human decision with two or more real options.
"Keeping what it has": the bugfix spec's current, expected and unchanged items map one-to-one onto a full spec's FR/AC with the `[human]` tags kept, so nothing is re-asked.

**Jury tier (open point).** Default to **the `low` ladder rung with one core lens: `correctness`** (#29's implementation lens) on the diff, plus triggered lenses from risk flags as usual. A bugfix has no spec gate worth a lens run. Testability is enforced by the three tests above, and the CLI runs them. Cost: one cheap-to-strong lens run per fix.

Refs: src/nio/templates/spec-bugfix.md · src/nio/spec.py (ROUTES) · #11 · #29 · #41 · [Kiro bugfix specs](https://kiro.dev/docs/specs/bugfix-specs/)


## Source: https://github.com/nikolajkarpic/nio/issues/11

# Lite vs full routing criteria

Decide the criteria the evaluator uses.

Under the specs effort (#32). #19 defines the full path, so the lite criteria here decide which of its stages are skipped.
Pipeline decision in #19: **lite keeps a mini spec and a fact-gated grill.** It writes a short bugfix spec (current / expected / unchanged behaviour), grills only on real ambiguity (often zero questions), then runs repro → failing test → fix → jury. It skips the research fan-out, the persona grill and the architecture grill. This issue still has to set the routing criteria.
## Research (2026-10-28)

**What exists.** The route is a flag the human or `nio:spec` picks: `nio new spec --route full|lite|epic` (`src/nio/cli.py`). There's no evaluator; the spec skill picks a route at intake (#40 decision 1). This issue sets the criteria.

**Prior art**
- **Kiro** asks the user up front: "feature spec" or "bugfix spec". There's no automatic router.
- **spec-kit** has one path. Users report it's heavy for small changes, the "illusion of work" critique (spec-kit#75).

**Proposed criteria: deterministic first, the human overrides**

Route **lite** when **all** hold:
1. It's a defect: the intake describes current vs expected behaviour, or comes from an issue labelled bug.
2. The expected behaviour is stated or obvious (no OP of kind *decision* would be needed).
3. Likely scope is one module, from a quick `nio query --path` / grep on the named symptom.
4. No risk flag from: auth, money, data-deletion, migration, PII (`spec.RISKS`). These always go full, because they need the jury's triggered lenses.

Route **epic** when the intake names more than ~3 independent user goals (one per would-be user story). Otherwise **full**.

**Show the call, then let the human flip it.** One plain-talk line: "Pick one: this looks like a small bugfix (one module, no risky data), so lite: repro, failing test, fix, one review. Full adds research, plan and tasks." The two lite→full escalation triggers in #44 (more than one module, new dependency, interface or data change) catch a wrong call later, so the router can be simple.

**Why not a model router.** RouteLLM-style learned routing needs labelled history NIO doesn't have yet. The four rules are checkable by the CLI and easy to explain. Revisit after #31 has data on mis-routes.

Refs: src/nio/cli.py (--route) · src/nio/spec.py (RISKS, ROUTES) · #40 · #44 · #31 · [Kiro bugfix specs](https://kiro.dev/docs/specs/bugfix-specs/)



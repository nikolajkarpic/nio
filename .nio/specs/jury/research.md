# Research: jury

Facts the grill looked up instead of asking.

- **RF-1** The jury's actors and journeys are defined by #27 and #47, and a live gate run (the logic lens and the refuter on a refunds spec, 2026-10-25) showed the loop end to end: three grounded contradictions, all confirmed, outcome rejected. Source: https://github.com/nikolajkarpic/nio/issues/27: "how lens outputs become one gate outcome, how findings are tracked to resolution".
- **RF-2** Only three agent cards exist: logic, refuter and spec-drafter. Testability, adversary, security, scope, consistency and triage have no card yet. Source: src/nio/agents/: "logic.md refuter.md spec-drafter.md".
- **RF-3** No lens-run cap is configured anywhere, and hit rate is not computed yet, although every ledger finding records its lenses and status. Source: src/nio/jury.py: "sources": [{"juror": …, "lens": …}].
- **RF-4** Nothing records which version of the spec a round judged: the ledger keeps hashes of the lens outputs it collected, not of the spec. Source: src/nio/jury.py:117: led["collected"][key] = sha.
- **RF-5** #47 (2026-10-25) decided 3 jurors only for lenses with high-severity findings; NORTH_STAR still says high risk or disagreement means 3 jurors, and #46 tracks its update. Source: https://github.com/nikolajkarpic/nio/issues/47: "The 3-juror escalation applies only to lenses with high-severity findings".
- **RF-6** The flow only enters the spec jury once the spec passes the gate. Source: https://github.com/nikolajkarpic/nio/issues/45: "grilling → spec_jury | `nio check spec` passes: no open points, no unconfirmed `default`".
- **RF-7** #27 decided who disposes what and how outcomes compose: the agent alone may spec-fix what changes no behaviour or open a question (back to the grill), behaviour changes go through the grill, accepted risk and out of scope are the human's, and every agent disposition is listed for the human. Source: https://github.com/nikolajkarpic/nio/issues/27: "Every disposition the agent sets is listed for the human to review at the gate".
- **RF-8** Points the grill deferred reach the jury as findings that only the human or a grill session closes. Source: src/nio/jury.py dispose(): "was deferred by the grill; only the human closes it".
- **RF-9** #27 covers every gate, but the plan and tasks artefacts don't exist yet. Source: https://github.com/nikolajkarpic/nio/issues/41: "The plan documents and their templates", still open.
- **RF-10** The scope lens checks FRs against the intake and the consistency lens checks the spec against memory and code. Source: https://github.com/nikolajkarpic/nio/issues/47: "scope: more than ~8 FRs, a new dependency, or an FR not traceable to the intake".

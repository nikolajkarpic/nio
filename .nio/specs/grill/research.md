# Research: grill

Facts the grill looked up instead of asking.

- **RF-1** The grill's actors come from the issue that defines it: the human settles decisions, an agent runs the loop and looks facts up, and the jury must see what was deferred. Source: https://github.com/nikolajkarpic/nio/issues/22: "`@nio:grill`: the question loop with the human."
- **RF-2** Grilling without scope control produces runaway sessions, and the usual cause is scope that should be split. Source: mattpocock/skills docs/productivity/grill-me.md:52: "two hundred questions… Usually the scope was too large".
- **RF-3** Spec-kit's clarify caps a session at 5 questions and guesses the rest. Source: github/spec-kit templates/commands/clarify.md:130: "Maximum of 5 total questions".
- **RF-4** "Checklist green" for the grill is the mechanical half of #21, which is `nio check spec --gate`; the judgement half belongs to the jury. Source: https://github.com/nikolajkarpic/nio/issues/21: "Mechanical, in the CLI (`nio check spec`)".

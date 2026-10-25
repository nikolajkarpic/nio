Split it: an epic with two slices (the grill loop, the checker changes), each re-drafted and juried.

## Source: .nio/specs/grill/spec.md (requirements moved out of the grill slice when it was split)

- FR-27 THE SYSTEM SHALL accept `[agent]` provenance in `nio check spec`, including at the gate, so the jury can see which decisions an agent made.
- FR-28 WHEN a spec has deferred points THE SYSTEM SHALL let it pass `nio check spec --gate` while listing them, and the jury SHALL turn each into a finding that needs the human's disposition (accepted risk or out of scope).
- FR-29 THE SYSTEM SHALL accept `[derived: <sources>]` in `nio check spec`, including at the gate, only when every source exists and none is itself derived.
- From FR-30: a contradiction the grill deferred, marked contradiction, is treated by the jury as a blocker finding.
- From AC-28: `nio check spec` rejects a synonym the glossary bans ("Never …") anywhere outside the glossary and Decisions.

## Source: the human's answers in the grill (`nio jury answers grill`)

- Q2: How far does an agent stand in for you? Delegate, tagged [agent]: the agent's answers are tagged [agent], never [human]; permissions, irreversible operations, money, deletion and breaking changes still wait for the human.
- Q3: Where do unsettled points go when the grill ends early? A Deferred section; `--gate` passes but lists them, and the jury turns each into a finding for the human.
- Q4: What provenance does a point settled by consequence carry? `[derived: …]` with sources; never derived from another derived item.
- Q10: An open contradiction is deferred as a blocker for the jury, with both sides quoted.
- Q13: Glossary discipline: `nio check spec` rejects a banned synonym anywhere else in the spec.

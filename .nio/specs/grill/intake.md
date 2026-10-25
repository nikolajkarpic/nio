lets do the grill, deepdive first

## Source: https://github.com/nikolajkarpic/nio/issues/22

### What needs designing

`@nio:grill`: the question loop with the human. Spec-kit's `clarify` caps it at **5 questions**, and `specify` at **3 `[NEEDS CLARIFICATION]`** markers, telling the agent to "make informed guesses" for the rest. Its own manifesto (`spec-driven.md`) says the opposite: "Don't guess". NORTH_STAR says vague requirements are the main source of hallucination, so NIO doesn't cap the questions. It **converges** instead.

Mechanisms to adopt:

- **Fact gate** (yoshi1220/speckit-grill-me, mattpocock grilling). Each candidate question is either a *fact* (code, memory, docs or research can answer it, so the agent looks it up and never asks) or a *decision* (only the human can make it). "Finding facts is always the agent's responsibility, not the user's."
- **Frontier rounds.** Only ask questions whose prerequisites are settled. Questions blocked on a running research job wait, and the others go ahead.
- **Coverage taxonomy**, from clarify's 10 categories (scope, domain and data, UX flow, NFRs, integrations, edge cases, constraints, terminology, completion signals, placeholders), plus the **6 core facets per stated goal** (meaning, actors and permissions, data/state effect, failure and conflict, transition from today, verification). Cover the core facets first, then raise the bar for asking.
- **Settlement by consequence.** Points that follow from accepted answers are written in with a citation and listed for review, never asked again. Permissions and irreversible operations are always asked.
- **Question format (decided 2026-10-24):** **one question at a time**, never a batch. Each question has a full question ending in `?`, a one-line "why it matters", and the verified facts it rests on. Then **exactly 3 options with one marked recommended**, giving what the agent thinks is best and why ("yes" accepts it), plus **one free-form input**.
- **Contradictions** are flagged and must be resolved before moving on, including contradictions with the code ("your code cancels whole orders, but you said partial cancellation is possible").
- Every answer is recorded as a decision with provenance (`human`), and the spec section is patched right away (as clarify does).

### What the design must define

- Stop rule: the checklist (#21) is green, the human confirms, or the human ends it early (open points become Deferred and are visible to the jury).
- A runaway guard. Pocock's grill got the issue "Codex asked me 200 questions". Options: a per-round threshold that rises, plus a soft budget that asks the human whether to continue.
- The grill state file (`grill.md`: frontier, asked, answered, deferred) so a new session can resume.
- The same skill runs the architecture grill with a different question source. The user advocate walk (#37) feeds its findings into this grill's queue.
- The grill fills in and confirms the spec's state and decision tables and its Risk flags (#47).



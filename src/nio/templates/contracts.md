---
slug: <slug>
retired: []                      # CT IDs removed from this plan; never reused
---
<!-- Contracts template: the interfaces this spec needs and where each lives in code. Derived from the approved spec,
architecture.md when it exists, and the code; never invented. Every item ends with its provenance, as in spec.md:
[human] (the human decided it), [agent] (a call below the grill's bar), [research: RF-n] (the code or research shows
it), [derived: <IDs>] (it follows from settled items) or [default] (your proposal; the plan jury judges it). IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in
`retired`. Remove a section or line that doesn't apply; never write N/A. Never restate the spec: cite its IDs, and
quote a constraint word for word when a builder needs it here. Open questions go in plan.md's Open points. -->
# Contracts: <title>

## Contracts

### CT-1 <name> (FR-1, FR-2) [default]
- Binding: `<file>:<symbol>` (new | existing)    <!-- the symbol is optional when the whole file is the contract -->
- Like: `<file>:<symbol>`    <!-- new contracts only: the existing code it follows, or `none: <reason>` when nothing is like it -->
- Kind: <function | class | cli | http | event | file | config>
- Shape: `<signature, command line or message>` | see `<project's own schema file>#<pointer>`
- Accepts: <each input and its limits>
- Returns: <what the caller gets>
- Fails: <condition> → <what the caller sees>
- Rules: "<constraint quoted word for word from the spec>" (FR-n)
- State: follows the spec's state table <name>

## Data model
<!-- Only when this spec stores or changes data. One entry per spec Key entity it touches. -->
- **<Entity>** (spec Key entity) in `<file>:<symbol>` (new | existing) [default]
  - <field>: <type>. "<constraint quoted word for word>" (FR-n)

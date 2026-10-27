---
slug: <slug>
retired: []                      # QS IDs removed from this plan; never reused
---
<!-- Quickstart template: one runnable scenario per journey in the spec, written as the human's demo script and
the evaluator's evidence. No implementation code. An `auto` scenario is run by the evaluator, which compares each
step's output with Expected: the exact output, or lines starting `contains:` that must each appear. A `manual`
scenario (UI, hardware, external accounts) goes to the human as a checklist. Provenance, permanent IDs and `retired`
work as in contracts.md. Open questions go in plan.md's Open points. -->
# Quickstart: <title>

## Prerequisites
- <tool, version or setup every scenario needs, with the command that installs or checks it>

## Scenarios

### QS-1 <journey name> (UJ-1; auto | manual) [default]
- Needs: <setup only this scenario needs, or leave the line out>

1. `<command>`
   Expected:
   ```
   <exact output>
   ```
2. `<command>`
   Expected:
   ```
   contains: <a line that must appear>
   ```
- Pass when: <every step matched, plus anything a person must see on a manual scenario>

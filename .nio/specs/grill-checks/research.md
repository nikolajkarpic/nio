# Research: grill-checks

Facts the grill looked up instead of asking.

- **RF-1** This slice's actors are the epic's: the human, the grill agent and the jury. Source: .nio/specs/grilling/spec.md:15: "A-1 Human", "A-2 Grill agent", "A-3 Jury".
- **RF-2** `nio check spec` accepts any `RF-n` as a `[derived: …]` source without looking for it in research.md. Source: src/nio/spec.py:367: "if src.startswith("RF-"): continue  # a research finding in research.md".
- **RF-3** `nio jury collect` adds deferred findings on every spec-gate collect, even when no lens output is new, and skips a DF a deferred finding already cites. Source: src/nio/jury.py:240: "if gate == "spec": out += deferred(led, root, slug)"; src/nio/jury.py:262: "known = {c for f in led["findings"] if any(s["lens"] == "deferred" …".
- **RF-4** `nio jury dispose` refuses `--by agent` on a deferred finding but accepts `--by grill`, with any disposition the grill may record, including spec-fix. Source: src/nio/jury.py:395: "if any(s["lens"] == "deferred" for s in f["sources"]) and by == "agent": raise ValueError".

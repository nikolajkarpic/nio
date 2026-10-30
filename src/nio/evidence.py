"""The implementation jury's CLI-first evidence (2026-10-27-implementation-jury): running commands in a throwaway copy of
the repo and the run's results file."""
import json
import os
import tempfile
from pathlib import Path

from nio import implement, records

RESULTS = "results.json"  # CT-7, under .nio/runs/<run>/
KEEP = 100_000  # FR-41: bytes kept at each end of a run's output


def cut(output):
    """(output, bytes cut): over 200 KB, its first and last 100 KB around a `cut N bytes` line (FR-41)."""
    raw = output.encode()
    n = len(raw) - 2 * KEEP
    if n <= 0:
        return output, 0
    return f"{raw[:KEEP].decode(errors='replace')}\n[cut {n} bytes]\n{raw[-KEEP:].decode(errors='replace')}", n


def one(copy, command, limit):
    """A command's entry in `in_copy`'s list."""
    if not command:
        return {"command": command, "result": "not configured", "output": "", "cut": 0}
    code, out, cause = implement.run(copy, command, limit)
    output, n = cut(out)
    if cause == "time limit":
        output += f"\ntimed out after {limit} seconds\n"
    return {"command": command, "result": "passed" if code == 0 else "failed", "output": output, "cut": n}


def in_copy(root, commit, commands, limit):
    """Run `commands` in order in one throwaway clone at `commit`, removed however the runs end (CT-2, FR-40, FR-41).
    Setup comes first in `commands`, so what it builds is there for the rest. ValueError, and nothing runs, when the
    clone can't be made."""
    limit = limit or implement.DEFAULT_LIMIT
    # A git hook or `rebase --exec` exports GIT_DIR and the like; left set, git in the copy would act on the human's repo.
    outer = {k: os.environ.pop(k) for k in records.git(root, "rev-parse", "--local-env-vars") if k in os.environ}
    try:
        with tempfile.TemporaryDirectory(prefix="nio-copy-", ignore_cleanup_errors=True) as tmp:
            copy = Path(tmp) / "copy"
            # --no-hardlinks: the temp folder is often another filesystem, where --local alone dies, and a linked
            # object file is one a run could write through. hooksPath: no global hooks or template hooks run here.
            clone = ("clone", "--local", "--no-hardlinks", "--no-checkout", "--config", "core.hooksPath=/dev/null",
                     str(Path(root).resolve()), str(copy))
            for where, args in ((tmp, clone), (copy, ("remote", "remove", "origin")),
                                (copy, ("checkout", "-q", "--detach", commit))):
                code, _, err = records.git(where, *args, full=True)
                if code:
                    raise ValueError(f"can't make the throwaway copy: {err.strip()}")
            return [one(copy, command, limit) for command in commands]
    finally:
        os.environ.update(outer)


def path(root, run):
    return Path(root) / ".nio/runs" / run / RESULTS


def load(root, run):
    """The run's results (CT-7), empty when none were written."""
    p = path(root, run)
    if p.exists():
        return json.loads(p.read_text())
    return {"commit": "", "tests": [], "checks": [], "attacks": [], "journeys": [], "hints": [], "requests": [], "evidence": []}


def save(root, run, results):
    p = path(root, run)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")

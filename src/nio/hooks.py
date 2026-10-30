"""Git hooks: refresh .nio/cache/index.db in the background and re-render agent cards after pulls, checkouts and
rebases, and run the CI check before commits and pushes. Only the checks block git, and only when `nio` is installed."""
import json
import shutil
from pathlib import Path

from nio import records

MARK = "# nio: memory hooks (installed by `nio hooks`)"
# the index refresh is slow, so it runs in the background; rendering agent cards is quick
INDEX = '[ -x "$NIO" ] && ( "$NIO" index </dev/null >/dev/null 2>&1 & )\n[ -x "$NIO" ] && "$NIO" agents sync >/dev/null 2>&1'
def check(base):
    """The CI check; on failure print the errors and stop git."""
    return f"""if [ -x "$NIO" ]; then
  out=$("$NIO" index --check --base "{base}" 2>&1) || {{
    printf '%s\\n' "$out" | grep -v "^WARN"
    echo "nio: memory check failed; fix the records, or skip once with --no-verify"
    exit 1
  }}
fi"""


BLOCKS = {
    # a merge can bring in a second record superseding the same decision: say so now, CI blocks the PR
    "post-merge": '[ -x "$NIO" ] && "$NIO" check | grep "^ERROR" && echo "nio: memory has errors after this merge; run nio check"\n' + INDEX,
    "post-checkout": f'if [ "${{3:-1}}" = 1 ]; then\n{INDEX}\nfi',  # branch switches only, not checking out single files
    "post-rewrite": INDEX,
    "pre-commit": check("HEAD"),
    # the remote's default branch, like CI's PR base; CI still checks the merge result
    "pre-push": 'base=$(git rev-parse --abbrev-ref origin/HEAD 2>/dev/null) || base=$(git rev-parse --abbrev-ref "@{upstream}" 2>/dev/null) || base=HEAD\n'
    + check("$base"),
}


def install(root, nio=None):
    """Add the nio block to each hook, or replace the one an older install wrote, keeping whatever else the hook
    does. Returns the hook paths."""
    nio = nio or shutil.which("nio")
    if not nio:
        raise ValueError("`nio` is not on PATH; install it with `uv tool install` or run this through `uv run`")
    folder = root / records.git(root, "rev-parse", "--git-path", "hooks")[0]  # honours core.hooksPath
    folder.mkdir(parents=True, exist_ok=True)
    out = []
    for name, block in BLOCKS.items():
        path = folder / name
        text = path.read_text() if path.exists() else "#!/bin/sh\n"
        if MARK in text:  # the block always ends at its own `true` line
            head, tail = text.split(MARK, 1)
            text = head + tail.split("\ntrue\n", 1)[1] if "\ntrue\n" in tail else head
        # `true`: post-checkout's status becomes git's, and a skipped step must not fail the checkout
        path.write_text(text.rstrip("\n") + f'\n\n{MARK}\nNIO="{Path(nio).absolute()}"\n{block}\ntrue\n')
        path.chmod(path.stat().st_mode | 0o111)
        out.append(path)
    return out


# stage work an agent may run unprompted; red and green are left out because they run any command they are given
ALLOW = ["check", "query", "get", "pack", "status", "index", "new", "run", "task", "agents sync", "agents verify",
         "flow next", "flow status", "flow start", "flow park", "flow done", "flow claim", "flow block",
         "jury template", "jury answers", "jury plan", "jury changed", "jury fixcheck", "jury collect", "jury dispose",
         "jury files", "jury check", "jury evidence", "jury pack"]
# the human's decisions always prompt. Short flags count: argparse takes --c for --commit and --h for --human.
# ponytail: pattern matching on the command text, a deterrent and not a boundary; the CLI's own rules still apply
ASK = ["*human*", "flow done *--c*", "flow done *--h*", "jury check *--h*"]


def allow(root, shared):
    """Merge the rules into Claude Code's settings for this repo, keeping what is there. Returns the file's path."""
    path = root / ".claude" / ("settings.json" if shared else "settings.local.json")
    try:
        cfg = json.loads(path.read_text()) if path.exists() else {}
    except ValueError as e:
        raise ValueError(f"{path} is not valid JSON, so nothing was changed: {e}")
    perms = cfg.setdefault("permissions", {})
    for key, rules in (("allow", [f"{r}:*" for r in ALLOW]), ("ask", ASK)):
        new = [f"Bash({run} {r})" for run in ("nio", "uv run nio") for r in rules]
        perms[key] = perms.get(key, []) + [r for r in new if r not in perms.get(key, [])]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2) + "\n")
    return path

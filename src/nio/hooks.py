"""Git hooks: refresh .nio/cache/index.db in the background and re-render agent cards after pulls, checkouts and
rebases, and run the CI check before commits and pushes. Only the checks block git, and only when `nio` is installed."""
import json
import shutil
import subprocess
from importlib import resources
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


def mods_dir():
    """The Claude Code mods: the packaged folder (an installed wheel), else the checkout's (an editable install)."""
    for d in (resources.files("nio") / "mods", Path(__file__).parents[2] / "tools/claude-mods"):
        if Path(str(d)).is_dir():
            return Path(str(d))
    raise ValueError("no NIO mods in this nio install")


MODS = ("background-nio-commands", "nio-status-pane")
CLAUDE_TIMEOUT = 120  # seconds per `claude plugin` call: a stalled install fails its mod instead of hanging setup (J-10)


def _claude(root, claude, *args):
    try:
        r = subprocess.run([claude, *args], cwd=root, capture_output=True, text=True, timeout=CLAUDE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {CLAUDE_TIMEOUT}s"
    return r.returncode, r.stdout, r.stderr


def mods_install(root, skip=False, claude="claude"):
    """One outcome line per mod; never raises, one mod failing never stops the other."""
    try:
        code, out, _ = _claude(root, claude, "plugin", "list", "--json")
        have = {e.get("id") for e in json.loads(out)} if code == 0 else set()
    except (OSError, ValueError, AttributeError):
        have = set()
    lines = []
    for mod in MODS:
        if f"{mod}@nio-mods" in have:
            lines.append(f"{mod}: already installed" + (" (left as is)" if skip else ""))
        elif skip:
            lines.append(f"{mod}: skipped")
        else:
            try:
                market = str(mods_dir())
                code, out, err = _claude(root, claude, "plugin", "install", mod, "--marketplace", market, "--scope", "local", "--json")
                text = (err.strip() or out.strip()).splitlines()
                lines.append(f"{mod}: installed" if code == 0 else f"{mod}: failed: {text[-1] if text else 'exit ' + str(code)}")
            except ValueError as e:
                lines.append(f"{mod}: failed: {e}")
            except OSError:
                lines.append(f"{mod}: failed: claude not found")
    return lines


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


# stage work an agent may run unprompted; finish is left out: it runs the tests and commits the epic
ALLOW = ["check", "query", "get", "pack", "status", "index", "new", "run", "task", "agents sync", "agents verify",
         "flow next", "flow status", "flow start", "flow park", "flow done", "flow claim", "flow block",
         "jury template", "jury answers", "jury plan", "jury changed", "jury fixcheck", "jury collect", "jury dispose",
         "jury files", "jury check", "jury evidence", "jury pack"]
# the human's decisions always prompt. Short flags count: argparse takes --c for --commit and --h for --human.
# ponytail: pattern matching on the command text, a deterrent and not a boundary; the CLI's own rules still apply
ASK = ["*human*", "flow done *--c*", "flow done *--h*", "jury check *--h*", "jury plan *--pick*"]


def settings(root, shared):
    """(path, parsed contents) of Claude Code's settings file for this repo."""
    path = root / ".claude" / ("settings.json" if shared else "settings.local.json")
    try:
        return path, json.loads(path.read_text()) if path.exists() else {}
    except ValueError as e:
        raise ValueError(f"{path} is not valid JSON, so nothing was changed: {e}")


def allow(root, shared):
    """Merge the rules into Claude Code's settings for this repo, keeping what is there. Returns the file's path."""
    path, cfg = settings(root, shared)
    perms = cfg.setdefault("permissions", {})
    for key, rules in (("allow", [f"{r}:*" for r in ALLOW]), ("ask", ASK)):
        new = [f"Bash({run} {r})" for run in ("nio", "uv run nio") for r in rules]
        perms[key] = perms.get(key, []) + [r for r in new if r not in perms.get(key, [])]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2) + "\n")
    return path

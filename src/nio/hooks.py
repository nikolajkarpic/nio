"""Git hooks: refresh .nio/cache/index.db in the background after pulls, checkouts and rebases, and run the CI
check before commits and pushes. Only the checks block git, and only when `nio` is installed."""
import shutil
from pathlib import Path

from nio import records

MARK = "# nio: memory hooks (installed by `nio hooks`)"
INDEX = '[ -x "$NIO" ] && ( "$NIO" index </dev/null >/dev/null 2>&1 & )'
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
    "post-checkout": f'[ "${{3:-1}}" = 1 ] && {INDEX}',  # branch switches only, not checking out single files
    "post-rewrite": INDEX,
    "pre-commit": check("HEAD"),
    # the remote's default branch, like CI's PR base; CI still checks the merge result
    "pre-push": 'base=$(git rev-parse --abbrev-ref origin/HEAD 2>/dev/null) || base=$(git rev-parse --abbrev-ref "@{upstream}" 2>/dev/null) || base=HEAD\n'
    + check("$base"),
}


def install(root, nio=None):
    """Add the nio block to each hook, keeping whatever the hook already does. Returns the hook paths."""
    nio = nio or shutil.which("nio")
    if not nio:
        raise ValueError("`nio` is not on PATH; install it with `uv tool install` or run this through `uv run`")
    folder = root / records.git(root, "rev-parse", "--git-path", "hooks")[0]  # honours core.hooksPath
    folder.mkdir(parents=True, exist_ok=True)
    out = []
    for name, block in BLOCKS.items():
        path = folder / name
        text = path.read_text() if path.exists() else "#!/bin/sh\n"
        if MARK not in text:
            # `true`: post-checkout's status becomes git's, and a skipped step must not fail the checkout
            path.write_text(text.rstrip("\n") + f'\n\n{MARK}\nNIO="{Path(nio).absolute()}"\n{block}\ntrue\n')
        path.chmod(path.stat().st_mode | 0o111)
        out.append(path)
    return out

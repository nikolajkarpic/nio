"""Self-check runner: call main(tests) last in a script's __main__ block."""
import os
import sys
import traceback


def main(tests):
    names = [a for a in sys.argv[1:] if not a.startswith("-")]
    known = {t.__name__ for t in tests}
    bad = [n for n in names if n not in known]
    for n in bad:
        print(f"no test named {n}")
    run = [] if bad else [t for t in tests if not names or t.__name__ in names]
    path = os.path.relpath(sys.modules["__main__"].__file__)  # a wrapped test's code lives in its wrapper's file
    failed = 0
    for t in run:
        try:
            print(f"{'skip' if t() == 'skipped' else 'ok'} {path}::{t.__name__}")
        except Exception:
            traceback.print_exc()
            print(f"FAIL {path}::{t.__name__}", flush=True)
            failed += 1
    print(f"ran {len(run)} tests, {failed} failed")
    sys.exit(0 if run and not failed else 1)

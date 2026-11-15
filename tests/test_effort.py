"""Self-check for the pr gate (2026-11-14-effort-jury): one implementation jury on the whole effort diff, after the last
task, on the pull request. GitHub is faked through `jury.hub`; nothing here touches the network.
Run: uv run python tests/test_effort.py"""
import tempfile
from pathlib import Path
import json
import re

import selfcheck
import test_flow
from test_implement import REFUNDS, RUN, S, TWO, close_epic, code_with, commit_all, flow, impl, lines, write_test

from nio import evidence, flow as nio_flow, implement, jury, tasks
from nio import records

HUB = []  # every (git|gh) call the gate made, in order
AT_TERMINAL = nio_flow.at_terminal  # the real one: `approve` below swaps in a fake


def fake_hub(fail=None, prs=None, comments=None):
    """Replace `jury.hub` with a fake GitHub: one PR list and one comment list; `fail` the step whose call exits 1."""
    HUB.clear()
    state = {"prs": prs if prs is not None else [], "comments": comments if comments is not None else {}}

    def hub(root, *args):
        HUB.append(args)
        step = "push" if args[:2] == ("git", "push") else "pull request" if args[:2] == ("gh", "pr") else "comment"
        if step == fail:
            return 1, "", f"{step} refused by the fake"
        if args[:3] == ("gh", "pr", "list"):
            return 0, (str(state["prs"][0]) + "\n") if state["prs"] else "", ""
        if args[:3] == ("gh", "pr", "create"):
            state["prs"].append(len(state["prs"]) + 1)
            return 0, "", ""
        if args[:2] == ("gh", "api"):
            body = next((a[5:] for a in args if a.startswith("body=")), None)
            if body is None:  # the list of comments
                return 0, "".join(f"{i}\n" for i, b in state["comments"].items() if jury.VERDICT_MARK in b), ""
            if "PATCH" in args:
                state["comments"][int(args[-3].rsplit("/", 1)[1])] = body
            else:
                state["comments"][len(state["comments"]) + 1] = body
        return 0, "", ""
    jury.hub = hub
    return state


def built(tasks_text=TWO, **kw):
    """Both epics of a two-epic effort (T-1, T-2 in E-1; T-3 in E-2) closed on their own test runs: at the pr gate."""
    root = impl(tasks=tasks_text, **kw)
    for eid in ("E-1", "E-2"):
        close_epic(root, eid)
    return root


def fix_epic(root, body="def refund(x):\n    return x  # fixed\n"):
    """Build the closing `PR fixes` epic as any other: claim it, change the code, finish it; finish's output."""
    code, out = flow(root, "claim", S)
    assert code == 0 and " PR fixes" in out, out
    eid = next(x.split()[1] for x in out.splitlines() if x.startswith("epic: "))
    code_with(root, body)
    code, out = flow(root, "finish", S, eid)
    assert code == 0, out
    return out


def step(root, run=""):
    return jury.step(root, S, "pr", run)


def juror(root, run, name, findings="none", matches=True):
    """A valid lens output for juror `name` (`<lens>` or `<lens>~<part>`); conformance matches every AC to test_refund."""
    lens = name.split("~")[0]
    line = next(n for n, x in enumerate((root / "tests/test_refund.py").read_text().splitlines(), 1) if "def test_refund" in x)
    body = "## Matches\n- AC-1 -> tests/test_refund.py:%d\n- AC-2 -> tests/test_refund.py:%d\n\n" % (line, line) if lens == "conformance" and matches else ""
    if findings != "none":
        base = {"cites": "AC-1", "kind": "gap", "severity": "major", "evidence": "observed", "quote": '"refund"',
                "situation": "x", "fix": "y", "gap": "missing", "where": "app.py"}
        findings = "".join(f"### F{i} {f['title']}\n" + "".join(f"- {k}: {v}\n" for k, v in {**base, **f}.items() if k != "title") + "\n"
                           for i, f in enumerate(findings, 1))
    path = root / f".nio/runs/{run}/jury/pr-{name}.md"
    path.write_text(f'---\nlens: {lens}\ngate: pr\nsubject: {S}\nby: "juror / claude-code / sonnet"\ncontext: sufficient\n---\n'
                    f"## Reasoning\nChecked.\n\n{body}## Findings\n{findings}\n")


def gate_round(root, findings=None):
    """One pr round to its outcome: start (push, PR), evidence, packs, every juror (`findings` {juror name: [dicts]}), the
    refuter confirming all. Returns (the run, the lines of every step)."""
    out = step(root)
    run = next(x[5:] for x in out if x.startswith("run: "))
    evidence.collect(root, S, "pr", run)
    out += step(root, run)
    names = json.loads((root / f".nio/runs/{run}/jury/packs/step.json").read_text())["lenses"]
    for name in names:
        juror(root, run, name, (findings or {}).get(name, "none"))
    out += step(root, run)
    if any("run nio-refuter" in x for x in out):
        pack = re.search(r"run nio-refuter on (\S+)", out[-1])[1]
        ids = re.findall(r"^### (J-\d+)", (root / pack).read_text(), re.M)
        (root / f".nio/runs/{run}/jury/pr-{Path(pack).stem}.md").write_text("".join(f"### {i}\n- result: confirmed\n- reason: so\n\n" for i in ids))
        out += step(root, run)
    return run, out


def stage(root):
    return nio_flow.where(root, S)["stage"]


def approve(root, typed=True):
    nio_flow.at_terminal = lambda slug: typed
    return nio_flow.approve(root, S)


def subjects(root):
    return test_flow.git(root, "log", "--format=%s").splitlines()


# --- US-1 ---

def test_effort_ac1_epic_closes_on_its_own_tests_no_jury():
    root = impl(tasks=TWO)
    out = close_epic(root, "E-1")
    assert not (root / f".nio/specs/{S}/jury/implementation-E-1.json").exists() and "implementation-E-1" not in out, out
    assert "task: E-2 " in flow(root, "next", S)[1] and stage(root) == "implementing"
    print("ok")


def test_epics_close_without_a_jury_then_one_pr_gate():
    """TC-6: epics close on their test runs with no jury; the pr gate is the one jury, and its findings become the
    `PR fixes` epic, rated per epic, which the next claim takes."""
    root = built()
    flow(root, "next", S)
    folder = root / f".nio/specs/{S}"
    assert not list(folder.glob("jury/implementation-E-*")), list(folder.glob("jury/*"))
    assert (lines(root)[-1]["kind"], lines(root)[-1]["from"], lines(root)[-1]["to"]) == ("pass", "implementing", "pr")
    fake_hub()
    errors = tasks.check(root, S)[0]  # the two-epic fixture's own
    _, out = gate_round(root, {"correctness": [{"title": "Refund pays twice"}]})
    assert "outcome: rejected" in out and (folder / "jury/pr.json").exists() and not list(folder.glob("jury/implementation-*")), out
    text = (folder / "tasks.md").read_text()
    assert "## E-3 PR fixes\n- Tier: strong: fixes from the pr jury\n- Effort: med\n" in text, text[-600:]
    assert tasks.check(root, S)[0] == errors
    code, out = flow(root, "claim", S)
    assert code == 0 and "epic: E-3 PR fixes" in out and "card: nio-worker-strong" in out, out
    print("ok")


def test_effort_ac2_last_task_moves_to_the_pr_gate_and_the_suite_runs_once_there():
    root = built()
    assert lines(root)[-1]["to"] == "pr" and stage(root) == "pr", lines(root)[-1]
    out = flow(root, "next", S)[1]
    assert "state: pr (working)" in out and "@nio:jury" in out, out
    runs = [x["evidence"] for x in lines(root) if x["kind"] == "epic_test"]
    assert len(runs) == 2 and not any(r["command"] == implement.records.config(root)["tests"]["suite"] for r in runs), runs
    fake_hub()
    run = next(x[5:] for x in step(root) if x.startswith("run: "))
    evidence.collect(root, S, "pr", run)
    suite = evidence.load(root, run)["suite"]
    assert suite["command"] == implement.records.config(root)["tests"]["suite"] and suite["result"] == "passed", suite
    print("ok")


def test_effort_ac3_out_of_flow_commit_is_judged():
    root = built()
    (root / "hand.py").write_text("HAND_FIX_MARK = 1\n")
    commit_all(root, "a hand fix")
    fake_hub()
    run = next(x[5:] for x in step(root) if x.startswith("run: "))
    evidence.collect(root, S, "pr", run)
    step(root, run)
    assert "HAND_FIX_MARK" in (root / f".nio/runs/{run}/jury/packs/correctness.md").read_text()
    print("ok")


def test_effort_ac4_core_lenses_and_refuter():
    root = built()
    out, ok = jury.plan(root, S, "pr")
    assert ok and out.lenses == jury.PR_CORE and "runs: 6 of 8" in out[2], out
    assert "refuter" in jury.agents.load(root) and "integration" in jury.agents.load(root)
    print("ok")


def test_effort_ac5_risk_flags_add_their_lenses():
    root = built()
    sp = root / f".nio/specs/{S}/spec.md"
    sp.write_text(re.sub(r"^risk: .*$", "risk: [auth, migration]", sp.read_text(), count=1, flags=re.M))
    out, ok = jury.plan(root, S, "pr")
    assert ok and out.lenses == jury.PR_CORE + ["security", "risk-rollback"] and "runs: 8 of 8" in out[2], out
    print("ok")


def test_effort_ac6_blocker_becomes_a_pr_fixes_task_then_suite_and_fix_check():
    root = built()
    fake_hub()
    errors = tasks.check(root, S)[0]  # the two-epic fixture's own
    _, out = gate_round(root, {"correctness": [{"title": "Refund pays twice"}]})
    assert "outcome: rejected" in out, out
    parsed = tasks.parse("\n".join(records.parse(tasks.path(root, S))[1]))
    last = parsed["epics"][-1]
    assert last["title"] == "PR fixes" and last["id"] == "E-3", last
    fix = parsed["tasks"][last["tasks"][0]]
    assert fix["fix"] and fix["fields"]["From"] == "J-1 (pr, round 1)", fix
    assert tasks.check(root, S)[0] == errors and stage(root) == "implementing"
    fix_epic(root)
    assert stage(root) == "pr"
    led = jury.load(root, S, "pr")
    run2 = next(x[5:] for x in step(root) if x.startswith("run: "))
    evidence.collect(root, S, "pr", run2)
    assert evidence.load(root, run2)["suite"]["result"] == "passed"
    packs = step(root, run2)
    assert any("pack .nio/runs/" in x for x in packs) and jury.load(root, S, "pr")["round"] == led["round"], packs
    print("ok")


def big(root, n):
    """A commit outside any epic adding `n` lines."""
    (root / "big.txt").write_text("".join(f"line {i}\n" for i in range(n)))
    commit_all(root, "a big hand-made file")


def split_root(extra):
    root = built()
    commit_all(root, "what the flow left untracked")  # so the big commit adds only its own lines
    base = evidence.changed_lines(root, S)
    big(root, extra - base)
    return root


def test_effort_ac17_over_the_limit_one_pack_per_epic_plus_rest_and_integration_whole():
    root = split_root(2501)
    assert evidence.changed_lines(root, S) == 2501 and list(evidence.split(root, S)) == ["E1", "E2", "rest"]
    fake_hub()
    run = next(x[5:] for x in step(root) if x.startswith("run: "))
    evidence.collect(root, S, "pr", run)
    step(root, run)
    names = json.loads((root / f".nio/runs/{run}/jury/packs/step.json").read_text())["lenses"]
    for lens in ("correctness", "conformance", "adversary", "consistency"):
        assert [n for n in names if n.split("~")[0] == lens] == [f"{lens}~E1", f"{lens}~E2", f"{lens}~rest"], names
    assert "integration" in names
    text = (root / f".nio/runs/{run}/jury/packs/integration.md").read_text()
    assert "Summary level" in text and "app.py" in text and "big.txt" in text, text
    print("ok")


def test_effort_ac17_earlier_efforts_task_commit_goes_to_rest():
    root = split_root(2501)
    branch = test_flow.git(root, "branch", "--show-current").strip()
    init = test_flow.git(root, "rev-list", "--max-parents=0", "HEAD").strip()
    test_flow.git(root, "branch", "-f", evidence.default_branch(root), init)  # the effort's own tasks.md is in its diff
    test_flow.git(root, "checkout", "-q", "-b", "earlier", init)  # the branch was cut from an unmerged earlier effort
    (root / "earlier.py").write_text("EARLIER = 1\n")
    commit_all(root, "T-1: an earlier effort's own T-1")
    old = test_flow.git(root, "rev-parse", "HEAD").strip()
    test_flow.git(root, "checkout", "-q", branch)
    test_flow.git(root, "rebase", "-q", "earlier")
    parts = evidence.split(root, S)
    assert list(parts) == ["E1", "E2", "rest"] and old in parts["rest"] and old not in parts["E1"], parts
    print("ok")


def test_effort_ac3_base_without_main_is_the_upstream_else_a_clear_error():
    root = built()
    test_flow.git(root, "branch", "-m", "master", "trunk")
    fake_hub()
    code, out, err = test_flow.run_main(root, "jury", "next", S, "pr")
    assert code == 1 and err.startswith("error: the pr gate has no default branch") and "Traceback" not in err, (out, err)
    assert nio_flow.guard(root, S, "pr")[0] == "fail" and stage(root) == "pr"
    test_flow.git(root, "branch", "--set-upstream-to=trunk")
    assert evidence.default_branch(root) == "trunk" and evidence.changed_lines(root, S) > 0
    assert test_flow.run_main(root, "jury", "next", S, "pr")[0] == 0
    print("ok")


def test_split_counts_no_nio_lines():
    root = split_root(10)
    before = evidence.changed_lines(root, S)
    (root / ".nio/specs" / S / "notes.md").write_text("x\n" * 5000)
    commit_all(root, "a long spec note")
    assert evidence.changed_lines(root, S) == before and evidence.split(root, S) == {}
    print("ok")


def test_skipped_e2e_test_passes_on_a_recorded_e2e_green():
    import subprocess, sys
    lines = [{"kind": "green", "evidence": {"command": "uv run python tests/a.py t_unit && NIO_E2E=1 uv run python tests/b_e2e.py test_x test_y"}},
             {"kind": "refused", "evidence": {"command": "NIO_E2E=1 uv run python tests/b_e2e.py test_z"}},
             {"kind": "green", "evidence": {"command": "uv run python tests/b_e2e.py test_w"}}]
    assert evidence.e2e_from(lines) == {("tests/b_e2e.py", "test_x"), ("tests/b_e2e.py", "test_y")}
    d = Path(tempfile.mkdtemp())
    (d / "t.py").write_text("import sys; sys.path.insert(0, %r)\nimport selfcheck\ndef test_a(): return 'skipped'\ndef test_b(): pass\n"
                            "selfcheck.main([test_a, test_b])\n" % str(Path(__file__).parent))
    out = subprocess.run([sys.executable, "t.py"], cwd=d, capture_output=True, text=True).stdout
    assert "skip t.py::test_a" in out and "ok t.py::test_b" in out, out
    print("ok")


def test_effort_ac17_exactly_at_the_limit_is_not_split():
    root = split_root(2500)
    assert evidence.changed_lines(root, S) == 2500 and evidence.split(root, S) == {}
    print("ok")


def test_effort_ac27_hand_fix_and_pr_fixes_task_only_in_the_rest_pack():
    root = split_root(2501)
    fake_hub()
    gate_round(root, {"correctness~E1": [{"title": "Refund pays twice"}]})
    fix_epic(root, "def refund(x):\n    return x\n\n\nPR_FIX_MARK = 1\n")
    run = records.new_run(root)
    evidence.collect(root, S, "pr", run)
    jury.save(root, {**jury.load(root, S, "pr"), "recorded": []})  # the full-review packs, not round 2's fix check
    parts = evidence.split(root, S)
    assert list(parts) == ["E1", "E2", "rest"], parts
    for lens in ("correctness", "conformance", "adversary", "consistency"):
        rest = evidence.pack(root, S, "pr", lens, run, "rest")
        assert "PR_FIX_MARK" in rest and "big.txt" in rest, lens
        for p in ("E1", "E2"):
            text = evidence.pack(root, S, "pr", lens, run, p)
            assert "PR_FIX_MARK" not in text and "big.txt" not in text and ("def refund" in text or p == "E2"), (lens, p)  # T-3 changes no code
    print("ok")


def test_effort_ac18_lite_route_gets_the_pr_gate():
    root = built(route="lite")
    assert stage(root) == "pr" and not list((root / f".nio/specs/{S}/jury").glob("implementation-*")), stage(root)
    assert "state: pr" in flow(root, "next", S)[1]
    print("ok")


# --- US-2 (the integration lens on real models: tests/test_lenses.py, NIO_E2E) ---

def test_effort_integration_card_is_valid():
    meta, body, _ = jury.agents.load(test_flow.repo())["integration"]
    assert not jury.agents.check("integration", meta, body) and meta["tools"] == ["read", "write"]
    print("ok")


# --- US-3 ---

def approved(root):
    fake_hub()
    _, out = gate_round(root)
    assert "outcome: approved" in out, out
    return out


def test_effort_ac10_pr_gate_is_its_own_unit_from_the_brief():
    root = impl(tasks=TWO)
    close_epic(root, "E-1")
    out = close_epic(root, "E-2")
    assert "fresh driver started from `nio flow brief" in out, out
    nxt = flow(root, "next", S)[1]
    assert "state: pr" in nxt and "skill: @nio:jury" in nxt, nxt
    assert "state: pr" in "\n".join(nio_flow.brief(root, S)[1])
    for name in ("jury", "implement"):
        text = " ".join((test_flow.Path(__file__).parent.parent / f"skills/{name}/SKILL.md").read_text().split())
        assert "the pr gate, on the whole effort diff, is always its own unit" in text, name
    print("ok")


def refused_done(root, auto):
    if auto:
        test_flow.history(root, S, {"kind": "start", "from": "pr", "to": "pr", "state": {"auto": True}})
    before = subjects(root)
    for args in (["done", "pr", S], ["done", "pr", S, "--commit", "--by", "human"]):
        code, out, err = test_flow.run_main(root, "flow", *args, *(["--by", test_flow.BY] if "--by" not in args else []))
        assert code == 1 and "nio flow approve" in out + err, (args, out, err)
    assert stage(root) == "pr" and subjects(root) == before


def test_effort_ac11_agent_done_refused_auto_on():
    root = built()
    approved(root)
    refused_done(root, auto=True)
    print("ok")


def test_effort_ac21_agent_done_refused_auto_off():
    root = built()
    approved(root)
    refused_done(root, auto=False)
    code, out = approve(root, typed=False)  # the approve command too, without the human at a terminal
    assert code == 1 and stage(root) == "pr", out
    print("ok")


def typed_at_tty(text):
    """Run the real `at_terminal` in a child whose controlling terminal is a fresh pty, type `text` at the prompt; returns
    whether it approved, or None where the platform has no pty."""
    import os
    try:
        import pty
        pid, fd = pty.fork()
    except (ImportError, OSError, AttributeError):
        return None
    if pid == 0:
        os._exit(0 if AT_TERMINAL(S) else 3)
    seen = b""
    try:
        while b"Type its slug" not in seen:
            chunk = os.read(fd, 1024)
            if not chunk:
                break
            seen += chunk
        os.write(fd, text.encode() + b"\n")
        while os.read(fd, 1024):
            pass
    except OSError:  # Linux: EIO once the child is gone
        pass
    code = os.waitstatus_to_exitcode(os.waitpid(pid, 0)[1])
    assert code in (0, 3), (code, seen)
    return code == 0


def test_effort_ac9_slug_typed_at_a_real_terminal():
    ok, wrong = typed_at_tty(S), typed_at_tty(S + "-not")
    if ok is None:
        print("skipped: no pty on this platform, at_terminal is untested here")
        return
    assert ok is True and wrong is False, (ok, wrong)
    print("ok")


def test_effort_ac22_merge_alone_records_nothing():
    root = built()
    approved(root)
    branch = test_flow.git(root, "branch", "--show-current").strip()
    test_flow.git(root, "checkout", "-q", "-B", "main")
    test_flow.git(root, "merge", "-q", branch)
    test_flow.git(root, "checkout", "-q", branch)
    assert stage(root) == "pr" and "nio: approve pr" not in subjects(root)
    print("ok")


def test_effort_ac23_unruled_finding_refuses_approval():
    root = built()
    fake_hub()
    (root / ".nio/config.json").write_text(json.dumps({**json.loads((root / ".nio/config.json").read_text()), "jury": {"max_rounds": 1}}))
    _, out = gate_round(root, {"correctness": [{"title": "Refund rounding", "severity": "major"}]})
    assert any(x.startswith("capped:") for x in out) and stage(root) == "pr", out  # the batch waits on the human
    led = jury.load(root, S, "pr")
    open_ = [f["id"] for f in led["findings"] if f["status"] == "open"]
    assert open_, led["findings"]
    code, out = approve(root)
    assert code == 1 and any(i in "\n".join(out) for i in open_) and stage(root) != "done", out
    print("ok")


def test_effort_ac12_human_approves_and_it_is_committed():
    root = built()
    approved(root)
    code, out = approve(root)
    assert code == 0 and "committed nio: approve pr" in out, out
    assert subjects(root)[0] == "nio: approve pr" and stage(root) == "done", subjects(root)
    print("ok")


def test_effort_ac13_capped_gate_closes_on_the_human_rulings():
    root = built()
    fake_hub()
    (root / ".nio/config.json").write_text(json.dumps({**json.loads((root / ".nio/config.json").read_text()), "jury": {"max_rounds": 1}}))
    _, out = gate_round(root, {"correctness": [{"title": "Refund rounding", "severity": "major"}]})
    assert any(x.startswith("capped:") for x in out), out
    jury.rule(root, S, "pr", "J-1", "accept", "fine as is")
    out = step(root)
    led = jury.load(root, S, "pr")
    assert led["findings"][0]["by"] == "human" and led.get("closed"), out
    assert nio_flow.guard(root, S, "pr")[0] in ("pass", "closed")  # every finding ruled: nothing left open
    code, o = approve(root)
    assert code == 0 and stage(root) == "done", o
    print("ok")


def test_effort_ac14_one_message_with_verdict_and_every_finding():
    root = built()
    fake_hub()
    _, out = gate_round(root, {"correctness": [{"title": "Refund pays twice"}]})
    at = out.index("outcome for the human:")
    msg = out[at + 1:]
    assert msg[0].startswith("REQUEST_CHANGES ") and msg[1].startswith("verdict: rejected") and "open:" in msg, msg
    assert any("J-1" in x and "fix-task by agent" in x for x in msg), msg
    print("ok")


def test_effort_ac19_pushed_pr_opened_one_verdict_comment_nothing_merged():
    root = built()
    st = fake_hub()
    _, out = gate_round(root)
    assert HUB[0][:2] == ("git", "push") and st["prs"] == [1] and len(st["comments"]) == 1, HUB
    body = st["comments"][1]
    head = jury.version_now(root, S, "pr")
    assert body.startswith(f"APPROVED {head}") and "verdict: approved" in body and jury.VERDICT_MARK in body, body
    assert not any("merge" in a for c in HUB for a in c) and stage(root) == "pr"
    print("ok")


def test_effort_ac24_reused_pr_and_one_edited_comment():
    root = built()
    st = fake_hub(prs=[7])
    gate_round(root, {"correctness": [{"title": "Refund pays twice"}]})
    first = dict(st["comments"])
    fix_epic(root)
    run = next(x[5:] for x in step(root) if x.startswith("run: "))
    evidence.collect(root, S, "pr", run)
    out = step(root, run)
    for name in json.loads((root / f".nio/runs/{run}/jury/packs/step.json").read_text())["lenses"]:
        p = root / f".nio/runs/{run}/jury/pr-{name}.md"
        juror(root, run, name)
        p.write_text(p.read_text().replace("## Findings", "## Verdicts\n- J-1: fixed — it pays once\n\n## Findings"))
    out = step(root, run)
    assert not any(c[:3] == ("gh", "pr", "create") for c in HUB) and st["prs"] == [7], HUB
    assert list(st["comments"]) == list(first) and st["comments"][1] != first[1], st["comments"]
    assert st["comments"][1].startswith("APPROVED " + jury.version_now(root, S, "pr")), (st["comments"], out)
    print("ok")


def test_effort_ac25_failed_step_stops_naming_it():
    for fail in ("push", "pull request", "comment"):
        root = built()
        fake_hub(fail=fail)
        try:
            gate_round(root)
            raise AssertionError(f"{fail} didn't stop the run")
        except ValueError as e:
            assert str(e).startswith(f"{fail} failed"), e
        code, out, err = test_flow.run_main(root, "jury", "next", S, "pr")
        assert code == 1 and f"{fail} failed" in err and stage(root) == "pr", (fail, out, err)
    # the comment step failed after the jury approved: no approval until the comment is on the pull request
    assert nio_flow.guard(root, S, "pr")[0] == "fail" and "nio flow approve" not in nio_flow.where(root, S)["command"]
    assert approve(root)[0] == 1 and stage(root) == "pr"
    st = fake_hub()
    code, out, err = test_flow.run_main(root, "jury", "next", S, "pr")
    assert code == 0 and len(st["comments"]) == 1 and st["comments"][1].startswith("APPROVED "), (out, err, st)
    assert f"nio flow approve {S}" in out and nio_flow.guard(root, S, "pr")[0] == "pass", out
    assert nio_flow.where(root, S)["command"] == f"nio flow approve {S}"
    print("ok")


def test_effort_ac26_stale_verdict_refuses_approval():
    root = built()
    approved(root)
    judged = jury.version(jury.load(root, S, "pr"), 1)
    (root / "late.py").write_text("x = 1\n")
    commit_all(root, "a late commit")
    assert test_flow.git(root, "rev-parse", "HEAD").strip() != judged
    code, out = approve(root)
    assert code == 1 and any("stale" in x for x in out) and stage(root) == "pr", out
    print("ok")


def test_effort_ac20_pr_fixes_done_push_updates_the_pr_and_fix_check_runs():
    root = built()
    st = fake_hub()
    gate_round(root, {"correctness": [{"title": "Refund pays twice"}]})
    fix_epic(root)
    assert lines(root)[-1]["to"] == "pr"
    pushes = sum(c[:2] == ("git", "push") for c in HUB)
    run = next(x[5:] for x in step(root) if x.startswith("run: "))
    assert sum(c[:2] == ("git", "push") for c in HUB) == pushes + 1 and st["prs"] == [1]
    evidence.collect(root, S, "pr", run)
    out = step(root, run)
    assert "Fix-check" in "".join(out) or any("pack" in x for x in out), out
    assert "This is a fix check" in (root / f".nio/runs/{run}/jury/packs/correctness.md").read_text()
    assert jury.load(root, S, "pr")["round"] == 1 and (root / f".nio/specs/{S}/jury/pr.json").exists()
    print("ok")


# --- US-4: efforts in flight ---

def old_done(root, *tids):
    """Tasks done under the per-task flow: their `task_done` lines and code, committed."""
    write_test(root)
    code_with(root)
    test_flow.git(root, "checkout", "-q", "-B", f"nio/{S}")
    test_flow.history(root, S, {"kind": "baseline", "from": "implementing", "to": "implementing", "evidence": {}},
                      *[implement.entry("task_done", t, commit="c") for t in tids])
    commit_all(root, f"{tids[-1]}: old flow")


def test_effort_ac15_in_flight_effort_switches_at_the_next_epic():
    root = impl(tasks=TWO)
    old_done(root, "T-1", "T-2")
    # E-1's old jury approved and closed before this change: its ledger and `epic` line
    led = jury.load(root, S, "implementation-E-1")
    led.update(round=1, outcome="approved", recorded=[[1, "approved"]])
    jury.save(root, led)
    test_flow.history(root, S, {"kind": "epic", "from": "implementing", "to": "implementing", "reason": "approved", "evidence": {"epic": "E-1"}})
    before = (root / f".nio/specs/{S}/history.jsonl").read_bytes()
    assert "task: E-2 " in flow(root, "next", S)[1]
    close_epic(root, "E-2")
    assert (root / f".nio/specs/{S}/history.jsonl").read_bytes().startswith(before) and stage(root) == "pr"
    fake_hub()
    run = next(x[5:] for x in step(root) if x.startswith("run: "))
    evidence.collect(root, S, "pr", run)
    step(root, run)
    assert "def refund" in (root / f".nio/runs/{run}/jury/packs/correctness.md").read_text()  # E-1's change, judged again
    print("ok")


def test_effort_ac28_epic_in_its_old_jury_finishes_it_first():
    root = impl(tasks=TWO)
    old_done(root, "T-1", "T-2")
    led = jury.load(root, S, "implementation-E-1")  # mid-round, a finding open
    led.update(round=1, outcome="rejected", recorded=[[1, "rejected"]], findings=[{
        "id": "J-1", "status": "open", "title": "x", "severity": "major", "kind": "gap", "cites": ["AC-1"], "quotes": [], "fix": "y",
        "sources": [{"juror": "implementation-E-1-correctness", "lens": "correctness", "situation": "x", "severity": "major"}],
        "validation": "confirmed", "reason": "", "disposition": "", "by": "", "note": "", "baseline": "new", "rounds": 0}])
    jury.save(root, led)
    out = flow(root, "next", S)[1]
    assert "implementation-E-1 is open" in out and "E-2" not in out, out
    assert jury.load(root, S, "implementation-E-1")["findings"][0]["status"] == "open"
    code, o = flow(root, "claim", S)
    assert code == 1 and "implementation-E-1" in o, o
    print("ok")


def test_effort_done_before_the_pr_gate_stays_done():
    root = impl(tasks=REFUNDS.split("### T-2")[0])
    close_epic(root, "E-1")
    test_flow.history(root, S, {"kind": "pass", "from": "implementing", "to": "done"})
    assert stage(root) == "done"
    test_flow.history(root, S, {"kind": "back", "from": "done", "to": "implementing", "change": "C-1"})  # sent back later
    assert stage(root) == "pr", stage(root)
    print("ok")


if __name__ == "__main__":
    selfcheck.main([f for n, f in list(globals().items()) if n.startswith("test_") and callable(f)])

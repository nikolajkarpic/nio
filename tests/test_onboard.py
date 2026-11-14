"""Self-check for nio onboard scan (2026-11-08-project-onboarding, T-1).
Run: uv run python tests/test_onboard.py"""
import hashlib
import subprocess
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import selfcheck


def repo(files, ignore=""):
    root = Path(tempfile.mkdtemp())
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / ".gitignore").write_text(ignore)
    for p, text in files.items():
        f = root / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
    return root


def scan(root):
    r = subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "onboard", "scan"],
                       cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout


def test_scan_lists_each_category():
    files = {"CLAUDE.md": "a", "README.md": "b", "ARCHITECTURE.md": "c", "pyproject.toml": "d", "main.tf": "e",
             ".github/workflows/ci.yml": "f"}
    want = {"CLAUDE.md": "agent-docs", "README.md": "product-docs", "ARCHITECTURE.md": "implementation-docs",
            "pyproject.toml": "manifests", "main.tf": "iac", ".github/workflows/ci.yml": "ci"}
    root = repo(files)
    code, out = scan(root)
    lines = out.strip().splitlines()
    assert lines and lines[-1] == "6 candidate files", out
    got = {l.split()[1]: l.split() for l in lines[:-1]}
    assert len(lines) == 7 and set(got) == set(want), out
    assert [l.split()[:2] for l in lines[:-1]] == sorted([c, p] for p, c in want.items()), out
    for p, cat in want.items():
        h = hashlib.sha256((root / p).read_bytes()).hexdigest()[:12]
        assert got[p] == [cat, p, h], (p, got[p])


def test_scan_secrets_path_only():
    root = repo({".env": "K=1", "prod.tfvars": "pw = 1"}, ignore=".env\n")
    subprocess.run(["git", "add", "prod.tfvars"], cwd=root, check=True)
    code, out = scan(root)
    lines = out.strip().splitlines()
    assert code == 0, out
    assert [l for l in lines if l.startswith("secrets")] == ["secrets .env", "secrets prod.tfvars"], out
    assert not [l for l in lines if not l.startswith("secrets") and (".env" in l or "prod.tfvars" in l)], out


def test_scan_more_secret_names():
    names = ["credentials.json", "deploy.pem", ".npmrc", "terraform.tfstate"]
    root = repo(dict.fromkeys(names, "s"))
    subprocess.run(["git", "add", *names], cwd=root, check=True)
    code, out = scan(root)
    lines = out.strip().splitlines()
    assert sorted(l for l in lines if l.startswith("secrets")) == sorted(f"secrets {n}" for n in names), out
    assert not [l for l in lines if not l.startswith("secrets") and any(n in l for n in names)], out


def test_scan_more_secret_patterns():
    names = ["id_ecdsa", "id_dsa", "a.keystore", "b.jks", ".htpasswd", "service-account-x.json", "Credentials.json", ".ENV"]
    root = repo(dict.fromkeys(names, "s") | {"secrets.tf": "x"})
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    lines = scan(root)[1].strip().splitlines()
    assert sorted(l for l in lines if l.startswith("secrets")) == sorted(f"secrets {n}" for n in names + ["secrets.tf"]), lines
    assert [l for l in lines if l.startswith("iac")] == ["iac secrets.tf"], lines


def test_backup_refuses_symlink_out_of_repo():
    root = repo({"a": "x"})
    outside = Path(tempfile.mkdtemp()) / "o.txt"
    outside.write_text("x")
    (root / "L.md").symlink_to(outside)
    r = nio(root, "backup", "L.md")
    assert r.returncode != 0, r.stdout
    assert not (root / ".nio/backup").exists()


def test_scan_skips_symlink():
    outside = Path(tempfile.mkdtemp()) / "README.md"
    outside.write_text("outside")
    root = repo({"CLAUDE.md": "a"})
    (root / "README.md").symlink_to(outside)
    code, out = scan(root)
    assert code == 0 and "CLAUDE.md" in out, out
    assert "README.md" not in out, out


def test_scan_prints_no_dependency():
    root = repo({"pyproject.toml": '[project]\ndependencies = ["requests>=2", "rich"]\n'})
    code, out = scan(root)
    assert "requests" not in out and "rich" not in out, out
    h = hashlib.sha256((root / "pyproject.toml").read_bytes()).hexdigest()[:12]
    assert f"manifests pyproject.toml {h}" in out.splitlines(), out


def test_scan_skips_ignored_and_nio():
    paths = ["build/README.md", ".nio/project/README.md", ".nio/backup/2026-11-08/CLAUDE.md"]
    root = repo({p: "x" for p in paths}, ignore="build/\n")
    code, out = scan(root)
    assert code == 0 and "candidate files" in out or "no candidate" in out, out
    assert not any(p in out for p in paths), out


def test_scan_empty_repo():
    root = repo({})
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"], cwd=root, check=True)
    code, out = scan(root)
    assert code == 0 and out.strip() == "no candidate files found", (code, out)


def test_scan_outside_git_repo():
    root = Path(tempfile.mkdtemp())
    r = subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "onboard", "scan"],
                       cwd=root, capture_output=True, text=True)
    assert r.returncode == 1 and "nio onboard scan needs a git repository" in r.stderr, (r.returncode, r.stdout, r.stderr)


def test_scan_keeps_non_ascii_paths():
    root = repo({"docs/résumé.md": "x", "docs/a b.md": "y"})
    code, out = scan(root)
    assert "docs/résumé.md" in out and "docs/a b.md" in out and "2 candidate files" in out, out


def test_scan_contract_categories():
    want = {"docs/x.md": "product-docs", "docs/adr/1.md": "implementation-docs", ".windsurfrules": "agent-docs",
            ".cursor/rules/a.mdc": "agent-docs", "Jenkinsfile": "ci", "fly.toml": "iac", "README.rst": "product-docs",
            "requirements-dev.txt": "manifests", "build.gradle.kts": "manifests", "docker-compose.prod.yml": "iac",
            ".gitlab-ci.yml": "ci"}
    root = repo(dict.fromkeys(want, "z"))
    code, out = scan(root)
    got = {l.split()[1]: l.split()[0] for l in out.strip().splitlines()[:-1]}
    assert got == want, got


def nio(root, *args):
    return subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "onboard", *args],
                          cwd=root, capture_output=True, text=True)


def test_skip_needs_reason():
    root = repo({})
    r = nio(root, "skip", "  ")
    assert r.returncode == 1, (r.stdout, r.stderr)
    assert not (root / ".nio/project/onboarding.json").exists()


def test_project_templates_match_headings():
    from nio import onboard
    d = Path(__file__).parent.parent / "src/nio/templates/project"
    for doc in onboard.DOCS:
        f = d / f"{doc}.md"
        assert f.exists(), f
        text = f.read_text()
        assert onboard.check_doc(doc, text) == [], (doc, onboard.check_doc(doc, text))
        assert [l[3:] for l in text.splitlines() if l.startswith("## ")] == onboard.HEADINGS[doc], doc


def test_empty_start_writes_blank_docs():
    root = repo({})
    r = nio(root, "start", "--empty")
    assert r.returncode == 0 and "next: product" in r.stdout, (r.stdout, r.stderr)
    for d in ("stack", "architecture", "infra"):
        text = (root / f".nio/project/{d}.md").read_text()
        bodies = [b for b in text.split("\n## ")[1:]]
        assert bodies and all("NEEDS CLARIFICATION" in b for b in bodies), (d, text)
    assert nio(root, "pause").returncode == 0
    r = nio(root, "pause")
    assert r.returncode == 0 and "ignored: onboarding is paused" in r.stdout, (r.stdout, r.stderr)
    r = nio(root, "confirm", "stack")
    assert r.returncode == 0 and "ignored: onboarding is paused" in r.stdout, (r.stdout, r.stderr)


def test_empty_start_keeps_existing_docs():
    root = repo({})
    d = root / ".nio/project"
    d.mkdir(parents=True)
    (d / "stack.md").write_text("confirmed stack\n")
    (d / "product.md").write_text("mine\n")
    assert nio(root, "start", "--empty").returncode == 0
    assert (d / "stack.md").read_text() == "confirmed stack\n"
    assert (d / "product.md").read_text() == "mine\n"
    assert (d / "architecture.md").exists() and (d / "infra.md").exists()
    assert not (d / "personas.md").exists() and not (d / "principles.md").exists()


def test_state_table_cells():
    import json
    # (state to reach, action) -> (exit, stdout fragment); "x" is the skip reason
    def at(state):
        root = repo({})
        steps = {"not started": [], "in progress": [["start"]], "paused": [["start"], ["pause"]], "skipped": [["skip", "r"]],
                 "done": [["start", "--empty"]]}[state]
        for a in steps:
            assert nio(root, *a).returncode == 0, a
        if state == "done":
            d = root / ".nio/project"
            tpl = Path(__file__).parent.parent / "src/nio/templates/project"
            for n in ("product", "personas", "principles"):
                (d / f"{n}.md").write_text((tpl / f"{n}.md").read_text().replace("NEEDS CLARIFICATION", "filled (source: dev, 2026-11-14)"))
                nio(root, "confirm", n)
        return root
    cells = {
        ("not started", "pause"): (0, "ignored"), ("not started", "confirm"): (0, "ignored"), ("not started", "start"): (0, "next:"),
        ("not started", "skip"): (0, "skipped"),
        ("in progress", "start"): (0, "ignored"), ("in progress", "pause"): (0, "paused"), ("in progress", "skip"): (0, "skipped"),
        ("paused", "start"): (0, "next:"), ("paused", "pause"): (0, "ignored"), ("paused", "confirm"): (0, "ignored"),
        ("paused", "skip"): (0, "skipped"),
        ("skipped", "start"): (0, "next:"), ("skipped", "pause"): (0, "ignored"), ("skipped", "confirm"): (0, "ignored"),
        ("skipped", "skip"): (0, "ignored"),
        ("done", "start"): (1, "onboarding is done"), ("done", "skip"): (1, "onboarding is done already"),
        ("done", "pause"): (0, "ignored"), ("done", "confirm"): (0, "ignored"),
    }
    for (state, action), (code, frag) in cells.items():
        root = at(state)
        before = (root / ".nio/project/onboarding.json")
        before = before.read_text() if before.exists() else None
        args = {"skip": ["skip", "y"], "confirm": ["confirm", "product"]}.get(action, [action])
        r = nio(root, *args)
        assert r.returncode == code and frag in r.stdout + r.stderr, (state, action, r.returncode, r.stdout, r.stderr)
        if frag == "ignored" or code == 1:
            f = root / ".nio/project/onboarding.json"
            assert (f.read_text() if f.exists() else None) == before, (state, action)
    root = at("paused")
    nio(root, "pause")
    f = root / ".nio/project/onboarding.json"
    st = json.loads(f.read_text()); st["confirmed"] = ["product"]; f.write_text(json.dumps(st))
    assert nio(root, "start", "--empty").returncode == 0
    st = json.loads(f.read_text())
    assert st["state"] == "in progress" and st["confirmed"] == ["product"] and st["empty"] is False, st


def newspec(root, route):
    return subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "new", "spec", "x", "--route", route],
                          cwd=root, capture_output=True, text=True)


def test_spec_waits_for_onboarding():
    root = repo({})
    for step in (None, ["start"], ["pause"]):
        if step:
            assert nio(root, *step).returncode == 0
        for route in ("full", "epic"):
            r = newspec(root, route)
            msg = r.stdout + r.stderr
            assert r.returncode == 1 and "@nio:onboard" in msg and "nio onboard skip" in msg, (step, route, msg)
            assert not list((root / ".nio/specs").glob("*")), (step, route)


def test_lite_spec_starts():
    root = repo({})
    r = newspec(root, "lite")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert list((root / ".nio/specs").glob("*/spec.md"))


def test_torn_progress_file():
    root = repo({})
    assert nio(root, "start").returncode == 0
    f = root / ".nio/project/onboarding.json"
    f.write_bytes(f.read_bytes()[:10])
    before = f.read_bytes()
    for r in (nio(root, "start"), newspec(root, "full")):
        assert r.returncode == 1 and ".nio/project/onboarding.json" in r.stdout + r.stderr, (r.stdout, r.stderr)
    assert f.read_bytes() == before


def status(root):
    return subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "status"],
                          cwd=root, capture_output=True, text=True)


def test_torn_progress_file_status():
    root = repo({})
    assert nio(root, "start").returncode == 0
    f = root / ".nio/project/onboarding.json"
    for bad in (f.read_bytes()[:10], b"[]", b'{"state": "paused"}'):
        f.write_bytes(bad)
        for r in (status(root), nio(root, "start"), nio(root, "confirm", "product")):
            out = r.stdout + r.stderr
            assert "Traceback" not in out and ".nio/project/onboarding.json" in out, (bad, out)
    f.unlink()
    assert nio(root, "skip", "a\nonboarding: done").returncode == 0
    assert sum(l.startswith("onboarding:") for l in status(root).stdout.splitlines()) == 1
    assert not list(f.parent.glob("*.tmp"))


def test_skip_lets_spec_start():
    root = repo({})
    assert nio(root, "skip", "prototype").returncode == 0
    import json
    got = json.loads((root / ".nio/project/onboarding.json").read_text())
    assert got["state"] == "skipped" and got["reason"] == "prototype", got
    r = newspec(root, "full")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert list((root / ".nio/specs").glob("*/spec.md"))
    r = status(root)
    assert "onboarding: skipped: prototype" in r.stdout, (r.stdout, r.stderr)


def test_skip_stays_visible():
    root = repo({})
    assert nio(root, "skip", "prototype").returncode == 0
    assert newspec(root, "full").returncode == 0
    r = status(root)
    assert "onboarding: skipped: prototype" in r.stdout, (r.stdout, r.stderr)
    r = nio(root, "start")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "onboarding: in progress" in status(root).stdout


def test_confirm_checks_docs_and_finishes():
    import json
    root = repo({"README.md": "hi\n"})
    d = root / ".nio/project"
    assert nio(root, "confirm", "product").returncode == 0  # not started: ignored
    assert not (d / "onboarding.json").exists()
    assert nio(root, "start", "--empty").returncode == 0
    r = nio(root, "confirm", "product")
    assert r.returncode == 1, (r.stdout, r.stderr)
    r = nio(root, "confirm", "stack")  # blank stub still holds NEEDS CLARIFICATION
    assert r.returncode == 1, (r.stdout, r.stderr)
    tpl = Path(__file__).parent.parent / "src/nio/templates/project"
    for n in ("product", "personas", "principles"):
        (d / f"{n}.md").write_text((tpl / f"{n}.md").read_text().replace("NEEDS CLARIFICATION", "filled (source: dev, 2026-11-14)"))
        r = nio(root, "confirm", n)
        assert r.returncode == 0, (n, r.stdout, r.stderr)
    assert "done" in r.stdout, r.stdout
    got = json.loads((d / "onboarding.json").read_text())
    assert got["state"] == "done" and got["seen"], got
    for a in ("start", "pause", "skip x"):
        nio(root, *a.split())
    assert json.loads((d / "onboarding.json").read_text())["state"] == "done"
    assert newspec(root, "full").returncode == 0


def test_confirm_refuses_missing_source_and_secret():
    root = repo({"README.md": "hi\n"})
    d = root / ".nio/project"
    assert nio(root, "start", "--empty").returncode == 0
    tpl = Path(__file__).parent.parent / "src/nio/templates/project"
    base = (tpl / "product.md").read_text().replace("NEEDS CLARIFICATION", "x (source: dev, 2026-11-14)")
    (d / "product.md").write_text(base.replace("x (source: dev, 2026-11-14)", "no record", 1))
    r = nio(root, "confirm", "product")
    assert r.returncode == 1 and "line 5" in r.stdout + r.stderr and "source" in r.stdout + r.stderr, (r.stdout, r.stderr)
    key = "ghp_" + "a" * 36
    (d / "product.md").write_text(base.replace("x (source: dev, 2026-11-14)", f"k {key} (source: dev, 2026-11-14)", 1))
    r = nio(root, "confirm", "product")
    out = r.stdout + r.stderr
    assert r.returncode == 1 and "line 5" in out and "secret" in out and key not in out, (r.stdout, r.stderr)
    (d / "product.md").write_text(base)
    assert nio(root, "confirm", "product").returncode == 0


def test_onboard_from_subdirectory_uses_repo_root():
    root = repo({"src/a.py": "x"})
    r = nio(root / "src", "skip", "prototype")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert (root / ".nio/project/onboarding.json").exists()
    assert not (root / "src/.nio").exists()


def test_onboard_act_outside_git_repo():
    import tempfile
    r = nio(Path(tempfile.mkdtemp()), "skip", "x")
    assert r.returncode == 1 and "needs a git repository" in r.stderr, (r.stdout, r.stderr)


def test_next_doc_first_unconfirmed():
    from nio import onboard
    p = {"empty": True, "confirmed": ["product", "personas"]}
    assert onboard.next_doc(p) == "principles", onboard.next_doc(p)
    assert onboard.next_doc({"empty": False, "confirmed": ["product", "personas"]}) == "stack"
    assert onboard.next_doc({"empty": True, "confirmed": ["product", "personas", "principles"]}) is None


def pack_reader(root, reader):
    return subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "pack", "x", "--reader", reader],
                          cwd=root, capture_output=True, text=True)


def setup_project(root, state, docs, reason=""):
    import json
    d = root / ".nio/project"
    d.mkdir(parents=True, exist_ok=True)
    for n, t in docs.items():
        (d / f"{n}.md").write_text(t)
    (d / "onboarding.json").write_text(json.dumps({"state": state, "reason": reason, "empty": False, "apps": {},
                                                    "confirmed": list(docs), "seen": []}))


def test_missing_doc_named():
    root = repo({})
    setup_project(root, "done", {n: f"## H\n{n} text\n" for n in ("product", "personas", "stack", "architecture", "principles")})
    r = pack_reader(root, "plan")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "missing: infra.md" in r.stdout, r.stdout


def test_skipped_pack():
    root = repo({})
    setup_project(root, "skipped", {"product": "## H\nproduct text\n"}, "prototype")
    r = pack_reader(root, "spec")
    assert r.returncode == 0, (r.stdout, r.stderr)
    heads = [l for l in r.stdout.splitlines() if l.startswith("### ") and l.endswith(".md")]
    assert heads == ["### product.md"], heads
    assert "onboarding: skipped: prototype" in r.stdout, r.stdout
    assert "missing:" not in r.stdout, r.stdout


def test_oversized_doc_flagged():
    root = repo({})
    body = "## Stack\n" + "x" * 19 + "\n" + ("y" * 99 + "\n") * 200 + "THE LAST LINE\n"
    setup_project(root, "done", {"stack": body, "principles": "## P\np\n"})
    r = pack_reader(root, "worker")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "THE LAST LINE" in r.stdout, r.stdout[-300:]
    assert "over 16 KB: stack.md (20 KB)" in r.stdout, r.stdout


ROWS = {"spec": ["product.md", "personas.md"], "plan": ["stack.md", "architecture.md", "infra.md", "principles.md"], "worker": ["stack.md", "principles.md"]}
ROWS["scope"], ROWS["architecture-fit"] = ROWS["spec"], ROWS["plan"]
SIX = {n: f"## {n.title()}\n{n} text\n" for n in ("product", "personas", "stack", "architecture", "infra", "principles")}


def headings(text):
    return [l[4:] for l in text.splitlines() if l.startswith("### ") and l.endswith(".md")]


def test_reader_packs():
    for r, want in ROWS.items():
        root = repo({})
        setup_project(root, "done", SIX)
        out = pack_reader(root, r)
        assert out.returncode == 0, (r, out.stdout, out.stderr)
        assert headings(out.stdout) == want, (r, headings(out.stdout))
    from test_jury import plan_repo, PSLUG
    from nio import jury
    root = plan_repo()
    setup_project(root, "done", SIX)
    got = headings(jury._pack_text(root, PSLUG, "spec", "R-1", "scope", False))
    assert got == ROWS["spec"], got
    got = headings(jury._pack_text(root, PSLUG, "plan", "R-1", "architecture-fit", False))
    assert got == ROWS["plan"], got
    import test_implement
    from nio import implement
    root = test_implement.impl()
    setup_project(root, "done", SIX)
    task = implement.tasks_of(root, test_implement.S)[0]
    text = implement.worker_pack(root, test_implement.S, task)
    assert headings(text) == ROWS["worker"], headings(text)
    assert len([l for l in text.splitlines() if l.startswith("## ")]) == 5, text


def test_lens_sources_include_docs():
    from test_jury import plan_repo, PSLUG
    from nio import jury
    root = plan_repo()
    setup_project(root, "done", SIX)
    p = root / ".nio/project/principles.md"
    assert p in jury.sources(root, PSLUG, "plan", lens="architecture-fit"), "docs not in sources"
    assert p not in jury.sources(root, PSLUG, "plan", lens="test-proof"), "test-proof must not get docs"
    text = jury._pack_text(root, PSLUG, "plan", "R-1", "architecture-fit", False)
    assert ".nio/project/principles.md" in text.split("## nio check")[0], text[:600]


def test_doc_quote_grounds_for_its_lens():
    from test_jury import plan_repo, PSLUG
    from nio import jury
    root = plan_repo()
    setup_project(root, "done", SIX)
    f = {"cites": [], "quotes": ["principles text"]}
    assert jury.grounded(f, jury.grounding(root, PSLUG, "plan", "architecture-fit")), "doc quote not grounded"
    assert not jury.grounded(f, jury.grounding(root, PSLUG, "plan", "test-proof")), "no-docs lens grounded"


def test_corrupt_progress_does_not_block_docs():
    from nio import onboard
    root = Path(tempfile.mkdtemp())
    (root / ".nio/project").mkdir(parents=True)
    (root / ".nio/project/onboarding.json").write_text("{half")
    out = onboard.docs_for(root, "worker")
    assert "onboarding: unreadable: fix .nio/project/onboarding.json" in out, out
    assert "### " not in out, out


def test_symlinked_doc_not_read():
    from nio import onboard
    root = Path(tempfile.mkdtemp())
    (root / ".nio/project").mkdir(parents=True)
    secret = Path(tempfile.mkdtemp()) / "secret"
    secret.write_text("TOPSECRET")
    (root / ".nio/project/stack.md").symlink_to(secret)
    (root / ".nio/project/principles.md").write_text("# P\nok\n")
    out = onboard.docs_for(root, "worker")
    assert "TOPSECRET" not in out, out
    assert "missing: stack.md" in out, out


def test_apps_line_front_matter_only():
    import json
    from nio import onboard
    root = Path(tempfile.mkdtemp())
    (root / ".nio/project").mkdir(parents=True)
    (root / ".nio/project/onboarding.json").write_text(json.dumps({"state": "done", "reason": "", "empty": False, "apps": {"api": {}, "web": {}}, "confirmed": [], "seen": []}))
    sp = root / ".nio/specs/s"
    sp.mkdir(parents=True)
    names = lambda: [n for n, _ in onboard._pairs(root, "worker", "s")]
    for body in ("---\napps: [api]\n---\n", "---\napps:\n  - api\n---\n"):
        (sp / "spec.md").write_text(body)
        assert all(n.startswith("api/") for n in names()), names()
    (sp / "spec.md").write_text("---\ntitle: x\n---\n```\napps: web\n```\n")
    assert any(n.startswith("api/") for n in names()), names()
    (sp / "spec.md").write_text("---\napps: [api, ghost]\n---\n")
    assert "not onboarded: ghost" in onboard.docs_for(root, "worker", "s")


def test_check_spec_apps():
    import json
    root = repo({})
    (root / ".nio/project").mkdir(parents=True, exist_ok=True)
    for a in ("web", "api"):
        (root / ".nio/project" / a).mkdir()
    (root / ".nio/project/onboarding.json").write_text(json.dumps({"state": "done", "reason": "", "empty": False, "apps": {"api": {}, "web": {}}, "confirmed": [], "seen": []}))
    assert newspec(root, "full").returncode == 0
    f = next((root / ".nio/specs").glob("*/spec.md"))
    slug = f.parent.name
    text = f.read_text()
    assert text.startswith("---\n"), text[:40]
    for val, want in (("[mobile]", "app mobile has no project docs (.nio/project/mobile/)"),
                      ("[]", "spec names no app; the project has apps: api, web")):
        body = "".join(ln for ln in text.splitlines(keepends=True) if not ln.startswith("apps:"))
        f.write_text(body.replace("---\n", f"---\napps: {val}\n", 1))
        r = subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "check", "spec", slug],
                           cwd=root, capture_output=True, text=True)
        assert r.returncode == 1 and want in r.stdout + r.stderr, (val, r.returncode, r.stdout, r.stderr)


def test_backup_keeps_first_copy():
    import datetime
    root = repo({"CLAUDE.md": "rules v1"})
    want = f".nio/backup/{datetime.date.today().isoformat()}/CLAUDE.md"
    r = nio(root, "backup", "CLAUDE.md")
    assert r.returncode == 0 and want in r.stdout, (r.stdout, r.stderr)
    (root / "CLAUDE.md").write_text("rules v2")
    r = nio(root, "backup", "CLAUDE.md")
    assert r.returncode == 0 and want in r.stdout, (r.stdout, r.stderr)
    assert (root / want).read_bytes() == b"rules v1"
    before = sorted(p.relative_to(root) for p in (root / ".nio/backup").rglob("*")) if (root / ".nio/backup").exists() else []
    assert before, "no backup written"
    for bad in ("missing.md", "../outside.md"):
        r = nio(root, "backup", bad)
        assert r.returncode == 1, (bad, r.returncode, r.stdout, r.stderr)
    assert sorted(p.relative_to(root) for p in (root / ".nio/backup").rglob("*")) == before


def test_six_docs_with_headings():
    from nio import onboard
    root = repo({})
    assert nio(root, "start").returncode == 0
    d = root / ".nio/project"
    tpl = Path(__file__).parent.parent / "src/nio/templates/project"
    for doc in onboard.DOCS:
        text = (tpl / f"{doc}.md").read_text().replace("NEEDS CLARIFICATION", "answered (source: dev, 2026-11-14)")
        if doc == "personas":
            text = text.replace("Who:", "Who: a dev").replace("Wants:", "Wants: speed").replace("Allowed to:", "Allowed to: all").replace("How often:", "How often: daily")
        (d / f"{doc}.md").write_text(text)
    stack = (d / "stack.md").read_text()
    (d / "stack.md").write_text(stack.replace("## Commands", ""))
    r = nio(root, "confirm", "stack")
    assert r.returncode == 1 and "Commands" in r.stdout + r.stderr, (r.stdout, r.stderr)
    assert onboard.progress(root)["confirmed"] == []
    (d / "stack.md").write_text(stack)
    persona = (d / "personas.md").read_text()
    (d / "personas.md").write_text(persona.replace("### P-", "### Q-"))
    r = nio(root, "confirm", "personas")
    assert r.returncode == 1 and "no persona entry" in r.stdout + r.stderr, (r.stdout, r.stderr)
    (d / "personas.md").write_text(persona)
    for doc in onboard.DOCS:
        r = nio(root, "confirm", doc)
        assert r.returncode == 0, (doc, r.stdout, r.stderr)
    assert onboard.progress(root)["state"] == "done"
    want = {"product": ["What it does", "Users", "Main flows", "Non-goals", "Glossary"],
            "stack": ["Languages", "Dependencies", "Commands", "CI"],
            "architecture": ["Modules", "Boundaries", "Data flow"],
            "infra": ["Cloud provider", "Deployables", "Eventing and queues", "Storage", "Secrets", "Environments", "Deploys"],
            "principles": ["Principles"]}
    for doc, hs in want.items():
        text = (d / f"{doc}.md").read_text()
        for h in hs:
            assert f"## {h}" in text, (doc, h)
    text = (d / "personas.md").read_text()
    for x in ("### P-1", "Who:", "Wants:", "Allowed to:", "How often:"):
        assert x in text, x


def test_fact_names_file_and_hash():
    from nio import onboard
    root = repo({"pyproject.toml": "[project]\nname='x'\n"})
    code, out = scan(root)
    h = next(l.split()[2] for l in out.splitlines() if l.split()[1:2] == ["pyproject.toml"])
    line = f"- Python 3.12 (source: pyproject.toml@{h})"
    d = root / ".nio/project"
    d.mkdir(parents=True)
    (d / "stack.md").write_text("# Stack\n\n## Languages\n" + line + "\n")
    assert hasattr(onboard, "stale"), "onboard.stale missing"
    assert onboard.stale(root) == []
    assert onboard.SOURCE.findall(line) == [("pyproject.toml", h)]
    (root / "pyproject.toml").write_text("changed\n")
    assert onboard.stale(root) == [("stack.md", "pyproject.toml", "changed")]


def test_skills_keep_skip_with_dev():
    import re
    root = Path(__file__).resolve().parent.parent
    for name in ("onboard", "reconcile-onboarding"):
        f = root / "skills" / name / "SKILL.md"
        if name != "onboard" and not f.exists():
            continue  # written by T-23; its check runs once the file exists
        assert f.exists(), f"{f} missing"
        text = " ".join(f.read_text().split())
        assert "never run `nio onboard skip`" in text, name
        assert re.search(r"no doc is (recorded as )?confirmed and no patch (is )?applied without the dev's answer in that session", text), name

def test_apps_start_and_confirm():
    import json
    root = repo({"README.md": "hi\n"})
    d = root / ".nio/project"
    r = nio(root, "start", "--empty", "--app", "web=web/", "--app", "api=api/,lib/")
    assert r.returncode == 0 and "next: web/product" in r.stdout, (r.stdout, r.stderr)
    assert json.loads((d / "onboarding.json").read_text())["apps"] == {"web": ["web/"], "api": ["api/", "lib/"]}
    assert nio(root, "confirm", "product").returncode == 1  # --app required
    assert nio(root, "confirm", "product", "--app", "nope").returncode == 1
    tpl = Path(__file__).parent.parent / "src/nio/templates/project"
    for a in ("web", "api"):
        for n in ("product", "personas", "principles"):
            (d / a / f"{n}.md").write_text((tpl / f"{n}.md").read_text().replace("NEEDS CLARIFICATION", "filled (source: dev, 2026-11-14)"))
            r = nio(root, "confirm", n, "--app", a)
            assert r.returncode == 0, (a, n, r.stdout, r.stderr)
    assert "done" in r.stdout and json.loads((d / "onboarding.json").read_text())["state"] == "done"


def test_app_slug_not_a_doc_name():
    root = repo({"README.md": "hi\n"})
    assert nio(root, "start", "--app", "stack=x/").returncode == 1
    assert not (root / ".nio/project/onboarding.json").exists()
def two_apps(root, apps_line):
    import json
    d = root / ".nio/project"
    for a in ("web", "api"):
        (d / a).mkdir(parents=True, exist_ok=True)
        for n, t in SIX.items():
            (d / a / f"{n}.md").write_text(t)
    (d / "onboarding.json").write_text(json.dumps({"state": "done", "reason": "", "empty": False, "apps": {"web": {}, "api": {}},
                                                    "confirmed": list(SIX), "seen": []}))
    s = root / ".nio/specs/two"
    s.mkdir(parents=True, exist_ok=True)
    (s / "spec.md").write_text(f"---\ntitle: two\n{apps_line}\n---\n# Two\n")


def pack_slug(root, text, reader, *slug):
    return subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "pack", text, "--reader", reader,
                           *(["--slug", slug[0]] if slug else [])], cwd=root, capture_output=True, text=True)


def test_plan_pack_two_apps():
    root = repo({})
    two_apps(root, "apps: [web, api]")
    r = pack_slug(root, "plan", "plan", "two")
    assert r.returncode == 0, (r.stdout, r.stderr)
    want = [f"{a}/{d}" for a in ("web", "api") for d in ROWS["plan"]]
    assert sorted(headings(r.stdout)) == sorted(want), headings(r.stdout)


def test_worker_pack_one_app():
    root = repo({})
    two_apps(root, "apps: [api]")
    r = pack_slug(root, "task", "worker", "two")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert not [l for l in r.stdout.splitlines() if "web/" in l], r.stdout
    assert "### api/stack.md" in r.stdout and "### api/principles.md" in r.stdout, r.stdout


def test_drafting_pack_all_apps():
    root = repo({})
    two_apps(root, "apps: []")
    r = pack_slug(root, "draft", "spec")
    assert r.returncode == 0, (r.stdout, r.stderr)
    want = [f"{a}/{d}.md" for a in ("web", "api") for d in ("product", "personas")]
    assert sorted(headings(r.stdout)) == sorted(want), headings(r.stdout)


def test_backup_failed_copy_leaves_no_partial():
    import datetime
    import shutil
    import os
    from nio import onboard
    root = repo({"CLAUDE.md": "rules v1 full"})
    real = shutil.copy2

    def broken(s, d, **k):
        Path(d).write_bytes(b"rul")
        raise OSError("disk full")
    shutil.copy2 = broken
    try:
        try:
            onboard.backup(str(root / "CLAUDE.md"), root)
            raise AssertionError("copy failure not raised")
        except OSError:
            pass
    finally:
        shutil.copy2 = real
    day = f".nio/backup/{datetime.date.today().isoformat()}"
    assert not (root / day / "CLAUDE.md").exists(), "truncated file at the backup path"
    assert nio(root, "backup", "CLAUDE.md").returncode == 0
    assert (root / day / "CLAUDE.md").read_bytes() == b"rules v1 full"
    root = repo({"CLAUDE.md": "x"})
    (root / ".nio/backup").mkdir(parents=True)
    (root / day).write_text("in the way")
    r = nio(root, "backup", "CLAUDE.md")
    assert r.returncode == 1 and "error:" in r.stdout + r.stderr and "Traceback" not in r.stderr, (r.returncode, r.stderr)
    root = repo({"AGENTS.md": "agents", ".env.md": "s"})
    os.symlink("AGENTS.md", root / "CLAUDE.md")
    r = nio(root, "backup", "CLAUDE.md")
    assert r.returncode == 0 and (root / day / "CLAUDE.md").read_bytes() == b"agents", (r.stdout, r.stderr)
    assert nio(root, "backup", ".env.md").returncode == 1


def test_labelled_unknown_is_not_a_fact():
    """A template's `Who: NEEDS CLARIFICATION` is an unknown, not a sourceless fact; a labelled fact still needs one."""
    from nio import onboard
    assert onboard.check_facts("### P-1 Owner\nWho: NEEDS CLARIFICATION\n") == ""
    assert "line 2" in onboard.check_facts("### P-1 Owner\nWho: shop owner\n")


def test_apps_line_keeps_template_comment():
    root = repo({})
    two_apps(root, "apps: [api]  # the apps this spec touches, when the project has docs per app")
    r = pack_slug(root, "task", "worker", "two")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "web/" not in r.stdout and "not onboarded" not in r.stdout and "### api/stack.md" in r.stdout, r.stdout
    two_apps(root, "apps: []  # the apps this spec touches, when the project has docs per app")
    r = pack_slug(root, "task", "worker", "two")
    assert "not onboarded" not in r.stdout and "### web/stack.md" in r.stdout and "### api/stack.md" in r.stdout, r.stdout
    two_apps(root, "apps: [ghost]")
    r = pack_slug(root, "task", "worker", "two")
    assert "not onboarded: ghost" in r.stdout and "### web/" not in r.stdout and "### api/" not in r.stdout, r.stdout


def test_check_spec_apps_only_onboarded():
    root = repo({})
    two_apps(root, "apps: []")
    (root / ".nio/project/other").mkdir()
    assert newspec(root, "full").returncode == 0
    f = next((root / ".nio/specs").glob("*/spec.md"))
    for val in ("[other]", "[..]"):
        body = "".join(ln for ln in f.read_text().splitlines(keepends=True) if not ln.startswith("apps:"))
        f.write_text(body.replace("---\n", f"---\napps: {val}\n", 1))
        r = subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "check", "spec", f.parent.name],
                           cwd=root, capture_output=True, text=True)
        assert f"app {val[1:-1]} has no project docs" in r.stdout + r.stderr, (val, r.stdout, r.stderr)


def test_skill_inline_secret_rule():
    """FR-30, AC-39: a secret value found inline in any file the agent reads is never written, quoted or shown."""
    text = " ".join((Path(__file__).resolve().parent.parent / "skills/onboard/SKILL.md").read_text().split())
    assert "secret value found inline in any file you read" in text, "inline-secret rule missing"
    assert "never write, quote or show the value" in text, "inline-secret rule missing"


def test_confirm_refuses_value_from_secrets_file():
    """J-3: a value copied from a file the scan lists as secrets is refused at confirm, without printing it."""
    pw = "hunter2" + "hunter2"
    root = repo({"README.md": "hi\n", ".env": f"DB_PASSWORD={pw}\nDEBUG=on\n"}, ignore=".env\n")
    d = root / ".nio/project"
    assert nio(root, "start", "--empty").returncode == 0
    tpl = Path(__file__).parent.parent / "src/nio/templates/project"
    base = (tpl / "product.md").read_text().replace("NEEDS CLARIFICATION", "x (source: dev, 2026-11-14)")
    (d / "product.md").write_text(base.replace("x (source: dev", f"db password {pw} (source: dev", 1))
    r = nio(root, "confirm", "product")
    out = r.stdout + r.stderr
    assert r.returncode == 1 and "line 5" in out and "secret" in out and pw not in out, (r.stdout, r.stderr)
    (d / "product.md").write_text(base.replace("x (source: dev", "debug is on (source: dev", 1))  # `on` is too short to count
    assert nio(root, "confirm", "product").returncode == 0


def test_grill_blank_fields_secret_rule():
    """FR-24, FR-30, CT-21: the grill's blank-tech-field step keeps secrets out and sources repo answers by file."""
    text = " ".join((Path(__file__).resolve().parent.parent / "skills/grill/SKILL.md").read_text().split())
    step = text[text.index("**Blank tech fields.**"):][:2000]
    assert "never open a file the scan lists under `secrets`" in step, "secrets-file rule missing"
    assert "never write, quote or show a secret value" in step, "secret-value rule missing"
    assert "(source: <path>@<hash>)" in step, "repo-answer source missing"


if __name__ == "__main__":
    selfcheck.main([test_scan_more_secret_patterns, test_backup_refuses_symlink_out_of_repo, test_scan_lists_each_category, test_scan_secrets_path_only, test_scan_more_secret_names, test_scan_skips_symlink, test_scan_prints_no_dependency, test_scan_skips_ignored_and_nio,
                    test_scan_empty_repo, test_scan_outside_git_repo, test_scan_keeps_non_ascii_paths, test_scan_contract_categories,
                    test_skip_needs_reason, test_project_templates_match_headings, test_empty_start_writes_blank_docs, test_empty_start_keeps_existing_docs, test_state_table_cells,
                    test_spec_waits_for_onboarding, test_lite_spec_starts, test_torn_progress_file, test_torn_progress_file_status,
                    test_skip_lets_spec_start, test_skip_stays_visible, test_confirm_checks_docs_and_finishes, test_confirm_refuses_missing_source_and_secret,
                    test_onboard_from_subdirectory_uses_repo_root, test_onboard_act_outside_git_repo, test_next_doc_first_unconfirmed,
                    test_missing_doc_named, test_skipped_pack, test_oversized_doc_flagged,
                    test_reader_packs, test_lens_sources_include_docs, test_doc_quote_grounds_for_its_lens,
                    test_corrupt_progress_does_not_block_docs, test_symlinked_doc_not_read, test_apps_line_front_matter_only, test_check_spec_apps,
                    test_backup_keeps_first_copy, test_backup_failed_copy_leaves_no_partial, test_six_docs_with_headings, test_fact_names_file_and_hash, test_skills_keep_skip_with_dev, test_apps_start_and_confirm, test_app_slug_not_a_doc_name,
                    test_plan_pack_two_apps, test_worker_pack_one_app, test_drafting_pack_all_apps, test_labelled_unknown_is_not_a_fact, test_apps_line_keeps_template_comment, test_check_spec_apps_only_onboarded, test_skill_inline_secret_rule, test_confirm_refuses_value_from_secrets_file, test_grill_blank_fields_secret_rule])

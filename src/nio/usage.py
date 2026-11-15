"""Run recording (#66): hooks around each agent and shell call append to .nio/runs/events.jsonl, and a finished effort
commits a short summary to .nio/specs/<slug>/usage.json. Records hold times, model, effort and tokens: never prompts,
code or the text of a command.

To add a host: write its `install` and `event` and add them to HOSTS. `event` turns one hook payload into one event;
the rest of this file only reads events, so it doesn't change. Hosts without hooks keep the times in history.jsonl."""
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from nio import agents, hooks, records

EVENTS = ".nio/runs/events.jsonl"
SUMMARY = "usage.json"
MARK = "usage event"
TOKENS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
RUN, SPEC, DATED = re.compile(r"R-\d{6}-\w+"), re.compile(r"\.nio/specs/([\w-]+)"), re.compile(r"\b\d{4}-\d\d-\d\d-[\w-]+")
TASK = re.compile(r"\bT-\d+\b")
NIO = re.compile(r"^\s*(?:uv run )?nio (\w+)(?: ([a-z]+))?")


def link(root, text):
    """{effort, task} a prompt or a command names: through the run in its pack path, else a spec folder or a slug."""
    out = {}
    if m := RUN.search(text):
        try:
            flow = json.loads((root / ".nio/runs" / m[0] / "flow.json").read_text())
            out = {k: flow[k] for k in ("effort", "task") if k in flow}
        except (OSError, ValueError):
            pass
    if "effort" not in out:
        for m in [*SPEC.finditer(text), *DATED.finditer(text)]:
            slug = m[1] if m.re is SPEC else m[0]
            if (root / ".nio/specs" / slug).is_dir():
                out["effort"] = slug
                break
    return out


def label(command):
    """A shell call's name: `nio flow finish` for NIO's own commands, plain `bash` for the rest, whose text may hold secrets."""
    m = NIO.match(command)
    return " ".join(["nio", *filter(None, m.groups())]) if m else "bash"


def claude_event(root, p):
    """One Claude Code hook payload as an event, or None for one this doesn't record."""
    name, tool, given = p.get("hook_event_name"), p.get("tool_name"), p.get("tool_input") or {}
    base = {"session": p.get("session_id"), "transcript": p.get("transcript_path")}
    if p.get("agent_id"):
        base["agent"] = p["agent_id"]
    if name == "PreToolUse" and tool == "Agent":
        text = f"{given.get('prompt', '')} {given.get('description', '')}"
        task = TASK.search(given.get("description", ""))
        return {**base, "kind": "agent_called", "call": p.get("tool_use_id"), "type": given.get("subagent_type"),
                "phase": given.get("description", "")[:80], **({"task": task[0]} if task else {}), **link(root, text)}
    if name == "PostToolUse" and tool == "Agent":
        return {**base, "kind": "agent_launched", "call": p.get("tool_use_id"), "agent": (p.get("tool_response") or {}).get("agentId")}
    if name == "SubagentStart":
        return {**base, "kind": "agent_start", "type": p.get("agent_type")}
    if name == "SubagentStop":
        return {**base, "kind": "agent_stop", "log": p.get("agent_transcript_path")}
    if name in ("PreToolUse", "PostToolUse") and tool == "Bash":
        command = given.get("command", "")
        return {**base, "kind": "bash_start" if name == "PreToolUse" else "bash_end", "call": p.get("tool_use_id"),
                "name": label(command), **link(root, command)}
    if name == "UserPromptSubmit":
        return {**base, "kind": "turn_start"}
    if name == "Stop":
        return {**base, "kind": "turn_end"}
    return None


def claude_install(root, shared, nio=None):
    """Merge the hooks into Claude Code's settings for this repo, replacing an older install's. Returns the file's path."""
    # a shared file can't hold this machine's path
    nio = "nio" if shared else nio or shutil.which("nio")
    if not nio:
        raise ValueError("`nio` is not on PATH; install it with `uv tool install` or run this through `uv run`")
    path, cfg = hooks.settings(root, shared)
    command = {"type": "command", "command": f"{nio} {MARK} claude 2>/dev/null || true", "timeout": 5}
    wanted = {"PreToolUse": "Agent|Bash", "PostToolUse": "Agent|Bash", "SubagentStart": "", "SubagentStop": "",
              "UserPromptSubmit": "", "Stop": ""}
    mine = cfg.setdefault("hooks", {})
    for name, matcher in wanted.items():
        kept = [g for g in mine.get(name, []) if not any(MARK in h.get("command", "") for h in g.get("hooks", []))]
        mine[name] = kept + [{"matcher": matcher, "hooks": [command]} if matcher else {"hooks": [command]}]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2) + "\n")
    return path


HOSTS = {"claude": {"install": claude_install, "event": claude_event}}


def record(host, stdin=None):
    """Append one hook payload to the events. Never raises: a recording problem must not stop the agent's work."""
    try:
        payload = json.load(stdin or sys.stdin)
        root = Path(payload.get("cwd") or ".")
        root = Path(records.git(root, "rev-parse", "--show-toplevel")[0])
        event = HOSTS[host]["event"](root, payload)
        if event and (root / ".nio").is_dir():
            path = root / EVENTS
            path.parent.mkdir(parents=True, exist_ok=True)
            event = {"at": datetime.now(timezone.utc).isoformat(), "host": host, **event}
            with path.open("a") as f:  # one short append per event, so parallel hooks don't interleave
                f.write(json.dumps(event) + "\n")
    except Exception:
        pass


def when(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def read(root):
    path = root / EVENTS
    out = []
    for line in path.read_text().splitlines() if path.exists() else []:
        try:
            out.append(json.loads(line))
        except ValueError:
            continue  # a torn last line
    return out


def own(events, slug):
    """The events of one effort. An event that names no effort belongs to the one its session last named."""
    # ponytail: a session hopping between efforts blurs at the switch; tag every event if that starts to matter
    last, out = {}, []
    for e in events:
        last[e.get("session")] = e.get("effort") or last.get(e.get("session"))
        if last[e.get("session")] == slug:
            out.append(e)
    return out


def tokens(log, start=None, end=None):
    """(token counts, model, effort) of a host transcript, between two times when given. Empty if it's gone."""
    total, seen, model, effort = {k: 0 for k in TOKENS} | {"thinking": 0}, set(), None, None
    for o in agents.replies(Path(log)) if log else []:
        usage, at = o.get("message", {}).get("usage"), when(o["timestamp"]) if o.get("timestamp") else None
        key = o.get("requestId") or o.get("uuid")
        if not usage or key in seen or start and at and not start <= at <= end:
            continue
        seen.add(key)  # one request can span several transcript lines
        for k in TOKENS:
            total[k] += usage.get(k, 0)
        total["thinking"] += (usage.get("output_tokens_details") or {}).get("thinking_tokens", 0)
        model, effort = o["message"].get("model") or model, o.get("effort") or effort
    return total, model, effort


def add(a, b):
    return {k: a.get(k, 0) + b.get(k, 0) for k in {*a, *b}}


def covered(spans):
    """Seconds covered by (start, end) spans that may overlap: parallel agents don't count twice."""
    total, reach = 0.0, None
    for start, end in sorted(spans):
        if reach is None or start > reach:
            total, reach = total + (end - start).total_seconds(), end
        elif end > reach:
            total, reach = total + (end - reach).total_seconds(), end
    return total


def pairs(events, opens, closes, key):
    """{key: (open event, close event)} of events that both happened."""
    began, out = {}, {}
    for e in events:
        if e["kind"] == opens:
            began[e.get(key)] = e
        elif e["kind"] == closes and e.get(key) in began:
            out[e[key]] = (began.pop(e[key]), e)
    return out


def report(root, slug):
    """The effort's summary, or None when nothing was recorded for it."""
    events = own(read(root), slug)
    if not events:
        return None
    start, end = when(events[0]["at"]), when(events[-1]["at"])
    called = pairs(events, "agent_called", "agent_launched", "call")
    calls = {done.get("agent"): first for first, done in called.values()}
    tasks, kinds, spans = {}, {}, []
    for agent, (begin, stop) in pairs(events, "agent_start", "agent_stop", "agent").items():
        span = (when(begin["at"]), when(stop["at"]))
        spans.append(span)
        seconds, call = (span[1] - span[0]).total_seconds(), calls.get(agent, {})
        used, model, effort = tokens(stop.get("log"))
        rollup = kinds.setdefault(f"{begin.get('type')} {model} {effort}", {"agents": 0, "seconds": 0.0, "tokens": {}})
        rollup.update(agents=rollup["agents"] + 1, seconds=rollup["seconds"] + seconds, tokens=add(rollup["tokens"], used))
        if call.get("task"):
            row = tasks.setdefault(call["task"], {"agents": 0, "seconds": 0.0, "tokens": {}})
            row.update(agents=row["agents"] + 1, seconds=row["seconds"] + seconds, tokens=add(row["tokens"], used))
    # shell time the orchestrator spent; a worker's own shell calls are inside its span already
    shell = [(when(a["at"]), when(b["at"])) for a, b in pairs(events, "bash_start", "bash_end", "call").values() if not a.get("agent")]
    waiting, gap = 0.0, {}
    for e in events:
        if e["kind"] == "turn_end" and not e.get("agent"):
            gap[e.get("session")] = when(e["at"])
        elif e["kind"] == "turn_start" and e.get("session") in gap:
            waiting += (when(e["at"]) - gap.pop(e["session"])).total_seconds()
    orchestrator = {}
    for log in {e["transcript"] for e in events if e.get("transcript")}:
        orchestrator = add(orchestrator, tokens(log, start, end)[0])
    for tid, n in attempts(root, slug).items():
        if tid in tasks:
            tasks[tid]["attempts"] = n
    wall, busy = (end - start).total_seconds(), covered(spans + shell)
    return {"effort": slug, "started": events[0]["at"], "ended": events[-1]["at"], "wall_seconds": wall,
            "waiting_for_human_seconds": waiting, "agents_seconds": covered(spans), "shell_seconds": covered(shell),
            "orchestrator_thinking_seconds": max(0.0, wall - waiting - busy), "orchestrator_tokens": orchestrator,
            "by_agent": kinds, "tasks": dict(sorted(tasks.items(), key=lambda x: int(x[0][2:])))}


def attempts(root, slug):
    """{task: 1 + its refusals and failed reviews}, from the effort's history."""
    out, path = {}, root / ".nio/specs" / slug / "history.jsonl"
    for line in path.read_text().splitlines() if path.exists() else []:
        try:
            x = json.loads(line)
        except ValueError:
            continue
        tid = (x.get("evidence") or {}).get("task")
        if tid:
            failed = x["kind"] == "refused" or x["kind"] == "review" and x["evidence"].get("passed") is False
            out[tid] = out.get(tid, 1) + failed
    return out


def write(root, slug):
    """Write the summary; returns its path, or None when nothing was recorded."""
    data = report(root, slug)
    if data is None:
        return None
    path = root / ".nio/specs" / slug / SUMMARY
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path


def finish(root, slug):
    """Commit the summary of a finished effort. Lines to print; a failure here never undoes the finish."""
    try:
        path = write(root, slug)
        if path is None:
            return []
        rel = str(path.relative_to(root))
        for args in (["add", "--", rel], ["commit", "-q", "-m", f"Record the usage of {slug}", "--", rel]):
            code, _, err = records.git(root, *args, full=True)
            if code:
                return [f"usage: {rel} written but not committed: {err.strip().splitlines()[0] if err.strip() else 'git failed'}"]
        return [f"usage: committed {rel}"]
    except (OSError, ValueError) as e:
        return [f"usage: not recorded: {e}"]

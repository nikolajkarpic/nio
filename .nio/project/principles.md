# Principles

## Principles

- Every change must serve `NORTH_STAR.md`; ideas that don't go to a GitHub issue labelled `type:*` and `area:*`. (source: CLAUDE.md@b0e3cba2321c)
- Agent-agnostic: skills are plain `SKILL.md` markdown that Claude Code, Antigravity, Cursor, Codex and Grok can use unchanged. (source: NORTH_STAR.md@70371da8a313)
- Files and git are the state: no database and no daemon; everything a run decides is readable and diffable. (source: NORTH_STAR.md@70371da8a313)
- Human in the loop by default: autonomy is earned through the jury, never assumed. (source: NORTH_STAR.md@70371da8a313)
- Minimal: a skill exists only if it's used. (source: NORTH_STAR.md@70371da8a313)
- DB scripts, secrets, breaking changes, anything irreversible and anything that can cost money always go to the human, never decided by the jury. (source: NORTH_STAR.md@70371da8a313)
- Never fix silently: when implementation shows the spec or plan is wrong, work stops and a change request goes to the human. (source: NORTH_STAR.md@70371da8a313)
- Each skill does one job, states its inputs and outputs (files under `.nio/`), and says when to stop. (source: CLAUDE.md@b0e3cba2321c)
- Prefer instructions over scripts; add a script only when instructions can't be followed reliably. (source: CLAUDE.md@b0e3cba2321c)
- Every message to the human follows "Talking to the human" in `NORTH_STAR.md`, and every skill carries that block word for word, checked by `tests/test_talk.py`. (source: CLAUDE.md@b0e3cba2321c)
- Small commits with imperative messages; stage approvals use `nio: approve <stage>`. (source: CLAUDE.md@b0e3cba2321c)
- Never commit without the human asking. (source: CLAUDE.md@b0e3cba2321c)

import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { NioRow } from '../types'

const PANE = { id: 'nio-efforts', title: 'NIO efforts' }
const EVERY_MS = 30_000 // NFR-3: one pass over six worktrees costs ~8 CPU-seconds (RF-9)
const board = atom({ plugin: 'nio-status-pane', key: 'board' } as const, null)
const drill = atom({ plugin: 'nio-status-pane', key: 'drill' } as const, null)
// FR-10: the worktree's own venv, never uv (which creates `.venv` where none is), and no bytecode,
// so reading the status writes nothing in the worktree.
const NIO = '.venv/bin/nio'
const NO_NIO = 'nio not found'
const ENV = { PYTHONDONTWRITEBYTECODE: '1' }
const STAMP = /^(\d{4}-\d\d-\d\d \d\d:\d\d|-)$/

type $ = EngineInterface
type Tree = { path: string; branch: string }
type Effort = { slug: string; stage: string; status: string; at: string; gone: boolean }
type Line = Effort | { slug: string; error: string }
type Ran = { out: string } | { error: string }
type Drill = { slug: string; path: string; shown: any; context: number | null; tab?: Tab; toggled?: string[] }

const message = (err: unknown) => (err instanceof Error ? err.message : String(err))
const lastLine = (text: string) => text.trim().split('\n').pop() ?? ''
const base = (path: string) => path.replace(/\/+$/, '').split('/').pop() ?? path

// FR-1: `git worktree list --porcelain`, bare entries left out.
export const worktrees = (porcelain: string): Tree[] =>
  porcelain.split(/\n\s*\n/).flatMap(block => {
    const path = /^worktree (.+)$/m.exec(block)?.[1]
    if (!path || /^bare$/m.test(block)) return []
    return [{ path, branch: /^branch refs\/heads\/(.+)$/m.exec(block)?.[1] ?? 'detached' }]
  })

// RF-2: `slug · stage · auto|manual · status · last activity[ · override …]`. Non-effort rows (legacy,
// unsupported) are dropped; done and abandoned ones are marked `gone` (FR-5 drops them after the dedupe in
// collect); a broken effort is kept as an error (FR-6).
export const parseStatus = (stdout: string): Line[] =>
  stdout.split('\n').filter(l => l.trim()).flatMap<Line>(line => {
    const p = line.split(' · ')
    const slug = p[0]!
    if (p[1]?.startsWith('broken:')) return [{ slug, error: p.slice(1).join(' · ') }]
    if (p[2] !== 'auto' && p[2] !== 'manual') return []
    const end = p.findIndex((x, i) => i > 3 && STAMP.test(x))
    const status = p.slice(3, end < 0 ? p.length : end).join(' · ')
    const gone = p[1] === 'done' || status.startsWith('abandoned')
    return [{ slug, stage: p[1]!, status, at: end < 0 ? '-' : p[end]!, gone }]
  })

const listTrees = async ($: $) => {
  const r = await $.process.run(['git', 'worktree', 'list', '--porcelain'])
  if (r.exitCode !== 0) throw new Error(lastLine(r.stderr) || `git exit ${r.exitCode}`)
  return worktrees(r.stdout)
}

// CT-13: the worktree's venv nio when it exists, else `nio` from PATH. Never uv.
export const nioFor = async ($: $, cwd: string): Promise<string> =>
  (await $.fs.exists(`${cwd}/${NIO}`)) ? `${cwd}/${NIO}` : 'nio'

const flowStatus = async ($: $, cwd: string): Promise<Ran> => {
  try {
    const nio = await nioFor($, cwd)
    let r
    try {
      r = await $.process.run([nio, 'flow', 'status'], { cwd, env: ENV, timeoutMs: 20_000 })
    } catch {
      return { error: NO_NIO }
    }
    if (r.exitCode === 0) return { out: r.stdout }
    return { error: lastLine(r.stderr) || lastLine(r.stdout) || `exit ${r.exitCode}` }
  } catch (err) {
    return { error: message(err) }
  }
}

const json = async ($: $, path: string): Promise<any> => JSON.parse(await $.fs.read(path))

type Step = { dir: string; gate: string; round: number; lenses: string[] }

// RF-5: every jury run's step.json in the worktree (it names no slug, so gate and round pick the round).
const stepsOf = async ($: $, wt: string): Promise<Step[]> => {
  const runs = await $.fs.list(`${wt}/.nio/runs`).catch(() => [])
  const all = await Promise.all(
    runs.filter(r => r.kind === 'dir').map(r => {
      const dir = `${wt}/.nio/runs/${r.name}/jury`
      return json($, `${dir}/packs/step.json`).then(
        s => ({ dir, gate: s.gate, round: s.round, lenses: Array.isArray(s.lenses) ? s.lenses : [] }),
        () => null,
      )
    }),
  )
  return all.filter((s): s is Step => s !== null)
}

// The jury gate of each stage that has one (src/nio/flow.py GATES, EPIC_GATE); any other stage has no jury fields.
const GATE: Record<string, RegExp> = {
  spec_jury: /^spec$/,
  plan_jury: /^plan$/,
  tasks_jury: /^tasks$/,
  implementing: /^implementation-E-\d+$/,
}

// FR-13, FR-7: the claimed task from state.json. The open round: a step.json for the gate of the effort's current
// stage whose ledger still has the round the packs were written at (0 with no ledger yet; collecting the outputs
// bumps it) and that has lenses with a pack and no output, the running jurors. It judges round + 1 (RF-4).
const fields = async ($: $, wt: string, slug: string, stage: string, steps: () => Promise<Step[]>) => {
  const dir = `${wt}/.nio/specs/${slug}`
  const task = await json($, `${dir}/state.json`).then(s => String(s?.claims?.task || '-'), () => '-')
  const gate = GATE[stage]
  if (!gate) return { task, round: '-', jurors: '-' }
  const ledgers = new Map<string, Promise<number>>()
  const roundOf = (gate: string) =>
    ledgers.get(gate) ??
    (ledgers.set(gate, json($, `${dir}/jury/${gate}.json`).then(l => Number(l?.round ?? 0), () => 0)), ledgers.get(gate)!)
  let round = 0
  const running = new Set<string>()
  for (const s of await steps()) {
    if (!gate.test(s.gate) || s.round !== (await roundOf(s.gate))) continue
    for (const lens of s.lenses) {
      if ((await $.fs.exists(`${s.dir}/packs/${lens}.md`)) && !(await $.fs.exists(`${s.dir}/${s.gate}-${lens}.md`))) {
        running.add(lens)
        round = Math.max(round, s.round + 1)
      }
    }
  }
  return { task, round: round ? String(round) : '-', jurors: [...running].join(', ') || '-' }
}

// One pass over every worktree, in parallel. An effort folder copied into several worktrees is one row:
// the copy with the newest activity, which is where the effort runs (on a tie, a done or abandoned copy);
// only then are done and abandoned efforts dropped, so a stale copy of a finished effort is not listed.
export const collect = async ($: $): Promise<NioRow[]> => {
  let trees: Tree[]
  try {
    trees = await listTrees($)
  } catch (err) {
    return [{ worktree: '.', slug: '', error: `git worktree list: ${message(err)}` }]
  }
  const ran = await Promise.all(trees.map(t => flowStatus($, t.path)))
  const errors: NioRow[] = []
  const broken = new Set<string>() // a broken effort copied into several worktrees: one error row
  const best = new Map<string, { wt: string; line: Effort }>()
  trees.forEach((t, i) => {
    const r = ran[i]!
    if ('error' in r) return void errors.push({ worktree: base(t.path), slug: '', error: r.error })
    for (const line of parseStatus(r.out)) {
      if ('error' in line) {
        if (!broken.has(line.slug)) errors.push({ worktree: base(t.path), slug: line.slug, error: line.error, path: t.path })
        broken.add(line.slug)
        continue
      }
      const cur = best.get(line.slug)?.line
      if (!cur || line.at > cur.at || (line.at === cur.at && line.gone && !cur.gone)) best.set(line.slug, { wt: t.path, line })
    }
  })
  const steps = new Map<string, Promise<Step[]>>()
  const stepsFor = (wt: string) => () => steps.get(wt) ?? (steps.set(wt, stepsOf($, wt)), steps.get(wt)!)
  const efforts = [...best.values()].filter(e => !e.line.gone).sort((a, b) => (a.line.at < b.line.at ? 1 : -1))
  const rows = await Promise.all(
    efforts.map(async ({ wt, line }) => ({
      worktree: base(wt),
      path: wt,
      slug: line.slug,
      stage: line.stage,
      status: line.status,
      ...(await fields($, wt, line.slug, line.stage, stepsFor(wt))),
    })),
  )
  return [...rows, ...errors]
}

// FR-8: the count and the stages of the active efforts.
export const summary = (rows: NioRow[]) => {
  const stages = new Map<string, number>()
  for (const r of rows) if (!('error' in r)) stages.set(r.stage, (stages.get(r.stage) ?? 0) + 1)
  const active = [...stages.values()].reduce((a, n) => a + n, 0)
  const head = active
    ? `nio: ${active} active (${[...stages].map(([s, n]) => (n > 1 ? `${s} x${n}` : s)).join(', ')})`
    : 'nio: no active effort'
  const failed = rows.length - active
  return failed ? `${head} · ${failed} error${failed > 1 ? 's' : ''}` : head
}

// FR-9: `nio flow status` per worktree, run in parallel, one block each.
export const report = async ($: $) => {
  let trees: Tree[]
  try {
    trees = await listTrees($)
  } catch (err) {
    return `git worktree list: ${message(err)}`
  }
  const ran = await Promise.all(trees.map(t => flowStatus($, t.path)))
  return trees
    .map((t, i) => {
      const r = ran[i]!
      const body = 'error' in r ? `error: ${r.error}` : r.out.trimEnd() || '(no efforts)'
      return `${t.path} [${t.branch}]\n${body}`
    })
    .join('\n\n')
}

// CT-12: `flow show <slug> --json` in the row's worktree; every failure becomes `{ error }`.
const show = async ($: $, slug: string, path: string): Promise<any> => {
  let r
  try {
    r = await $.process.run([await nioFor($, path), 'flow', 'show', slug, '--json'], { cwd: path, env: ENV, timeoutMs: 60_000 })
  } catch {
    return { error: NO_NIO }
  }
  if (r.exitCode === 0) {
    try {
      return JSON.parse(r.stdout)
    } catch {
      return { error: lastLine(r.stdout) || 'no output' }
    }
  }
  if (r.exitCode === 2 && r.stderr.includes('invalid choice')) return { error: 'this nio has no flow show: update nio' }
  if (r.exitCode === 1) {
    try {
      const e = JSON.parse(r.stdout)?.error
      if (e) return { error: String(e) }
    } catch {}
  }
  return { error: lastLine(r.stderr) || lastLine(r.stdout) || `exit ${r.exitCode}` }
}

const TABS = ['overview', 'history', 'juries', 'tasks', 'cost', 'memory'] as const
type Tab = (typeof TABS)[number]
const NONE = { history: 'no timeline yet', juries: 'no juries yet', tasks: 'no tasks yet', memory: 'no memory yet' } as const

// Display helpers: 382109278 → 382.1M, 23823 → 6h37m, an ISO stamp → local `11-15 14:20`.
export const num = (n: any) =>
  typeof n !== 'number' ? '-' : n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : n >= 1e3 ? `${(n / 1e3).toFixed(1)}k` : String(n)
export const dur = (s: any) =>
  typeof s !== 'number' ? '-' : s < 60 ? `${s}s` : s < 3600 ? `${Math.round(s / 60)}m` : `${Math.floor(s / 3600)}h${String(Math.round((s % 3600) / 60)).padStart(2, '0')}m`
const pad = (n: number) => String(n).padStart(2, '0')
export const when = (at: any) => {
  const d = new Date(at)
  return isNaN(d.getTime()) ? String(at ?? '-') : `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
const tone = (word: any): 'success' | 'error' | 'warning' | undefined => {
  const w = String(word)
  if (/^(done|approved|pass|accepted|current)$/.test(w)) return 'success'
  if (/^(block|blocker|fail|failed|rejected|broken)/.test(w)) return 'error'
  if (/^(major|claimed|working|human|waiting|open|proposed)/.test(w)) return 'warning'
  return undefined
}
const GLYPH: Record<string, string> = { success: '✓', error: '✗', warning: '●' }
const arr = (v: any): any[] => (Array.isArray(v) ? v : [])
const failed = (v: any) => (v && !Array.isArray(v) && v.error ? String(v.error) : null)

// The effort's drill-down, one tab at a time, from the one `flow show` JSON (FR-21).
const drillView = (ui: any, d: Drill, row: NioRow | undefined, set: (fn: (d: Drill) => Drill) => void) => {
  const { Box, Text, Button, Progress } = ui
  const s = d.shown
  const tab: Tab = d.tab ?? 'overview'
  const err = (v: any) => <Text color="error">error: {failed(v)}</Text>
  const none = (t: string) => <Text dimColor>{t}</Text>
  const open = (g: any) => (tone(g.outcome) !== 'success') !== (d.toggled ?? []).includes(g.gate)

  const event = (x: any) =>
    x.kind === 'review' ? (
      <Box flexDirection="column">
        <Text>
          <Text dimColor>{when(x.at)} </Text>
          <Text color="error">✗ review {x.from}</Text>
        </Text>
        <Text dimColor>{`   ${arr(x.reasons).length ? arr(x.reasons).join('; ') : '-'}`}</Text>
      </Box>
    ) : (
      <Text>
        <Text dimColor>{when(x.at)} </Text>
        {x.from} → <Text bold>{x.to}</Text>
        <Text dimColor>{` · ${x.role}${x.model && x.model !== '-' ? ` · ${x.model}` : ''}`}</Text>
      </Text>
    )
  const findingsOf = (g: any) => arr(g.rounds).reduce((n, r) => n + arr(r.findings).length, 0)
  const juryLine = (g: any, arrow = '') => (
    <Text>
      {arrow}
      <Text color={tone(g.outcome)}>{GLYPH[tone(g.outcome) ?? ''] ?? '·'} </Text>
      <Text bold>{g.gate}</Text> <Text color={tone(g.outcome)}>{g.outcome}</Text>
      <Text dimColor>{` · ${arr(g.rounds).length} rounds · ${findingsOf(g)} findings`}</Text>
    </Text>
  )
  const finding = (f: any) => (
    <Box flexDirection="column" marginLeft={4}>
      <Text>
        <Text color={tone(f.severity)}>{f.severity}</Text> {f.id}: {f.title}
      </Text>
      <Text dimColor>{`  ${f.validation}${arr(f.fix_tasks).length ? ` → ${f.fix_tasks.join(', ')}` : ''}`}</Text>
    </Box>
  )
  const jury = (g: any) => (
    <Box flexDirection="column">
      <Button key={`jury:${g.gate}`} onPress={() => set(c => ({ ...c, toggled: (c.toggled ?? []).includes(g.gate) ? c.toggled!.filter(x => x !== g.gate) : [...(c.toggled ?? []), g.gate] }))}>
        {juryLine(g, open(g) ? '▾ ' : '▸ ')}
      </Button>
      {open(g) &&
        [...arr(g.rounds)].reverse().map(r => (
          <Box flexDirection="column" marginLeft={2}>
            <Text>
              <Text bold>round {r.round}</Text>
              {arr(r.lenses).map(l => (
                <Text>
                  {'  '}
                  {l.lens} <Text color={tone(l.verdict)}>{l.verdict}</Text>
                </Text>
              ))}
            </Text>
            {arr(r.findings).map(finding)}
          </Box>
        ))}
    </Box>
  )
  const counts = (tasks: any[]) => [tasks.filter(t => t.status === 'done').length, tasks.length] as const
  const epic = (x: any) => {
    const [done, all] = counts(arr(x.tasks))
    return (
      <Box flexDirection="column">
        <Text>
          <Text bold>{String(x.epic)}</Text>
          <Text dimColor>{`  ${done}/${all} done`}</Text>
        </Text>
        {arr(x.tasks).map(t => (
          <Text>
            {'  '}
            <Text color={tone(t.status)}>{GLYPH[tone(t.status) ?? ''] ?? '○'}</Text> {t.id} {t.title}
            <Text dimColor>{` · ${t.status}${t.attempts && t.attempts !== '-' ? ` · attempts ${t.attempts}` : ''}`}</Text>
          </Text>
        ))}
      </Box>
    )
  }
  const costLine = (name: string, x: any, indent = '') => (
    <Text>
      {indent}
      {name}
      <Text dimColor>{`  ${num(x?.tokens)} tokens · ${dur(x?.seconds)}`}</Text>
    </Text>
  )
  const allTasks = arr(s?.tasks).flatMap(x => arr(x.tasks))
  const [done, total] = counts(allTasks)

  const body = (): any[] => {
    if (tab === 'history') return failed(s.timeline) ? [err(s.timeline)] : arr(s.timeline).length ? arr(s.timeline).map(event) : [none(NONE.history)]
    if (tab === 'juries') return failed(s.juries) ? [err(s.juries)] : arr(s.juries).length ? arr(s.juries).map(jury) : [none(NONE.juries)]
    if (tab === 'tasks') return failed(s.tasks) ? [err(s.tasks)] : arr(s.tasks).length ? arr(s.tasks).map(epic) : [none(NONE.tasks)]
    if (tab === 'memory')
      return failed(s.memory)
        ? [err(s.memory)]
        : arr(s.memory).length
          ? arr(s.memory).map(r => (
              <Box flexDirection="column">
                <Text>{r.title}</Text>
                <Text dimColor>
                  {`  ${r.id} · ${r.kind} · `}
                  <Text color={tone(r.standing)}>{r.standing}</Text>
                </Text>
              </Box>
            ))
          : [none(NONE.memory)]
    if (tab === 'cost')
      return failed(s.cost)
        ? [err(s.cost)]
        : [
            ...arr(s.cost?.stages).flatMap(st => [costLine(st.stage, st), ...arr(st.juries).map(j => costLine(`jury ${j.gate ?? j.name}`, j, '  '))]),
            costLine('unattributed', s.cost?.unattributed),
            <Text bold>
              total<Text dimColor>{`  ${num(s.cost?.total?.tokens)} tokens · ${dur(s.cost?.total?.seconds)}`}</Text>
            </Text>,
          ]
    // overview: progress, each gate's outcome, the latest moves, the total cost
    const recent = arr(s.timeline).slice(-3)
    return [
      <Text bold>Tasks</Text>,
      failed(s.tasks) ? err(s.tasks) : total ? <Progress label="tasks done" value={done} max={total} valueText={`${done}/${total} done`} color="success" /> : none(NONE.tasks),
      <Text bold>Juries</Text>,
      ...(failed(s.juries) ? [err(s.juries)] : arr(s.juries).length ? arr(s.juries).map(g => juryLine(g)) : [none(NONE.juries)]),
      <Text bold>Latest</Text>,
      ...(failed(s.timeline) ? [err(s.timeline)] : recent.length ? recent.map(event) : [none(NONE.history)]),
      <Text bold>Cost</Text>,
      failed(s.cost) ? err(s.cost) : <Text>{`${num(s.cost?.total?.tokens)} tokens · ${dur(s.cost?.total?.seconds)}`}</Text>,
    ]
  }

  return (
    <Box flexDirection="column">
      <Box flexDirection="row" gap={1}>
        <Button key="back" hotkey="b" onPress={() => set(() => null as any)}>
          ← Back
        </Button>
      </Box>
      <Box flexDirection="column" marginTop={1}>
        <Text bold>{d.slug}</Text>
        <Text dimColor>
          {row && !('error' in row) ? `${row.stage} · ${row.status} · ${row.worktree}` : base(d.path)}
          {typeof d.context === 'number' ? ` · context: ${d.context}%` : ''}
        </Text>
      </Box>
      {!s ? (
        <Text dimColor>Reading...</Text>
      ) : s.error ? (
        <Text color="error">{s.error}</Text>
      ) : (
        <Box flexDirection="column">
          <Box flexDirection="row" flexWrap="wrap" columnGap={1} marginY={1}>
            {TABS.map((t, i) => (
              <Button key={`tab:${t}`} hotkey={String(i + 1)} variant={t === tab ? 'primary' : undefined} dimColor={t !== tab} onPress={() => set(c => ({ ...c, tab: t }))}>
                {t}
              </Button>
            ))}
          </Box>
          <Box flexDirection="column" gap={tab === 'overview' ? 0 : 1}>
            {body()}
          </Box>
        </Box>
      )}
    </Box>
  )
}

let busy = false // module state: a reload starts a fresh environment, timers included

// FR-4: one pass, then the pane's state and the status line; no model turn.
const refresh = async ($: $) => {
  if (busy) return // a pass still running: skip this tick
  busy = true
  try {
    const rows = await collect($)
    const at = new Date(await $.clock.now()).toTimeString().slice(0, 8)
    await update($, board, () => ({ at, rows }))
    $.ui.status(summary(rows))
  } finally {
    busy = false
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'nio',
      description: 'Print nio flow status for every worktree (no model turn)',
      immediate: true,
    })
    $.ui.open(PANE).catch(() => undefined) // a narrow terminal: `/nio` places it
    const tick = () => void refresh($).catch(err => $.ui.status(`nio: ${message(err)}`))
    tick()
    $.clock.every(EVERY_MS, tick)
    return next(e)
  })

  on('command.run', { command: 'nio' }, async $ => {
    await $.ui.open(PANE).catch(() => undefined) // asked for: placed even on a narrow terminal
    return { text: await report($) }
  })

  on('ui.render', { component: 'Pane', requestId: 'nio-efforts' }, async ($, e) => {
    const { Box, Text, Button } = $.ui.resolve(e)
    const b = await read($, board)
    if (!b) return <Text dimColor>Reading nio flow status...</Text>
    const d = (await read($, drill)) as Drill | null
    if (d) {
      const row = b.rows.find(r => r.slug === d.slug)
      return drillView($.ui.resolve(e), d, row, fn => void update($, drill, cur => (cur ? fn(cur as Drill) : cur)))
    }
    const open = (slug: string, path: string) => async () => {
      await update($, drill, () => ({ slug, path, shown: null, context: null, tab: 'overview', toggled: [] }))
      const shown = await show($, slug, path)
      const context = await $.session.usage().then(u => (typeof u?.context?.percent === 'number' ? u.context.percent : null), () => null)
      await update($, drill, cur => (cur && cur.slug === slug ? { ...cur, shown, context } : cur))
    }
    const brokenSlugs = new Set(b.rows.flatMap(r => ('error' in r && r.slug && r.path ? [r.slug] : [])))
    return (
      <Box flexDirection="column">
        <Text dimColor>
          {summary(b.rows)} · updated {b.at}
        </Text>
        {b.rows.map((r, i) =>
          'error' in r ? (
            r.slug && r.path ? (
              <Button key={r.slug} onPress={open(r.slug, r.path)}>
                <Text color="error">{`${r.worktree} ${r.slug}: ${r.error}`}</Text>
              </Button>
            ) : (
              <Text color="error">
                {r.worktree}
                {r.slug ? ` ${r.slug}` : ''}: {r.error}
              </Text>
            )
          ) : (
            <Box flexDirection="column" marginTop={1} paddingLeft={1} borderStyle="single" borderColor="subtle">
              {brokenSlugs.has(r.slug) ? (
                <Text bold>{r.slug}</Text>
              ) : (
                <Button key={r.slug} hotkey={i < 9 ? String(i + 1) : undefined} onPress={open(r.slug, r.path!)}>
                  <Text bold>{r.slug}</Text>
                </Button>
              )}
              <Text color={tone(r.status)}>
                {r.stage} · {r.status}
              </Text>
              <Text dimColor>
                {r.worktree} · jury {r.round} · task {r.task} · jurors {r.jurors}
              </Text>
            </Box>
          ),
        )}
      </Box>
    )
  })
}

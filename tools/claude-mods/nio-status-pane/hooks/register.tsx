import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { NioRow } from '../types'

const PANE = { id: 'nio-efforts', title: 'NIO efforts' }
const EVERY_MS = 30_000 // NFR-3: one pass over six worktrees costs ~8 CPU-seconds (RF-9)
const board = atom({ plugin: 'nio-status-pane', key: 'board' } as const, null)
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
        if (!broken.has(line.slug)) errors.push({ worktree: base(t.path), slug: line.slug, error: line.error })
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
    const { Box, Text } = $.ui.resolve(e)
    const b = await read($, board)
    if (!b) return <Text dimColor>Reading nio flow status...</Text>
    return (
      <Box flexDirection="column">
        <Text dimColor>
          {summary(b.rows)} · updated {b.at}
        </Text>
        {b.rows.map(r =>
          'error' in r ? (
            <Text color="error">
              {r.worktree}
              {r.slug ? ` ${r.slug}` : ''}: {r.error}
            </Text>
          ) : (
            <Box flexDirection="column" marginTop={1}>
              <Text bold>{r.slug}</Text>
              <Text>
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

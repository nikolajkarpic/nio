import { expect, mock, test } from 'claude-code/testing'

const PANE = {
  plugin: 'nio-status-pane',
  component: 'Pane',
  requestId: 'nio-efforts',
  props: {
    title: 'NIO efforts',
    isFocused: false,
    bodyColumns: 100,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 40 },
    view: {},
  },
} as const

const PORCELAIN = [
  'worktree /w/nio\nHEAD 1\nbranch refs/heads/main',
  'worktree /w/nio-123\nHEAD 2\nbranch refs/heads/nio/e123',
  'worktree /w/nio-bad\nHEAD 3\nbranch refs/heads/nio/bad',
  'worktree /w/bare.git\nbare',
].join('\n\n') + '\n'

// `nio flow status` per worktree, in its own words (RF-2); a missing key fails the run.
const STATUS: Record<string, string> = {
  '/w/nio': [
    '2026-11-08-e123 · spec_jury · manual · working · 2026-11-08 10:00', // a stale copy: e123 runs in nio-123
    '2026-11-08-e49 · implementing · manual · waiting_for_human: approve the plan · 2026-11-14 09:00',
    '2026-11-07-old · done · manual · done · 2026-11-07 16:28 · override not seen: implementing: x',
    '2026-11-06-gone · tasking · manual · abandoned: not needed · 2026-11-06 10:00',
    '2026-11-05-wreck · broken: state.json, line 3',
    'plain-talk · legacy · 2026-10-26 11:50',
  ].join('\n') + '\n',
  // wreck is copied here too, as broken: one error row for it.
  '/w/nio-123': '2026-11-08-e123 · implementing · auto · working · 2026-11-14 12:00\n2026-11-05-wreck · broken: state.json, line 3\n',
}

// The worktree's files, for $.fs: e123 claims T-18. Its implementation-E-1 ledger recorded round 1 (rejected:
// `nio jury next` always writes an outcome), and R-1's packs were written at that round, so round 2 is open,
// with correctness still running (conformance has written its output; R-0, round 0's packs, is done).
// Each worktree but nio-bare has a venv.
const FILES: Record<string, string> = {
  '/w/nio/.venv/bin/nio': '',
  '/w/nio-123/.venv/bin/nio': '',
  '/w/nio-bad/.venv/bin/nio': '',
  '/w/nio-123/.nio/specs/2026-11-08-e123/state.json': JSON.stringify({ claims: { task: 'T-18' } }),
  '/w/nio-123/.nio/specs/2026-11-08-e123/jury/spec.json': JSON.stringify({ round: 3, outcome: 'approved' }),
  '/w/nio-123/.nio/specs/2026-11-08-e123/jury/spec.md': '',
  '/w/nio-123/.nio/specs/2026-11-08-e123/jury/implementation-E-1.json': JSON.stringify({ round: 1, outcome: 'rejected' }),
  '/w/nio-123/.nio/runs/R-1/jury/packs/step.json': JSON.stringify({ gate: 'implementation-E-1', round: 1, lenses: ['correctness', 'conformance', 'security'] }),
  '/w/nio-123/.nio/runs/R-1/jury/packs/correctness.md': '',
  '/w/nio-123/.nio/runs/R-1/jury/packs/conformance.md': '',
  '/w/nio-123/.nio/runs/R-1/jury/implementation-E-1-conformance.md': '',
  '/w/nio-123/.nio/runs/R-0/jury/packs/step.json': JSON.stringify({ gate: 'implementation-E-1', round: 0, lenses: ['logic'] }),
  '/w/nio-123/.nio/runs/R-0/jury/packs/logic.md': '',
  '/w/nio-123/.nio/runs/events.jsonl': '',
  '/w/nio/.nio/specs/2026-11-08-e49/state.json': JSON.stringify({ claims: {} }),
}

const list = (FILES: Record<string, string>, path: string) => {
  const pre = path.replace(/\/$/, '') + '/'
  const names = new Map<string, 'file' | 'dir'>()
  for (const key of Object.keys(FILES)) {
    if (!key.startsWith(pre)) continue
    const [name, ...rest] = key.slice(pre.length).split('/')
    names.set(name!, rest.length ? 'dir' : 'file')
  }
  if (!names.size) throw new Error(`ENOENT: ${path}`)
  return [...names].map(([name, kind]) => ({ name, kind, size: 0, mtimeMs: 0, isLink: false }))
}

// Stands for the engine: git, `<worktree>/.venv/bin/nio flow status` and the files; records every call that could write.
const setup = (on: any, status: Record<string, string> = STATUS, files = FILES, porcelain = PORCELAIN, show?: (cwd: string | undefined) => ReturnType<typeof result>) => {
  const FILES = files
  const seen = { argv: [] as string[], writes: [] as string[], statuses: [] as (string | undefined)[] }
  on('process.run', (_: unknown, e: { argv: string[]; init?: { cwd?: string } }) => {
    seen.argv.push(e.argv.join(' '))
    if (e.argv[0] === 'git') return { value: result(0, porcelain) }
    if (e.argv[0] === 'nio' && status.NO_NIO) throw new Error('ENOENT: nio') // no nio on PATH
    if (e.argv.includes('show') && show) return { value: show(e.init?.cwd) }
    const out = status[e.init?.cwd ?? '']
    return { value: out === undefined ? result(1, '', 'Traceback\nValueError: boom') : result(0, out) }
  })
  on('fs.read', (_: unknown, e: { path: string }) => {
    if (!(e.path in FILES)) throw new Error(`ENOENT: ${e.path}`)
    return { value: FILES[e.path] }
  })
  on('fs.list', (_: unknown, e: { path: string }) => ({ value: list(FILES, e.path) }))
  on('fs.exists', (_: unknown, e: { path: string }) => ({ value: e.path in FILES }))
  on('fs.write', (_: unknown, e: { path: string }) => {
    seen.writes.push(e.path)
    return { value: undefined }
  })
  on('ui.status', (_: unknown, e: { text?: string }) => {
    seen.statuses.push(e.text)
    return { value: undefined }
  })
  on('command.register', () => ({ value: { command: 'nio' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  return seen
}

const result = (exitCode: number, stdout: string, stderr = '') => ({
  exitCode,
  stdout,
  stderr,
  isStdoutTruncated: false,
  isStderrTruncated: false,
})

const start = async ($: any, on: any) => {
  const clock = mock.clock(on, { now: Date.UTC(2026, 10, 14, 12, 0, 0) })
  await $.session.start({ cwd: '/w/nio', surface: 'terminal', isInteractive: true })
  await clock.settle()
  return clock
}

const texts = async ($: any, surface: 'terminal' | 'desktop') => {
  const ui = await $.ui.mount({ ...PANE, surface })
  const all: string[] = []
  for (const t of (await ui.findAll({ type: 'Text' })) ?? []) all.push(t.text)
  await ui.unmount()
  return all
}

test('AC-1, AC-3, AC-4, AC-5, AC-14: one row per active effort, with its fields, on every surface', async ($, on) => {
  setup(on)
  await start($, on)
  for (const surface of ['terminal', 'desktop'] as const) {
    const lines = await texts($, surface)
    const all = lines.join('\n')
    // AC-1, AC-14: e123 from the worktree where it runs, its claim, open round and the one juror still running.
    expect(all).toContain('2026-11-08-e123\nimplementing · working\nnio-123 · jury 2 · task T-18 · jurors correctness\n')
    // AC-5: e49 records no claim and no open jury.
    expect(all).toContain('2026-11-08-e49\nimplementing · waiting_for_human: approve the plan\nnio · jury - · task - · jurors -\n')
    // AC-3: done, abandoned and non-effort folders are not listed; e123 is listed once.
    for (const gone of ['2026-11-07-old', '2026-11-06-gone', 'plain-talk']) expect(all).not.toContain(gone)
    expect(lines.filter(l => l === '2026-11-08-e123').length).toBe(1)
    // AC-4: the failing worktree and the broken effort show their error; the rest are still listed.
    expect(all).toContain('nio-bad: ValueError: boom')
    expect(all).toContain('nio 2026-11-05-wreck: broken: state.json, line 3')
    // wreck is broken in two worktrees: one error row.
    expect(lines.filter(l => l.includes('2026-11-05-wreck')).length).toBe(1)
  }
})

test('AC-2: the pane follows a state change within one 30 s refresh', async ($, on) => {
  const status = { ...STATUS }
  setup(on, status)
  const clock = await start($, on)
  status['/w/nio-123'] = '2026-11-08-e123 · tasks_jury · auto · working · 2026-11-14 12:05\n'
  await clock.advance(29_000)
  expect((await texts($, 'terminal')).join('\n')).toContain('implementing · working')
  await clock.advance(1_000)
  expect((await texts($, 'terminal')).join('\n')).toContain('tasks_jury · working')
})

test('AC-6: the status line names the active count and their stages', async ($, on) => {
  const seen = setup(on)
  await start($, on)
  expect(seen.statuses.pop()).toBe('nio: 2 active (implementing x2) · 2 errors')
})

test('AC-7: no active effort anywhere', async ($, on) => {
  const seen = setup(on, {
    '/w/nio': '2026-11-07-old · done · manual · done · 2026-11-07 16:28\n',
    '/w/nio-123': '',
    '/w/nio-bad': '',
  })
  await start($, on)
  expect(seen.statuses.pop()).toBe('nio: no active effort')
  expect((await texts($, 'terminal'))[0]).toMatch(/^nio: no active effort · updated /)
})

test('AC-8, AC-10: /nio prints nio flow status per worktree, a failing one as an error block', async ($, on) => {
  const seen = setup(on)
  const { text } = await $.command.run({ command: 'nio' } as any)
  expect(text).toBe(
    [
      `/w/nio [main]\n${STATUS['/w/nio']!.trimEnd()}`,
      `/w/nio-123 [nio/e123]\n${STATUS['/w/nio-123']!.trimEnd()}`,
      '/w/nio-bad [nio/bad]\nerror: ValueError: boom',
    ].join('\n\n'),
  )
  // FR-9: every worktree's status run, from its own venv.
  expect(seen.argv.filter(a => a.endsWith('/.venv/bin/nio flow status')).length).toBe(3)
})

test('AC-11: a pane refresh and /nio write nothing and run only the two read commands', async ($, on) => {
  const seen = setup(on)
  const clock = await start($, on)
  await clock.advance(30_000)
  await $.command.run({ command: 'nio' } as any)
  expect(seen.writes).toEqual([])
  expect([...new Set(seen.argv)].sort()).toEqual([
    '/w/nio-123/.venv/bin/nio flow status',
    '/w/nio-bad/.venv/bin/nio flow status',
    '/w/nio/.venv/bin/nio flow status',
    'git worktree list --porcelain',
  ])
})

const NEW_TREE = PORCELAIN + '\nworktree /w/nio-new\nHEAD 4\nbranch refs/heads/nio/new\n'
const FRESH = '2026-11-15-fresh · planning · manual · working · 2026-11-15 09:00\n'

test('AC-24 nio on PATH: no venv runs the PATH nio, never uv', async ($, on) => {
  const seen = setup(on, { ...STATUS, '/w/nio-new': FRESH }, FILES, NEW_TREE)
  await start($, on)
  expect(seen.argv).toContain('nio flow status')
  expect(seen.argv.filter(a => a.startsWith('uv'))).toEqual([])
  expect((await texts($, 'terminal')).join('\n')).toContain('2026-11-15-fresh')
})

test('AC-24 nio on PATH: with no nio either, the row reads nio not found', async ($, on) => {
  setup(on, { ...STATUS, NO_NIO: 'x' }, FILES, NEW_TREE)
  await start($, on)
  expect((await texts($, 'terminal')).join('\n')).toContain('nio-new: nio not found')
})

// A finished effort is not listed from a stale copy in another worktree, older or as new.
for (const at of ['2026-11-14 11:00', '2026-11-14 12:00'])
  test(`AC-3: done at 12:00 in one worktree, implementing at ${at} in another: not listed`, async ($, on) => {
    const seen = setup(on, {
      '/w/nio': '2026-11-07-fin · done · manual · done · 2026-11-14 12:00\n',
      '/w/nio-123': `2026-11-07-fin · implementing · manual · working · ${at}\n`,
      '/w/nio-bad': '',
    })
    await start($, on)
    expect(seen.statuses.pop()).toBe('nio: no active effort')
  })

test('AC-14: an open first round with no ledger yet is round 1', async ($, on) => {
  // R-0 is a stale spec step (the spec ledger is at round 3): its logic pack has no output but is not running.
  const files: Record<string, string> = {
    ...FILES,
    '/w/nio-123/.nio/runs/R-1/jury/packs/step.json': JSON.stringify({ gate: 'implementation-E-1', round: 0, lenses: ['correctness'] }),
    '/w/nio-123/.nio/runs/R-0/jury/packs/step.json': JSON.stringify({ gate: 'spec', round: 2, lenses: ['logic'] }),
  }
  delete files['/w/nio-123/.nio/specs/2026-11-08-e123/jury/implementation-E-1.json']
  setup(on, STATUS, files)
  await start($, on)
  expect((await texts($, 'terminal')).join('\n')).toContain('nio-123 · jury 1 · task T-18 · jurors correctness\n')
})

test('AC-5, AC-14: a run left over from a gate the effort has passed shows no jury fields', async ($, on) => {
  // nio-jury's 2026-11-14-short-lived-drivers: at planning, its spec gate closed by the human at round 3, and
  // R-261114-i6dl's spec packs, written at round 3, never run.
  const wt = '/w/nio-123'
  const files: Record<string, string> = {
    ...FILES,
    [`${wt}/.nio/specs/2026-11-14-short-lived-drivers/state.json`]: JSON.stringify({ claims: {} }),
    [`${wt}/.nio/specs/2026-11-14-short-lived-drivers/jury/spec.json`]: JSON.stringify({ round: 3, outcome: 'human' }),
    [`${wt}/.nio/runs/R-261114-i6dl/jury/packs/step.json`]: JSON.stringify({ gate: 'spec', round: 3, lenses: ['consistency', 'logic', 'scope', 'testability'] }),
  }
  for (const lens of ['consistency', 'logic', 'scope', 'testability']) files[`${wt}/.nio/runs/R-261114-i6dl/jury/packs/${lens}.md`] = ''
  setup(on, { ...STATUS, [wt]: '2026-11-14-short-lived-drivers · planning · manual · working · 2026-11-14 12:00\n' }, files)
  await start($, on)
  expect((await texts($, 'terminal')).join('\n')).toContain('2026-11-14-short-lived-drivers\nplanning · working\nnio-123 · jury - · task - · jurors -\n')
})

// The drill-down: `flow show` answers per worktree (CT-12).
const ROW = (n: number, to: string) => ({ from: n === 1 ? 'planning' : 'plan_jury', to, role: 'orchestrator', host: 'test', model: 'test', at: `2026-11-10T1${n - 1}:00:00Z` })
const SHOWN = {
  timeline: [ROW(1, 'plan_jury'), ROW(2, 'tasking'), ROW(3, 'implementing')],
  juries: [], tasks: [], memory: [], context: [],
  cost: { stages: [], unattributed: '-', total: '-' },
}
const ok = () => result(0, JSON.stringify(SHOWN))
const SLUG = '2026-11-08-e123'
const NIO = '/w/nio-123/.venv/bin/nio'

const open = async ($: any, on: any, show: (cwd: string | undefined) => ReturnType<typeof result>, status = STATUS) => {
  const seen = setup(on, status, FILES, PORCELAIN, show)
  const model: string[] = []
  on('model.complete' as any, () => (model.push('call'), { value: '' }))
  const clock = await start($, on)
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  await ui.press({ key: SLUG })
  await clock.settle()
  const read = async () => ((await ui.findAll({ type: 'Text' })) ?? []).map((t: any) => t.text as string)
  return { seen, model, ui, read, clock }
}
const buttons = async (ui: any) => ((await ui.findAll({ type: 'Button' })) ?? []).map((b: any) => b.key ?? b.props?.key)

test('AC-1 drill-down timeline', async ($, on) => {
  const { seen, model, read } = await open($, on, ok)
  expect(seen.argv.filter(a => a === `${NIO} flow show ${SLUG} --json`).length).toBe(1)
  const all = (await read()).join('\n')
  const at = ['planning → plan_jury', 'plan_jury → tasking', 'plan_jury → implementing'].map((x, i) => `${x} · orchestrator · test · test · 2026-11-10T1${i}:00:00Z`)
  expect(all.indexOf(at[0]!)).toBeGreaterThanOrEqual(0)
  expect(all.indexOf(at[1]!)).toBeGreaterThan(all.indexOf(at[0]!))
  expect(all.indexOf(at[2]!)).toBeGreaterThan(all.indexOf(at[1]!))
  expect(model).toEqual([])
})

test('AC-5 back to the list', async ($, on) => {
  const { ui, read, clock } = await open($, on, ok)
  await ui.press({ key: 'back' })
  await clock.settle()
  const all = (await read()).join('\n')
  expect(all).toContain('2026-11-08-e123\nimplementing · working\nnio-123 · jury 2 · task T-18 · jurors correctness')
  expect(all).toContain('2026-11-08-e49')
  expect(all).not.toContain('orchestrator · test · test')
})

test('AC-29 AC-30 drill-down errors', async ($, on) => {
  let o = await open($, on, () => result(1, JSON.stringify({ error: `${SLUG} is done` })))
  expect((await o.read()).join('\n')).toContain(`${SLUG} is done`)
  expect(await buttons(o.ui)).toEqual(['back'])
})

test('AC-29 AC-30 drill-down errors: an old nio says to update', async ($, on) => {
  const o = await open($, on, () => result(2, '', "nio flow: error: argument flow_cmd: invalid choice: 'show' (choose from ...)"))
  expect((await o.read()).join('\n')).toContain('this nio has no flow show: update nio')
  expect(await buttons(o.ui)).toEqual(['back'])
})

test('UJ-1 the drill-down only reads', async ($, on) => {
  const { seen, ui } = await open($, on, ok)
  expect(await buttons(ui)).toEqual(['back'])
  expect([...new Set(seen.argv)].sort()).toEqual([
    `${NIO} flow show ${SLUG} --json`,
    '/w/nio-123/.venv/bin/nio flow status',
    '/w/nio-bad/.venv/bin/nio flow status',
    '/w/nio/.venv/bin/nio flow status',
    'git worktree list --porcelain',
  ])
  expect(seen.writes).toEqual([])
})

test('AC-4 a broken effort opens', async ($, on) => {
  const err = `${SLUG}: history.jsonl, line 2`
  const shown = { ...SHOWN, timeline: { error: err }, cost: { error: err }, juries: [{ gate: 'spec', outcome: 'approved', rounds: [], findings: [] }] }
  const { seen, read, ui } = await open($, on, () => result(0, JSON.stringify(shown)), {
    ...STATUS,
    '/w/nio-123': `${SLUG} · broken: history.jsonl, line 2\n`,
  })
  expect(seen.argv.filter(a => a.includes('flow show')).length).toBe(1)
  const all = (await read()).join('\n')
  expect(all).toContain(`error: ${err}`)
  expect(all).toContain('spec')
  expect(all).toContain('no tasks yet')
  expect(all).toContain('no memory yet')
  expect(await buttons(ui)).toContain('back')
})

import { expect, test } from 'claude-code/testing'

const SUITE = "printf '%s\\n' tests/test_*.py | xargs -P8 -I{} sh -c 'uv run python {} || exit 1'"
const CONFIG = JSON.stringify({ tests: { suite: SUITE }, jury: { run_timeout: 1800 } })

type Seen = { command?: unknown; description?: unknown; timeout?: unknown; run_in_background?: unknown }

// Stands for the engine: answers the config read and records the call the mod passed down.
const setup = (on: any, config: () => string = () => CONFIG) => {
  const seen: Seen[] = []
  on('fs.read', () => ({ value: config() }))
  on('tool.call', (_: unknown, e: Seen) => {
    seen.push(e)
    return { result: {} }
  })
  return seen
}

const call = async ($: any, command: unknown, extra: object = {}) =>
  $.tool.call({ tool: 'Bash', command, description: 'Run it', timeout: 600000, ...extra })

const BACKGROUNDED = [
  'nio jury evidence S pr --run R', // AC-1
  'nio flow finish 2026-11-14-x E-3 --by x', // AC-2
  SUITE, // AC-3
  'uv run nio jury evidence x pr', // AC-4
  'uv run nio flow finish S E-1 --by x',
  'cd /w && nio jury evidence S pr',
  'cd /home/work/nio && uv run nio flow finish x E-1 2>&1 | tail -40',
  `cd /home/work/nio && ${SUITE}`,
]

test('AC-1..AC-5: long commands are backgrounded, nothing else changes', async ($, on) => {
  const seen = setup(on)
  for (const command of BACKGROUNDED) {
    await call($, command)
    // AC-5: the same call, plus run_in_background alone.
    const { tool_use_id: _, ...e } = seen.pop() as Seen & { tool_use_id?: string }
    expect(e).toEqual({
      tool: 'Bash',
      command,
      description: 'Run it',
      timeout: 600000,
      run_in_background: true,
    } as any)
  }
})

const UNCHANGED = [
  'nio flow status', // AC-8
  'nio check spec 2026-11-14-x',
  'uv run python tests/test_flow.py',
  'uv run nio jury collect x',
  'nio jury run S spec', // no such command since 2026-11-15
  'nio flow green S T-1', // removed with red/green (2026-11-15)
  'ls -la',
  'echo "nio jury evidence"', // AC-9
  "grep 'nio flow finish' skills/implement/SKILL.md",
  'grep -n "nio jury evidence" a && echo "x; nio flow finish"',
  `echo "${SUITE.replace(/'/g, '')}"`,
]

const expectUnchanged = async ($: any, seen: Seen[], command: unknown, extra: object = {}) => {
  await call($, command, extra)
  const e = seen.pop()!
  expect(e.command).toBe(command)
  expect(e.run_in_background).toBe((extra as Seen).run_in_background)
}

test('AC-8, AC-9: other commands and mentions pass through unchanged', async ($, on) => {
  const seen = setup(on)
  for (const command of UNCHANGED) await expectUnchanged($, seen, command)
})

test('AC-10: an explicit run_in_background, true or false, is kept', async ($, on) => {
  const seen = setup(on)
  for (const command of BACKGROUNDED) {
    await expectUnchanged($, seen, command, { run_in_background: false })
    await expectUnchanged($, seen, command, { run_in_background: true })
  }
})

for (const [name, config] of [
  ['missing', () => { throw new Error('ENOENT: .nio/config.json') }],
  ['malformed', () => '{ not json'],
  ['without a suite', () => '{"jury": {}}'],
] as const) {
  test(`AC-11: with the config ${name}, only the nio commands are backgrounded`, async ($, on) => {
    const seen = setup(on, config)
    await call($, 'nio jury evidence x pr')
    expect(seen.pop()!.run_in_background).toBe(true)
    await call($, 'cd /tmp && uv run nio flow finish x E-1')
    expect(seen.pop()!.run_in_background).toBe(true)
    await expectUnchanged($, seen, SUITE)
  })
}

test('AC-12: a hook failure on bad input lets the call run as issued', async ($, on) => {
  const seen = setup(on)
  await expectUnchanged($, seen, undefined)
  await expectUnchanged($, seen, 42)
})

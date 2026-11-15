import type { Register } from 'claude-code'

// A segment that runs `nio jury evidence` or `nio flow finish`, optionally via `uv run`.
const LONG_NIO = /^(?:uv\s+run\s+)?nio\s+(?:jury\s+evidence|flow\s+finish)(?:\s|$)/
// Leading `cd <dir> &&` prefixes before the configured suite command.
const CD_PREFIX = /^(?:\s*cd\s+\S+\s*&&)*\s*/

// Splits a command on `&&`, `||`, `;`, `|` and newlines outside quotes.
const segments = (command: string): string[] => {
  const out: string[] = []
  let quote = ''
  let cur = ''
  for (let i = 0; i < command.length; i++) {
    const c = command[i]!
    if (quote) {
      if (c === quote) quote = ''
      else if (c === '\\' && quote === '"') cur += command[i++]
    } else if (c === '"' || c === "'") quote = c
    else if (c === '\\') cur += command[i++]
    else if (c === ';' || c === '\n' || c === '|' || (c === '&' && command[i + 1] === '&')) {
      if (command[i + 1] === c) i++
      out.push(cur.trim())
      cur = ''
      continue
    }
    cur += c
  }
  out.push(cur.trim())
  return out
}

export const register: Register = on => {
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    let long = false
    try {
      // The agent's own choice, true or false, always wins.
      if (e.run_in_background === undefined) {
        long = segments(e.command).some(s => LONG_NIO.test(s))
        if (!long) {
          const suite = JSON.parse(await $.fs.read('.nio/config.json'))?.tests?.suite
          long = typeof suite === 'string' && suite.trim() !== '' &&
            e.command.replace(CD_PREFIX, '').trim() === suite.trim()
        }
      }
    } catch {
      // Missing or broken config, or bad input: leave the call as issued.
    }
    return next(long ? { ...e, run_in_background: true } : e)
  }).catch(($, e, next) => next(e)) // Throw or overrun: run as issued (a call already made replays).
}

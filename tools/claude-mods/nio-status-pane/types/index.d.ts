// One pane row: an active effort, or an error (`slug` empty when the whole worktree failed).
export type NioRow =
  | { worktree: string; slug: string; stage: string; status: string; round: string; task: string; jurors: string; path?: string }
  | { worktree: string; slug: string; error: string; path?: string }

export type NioBoard = { at: string; rows: NioRow[] }

declare module 'claude-code' {
  interface PluginState {
    'nio-status-pane': { board: NioBoard | null; drill: { path: string; slug: string } | null }
  }
}

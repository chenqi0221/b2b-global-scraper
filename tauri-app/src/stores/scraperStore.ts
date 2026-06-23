import { create } from 'zustand'

import { API_BASE } from '../config/api'
import type { ScrapeStatus } from '../types/api'

type State = {
  status: ScrapeStatus | null
  statusError: string | null
  projectRoot: string | null
  pollIntervalMs: number
  fetchStatus: () => Promise<void>
  fetchProjectRoot: () => Promise<void>
}

const BASE_POLL_INTERVAL_MS = 2000
const MAX_POLL_INTERVAL_MS = 30000

let statusFailCount = 0

function computePollInterval(failCount: number): number {
  if (failCount <= 0) return BASE_POLL_INTERVAL_MS
  return Math.min(MAX_POLL_INTERVAL_MS, BASE_POLL_INTERVAL_MS * 2 ** Math.min(failCount, 4))
}

export const useScraperStore = create<State>((set) => ({
  status: null,
  statusError: null,
  projectRoot: null,
  pollIntervalMs: BASE_POLL_INTERVAL_MS,
  fetchStatus: async () => {
    const delays = [0, 800, 2000, 4000]
    let last: unknown = null
    for (const ms of delays) {
      if (ms > 0) await new Promise((r) => setTimeout(r, ms))
      try {
        const r = await fetch(`${API_BASE}/api/scraper/status`)
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const j = (await r.json()) as ScrapeStatus
        statusFailCount = 0
        set({ status: j, statusError: null, pollIntervalMs: computePollInterval(0) })
        return
      } catch (e) {
        last = e
      }
    }
    statusFailCount++
    const nextInterval = computePollInterval(statusFailCount)
    const update: Partial<State> = { pollIntervalMs: nextInterval }
    if (statusFailCount >= 5) {
      update.statusError =
        last instanceof Error
          ? last.message
          : String(last ?? 'unknown')
    }
    set(update)
  },
  fetchProjectRoot: async () => {
    const delays = [0, 800, 2000, 4000]
    for (const ms of delays) {
      if (ms > 0) await new Promise((r) => setTimeout(r, ms))
      try {
        const r = await fetch(`${API_BASE}/api/system/project-root`)
        if (!r.ok) continue
        const j = (await r.json()) as { root: string }
        set({ projectRoot: j.root })
        return
      } catch {
        /* retry */
      }
    }
  },
}))

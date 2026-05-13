import { create } from 'zustand'

import { API_BASE } from '../config/api'
import type { ScrapeStatus } from '../types/api'

type State = {
  status: ScrapeStatus | null
  statusError: string | null
  projectRoot: string | null
  fetchStatus: () => Promise<void>
  fetchProjectRoot: () => Promise<void>
}

export const useScraperStore = create<State>((set) => ({
  status: null,
  statusError: null,
  projectRoot: null,
  fetchStatus: async () => {
    const delays = [0, 500, 1500]
    let last: unknown = null
    for (const ms of delays) {
      if (ms > 0) await new Promise((r) => setTimeout(r, ms))
      try {
        const r = await fetch(`${API_BASE}/api/scraper/status`)
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const j = (await r.json()) as ScrapeStatus
        set({ status: j, statusError: null })
        return
      } catch (e) {
        last = e
      }
    }
    set({
      statusError:
        last instanceof Error
          ? last.message
          : String(last ?? 'unknown'),
    })
  },
  fetchProjectRoot: async () => {
    const delays = [0, 500, 1500]
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

import { useEffect, useState } from 'react'

export type AccentTheme = 'default' | 'purple' | 'green' | 'orange'
export type ThemeMode = 'dark' | 'light'

const ACCENT_KEY = 'b2b-accent'
const MODE_KEY = 'b2b-mode'

const ACCENTS: { key: AccentTheme; label: string; color: string }[] = [
  { key: 'default', label: '科技蓝', color: '#38bdf8' },
  { key: 'purple', label: '极光紫', color: '#a78bfa' },
  { key: 'green', label: '翡翠绿', color: '#34d399' },
  { key: 'orange', label: '暖阳橙', color: '#fb923c' },
]

function getStoredAccent(): AccentTheme {
  try {
    const v = localStorage.getItem(ACCENT_KEY)
    if (v === 'default' || v === 'purple' || v === 'green' || v === 'orange') return v
  } catch { /* ignore */ }
  return 'default'
}

function setStoredAccent(v: AccentTheme) {
  try { localStorage.setItem(ACCENT_KEY, v) } catch { /* ignore */ }
}

function getStoredMode(): ThemeMode {
  try {
    const v = localStorage.getItem(MODE_KEY)
    if (v === 'dark' || v === 'light') return v
  } catch { /* ignore */ }
  return 'dark'
}

function setStoredMode(v: ThemeMode) {
  try { localStorage.setItem(MODE_KEY, v) } catch { /* ignore */ }
}

export function useTheme() {
  const [accent, setAccent] = useState<AccentTheme>(getStoredAccent)
  const [mode, setMode] = useState<ThemeMode>(getStoredMode)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', accent)
    document.documentElement.setAttribute('data-mode', mode)
    setStoredAccent(accent)
    setStoredMode(mode)
  }, [accent, mode])

  const toggleMode = () => setMode((prev) => (prev === 'dark' ? 'light' : 'dark'))

  return { accent, setAccent, mode, toggleMode, accents: ACCENTS }
}
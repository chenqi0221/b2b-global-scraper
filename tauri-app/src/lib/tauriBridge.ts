import { invoke } from '@tauri-apps/api/core'

/** 在 Tauri WebView 内为 true；纯浏览器 `vite` 为 false。 */
export function isTauri(): boolean {
  if (typeof window === 'undefined') return false
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return Boolean((window as any).__TAURI_INTERNALS__)
}

export async function pickCsvFile(): Promise<string | null> {
  if (!isTauri()) return null
  const { open } = await import('@tauri-apps/plugin-dialog')
  const selected = await open({
    multiple: false,
    directory: false,
    filters: [{ name: 'CSV', extensions: ['csv'] }],
  })
  if (selected === null) return null
  return Array.isArray(selected) ? (selected[0] ?? null) : selected
}

export async function pickDirectory(): Promise<string | null> {
  if (!isTauri()) return null
  const { open } = await import('@tauri-apps/plugin-dialog')
  const selected = await open({
    multiple: false,
    directory: true,
  })
  if (selected === null) return null
  return Array.isArray(selected) ? (selected[0] ?? null) : selected
}

export async function pickDirectoryBrowser(): Promise<File[]> {
  if (typeof window === 'undefined' || typeof (window as any).showDirectoryPicker !== 'function') {
    return []
  }
  try {
    const dirHandle = await (window as any).showDirectoryPicker({ mode: 'read' })
    const files: File[] = []
    for await (const [name, handle] of (dirHandle as any).entries()) {
      if (name.endsWith('.csv') && (handle as any).kind === 'file') {
        const file = await (handle as any).getFile()
        files.push(file)
      }
    }
    return files
  } catch {
    return []
  }
}

export async function revealPath(path: string): Promise<void> {
  if (!isTauri()) {
    window.alert('请在 Tauri 桌面版中使用「在资源管理器中打开」')
    return
  }
  await invoke('reveal_path', { path })
}

export async function whatsappServiceStart(): Promise<string> {
  if (!isTauri()) {
    return '请在 Tauri 桌面版中启动 Node 服务（或命令行运行 node web.js）'
  }
  return invoke<string>('whatsapp_service_start')
}

export async function whatsappServiceStop(): Promise<void> {
  if (!isTauri()) return
  await invoke('whatsapp_service_stop')
}

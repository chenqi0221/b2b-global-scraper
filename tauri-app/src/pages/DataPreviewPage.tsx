import { useEffect, useState } from 'react'

import { API_BASE } from '../config/api'
import type { CsvPreview, DownloadSession, RootCsvEntry } from '../types/api'

import './FormPage.css'

export default function DataPreviewPage() {
  const [sessions, setSessions] = useState<DownloadSession[]>([])
  const [rootCsv, setRootCsv] = useState<RootCsvEntry[]>([])
  const [sessionSel, setSessionSel] = useState('')
  const [rootSel, setRootSel] = useState('')
  /** 当前选中的 CSV 路径（会话目录或根目录文件），供预览与刷新 */
  const [path, setPath] = useState('')
  const [preview, setPreview] = useState<CsvPreview | null>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    void (async () => {
      try {
        const [a, b] = await Promise.all([
          fetch(`${API_BASE}/api/data/downloads-sessions`),
          fetch(`${API_BASE}/api/data/root-csv`),
        ])
        if (!a.ok || !b.ok) return
        const s = (await a.json()) as DownloadSession[]
        const r = (await b.json()) as RootCsvEntry[]
        if (!cancelled) {
          setSessions(s)
          setRootCsv(r)
        }
      } catch {
        /* ignore */
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  async function loadPreview(p: string) {
    setErr(null)
    setPreview(null)
    if (!p) return
    try {
      const q = `${API_BASE}/api/data/preview-csv?path=${encodeURIComponent(p)}&limit=120`
      const r = await fetch(q)
      if (!r.ok) {
        const t = await r.text()
        throw new Error(t || `HTTP ${r.status}`)
      }
      const data = (await r.json()) as Partial<CsvPreview>
      if (!Array.isArray(data.columns)) {
        throw new Error('预览数据格式异常：缺少 columns')
      }
      setPreview({
        path: String(data.path ?? p),
        columns: data.columns.map(String),
        rows: Array.isArray(data.rows) ? (data.rows as CsvPreview['rows']) : [],
      })
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e))
    }
  }

  return (
    <div className="form-page">
      <h1 className="page-title">数据预览</h1>
      <p className="page-muted">从 Downloads 会话目录（自动取该目录内最新修改的 CSV）或根目录汇总 CSV 中选择，抽样展示前若干行。</p>

      <div className="preview-toolbar">
        <label>
          Downloads 会话
          <select
            value={sessionSel}
            onChange={(e) => {
              const p = e.target.value
              setSessionSel(p)
              setRootSel('')
              setPath(p)
              void loadPreview(p)
            }}
          >
            <option value="">选择会话目录…</option>
            {sessions.map((s) => (
              <option key={s.path} value={s.path}>
                {s.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          根目录 CSV
          <select
            value={rootSel}
            onChange={(e) => {
              const p = e.target.value
              setRootSel(p)
              setSessionSel('')
              setPath(p)
              void loadPreview(p)
            }}
          >
            <option value="">选择文件…</option>
            {rootCsv.map((c) => (
              <option key={c.path} value={c.path}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
        <button type="button" className="btn" disabled={!path} onClick={() => void loadPreview(path)}>
          刷新预览
        </button>
      </div>

      {path ? (
        <p className="page-muted">
          当前：<code>{path}</code>
        </p>
      ) : null}
      {err ? <p className="page-muted" style={{ color: '#b91c1c' }}>{err}</p> : null}

      {preview && preview.columns.length > 0 ? (
        <div className="preview-table-wrap">
          <table className="preview-table">
            <thead>
              <tr>
                {preview.columns.map((c) => (
                  <th key={c}>{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.rows.map((row, i) => (
                <tr key={i}>
                  {preview.columns.map((c) => (
                    <td key={c}>{String(row[c] ?? '')}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  )
}

import { useEffect, useMemo, useState } from 'react'

import { API_BASE } from '../config/api'
import type { KeywordRow } from '../types/api'

import './KeywordLibraryModal.css'

type Props = {
  open: boolean
  onClose: () => void
  onApplyToEngine?: (lines: string) => void
}

export function KeywordLibraryModal({ open, onClose, onApplyToEngine }: Props) {
  const [rows, setRows] = useState<KeywordRow[]>([])
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [loading, setLoading] = useState(false)
  const [seed, setSeed] = useState('')
  const [num, setNum] = useState(7)

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return rows.map((r, i) => ({ row: r, idx: i }))
    return rows
      .map((r, i) => ({ row: r, idx: i }))
      .filter(
        ({ row }) =>
          row.en.toLowerCase().includes(q) || (row.zh || '').toLowerCase().includes(q)
      )
  }, [rows, search])

  const load = async () => {
    setLoading(true)
    try {
      const r = await fetch(`${API_BASE}/api/keywords/library`)
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      setSelected(new Set())
      setRows((await r.json()) as KeywordRow[])
    } catch {
      setRows([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (open) void load()
  }, [open])

  function toggle(i: number) {
    setSelected((prev) => {
      const n = new Set(prev)
      if (n.has(i)) n.delete(i)
      else n.add(i)
      return n
    })
  }

  function selectAllFiltered() {
    setSelected((prev) => {
      const n = new Set(prev)
      for (const { idx } of filtered) n.add(idx)
      return n
    })
  }

  function invertFiltered() {
    setSelected((prev) => {
      const n = new Set(prev)
      for (const { idx } of filtered) {
        if (n.has(idx)) n.delete(idx)
        else n.add(idx)
      }
      return n
    })
  }

  async function onDelete() {
    const items = [...selected].sort((a, b) => a - b).map((i) => rows[i])
    if (!items.length) return
    if (!window.confirm(`删除 ${items.length} 条？`)) return
    const r = await fetch(`${API_BASE}/api/keywords/library/delete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items }),
    })
    if (!r.ok) {
      window.alert('删除失败')
      return
    }
    void load()
  }

  function onExport() {
    window.open(`${API_BASE}/api/keywords/library/export`, '_blank', 'noopener,noreferrer')
  }

  async function onImport(ev: React.ChangeEvent<HTMLInputElement>) {
    const f = ev.target.files?.[0]
    if (!f) return
    const fd = new FormData()
    fd.append('file', f)
    const r = await fetch(`${API_BASE}/api/keywords/library/import`, { method: 'POST', body: fd })
    ev.target.value = ''
    const j = (await r.json()) as { ok: boolean; message?: string }
    window.alert(j.message ?? (j.ok ? '导入完成' : '导入失败'))
    void load()
  }

  async function onGenerate() {
    if (!seed.trim()) {
      window.alert('请输入 AI 种子 / 行业描述')
      return
    }
    const r = await fetch(`${API_BASE}/api/keywords/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ seed: seed.trim(), num }),
    })
    if (!r.ok) {
      window.alert('生成失败')
      return
    }
    const j = (await r.json()) as { keywords: KeywordRow[] }
    const nk = j.keywords ?? []
    if (!nk.length) {
      window.alert('无结果')
      return
    }
    const r2 = await fetch(`${API_BASE}/api/keywords/library/append`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(nk),
    })
    if (!r2.ok) {
      window.alert('写入词库失败')
      return
    }
    void load()
  }

  function applyToEngine() {
    if (selected.size === 0) {
      window.alert('请先勾选要应用到引擎的关键词')
      return
    }
    const items = [...selected].sort((a, b) => a - b).map((i) => rows[i])
    const text = items.map((x) => x.en.trim()).filter(Boolean).join('\n')
    onApplyToEngine?.(text)
    onClose()
  }

  if (!open) return null

  return (
    <div className="kw-modal-root" role="dialog" aria-modal="true">
      <button type="button" className="kw-modal-backdrop" aria-label="关闭" onClick={onClose} />
      <div className="kw-modal-panel">
        <header className="kw-modal-head">
          <h2>关键词库</h2>
          <button type="button" className="btn" onClick={onClose}>
            关闭
          </button>
        </header>
        {loading ? <p className="page-muted">加载中…</p> : null}
        <div className="kw-search-row">
          <label className="kw-search-label">
            搜索
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="英文或中文…"
            />
          </label>
          <span className="kw-count">共 {filtered.length} / {rows.length}</span>
        </div>
        <div className="kw-modal-toolbar">
          <button type="button" className="btn" onClick={selectAllFiltered}>
            全选当前列表
          </button>
          <button type="button" className="btn" onClick={invertFiltered}>
            反选当前列表
          </button>
          <button type="button" className="btn" onClick={() => void onDelete()} disabled={selected.size === 0}>
            删除选中
          </button>
          <button type="button" className="btn" onClick={onExport}>
            导出 CSV
          </button>
          <label className="btn">
            导入 CSV
            <input type="file" accept=".csv" hidden onChange={(e) => void onImport(e)} />
          </label>
          {onApplyToEngine ? (
            <button type="button" className="btn primary" onClick={applyToEngine}>
              应用到引擎
            </button>
          ) : null}
        </div>
        <div className="kw-gen-row">
          <input placeholder="AI 种子 / 行业" value={seed} onChange={(e) => setSeed(e.target.value)} />
          <input type="number" min={1} max={30} value={num} onChange={(e) => setNum(Number(e.target.value) || 7)} />
          <button type="button" className="btn primary" onClick={() => void onGenerate()}>
            AI 生成并入库
          </button>
        </div>
        <div className="kw-table-wrap">
          <table className="kw-table">
            <thead>
              <tr>
                <th className="kw-col-check" />
                <th>English</th>
                <th>中文</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(({ row, idx }) => (
                <tr key={idx}>
                  <td>
                    <input type="checkbox" checked={selected.has(idx)} onChange={() => toggle(idx)} />
                  </td>
                  <td>{row.en}</td>
                  <td>{row.zh}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

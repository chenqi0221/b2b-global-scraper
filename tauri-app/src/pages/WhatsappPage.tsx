import { useCallback, useEffect, useState } from 'react'

import { API_BASE } from '../config/api'
import { isTauri, pickCsvFile, whatsappServiceStart, whatsappServiceStop } from '../lib/tauriBridge'

import './FormPage.css'

const WA_UI = 'http://127.0.0.1:3003'

export default function WhatsappPage() {
  const [probe, setProbe] = useState<string | null>(null)
  const [upstream, setUpstream] = useState<unknown>(null)
  const [csvPath, setCsvPath] = useState('')
  const [phonesPreview, setPhonesPreview] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const refreshUpstream = useCallback(async () => {
    try {
      const r = await fetch(`${API_BASE}/api/whatsapp/upstream-status`)
      if (!r.ok) {
        setUpstream({ error: `HTTP ${r.status}` })
        return
      }
      setUpstream(await r.json())
    } catch (e) {
      setUpstream({ error: e instanceof Error ? e.message : String(e) })
    }
  }, [])

  useEffect(() => {
    void refreshUpstream()
    const id = window.setInterval(() => void refreshUpstream(), 4000)
    return () => window.clearInterval(id)
  }, [refreshUpstream])

  async function checkHealth() {
    try {
      const r = await fetch(`${API_BASE}/api/whatsapp/health`)
      const j = (await r.json()) as { ok: boolean; upstream_status?: number; error?: string }
      setProbe(JSON.stringify(j, null, 2))
    } catch (e) {
      setProbe(e instanceof Error ? e.message : String(e))
    }
  }

  async function onPickCsv() {
    const p = await pickCsvFile()
    if (p) setCsvPath(p)
  }

  async function loadPhones() {
    if (!csvPath.trim()) {
      window.alert('请填写或选择 CSV 路径（须在项目根下）')
      return
    }
    setBusy(true)
    setPhonesPreview(null)
    try {
      const q = `${API_BASE}/api/whatsapp/map-csv-phones?path=${encodeURIComponent(csvPath.trim())}&limit=80`
      const r = await fetch(q)
      const j = (await r.json()) as { phones?: string[]; phone_column?: string | null; hint?: string }
      setPhonesPreview(JSON.stringify(j, null, 2))
    } catch (e) {
      setPhonesPreview(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
    }
  }

  async function onStartNode() {
    if (!isTauri()) {
      window.alert('请在 Tauri 桌面版使用「启动 Node」或手动在项目目录运行 node third_party/whatsapp-service/web.js')
      return
    }
    try {
      const msg = await whatsappServiceStart()
      window.alert(msg)
      void refreshUpstream()
    } catch (e) {
      window.alert(e instanceof Error ? e.message : String(e))
    }
  }

  async function onStopNode() {
    if (!isTauri()) return
    try {
      await whatsappServiceStop()
      window.alert('已请求停止 Node 进程')
    } catch (e) {
      window.alert(e instanceof Error ? e.message : String(e))
    }
  }

  return (
    <div className="form-page whatsapp-page">
      <h1 className="page-title">WhatsApp</h1>
      <p className="page-muted">
        本地 Node 默认 <code>{WA_UI}</code>。环境变量 <code>WA_SERVICE_URL</code> 可覆盖上游地址。桌面版可用「启动/停止
        Node」编排子进程（需已 <code>npm install</code>）。
      </p>
      <div className="wa-toolbar">
        <button type="button" className="btn primary" onClick={() => void checkHealth()}>
          探测 TCP 连通
        </button>
        <button type="button" className="btn" onClick={() => void refreshUpstream()}>
          刷新扫码状态
        </button>
        <button type="button" className="btn" onClick={() => void onStartNode()}>
          启动 Node（Tauri）
        </button>
        <button type="button" className="btn" onClick={() => void onStopNode()}>
          停止 Node（Tauri）
        </button>
        <a className="btn" href={WA_UI} target="_blank" rel="noreferrer">
          浏览器打开控制台
        </a>
      </div>
      {probe ? (
        <pre className="page-muted" style={{ marginTop: '0.75rem', whiteSpace: 'pre-wrap' }}>
          {probe}
        </pre>
      ) : null}

      <div className="wa-wrap">
        <div className="wa-frame">
          <iframe title="WhatsApp Web UI" src={WA_UI} />
        </div>
      </div>

      <section className="form-card" style={{ marginTop: '1rem' }}>
        <h2 className="wa-section-title">上游状态（GET /api/status）</h2>
        <pre className="wa-json-pre">{upstream ? JSON.stringify(upstream, null, 2) : '加载中…'}</pre>
      </section>
      <section className="form-card" style={{ marginTop: '1rem' }}>
        <h2 className="wa-section-title">地图 CSV → 号码预览（联动）</h2>
        <p className="page-muted">用于核对导出 CSV 中的电话列，再于 Node 控制台进行群发等操作。</p>
        <div className="wa-csv-row">
          <input
            type="text"
            placeholder="项目根下 CSV 路径，或点「选文件」"
            value={csvPath}
            onChange={(e) => setCsvPath(e.target.value)}
            style={{ flex: 1, minWidth: 200 }}
          />
          <button type="button" className="btn" onClick={() => void onPickCsv()}>
            选文件
          </button>
          <button type="button" className="btn primary" disabled={busy} onClick={() => void loadPhones()}>
            加载号码
          </button>
        </div>
        {phonesPreview ? (
          <pre className="wa-json-pre" style={{ marginTop: '0.75rem' }}>
            {phonesPreview}
          </pre>
        ) : null}
      </section>
    </div>
  )
}

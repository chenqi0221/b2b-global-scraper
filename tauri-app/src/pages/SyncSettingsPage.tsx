import { useEffect, useState } from 'react'

import { API_BASE } from '../config/api'
import type { EnvSettingsView, OauthStatus } from '../types/api'

import './FormPage.css'

export default function SyncSettingsPage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState<EnvSettingsView | null>(null)
  const [oauth, setOauth] = useState<OauthStatus | null>(null)
  const [oauthBusy, setOauthBusy] = useState(false)
  const [oauthMsg, setOauthMsg] = useState<string | null>(null)
  const [testStatus, setTestStatus] = useState<{ ok: boolean; msg: string } | null>(null)
  const [testing, setTesting] = useState(false)

  const loadOauth = async () => {
    try {
      const r = await fetch(`${API_BASE}/api/google/oauth/status`)
      if (!r.ok) return
      setOauth((await r.json()) as OauthStatus)
    } catch {
      setOauth(null)
    }
  }

  useEffect(() => {
    let cancelled = false
    void (async () => {
      try {
        const r = await fetch(`${API_BASE}/api/config/`)
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const j = (await r.json()) as EnvSettingsView
        if (!cancelled) setForm(j)
      } catch {
        if (!cancelled) setForm(null)
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    void loadOauth()
    return () => {
      cancelled = true
    }
  }, [])

  async function onSave() {
    if (!form) return
    setSaving(true)
    try {
      const r = await fetch(`${API_BASE}/api/config/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      window.alert('已保存（含「…」的脱敏字段未改动，需重新填写才会更新）。')
    } catch (e) {
      window.alert(e instanceof Error ? e.message : String(e))
    } finally {
      setSaving(false)
    }
  }

  async function onOauthAuthorize() {
    if (!window.confirm('将打开系统浏览器完成 Google 登录，完成后请返回本应用。是否继续？')) return
    setOauthBusy(true)
    setOauthMsg(null)
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 120000)
    try {
      const r = await fetch(`${API_BASE}/api/google/oauth/authorize`, {
        method: 'POST',
        signal: controller.signal,
      })
      const j = (await r.json().catch(() => ({}))) as { ok?: boolean; detail?: string }
      if (!r.ok) {
        const detail = typeof j.detail === 'string' ? j.detail : `失败 HTTP ${r.status}`
        setOauthMsg(`授权失败: ${detail}`)
        return
      }
      setOauthMsg(j.ok ? '授权完成，正在更新 token 状态…' : '授权未完成')
      await loadOauth()
      setOauthMsg('授权成功 ✓')
    } catch (e) {
      if (e instanceof DOMException && e.name === 'AbortError') {
        setOauthMsg('授权超时（超过 2 分钟），请重试')
      } else {
        setOauthMsg(e instanceof TypeError ? '后端无响应，请确认程序已启动' : `授权出错: ${e instanceof Error ? e.message : String(e)}`)
      }
    } finally {
      clearTimeout(timeout)
      setOauthBusy(false)
    }
  }

  async function onOauthRefresh() {
    setOauthBusy(true)
    setOauthMsg(null)
    try {
      const r = await fetch(`${API_BASE}/api/google/oauth/refresh`, { method: 'POST' })
      const j = (await r.json()) as { ok?: boolean }
      setOauthMsg(j.ok ? 'token 已刷新 ✓' : '刷新失败或无 refresh_token，请重新授权')
      void loadOauth()
    } catch (e) {
      setOauthMsg(e instanceof TypeError ? '后端无响应，请确认程序已启动' : `刷新出错: ${e instanceof Error ? e.message : String(e)}`)
    } finally {
      setOauthBusy(false)
    }
  }

  async function onTestLLM() {
    if (!form) return
    const key = form.DOUBAO_API_KEY
    if (!key || key.includes('…')) {
      setTestStatus({ ok: false, msg: '请先填写完整的豆包 API Key（不能包含脱敏的「…」）' })
      return
    }
    if (!form.DOUBAO_MODEL_ENDPOINT) {
      setTestStatus({ ok: false, msg: '请先填写 豆包 Model Endpoint' })
      return
    }
    setTesting(true)
    setTestStatus(null)
    try {
      const r = await fetch(`${API_BASE}/api/ai/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: key,
          base_url: form.DOUBAO_BASE_URL,
          model_endpoint: form.DOUBAO_MODEL_ENDPOINT,
        }),
      })
      const j = (await r.json()) as {
        ok?: boolean
        elapsed_ms?: number
        reply?: string
        error?: string
        usage?: { prompt_tokens?: number; completion_tokens?: number }
      }
      if (j.ok) {
        setTestStatus({ ok: true, msg: `连接成功！响应: "${j.reply ?? ''}"，耗时 ${j.elapsed_ms ?? 0}ms` })
      } else {
        setTestStatus({ ok: false, msg: `连接失败：${j.error ?? '未知错误'} (${j.elapsed_ms ?? 0}ms)` })
      }
    } catch (e) {
      setTestStatus({ ok: false, msg: e instanceof TypeError ? '后端无响应，请确认程序已启动' : `请求出错: ${e instanceof Error ? e.message : String(e)}` })
    } finally {
      setTesting(false)
    }
  }

  if (loading) return <p className="page-muted">加载中…</p>
  if (!form) return <p className="page-muted">无法读取配置，请确认后端已启动。</p>

  const patch =
    <K extends keyof EnvSettingsView>(k: K) =>
    (v: EnvSettingsView[K]) =>
      setForm((prev) => (prev ? { ...prev, [k]: v } : prev))

  return (
    <div className="form-page">
      <h1 className="page-title">同步设置</h1>
      <p className="page-muted">
        与桌面版 <code>.env</code> 一致。密钥在列表中显示为脱敏；若不想修改某一项，请勿改动其中的「…」片段。
      </p>

      <section className="form-card">
        <label className="field">
          <span>HTTP 代理</span>
          <input type="text" value={form.HTTP_PROXY} onChange={(e) => patch('HTTP_PROXY')(e.target.value)} />
        </label>
        <label className="field">
          <span>Google Sheets 表格 ID</span>
          <input
            type="text"
            value={form.GOOGLE_SHEETS_ID}
            onChange={(e) => patch('GOOGLE_SHEETS_ID')(e.target.value)}
          />
        </label>
        <label className="field">
          <span>Gemini API Key</span>
          <input
            type="password"
            value={form.GEMINI_API_KEY}
            onChange={(e) => patch('GEMINI_API_KEY')(e.target.value)}
            autoComplete="off"
          />
        </label>
        <label className="field">
          <span>豆包 API Key</span>
          <input
            type="password"
            value={form.DOUBAO_API_KEY}
            onChange={(e) => patch('DOUBAO_API_KEY')(e.target.value)}
            autoComplete="off"
          />
        </label>
        <label className="field">
          <span>豆包 Base URL</span>
          <input type="text" value={form.DOUBAO_BASE_URL} onChange={(e) => patch('DOUBAO_BASE_URL')(e.target.value)} />
        </label>
        <label className="field">
          <span>豆包 Model Endpoint</span>
          <input
            type="text"
            value={form.DOUBAO_MODEL_ENDPOINT}
            onChange={(e) => patch('DOUBAO_MODEL_ENDPOINT')(e.target.value)}
          />
        </label>
        <div className="form-actions" style={{ marginTop: 0, marginBottom: '0.75rem' }}>
          <button type="button" className="btn primary" disabled={testing} onClick={() => void onTestLLM()}>
            {testing ? '测试中…' : '测试大模型连接'}
          </button>
        </div>
        {testStatus ? (
          <p className="page-muted" style={{ color: testStatus.ok ? '#16a34a' : '#b91c1c', whiteSpace: 'pre-wrap' }}>
            {testStatus.msg}
          </p>
        ) : null}
        <label className="field inline">
          <input type="checkbox" checked={form.SYNC_BY_DATE} onChange={(e) => patch('SYNC_BY_DATE')(e.target.checked)} />
          <span>按日期分表同步（SYNC_BY_DATE）</span>
        </label>
        <label className="field">
          <span>冲突处理（SYNC_CONFLICT_RESOLUTION）</span>
          <input
            type="text"
            value={form.SYNC_CONFLICT_RESOLUTION}
            onChange={(e) => patch('SYNC_CONFLICT_RESOLUTION')(e.target.value)}
            placeholder="keep_latest"
          />
        </label>
        <div className="form-actions">
          <button type="button" className="btn primary" disabled={saving} onClick={() => void onSave()}>
            {saving ? '保存中…' : '保存到 .env'}
          </button>
        </div>
      </section>

      <section className="form-card" style={{ marginTop: '1rem' }}>
        <h2 style={{ fontSize: '1.05rem', margin: '0 0 0.5rem' }}>Google OAuth（Sheets / Drive）</h2>
        <p className="page-muted">
          需在项目根放置 <code>client_secret.json</code>。授权后生成 <code>token.json</code>（已由{' '}
          <code>.gitignore</code> 忽略）。详情见运行日志 SSE。
        </p>
        {oauth ? (
          <pre className="wa-json-pre" style={{ maxHeight: 160 }}>
            {JSON.stringify(oauth, null, 2)}
          </pre>
        ) : (
          <p className="page-muted">无法读取 OAuth 状态</p>
        )}
        <div className="form-actions">
          <button type="button" className="btn primary" disabled={oauthBusy} onClick={() => void onOauthAuthorize()}>
            {oauthBusy ? '授权中…' : '浏览器登录（完整授权）'}
          </button>
          <button type="button" className="btn" disabled={oauthBusy} onClick={() => void onOauthRefresh()}>
            仅刷新 token
          </button>
          <button type="button" className="btn" disabled={oauthBusy} onClick={() => void loadOauth()}>
            刷新状态
          </button>
        </div>
        {oauthMsg ? <p className="page-muted" style={{ marginTop: '0.5rem', color: oauthMsg.includes('成功') || oauthMsg.includes('✓') ? '#16a34a' : oauthMsg.includes('授权中') ? undefined : '#b91c1c' }}>{oauthMsg}</p> : null}
      </section>
    </div>
  )
}

import { useEffect, useState } from 'react'

import { API_BASE } from '../config/api'

import './FormPage.css'

export default function AiStrategyPage() {
  const [prompt, setPrompt] = useState('')
  const [source, setSource] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    let cancelled = false
    void (async () => {
      try {
        const r = await fetch(`${API_BASE}/api/ai/prompt`)
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const j = (await r.json()) as { content: string; source: string }
        if (!cancelled) {
          setPrompt(j.content)
          setSource(j.source)
        }
      } catch {
        if (!cancelled) setPrompt('')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  async function onSave() {
    setSaving(true)
    try {
      const r = await fetch(`${API_BASE}/api/ai/prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: prompt }),
      })
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      const j = (await r.json()) as { path?: string }
      window.alert(`已保存${j.path ? ` → ${j.path}` : ''}`)
    } catch (e) {
      window.alert(e instanceof Error ? e.message : String(e))
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="form-page">
        <h1 className="page-title">AI 策略</h1>
        <p className="loading-text">加载中</p>
      </div>
    )
  }

  return (
    <div className="form-page">
      <h1 className="page-title">AI 策略</h1>
      <p className="page-muted">
        当前来源：<code>{source || '—'}</code>。保存后写入项目根目录 <code>user_ai_prompt.txt</code>，供关键词 AI 生成使用。
      </p>
      <section className="form-card">
        <label className="field">
          <span>关键词生成提示词模板</span>
          <textarea
            className="prompt-area"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            spellCheck={false}
            placeholder="在此输入 AI 关键词生成提示词模板..."
          />
        </label>
        <div className="form-actions">
          <button
            type="button"
            className="btn primary"
            disabled={saving || !prompt.trim()}
            onClick={() => void onSave()}
          >
            {saving ? (
              <>
                <span className="spinner" />
                保存中…
              </>
            ) : (
              '保存'
            )}
          </button>
        </div>
      </section>
    </div>
  )
}

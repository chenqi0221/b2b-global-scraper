import { useEffect, useMemo, useRef, useState } from 'react'

import { KeywordLibraryModal } from '../components/KeywordLibraryModal'
import { API_BASE } from '../config/api'
import { isTauri, pickCsvFile, pickDirectory, pickDirectoryBrowser, revealPath } from '../lib/tauriBridge'
import { useScraperStore } from '../stores/scraperStore'
import type { GeoData, IndustryMap, LogEventPayload, LocationModel } from '../types/api'

import './EnginePage.css'

function pathJoinRoot(root: string, rel: string): string {
  const sep = root.includes('\\') ? '\\' : '/'
  return `${root.replace(/[/\\]$/, '')}${sep}${rel.replace(/^[/\\]/, '')}`
}

export default function EnginePage() {
  const [geo, setGeo] = useState<GeoData | null>(null)
  const [industries, setIndustries] = useState<IndustryMap | null>(null)
  const [geoMode, setGeoMode] = useState<'select' | 'manual'>('select')
  const [continent, setContinent] = useState('')
  const [country, setCountry] = useState('')
  const [city, setCity] = useState('')
  const [district, setDistrict] = useState('所有')
  const [manualAddress, setManualAddress] = useState('')
  const [category, setCategory] = useState('')
  const [kwText, setKwText] = useState('')
  const [concurrency, setConcurrency] = useState(3)
  const [logs, setLogs] = useState<string[]>([])
  const [kwLibOpen, setKwLibOpen] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<string | null>(null)
  const [aiSeed, setAiSeed] = useState('')
  const [aiNum, setAiNum] = useState(7)
  const [aiBusy, setAiBusy] = useState(false)
  const [aiMsg, setAiMsg] = useState<string | null>(null)
  const [generatedPairs, setGeneratedPairs] = useState<{ en: string; zh: string }[]>([])
  const logRef = useRef<HTMLPreElement>(null)
  const syncCsvInputRef = useRef<HTMLInputElement>(null)

  const fetchStatus = useScraperStore((s) => s.fetchStatus)
  const fetchProjectRoot = useScraperStore((s) => s.fetchProjectRoot)
  const projectRoot = useScraperStore((s) => s.projectRoot)
  const status = useScraperStore((s) => s.status)
  const statusError = useScraperStore((s) => s.statusError)

  useEffect(() => {
    let cancelled = false
    void (async () => {
      try {
        const [gr, ir] = await Promise.all([
          fetch(`${API_BASE}/api/meta/geography`),
          fetch(`${API_BASE}/api/meta/industries`),
        ])
        if (!gr.ok || !ir.ok) return
        const g = (await gr.json()) as GeoData
        const ind = (await ir.json()) as IndustryMap
        if (!cancelled) {
          setGeo(g)
          setIndustries(ind)
        }
      } catch {
        /* 元数据加载失败时仍可使用手动地址 */
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    const id = window.setInterval(() => void fetchStatus(), 2000)
    void fetchStatus()
    void fetchProjectRoot()
    return () => window.clearInterval(id)
  }, [fetchStatus, fetchProjectRoot])

  useEffect(() => {
    const es = new EventSource(`${API_BASE}/api/logs/stream`)
    const onLog = (ev: MessageEvent) => {
      try {
        const p = JSON.parse(ev.data) as LogEventPayload
        const line = `[${p.level}] ${p.message}`
        setLogs((prev) => [...prev.slice(-800), line])
      } catch {
        /* ignore */
      }
    }
    es.addEventListener('log', onLog as EventListener)
    return () => {
      es.removeEventListener('log', onLog as EventListener)
      es.close()
    }
  }, [])

  useEffect(() => {
    const el = logRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [logs])

  const continents = useMemo(() => (geo ? Object.keys(geo) : []), [geo])
  const countries = useMemo(() => {
    if (!geo || !continent) return []
    return Object.keys(geo[continent] ?? {})
  }, [geo, continent])

  const cities = useMemo(() => {
    if (!geo || !continent || !country) return []
    return Object.keys(geo[continent]?.[country]?.cities ?? {})
  }, [geo, continent, country])

  const districtOptions = useMemo(() => {
    if (!geo || !continent || !country || !city) return ['所有']
    const list = geo[continent]?.[country]?.cities?.[city] ?? []
    return ['所有', ...list.map((d) => `${d.en} (${d.zh})`)]
  }, [geo, continent, country, city])

  useEffect(() => {
    if (!districtOptions.includes(district)) setDistrict('所有')
  }, [districtOptions, district])

  const onCategoryChange = (cat: string) => {
    setCategory(cat)
    if (!industries || !cat) return
    const words = industries[cat]
    if (words?.length) setKwText(words.join('\n'))
  }

  async function resolveLocation(): Promise<LocationModel | null> {
    if (geoMode === 'manual') {
      const r = await fetch(`${API_BASE}/api/meta/resolve-location`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'manual', manual_address: manualAddress }),
      })
      if (!r.ok) return null
      return (await r.json()) as LocationModel
    }
    const r = await fetch(`${API_BASE}/api/meta/resolve-location`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mode: 'select',
        continent,
        country,
        city,
        district,
      }),
    })
    if (!r.ok) return null
    return (await r.json()) as LocationModel
  }

  async function onStart() {
    const kws = kwText
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean)
    if (!kws.length) {
      window.alert('请输入或选择行业关键词')
      return
    }
    const loc = await resolveLocation()
    if (!loc) {
      window.alert('地理位置解析失败，请检查级联选项或手动地址')
      return
    }
    const r = await fetch(`${API_BASE}/api/scraper/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keywords: kws, location: loc, concurrency }),
    })
    if (!r.ok) {
      window.alert('启动失败')
      return
    }
    void fetchStatus()
  }

  async function onStop() {
    await fetch(`${API_BASE}/api/scraper/stop`, { method: 'POST' })
    void fetchStatus()
  }

  async function postSyncByPath(filePath: string) {
    const r = await fetch(`${API_BASE}/api/sync/file`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath }),
    })
    const j = (await r.json().catch(() => ({}))) as { ok?: boolean; detail?: string }
    if (!r.ok) {
      window.alert(typeof j.detail === 'string' ? j.detail : `同步失败 HTTP ${r.status}`)
      return
    }
    window.alert(j.ok ? '已提交同步任务' : '同步未完成')
  }

  async function postSyncUpload(file: File) {
    const fd = new FormData()
    fd.append('file', file)
    const r = await fetch(`${API_BASE}/api/sync/upload-csv`, { method: 'POST', body: fd })
    const j = (await r.json().catch(() => ({}))) as { ok?: boolean; detail?: string }
    if (!r.ok) {
      window.alert(typeof j.detail === 'string' ? j.detail : `上传同步失败 HTTP ${r.status}`)
      return
    }
    window.alert(j.ok ? '上传并同步完成' : '同步未完成')
  }

  async function onSyncSingleCsv() {
    if (isTauri()) {
      const p = await pickCsvFile()
      if (!p) return
      await postSyncByPath(p)
      return
    }
    syncCsvInputRef.current?.click()
  }

  async function onSyncCsvPicked(ev: React.ChangeEvent<HTMLInputElement>) {
    const f = ev.target.files?.[0]
    ev.target.value = ''
    if (!f) return
    await postSyncUpload(f)
  }

  async function onAggregateSync() {
    if (isTauri()) {
      const dir = await pickDirectory()
      if (!dir) return
      const r = await fetch(`${API_BASE}/api/sync/aggregate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dir_path: dir,
          target_title: 'lengdangb2b',
          by_date: false,
          conflict_resolution: 'keep_latest',
        }),
      })
      const j = (await r.json().catch(() => ({}))) as { ok?: boolean; detail?: string }
      if (!r.ok) {
        window.alert(typeof j.detail === 'string' ? j.detail : `汇总失败 HTTP ${r.status}`)
        return
      }
      window.alert(j.ok ? '汇总同步完成' : '汇总同步未完成')
      return
    }

    /* 浏览器模式：弹出目录选择器，自动上传 CSV 并汇总 */
    const files = await pickDirectoryBrowser()
    if (files.length === 0) return
    const fd = new FormData()
    for (const f of files) {
      if (f.name.endsWith('.csv')) fd.append('files', f)
    }
    if (!fd.has('files')) {
      window.alert('选择的目录中没有 CSV 文件')
      return
    }
    fd.append('target_title', 'lengdangb2b')
    const r = await fetch(`${API_BASE}/api/sync/aggregate-files`, { method: 'POST', body: fd })
    const j = (await r.json().catch(() => ({}))) as { ok?: boolean; detail?: string }
    if (!r.ok) {
      window.alert(typeof j.detail === 'string' ? j.detail : `汇总失败 HTTP ${r.status}`)
      return
    }
    window.alert(j.ok ? '汇总同步完成' : '汇总同步未完成')
  }

  async function onTestProxy() {
    setTesting(true)
    setTestResult(null)
    try {
      const r = await fetch(`${API_BASE}/api/system/test-proxy`, { method: 'POST' })
      const j = (await r.json().catch(() => ({}))) as { ok?: boolean }
      setTestResult(j.ok ? '代理测试成功 ✓' : '代理测试失败，请检查运行日志')
    } catch (e) {
      setTestResult(e instanceof TypeError && e.message === 'Failed to fetch'
        ? '后端无响应，请确认程序已启动'
        : `测试出错: ${e instanceof Error ? e.message : String(e)}`)
    } finally {
      setTesting(false)
    }
  }

  async function onRevealOutput() {
    await fetchProjectRoot()
    const pr = useScraperStore.getState().projectRoot
    const out = status?.output_dir
    const fallback = pr ? pathJoinRoot(pr, 'Downloads') : ''
    const target = out || fallback
    if (!target) {
      window.alert('暂无输出路径，请先启动一次抓取或确认后端正常')
      return
    }
    try {
      await revealPath(target)
    } catch (e) {
      window.alert(e instanceof Error ? e.message : String(e))
    }
  }

  async function onAiGenerate() {
    if (!aiSeed.trim()) {
      window.alert('请输入 AI 种子 / 行业描述')
      return
    }
    setAiBusy(true)
    setAiMsg(null)
    setGeneratedPairs([])
    try {
      const r = await fetch(`${API_BASE}/api/keywords/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed: aiSeed.trim(), num: aiNum }),
      })
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      const j = (await r.json()) as { keywords: { en: string; zh: string }[] }
      const kw = j.keywords ?? []
      setGeneratedPairs(kw)
      const lines = kw.map((k) => k.en).join('\n')
      setKwText((prev) => {
        const existing = new Set(prev.split('\n').map((s) => s.trim()).filter(Boolean))
        const newLines = lines.split('\n').filter((l) => !existing.has(l))
        return prev + (prev && newLines.length ? '\n' : '') + newLines.join('\n')
      })
      setAiMsg(`生成了 ${kw.length} 个关键词`)
    } catch (e) {
      setAiMsg(e instanceof Error ? e.message : '生成失败')
    } finally {
      setAiBusy(false)
    }
  }

  async function onSaveToLibrary() {
    if (!generatedPairs.length) return
    setAiBusy(true)
    try {
      const r = await fetch(`${API_BASE}/api/keywords/library/append`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generatedPairs),
      })
      const j = (await r.json()) as { ok?: boolean; added?: number }
      setAiMsg(j.ok ? `已存入种子库: ${j.added ?? generatedPairs.length} 条` : '存入失败')
    } catch (e) {
      setAiMsg(e instanceof Error ? e.message : '存入失败')
    } finally {
      setAiBusy(false)
    }
  }

  const running = status?.is_running ?? false

  return (
    <div className="engine-page">
      <h1 className="page-title">获客引擎</h1>
      {statusError ? <p className="engine-banner error">状态同步失败：{statusError}</p> : null}

      <section className="engine-cards">
        <div className="stat-card">
          <div className="stat-label">今日已抓取</div>
          <div className="stat-value">{status?.total_found ?? '—'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">包含邮箱数</div>
          <div className="stat-value">{status?.email_found ?? '—'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">已同步云端</div>
          <div className="stat-value">{status?.synced_count ?? '—'}</div>
        </div>
      </section>

      <div className="engine-grid">
        <section className="engine-panel">
          <h2>关键词</h2>
          <label className="field">
            <span>行业模板</span>
            <select
              value={category}
              onChange={(e) => onCategoryChange(e.target.value)}
              disabled={!industries}
            >
              <option value="">选择行业…</option>
              {industries
                ? Object.keys(industries).map((k) => (
                    <option key={k} value={k}>
                      {k}
                    </option>
                  ))
                : null}
            </select>
          </label>
          <label className="field">
            <span>关键词列表（每行一个）</span>
            <textarea
              className="kw-area"
              value={kwText}
              onChange={(e) => setKwText(e.target.value)}
              rows={10}
              spellCheck={false}
            />
          </label>
          <div className="engine-inline-actions">
            <button type="button" className="btn" onClick={() => setKwLibOpen(true)}>
              关键词库…
            </button>
          </div>
          <div className="engine-ai-gen">
            <input
              placeholder="AI 种子词"
              value={aiSeed}
              onChange={(e) => setAiSeed(e.target.value)}
              disabled={aiBusy}
            />
            <input
              type="number"
              min={1}
              value={aiNum}
              onChange={(e) => setAiNum(Number(e.target.value) || 7)}
              disabled={aiBusy}
              style={{ width: 70 }}
            />
            <button type="button" className="btn" disabled={aiBusy} onClick={() => void onAiGenerate()}>
              {aiBusy ? 'AI 生成中…' : 'AI 生成'}
            </button>
            {generatedPairs.length > 0 && (
              <button type="button" className="btn primary" disabled={aiBusy} onClick={() => void onSaveToLibrary()}>
                存入种子库
              </button>
            )}
          </div>
          {aiMsg ? <p className={`engine-hint ${(aiMsg.startsWith('生成了') || aiMsg.startsWith('已存入')) ? 'engine-success' : 'engine-error'}`}>{aiMsg}</p> : null}
          <label className="field inline">
            <span>并发数</span>
            <input
              type="number"
              min={1}
              max={10}
              value={concurrency}
              onChange={(e) => setConcurrency(Number(e.target.value) || 1)}
            />
          </label>
        </section>

        <section className="engine-panel">
          <h2>地理位置</h2>
          <div className="geo-mode">
            <label>
              <input
                type="radio"
                name="geo"
                checked={geoMode === 'select'}
                onChange={() => setGeoMode('select')}
              />
              预设位置
            </label>
            <label>
              <input
                type="radio"
                name="geo"
                checked={geoMode === 'manual'}
                onChange={() => setGeoMode('manual')}
              />
              手动地址
            </label>
          </div>

          {geoMode === 'select' ? (
            <div className="cascade">
              <label className="field">
                <span>大洲</span>
                <select
                  value={continent}
                  onChange={(e) => {
                    setContinent(e.target.value)
                    setCountry('')
                    setCity('')
                    setDistrict('所有')
                  }}
                >
                  <option value="">请选择</option>
                  {continents.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>国家</span>
                <select
                  value={country}
                  onChange={(e) => {
                    setCountry(e.target.value)
                    setCity('')
                    setDistrict('所有')
                  }}
                  disabled={!continent}
                >
                  <option value="">请选择</option>
                  {countries.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>城市</span>
                <select
                  value={city}
                  onChange={(e) => {
                    setCity(e.target.value)
                    setDistrict('所有')
                  }}
                  disabled={!country}
                >
                  <option value="">请选择</option>
                  {cities.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>区域</span>
                <select value={district} onChange={(e) => setDistrict(e.target.value)} disabled={!city}>
                  {districtOptions.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          ) : (
            <label className="field">
              <span>地址（英文优先；中文完整功能将接翻译 API）</span>
              <input
                type="text"
                value={manualAddress}
                onChange={(e) => setManualAddress(e.target.value)}
                placeholder="例如 Dubai Marina"
              />
            </label>
          )}

          <div className="engine-actions">
            <button type="button" className="btn primary" disabled={running} onClick={() => void onStart()}>
              开始获客
            </button>
            <button type="button" className="btn danger" disabled={!running} onClick={() => void onStop()}>
              停止
            </button>
          </div>
          {status?.output_dir ? (
            <p className="engine-hint">
              输出目录：<code>{status.output_dir}</code>
            </p>
          ) : projectRoot ? (
            <p className="engine-hint">
              项目根：<code>{projectRoot}</code>
            </p>
          ) : null}
        </section>
      </div>

      <section className="engine-log">
        <h2>运行日志</h2>
        <pre ref={logRef} className="log-pre">
          {logs.length ? logs.join('\n') : '（等待后端推送…）'}
        </pre>
      </section>

      <section className="engine-footer-actions">
        <p className="engine-hint">快捷操作（同步依赖已配置的 Google Sheets 凭证）</p>
        <input ref={syncCsvInputRef} type="file" accept=".csv" hidden onChange={(e) => void onSyncCsvPicked(e)} />
        <div className="engine-footer-btns">
          <button type="button" className="btn" onClick={() => void onSyncSingleCsv()}>
            同步单个 CSV
          </button>
          <button type="button" className="btn" onClick={() => void onAggregateSync()}>
            汇总目录同步
          </button>
          <button type="button" className="btn" disabled={testing} onClick={() => void onTestProxy()}>
            测代理
          </button>
          <button type="button" className="btn" onClick={() => void onRevealOutput()}>
            打开输出 / 下载
          </button>
        </div>
        {testing ? <p className="engine-hint">正在测试代理连通性…</p> : testResult ? <p className={`engine-hint ${testResult.includes('成功') ? 'engine-success' : 'engine-error'}`}>{testResult}</p> : null}
      </section>

      <KeywordLibraryModal
        open={kwLibOpen}
        onClose={() => setKwLibOpen(false)}
        onApplyToEngine={(lines) => setKwText(lines)}
      />
    </div>
  )
}

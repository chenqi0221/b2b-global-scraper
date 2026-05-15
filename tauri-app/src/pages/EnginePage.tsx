import { useEffect, useMemo, useRef, useState } from 'react'

import { KeywordLibraryModal } from '../components/KeywordLibraryModal'
import { API_BASE } from '../config/api'
import { isTauri, pickCsvFile, pickDirectory, pickDirectoryBrowser, revealPath } from '../lib/tauriBridge'
import { useEngineStore } from '../stores/engineStore'
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
  const [logs, setLogs] = useState<string[]>([])
  const [kwLibOpen, setKwLibOpen] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<string | null>(null)
  const [aiBusy, setAiBusy] = useState(false)
  const [aiMsg, setAiMsg] = useState<string | null>(null)
  const [generatedPairs, setGeneratedPairs] = useState<{ en: string; zh: string }[]>([])
  const logRef = useRef<HTMLPreElement>(null)
  const syncCsvInputRef = useRef<HTMLInputElement>(null)

  // 持久化状态
  const geoMode = useEngineStore((s) => s.geoMode)
  const continent = useEngineStore((s) => s.continent)
  const country = useEngineStore((s) => s.country)
  const city = useEngineStore((s) => s.city)
  const district = useEngineStore((s) => s.district)
  const manualAddress = useEngineStore((s) => s.manualAddress)
  const category = useEngineStore((s) => s.category)
  const kwText = useEngineStore((s) => s.kwText)
  const concurrency = useEngineStore((s) => s.concurrency)
  const aiSeed = useEngineStore((s) => s.aiSeed)
  const aiNum = useEngineStore((s) => s.aiNum)

  const setGeoMode = useEngineStore((s) => s.setGeoMode)
  const setContinent = useEngineStore((s) => s.setContinent)
  const setCountry = useEngineStore((s) => s.setCountry)
  const setCity = useEngineStore((s) => s.setCity)
  const setDistrict = useEngineStore((s) => s.setDistrict)
  const setManualAddress = useEngineStore((s) => s.setManualAddress)
  const setCategory = useEngineStore((s) => s.setCategory)
  const setKwText = useEngineStore((s) => s.setKwText)
  const setConcurrency = useEngineStore((s) => s.setConcurrency)
  const setAiSeed = useEngineStore((s) => s.setAiSeed)
  const setAiNum = useEngineStore((s) => s.setAiNum)

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
    return ['所有', ...list]
  }, [geo, continent, country, city])

  useEffect(() => {
    if (!districtOptions.includes(district)) setDistrict('所有')
  }, [districtOptions, district, setDistrict])

  const onCategoryChange = (cat: string) => {
    setCategory(cat)
    if (!industries || !cat) return
    const words = industries[cat]
    if (words?.length) {
      const lines = words.map((w) => `${w.zh} | ${w.en}`)
      setKwText(lines.join('\n'))
    }
  }

  /** 获取国家的英文名称 */
  const getCountryEn = (countryZh: string): string => {
    if (!geo || !continent) return countryZh
    return geo[continent]?.[countryZh]?.en ?? countryZh
  }

  /** 获取城市的英文名称（城市名本身就是中文，需要映射） */
  const getCityEn = (cityZh: string): string => {
    // 后端 location_resolve.py 会从 body.city 中提取括号内的英文
    // 但我们的数据格式是 { "上海": [...] }，没有英文
    // 所以需要手动映射常见城市
    const cityMap: Record<string, string> = {
      '上海': 'Shanghai', '北京': 'Beijing', '深圳': 'Shenzhen', '广州': 'Guangzhou',
      '杭州': 'Hangzhou', '成都': 'Chengdu', '重庆': 'Chongqing', '武汉': 'Wuhan',
      '南京': 'Nanjing', '天津': 'Tianjin', '苏州': 'Suzhou', '东莞': 'Dongguan',
      '佛山': 'Foshan', '宁波': 'Ningbo', '厦门': 'Xiamen',
      '东京': 'Tokyo', '大阪': 'Osaka', '名古屋': 'Nagoya', '横滨': 'Yokohama', '福冈': 'Fukuoka',
      '首尔': 'Seoul', '釜山': 'Busan', '仁川': 'Incheon',
      '孟买': 'Mumbai', '德里': 'Delhi', '班加罗尔': 'Bangalore', '钦奈': 'Chennai', '海得拉巴': 'Hyderabad', '浦那': 'Pune',
      '台北': 'Taipei', '新北': 'New Taipei', '台中': 'Taichung', '高雄': 'Kaohsiung',
      '伦敦': 'London', '曼彻斯特': 'Manchester', '伯明翰': 'Birmingham', '格拉斯哥': 'Glasgow', '利兹': 'Leeds',
      '柏林': 'Berlin', '慕尼黑': 'Munich', '法兰克福': 'Frankfurt', '汉堡': 'Hamburg', '斯图加特': 'Stuttgart', '杜塞尔多夫': 'Dusseldorf',
      '巴黎': 'Paris', '里昂': 'Lyon', '马赛': 'Marseille',
      '米兰': 'Milan', '罗马': 'Rome',
      '马德里': 'Madrid', '巴塞罗那': 'Barcelona', '瓦伦西亚': 'Valencia', '塞维利亚': 'Seville',
      '阿姆斯特丹': 'Amsterdam', '鹿特丹': 'Rotterdam', '海牙': 'The Hague',
      '布鲁塞尔': 'Brussels', '安特卫普': 'Antwerp',
      '苏黎世': 'Zurich', '日内瓦': 'Geneva', '巴塞尔': 'Basel',
      '维也纳': 'Vienna', '萨尔茨堡': 'Salzburg',
      '华沙': 'Warsaw', '克拉科夫': 'Krakow',
      '布拉格': 'Prague',
      '布达佩斯': 'Budapest',
      '哥本哈根': 'Copenhagen',
      '斯德哥尔摩': 'Stockholm', '哥德堡': 'Gothenburg',
      '赫尔辛基': 'Helsinki',
      '奥斯陆': 'Oslo',
      '都柏林': 'Dublin',
      '里斯本': 'Lisbon',
      '雅典': 'Athens',
      '伊斯坦布尔': 'Istanbul', '安卡拉': 'Ankara', '伊兹密尔': 'Izmir',
      '迪拜': 'Dubai', '阿布扎比': 'Abu Dhabi',
      '利雅得': 'Riyadh', '吉达': 'Jeddah',
      '多哈': 'Doha',
      '科威特城': 'Kuwait City',
      '马斯喀特': 'Muscat',
      '麦纳麦': 'Manama',
      '安曼': 'Amman',
      '贝鲁特': 'Beirut',
      '特拉维夫': 'Tel Aviv', '耶路撒冷': 'Jerusalem',
      '开罗': 'Cairo', '亚历山大': 'Alexandria',
      '约翰内斯堡': 'Johannesburg', '开普敦': 'Cape Town', '德班': 'Durban',
      '拉各斯': 'Lagos',
      '内罗毕': 'Nairobi',
      '卡萨布兰卡': 'Casablanca',
      '突尼斯': 'Tunis',
      '阿尔及尔': 'Algiers',
      '悉尼': 'Sydney', '墨尔本': 'Melbourne', '布里斯班': 'Brisbane', '珀斯': 'Perth', '阿德莱德': 'Adelaide',
      '奥克兰': 'Auckland', '惠灵顿': 'Wellington', '基督城': 'Christchurch',
      '纽约': 'New York', '洛杉矶': 'Los Angeles', '芝加哥': 'Chicago', '休斯顿': 'Houston', '旧金山': 'San Francisco',
      '西雅图': 'Seattle', '波士顿': 'Boston', '迈阿密': 'Miami', '亚特兰大': 'Atlanta', '达拉斯': 'Dallas',
      '华盛顿': 'Washington DC', '费城': 'Philadelphia', '丹佛': 'Denver', '凤凰城': 'Phoenix', '底特律': 'Detroit',
      '多伦多': 'Toronto', '温哥华': 'Vancouver', '蒙特利尔': 'Montreal', '卡尔加里': 'Calgary',
      '墨西哥城': 'Mexico City', '瓜达拉哈拉': 'Guadalajara', '蒙特雷': 'Monterrey',
      '圣保罗': 'Sao Paulo', '里约热内卢': 'Rio de Janeiro', '巴西利亚': 'Brasilia',
      '布宜诺斯艾利斯': 'Buenos Aires',
      '圣地亚哥': 'Santiago',
      '利马': 'Lima',
      '波哥大': 'Bogota',
      '加拉加斯': 'Caracas',
      '蒙得维的亚': 'Montevideo',
      '圣克鲁斯': 'Santa Cruz',
      '亚松森': 'Asuncion',
      '巴拿马城': 'Panama City',
      '圣何塞': 'San Jose',
      '危地马拉城': 'Guatemala City',
      '圣萨尔瓦多': 'San Salvador',
      '马那瓜': 'Managua',
      '圣佩德罗苏拉': 'San Pedro Sula',
      '圣多明各': 'Santo Domingo',
      '哈瓦那': 'Havana',
      '圣胡安': 'San Juan',
      '圣乔治': 'St. George\'s',
      '布里奇敦': 'Bridgetown',
      '太子港': 'Port-au-Prince',
      '金斯敦': 'Kingston',
      '拿骚': 'Nassau',
      '新加坡': 'Singapore',
      '曼谷': 'Bangkok', '清迈': 'Chiang Mai',
      '吉隆坡': 'Kuala Lumpur', '槟城': 'Penang',
      '雅加达': 'Jakarta', '泗水': 'Surabaya',
      '马尼拉': 'Manila', '宿务': 'Cebu',
      '河内': 'Hanoi', '胡志明市': 'Ho Chi Minh City',
      '金边': 'Phnom Penh',
      '万象': 'Vientiane',
      '仰光': 'Yangon',
      '达卡': 'Dhaka',
      '科伦坡': 'Colombo',
      '加德满都': 'Kathmandu',
      '伊斯兰堡': 'Islamabad', '卡拉奇': 'Karachi', '拉合尔': 'Lahore',
      '新德里': 'New Delhi',
      '科钦': 'Kochi',
      '阿姆利则': 'Amritsar',
      '斋浦尔': 'Jaipur',
      '加尔各答': 'Kolkata',
      '塔什干': 'Tashkent', '阿拉木图': 'Almaty', '阿斯塔纳': 'Astana',
      '巴库': 'Baku',
      '第比利斯': 'Tbilisi',
      '埃里温': 'Yerevan',
      '比什凯克': 'Bishkek',
      '杜尚别': 'Dushanbe',
      '阿什哈巴德': 'Ashgabat',
    }
    return cityMap[cityZh] ?? cityZh
  }

  /** 获取区域的英文名称 */
  const getDistrictEn = (districtZh: string): string => {
    if (districtZh === '所有') return getCityEn(city)
    // 区域目前都是中文，直接返回中文（Google Maps 支持中文搜索区域）
    return districtZh
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
    // 传给后端的是英文
    const countryEn = getCountryEn(country)
    const cityEn = getCityEn(city)
    const districtEn = getDistrictEn(district)
    const r = await fetch(`${API_BASE}/api/meta/resolve-location`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mode: 'select',
        continent,
        country: countryEn,
        city: cityEn,
        district: districtEn,
      }),
    })
    if (!r.ok) return null
    return (await r.json()) as LocationModel
  }

  /** 从显示文本中提取英文关键词 */
  const extractEnglishKeywords = (text: string): string[] => {
    return text
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean)
      .map((line) => {
        const parts = line.split('|')
        return parts.length >= 2 ? parts[parts.length - 1].trim() : line.trim()
      })
      .filter(Boolean)
  }

  async function onStart() {
    const kws = extractEnglishKeywords(kwText)
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
      const lines = kw.map((k) => `${k.zh} | ${k.en}`).join('\n')
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

  async function onSaveCurrentToLibrary() {
    const lines = kwText
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean)
    if (!lines.length) {
      window.alert('关键词列表为空')
      return
    }
    const pairs = lines.map((line) => {
      const parts = line.split('|')
      if (parts.length >= 2) {
        return { en: parts[parts.length - 1].trim(), zh: parts[0].trim() }
      }
      return { en: line, zh: '' }
    })
    try {
      const r = await fetch(`${API_BASE}/api/keywords/library/append`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pairs),
      })
      const j = (await r.json()) as { ok?: boolean; added?: number }
      window.alert(j.ok ? `已保存 ${j.added ?? pairs.length} 条到关键词库` : '保存失败')
    } catch (e) {
      window.alert(e instanceof Error ? e.message : '保存失败')
    }
  }

  function onClearKeywords() {
    if (!kwText.trim()) return
    if (window.confirm('确定要清空关键词列表吗？')) {
      setKwText('')
    }
  }

  const running = status?.is_running ?? false

  return (
    <div className="engine-page">
      <h1 className="page-title">获客引擎</h1>
      {statusError ? <p className="engine-banner error">状态同步失败：{statusError}</p> : null}

      <section className="engine-stats">
        <div className="engine-stat-card">
          <div className="engine-stat-label">今日已抓取</div>
          <div className="engine-stat-value">{status?.total_found ?? '—'}</div>
        </div>
        <div className="engine-stat-card">
          <div className="engine-stat-label">包含邮箱数</div>
          <div className="engine-stat-value">{status?.email_found ?? '—'}</div>
        </div>
        <div className="engine-stat-card">
          <div className="engine-stat-label">已同步云端</div>
          <div className="engine-stat-value">{status?.synced_count ?? '—'}</div>
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
          <div className="kw-toolbar">
            <button type="button" className="btn kw-lib-btn" onClick={() => setKwLibOpen(true)}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
              关键词库
            </button>
            <button type="button" className="btn kw-save-btn" onClick={() => void onSaveCurrentToLibrary()}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
              保存到关键词库
            </button>
            <button type="button" className="btn kw-clear-btn" onClick={onClearKeywords}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              清空列表
            </button>
          </div>
          <div className="ai-gen-card">
            <div className="ai-gen-header">
              <span className="ai-gen-title">AI 关键词生成</span>
              <span className="ai-gen-desc">输入种子词，AI 自动扩展相关关键词</span>
            </div>
            <div className="ai-gen-body">
              <input
                className="ai-seed-input"
                placeholder="输入种子词，如：浴室柜、LED 灯、机械零件…"
                value={aiSeed}
                onChange={(e) => setAiSeed(e.target.value)}
                disabled={aiBusy}
              />
              <div className="ai-gen-actions-row">
                <div className="ai-gen-quantity">
                  <input
                    type="number"
                    min={1}
                    max={50}
                    value={aiNum}
                    onChange={(e) => setAiNum(Number(e.target.value) || 7)}
                    disabled={aiBusy}
                    title="生成数量"
                  />
                </div>
                <button type="button" className="btn ai-gen-btn" disabled={aiBusy || !aiSeed.trim()} onClick={() => void onAiGenerate()}>
                  {aiBusy ? (
                    <>
                      <span className="ai-spinner" />
                      生成中…
                    </>
                  ) : (
                    <>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v18"/><path d="M3 12h18"/></svg>
                      AI 生成
                    </>
                  )}
                </button>
                {generatedPairs.length > 0 && (
                  <button type="button" className="btn primary ai-save-btn" disabled={aiBusy} onClick={() => void onSaveToLibrary()}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                    存入种子库
                  </button>
                )}
              </div>
            </div>
            {aiMsg ? (
              <div className={`ai-gen-toast ${(aiMsg.startsWith('生成了') || aiMsg.startsWith('已存入')) ? 'ai-toast-success' : 'ai-toast-error'}`}>
                <span className="ai-toast-icon">{(aiMsg.startsWith('生成了') || aiMsg.startsWith('已存入')) ? '✓' : '✗'}</span>
                {aiMsg}
              </div>
            ) : null}
          </div>
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
            <label className="field inline concurrency-field">
              <span>并发数</span>
              <input
                type="number"
                min={1}
                max={10}
                value={concurrency}
                onChange={(e) => setConcurrency(Number(e.target.value) || 1)}
              />
            </label>
          </div>
          {status?.output_dir ? (
            <div className="path-box">
              <span className="path-label">输出目录</span>
              <code className="path-value">{status.output_dir}</code>
              <button type="button" className="btn path-open-btn" onClick={() => void revealPath(status.output_dir!)}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                打开
              </button>
            </div>
          ) : projectRoot ? (
            <div className="path-box">
              <span className="path-label">项目根</span>
              <code className="path-value">{projectRoot}</code>
              <button type="button" className="btn path-open-btn" onClick={() => void revealPath(projectRoot)}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                打开
              </button>
            </div>
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

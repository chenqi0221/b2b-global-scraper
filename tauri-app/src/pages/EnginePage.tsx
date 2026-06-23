import { useEffect, useMemo, useRef, useState } from 'react'

import { KeywordLibraryModal } from '../components/KeywordLibraryModal'
import { ProgressPanel } from '../components/ProgressPanel'
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
  const headless = useEngineStore((s) => s.headless)
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
  const setHeadless = useEngineStore((s) => s.setHeadless)
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

  const pollIntervalMs = useScraperStore((s) => s.pollIntervalMs)

  useEffect(() => {
    const id = window.setInterval(() => void fetchStatus(), pollIntervalMs)
    void fetchStatus()
    void fetchProjectRoot()
    return () => window.clearInterval(id)
  }, [fetchStatus, fetchProjectRoot, pollIntervalMs])

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
    // 后端 location_resolve.py 期望 city 是纯英文或带括号格式
    // 数据格式是 "广州 (Guangzhou)", 先尝试提取括号内的英文
    const match = cityZh.match(/\(([^)]+)\)/)
    if (match) return match[1]
    // 兜底：手动映射表
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
      '圣乔治': "St. George's",
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
    // 常见区域中文→英文映射（Google Maps 搜索需要英文）
    // 注意：不同城市可能有同名区域，这里统一用拼音，Google Maps 会结合城市名自动定位
    const districtMap: Record<string, string> = {
      '海淀区': 'Haidian', '朝阳区': 'Chaoyang', '东城区': 'Dongcheng', '西城区': 'Xicheng',
      '丰台区': 'Fengtai', '石景山区': 'Shijingshan', '门头沟区': 'Mentougou', '房山区': 'Fangshan',
      '通州区': 'Tongzhou', '顺义区': 'Shunyi', '昌平区': 'Changping', '大兴区': 'Daxing',
      '怀柔区': 'Huairou', '平谷区': 'Pinggu', '密云区': 'Miyun', '延庆区': 'Yanqing',
      '黄浦区': 'Huangpu', '徐汇区': 'Xuhui', '长宁区': 'Changning', '静安区': "Jing'an",
      '普陀区': 'Putuo', '虹口区': 'Hongkou', '杨浦区': 'Yangpu', '闵行区': 'Minhang',
      '宝山区': 'Baoshan', '嘉定区': 'Jiading', '浦东新区': 'Pudong', '金山区': 'Jinshan',
      '松江区': 'Songjiang', '青浦区': 'Qingpu', '奉贤区': 'Fengxian', '崇明区': 'Chongming',
      '天河区': 'Tianhe', '越秀区': 'Yuexiu', '海珠区': 'Haizhu', '荔湾区': 'Liwan',
      '白云区': 'Baiyun', '黄埔区': 'Huangpu', '番禺区': 'Panyu', '花都区': 'Huadu',
      '南沙区': 'Nansha', '从化区': 'Conghua', '增城区': 'Zengcheng',
      '福田区': 'Futian', '罗湖区': 'Luohu', '南山区': 'Nanshan', '盐田区': 'Yantian',
      '宝安区': "Bao'an", '龙岗区': 'Longgang', '龙华区': 'Longhua', '坪山区': 'Pingshan', '光明区': 'Guangming',
      '上城区': 'Shangcheng', '拱墅区': 'Gongshu', '西湖区': 'Xihu', '滨江区': 'Binjiang',
      '萧山区': 'Xiaoshan', '余杭区': 'Yuhang', '富阳区': 'Fuyang', '临安区': 'Linan',
      '临平区': 'Linping', '钱塘区': 'Qiantang',
      '锦江区': 'Jinjiang', '青羊区': 'Qingyang', '金牛区': 'Jinniu', '武侯区': 'Wuhou',
      '成华区': 'Chenghua', '龙泉驿区': 'Longquanyi', '青白江区': 'Qingbaijiang', '新都区': 'Xindu',
      '温江区': 'Wenjiang', '双流区': 'Shuangliu', '郫都区': 'Pidu', '新津区': 'Xinjin',
      '江岸区': "Jiang'an", '江汉区': 'Jianghan', '硚口区': 'Qiaokou', '汉阳区': 'Hanyang',
      '武昌区': 'Wuchang', '青山区': 'Qingshan', '洪山区': 'Hongshan', '东西湖区': 'Dongxihu',
      '汉南区': 'Hannan', '蔡甸区': 'Caidian', '江夏区': 'Jiangxia', '黄陂区': 'Huangpi', '新洲区': 'Xinzhou',
      '玄武区': 'Xuanwu', '秦淮区': 'Qinhuai', '建邺区': 'Jianye', '鼓楼区': 'Gulou',
      '浦口区': 'Pukou', '栖霞区': 'Qixia', '雨花台区': 'Yuhuatai', '江宁区': 'Jiangning',
      '六合区': 'Luhe', '溧水区': 'Lishui', '高淳区': 'Gaochun',
      '和平区': 'Heping', '河东区': 'Hedong', '河西区': 'Hexi', '南开区': 'Nankai',
      '河北区': 'Hebei', '红桥区': 'Hongqiao', '东丽区': 'Dongli', '西青区': 'Xiqing',
      '津南区': 'Jinnan', '北辰区': 'Beichen', '武清区': 'Wuqing', '宝坻区': 'Baodi',
      '滨海新区': 'Binhai', '宁河区': 'Ninghe', '静海区': 'Jinghai', '蓟州区': 'Jizhou',
      '渝中区': 'Yuzhong', '大渡口区': 'Dadukou', '江北区': 'Jiangbei', '沙坪坝区': 'Shapingba',
      '九龙坡区': 'Jiulongpo', '南岸区': "Nan'an", '北碚区': 'Beibei', '渝北区': 'Yubei',
      '巴南区': 'Banan', '涪陵区': 'Fuling', '万州区': 'Wanzhou', '黔江区': 'Qianjiang',
      '长寿区': 'Changshou', '江津区': 'Jiangjin', '合川区': 'Hechuan', '永川区': 'Yongchuan',
      '南川区': 'Nanchuan', '綦江区': 'Qijiang', '大足区': 'Dazu', '璧山区': 'Bishan',
      '铜梁区': 'Tongliang', '潼南区': 'Tongnan', '荣昌区': 'Rongchang', '开州区': 'Kaizhou',
      '梁平区': 'Liangping', '武隆区': 'Wulong',
      '姑苏区': 'Gusu', '虎丘区': 'Huqiu', '吴中区': 'Wuzhong', '相城区': 'Xiangcheng',
      '吴江区': 'Wujiang', '工业园区': 'Suzhou Industrial Park',
      '莞城街道': 'Guancheng', '南城街道': 'Nancheng', '东城街道': 'Dongcheng', '万江街道': 'Wanjiang',
      '新城区': 'Xincheng', '碑林区': 'Beilin', '莲湖区': 'Lianhu', '雁塔区': 'Yanta',
      '灞桥区': 'Baqiao', '未央区': 'Weiyang', '阎良区': 'Yanliang', '临潼区': 'Lintong',
      '长安区': "Chang'an", '高陵区': 'Gaoling', '鄠邑区': 'Huyi',
      '沈河区': 'Shenhe', '大东区': 'Dadong', '皇姑区': 'Huanggu',
      '铁西区': 'Tiexi', '苏家屯区': 'Sujiatun', '浑南区': 'Hunnan', '沈北新区': 'Shenbei',
      '于洪区': 'Yuhong', '辽中区': 'Liaozhong',
      '中山区': 'Zhongshan', '西岗区': 'Xigang', '沙河口区': 'Shahekou', '甘井子区': 'Ganjingzi',
      '旅顺口区': 'Lvshunkou', '金州区': 'Jinzhou', '普兰店区': 'Pulandian',
      '市南区': 'Shinan', '市北区': 'Shibei', '黄岛区': 'Huangdao', '崂山区': 'Laoshan',
      '李沧区': 'Licang', '城阳区': 'Chengyang', '即墨区': 'Jimo',
      '思明区': 'Siming', '海沧区': 'Haicang', '湖里区': 'Huli', '集美区': 'Jimei',
      '同安区': "Tong'an", '翔安区': "Xiang'an",
      '海曙区': 'Haishu', '北仑区': 'Beilun', '镇海区': 'Zhenhai',
      '鄞州区': 'Yinzhou', '奉化区': 'Fenghua',
      '芙蓉区': 'Furong', '天心区': 'Tianxin', '岳麓区': 'Yuelu', '开福区': 'Kaifu',
      '雨花区': 'Yuhua', '望城区': 'Wangcheng',
      '中原区': 'Zhongyuan', '二七区': 'Erqi', '管城回族区': 'Guancheng', '金水区': 'Jinshui',
      '上街区': 'Shangjie', '惠济区': 'Huiji',
      '台江区': 'Taijiang', '仓山区': 'Cangshan', '马尾区': 'Mawei',
      '晋安区': "Jin'an", '长乐区': 'Changle',
      '五华区': 'Wuhua', '盘龙区': 'Panlong', '官渡区': 'Guandu', '西山区': 'Xishan',
      '东川区': 'Dongchuan', '呈贡区': 'Chenggong', '晋宁区': 'Jinning',
      '桥西区': 'Qiaoxi', '新华区': 'Xinhua', '井陉矿区': 'Jingxing',
      '裕华区': 'Yuhua', '藁城区': 'Gaocheng', '鹿泉区': 'Luquan', '栾城区': 'Luancheng',
      '历下区': 'Lixia', '市中区': 'Shizhong', '槐荫区': 'Huaiyin', '天桥区': 'Tianqiao',
      '历城区': 'Licheng', '长清区': 'Changqing', '章丘区': 'Zhangqiu', '济阳区': 'Jiyang',
      '莱芜区': 'Laiwu', '钢城区': 'Gangcheng',
      '道里区': 'Daoli', '南岗区': 'Nangang', '道外区': 'Daowai', '平房区': 'Pingfang',
      '松北区': 'Songbei', '香坊区': 'Xiangfang', '呼兰区': 'Hulan', '阿城区': 'Acheng',
      '双城区': 'Shuangcheng',
      '南关区': 'Nanguan', '宽城区': 'Kuancheng', '二道区': 'Erdao',
      '绿园区': 'Lvyuan', '双阳区': 'Shuangyang', '九台区': 'Jiutai',
      '小店区': 'Xiaodian', '迎泽区': 'Yingze', '杏花岭区': 'Xinghualing', '尖草坪区': 'Jiancaoping',
      '万柏林区': 'Wanbailin', '晋源区': 'Jinyuan',
      '瑶海区': 'Yaohai', '庐阳区': 'Luyang', '蜀山区': 'Shushan', '包河区': 'Baohe',
      '长丰县': 'Changfeng', '肥东县': 'Feidong', '肥西县': 'Feixi', '庐江县': 'Lujiang',
      '巢湖市': 'Chaohu',
      '青云谱区': 'Qingyunpu', '湾里区': 'Wanli',
      '青山湖区': 'Qingshanhu', '新建区': 'Xinjian',
      '兴宁区': 'Xingning', '青秀区': 'Qingxiu', '江南区': 'Jiangnan', '西乡塘区': 'Xixiangtang',
      '良庆区': 'Liangqing', '邕宁区': 'Yongning', '武鸣区': 'Wuming',
      '南明区': 'Nanming', '云岩区': 'Yunyan', '花溪区': 'Huaxi', '乌当区': 'Wudang',
      '观山湖区': 'Guanshanhu',
      '城关区': 'Chengguan', '七里河区': 'Qilihe', '西固区': 'Xigu', '安宁区': 'Anning',
      '红古区': 'Honggu',
      '秀英区': 'Xiuying', '琼山区': 'Qiongshan', '美兰区': 'Meilan',
      '天山区': 'Tianshan', '沙依巴克区': 'Shayibake', '新市区': 'Xinshi', '水磨沟区': 'Shuimogou',
      '头屯河区': 'Toutunhe', '达坂城区': 'Dabancheng', '米东区': 'Midong',
      '堆龙德庆区': 'Duilongdeqing', '达孜区': 'Dazi',
      '兴庆区': 'Xingqing', '西夏区': 'Xixia', '金凤区': 'Jinfeng',
      '城东区': 'Chengdong', '城中区': 'Chengzhong', '城西区': 'Chengxi', '城北区': 'Chengbei',
      '回民区': 'Huimin', '玉泉区': 'Yuquan', '赛罕区': 'Saihan',
      '中西区': 'Central and Western', '湾仔区': 'Wan Chai', '东区': 'Eastern', '南区': 'Southern',
      '油尖旺区': 'Yau Tsim Mong', '深水埗区': 'Sham Shui Po', '九龙城区': 'Kowloon City',
      '黄大仙区': 'Wong Tai Sin', '观塘区': 'Kwun Tong', '荃湾区': 'Tsuen Wan',
      '屯门区': 'Tuen Mun', '元朗区': 'Yuen Long', '北区': 'North', '大埔区': 'Tai Po',
      '西贡区': 'Sai Kung', '沙田区': 'Sha Tin', '葵青区': 'Kwai Tsing', '离岛区': 'Islands',
      '花地玛堂区': 'Nossa Senhora de Fatima', '圣安多尼堂区': 'Santo Antonio',
      '大堂区': 'Sé', '望德堂区': 'Sao Lazaro', '风顺堂区': 'Sao Lourenco',
      '嘉模堂区': 'Our Lady of Carmel', '圣方济各堂区': 'St. Francis Xavier',
      '松山区': 'Songshan', '信义区': 'Xinyi',
      '中正区': 'Zhongzheng', '大同区': 'Datong', '万华区': 'Wanhua', '文山区': 'Wenshan',
      '南港区': 'Nangang', '内湖区': 'Neihu', '士林区': 'Shilin', '北投区': 'Beitou',
      '千代田区': 'Chiyoda', '中央区': 'Chuo', '港区': 'Minato', '新宿区': 'Shinjuku',
      '文京区': 'Bunkyo', '台东区': 'Taito', '墨田区': 'Sumida', '江东区': 'Koto',
      '品川区': 'Shinagawa', '目黑区': 'Meguro', '大田区': 'Ota', '世田谷区': 'Setagaya',
      '涩谷区': 'Shibuya', '中野区': 'Nakano', '杉并区': 'Suginami', '丰岛区': 'Toshima',
      '荒川区': 'Arakawa', '板桥区': 'Itabashi', '练马区': 'Nerima',
      '足立区': 'Adachi', '葛饰区': 'Katsushika', '江户川区': 'Edogawa',
      '大阪市': 'Osaka City', '堺市': 'Sakai', '丰中市': 'Toyonaka', '池田市': 'Ikeda',
      '吹田市': 'Suita', '泉大津市': 'Izumiotsu', '高槻市': 'Takatsuki', '守口市': 'Moriguchi',
      '枚方市': 'Hirakata', '茨木市': 'Ibaraki', '八尾市': 'Yao', '泉佐野市': 'Izumisano',
      '富田林市': 'Tondabayashi', '寝屋川市': 'Neyagawa', '河内长野市': 'Kawachinagano',
      '松原市': 'Matsubara', '大东市': 'Daito', '和泉市': 'Izumi', '箕面市': 'Minoh',
      '柏原市': 'Kashiwara', '羽曳野市': 'Habikino', '门真市': 'Kadoma', '摄津市': 'Settsu',
      '东大阪市': 'Higashiosaka', '藤井寺市': 'Fujiidera', '交野市': 'Katano',
      '岛本町': 'Shimamoto', '太子町': 'Taishi', '河南町': 'Kanan', '千早赤阪村': 'Chihayaakasaka',
      '拍那空区': 'Phra Nakhon', '律实区': 'Dusit', '娜那区': 'Nong Chok', '挽卿区': 'Bang Khen',
      '邦纳区': 'Bang Na', '挽甲必区': 'Bang Kapi', '巴威区': 'Prawet', '沙吞区': 'Sathon',
      '宛他那县': 'Watthana', '叻差贴威县': 'Ratchathewi', '邻铃县': 'Din Daeng',
      '汇权县': 'Huai Khwang', '乍都节区': 'Chatuchak', '廊曼区': 'Don Mueang',
      '挽拍区': 'Bang Phlat', '拍昆仑区': 'Phra Khanong', '然那哇县': 'Yan Nawa',
      '挽叻区': 'Bang Rak', '拍耶泰区': 'Phaya Thai',
      '空堤区': 'Khlong Toei', '吞武里区': 'Thon Buri', '曼谷莲区': 'Bangkok Noi',
      '曼谷艾区': 'Bangkok Yai', '邦巴沙都拍区': 'Pom Prap Sattru Phai',
      '冠岳区': 'Gwanak', '广津区': 'Gwangjin', '九老区': 'Guro', '衿川区': 'Geumcheon',
      '芦原区': 'Nowon', '道峰区': 'Dobong', '东大门区': 'Dongdaemun', '铜雀区': 'Dongjak',
      '恩平区': 'Eunpyeong', '龙山区': 'Yongsan', '麻浦区': 'Mapo', '西大门区': 'Seodaemun', '瑞草区': 'Seocho',
      '松坡区': 'Songpa', '阳川区': 'Yangcheon', '永登浦区': 'Yeongdeungpo',
      '钟路区': 'Jongno', '中区': 'Jung', '中浪区': 'Jungnang',
      '东北区': 'North East', '西北区': 'North West', '东南区': 'South East', '西南区': 'South West',
      '武吉免登': 'Bukit Bintang', '蒂蒂旺沙': 'Titiwangsa', '斯迪亚旺沙': 'Setiawangsa',
      '旺沙玛珠': 'Wangsa Maju', '峇都': 'Batu', '甲洞': 'Kepong', '泗岩沫': 'Segambut',
      '班底谷': 'Lembah Pantai', '士布爹': 'Seputeh', '武吉加里尔': 'Bukit Jalil',
      '敦拉萨镇': 'Bandar Tun Razak', '蕉赖': 'Cheras', '新街场': 'Sungai Besi',
      '大使路': 'Jalan Duta', '孟沙': 'Bangsar', '班底': 'Pantai',
      'A区': 'Zone A', 'B区': 'Zone B', 'C区': 'Zone C', 'D区': 'Zone D',
      'E区': 'Zone E', 'F区': 'Zone F', 'G区': 'Zone G',
      '新德里区': 'New Delhi District', '北德里': 'North Delhi', '南德里': 'South Delhi',
      '东德里': 'East Delhi', '东北德里': 'North East Delhi', '西北德里': 'North West Delhi',
      '西南德里': 'South West Delhi', '西德里': 'West Delhi',
      '班加罗尔市区': 'Bangalore Urban', '班加罗尔郊区': 'Bangalore Rural',
      '德拉区': 'Deira', '布尔迪拜': 'Bur Dubai', '朱美拉': 'Jumeirah',
      '阿尔巴沙': 'Al Barsha', '迪拜码头': 'Dubai Marina', '商业湾': 'Business Bay',
      '迪拜市中心': 'Downtown Dubai', '国际城': 'International City',
      '八王子市': 'Hachioji', '立川市': 'Tachikawa', '武藏野市': 'Musashino',
      '三鹰市': 'Mitaka', '青梅市': 'Ome', '府中市': 'Fuchu', '昭岛市': 'Akishima',
      '调布市': 'Chofu', '町田市': 'Machida', '小金井市': 'Koganei', '小平市': 'Kodaira',
      '日野市': 'Hino', '东村山市': 'Higashimurayama', '国分寺市': 'Kokubunji',
      '国立市': 'Kunitachi', '福生市': 'Fussa', '狛江市': 'Komaae', '东大和市': 'Higashiyamato',
      '清濑市': 'Kiyose', '东久留米市': 'Higashikurume', '武藏村山市': 'Musashimurayama',
      '西东京市': 'Nishitokyo', '瑞穗町': 'Mizuho', '日之出町': 'Hinode',
      '桧原村': 'Hinohara', '奥多摩町': 'Okutama',
    }
    return districtMap[districtZh] ?? districtZh
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
    console.log('[resolveLocation] sending:', { continent, country: countryEn, city: cityEn, district: districtEn })
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
    const respText = await r.text()
    console.log('[resolveLocation] response status:', r.status, 'body:', respText)
    if (!r.ok) return null
    return JSON.parse(respText) as LocationModel
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
      body: JSON.stringify({ keywords: kws, location: loc, concurrency, headless }),
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
            <label className="field inline checkbox-field">
              <input
                type="checkbox"
                checked={!headless}
                onChange={(e) => setHeadless(!e.target.checked)}
              />
              <span>显示浏览器</span>
            </label>
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

      <ProgressPanel status={status} />

      <section className="engine-log">
        <h2>运行日志</h2>
        <pre ref={logRef} className="engine-logs">
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

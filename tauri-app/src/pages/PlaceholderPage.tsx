import { useLocation } from 'react-router-dom'

const copy: Record<string, { title: string; body: string }> = {
  '/ai': {
    title: 'AI 策略',
    body: '下一步：对接 /api/keywords/generate 与模板持久化（对齐 AIStrategyPage）。',
  },
  '/sync': {
    title: '同步设置',
    body: '下一步：对接 /api/config、/api/sync 与 OAuth 流程（对齐 SyncSettingsPage）。',
  },
  '/whatsapp': {
    title: 'WhatsApp',
    body: '本地服务默认 http://127.0.0.1:3003 ；可在外部浏览器打开扫码页，此处仅占位。',
  },
}

export default function PlaceholderPage() {
  const { pathname } = useLocation()
  const c = copy[pathname] ?? { title: '页面', body: '开发中。' }

  return (
    <div>
      <h1 className="page-title">{c.title}</h1>
      <p>{c.body}</p>
    </div>
  )
}

import { useCallback, useEffect, useRef, useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { Sun, Moon, RefreshCw, Palette } from 'lucide-react'

import { useTheme } from '../hooks/useTheme'
import { checkBackendHealth, restartBackend } from '../lib/tauriBridge'

import './AppLayout.css'

const nav = [
  { to: '/engine', label: '获客引擎', icon: '🔍' },
  { to: '/preview', label: '数据预览', icon: '📄' },
  { to: '/strategy', label: 'AI 策略', icon: '🤖' },
  { to: '/settings', label: '同步设置', icon: '☁️' },
  { to: '/whatsapp', label: 'WhatsApp', icon: '💬' },
]

export default function AppLayout() {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const { accent, setAccent, mode, toggleMode, accents } = useTheme()

  const [accentOpen, setAccentOpen] = useState(false)
  const [backendAlive, setBackendAlive] = useState(true)
  const [restarting, setRestarting] = useState(false)
  const healthTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const pollHealth = useCallback(async () => {
    const result = await checkBackendHealth()
    setBackendAlive(result === 'alive')
  }, [])

  useEffect(() => {
    pollHealth()
    healthTimerRef.current = setInterval(pollHealth, 5000)
    return () => {
      if (healthTimerRef.current) clearInterval(healthTimerRef.current)
    }
  }, [pollHealth])

  const handleRestart = async () => {
    setRestarting(true)
    setBackendAlive(false)
    try {
      await restartBackend()
      setTimeout(async () => {
        await pollHealth()
        setRestarting(false)
      }, 3000)
    } catch {
      setRestarting(false)
    }
  }

  return (
    <div className={`app-layout ${collapsed ? 'sidebar-collapsed' : ''}`}>
      {drawerOpen ? <div className="sidebar-overlay" onClick={() => setDrawerOpen(false)} /> : null}

      <aside className={`sidebar ${drawerOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <span className="sidebar-brand-icon">🌐</span>
            {!collapsed && (
              <div className="sidebar-brand-text">
                <div className="sidebar-brand-title">B2B Global</div>
                <div className="sidebar-brand-subtitle">获客系统</div>
              </div>
            )}
          </div>
          <button
            type="button"
            className="sidebar-collapse-btn"
            onClick={() => setCollapsed((c) => !c)}
            title={collapsed ? '展开侧边栏' : '收起侧边栏'}
          >
            {collapsed ? '→' : '←'}
          </button>
        </div>

        <nav className="sidebar-nav">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
              onClick={() => setDrawerOpen(false)}
              title={collapsed ? item.label : undefined}
            >
              <span className="sidebar-link-icon">{item.icon}</span>
              {!collapsed && <span className="sidebar-link-text">{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleMode}
            title={mode === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
          >
            <span className="theme-toggle-icon">{mode === 'dark' ? '☀️' : '🌙'}</span>
            {!collapsed && <span className="theme-toggle-text">{mode === 'dark' ? '浅色模式' : '深色模式'}</span>}
          </button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <button
            type="button"
            className="menu-btn"
            onClick={() => setDrawerOpen(true)}
            aria-label="打开菜单"
          >
            ☰
          </button>

          <div className="topbar-right">
            {/* 主题颜色选择器 */}
            <div className="accent-selector">
              <button
                type="button"
                className="topbar-icon-btn"
                onClick={() => setAccentOpen((o) => !o)}
                title="切换主题颜色"
              >
                <Palette size={17} />
              </button>
              {accentOpen && (
                <>
                  <div className="accent-dropdown-backdrop" onClick={() => setAccentOpen(false)} />
                  <div className="accent-dropdown">
                    {accents.map((a) => (
                      <button
                        key={a.key}
                        type="button"
                        className={`accent-option ${accent === a.key ? 'active' : ''}`}
                        onClick={() => { setAccent(a.key); setAccentOpen(false) }}
                      >
                        <span className="accent-dot" style={{ background: a.color }} />
                        <span className="accent-label">{a.label}</span>
                        {accent === a.key && <span className="accent-check">✓</span>}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>

            <span className="topbar-divider" />

            {/* 暗/亮模式切换 */}
            <button
              type="button"
              className="topbar-icon-btn"
              onClick={toggleMode}
              title={mode === 'dark' ? '浅色模式' : '深色模式'}
            >
              {mode === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
            </button>

            <span className="topbar-divider" />

            {/* 后端状态指示器 */}
            <div
              className={`backend-status ${backendAlive ? 'alive' : 'dead'} ${restarting ? 'restarting' : ''}`}
              onClick={() => !backendAlive && !restarting && handleRestart()}
              title={backendAlive ? '后端服务运行正常' : restarting ? '正在重启...' : '点击重启后端服务'}
            >
              <span className="status-dot" />
              <span className="status-text">
                {restarting ? '重启中...' : backendAlive ? '后端正常' : '后端已停止'}
              </span>
              {!backendAlive && !restarting && (
                <button
                  type="button"
                  className="restart-btn"
                  onClick={(e) => { e.stopPropagation(); handleRestart() }}
                >
                  <RefreshCw size={13} />
                  重启
                </button>
              )}
            </div>
          </div>
        </header>
        <div className="content">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
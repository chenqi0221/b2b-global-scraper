import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

import { useTheme } from '../hooks/useTheme'

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
  const { theme, toggle } = useTheme()

  return (
    <div className={`app-layout ${collapsed ? 'sidebar-collapsed' : ''}`}>
      {/* 移动端遮罩 */}
      {drawerOpen ? <div className="sidebar-overlay" onClick={() => setDrawerOpen(false)} /> : null}

      {/* 侧边栏 */}
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
            onClick={toggle}
            title={theme === 'dark' ? '切换到浅色主题' : '切换到深色主题'}
          >
            <span className="theme-toggle-icon">{theme === 'dark' ? '☀️' : '🌙'}</span>
            {!collapsed && <span className="theme-toggle-text">{theme === 'dark' ? '浅色模式' : '深色模式'}</span>}
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
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
        </header>
        <div className="content">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

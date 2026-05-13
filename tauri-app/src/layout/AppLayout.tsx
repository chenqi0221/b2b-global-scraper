import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'

import './AppLayout.css'

const nav = [
  { to: '/engine', label: '获客引擎', icon: '🔍' },
  { to: '/data', label: '数据预览', icon: '📄' },
  { to: '/ai', label: 'AI 策略', icon: '🤖' },
  { to: '/sync', label: '同步设置', icon: '☁️' },
  { to: '/whatsapp', label: 'WhatsApp', icon: '💬' },
]

export function AppLayout() {
  const [navOpen, setNavOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    setNavOpen(false)
  }, [location.pathname])

  useEffect(() => {
    if (!navOpen) return
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = prev
    }
  }, [navOpen])

  return (
    <div className={`app-root${navOpen ? ' app-root--nav-open' : ''}`}>
      <header className="app-topbar">
        <button
          type="button"
          className="app-menu-btn"
          aria-expanded={navOpen}
          aria-controls="app-sidebar"
          onClick={() => setNavOpen((v) => !v)}
        >
          <span className="app-menu-icon" aria-hidden>
            ☰
          </span>
          <span>菜单</span>
        </button>
        <span className="app-topbar-title">B2B Global 获客系统</span>
      </header>

      <button
        type="button"
        className="app-backdrop"
        aria-label="关闭菜单"
        tabIndex={-1}
        onClick={() => setNavOpen(false)}
      />

      <aside id="app-sidebar" className="app-sidebar">
        <div className="app-brand">
          <div className="app-brand-title">B2B Global</div>
          <div className="app-brand-sub">获客系统</div>
        </div>
        <nav className="app-nav" aria-label="主导航">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `app-nav-link${isActive ? ' app-nav-link-active' : ''}`
              }
            >
              <span className="app-nav-ico" aria-hidden>
                {item.icon}
              </span>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="app-main">
        <Outlet />
      </div>
    </div>
  )
}

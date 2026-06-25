# B2B Global 获客系统 — 整体架构蓝图

## 1. 系统全景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           B2B Global 获客系统                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────┐                                          │
│  │      Tauri 桌面壳层 (Rust)    │                                          │
│  │  ┌────────┐ ┌──────────────┐ │                                          │
│  │  │ main.rs│ │   lib.rs      │ │  单实例 / 窗口状态 / 文件对话框            │
│  │  └────────┘ └──────────────┘ │  Python 子进程管理                         │
│  └──────────────┬───────────────┘                                          │
│                 │ HTTP / SSE                                               │
│                 ▼                                                          │
│  ┌──────────────────────────────┐                                          │
│  │   React 19 前端 (Vite 8)     │                                          │
│  │  ┌────────┐ ┌──────────────┐ │                                          │
│  │  │ Pages  │ │  Components  │ │  Engine / Data / AI / Sync               │
│  │  │ Layout │ │   Modals     │ │                                          │
│  │  └────────┘ └──────────────┘ │                                          │
│  │  ┌────────┐ ┌──────────────┐ │                                          │
│  │  │Zustand │ │ Tauri Bridge │ │  全局状态 / 文件选择 / 路径Reveal          │
│  │  │ Store  │ │              │ │                                          │
│  │  └────────┘ └──────────────┘ │                                          │
│  └──────────────┬───────────────┘                                          │
│                 │ HTTP fetch / SSE                                         │
│                 ▼                                                          │
│  ┌──────────────────────────────┐                                          │
│  │   Python FastAPI 后端        │  127.0.0.1:8756                          │
│  │  ┌────────┐ ┌──────────────┐ │                                          │
│  │  │Routers │ │  Schemas     │ │  REST API / Pydantic 模型                 │
│  │  │Services│ │              │ │                                          │
│  │  └────────┘ └──────────────┘ │                                          │
│  └──────────────┬───────────────┘                                          │
│                 │                                                          │
│  ┌──────────────┼──────────────┐                                          │
│  ▼              ▼              ▼                                          │
│  ┌────────┐  ┌────────┐                                                  │
│  │  Core  │  │Scraper │                                                  │
│  │Services│  │Engine  │                                                  │
│  │        │  │        │                                                  │
│  └────────┘  └────────┘                                                  │
│                                                                             │
│  ┌──────────────┬──────────────┬──────────────┐                         │
│  ▼              ▼              ▼              ▼                         │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                         │
│  │Playwright│ │BeautifulSoup│ │Google Sheets│ │Gemini/  │                         │
│  │Google Maps│ │Email Extract │ │OAuth2 API  │ │OpenAI   │                         │
│  └────────┘  └────────┘  └────────┘  └────────┘                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 模块职责

### 2.1 Tauri 桌面壳层 (`tauri-app/src-tauri/`)

| 文件 | 职责 |
|------|------|
| `main.rs` | 程序入口，`windows_subsystem` 隐藏控制台 |
| `lib.rs` | Tauri Builder 配置、命令注册、setup 钩子 |
| `Cargo.toml` | Rust 依赖管理 |
| `tauri.conf.json` | 构建配置、窗口设置、权限声明 |
| `capabilities/default.json` | Tauri v2 权限模型配置 |

**核心能力：**
- 自动启动 Python 后端（查找 bundled `backend.exe` 或 `python -m uvicorn`）
- 单实例限制（`tauri-plugin-single-instance`）
- 文件对话框（`tauri-plugin-dialog`）
- 窗口状态记忆（`tauri-plugin-window-state`）
- 系统命令：`reveal_path`（资源管理器中打开文件）

### 2.2 React 前端 (`tauri-app/src/`)

| 目录 | 职责 |
|------|------|
| `pages/` | 4 个核心页面：Engine / DataPreview / AiStrategy / SyncSettings |
| `layout/` | 侧边栏布局 + 响应式抽屉 |
| `components/` | 可复用组件（关键词库弹窗） |
| `stores/` | Zustand 全局状态（采集状态、项目根路径） |
| `types/` | TypeScript 类型定义（与后端共享） |
| `config/` | 运行时配置（API 基址） |
| `lib/` | 工具函数（Tauri 命令桥接） |

### 2.3 Python FastAPI 后端 (`backend/`)

| 目录 | 职责 |
|------|------|
| `main.py` | FastAPI 应用入口、CORS、静态文件、SPA 回退 |
| `routers/` | API 路由模块（12 个路由文件） |
| `schemas/` | Pydantic 请求/响应模型 |
| `services/` | 业务服务（日志总线） |
| `deps.py` | 依赖注入 |
| `path_utils.py` | 路径工具 |
| `location_resolve.py` | 地理位置解析 |
| `run_sidecar.py` | Sidecar 运行工具 |

**API 路由清单：**

| 路由文件 | 端点前缀 | 功能 |
|----------|----------|------|
| `scraper.py` | `/api/scraper` | 采集控制（启动/停止/状态） |
| `meta.py` | `/api/meta` | 元数据（地理、行业、位置解析） |
| `data.py` | `/api/data` | 数据预览（Downloads、CSV） |
| `keywords.py` | `/api/keywords` | 关键词库（CRUD、AI生成、导入导出） |
| `ai.py` | `/api/ai` | AI 策略（提示词模板） |
| `sync.py` | `/api/sync` | 同步（单文件、汇总目录） |
| `config.py` | `/api/config` | 环境配置读写 |
| `google_oauth.py` | `/api/google/oauth` | Google OAuth 授权流程 |
| `logs.py` | `/api/logs` | SSE 日志流 |
| `system.py` | `/api/system` | 系统信息 |

### 2.4 Python 核心模块 (`core/`)

| 文件 | 职责 |
|------|------|
| `scraper_controller.py` | 采集任务控制（启动/停止/状态管理） |
| `keyword_service.py` | 关键词库服务（CRUD、AI生成） |
| `sync_service.py` | Google Sheets 同步服务 |
| `config_service.py` | 配置读写服务 |

### 2.5 抓取引擎 (`scraper/`)

| 文件 | 职责 |
|------|------|
| `google_maps.py` | Playwright + Stealth 抓取 Google Maps 商家数据 |
| `email_extractor.py` | 访问商家官网提取邮箱地址 |
| `file_export.py` | CSV / Excel 导出 |

### 2.6 旧版 tkinter GUI (`gui/`)

保留作为兼容入口，`main.py` 可启动 tkinter 版本。

| 目录 | 职责 |
|------|------|
| `app.py` | tkinter 应用主类 |
| `components/` | UI 组件（侧边栏、状态卡片、日志面板等） |
| `pages/` | 页面（引擎、AI策略、同步设置） |
| `effects/` | Win11 毛玻璃效果 |

---

## 3. 数据流

### 3.1 采集流程

```
┌─────────┐    keywords + location + concurrency
│  User   │ ───────────────────────────────────────►
└─────────┘
              │
              ▼
        ┌─────────────┐
        │ EnginePage  │ ──POST /api/scraper/start──►
        └─────────────┘
              │
              ▼ (SSE)
        ┌─────────────┐ ◄───EventSource /api/logs/stream───
        │  log-pre    │      实时日志推送
        └─────────────┘
              │
              ▼ (轮询 2s)
        ┌─────────────┐ ◄───GET /api/scraper/status ────
        │ scraperStore│      状态更新
        └─────────────┘
              │
              ▼
        输出 CSV → Downloads/{timestamp}/
```

### 3.2 同步流程

```
┌─────────┐    点击「同步单个 CSV」/「汇总目录同步」
│  User   │ ────────────────────────────────────────────►
└─────────┘
              │
              ▼
        ┌─────────────┐
        │ EnginePage  │ ──POST /api/sync/file 或 /api/sync/aggregate ──►
        └─────────────┘
              │
              ▼
        Python 后端：读取 CSV → 去重 → Google Sheets API 写入
              │
              ▼
        返回 {ok: true} → UI alert 提示
```

---

## 4. 状态管理

### Zustand Store (`scraperStore`)

```typescript
interface State {
  status: ScrapeStatus | null        // 当前采集状态
  statusError: string | null         // 状态同步错误
  projectRoot: string | null         // 项目根路径
  fetchStatus: () => Promise<void>   // 轮询状态
  fetchProjectRoot: () => Promise<void>
}
```

### 本地状态 (useState)

各页面独立管理表单状态：
- `EnginePage`: 关键词文本、地理位置级联、并发数、日志
- `SyncSettingsPage`: 表单字段、OAuth 状态
- `WhatsappPage`: CSV 路径、号码预览

---

## 5. 路由设计

| 路径 | 页面 | 功能 |
|------|------|------|
| `/` | 重定向 | → `/engine` |
| `/engine` | EnginePage | 获客引擎（核心） |
| `/data` | DataPreviewPage | 数据预览 |
| `/ai` | AiStrategyPage | AI 策略编辑 |
| `/sync` | SyncSettingsPage | 同步设置 + OAuth |

使用 `HashRouter` 确保 Tauri 桌面环境路由正常。

---

## 6. 样式架构

### CSS 变量系统 (`index.css`)

```css
:root {
  --text: #475569;
  --text-h: #0f172a;
  --bg: #f8fafc;
  --bg-elevated: #ffffff;
  --border: #e2e8f0;
  --accent: #6366f1;
  --sidebar-bg: #0f172a;
  /* ... */
}

@media (prefers-color-scheme: dark) {
  :root { /* 深色模式变量 */ }
}
```

### 响应式断点

| 断点 | 行为 |
|------|------|
| `>1024px` | 完整侧边栏 240px，三列卡片 |
| `768-1024px` | 侧边栏 200px |
| `<768px` | 顶栏 + 抽屉式侧边栏，单列布局 |
| `<560px` | 按钮全宽堆叠 |

---

## 7. 安全设计

| 方面 | 措施 |
|------|------|
| CSP | `null`（开发期），生产环境按需配置 |
| API Key | 输入框 `type="password"`，脱敏显示 |
| OAuth Token | 存储于 `token.json`（已 gitignore） |
| 文件路径 | 通过 Tauri Dialog API 选择，避免手动输入 |
| 单实例 | 防止重复启动导致端口冲突 |

---

## 8. 扩展点

| 扩展 | 位置 |
|------|------|
| 新增页面 | `tauri-app/src/pages/NewPage.tsx` + 路由注册 |
| 新增 API | `backend/routers/new.py` + `backend/main.py` 注册 |
| 新增核心服务 | `core/new_service.py` |
| 新增全局状态 | `tauri-app/src/stores/` |
| 新增 Tauri 命令 | `src-tauri/src/lib.rs` + `capabilities/default.json` |

---

## 9. 技术决策记录

### 为什么用 Tauri 而不是 Electron？
- 更小的包体积（Rust + OS WebView）
- 更好的性能
- 单实例插件原生支持
- 与 Python 后端 sidecar 集成更简洁

### 为什么用 HashRouter？
- Tauri 桌面环境文件协议（`tauri://localhost`）对 BrowserRouter 不友好
- HashRouter 无需服务端配置

### 为什么用 Zustand 而不是 Redux？
- 项目规模适中，Zustand 更轻量
- 无需 Provider 包裹
- TypeScript 类型推导更自然

### 为什么 SSE 而不是 WebSocket？
- 单向日志流，SSE 足够
- 自动重连、基于 HTTP 更易穿透代理
- 后端实现更简单

### 为什么保留 tkinter GUI？
- 兼容旧版入口
- 作为 Tauri 构建失败时的 fallback
- `main.py` 可直接启动

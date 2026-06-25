# B2B Global 获客系统 — 架构蓝图

## 1. 系统全景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           B2B Global 获客系统                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   桌面壳层    │    │   前端 UI    │    │  Python 后端  │                  │
│  │  Tauri v2    │◄──►│ React 19 + TS│◄──►│  FastAPI      │                  │
│  │  (Rust)      │    │  (Vite 8)    │    │  (Uvicorn)    │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                   │                           │
│         ▼                   ▼                   ▼                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │ 子进程管理    │    │ 状态管理     │    │  数据采集     │                  │
│  │ · Python后端  │    │ Zustand      │    │ · Google Maps│                  │
│  │              │    │              │    │ · 邮箱提取    │                  │
│  │              │    │              │    │ · CSV导出     │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│                                                   │                         │
│                              ┌────────────────────┼────────────────────┐   │
│                              ▼                    ▼                       │
│                        ┌──────────┐        ┌──────────┐                   │
│                        │ Google   │        │  豆包AI  │                   │
│                        │ Sheets   │        │  Gemini  │                   │
│                        │ (OAuth2) │        │  关键词  │                   │
│                        └──────────┘        └──────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 分层架构

### 2.1 桌面壳层 (Tauri Rust)

| 模块 | 职责 |
|------|------|
| `lib.rs` | Tauri Builder 配置、命令注册、setup 钩子 |
| `main.rs` | 程序入口 (`windows_subsystem`) |
| 子进程管理 | 自动启动/停止 Python 后端 |
| 单实例 | `tauri-plugin-single-instance` 防止多开 |
| 文件对话框 | `tauri-plugin-dialog` (CSV/目录选择) |
| 窗口状态 | `tauri-plugin-window-state` 记忆窗口大小位置 |

### 2.2 前端层 (React + TypeScript)

| 目录 | 职责 |
|------|------|
| `pages/` | 页面级组件 (5个核心页面) |
| `components/` | 可复用组件 (关键词库弹窗) |
| `layout/` | 布局组件 (侧边栏 + 响应式抽屉) |
| `stores/` | 全局状态 (Zustand) |
| `types/` | TypeScript 类型定义 |
| `config/` | 运行时配置 (API 基址) |
| `lib/` | 工具函数 (Tauri 桥接) |

### 2.3 后端层 (Python FastAPI)

由 Tauri 壳层自动启动，提供：

- `/api/scraper/*` — 采集控制 (启动/停止/状态)
- `/api/meta/*` — 元数据 (地理信息、行业模板、位置解析)
- `/api/data/*` — 数据预览 (Downloads 会话、CSV 预览)
- `/api/keywords/*` — 关键词库 (CRUD、AI 生成、导入导出)
- `/api/ai/*` — AI 策略 (提示词模板)
- `/api/sync/*` — 同步 (单文件、汇总目录)
- `/api/config/*` — 环境配置读写
- `/api/google/oauth/*` — Google OAuth 授权
- `/api/logs/stream` — SSE 日志流

---

## 3. 数据流

### 3.1 采集流程

```
用户输入关键词 + 地理位置
        │
        ▼
┌───────────────┐
│  EnginePage   │ ──POST /api/scraper/start──► Python 后端启动采集任务
└───────────────┘
        │
        ▼ (SSE 流)
┌───────────────┐
│   log-pre     │ ◄───EventSource /api/logs/stream──── 实时日志
└───────────────┘
        │
        ▼ (轮询)
┌───────────────┐
│  scraperStore │ ◄───GET /api/scraper/status ──── 状态更新 (2s间隔)
└───────────────┘
        │
        ▼
   输出 CSV 到 Downloads/
```

### 3.2 同步流程

```
用户点击「同步单个 CSV」/「汇总目录同步」
        │
        ▼
┌───────────────┐
│  EnginePage   │ ──POST /api/sync/file 或 /api/sync/aggregate──►
└───────────────┘
        │
        ▼
   Python 后端读取 CSV → 去重 → Google Sheets API 写入
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

---

## 5. 路由设计

| 路径 | 页面 | 功能 |
|------|------|------|
| `/` | 重定向 | → `/engine` |
| `/engine` | EnginePage | 获客引擎 (核心) |
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
| CSP | `null` (开发期)，生产环境按需配置 |
| API Key | 输入框 `type="password"`，脱敏显示 |
| OAuth Token | 存储于 `token.json` (已 gitignore) |
| 文件路径 | 通过 Tauri Dialog API 选择，避免手动输入 |
| 单实例 | 防止重复启动导致端口冲突 |

---

## 8. 扩展点

| 扩展 | 位置 |
|------|------|
| 新增页面 | `src/pages/NewPage.tsx` + 路由注册 |
| 新增 API 类型 | `src/types/api.ts` |
| 新增全局状态 | `src/stores/` |
| 新增 Tauri 命令 | `src-tauri/src/lib.rs` + `capabilities/default.json` |
| 新增后端接口 | Python FastAPI 路由 |

---

## 9. 技术决策记录

### 为什么用 Tauri 而不是 Electron？
- 更小的包体积 (Rust + OS WebView)
- 更好的性能
- 单实例插件原生支持
- 与 Python 后端 sidecar 集成更简洁

### 为什么用 HashRouter？
- Tauri 桌面环境文件协议 (`tauri://localhost`) 对 BrowserRouter 不友好
- HashRouter 无需服务端配置

### 为什么用 Zustand 而不是 Redux？
- 项目规模适中，Zustand 更轻量
- 无需 Provider 包裹
- TypeScript 类型推导更自然

### 为什么 SSE 而不是 WebSocket？
- 单向日志流，SSE 足够
- 自动重连、基于 HTTP 更易穿透代理
- 后端实现更简单

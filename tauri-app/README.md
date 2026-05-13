# B2B Global 获客系统（Tauri + React）

基于 Tauri v2 + React 19 + TypeScript 的桌面端获客系统前端壳层，配套 Python FastAPI 后端提供 Google Maps 商家数据采集、AI 关键词生成、Google Sheets 同步、WhatsApp 消息服务。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 桌面壳层 | Tauri v2 (Rust) |
| 前端框架 | React 19 + TypeScript |
| 构建工具 | Vite 8 |
| 路由 | React Router v7 (HashRouter) |
| 状态管理 | Zustand |
| 样式 | Tailwind CSS v4 + 原生 CSS |
| 表格 | TanStack React Table |
| 图标 | Lucide React |
| 后端通信 | Fetch API → Python FastAPI |

---

## 项目结构

```
tauri-app/
├── public/                     # 静态资源
│   └── favicon.svg
├── src/
│   ├── main.tsx                # 应用入口 (HashRouter + StrictMode)
│   ├── App.tsx                 # 路由配置
│   ├── index.css               # 全局样式 / CSS 变量 / 深色模式
│   ├── App.css                 # App 级样式 (已精简)
│   ├── config/
│   │   └── api.ts              # API 基址配置
│   ├── lib/
│   │   └── tauriBridge.ts      # Tauri 命令桥接 (文件选择、路径Reveal、WhatsApp进程)
│   ├── types/
│   │   └── api.ts              # 前后端共享类型定义
│   ├── stores/
│   │   └── scraperStore.ts     # Zustand 全局状态 (采集状态、项目根路径)
│   ├── layout/
│   │   ├── AppLayout.tsx       # 侧边栏布局 + 响应式抽屉
│   │   └── AppLayout.css
│   ├── components/
│   │   ├── KeywordLibraryModal.tsx   # 关键词库弹窗 (CRUD + AI生成)
│   │   └── KeywordLibraryModal.css
│   └── pages/
│       ├── EnginePage.tsx      # 获客引擎 (核心页面：关键词/地理位置/启停/日志)
│       ├── EnginePage.css
│       ├── DataPreviewPage.tsx # 数据预览 (CSV 预览、会话选择)
│       ├── AiStrategyPage.tsx  # AI 策略 (提示词模板编辑)
│       ├── SyncSettingsPage.tsx# 同步设置 (Google OAuth、代理、API Key)
│       ├── WhatsappPage.tsx    # WhatsApp (iframe 嵌入、Node 进程控制)
│       └── FormPage.css        # 表单页面通用样式
├── src-tauri/
│   ├── src/
│   │   ├── main.rs             # Rust 入口 (windows_subsystem)
│   │   └── lib.rs              # Tauri 命令 + 后端子进程管理
│   ├── capabilities/
│   │   └── default.json        # Tauri 权限配置
│   ├── icons/                  # 应用图标 (多尺寸)
│   ├── Cargo.toml              # Rust 依赖
│   ├── tauri.conf.json         # Tauri 构建配置
│   └── build.rs
├── package.json
├── vite.config.ts
├── tsconfig.json / tsconfig.app.json / tsconfig.node.json
├── eslint.config.js
├── env.example
└── index.html
```

---

## 开发方式

```bash
# 1. 只启动前端 (系统浏览器调试，无桌面窗口)
npm run web
# 或
npm run dev

# 2. 启动 Tauri 桌面窗口 (完整桌面体验)
npm run desktop
# 或
npm run tauri:dev
```

后端 API 需按项目主 README 另行启动（Python FastAPI on `127.0.0.1:8756`）。

---

## 构建与打包

```bash
# 前端生产构建
npm run build

# 打包桌面安装包 (NSIS)
npm run package
# 产出: src-tauri/target/release/bundle/nsis/*.exe
```

---

## 核心功能模块

### 1. 获客引擎 (`/engine`)
- 关键词输入 / 行业模板选择 / 关键词库弹窗
- 地理位置级联选择 (大洲 → 国家 → 城市 → 区域) 或手动地址
- 并发数控制
- 实时采集状态看板 (已抓取 / 邮箱数 / 已同步)
- SSE 日志流实时显示
- 快捷操作：同步 CSV、汇总目录同步、代理探测、打开输出目录

### 2. 数据预览 (`/data`)
- Downloads 会话目录选择
- 根目录汇总 CSV 选择
- CSV 内容预览表格 (前 120 行)

### 3. AI 策略 (`/ai`)
- 关键词生成提示词模板编辑
- 持久化到 `user_ai_prompt.txt`

### 4. 同步设置 (`/sync`)
- 环境变量配置 (HTTP 代理、Google Sheets ID、Gemini/豆包 API Key)
- Google OAuth 授权流程 (需 `client_secret.json`)
- Token 刷新

### 5. WhatsApp (`/whatsapp`)
- 嵌入 WhatsApp Web UI (iframe)
- Node 子进程启动/停止 (Tauri 桌面版)
- 上游状态轮询
- CSV 电话号码预览联动

---

## Tauri Rust 后端职责

- **自动启动 Python 后端**：优先查找 bundled `backend.exe`，回退到 `python -m uvicorn backend.main:app`
- **单实例限制**：`tauri-plugin-single-instance`
- **文件对话框**：`tauri-plugin-dialog`
- **窗口状态记忆**：`tauri-plugin-window-state`
- **系统命令**：`reveal_path` (在资源管理器中打开文件/目录)
- **WhatsApp 进程管理**：`whatsapp_service_start/stop`

---

## 环境变量

复制 `env.example` 为 `.env.development` / `.env.production`：

```
VITE_API_BASE_URL=http://127.0.0.1:8756
```

---

## 注意事项

1. **CORS**：生产 WebView 源常为 `https://tauri.localhost:<随机端口>`，后端已配置 `allow_origin_regex` 放行
2. **Python 路径**：双击 exe 时 PATH 可能不含 `python`，已优先尝试 Windows `py -3`
3. **仓库根路径**：API 进程需在含 `backend/main.py` 的目录下启动，壳层按 `app.exe` 位置自动推断
4. **中文路径**：WiX MSI 打包在中文路径下可能失败，建议使用 NSIS (默认)

---

## License

MIT

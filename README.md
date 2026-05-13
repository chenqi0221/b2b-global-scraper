# B2B Global 获客系统

基于 Google Maps 的 B2B 商家数据抓取工具，支持多地区、多关键词批量采集，自动提取官网邮箱，并可通过 Google Sheets 同步或 WhatsApp 群发触达客户。

---

## 项目架构

本项目采用 **Tauri 桌面应用 + Python FastAPI 后端** 的混合架构：

```
┌─────────────────────────────────────────────────────────────┐
│                    Tauri 桌面应用 (Rust)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ React 19 前端 │  │ 窗口/对话框   │  │ 单实例/状态保存   │  │
│  │  (Vite 8)    │  │   管理       │  │                  │  │
│  └──────┬───────┘  └──────────────┘  └──────────────────┘  │
│         │                                                   │
│         │  HTTP fetch / SSE                                 │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Python FastAPI 后端 (自动拉起)               │   │
│  │  127.0.0.1:8756                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Python 业务核心层                         │
│  ┌────────────┐ ┌────────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Playwright │ │ 邮箱提取    │ │ Google   │ │ WhatsApp │  │
│  │ 地图抓取    │ │ 官网爬虫    │ │ Sheets   │ │ 消息群发  │  │
│  └────────────┘ └────────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 桌面壳 | Tauri | 2.11 |
| 前端 | React + Vite + Tailwind CSS | 19 / 8 / 4 |
| 状态管理 | Zustand | 5 |
| 后端 API | FastAPI | - |
| 抓取引擎 | Playwright + Stealth | - |
| 数据导出 | Pandas + OpenPyXL | - |
| AI 生成 | Google Gemini / OpenAI | - |
| 消息群发 | whatsapp-web.js | - |

---

## 目录结构

```
.
├── tauri-app/              # Tauri 桌面应用（React 前端 + Rust 后端）
│   ├── src/                # React 源码
│   ├── src-tauri/          # Rust 源码
│   ├── README.md           # 前端子项目说明
│   └── ARCHITECTURE.md     # 前端架构蓝图
│
├── backend/                # Python FastAPI 后端
│   ├── main.py             # 入口
│   ├── routers/            # API 路由
│   ├── schemas/            # Pydantic 模型
│   ├── services/           # 业务服务
│   └── requirements.txt    # 后端依赖
│
├── core/                   # Python 核心模块
│   ├── scraper_controller.py
│   ├── keyword_service.py
│   └── sync_service.py
│
├── scraper/                # 抓取引擎
│   ├── google_maps.py
│   ├── email_extractor.py
│   └── file_export.py
│
├── gui/                    # 旧版 tkinter GUI（兼容保留）
│   ├── app.py
│   ├── components/
│   ├── pages/
│   └── effects/
│
├── models/                 # Pydantic 数据模型
├── utils/                  # 工具函数
├── third_party/            # 第三方服务
│   └── whatsapp-service/   # WhatsApp Node 服务
│
├── tests/                  # 测试脚本
├── docs/                   # 文档
│   ├── api/
│   └── plans/
├── Downloads/              # 抓取结果输出
├── backups/                # 历史备份（空目录占位）
├── requirements.txt        # Python 依赖
├── main.py                 # tkinter GUI 入口
└── README.md               # 本文件
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/chenqi0221/b2b-global-scraper.git
cd b2b-global-scraper
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
python -m playwright install
```

### 3. 安装前端依赖

```bash
cd tauri-app
npm install
```

### 4. 开发模式启动

```bash
# 方式一：一键启动 Tauri 桌面应用（推荐）
npm run tauri:dev

# 方式二：单独启动后端 + 前端
# 终端 1
cd ..
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8756 --reload
# 终端 2
cd tauri-app
npm run dev
```

### 5. 打包构建

```bash
cd tauri-app
npm run package
```

构建产物位于 `tauri-app/src-tauri/target/release/bundle/`。

---

## 核心功能

### 获客引擎
- 选择地理位置（大洲 → 国家 → 城市 → 区域）
- 输入关键词或从关键词库选择
- 设置并发数，开始批量抓取
- 自动滚动加载更多商家
- 访问商家官网提取邮箱
- 实时日志和进度展示

### 数据预览
- 查看历史抓取会话
- CSV / Excel 文件预览
- 在资源管理器中打开文件

### AI 策略
- AI 自动生成行业关键词
- 自定义 AI 提示词模板
- 支持 Google Gemini 和 OpenAI

### 同步设置
- Google OAuth 授权
- 同步到 Google Sheets
- 多表汇总合并

### WhatsApp
- 扫码登录 WhatsApp
- 批量发送消息
- 防检测模拟（打字间隔、随机消息）

---

## 环境变量

创建 `.env` 文件：

```env
# OpenAI / Google Gemini API Key
OPENAI_API_KEY=sk-xxx
GOOGLE_API_KEY=xxx

# HTTP 代理（可选）
HTTP_PROXY=127.0.0.1:7890

# 开发时指定仓库根目录（可选）
B2B_REPO_ROOT=E:\google-maps-scraper

# 自动启动 WhatsApp 服务（可选）
B2B_SPAWN_WHATSAPP=1
```

---

## 后端 API 文档

开发模式下访问：
- Swagger UI: http://127.0.0.1:8756/docs
- OpenAPI JSON: http://127.0.0.1:8756/openapi.json

主要端点：

| 端点 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `GET /api/scraper/status` | 抓取状态 |
| `POST /api/scraper/start` | 开始抓取 |
| `POST /api/scraper/stop` | 停止抓取 |
| `GET /api/meta/geography` | 地理位置数据 |
| `GET /api/meta/industries` | 行业关键词模板 |
| `GET /api/logs` | SSE 实时日志 |

---

## 更新日志

### 2025-05-13
- 完成 Tauri 桌面应用重构
- 新增 FastAPI 后端，提供 REST API 和 SSE 日志推送
- Rust 后端自动拉起 Python，带端口健康检测（15秒超时）
- 修复 `py` launcher 启动失败时自动回退到 `python` 直接启动
- 保留原有 tkinter 版本作为兼容入口
- 清理历史冗余文件和旧版备份代码

---

## License

MIT

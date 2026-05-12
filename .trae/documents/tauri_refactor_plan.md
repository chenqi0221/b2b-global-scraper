# Tauri + Python 后端重构计划

> **目标:** 将现有 tkinter+ttkbootstrap GUI 重构为 Tauri (Rust+Web前端) + Python 后端架构，完整保留所有业务功能，修复已知 bug，优化用户体验。
>
> **范围:** 完整功能还原 + Bug 修复 + 架构优化 + 开发框架搭建
>
> **技术栈:** Tauri v2 + React/TypeScript + Tailwind CSS + Python FastAPI + Playwright

---

## 目录

1. [Phase 0: 保存当前版本并上传 GitHub](#phase-0-保存当前版本并上传-github)
2. [Phase 1: 开发框架与蓝图搭建](#phase-1-开发框架与蓝图搭建)
3. [Phase 2: Python 后端 API 服务](#phase-2-python-后端-api-服务)
4. [Phase 3: Tauri 前端核心架构](#phase-3-tauri-前端核心架构)
5. [Phase 4: 页面功能实现](#phase-4-页面功能实现)
6. [Phase 5: 数据同步与云服务](#phase-5-数据同步与云服务)
7. [Phase 6: Bug 修复与优化](#phase-6-bug-修复与优化)
8. [Phase 7: 打包与部署](#phase-7-打包与部署)

---

## Phase 0: 保存当前版本并上传 GitHub

### Task 0.1: Git 提交当前版本

**Files:**
- Modify: `.gitignore`

**Steps:**

- [ ] **Step 1: 检查 Git 状态**

```bash
git status
git log --oneline -5
```

- [ ] **Step 2: 添加所有变更并提交**

```bash
git add .
git commit -m "feat: save tkinter version before tauri refactor

- Win11 Mica glassmorphism effect
- Collapsible sidebar
- Responsive layout
- Keyword library management
- Google Maps scraper with Playwright
- Google Sheets sync
- AI keyword generation"
```

- [ ] **Step 3: 创建 Tag 标记版本**

```bash
git tag -a v2.0-tkinter -m "Final tkinter version before Tauri refactor"
```

### Task 0.2: 推送到 GitHub

**Steps:**

- [ ] **Step 1: 检查远程仓库**

```bash
git remote -v
```

- [ ] **Step 2: 推送代码和 Tag**

```bash
git push origin main
git push origin v2.0-tkinter
```

- [ ] **Step 3: 创建 Release**

在 GitHub 上创建 Release，附上版本说明。

---

## Phase 1: 开发框架与蓝图搭建

### Task 1.1: 创建 Tauri 项目结构

**Files:**
- Create: `tauri-app/` (新目录)
- Create: `tauri-app/src-tauri/Cargo.toml`
- Create: `tauri-app/src-tauri/tauri.conf.json`
- Create: `tauri-app/package.json`
- Create: `tauri-app/vite.config.ts`
- Create: `tauri-app/tsconfig.json`
- Create: `tauri-app/tailwind.config.js`
- Create: `tauri-app/index.html`

**项目结构:**

```
tauri-app/
├── src/                          # 前端 React 源码
│   ├── main.tsx                  # 入口
│   ├── App.tsx                   # 根组件
│   ├── components/               # 共享组件
│   │   ├── Sidebar.tsx           # 侧边栏导航
│   │   ├── StatusCard.tsx        # 状态卡片
│   │   ├── LogPanel.tsx          # 日志面板
│   │   ├── Toast.tsx             # 消息提示
│   │   ├── DataTable.tsx         # 数据表格
│   │   └── Modal.tsx             # 弹窗组件
│   ├── pages/                    # 页面
│   │   ├── EnginePage.tsx        # 获客引擎
│   │   ├── AIStrategyPage.tsx    # AI 策略
│   │   └── SyncSettingsPage.tsx  # 同步设置
│   ├── hooks/                    # 自定义 Hooks
│   │   ├── useScraper.ts         # 抓取逻辑
│   │   ├── useKeywords.ts        # 关键词管理
│   │   ├── useSync.ts            # 同步逻辑
│   │   └── useLogs.ts            # 日志管理
│   ├── stores/                   # 状态管理
│   │   └── appStore.ts           # Zustand 全局状态
│   ├── types/                    # TypeScript 类型
│   │   └── index.ts
│   ├── api/                      # 后端 API 调用
│   │   └── pythonApi.ts          # 与 Python 通信
│   └── styles/                   # 样式
│       └── globals.css
├── src-tauri/                    # Rust + Tauri 后端
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   ├── src/
│   │   ├── main.rs               # Rust 入口
│   │   ├── lib.rs
│   │   └── commands/             # Tauri Commands
│   │       ├── scraper.rs
│   │       ├── config.rs
│   │       └── system.rs
│   └── capabilities/
└── python_backend/               # Python FastAPI 服务
    ├── main.py                   # FastAPI 入口
    ├── api/
    │   ├── scraper.py            # 抓取 API
    │   ├── keywords.py           # 关键词 API
    │   ├── sync.py               # 同步 API
    │   └── config.py             # 配置 API
    ├── core/                     # 核心业务逻辑 (从现有项目迁移)
    │   ├── scraper_controller.py
    │   ├── keyword_service.py
    │   ├── sync_service.py
    │   └── config_service.py
    ├── services/                 # 第三方服务
    │   ├── sheet_aggregator.py
    │   ├── google_sheets_service.py
    │   ├── google_auth.py
    │   └── google_drive.py
    ├── scraper/                  # 抓取实现
    │   └── google_maps.py
    ├── models/                   # Pydantic 模型
    │   └── schemas.py
    └── utils/
        └── helpers.py
```

### Task 1.2: 初始化前端项目

**Steps:**

- [ ] **Step 1: 创建 Vite + React + TypeScript 项目**

```bash
cd tauri-app
npm create vite@latest . -- --template react-ts
```

- [ ] **Step 2: 安装依赖**

```bash
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install @tauri-apps/cli @tauri-apps/api
npm install zustand react-router-dom lucide-react
npm install @radix-ui/react-dialog @radix-ui/react-select @radix-ui/react-tabs
npm install class-variance-authority clsx tailwind-merge
npm install recharts  # 图表库
npm install @tanstack/react-table  # 数据表格
```

- [ ] **Step 3: 配置 Tailwind CSS**

`tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sidebar: '#0F172A',
        main: '#0F172A',
        card: '#1E293B',
        'card-hover': '#334155',
        primary: '#3B82F6',
        secondary: '#64748B',
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
      },
      fontFamily: {
        sans: ['Segoe UI', 'system-ui', 'sans-serif'],
        mono: ['Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 4: 配置 Tauri**

`src-tauri/tauri.conf.json`:
```json
{
  "productName": "B2B Global",
  "version": "3.0.0",
  "identifier": "com.b2bglobal.app",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://localhost:5173",
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build"
  },
  "app": {
    "windows": [
      {
        "title": "B2B Global 获客系统",
        "width": 1400,
        "height": 900,
        "minWidth": 900,
        "minHeight": 600,
        "center": true,
        "decorations": true,
        "transparent": false,
        "theme": "Dark"
      }
    ]
  }
}
```

### Task 1.3: 初始化 Python 后端

**Files:**
- Create: `tauri-app/python_backend/main.py`
- Create: `tauri-app/python_backend/requirements.txt`

**Steps:**

- [ ] **Step 1: 创建 requirements.txt**

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
python-dotenv==1.0.0
playwright==1.40.0
playwright-stealth==1.0.0
httpx[socks]==0.26.0
requests==2.31.0
openai==1.10.0
beautifulsoup4==4.12.0
pandas==2.1.0
openpyxl==3.1.0
google-generativeai==0.3.0
gspread==6.0.0
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.115.0
```

- [ ] **Step 2: 创建 FastAPI 入口**

`python_backend/main.py`:
```python
"""Python FastAPI 后端服务 - B2B Global 获客系统"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.scraper import router as scraper_router
from api.keywords import router as keywords_router
from api.sync import router as sync_router
from api.config import router as config_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Python 后端服务启动")
    yield
    logger.info("Python 后端服务关闭")


app = FastAPI(
    title="B2B Global API",
    description="B2B Global 获客系统后端 API",
    version="3.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为 Tauri 前端
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(scraper_router, prefix="/api/scraper", tags=["scraper"])
app.include_router(keywords_router, prefix="/api/keywords", tags=["keywords"])
app.include_router(sync_router, prefix="/api/sync", tags=["sync"])
app.include_router(config_router, prefix="/api/config", tags=["config"])


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "3.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
```

- [ ] **Step 3: 创建 Pydantic 模型**

`python_backend/models/schemas.py`:
```python
"""Pydantic 数据模型"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Location(BaseModel):
    """地理位置"""
    country: str
    city: str
    district: str


class ScrapeRequest(BaseModel):
    """抓取请求"""
    keywords: List[str]
    location: Location
    concurrency: int = 3


class ScrapeStatus(BaseModel):
    """抓取状态"""
    is_running: bool
    total_found: int
    email_found: int
    synced_count: int
    current_keyword: Optional[str] = None
    output_dir: Optional[str] = None


class KeywordItem(BaseModel):
    """关键词项"""
    english: str
    chinese: str
    selected: bool = True


class AIGenerateRequest(BaseModel):
    """AI 生成请求"""
    seed_word: str
    num: int = 7


class SyncRequest(BaseModel):
    """同步请求"""
    file_path: Optional[str] = None
    dir_path: Optional[str] = None
    target_title: str = "lengdangb2b"
    by_date: bool = False
    conflict_resolution: str = "keep_latest"


class ConfigItem(BaseModel):
    """配置项"""
    proxy: Optional[str] = None
    sheets_id: Optional[str] = None
    gemini_api_key: Optional[str] = None
    doubao_api_key: Optional[str] = None
    doubao_base_url: Optional[str] = None
    doubao_model_endpoint: Optional[str] = None
    sync_by_date: bool = False
    conflict_resolution: str = "keep_latest"


class LogEntry(BaseModel):
    """日志条目"""
    timestamp: str
    message: str
    level: str = "info"


class ProgressUpdate(BaseModel):
    """进度更新"""
    total: int
    email: int
    synced: int
```

---

## Phase 2: Python 后端 API 服务

### Task 2.1: 迁移抓取核心逻辑

**Files:**
- Create: `tauri-app/python_backend/core/scraper_controller.py`
- Create: `tauri-app/python_backend/api/scraper.py`

**Steps:**

- [ ] **Step 1: 迁移 ScraperController**

从现有 `core/scraper_controller.py` 迁移，修改为 FastAPI 兼容的异步模式：

```python
"""抓取控制器 - FastAPI 版本"""

import os
import asyncio
from datetime import datetime
from typing import Optional, Callable, List
from fastapi import APIRouter, BackgroundTasks
from sse_starlette.sse import EventSourceResponse

from models.schemas import ScrapeRequest, ScrapeStatus, ProgressUpdate
from scraper.google_maps import scrape_google_maps
from config import HTTP_PROXY

router = APIRouter()


class ScraperController:
    """抓取控制器"""
    
    def __init__(self):
        self.is_running = False
        self.stop_event = asyncio.Event()
        self.total_found = 0
        self.email_found = 0
        self.synced_count = 0
        self.output_dir = None
        self.logs: List[dict] = []
        self.progress_callbacks: List[Callable] = []
    
    async def start_scraping(self, request: ScrapeRequest):
        """开始抓取"""
        if self.is_running:
            return {"error": "已有任务正在运行"}
        
        self.is_running = True
        self.stop_event.clear()
        self.total_found = 0
        self.email_found = 0
        self.logs = []
        
        # 创建输出目录
        session_folder = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.output_dir = os.path.join("Downloads", session_folder)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self._log(f"本次任务文件将保存至: {self.output_dir}", "info")
        
        # 启动抓取任务
        asyncio.create_task(self._scraping_worker(request))
        
        return {"status": "started", "output_dir": self.output_dir}
    
    async def _scraping_worker(self, request: ScrapeRequest):
        """抓取工作协程"""
        try:
            # 复用现有 google_maps_scraper.py 逻辑
            # ... (完整迁移现有逻辑)
            pass
        except Exception as e:
            self._log(f"抓取异常: {str(e)}", "error")
        finally:
            self.is_running = False
    
    def stop_scraping(self):
        """停止抓取"""
        self.is_running = False
        self.stop_event.set()
        return {"status": "stopped"}
    
    def get_status(self) -> ScrapeStatus:
        """获取状态"""
        return ScrapeStatus(
            is_running=self.is_running,
            total_found=self.total_found,
            email_found=self.email_found,
            synced_count=self.synced_count,
            output_dir=self.output_dir
        )
    
    def _log(self, message: str, level: str = "info"):
        """记录日志"""
        entry = {
            "timestamp": datetime.now().strftime('%H:%M:%S'),
            "message": message,
            "level": level
        }
        self.logs.append(entry)
        # 通知前端
        for callback in self.progress_callbacks:
            callback({"type": "log", "data": entry})


# 全局控制器实例
scraper = ScraperController()


@router.post("/start")
async def start_scraping(request: ScrapeRequest):
    """开始抓取"""
    return await scraper.start_scraping(request)


@router.post("/stop")
async def stop_scraping():
    """停止抓取"""
    return scraper.stop_scraping()


@router.get("/status")
async def get_status():
    """获取抓取状态"""
    return scraper.get_status()


@router.get("/logs")
async def get_logs(limit: int = 100):
    """获取日志"""
    return scraper.logs[-limit:]


@router.get("/progress")
async def progress_stream():
    """SSE 进度流"""
    async def event_generator():
        queue = asyncio.Queue()
        
        def callback(data):
            queue.put_nowait(data)
        
        scraper.progress_callbacks.append(callback)
        try:
            while True:
                data = await queue.get()
                yield {"event": "message", "data": data}
        finally:
            scraper.progress_callbacks.remove(callback)
    
    return EventSourceResponse(event_generator())
```

### Task 2.2: 迁移关键词服务

**Files:**
- Create: `tauri-app/python_backend/core/keyword_service.py`
- Create: `tauri-app/python_backend/api/keywords.py`

**Steps:**

- [ ] **Step 1: 迁移关键词管理**

```python
"""关键词 API"""

from typing import List
from fastapi import APIRouter

from models.schemas import KeywordItem, AIGenerateRequest
from core.keyword_service import KeywordService

router = APIRouter()
keyword_service = KeywordService()


@router.get("/library", response_model=List[KeywordItem])
async def get_library():
    """获取关键词库"""
    return keyword_service.load_keywords()


@router.post("/library")
async def save_to_library(items: List[KeywordItem]):
    """保存到关键词库"""
    return keyword_service.save_keywords(items)


@router.post("/generate")
async def generate_keywords(request: AIGenerateRequest):
    """AI 生成关键词"""
    return await keyword_service.generate_keywords(request.seed_word, request.num)


@router.delete("/library/{keyword}")
async def delete_keyword(keyword: str):
    """删除关键词"""
    return keyword_service.delete_keyword(keyword)
```

### Task 2.3: 迁移同步服务

**Files:**
- Create: `tauri-app/python_backend/api/sync.py`

**Steps:**

- [ ] **Step 1: 创建同步 API**

```python
"""同步 API"""

from fastapi import APIRouter

from models.schemas import SyncRequest
from services.sheet_aggregator import aggregate_and_sync
from google_sheets_service import upload_to_google_sheets

router = APIRouter()


@router.post("/file")
async def sync_file(request: SyncRequest):
    """同步单个文件"""
    # 实现文件同步逻辑
    pass


@router.post("/aggregate")
async def sync_aggregate(request: SyncRequest):
    """汇总同步"""
    # 实现汇总同步逻辑
    pass
```

### Task 2.4: 迁移配置服务

**Files:**
- Create: `tauri-app/python_backend/api/config.py`

**Steps:**

- [ ] **Step 1: 创建配置 API**

```python
"""配置 API"""

from fastapi import APIRouter
from models.schemas import ConfigItem

router = APIRouter()


@router.get("/")
async def get_config():
    """获取配置"""
    # 从 .env 或配置文件读取
    pass


@router.post("/")
async def save_config(config: ConfigItem):
    """保存配置"""
    # 保存到 .env
    pass


@router.post("/test-proxy")
async def test_proxy():
    """测试代理连接"""
    pass
```

---

## Phase 3: Tauri 前端核心架构

### Task 3.1: 创建前端状态管理

**Files:**
- Create: `tauri-app/src/stores/appStore.ts`

**Steps:**

- [ ] **Step 1: 创建 Zustand Store**

```typescript
// src/stores/appStore.ts
import { create } from 'zustand';

interface AppState {
  // 页面状态
  currentPage: string;
  sidebarExpanded: boolean;
  
  // 抓取状态
  isScraping: boolean;
  totalFound: number;
  emailFound: number;
  syncedCount: number;
  logs: LogEntry[];
  
  // 关键词状态
  keywords: KeywordItem[];
  
  // 配置状态
  config: ConfigItem;
  
  // Actions
  setPage: (page: string) => void;
  toggleSidebar: () => void;
  addLog: (entry: LogEntry) => void;
  setScrapingStatus: (status: boolean) => void;
  updateProgress: (total: number, email: number, synced: number) => void;
}

export const useAppStore = create<AppState>((set) => ({
  currentPage: 'engine',
  sidebarExpanded: true,
  isScraping: false,
  totalFound: 0,
  emailFound: 0,
  syncedCount: 0,
  logs: [],
  keywords: [],
  config: {},
  
  setPage: (page) => set({ currentPage: page }),
  toggleSidebar: () => set((state) => ({ sidebarExpanded: !state.sidebarExpanded })),
  addLog: (entry) => set((state) => ({ logs: [...state.logs, entry] })),
  setScrapingStatus: (status) => set({ isScraping: status }),
  updateProgress: (total, email, synced) => set({ totalFound: total, emailFound: email, syncedCount: synced }),
}));
```

### Task 3.2: 创建前端 API 层

**Files:**
- Create: `tauri-app/src/api/pythonApi.ts`

**Steps:**

- [ ] **Step 1: 创建 API 客户端**

```typescript
// src/api/pythonApi.ts
const API_BASE = 'http://127.0.0.1:8000/api';

class PythonAPI {
  private async request(endpoint: string, options?: RequestInit) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    return response.json();
  }

  // 抓取 API
  async startScraping(data: ScrapeRequest) {
    return this.request('/scraper/start', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async stopScraping() {
    return this.request('/scraper/stop', { method: 'POST' });
  }

  async getScraperStatus() {
    return this.request('/scraper/status');
  }

  async getLogs() {
    return this.request('/scraper/logs');
  }

  // 关键词 API
  async getKeywordLibrary() {
    return this.request('/keywords/library');
  }

  async generateKeywords(seedWord: string, num: number) {
    return this.request('/keywords/generate', {
      method: 'POST',
      body: JSON.stringify({ seed_word: seedWord, num }),
    });
  }

  // 同步 API
  async syncFile(filePath: string) {
    return this.request('/sync/file', {
      method: 'POST',
      body: JSON.stringify({ file_path: filePath }),
    });
  }

  async aggregateSync(dirPath: string) {
    return this.request('/sync/aggregate', {
      method: 'POST',
      body: JSON.stringify({ dir_path: dirPath }),
    });
  }

  // 配置 API
  async getConfig() {
    return this.request('/config/');
  }

  async saveConfig(config: ConfigItem) {
    return this.request('/config/', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }
}

export const pythonApi = new PythonAPI();
```

### Task 3.3: 创建 SSE 日志流 Hook

**Files:**
- Create: `tauri-app/src/hooks/useLogs.ts`

**Steps:**

- [ ] **Step 1: 创建日志 Hook**

```typescript
// src/hooks/useLogs.ts
import { useEffect, useCallback } from 'react';
import { useAppStore } from '../stores/appStore';

export function useLogs() {
  const addLog = useAppStore((state) => state.addLog);

  useEffect(() => {
    const eventSource = new EventSource('http://127.0.0.1:8000/api/scraper/progress');
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'log') {
        addLog(data.data);
      }
    };

    return () => eventSource.close();
  }, [addLog]);
}
```

---

## Phase 4: 页面功能实现

### Task 4.1: 创建侧边栏组件

**Files:**
- Create: `tauri-app/src/components/Sidebar.tsx`

**Steps:**

- [ ] **Step 1: 实现可折叠侧边栏**

```tsx
// src/components/Sidebar.tsx
import { useAppStore } from '../stores/appStore';
import { Search, Brain, Cloud, ChevronLeft, ChevronRight } from 'lucide-react';

const navItems = [
  { id: 'engine', label: '获客引擎', icon: Search },
  { id: 'ai', label: 'AI 策略', icon: Brain },
  { id: 'sync', label: '同步设置', icon: Cloud },
];

export function Sidebar() {
  const { currentPage, sidebarExpanded, setPage, toggleSidebar } = useAppStore();

  return (
    <aside
      className={`bg-sidebar flex flex-col transition-all duration-300 ${
        sidebarExpanded ? 'w-56' : 'w-16'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4">
        {sidebarExpanded && (
          <div>
            <h1 className="text-xl font-bold text-white">B2B Global</h1>
            <p className="text-xs text-gray-400">获客系统</p>
          </div>
        )}
        <button
          onClick={toggleSidebar}
          className="p-1 rounded hover:bg-white/10 text-white"
        >
          {sidebarExpanded ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => setPage(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg mb-1 transition-colors ${
                isActive
                  ? 'bg-primary text-white'
                  : 'text-gray-300 hover:bg-white/10'
              }`}
            >
              <Icon size={20} />
              {sidebarExpanded && <span>{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4">
        {sidebarExpanded && (
          <p className="text-xs text-gray-500">v3.0.0</p>
        )}
      </div>
    </aside>
  );
}
```

### Task 4.2: 创建获客引擎页面

**Files:**
- Create: `tauri-app/src/pages/EnginePage.tsx`

**Steps:**

- [ ] **Step 1: 实现状态卡片**

```tsx
// src/components/StatusCard.tsx
interface StatusCardProps {
  title: string;
  value: string;
  color: string;
}

export function StatusCard({ title, value, color }: StatusCardProps) {
  return (
    <div className="bg-card rounded-xl p-4 flex items-center gap-4 border border-gray-700">
      <div className={`w-1 h-12 rounded-full ${color}`} />
      <div>
        <p className="text-sm text-gray-400">{title}</p>
        <p className={`text-2xl font-bold ${color.replace('bg-', 'text-')}`}>{value}</p>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: 实现主页面布局**

```tsx
// src/pages/EnginePage.tsx
import { useState } from 'react';
import { useAppStore } from '../stores/appStore';
import { StatusCard } from '../components/StatusCard';
import { LogPanel } from '../components/LogPanel';
import { pythonApi } from '../api/pythonApi';

export function EnginePage() {
  const { totalFound, emailFound, syncedCount, isScraping, logs } = useAppStore();
  const [keywords, setKeywords] = useState('');
  const [location, setLocation] = useState({ country: '', city: '', district: '' });
  const [concurrency, setConcurrency] = useState(3);

  const handleStart = async () => {
    const keywordList = keywords.split('\n').filter(k => k.trim());
    await pythonApi.startScraping({
      keywords: keywordList,
      location,
      concurrency,
    });
  };

  return (
    <div className="flex flex-col h-full p-6 gap-6">
      {/* Status Cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatusCard title="今日已抓取" value={String(totalFound)} color="bg-primary" />
        <StatusCard title="包含邮箱数" value={String(emailFound)} color="bg-success" />
        <StatusCard title="已同步云端数" value={String(syncedCount)} color="bg-warning" />
        <button className="bg-card rounded-xl p-4 border border-gray-700 hover:border-primary transition-colors">
          数据预览
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 grid grid-cols-3 gap-6 min-h-0">
        {/* Keywords Panel */}
        <div className="bg-card rounded-xl p-4 border border-gray-700 col-span-2">
          <h3 className="text-lg font-semibold mb-4">关键词配置</h3>
          
          {/* Category Select */}
          <div className="mb-4">
            <label className="block text-sm text-gray-400 mb-1">选择行业</label>
            <select className="w-full bg-main border border-gray-700 rounded-lg px-3 py-2">
              <option>卫浴行业</option>
              <option>建材行业</option>
            </select>
          </div>

          {/* AI Generation */}
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              placeholder="种子词..."
              className="flex-1 bg-main border border-gray-700 rounded-lg px-3 py-2"
            />
            <select className="bg-main border border-gray-700 rounded-lg px-3 py-2 w-20">
              {[...Array(20)].map((_, i) => (
                <option key={i} value={i + 1}>{i + 1}</option>
              ))}
            </select>
            <button className="bg-info px-4 py-2 rounded-lg hover:bg-info/80">
              AI 生成
            </button>
          </div>

          {/* Keywords Text Area */}
          <textarea
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            className="w-full h-40 bg-main border border-gray-700 rounded-lg p-3 resize-none"
            placeholder="输入关键词，每行一个..."
          />
        </div>

        {/* Location + Logs Panel */}
        <div className="flex flex-col gap-4">
          {/* Location */}
          <div className="bg-card rounded-xl p-4 border border-gray-700">
            <h3 className="text-lg font-semibold mb-4">地理位置选择</h3>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-gray-400 mb-1">大洲</label>
                <select className="w-full bg-main border border-gray-700 rounded-lg px-3 py-2">
                  <option>中东地区</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">国家</label>
                <select className="w-full bg-main border border-gray-700 rounded-lg px-3 py-2">
                  <option>阿联酋</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">城市</label>
                <select className="w-full bg-main border border-gray-700 rounded-lg px-3 py-2">
                  <option>迪拜</option>
                </select>
              </div>
            </div>

            <div className="flex gap-2 mt-4">
              <button
                onClick={handleStart}
                disabled={isScraping}
                className="flex-1 bg-success px-4 py-2 rounded-lg hover:bg-success/80 disabled:opacity-50"
              >
                {isScraping ? '抓取中...' : '开始获客'}
              </button>
              <button className="bg-danger px-4 py-2 rounded-lg hover:bg-danger/80">
                停止
              </button>
            </div>
          </div>

          {/* Logs */}
          <LogPanel logs={logs} className="flex-1" />
        </div>
      </div>
    </div>
  );
}
```

### Task 4.3: 创建 AI 策略页面

**Files:**
- Create: `tauri-app/src/pages/AIStrategyPage.tsx`

**Steps:**

- [ ] **Step 1: 实现 AI 提示词模板编辑**

```tsx
// src/pages/AIStrategyPage.tsx
import { useState } from 'react';

export function AIStrategyPage() {
  const [prompt, setPrompt] = useState('');

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">AI 策略配置</h2>
      
      <div className="bg-card rounded-xl p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">关键词生成提示词模板</h3>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="w-full h-96 bg-main border border-gray-700 rounded-lg p-4 font-mono text-sm"
        />
        <div className="flex justify-end mt-4">
          <button className="bg-primary px-6 py-2 rounded-lg hover:bg-primary/80">
            保存模板
          </button>
        </div>
      </div>
    </div>
  );
}
```

### Task 4.4: 创建同步设置页面

**Files:**
- Create: `tauri-app/src/pages/SyncSettingsPage.tsx`

**Steps:**

- [ ] **Step 1: 实现同步配置**

```tsx
// src/pages/SyncSettingsPage.tsx
import { useState } from 'react';

export function SyncSettingsPage() {
  const [config, setConfig] = useState({
    proxy: '',
    sheetsId: '',
    geminiApiKey: '',
    doubaoApiKey: '',
    doubaoBaseUrl: '',
    doubaoModelEndpoint: '',
    syncByDate: false,
    conflictResolution: 'keep_latest',
  });

  return (
    <div className="p-6 max-w-2xl">
      <h2 className="text-2xl font-bold mb-6">同步设置</h2>
      
      <div className="bg-card rounded-xl p-6 border border-gray-700 space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">代理地址</label>
          <input
            type="text"
            value={config.proxy}
            onChange={(e) => setConfig({ ...config, proxy: e.target.value })}
            className="w-full bg-main border border-gray-700 rounded-lg px-3 py-2"
            placeholder="http://127.0.0.1:7890"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">Google Sheets ID</label>
          <input
            type="text"
            value={config.sheetsId}
            onChange={(e) => setConfig({ ...config, sheetsId: e.target.value })}
            className="w-full bg-main border border-gray-700 rounded-lg px-3 py-2"
          />
        </div>

        <div className="flex gap-4">
          <button className="bg-primary px-6 py-2 rounded-lg hover:bg-primary/80">
            保存设置
          </button>
          <button className="bg-warning px-6 py-2 rounded-lg hover:bg-warning/80">
            测试代理
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## Phase 5: 数据同步与云服务

### Task 5.1: 实现 Google Sheets 同步

**Files:**
- Create: `tauri-app/python_backend/services/google_sheets_service.py`

**Steps:**

- [ ] **Step 1: 迁移现有同步逻辑**

从现有 `google_sheets_service.py` 完整迁移，保持所有功能：
- 单文件同步
- 汇总同步
- 去重逻辑
- 冲突处理

### Task 5.2: 实现数据预览

**Files:**
- Create: `tauri-app/src/components/DataTable.tsx`

**Steps:**

- [ ] **Step 1: 使用 TanStack Table**

```tsx
// src/components/DataTable.tsx
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
} from '@tanstack/react-table';

interface DataTableProps {
  data: any[];
  columns: any[];
}

export function DataTable({ data, columns }: DataTableProps) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div className="overflow-auto">
      <table className="w-full">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id} className="text-left p-2 border-b border-gray-700">
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="hover:bg-white/5">
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="p-2 border-b border-gray-700/50">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## Phase 6: Bug 修复与优化

### Task 6.1: 修复已知 Bug

**已知问题清单:**

- [ ] **Bug 1: 日志过滤未实现**
  - 文件: `gui/components/log_panel.py:86`
  - 修复: 在 Tauri 版本中实现日志级别过滤

- [ ] **Bug 2: AI 生成关键词超时处理**
  - 文件: `ai_generator.py`
  - 修复: 添加更优雅的超时和降级处理

- [ ] **Bug 3: 抓取过程中浏览器崩溃**
  - 文件: `scraper/google_maps.py`
  - 修复: 添加浏览器实例健康检查和自动重启

- [ ] **Bug 4: Google Auth 令牌过期**
  - 文件: `google_auth.py`
  - 修复: 自动刷新令牌，避免频繁重新授权

- [ ] **Bug 5: 并发抓取时数据竞争**
  - 修复: 使用 asyncio.Lock 保护共享状态

### Task 6.2: 性能优化

**优化项:**

- [ ] **优化 1: 虚拟滚动**
  - 大数据表格使用虚拟滚动，避免渲染过多 DOM

- [ ] **优化 2: 日志节流**
  - 高频日志更新使用节流，避免 UI 卡顿

- [ ] **优化 3: 图片懒加载**
  - 数据预览中的图片使用懒加载

- [ ] **优化 4: 数据库缓存**
  - 关键词库使用 SQLite 替代 JSON 文件

---

## Phase 7: 打包与部署

### Task 7.1: Tauri 打包配置

**Files:**
- Modify: `tauri-app/src-tauri/tauri.conf.json`

**Steps:**

- [ ] **Step 1: 配置 Windows 打包**

```json
{
  "bundle": {
    "active": true,
    "targets": ["msi", "nsis"],
    "identifier": "com.b2bglobal.app",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "windows": {
      "certificateThumbprint": null,
      "digestAlgorithm": "sha256",
      "timestampUrl": "",
      "nsis": {
        "installerIcon": "icons/icon.ico",
        "installMode": "both"
      }
    }
  }
}
```

### Task 7.2: Python 后端打包

**Files:**
- Create: `tauri-app/python_backend/build.py`

**Steps:**

- [ ] **Step 1: 使用 PyInstaller 打包 Python**

```python
# build.py
import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--name=b2b-backend',
    '--onefile',
    '--windowed',
    '--add-data=scraper;scraper',
    '--add-data=services;services',
    '--add-data=core;core',
    '--add-data=data.py;.',
    '--hidden-import=playwright',
    '--hidden-import=google.auth',
])
```

### Task 7.3: 一键启动脚本

**Files:**
- Create: `tauri-app/launcher.bat`

**Steps:**

- [ ] **Step 1: 创建 Windows 启动脚本**

```batch
@echo off
start "" "b2b-backend.exe"
timeout /t 3
start "" "B2B Global.exe"
```

---

## 附录

### A. 现有功能完整清单

| 功能模块 | 功能点 | 优先级 |
|----------|--------|--------|
| **获客引擎** | 关键词输入/选择 | P0 |
| | AI 关键词生成 | P0 |
| | 地理位置选择 (大洲/国家/城市/区域) | P0 |
| | 手动地址输入 | P0 |
| | 并发数设置 | P0 |
| | 开始/停止抓取 | P0 |
| | 实时日志显示 | P0 |
| | 状态统计 (已抓取/邮箱/同步) | P0 |
| | 数据预览 | P1 |
| | 导出日志 | P2 |
| **关键词库** | 关键词列表展示 | P0 |
| | 搜索过滤 | P0 |
| | 全选/反选 | P0 |
| | 导入/导出 | P1 |
| | 删除选中 | P1 |
| | 加载到引擎 | P0 |
| **AI 策略** | 提示词模板编辑 | P0 |
| | 保存模板 | P0 |
| **同步设置** | 代理配置 | P0 |
| | Google Sheets ID | P0 |
| | API Key 配置 | P0 |
| | 同步模式设置 | P1 |
| | 冲突处理策略 | P1 |
| | 测试代理 | P0 |
| **数据同步** | 单文件同步 | P0 |
| | 汇总同步 | P0 |
| | 去重逻辑 | P0 |
| | 云端合并 | P0 |
| | 新增数据单独保存 | P0 |
| **系统** | 窗口大小记忆 | P1 |
| | 配置持久化 | P0 |
| | 关键词记忆 | P1 |

### B. 技术栈版本

| 组件 | 版本 |
|------|------|
| Tauri | 2.0 |
| React | 18.2 |
| TypeScript | 5.3 |
| Tailwind CSS | 3.4 |
| Vite | 5.0 |
| Zustand | 4.5 |
| FastAPI | 0.109 |
| Python | 3.11 |
| Playwright | 1.40 |

### C. 文件映射 (旧 → 新)

| 旧文件 | 新文件 | 说明 |
|--------|--------|------|
| `main.py` | `tauri-app/src/main.tsx` | 入口 |
| `gui/app.py` | `tauri-app/src/App.tsx` | 主应用 |
| `gui/components/sidebar.py` | `tauri-app/src/components/Sidebar.tsx` | 侧边栏 |
| `gui/components/status_card.py` | `tauri-app/src/components/StatusCard.tsx` | 状态卡片 |
| `gui/components/log_panel.py` | `tauri-app/src/components/LogPanel.tsx` | 日志面板 |
| `gui/pages/engine_page.py` | `tauri-app/src/pages/EnginePage.tsx` | 获客引擎 |
| `gui/pages/ai_strategy_page.py` | `tauri-app/src/pages/AIStrategyPage.tsx` | AI 策略 |
| `gui/pages/sync_settings_page.py` | `tauri-app/src/pages/SyncSettingsPage.tsx` | 同步设置 |
| `core/scraper_controller.py` | `tauri-app/python_backend/core/scraper_controller.py` | 抓取控制 |
| `core/keyword_service.py` | `tauri-app/python_backend/core/keyword_service.py` | 关键词服务 |
| `services/sheet_aggregator.py` | `tauri-app/python_backend/services/sheet_aggregator.py` | 汇总同步 |
| `google_sheets_service.py` | `tauri-app/python_backend/services/google_sheets_service.py` | Sheets 服务 |
| `google_maps_scraper.py` | `tauri-app/python_backend/scraper/google_maps.py` | 抓取实现 |
| `ai_generator.py` | `tauri-app/python_backend/core/keyword_service.py` | AI 生成 |
| `data.py` | `tauri-app/python_backend/data.py` | 数据定义 |
| `config.py` | `tauri-app/python_backend/config.py` | 配置 |

---

## 执行建议

### 开发顺序

1. **Week 1:** Phase 0-1 (保存版本 + 框架搭建)
2. **Week 2:** Phase 2 (Python 后端 API)
3. **Week 3:** Phase 3-4 (前端核心 + 页面实现)
4. **Week 4:** Phase 5-6 (同步 + Bug 修复)
5. **Week 5:** Phase 7 (打包 + 测试)

### 关键决策点

1. **前端框架:** React + TypeScript (推荐) vs Vue
2. **状态管理:** Zustand (推荐) vs Redux
3. **UI 组件库:** 自定义 (推荐) vs shadcn/ui
4. **表格组件:** TanStack Table (推荐) vs AG Grid
5. **Python 打包:** PyInstaller (推荐) vs Nuitka

### 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Playwright 在打包后路径问题 | 高 | 测试打包后的浏览器启动 |
| Google Auth 流程在 Tauri 内 | 中 | 使用系统浏览器 OAuth |
| SSE 跨域问题 | 低 | 配置 CORS |
| 前端体积过大 | 中 | 代码分割 + 懒加载 |
| Python 后端启动失败 | 高 | 添加健康检查和重试 |

"""
FastAPI 入口：开发时从项目根目录执行
  python -m uvicorn backend.main:app --host 127.0.0.1 --port 8756 --reload
"""

from __future__ import annotations

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# 保证可 import core、scraper、services（工作目录未必是根时）
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.deps import get_scraper_controller
from backend.routers import (
    ai,
    config,
    data,
    google_oauth,
    keywords,
    logs,
    meta,
    scraper,
    sync,
    system,
    whatsapp,
)
from backend.schemas.common import HealthResponse
from backend.services.log_bus import log_bus

API_VERSION = "0.2.0"

# 调试：打印 sys.path 和 backend 模块路径
import logging
logger = logging.getLogger("main")
logger.info(f"sys.path={sys.path}")
try:
    import backend
    logger.info(f"backend module file={backend.__file__}")
    logger.info(f"backend module path={backend.__path__}")
except Exception as e:
    logger.error(f"Failed to import backend: {e}")

OPENAPI_TAGS = [
    {"name": "health", "description": "进程存活与版本"},
    {"name": "scraper", "description": "地图抓取启停与状态"},
    {"name": "keywords", "description": "关键词库与 AI 生成"},
    {"name": "sync", "description": "Google Sheets 同步与汇总"},
    {"name": "config", "description": "应用配置（响应脱敏）"},
    {"name": "whatsapp", "description": "WhatsApp Node 服务探测与代理"},
    {"name": "logs", "description": "运行日志（SSE）"},
    {"name": "meta", "description": "行业与地理静态数据"},
    {"name": "ai", "description": "AI 提示词模板"},
    {"name": "system", "description": "代理与系统探测"},
    {"name": "data", "description": "数据预览与 Downloads 会话"},
    {"name": "google_oauth", "description": "Google OAuth 与 token 刷新"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_bus.set_loop(asyncio.get_running_loop())
    ctrl = get_scraper_controller()

    def on_status(msg: str, level: str = "info") -> None:
        log_bus.publish(msg, level)

    def on_progress(a: int, b: int, c: int) -> None:
        log_bus.publish(f"进度：已抓取 {a}，邮箱 {b}，已同步 {c}", "info")

    ctrl.on_status_update = on_status
    ctrl.on_progress_update = on_progress
    yield


app = FastAPI(
    title="B2B Global 获客系统 API",
    version=API_VERSION,
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
    description=(
        "桌面壳（Tauri）通过本服务操作既有 Python 业务模块。"
        " OpenAPI JSON：`GET /openapi.json`；交互文档：`GET /docs`。"
    ),
)

allowed_origins = [
    "http://localhost:1420",      # Tauri dev
    "http://localhost:3000",      # Vite dev
    "http://127.0.0.1:1420",      # Tauri dev (IP)
    "http://127.0.0.1:3000",      # Vite dev (IP)
    "tauri://localhost",          # Tauri production
]

if os.environ.get("B2B_CORS_ORIGIN"):
    allowed_origins.append(os.environ.get("B2B_CORS_ORIGIN"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(scraper.router, prefix="/api/scraper", tags=["scraper"])
app.include_router(keywords.router, prefix="/api/keywords", tags=["keywords"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["whatsapp"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(meta.router, prefix="/api/meta", tags=["meta"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(google_oauth.router, prefix="/api/google/oauth", tags=["google_oauth"])


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health():
    return HealthResponse(version=API_VERSION, python_path=sys.executable)


@app.get("/debug/modules")
def debug_modules():
    import backend.routers.keywords as kw
    return {
        "keywords_module_file": kw.__file__,
        "keywords_module_path": str(kw.__path__) if hasattr(kw, '__path__') else 'N/A',
        "sys_path": sys.path,
    }

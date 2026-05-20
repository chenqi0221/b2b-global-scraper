"""系统级操作：健康检查、代理连通性测试、进程重启。"""

from __future__ import annotations

import asyncio
import os
import signal
import sys

from fastapi import APIRouter

from async_utils import run_coro_in_new_loop
from backend.path_utils import project_root
from backend.services.log_bus import log_bus

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "pid": os.getpid()}


@router.get("/project-root")
def get_project_root():
    return {"root": str(project_root())}


@router.post("/restart")
async def restart_backend():
    def _restart():
        os.kill(os.getpid(), signal.SIGTERM)

    asyncio.get_event_loop().call_later(0.3, _restart)
    return {"ok": True, "message": "后端正在重启..."}


@router.post("/test-proxy")
async def test_proxy():
    from scraper_core import test_connection

    def cb(msg: str) -> None:
        log_bus.publish(msg, "info")

    def run() -> bool:
        return bool(run_coro_in_new_loop(test_connection(cb)))

    ok = await asyncio.to_thread(run)
    return {"ok": ok}

"""系统级操作：代理连通性测试。"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter

from async_utils import run_coro_in_new_loop
from backend.path_utils import project_root
from backend.services.log_bus import log_bus

router = APIRouter()


@router.get("/project-root")
def get_project_root():
    return {"root": str(project_root())}


@router.post("/test-proxy")
async def test_proxy():
    from scraper_core import test_connection

    def cb(msg: str) -> None:
        log_bus.publish(msg, "info")

    def run() -> bool:
        return bool(run_coro_in_new_loop(test_connection(cb)))

    ok = await asyncio.to_thread(run)
    return {"ok": ok}

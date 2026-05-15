"""WhatsApp Node 服务：健康检查、状态代理、可选广播转发、地图 CSV 电话预览。"""

from __future__ import annotations

import os
from typing import Optional

import httpx
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.path_utils import resolve_under_root

router = APIRouter()


def _wa_base() -> str:
    return os.environ.get("WA_SERVICE_URL", "http://127.0.0.1:3003").rstrip("/")


@router.get("/health")
async def whatsapp_upstream_health():
    """探测 WhatsApp Node 服务端口是否可达（不校验业务路由）。"""
    url = f"{_wa_base()}/api/status"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(url, follow_redirects=True)
            return {"ok": True, "upstream_status": r.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/upstream-status")
async def whatsapp_upstream_status_json():
    """透传 Node `GET /api/status` JSON（扫码状态、ready 等）。"""
    url = f"{_wa_base()}/api/status"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url, follow_redirects=True)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"无法连接 WhatsApp 服务: {e}") from e


@router.get("/daily-stats")
async def whatsapp_daily_stats():
    url = f"{_wa_base()}/api/daily-stats"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url, follow_redirects=True)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


class BroadcastProxyBody(BaseModel):
    """与 `third_party/whatsapp-service/API.md` 中 POST /api/broadcast 对齐。"""

    message: list[str] = Field(..., min_length=1)
    interval: int = 10000
    randomInterval: bool = True
    randomizeMsg: bool = True
    lengthRandomize: bool = True
    simulateTyping: bool = False
    simulateMouse: bool = False
    respectHours: bool = True
    randomPause: bool = True
    excludeGroups: bool = True
    personalize: bool = False
    targetType: str = "chats"
    accountLevel: str = "new"


@router.post("/broadcast")
async def whatsapp_broadcast_proxy(body: BroadcastProxyBody):
    """将广播请求转发到本地 Node（需已登录 WhatsApp）。"""
    url = f"{_wa_base()}/api/broadcast"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(url, json=body.model_dump(), follow_redirects=True)
            return r.json() if r.content else {"ok": r.ok, "status_code": r.status_code}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


_PHONE_COLUMNS = ("phone", "mobile", "tel", "电话", "手机", "whatsapp")


@router.get("/map-csv-phones")
def map_csv_phones_preview(
    path: str = Query(..., description="项目根下的 CSV"),
    limit: int = Query(50, ge=1, le=500),
):
    """从地图导出 CSV 中提取电话列（用于与 WhatsApp 联动前的号码预览）。"""
    p = resolve_under_root(path, must_exist=True, expect_dir=False)
    if p.suffix.lower() != ".csv":
        raise HTTPException(400, detail="需要 CSV")
    try:
        df = pd.read_csv(p, nrows=500)
    except Exception as e:
        raise HTTPException(400, detail=f"读取失败: {e}") from e
    col: Optional[str] = None
    lower = {str(c).lower(): str(c) for c in df.columns}
    for key in _PHONE_COLUMNS:
        if key in lower:
            col = lower[key]
            break
    if col is None:
        for c in df.columns:
            if "phone" in str(c).lower():
                col = str(c)
                break
    if col is None:
        return {"path": str(p), "phone_column": None, "phones": [], "hint": "未识别电话列，请确认 CSV 含 Phone 等列名"}
    series = df[col].dropna().astype(str).str.strip()
    phones = [x for x in series.tolist() if x and x != "nan"][:limit]
    return {"path": str(p), "phone_column": col, "phones": phones, "total_sampled": int(len(df))}

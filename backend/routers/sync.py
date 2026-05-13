"""Google 同步：单文件、汇总（与 `gui.app` 行为对齐）。"""

from __future__ import annotations

import asyncio
import io

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from async_utils import run_coro_in_new_loop
from backend.path_utils import resolve_under_root
from backend.schemas.settings import AggregateSyncBody, SyncFileBody
from backend.services.log_bus import log_bus
from google_sheets_service import upload_to_google_sheets
from services.sheet_aggregator import aggregate_and_sync

router = APIRouter()


def _log(msg: str, level: str = "info") -> None:
    log_bus.publish(msg, level)


@router.post("/file")
async def sync_single_csv(body: SyncFileBody):
    """路径须在项目根下（Tauri 选盘返回绝对路径）。"""
    path = resolve_under_root(body.file_path, must_exist=True, expect_dir=False)
    if path.suffix.lower() != ".csv":
        raise HTTPException(400, detail="需要 CSV 文件")

    def _run() -> bool:
        if path.stat().st_size == 0:
            _log("文件为空", "warning")
            return False
        df = pd.read_csv(path)
        if df.empty:
            _log("CSV 无数据行", "warning")
            return False
        title = path.stem
        _log(f"开始同步文件: {title}", "info")
        ok, _ = run_coro_in_new_loop(upload_to_google_sheets(df, title, _log))
        return bool(ok)

    ok = await asyncio.to_thread(_run)
    return {"ok": ok, "file": str(path)}


@router.post("/upload-csv")
async def sync_upload_csv(file: UploadFile = File(...)):
    """表单上传 CSV（浏览器 / Tauri 通用）。"""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, detail="请上传 .csv 文件")

    raw = await file.read()
    if not raw:
        raise HTTPException(400, detail="空文件")

    title = file.filename.rsplit(".", 1)[0]

    def _run() -> bool:
        df = pd.read_csv(io.BytesIO(raw))
        if df.empty:
            _log("CSV 无数据行", "warning")
            return False
        _log(f"开始同步上传文件: {title}", "info")
        ok, _ = run_coro_in_new_loop(upload_to_google_sheets(df, title, _log))
        return bool(ok)

    ok = await asyncio.to_thread(_run)
    return {"ok": ok, "title": title}


@router.post("/aggregate")
async def sync_aggregate(body: AggregateSyncBody):
    dir_path = resolve_under_root(body.dir_path, must_exist=True, expect_dir=True)

    def _run() -> bool:
        return run_coro_in_new_loop(
            aggregate_and_sync(
                str(dir_path),
                _log,
                target_title=body.target_title,
                by_date=body.by_date,
                conflict_resolution=body.conflict_resolution,
            )
        )

    ok = await asyncio.to_thread(_run)
    return {"ok": ok, "dir": str(dir_path)}

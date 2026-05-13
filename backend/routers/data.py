"""数据预览：Downloads 会话目录与 CSV 抽样。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from backend.path_utils import downloads_dir, project_root, resolve_under_root

router = APIRouter()


@router.get("/downloads-sessions")
def list_download_sessions():
    dd = downloads_dir()
    if not dd.is_dir():
        return []
    dirs = [p for p in dd.iterdir() if p.is_dir()]
    dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [{"name": p.name, "path": str(p)} for p in dirs[:80]]


@router.get("/root-csv")
def find_root_summary_csv():
    """根目录 `lengdangb2b.csv` 等汇总文件。"""
    root = project_root()
    candidates = sorted(root.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [{"name": p.name, "path": str(p)} for p in candidates[:20]]


@router.get("/preview-csv")
def preview_csv(
    path: str = Query(..., description="项目根下的 CSV 文件路径，或 Downloads 会话目录（取目录内最新 CSV）"),
    limit: int = Query(80, ge=1, le=500),
):
    p = resolve_under_root(path, must_exist=True, expect_dir=None)
    if p.is_dir():
        csvs = sorted(
            [x for x in p.iterdir() if x.is_file() and x.suffix.lower() == ".csv"],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )
        if not csvs:
            raise HTTPException(400, detail="该目录下没有 CSV 文件")
        p = csvs[0]
    elif p.suffix.lower() != ".csv":
        raise HTTPException(400, detail="需要 CSV")
    try:
        df = pd.read_csv(p, nrows=limit)
    except Exception as e:
        raise HTTPException(400, detail=f"读取失败: {e}") from e
    return {
        "path": str(p),
        "columns": [str(c) for c in df.columns],
        "rows": df.fillna("").to_dict(orient="records"),
    }

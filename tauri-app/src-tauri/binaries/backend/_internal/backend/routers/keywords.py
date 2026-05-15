"""关键词库 HTTP API（封装 `keyword_manager`）。"""

from __future__ import annotations

import asyncio
import io
import os
import tempfile
from typing import List

import pandas as pd
from fastapi import APIRouter, Body, File, HTTPException, UploadFile
from fastapi.responses import Response

from async_utils import run_coro_in_new_loop
import keyword_manager
from backend.schemas.settings import AiGenBody, KeywordDeleteBody, KeywordPair

router = APIRouter()


@router.get("/library")
def get_library():
    rows = keyword_manager.load_keywords()
    result = []
    for r in rows:
        if isinstance(r, dict):
            result.append({"en": r.get("en", ""), "zh": r.get("zh", "")})
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            result.append({"en": r[0], "zh": r[1]})
        else:
            result.append({"en": str(r), "zh": ""})
    return result


@router.post("/library/append")
def append_library(items: List[KeywordPair] = Body(...)):
    pairs = [(x.en.strip(), (x.zh or "").strip()) for x in items if x.en.strip()]
    if not pairs:
        raise HTTPException(400, detail="无有效关键词")
    ok, added = keyword_manager.save_keywords(pairs)
    return {"ok": ok, "added": added}


@router.post("/library/delete")
def delete_library(body: KeywordDeleteBody):
    pairs = [(x.en, x.zh or "") for x in body.items]
    ok, msg = keyword_manager.delete_keywords(pairs)
    return {"ok": ok, "message": msg}


@router.post("/library/import")
async def import_library(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, detail="请上传 CSV")
    raw = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tf:
        tf.write(raw)
        tpath = tf.name
    try:
        ok, msg = keyword_manager.import_keywords(tpath)
    finally:
        try:
            os.unlink(tpath)
        except OSError:
            pass
    return {"ok": ok, "message": msg}


@router.get("/library/export")
def export_library():
    rows = keyword_manager.load_keywords()
    if not rows:
        raise HTTPException(400, detail="关键词库为空")
    df = pd.DataFrame(rows, columns=["English Keyword", "Chinese Translation"])
    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig")
    return Response(
        content=buf.getvalue().encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="keywords_library.csv"',
        },
    )


@router.post("/generate")
async def generate_keywords(body: AiGenBody):
    from scraper_core import generate_keywords_with_ai

    def run():
        return run_coro_in_new_loop(generate_keywords_with_ai(body.seed, body.num))

    pairs = await asyncio.to_thread(run)
    out = [{"en": a, "zh": b} for a, b in (pairs or [])]
    return {"ok": True, "keywords": out}

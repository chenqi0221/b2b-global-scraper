"""运行日志 SSE（与 `gui` LogPanel 等价的数据源）。"""

from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.services.log_bus import LogEntry, log_bus

router = APIRouter()


def _format_sse(entry: LogEntry) -> str:
    payload = json.dumps(
        {"id": entry.id, "ts": entry.ts, "level": entry.level, "message": entry.message},
        ensure_ascii=False,
    )
    return f"id: {entry.id}\nevent: log\ndata: {payload}\n\n"


async def _log_event_stream() -> AsyncIterator[bytes]:
    q = log_bus.subscribe()
    try:
        yield b": connected\n\n"
        for e in log_bus.snapshot(since_id=0, limit=200):
            yield _format_sse(e).encode("utf-8")
        while True:
            try:
                entry = await asyncio.wait_for(q.get(), timeout=12.0)
            except asyncio.TimeoutError:
                yield b": keepalive\n\n"
                continue
            yield _format_sse(entry).encode("utf-8")
    finally:
        log_bus.unsubscribe(q)


@router.get("/stream")
async def stream_logs():
    return StreamingResponse(
        _log_event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

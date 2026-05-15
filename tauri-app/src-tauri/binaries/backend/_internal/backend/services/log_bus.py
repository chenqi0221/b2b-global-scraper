"""抓取与系统日志总线：线程安全写入 + 异步 SSE 订阅。"""

from __future__ import annotations

import asyncio
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional


@dataclass(frozen=True)
class LogEntry:
    id: int
    ts: float
    level: str
    message: str


class LogBus:
    def __init__(self, maxlen: int = 2000) -> None:
        self._lock = threading.Lock()
        self._seq = 0
        self._recent: Deque[LogEntry] = deque(maxlen=maxlen)
        self._queues: List[asyncio.Queue[LogEntry]] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def publish(self, message: str, level: str = "info") -> None:
        with self._lock:
            self._seq += 1
            entry = LogEntry(id=self._seq, ts=time.time(), level=level, message=message)
            self._recent.append(entry)
            queues = list(self._queues)
        loop = self._loop
        if not loop:
            return

        def notify(q: asyncio.Queue[LogEntry], e: LogEntry) -> None:
            try:
                q.put_nowait(e)
            except asyncio.QueueFull:
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    q.put_nowait(e)
                except asyncio.QueueFull:
                    pass

        for q in queues:
            loop.call_soon_threadsafe(notify, q, entry)

    def subscribe(self, maxsize: int = 256) -> asyncio.Queue[LogEntry]:
        q: asyncio.Queue[LogEntry] = asyncio.Queue(maxsize=maxsize)
        with self._lock:
            self._queues.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[LogEntry]) -> None:
        with self._lock:
            try:
                self._queues.remove(q)
            except ValueError:
                pass

    def snapshot(self, since_id: int = 0, limit: Optional[int] = None) -> List[LogEntry]:
        with self._lock:
            rows = [e for e in self._recent if e.id > since_id]
        if limit is not None:
            rows = rows[-limit:]
        return rows


log_bus = LogBus()

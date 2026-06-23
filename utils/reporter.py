"""统一状态报告接口与旧回调适配器。"""

import inspect
from typing import Callable, Optional, Protocol


class StatusReporter(Protocol):
    """统一状态报告接口：兼容 (msg) 与 (msg, level) 两种旧回调。"""

    def __call__(self, message: str, level: str = "info") -> None: ...


def _noop_reporter(message: str, level: str = "info") -> None:
    pass


def as_status_reporter(callback: Optional[Callable]) -> StatusReporter:
    """将旧的单参数回调适配为 StatusReporter；已是两参数则直接返回。"""
    if callback is None:
        return _noop_reporter
    sig = inspect.signature(callback)
    if len(sig.parameters) == 1:
        def _legacy(message: str, level: str = "info") -> None:
            callback(message)
        return _legacy
    return callback

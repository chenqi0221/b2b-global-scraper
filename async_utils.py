import asyncio
from contextlib import contextmanager


@contextmanager
def new_event_loop():
    """
    在当前线程创建一个新的 asyncio 事件循环，并在退出时关闭。

    用于 GUI 场景：Tk 主线程不要直接跑 event loop，
    而在后台线程中短暂创建/关闭，避免重复样板代码。
    """
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        yield loop
    finally:
        try:
            loop.close()
        except Exception:
            # 关闭失败不影响主流程
            pass


def run_coro_in_new_loop(coro):
    """同步执行协程：在新事件循环中 run_until_complete，然后关闭循环。"""
    with new_event_loop() as loop:
        return loop.run_until_complete(coro)


import asyncio
import threading
from typing import TypeVar, Callable, Awaitable, Optional, Union

T = TypeVar("T")


def run_coro_in_new_loop(
    coro: Union[Callable[..., Awaitable[T]], Awaitable[T]],
    *args,
    timeout: Optional[float] = None,
    **kwargs,
) -> T:
    result = None
    exception = None

    def _runner():
        nonlocal result, exception
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            if callable(coro):
                result = loop.run_until_complete(coro(*args, **kwargs))
            else:
                result = loop.run_until_complete(coro)
        except Exception as e:
            exception = e
        finally:
            loop.close()

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if exception is not None:
        raise exception
    if thread.is_alive():
        raise TimeoutError(f"协程执行超时 ({timeout}s)")
    return result
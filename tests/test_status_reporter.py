"""统一状态报告接口的兼容性测试。"""

from utils.reporter import as_status_reporter


def test_legacy_single_arg_callback():
    messages = []

    def cb(msg):
        messages.append(msg)

    reporter = as_status_reporter(cb)
    reporter("hello", "warning")
    reporter("world")
    assert messages == ["hello", "world"]


def test_two_arg_callback_passthrough():
    calls = []

    def cb(msg, level="info"):
        calls.append((msg, level))

    reporter = as_status_reporter(cb)
    reporter("hello", "warning")
    reporter("world")
    assert calls == [("hello", "warning"), ("world", "info")]


def test_none_callback_is_noop():
    reporter = as_status_reporter(None)
    reporter("ignored", "error")  # 不应抛出异常

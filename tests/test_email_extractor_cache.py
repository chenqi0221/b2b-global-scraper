"""邮箱提取器熔断与缓存测试。"""

import asyncio

from scraper import email_extractor


def test_failed_domain_is_cached(monkeypatch):
    email_extractor._FAILED_DOMAINS.clear()
    email_extractor._REQUEST_COUNT = 0

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, *args, **kwargs):
            raise ConnectionError("no network")

    monkeypatch.setattr(email_extractor.httpx, "AsyncClient", FakeClient)

    result = asyncio.run(email_extractor.find_emails_on_website("https://example.com"))
    assert result == ""
    assert "example.com" in email_extractor._FAILED_DOMAINS


def test_failed_domain_short_circuits():
    email_extractor._FAILED_DOMAINS.clear()
    email_extractor._REQUEST_COUNT = 0
    email_extractor._FAILED_DOMAINS.add("blocked.example.com")

    result = asyncio.run(email_extractor.find_emails_on_website("https://blocked.example.com"))
    assert result == ""
    assert email_extractor._REQUEST_COUNT == 0


def test_decode_obfuscated_email():
    sample = "contact us: sales [at] example [dot] com or info (AT) example (DOT) com"
    decoded = email_extractor._decode_obfuscated_emails(sample)
    assert "sales@example.com" in decoded
    assert "info@example.com" in decoded

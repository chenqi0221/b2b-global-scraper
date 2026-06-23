"""浏览器启动预检与熔断测试。"""

from core.scraper_controller import _any_browser_available


def test_any_browser_available_finds_none_when_no_paths(monkeypatch):
    monkeypatch.setattr("core.scraper_controller._get_bundled_chromium_path", lambda: None)
    monkeypatch.setattr("core.scraper_controller._find_chrome_executable", lambda: None)
    monkeypatch.setattr("core.scraper_controller._find_edge_executable", lambda: None)
    monkeypatch.setattr("core.scraper_controller._get_playwright_installed_chromium_path", lambda: None)

    ok, strategy = _any_browser_available()
    assert ok is False
    assert strategy is None


def test_any_browser_available_prefers_bundled(monkeypatch):
    monkeypatch.setattr("core.scraper_controller._get_bundled_chromium_path", lambda: "/fake/chrome.exe")
    monkeypatch.setattr("core.scraper_controller._find_chrome_executable", lambda: None)
    monkeypatch.setattr("core.scraper_controller._find_edge_executable", lambda: None)
    monkeypatch.setattr("core.scraper_controller._get_playwright_installed_chromium_path", lambda: None)

    ok, strategy = _any_browser_available()
    assert ok is True
    assert strategy == "bundled-chromium"

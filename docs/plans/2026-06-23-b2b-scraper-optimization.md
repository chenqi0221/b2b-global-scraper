# B2B Global 获客系统优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 解决无浏览器环境下的流量风暴问题，同时修复代码质量、安全与可维护性问题。

**Architecture:** 在 `core/scraper_controller.py` 增加浏览器存在性预检与启动熔断；在 `scraper/google_maps.py` 增加页面异常早停与滚动收敛；在 `scraper/email_extractor.py` 增加域名缓存与请求上限；统一状态报告接口；收紧 FastAPI CORS；清理临时文件。

**Tech Stack:** Python 3.12, FastAPI, Playwright, Tauri v2, React 19, Zustand, Tailwind 4.

---

## 任务总览

| 优先级 | 任务 | 核心改动文件 |
|--------|------|--------------|
| P0 | Task 1 | 无浏览器时流量风暴治理：`core/scraper_controller.py`, `scraper/google_maps.py`, `scraper/email_extractor.py` |
| P1 | Task 2 | 清理调试文件与 `.gitignore`：项目根目录、tauri-app/ |
| P1 | Task 3 | 统一回调签名：`core/scraper_controller.py`, `scraper/google_maps.py`, `services/sheet_aggregator.py`, `scraper/file_export.py` |
| P1 | Task 4 | 收紧 CORS：`backend/main.py`, `tauri-app/src/config/api.ts` |
| P2 | Task 5 | 统一依赖：`requirements.txt`, `backend/requirements.txt` |
| P2 | Task 6 | 采集容错增强：`scraper/google_maps.py`, `scraper/email_extractor.py` |
| P2 | Task 7 | 补充测试：`tests/test_browser_launch_guard.py` 等 |

---

## Task 1: 无浏览器时流量风暴治理（P0）

**背景：** 当机器没有可用浏览器时，每个关键词仍会尝试 `_launch_browser` 的 6 种策略 × 3 次重试；若页面被 Google 拦截或无结果，`smart_scroll` 仍会滚动到 50 次上限并持续加载页面资源；邮箱提取阶段可能对每个商家官网发起请求。三者叠加会造成流量与请求放大。

### Step 1.1: 浏览器存在性预检与任务级熔断

**Modify:** `core/scraper_controller.py`

在 `_launch_browser` 之前新增预检函数，若完全找不到浏览器则直接失败，避免反复启动子进程：

```python
def _any_browser_available(p) -> tuple[bool, Optional[str]]:
    """返回 (是否找到浏览器, 推荐策略名)。"""
    bundled = _get_bundled_chromium_path()
    if bundled:
        return True, "bundled-chromium"
    chrome = _find_chrome_executable()
    if chrome:
        return True, "system-chrome-direct"
    edge = _find_edge_executable()
    if edge:
        return True, "system-edge-direct"
    # Playwright 自带 Chromium 检查：通过运行 CLI 的 installed 状态（不下载）
    try:
        from playwright._impl._driver import compute_driver_executable
        node, cli = compute_driver_executable()
        import subprocess
        out = subprocess.run(
            [node, cli, "install", "--dry-run", "chromium"],
            capture_output=True, text=True, timeout=15
        )
        # 若已安装，输出包含路径；未安装则报错；无论哪种都不触发下载
        if out.returncode == 0 and out.stdout:
            return True, "playwright-default"
    except Exception:
        pass
    return False, None
```

> 注：`playwright install --dry-run` 是假设命令；若实际不存在，改为通过 `subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], env={**os.environ, "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1"}, ...)` 让命令因跳过下载而快速失败，通过 stderr 判断是否已安装。

在 `ScraperController` 中新增 `_browser_available: Optional[bool] = None`：

```python
class ScraperController:
    def __init__(self):
        ...
        self._browser_available: Optional[bool] = None
        self._browser_fail_count = 0
        self._browser_fail_threshold = 2
```

在 `_scraping_worker` 的 `worker(kw, index)` 开头增加熔断：

```python
async def worker(kw: str, index: int):
    async with semaphore:
        if not self.is_running:
            return
        if self._browser_available is False:
            self._status_callback(f"[跳过] '{kw}'：前置检测到无可用浏览器", "warning")
            self.keyword_progress[kw]["status"] = "failed"
            self.completed_keywords += 1
            return
        ...
```

在 `_safe_scrape_with_retry` 中，当 `_launch_browser` 连续失败次数超过阈值时，将 `self._browser_available` 设为 False 并停止重试：

```python
async def _safe_scrape_with_retry(...):
    for attempt in range(max_retries + 1):
        browser = None
        try:
            browser = await _launch_browser(p, status_callback, headless=headless)
            self._browser_available = True
            ...
        except Exception as e:
            error_msg = str(e)
            self._browser_fail_count += 1
            if self._browser_fail_count >= self._browser_fail_threshold:
                self._browser_available = False
                status_callback(
                    "[错误] 连续多次无法启动浏览器，已停止后续关键词以避免流量/资源浪费。",
                    "error",
                )
                return 0, 0
            ...
```

### Step 1.2: 页面异常早停

**Modify:** `scraper/google_maps.py`

在 `smart_scroll` 中增加“无结果/被拦截”检测，避免无意义滚动：

```python
async def smart_scroll(page: Page, stop_event: asyncio.Event, update_gui_callback=None):
    ...
    # 在滚动前检查页面是否包含商家卡片
    article_count = await page.locator('div[role="article"]').count()
    if article_count == 0:
        body_text = await page.evaluate("() => document.body.innerText.substring(0, 500)")
        if any(x in body_text for x in ["Google", "unusual traffic", "captcha", "CAPTCHA", "验证", "Verify"]):
            if update_gui_callback:
                update_gui_callback("[警告] 页面疑似被 Google 拦截，停止滚动以避免额外请求。")
            return
    ...
```

限制最大滚动次数根据实际结果动态调整：

```python
max_scrolls = min(50, max(5, article_count // 5 + 5))  # 基于初始结果数动态上限
```

### Step 1.3: 邮箱提取域名缓存与请求上限

**Modify:** `scraper/email_extractor.py`

在模块级增加域名失败缓存与请求计数器：

```python
_failed_domains: set[str] = set()
_request_count = 0
_max_requests_per_run = 200  # 每个关键词任务上限，由调用方注入更合理
```

在 `find_emails_on_website` 开头：

```python
async def find_emails_on_website(url: str, status_callback=None, max_pages_per_site: int = 2):
    global _request_count
    domain = urlparse(url).netloc.lower()
    if domain in _failed_domains:
        return ""
    if _request_count >= _max_requests_per_run:
        if status_callback:
            status_callback(f"[跳过] 已达到本次任务邮箱请求上限: {domain}")
        return ""
    ...
```

失败时加入缓存：

```python
try:
    ...
except Exception:
    _failed_domains.add(domain)
    return ""
```

### Step 1.4: 前端轮询退避

**Modify:** `tauri-app/src/stores/scraperStore.ts`

在多次失败后拉长轮询间隔：

```typescript
let statusFailCount = 0
let pollIntervalMs = 2000

export const useScraperStore = create<State>((set) => ({
  ...
  fetchStatus: async () => {
    try {
      const r = await fetch(`${API_BASE}/api/scraper/status`)
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      const j = (await r.json()) as ScrapeStatus
      set({ status: j, statusError: null })
      statusFailCount = 0
      pollIntervalMs = 2000
    } catch (e) {
      statusFailCount++
      pollIntervalMs = Math.min(30000, 2000 * 2 ** Math.min(statusFailCount, 4))
      if (statusFailCount >= 5) {
        set({ statusError: e instanceof Error ? e.message : String(e ?? 'unknown') })
      }
    }
  },
}))
```

> 注：当前 React 组件使用 `setInterval(() => useScraperStore.getState().fetchStatus(), 2000)`，需要同步修改调用处以使用动态 `pollIntervalMs`。为简化，可让 store 暴露 `getPollInterval()` 或让组件使用 store 订阅状态。

---

## Task 2: 清理调试文件与 `.gitignore`（P1）

### Step 2.1: 识别并清理临时文件

**Modify:** 项目根目录、tauri-app/

常见临时文件模式：
- `tauri-app/debug*.py`
- `tauri-app/debug*.json`
- `tauri-app/debug*.txt`
- `tauri-app/src/debug*.py`
- `Downloads/` 下的历史会话（不删除，只忽略）
- `*.log`, `*.tmp`

执行前先用 `git status --short` 列出未跟踪文件，确认后再删除。

### Step 2.2: 更新 `.gitignore`

**Modify:** `.gitignore`

追加：

```gitignore
# 调试临时文件
debug*.py
debug*.json
debug*.txt
*.log
*.tmp

# 运行输出
Downloads/
__pycache__/
*.pyc
.venv/
venv/
venv_build/
node_modules/
target/
build_portable/
dist/

# IDE
.vscode/
.idea/
*.swp

# 打包产物
*.exe
*.spec
build/
```

---

## Task 3: 统一回调签名（P1）

**背景：** `update_gui_callback` 在多处使用：有时 `(msg: str)`，有时 `(msg: str, level: str)`，调用方和实现方容易不匹配。

**Modify:** 
- `core/scraper_controller.py`
- `scraper/google_maps.py`
- `scraper/email_extractor.py`
- `scraper/file_export.py`
- `services/sheet_aggregator.py`

### Step 3.1: 定义统一接口

在 `core/scraper_controller.py` 顶部新增：

```python
from typing import Protocol

class StatusReporter(Protocol):
    def __call__(self, message: str, level: str = "info") -> None: ...
```

### Step 3.2: 兼容旧签名

新增适配器，允许旧的一参数回调继续工作：

```python
def _as_status_reporter(callback: Optional[Callable]) -> StatusReporter:
    if callback is None:
        return lambda msg, level=None: None
    import inspect
    sig = inspect.signature(callback)
    if len(sig.parameters) == 1:
        def _legacy(msg: str, level: str = "info"):
            callback(msg)
        return _legacy
    return callback
```

### Step 3.3: 修改各模块签名

将所有 `update_gui_callback=None` 替换为 `status_reporter: Optional[StatusReporter] = None`，并在函数入口统一使用 `_as_status_reporter(update_gui_callback)` 进行适配。保持对外 API 兼容：仍接受旧的单参数 callable。

---

## Task 4: 收紧 CORS（P1）

**Modify:** `backend/main.py`, `tauri-app/src/config/api.ts`

### Step 4.1: 后端允许 Tauri 本地源

```python
import os

allowed_origins = [
    "http://localhost:1420",      # Tauri dev
    "http://localhost:3000",      # Vite dev
    "tauri://localhost",          # Tauri production
]

if os.environ.get("B2B_CORS_ORIGIN"):
    allowed_origins.append(os.environ.get("B2B_CORS_ORIGIN"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### Step 4.2: 前端保持默认 API_BASE

确认 `tauri-app/src/config/api.ts` 使用 `http://127.0.0.1:8756`，无需改动。

---

## Task 5: 统一 Python 依赖管理（P2）

**Modify:** `requirements.txt`, `backend/requirements.txt`

### Step 5.1: 差异合并

读取两个文件，找出只在 `backend/requirements.txt` 中存在而在根目录不存在的包，合并到根目录 `requirements.txt` 中，并删除 `backend/requirements.txt`。根目录的 `requirements.txt` 应该是唯一依赖清单。

### Step 5.2: 锁定关键版本

确保以下依赖版本明确：
- `fastapi>=0.110,<1.0`
- `uvicorn[standard]>=0.29`
- `playwright>=1.42,<2.0`
- `pydantic>=2.0,<3.0`
- `openpyxl`, `pandas`, `requests`

---

## Task 6: 采集容错增强（P2）

### Step 6.1: Google Maps 选择器降级

**Modify:** `scraper/google_maps.py`

为 `extract_details` 中每个字段准备多选择器：

```python
ADDRESS_SELECTORS = [
    'button[data-item-id="address"]',
    'button[data-tooltip="复制地址"]',
    '[data-item-id*="address"]',
]
WEBSITE_SELECTORS = [
    'a[data-item-id="authority"]',
    'a[data-item-id="olympic-website"]',
    '[data-item-id*="authority"]',
]
PHONE_SELECTORS = [
    'button[data-item-id^="phone:tel:"]',
    'button[data-tooltip="拨打电话"]',
    '[data-item-id*="phone"]',
]
```

遍历选择器，第一个非空结果即返回。

### Step 6.2: 邮箱提取增强

**Modify:** `scraper/email_extractor.py`

- 增加 contact/about 页面探测：在首页源码未找到邮箱时，尝试 `/contact`, `/contact-us`, `/about`。
- 增加常见反爬虫编码解码：将 `[at]`, `(at)`, `&#64;`, ` AT ` 替换为 `@`。
- 限制每个站点访问页数（默认 2 页）。

---

## Task 7: 补充测试（P2）

### Step 7.1: 浏览器预检测试

**Create:** `tests/test_browser_launch_guard.py`

```python
import pytest
from core.scraper_controller import _any_browser_available

class FakePlaywright:
    pass

def test_any_browser_available_finds_none_when_no_paths(monkeypatch):
    monkeypatch.setattr("core.scraper_controller._get_bundled_chromium_path", lambda: None)
    monkeypatch.setattr("core.scraper_controller._find_chrome_executable", lambda: None)
    monkeypatch.setattr("core.scraper_controller._find_edge_executable", lambda: None)
    ok, strategy = _any_browser_available(FakePlaywright())
    assert ok is False
    assert strategy is None
```

### Step 7.2: 回调适配器测试

**Create:** `tests/test_status_reporter.py`

```python
from core.scraper_controller import _as_status_reporter

def test_legacy_single_arg_callback():
    messages = []
    def cb(msg):
        messages.append(msg)
    reporter = _as_status_reporter(cb)
    reporter("hello", "warning")
    assert messages == ["hello"]
```

### Step 7.3: 邮箱域名缓存测试

**Create:** `tests/test_email_extractor_cache.py`

```python
import pytest
from scraper.email_extractor import find_emails_on_website

@pytest.mark.asyncio
async def test_failed_domain_is_cached(monkeypatch):
    from scraper import email_extractor
    email_extractor._failed_domains.clear()
    email_extractor._request_count = 0

    async def fake_request(*args, **kwargs):
        raise ConnectionError("no network")

    monkeypatch.setattr(email_extractor, "_fetch_page", fake_request)
    result = await find_emails_on_website("https://example.com")
    assert result == ""
    assert "example.com" in email_extractor._failed_domains
```

---

## 验证清单

- [ ] 在未安装 Chrome/Edge 且无便携 Chromium 的机器上运行采集，所有关键词在首次浏览器启动失败后即停止，不产生后续 Google/官网请求。
- [ ] 正常机器上采集流程仍能通过，结果导出正确。
- [ ] `git status --short` 不再出现大量临时文件。
- [ ] `pytest tests/` 全部通过。
- [ ] 前端与后端在 dev/prod 模式下通信正常。

---

## 执行方式

**推荐：** 使用 `superpowers:subagent-driven-development` 按任务分派子代理，每个任务独立验证后合并。

**备选：** 使用 `superpowers:executing-plans` 在当前会话顺序执行，适合需要频繁与用户确认的场景。

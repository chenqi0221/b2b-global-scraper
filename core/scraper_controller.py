"""抓取控制器，协调抓取流程"""

import os
import sys
from pathlib import Path

# ========== Playwright 环境变量必须在导入 playwright 之前设置 ==========
def _get_app_dir() -> Path:
    if getattr(sys, 'frozen', False):
        # PyInstaller --onedir 模式：exe 在根目录，_internal 是打包文件
        exe_parent = Path(sys.executable).parent
        # 若 _internal 目录在同级存在，确认是 onedir 打包
        if (exe_parent / "_internal").exists():
            return exe_parent
        return exe_parent
    return Path(__file__).resolve().parent.parent

# 在导入 playwright 之前设置 PLAYWRIGHT_NODEJS_PATH
if getattr(sys, 'frozen', False):
    _app_dir = _get_app_dir()
    _node_paths = [
        _app_dir / "_internal" / "playwright" / "driver" / "node.exe",
        _app_dir / "playwright" / "driver" / "node.exe",
    ]
    for _node_path in _node_paths:
        if _node_path.exists():
            os.environ["PLAYWRIGHT_NODEJS_PATH"] = str(_node_path)
            break

# 设置 PLAYWRIGHT_BROWSERS_PATH，使得 Playwright 能在便携目录中搜索浏览器
# 这对于 channel="chrome"/"msedge" 的 fallback 以及 driver 内部浏览器查找至关重要
_browsers_path = _get_app_dir()
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(_browsers_path))
# ===================================================================

import asyncio
import logging
import subprocess
import threading
from datetime import datetime
from typing import Callable, List, Optional
from playwright.async_api import async_playwright, Browser

from utils.reporter import as_status_reporter

from scraper.google_maps import scrape_google_maps
from scraper.email_extractor import reset_email_extractor_state
from services.sheet_aggregator import aggregate_and_sync
from config import HTTP_PROXY

logger = logging.getLogger(__name__)


def _patch_playwright_driver():
    """在 PyInstaller 打包环境下 monkey-patch Playwright 驱动路径解析。
    
    Playwright 的 compute_driver_executable() 使用 inspect.getfile(playwright)
    来查找 driver 目录。PyInstaller 打包后，inspect.getfile 返回的是原始
    site-packages 路径（目标机器上不存在），导致驱动无法启动。
    
    PLAYWRIGHT_NODEJS_PATH 环境变量只能覆盖 node.exe 路径，cli.js 路径无法覆盖。
    因此需要 monkey-patch 整个函数。
    """
    if not getattr(sys, 'frozen', False):
        return

    _app_dir = _get_app_dir()
    bundled_driver_paths = [
        _app_dir / "_internal" / "playwright" / "driver",
        _app_dir / "playwright" / "driver",
    ]
    bundled_driver = None
    for p in bundled_driver_paths:
        if p.exists() and (p / "node.exe").exists() and (p / "package" / "cli.js").exists():
            bundled_driver = p
            break

    if bundled_driver is None:
        logger.warning("[Playwright] 未找到完整的打包驱动目录")
        return

    import playwright._impl._driver as _pw_driver_module

    def _patched_compute_driver_executable():
        return (
            str(bundled_driver / "node.exe"),
            str(bundled_driver / "package" / "cli.js"),
        )

    _pw_driver_module.compute_driver_executable = _patched_compute_driver_executable

    try:
        import playwright._impl._transport as _pw_transport_module
        _pw_transport_module.compute_driver_executable = _patched_compute_driver_executable
    except ImportError:
        pass

    logger.info(f"[Playwright] 已 patch 驱动路径: {bundled_driver}")

_patch_playwright_driver()


def _get_bundled_chromium_path() -> Optional[str]:
    """递归查找便携版内嵌的 Chromium 浏览器 (chrome.exe)"""
    app_dir = _get_app_dir()

    # 1. 精确已知路径
    exact_paths = [
        app_dir / "playwright" / "chromium-1208" / "chrome-win64" / "chrome.exe",
        app_dir / "_internal" / "playwright" / "chromium-1208" / "chrome-win64" / "chrome.exe",
    ]
    for p in exact_paths:
        if p.exists():
            return str(p)

    # 2. 递归搜索 app_dir 下两层的 chromium 目录
    #    避免全盘扫描，限制深度
    for depth in range(1, 4):
        pattern = "/".join(["*"] * depth)
        for candidate in app_dir.glob(f"{pattern}/chrome.exe"):
            if candidate.is_file() and "chromium" in str(candidate).lower():
                return str(candidate)
        for candidate in app_dir.glob(f"{pattern}/chromium-*/chrome-win64/chrome.exe"):
            if candidate.is_file():
                return str(candidate)

    return None


def _find_edge_executable() -> Optional[str]:
    """在 Windows 上查找 Microsoft Edge 可执行文件路径"""
    edge_paths = [
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    ]
    for p in edge_paths:
        if Path(p).exists():
            return p

    # 通过注册表查找
    try:
        import winreg
        for reg_path in [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
            r"SOFTWARE\Clients\StartMenuInternet\Microsoft Edge\shell\open\command",
        ]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    value = winreg.QueryValue(key, "")
                    if value:
                        exe_path = value.strip().strip('"')
                        if Path(exe_path).exists():
                            return exe_path
            except FileNotFoundError:
                continue
    except Exception:
        pass

    return None


def _find_chrome_executable() -> Optional[str]:
    """在 Windows 上查找 Google Chrome 可执行文件路径"""
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ]
    for p in chrome_paths:
        if Path(p).exists():
            return p

    local_appdata = os.environ.get("LOCALAPPDATA", "")
    if local_appdata:
        user_chrome = Path(local_appdata) / "Google" / "Chrome" / "Application" / "chrome.exe"
        if user_chrome.exists():
            return str(user_chrome)

    # 通过注册表查找
    try:
        import winreg
        for reg_path in [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
        ]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    value = winreg.QueryValue(key, "")
                    if value:
                        exe_path = value.strip().strip('"')
                        if Path(exe_path).exists():
                            return exe_path
            except FileNotFoundError:
                continue
    except Exception:
        pass

    return None


def _get_playwright_installed_chromium_path() -> Optional[str]:
    """查找 Playwright `playwright install chromium` 安装的 Chromium 路径。"""
    search_roots = []
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    if local_appdata:
        search_roots.append(Path(local_appdata) / "ms-playwright")
    userprofile = os.environ.get("USERPROFILE", "")
    if userprofile:
        search_roots.append(Path(userprofile) / "AppData" / "Local" / "ms-playwright")

    browsers_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if browsers_path:
        search_roots.append(Path(browsers_path))

    for root in search_roots:
        if not root.exists():
            continue
        for candidate in root.rglob("chrome.exe"):
            if "chromium" in str(candidate).lower():
                return str(candidate)
    return None


def _any_browser_available() -> tuple[bool, Optional[str]]:
    """返回 (是否存在可用浏览器, 推荐策略名)。

    预检目标：在完全无浏览器时直接失败，避免 Playwright 反复 launch 产生
    子进程/代理请求风暴。
    """
    bundled = _get_bundled_chromium_path()
    if bundled:
        return True, "bundled-chromium"
    chrome = _find_chrome_executable()
    if chrome:
        return True, "system-chrome-direct"
    edge = _find_edge_executable()
    if edge:
        return True, "system-edge-direct"
    pw_chromium = _get_playwright_installed_chromium_path()
    if pw_chromium:
        return True, "playwright-default"
    return False, None


def _check_visual_cpp_redist() -> bool:
    """检查是否安装了 Visual C++ Redistributable（Playwright 必需）"""
    try:
        import winreg
        keys_to_check = [
            r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
            r"SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
        ]
        for key_path in keys_to_check:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    installed = winreg.QueryValueEx(key, "Installed")
                    if installed and installed[0] == 1:
                        return True
            except FileNotFoundError:
                continue
    except Exception:
        pass

    # 备选：检查常见 DLL 是否存在
    system32 = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32"
    required_dlls = ["msvcp140.dll", "vcruntime140.dll"]
    found = sum(1 for dll in required_dlls if (system32 / dll).exists())
    return found >= len(required_dlls)


def _get_chromium_args() -> list:
    """获取增强兼容性的 Chromium 启动参数"""
    return [
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-setuid-sandbox",
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",
        "--js-flags=--max-old-space-size=512",
        "--disable-background-networking",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-breakpad",
        "--disable-component-update",
        "--disable-default-apps",
        "--disable-features=TranslateUI",
        "--disable-hang-monitor",
        "--disable-ipc-flooding-protection",
        "--disable-popup-blocking",
        "--disable-prompt-on-repost",
        "--disable-renderer-backgrounding",
        "--force-color-profile=srgb",
        "--metrics-recording-only",
        "--safebrowsing-disable-auto-update",
    ]


async def _launch_browser(p, status_callback: Optional[Callable] = None, headless: bool = True) -> Browser:
    """启动浏览器，带详细诊断和多级回退
    
    回退链:
    1. 便携版内嵌 Chromium（路径由 _get_bundled_chromium_path 搜索）
    2. 系统安装的 Google Chrome（通过 _find_chrome_executable 搜索）
    3. 系统安装的 Microsoft Edge（通过 _find_edge_executable 搜索）
    4. Playwright 默认 channel 机制（chrome → msedge）
    """
    proxy = {"server": HTTP_PROXY} if HTTP_PROXY else None
    chromium_args = _get_chromium_args()

    # 预检：完全无浏览器时直接失败，避免后续所有 launch 尝试浪费资源/流量
    browser_available, preferred_strategy = _any_browser_available()
    if not browser_available:
        error_detail = (
            "无法找到任何可用浏览器。\n"
            "已检查：内嵌 Chromium、系统 Chrome、系统 Edge、Playwright 已安装 Chromium。\n\n"
            "解决方案:\n"
            "1. 安装 Google Chrome 或 Microsoft Edge\n"
            "2. 运行: python -m playwright install chromium\n"
            "3. 使用包含便携 Chromium 的打包版本"
        )
        logger.error(error_detail)
        if status_callback:
            status_callback(error_detail, "error")
        raise RuntimeError(error_detail)

    if status_callback:
        status_callback(f"[诊断] 预检可用浏览器策略: {preferred_strategy}", "info")

    has_vcredist = _check_visual_cpp_redist()
    if not has_vcredist:
        msg = (
            "[系统检查] 未检测到 Visual C++ Redistributable。\n"
            "Playwright 需要此组件才能与 Chromium 通信。\n"
            "请下载安装：https://aka.ms/vs/17/release/vc_redist.x64.exe"
        )
        logger.warning(msg)
        if status_callback:
            status_callback(msg, "warning")

    if headless:
        headless_mode = "无头"
        headless_new_args = ["--headless=new"]
    else:
        headless_mode = "有头（显示窗口）"
        headless_new_args = []

    if status_callback:
        status_callback(f"[诊断] 浏览器模式: {headless_mode}", "info")

    # 构建多级回退策略列表
    strategies = []

    # 策略 1: 便携版内嵌 Chromium
    bundled_chromium = _get_bundled_chromium_path()
    if bundled_chromium:
        if status_callback:
            status_callback(f"[诊断] 找到内嵌 Chromium: {bundled_chromium}", "info")
        strategies.append(("bundled-chromium", dict(
            executable_path=bundled_chromium,
            headless=headless,
            proxy=proxy,
            args=chromium_args + headless_new_args,
        )))
    else:
        if status_callback:
            status_callback("[诊断] 未找到内嵌 Chromium", "warning")

    # 策略 2: 系统安装的 Google Chrome（直接路径，不依赖 Playwright channel）
    system_chrome = _find_chrome_executable()
    if system_chrome:
        if status_callback:
            status_callback(f"[诊断] 找到系统 Chrome: {system_chrome}", "info")
        strategies.append(("system-chrome-direct", dict(
            executable_path=system_chrome,
            headless=headless,
            proxy=proxy,
            args=chromium_args + headless_new_args,
        )))

    # 策略 3: 系统安装的 Microsoft Edge（直接路径）
    system_edge = _find_edge_executable()
    if system_edge:
        if status_callback:
            status_callback(f"[诊断] 找到系统 Edge: {system_edge}", "info")
        strategies.append(("system-edge-direct", dict(
            executable_path=system_edge,
            headless=headless,
            proxy=proxy,
            args=chromium_args + headless_new_args,
        )))

    # 策略 4-5: Playwright channel 机制（作为最后回退）
    if not system_chrome:
        strategies.append(("channel-chrome", dict(
            channel="chrome", headless=headless, proxy=proxy,
            args=chromium_args + headless_new_args,
        )))
    if not system_edge:
        strategies.append(("channel-msedge", dict(
            channel="msedge", headless=headless, proxy=proxy,
            args=chromium_args + headless_new_args,
        )))

    # 策略 6: Playwright install 安装的 Chromium（显式 executable_path，避免隐式查找）
    pw_chromium = _get_playwright_installed_chromium_path()
    if pw_chromium:
        strategies.append(("playwright-default", dict(
            executable_path=pw_chromium,
            headless=headless, proxy=proxy, args=chromium_args + headless_new_args,
        )))

    if status_callback:
        strategy_names = [name for name, _ in strategies]
        status_callback(f"[诊断] 将依次尝试以下策略: {strategy_names}", "info")

    last_error = None
    for label, kwargs in strategies:
        try:
            if status_callback:
                status_callback(f"[诊断] 尝试启动浏览器: {label}...", "info")
            browser = await p.chromium.launch(**kwargs)
            if status_callback:
                status_callback(f"[诊断] 浏览器启动成功: {label}", "info")
            logger.info(f"浏览器启动成功: {label}")
            return browser
        except Exception as e:
            last_error = f"[{label}] {e}"
            logger.warning(f"浏览器启动失败: {last_error}")
            if status_callback:
                status_callback(f"[诊断] 启动失败 {label}: {str(e)[:150]}", "warning")
            continue

    # 所有策略都失败，提供详细错误信息
    error_detail = (
        f"无法启动浏览器，已尝试 {len(strategies)} 种策略。\n"
        f"最后错误: {last_error}\n\n"
        f"可能原因及解决方案:\n"
        f"1. 缺少 Visual C++ Redistributable:\n"
        f"   运行目录中的 VC_redist.x64.exe 或下载 https://aka.ms/vs/17/release/vc_redist.x64.exe\n"
        f"2. 安全软件拦截:\n"
        f"   将本程序目录添加到杀毒软件白名单\n"
        f"3. 系统缺少 Chrome/Edge 浏览器:\n"
        f"   安装 Google Chrome 或 Microsoft Edge\n"
        f"4. 便携版文件损坏:\n"
        f"   重新解压便携版压缩包\n"
        f"5. 诊断信息:\n"
        f"   PLAYWRIGHT_BROWSERS_PATH={os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '未设置')}\n"
        f"   PLAYWRIGHT_NODEJS_PATH={os.environ.get('PLAYWRIGHT_NODEJS_PATH', '未设置')}"
    )
    raise RuntimeError(error_detail)


async def _safe_scrape_with_retry(
    p, task_info, output_dir, status_callback, stop_event, max_retries=2, headless=True, on_progress=None, controller=None
):
    """带错误重试的抓取，遇到 Connection closed 时重启浏览器。

    controller 用于任务级熔断：当浏览器连续启动失败时，后续关键词直接跳过，
    避免产生大量无意义的启动请求/流量。
    """
    for attempt in range(max_retries + 1):
        browser = None
        try:
            if controller is not None and controller._browser_available is False:
                status_callback(
                    f"[跳过] '{task_info['keyword']}'：前置检测到无可用浏览器",
                    "warning",
                )
                return 0, 0

            browser = await _launch_browser(p, status_callback, headless=headless)
            if controller is not None:
                controller._browser_available = True
                controller._browser_fail_count = 0

            result = await scrape_google_maps(
                browser, task_info, output_dir, status_callback, stop_event,
                on_progress=on_progress,
            )
            return result
        except Exception as e:
            error_msg = str(e)
            if controller is not None:
                controller._browser_fail_count += 1
                if controller._browser_fail_count >= controller._browser_fail_threshold:
                    controller._browser_available = False
                    status_callback(
                        "[错误] 连续多次无法启动浏览器，已停止后续关键词以避免流量/资源浪费。",
                        "error",
                    )
                    logger.error(f"Browser launch failed {controller._browser_fail_count} times; aborting task")
                    return 0, 0

            if "Connection closed" in error_msg or "Target page, context or browser has been closed" in error_msg:
                if attempt < max_retries:
                    status_callback(
                        f"[警告] 浏览器连接断开，正在重启浏览器后重试 ({attempt + 1}/{max_retries})...",
                        "warning",
                    )
                    logger.warning(f"Connection closed, restarting browser and retrying {attempt + 1}/{max_retries}: {error_msg}")
                    await asyncio.sleep(5)
                    # 继续循环，会创建新的浏览器实例
                else:
                    status_callback(
                        f"[错误] 浏览器连接多次断开，跳过此关键词: {task_info['keyword']}\n"
                        f"建议: 检查系统内存、关闭其他程序，或安装 Visual C++ Redistributable",
                        "error",
                    )
                    logger.error(f"Connection closed after {max_retries} retries: {error_msg}")
                    return 0, 0
            else:
                raise
        finally:
            if browser:
                try:
                    await browser.close()
                except Exception:
                    pass
    return 0, 0


class ScraperController:
    """抓取控制器"""

    def __init__(self):
        self.is_running = False
        self.stop_event = asyncio.Event()
        self.on_status_update: Optional[Callable[[str, str], None]] = None
        self.on_progress_update: Optional[Callable[[int, int, int], None]] = None

        self.total_found = 0
        self.email_found = 0
        self.synced_count = 0
        self.output_dir = None

        # 浏览器启动熔断状态
        self._browser_available: Optional[bool] = None
        self._browser_fail_count = 0
        self._browser_fail_threshold = 2

    def start_scraping(
        self,
        keywords: List[str],
        location: dict,
        concurrency: int = 3,
        headless: bool = True,
    ):
        """开始抓取"""
        if self.is_running:
            return

        self.is_running = True
        self.stop_event.clear()
        self.headless = headless

        self.keyword_progress: dict[str, dict] = {}
        self.total_keywords = len(keywords)
        self.completed_keywords = 0

        # 预填充所有关键词为 "queued"
        for kw in keywords:
            self.keyword_progress[kw] = {
                "keyword": kw,
                "status": "queued",
                "found": 0,
                "processed": 0,
                "succeeded": 0,
                "skipped": 0,
            }

        session_folder_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        downloads_root = _get_app_dir() / "Downloads"
        self.output_dir = str(downloads_root / session_folder_name)
        os.makedirs(self.output_dir, exist_ok=True)

        # 每次新任务重置邮箱提取器熔断状态
        reset_email_extractor_state(max_requests_per_run=max(100, len(keywords) * 10))

        if self.on_status_update:
            self.on_status_update(f"本次任务文件将保存至: {self.output_dir}", "info")

        thread = threading.Thread(
            target=self._run_scraping,
            args=(keywords, location, concurrency, self.headless),
            daemon=True
        )
        thread.start()

    def stop_scraping(self):
        """停止抓取"""
        self.is_running = False
        self.stop_event.set()

    def _run_scraping(self, keywords: List[str], location: dict, concurrency: int, headless: bool):
        """运行抓取（在线程中）"""
        asyncio.run(self._scraping_worker(keywords, location, concurrency, headless))

    async def _scraping_worker(self, keywords: List[str], location: dict, concurrency: int, headless: bool):
        """抓取工作协程"""
        try:
            async with async_playwright() as p:
                # 创建信号量控制并发
                semaphore = asyncio.Semaphore(concurrency)

                async def worker(kw: str, index: int):
                    async with semaphore:
                        if not self.is_running:
                            return

                        if kw in self.keyword_progress:
                            self.keyword_progress[kw]["status"] = "running"

                        task_info = {
                            "keyword": kw,
                            "country": location.get("country", ""),
                            "city": location.get("city", ""),
                            "district": location.get("district", "")
                        }

                        def on_kw_progress(progress_type: str, **kwargs):
                            if kw in self.keyword_progress:
                                if progress_type == "found":
                                    self.keyword_progress[kw]["found"] = kwargs.get("count", 0)
                                elif progress_type == "business":
                                    self.keyword_progress[kw]["processed"] = kwargs.get("index", 0) + 1
                                    if kwargs.get("success"):
                                        self.keyword_progress[kw]["succeeded"] += 1
                                    else:
                                        self.keyword_progress[kw]["skipped"] += 1

                            if self.on_progress_update:
                                self.on_progress_update(
                                    self.total_found,
                                    self.email_found,
                                    self.synced_count
                                )

                        try:
                            found, email = await _safe_scrape_with_retry(
                                p, task_info, self.output_dir,
                                as_status_reporter(self._status_callback), self.stop_event,
                                headless=headless,
                                on_progress=on_kw_progress,
                                controller=self,
                            )

                            self.total_found += found
                            self.email_found += email
                            self.completed_keywords += 1

                            if kw in self.keyword_progress:
                                self.keyword_progress[kw]["status"] = "done"
                                self.keyword_progress[kw]["found"] = found

                            if self.on_progress_update:
                                self.on_progress_update(
                                    self.total_found,
                                    self.email_found,
                                    self.synced_count
                                )
                        except Exception as e:
                            logger.error(f"关键词 '{kw}' 抓取失败: {e}")
                            self._status_callback(f"[错误] 关键词 '{kw}' 抓取失败: {str(e)}", "error")
                            self.completed_keywords += 1
                            if kw in self.keyword_progress:
                                self.keyword_progress[kw]["status"] = "failed"

                tasks = [worker(kw, i) for i, kw in enumerate(keywords)]
                await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.exception("抓取主循环错误")
            self._status_callback(f"抓取错误: {str(e)}", "error")
        finally:
            self.is_running = False

    def _status_callback(self, message: str, level: str = "info"):
        """状态回调"""
        if self.on_status_update:
            self.on_status_update(message, level)

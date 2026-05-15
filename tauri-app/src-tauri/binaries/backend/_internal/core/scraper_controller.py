"""抓取控制器，协调抓取流程"""

import os
import sys
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional
from playwright.async_api import async_playwright, Browser

from scraper.google_maps import scrape_google_maps
from services.sheet_aggregator import aggregate_and_sync
from config import HTTP_PROXY


def _get_app_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


async def _launch_browser(p) -> Browser:
    proxy = {"server": HTTP_PROXY} if HTTP_PROXY else None

    strategies = [
        ("内置 Chromium (headless=False)", dict(headless=False, proxy=proxy)),
        ("系统 Chrome", dict(channel="chrome", headless=False, proxy=proxy)),
        ("系统 Edge", dict(channel="msedge", headless=False, proxy=proxy)),
        ("内置 Chromium (headless=True)", dict(headless=True, proxy=proxy)),
    ]

    last_error = None
    for label, kwargs in strategies:
        try:
            browser = await p.chromium.launch(**kwargs)
            return browser
        except Exception as e:
            last_error = str(e)
            continue

    raise RuntimeError(
        f"无法启动浏览器，已尝试所有策略。请确保已安装 Chrome 或 Edge。\n最后错误: {last_error}"
    )


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
    
    def start_scraping(
        self, 
        keywords: List[str], 
        location: dict,
        concurrency: int = 3
    ):
        """开始抓取"""
        if self.is_running:
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        # 创建带时间戳的输出目录（位于 exe 所在目录下）
        session_folder_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        downloads_root = _get_app_dir() / "Downloads"
        self.output_dir = str(downloads_root / session_folder_name)
        os.makedirs(self.output_dir, exist_ok=True)
        
        if self.on_status_update:
            self.on_status_update(f"本次任务文件将保存至: {self.output_dir}", "info")
        
        thread = threading.Thread(
            target=self._run_scraping,
            args=(keywords, location, concurrency),
            daemon=True
        )
        thread.start()
    
    def stop_scraping(self):
        """停止抓取"""
        self.is_running = False
        self.stop_event.set()
    
    def _run_scraping(self, keywords: List[str], location: dict, concurrency: int):
        """运行抓取（在线程中）"""
        asyncio.run(self._scraping_worker(keywords, location, concurrency))
    
    async def _scraping_worker(self, keywords: List[str], location: dict, concurrency: int):
        """抓取工作协程"""
        try:
            async with async_playwright() as p:
                browser = await _launch_browser(p)
                
                # 创建信号量控制并发
                semaphore = asyncio.Semaphore(concurrency)
                
                async def worker(kw: str, index: int):
                    async with semaphore:
                        if not self.is_running:
                            return
                        
                        task_info = {
                            "keyword": kw,
                            "country": location.get("country", ""),
                            "city": location.get("city", ""),
                            "district": location.get("district", "")
                        }
                        
                        found, email = await scrape_google_maps(
                            browser, task_info, self.output_dir, 
                            self._status_callback, self.stop_event
                        )
                        
                        self.total_found += found
                        self.email_found += email
                        
                        if self.on_progress_update:
                            self.on_progress_update(
                                self.total_found, 
                                self.email_found, 
                                self.synced_count
                            )
                
                # 创建任务
                tasks = [worker(kw, i) for i, kw in enumerate(keywords)]
                await asyncio.gather(*tasks)
                
                await browser.close()
                
        except Exception as e:
            self._status_callback(f"抓取错误: {str(e)}", "error")
        finally:
            self.is_running = False
    
    def _status_callback(self, message: str, level: str = "info"):
        """状态回调"""
        if self.on_status_update:
            self.on_status_update(message, level)

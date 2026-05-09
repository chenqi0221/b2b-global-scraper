import asyncio
import os
from datetime import datetime

from playwright.async_api import async_playwright

from config import HTTP_PROXY
from scraper_core import scrape_google_maps


async def main() -> None:
    task_info = {
        "keyword": "Sanitary ware wholesale",
        "district": "Dubai Marina",
        "city": "Dubai",
        "country": "United Arab Emirates",
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("Downloads", f"one_keyword_test_{ts}")
    os.makedirs(output_dir, exist_ok=True)

    stop_event = asyncio.Event()

    def update_gui_callback(msg: str) -> None:
        print(msg)

    # 给它一个“时间上限”，确保不会长时间跑。
    async def stop_later() -> None:
        await asyncio.sleep(35)
        stop_event.set()

    async with async_playwright() as p:
        # 显式禁用系统代理，避免 Playwright/Chromium 默认走了不可用的系统代理
        launch_kwargs = {
            "headless": False,
            "args": ["--no-proxy-server"],
        }
        if HTTP_PROXY:
            launch_kwargs["proxy"] = {"server": HTTP_PROXY}

        browser = await p.chromium.launch(**launch_kwargs)
        try:
            await asyncio.gather(
                scrape_google_maps(
                    browser,
                    task_info,
                    output_dir,
                    update_gui_callback,
                    stop_event,
                ),
                stop_later(),
            )
        finally:
            await browser.close()

    print(f"Done. Output dir: {output_dir}")


if __name__ == "__main__":
    asyncio.run(main())


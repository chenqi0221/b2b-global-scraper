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
    output_dir = os.path.join("Downloads", f"headless_limited_test_{ts}")
    os.makedirs(output_dir, exist_ok=True)

    stop_event = asyncio.Event()

    def update_gui_callback(msg: str) -> None:
        print(msg)

    async def stop_later() -> None:
        # 让页面先完成初次加载/进入列表区域，再中止
        await asyncio.sleep(40)
        stop_event.set()

    async with async_playwright() as p:
        launch_kwargs = {"headless": True}
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


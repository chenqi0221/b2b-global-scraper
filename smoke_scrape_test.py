import asyncio
import os

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

    output_dir = os.path.join("Downloads", "smoke_test")
    os.makedirs(output_dir, exist_ok=True)

    stop_event = asyncio.Event()
    stop_event.set()  # 立刻触发停止，避免真正抓取大量商家

    def update_gui_callback(msg: str) -> None:
        print(msg)

    async with async_playwright() as p:
        launch_kwargs = {"headless": True}
        if HTTP_PROXY:
            launch_kwargs["proxy"] = {"server": HTTP_PROXY}

        browser = await p.chromium.launch(**launch_kwargs)
        try:
            await scrape_google_maps(
                browser,
                task_info,
                output_dir,
                update_gui_callback,
                stop_event,
            )
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())


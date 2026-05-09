# test_scraper_improvements.py
# 测试抓取改进效果

import asyncio
import logging
from playwright.async_api import async_playwright

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from google_maps_scraper import scrape_google_maps

async def test_scrape():
    """测试抓取改进效果"""
    try:
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=False)
            
            # 简单的更新回调
            def update_gui(msg):
                print(f"[GUI] {msg}")
            
            # 创建停止事件
            stop_event = asyncio.Event()
            
            # 测试任务
            task_info = {
                "keyword": "bathroom vanity",
                "country": "United Arab Emirates",
                "city": "Dubai",
                "district": "Deira"
            }
            
            print("开始测试抓取改进效果...")
            found_count, email_count = await scrape_google_maps(
                browser,
                task_info,
                "test_output",
                update_gui,
                stop_event
            )
            
            print(f"测试完成：找到 {found_count} 个商家，其中 {email_count} 个包含邮箱")
            
            await browser.close()
            
            return found_count
            
    except Exception as e:
        logger.error(f"测试出错: {str(e)}")
        return 0

if __name__ == "__main__":
    found = asyncio.run(test_scrape())
    print(f"最终结果：成功抓取 {found} 个商家")
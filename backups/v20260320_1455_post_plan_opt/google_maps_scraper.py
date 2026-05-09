import asyncio
import csv
import os
import logging
import random
from datetime import datetime

import pandas as pd
from playwright.async_api import Page
from playwright_stealth import Stealth
from urllib.parse import quote

from email_extractor import find_emails_on_website

logger = logging.getLogger(__name__)


async def smart_scroll(page: Page, stop_event: asyncio.Event):
    """模拟真人随机滚动，防止被识别，并确保加载更多结果"""
    scrollable_div = 'div[role="feed"]'
    try:
        await page.wait_for_selector(scrollable_div, timeout=10000)
        feed_el = await page.query_selector(scrollable_div)
        if feed_el:
            box = await feed_el.bounding_box()
            if box:
                await page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)

        last_height = await page.evaluate(f"document.querySelector('{scrollable_div}').scrollHeight")
        no_change_count = 0
        while not stop_event.is_set() and no_change_count < 3:
            scroll_dist = random.randint(800, 1200)
            await page.mouse.wheel(0, scroll_dist)
            await page.evaluate(f"document.querySelector('{scrollable_div}').scrollBy(0, {scroll_dist})")
            await asyncio.sleep(random.uniform(2, 4))
            new_height = await page.evaluate(f"document.querySelector('{scrollable_div}').scrollHeight")
            if new_height == last_height:
                no_change_count += 1
                await page.mouse.wheel(0, 500)
            else:
                no_change_count = 0
            last_height = new_height
    except Exception as e:
        logger.debug(f"滚动加载失败: {str(e)}")


async def extract_details(page: Page):
    """从详情面板提取商家详细信息"""
    data = {"Rating": "", "Reviews": "", "Address": "", "Website": "", "Phone": ""}
    try:
        rating_el = await page.query_selector('span[role="img"]')
        if rating_el:
            label = await rating_el.get_attribute('aria-label')
            if label and "stars" in label:
                data["Rating"] = label.split("stars")[0].strip()
                if "reviews" in label:
                    data["Reviews"] = label.split("stars")[1].replace("reviews", "").strip()

        address_el = await page.query_selector('button[data-item-id="address"]')
        if address_el:
            data["Address"] = await address_el.get_attribute('aria-label')
            if data["Address"]:
                data["Address"] = data["Address"].replace("Address: ", "")

        website_el = await page.query_selector('a[data-item-id="authority"]')
        if website_el:
            data["Website"] = await website_el.get_attribute('href')

        phone_el = await page.query_selector('button[data-item-id^="phone:tel:"]')
        if phone_el:
            data["Phone"] = await phone_el.get_attribute('aria-label')
            if data["Phone"]:
                data["Phone"] = data["Phone"].replace("Phone: ", "")
    except Exception as e:
        logger.debug(f"详情提取部分失败: {str(e)}")
    return data


async def scrape_google_maps(
    browser,
    task_info,
    output_dir,
    update_gui_callback,
    stop_event: asyncio.Event,
):
    keyword = task_info["keyword"]
    location = f"{task_info['district']}, {task_info['city']}, {task_info['country']}"
    search_query = f"{keyword} in {location}"

    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800},
    )
    page = await context.new_page()
    await Stealth().apply_stealth_async(page)

    results = []
    try:
        update_gui_callback(f"正在搜索: {search_query}")
        encoded_query = quote(search_query)
        search_url = f"https://www.google.com/maps/search/{encoded_query}"

        for attempt in range(2):
            try:
                await page.goto(
                    search_url,
                    wait_until="domcontentloaded",
                    timeout=45000,
                )
                await page.wait_for_selector("div[role='feed']", timeout=15000)
                break
            except Exception:
                if attempt == 0:
                    update_gui_callback(f"搜索响应慢，正在重试 ({attempt+1}/2)...")
                    await asyncio.sleep(2)
                else:
                    raise

        await smart_scroll(page, stop_event)
        listings = await page.query_selector_all("div[role='article']")
        update_gui_callback(f"共找到 {len(listings)} 个潜在商家，准备抓取详情...")

        for index, li in enumerate(listings):
            if stop_event.is_set():
                break
            try:
                await li.scroll_into_view_if_needed()
                await li.click()
                await asyncio.sleep(random.uniform(1.5, 3.0))

                detail_data = await extract_details(page)
                detail_data["Name"] = await li.get_attribute("aria-label") or "未知商家"
                detail_data["关键词"] = keyword
                detail_data["区域"] = location
                detail_data["抓取时间"] = datetime.now().strftime("%Y-%m-%d %H:%M")

                if detail_data.get("Website"):
                    detail_data["Email"] = await find_emails_on_website(
                        detail_data["Website"], update_gui_callback
                    )
                else:
                    detail_data["Email"] = ""

                results.append(detail_data)
                update_gui_callback(
                    f"进度 ({index+1}/{len(listings)}): {detail_data['Name']}"
                )
                await asyncio.sleep(random.uniform(0.5, 1.5))
            except Exception as e:
                logger.warning(f"跳过第 {index+1} 个商家: {str(e)}")
                continue

        if results:
            base_filename = f"{keyword}_{task_info['city']}_{datetime.now().strftime('%H%M')}"
            fieldnames = [
                "Name",
                "Rating",
                "Reviews",
                "Address",
                "Website",
                "Phone",
                "Email",
                "关键词",
                "区域",
                "抓取时间",
            ]

            csv_path = os.path.join(output_dir, f"{base_filename}.csv")
            with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(
                    f, fieldnames=fieldnames, extrasaction="ignore"
                )
                writer.writeheader()
                writer.writerows(results)

            try:
                excel_path = os.path.join(output_dir, f"{base_filename}.xlsx")
                # 使用 reindex 解决 KeyError；字段缺失也会生成空列
                df = pd.DataFrame(results).reindex(columns=fieldnames)
                df.to_excel(excel_path, index=False)
                update_gui_callback(f"本地保存成功: {base_filename}.xlsx")
            except Exception as ex:
                logger.error(f"Excel 保存失败: {str(ex)}")
                update_gui_callback(f"本地 Excel 保存失败: {str(ex)}")
        else:
            update_gui_callback(f"关键词 '{keyword}' 未抓取到任何有效商家。")

    except Exception as e:
        logger.error(f"抓取过程出错: {str(e)}")
        update_gui_callback(f"错误: {keyword} 抓取异常中断")
    finally:
        await context.close()


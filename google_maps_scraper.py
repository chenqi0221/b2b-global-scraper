import asyncio
import logging
import random
from datetime import datetime

from playwright.async_api import Page
from playwright_stealth import Stealth
from urllib.parse import quote

from email_extractor import find_emails_on_website
from file_export import export_results_csv_xlsx

logger = logging.getLogger(__name__)


async def smart_scroll(page: Page, stop_event: asyncio.Event):
    """模拟真人随机滚动，防止被识别，并确保加载更多结果"""
    scrollable_div = 'div[role="feed"]'
    try:
        # 等待滚动区域出现，增加超时时间
        await page.wait_for_selector(scrollable_div, timeout=15000)
        
        # 使用locator替代query_selector
        feed_locator = page.locator(scrollable_div)
        
        # 确保滚动区域可见
        await feed_locator.wait_for(state="visible", timeout=10000)
        
        # 获取初始高度
        last_height = await page.evaluate(f"document.querySelector('{scrollable_div}').scrollHeight")
        no_change_count = 0
        max_no_change = 5
        total_scrolls = 0
        max_scrolls = 20  # 防止无限滚动
        
        while not stop_event.is_set() and no_change_count < max_no_change and total_scrolls < max_scrolls:
            total_scrolls += 1
            
            # 随机滚动距离，更接近真人行为
            scroll_dist = random.randint(600, 1500)
            
            # 尝试多种滚动方式
            try:
                await page.mouse.wheel(0, scroll_dist)
            except Exception:
                await page.evaluate(f"document.querySelector('{scrollable_div}').scrollBy(0, {scroll_dist})")
            
            # 增加等待时间，确保内容加载
            await asyncio.sleep(random.uniform(3, 5))
            
            # 再次获取高度
            new_height = await page.evaluate(f"document.querySelector('{scrollable_div}').scrollHeight")
            
            if new_height == last_height:
                no_change_count += 1
                # 尝试小幅度滚动，可能触发加载
                await page.mouse.wheel(0, 300)
                await asyncio.sleep(2)
            else:
                no_change_count = 0
                last_height = new_height
                
                # 随机暂停，更接近真人行为
                await asyncio.sleep(random.uniform(1, 2))
                
    except Exception as e:
        logger.error(f"滚动加载失败: {str(e)}")


async def extract_details(page: Page):
    """从详情面板提取商家详细信息"""
    data = {"Rating": "", "Reviews": "", "Address": "", "Website": "", "Phone": ""}
    try:
        # 使用 locator 替代 query_selector，更稳定
        
        # 提取评分和评论数
        try:
            rating_locator = page.locator('span[role="img"]')
            if await rating_locator.count() > 0:
                label = await rating_locator.first.get_attribute('aria-label')
                if label and "stars" in label:
                    parts = label.split("stars")
                    if len(parts) > 0:
                        data["Rating"] = parts[0].strip()
                    if len(parts) > 1:
                        data["Reviews"] = parts[1].replace("reviews", "").replace("review", "").strip()
        except Exception as rating_error:
            logger.debug(f"提取评分时出错: {str(rating_error)}")
        
        # 提取地址
        try:
            address_locator = page.locator('button[data-item-id="address"]')
            if await address_locator.count() > 0:
                data["Address"] = await address_locator.first.get_attribute('aria-label')
                if data["Address"]:
                    data["Address"] = data["Address"].replace("Address: ", "")
        except Exception as address_error:
            logger.debug(f"提取地址时出错: {str(address_error)}")
        
        # 提取网站
        try:
            website_locator = page.locator('a[data-item-id="authority"]')
            if await website_locator.count() > 0:
                data["Website"] = await website_locator.first.get_attribute('href')
        except Exception as website_error:
            logger.debug(f"提取网站时出错: {str(website_error)}")
        
        # 提取电话
        try:
            phone_locator = page.locator('button[data-item-id^="phone:tel:"]')
            if await phone_locator.count() > 0:
                data["Phone"] = await phone_locator.first.get_attribute('aria-label')
                if data["Phone"]:
                    data["Phone"] = data["Phone"].replace("Phone: ", "")
        except Exception as phone_error:
            logger.debug(f"提取电话时出错: {str(phone_error)}")
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

        try:
            await page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=45000,
            )
            # 等待第一个 article 或“无结果”提示
            await page.wait_for_selector("div[role='article'], div.fontBodyMedium > span", timeout=15000)
        except Exception as e:
            logger.warning(f"页面加载超时或无结果: {search_query} - {e}")
            update_gui_callback(f"[{keyword}] 页面加载超时或无结果")
            return 0, 0 # 直接返回，不继续执行

        # 检查是否是“无结果”页面
        no_results_el = await page.query_selector("div.fontBodyMedium > span")
        if no_results_el and "找不到" in await no_results_el.inner_text():
            update_gui_callback(f"[{keyword}] 未找到任何结果")
            return 0, 0

        await smart_scroll(page, stop_event)
        
        # 使用 locator 动态查找，避免 Stale Element 问题
        listings_locator = page.locator("div[role='article']")
        listings_count = await listings_locator.count()
        update_gui_callback(f"共找到 {listings_count} 个潜在商家，准备抓取详情...")

        for i in range(listings_count):
            if stop_event.is_set():
                update_gui_callback("用户停止了抓取任务。")
                break
            
            # 每次循环都重新定位元素
            listing = listings_locator.nth(i)
            retry_count = 0
            max_retries = 3
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    # 重试时重新定位元素，避免元素过期
                    listing = listings_locator.nth(i)
                    await listing.scroll_into_view_if_needed(timeout=10000)
                    
                    # 确保元素可见
                    await listing.wait_for(state="visible", timeout=5000)
                    
                    # 尝试多种点击方式
                    try:
                        await listing.click(timeout=5000)
                    except Exception as click_error:
                        update_gui_callback(f"尝试JavaScript点击商家卡片...")
                        await page.evaluate("el => el.click()", listing)
                    
                    await asyncio.sleep(random.uniform(3.0, 5.0))  # 增加等待时间，确保详情加载完成

                    detail_data = await extract_details(page)
                    
                    # 尝试多种方式获取商家名称
                    name = "未知商家"
                    try:
                        # 方式1：从aria-label获取
                        name_aria_label = await listing.get_attribute("aria-label")
                        if name_aria_label:
                            name = name_aria_label
                        else:
                            # 方式2：从fontHeadlineSmall元素获取
                            name_el = listing.locator('div.fontHeadlineSmall')
                            if await name_el.count() > 0:
                                name = await name_el.inner_text()
                            else:
                                # 方式3：从其他可能的元素获取
                                alt_name_el = listing.locator('div[class*="fontHeadline"]')
                                if await alt_name_el.count() > 0:
                                    name = await alt_name_el.inner_text()
                    except Exception as name_error:
                        logger.debug(f"获取商家名称时出错: {str(name_error)}")
                    
                    detail_data["Name"] = name
                    detail_data["关键词"] = keyword
                    detail_data["区域"] = location
                    detail_data["抓取时间"] = datetime.now().strftime("%Y-%m-%d %H:%M")

                    if detail_data.get("Website"):
                        try:
                            update_gui_callback(f"正在尝试从官网获取邮箱: `{detail_data['Website']}`")
                            detail_data["Email"] = await find_emails_on_website(
                                detail_data["Website"], update_gui_callback
                            )
                        except Exception as email_error:
                            logger.debug(f"获取邮箱时出错: {str(email_error)}")
                            detail_data["Email"] = ""
                    else:
                        detail_data["Email"] = ""

                    results.append(detail_data)
                    update_gui_callback(
                        f"进度 ({i+1}/{listings_count}): {detail_data['Name']}"
                    )
                    await asyncio.sleep(random.uniform(1.0, 2.0))
                    success = True
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        update_gui_callback(f"重试第 {i+1} 个商家 ({retry_count}/{max_retries}): {str(e)}")
                        logger.warning(f"重试第 {i+1} 个商家 ({retry_count}/{max_retries}): {str(e)}")
                        # 等待一段时间后重试
                        await asyncio.sleep(random.uniform(2.0, 3.0))
                    else:
                        update_gui_callback(f"跳过第 {i+1} 个商家: 多次尝试失败 ({str(e)})")
                        logger.error(f"跳过第 {i+1} 个商家: 多次尝试失败 ({str(e)})")

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
            export_results_csv_xlsx(
                results=results,
                base_filename=base_filename,
                output_dir=output_dir,
                fieldnames=fieldnames,
                update_gui_callback=update_gui_callback,
            )
        else:
            update_gui_callback(f"关键词 '{keyword}' 未抓取到任何有效商家。")

    except Exception as e:
        logger.error(f"抓取过程出错: {str(e)}")
        update_gui_callback(f"错误: {keyword} 抓取异常中断")
    finally:
        await context.close()
        
    email_count = sum(1 for r in results if r.get("Email"))
    return len(results), email_count


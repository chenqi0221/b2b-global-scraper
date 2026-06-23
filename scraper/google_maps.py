import asyncio
import logging
import random
from datetime import datetime

from playwright.async_api import Page
from urllib.parse import quote

from scraper.email_extractor import find_emails_on_website
from scraper.file_export import export_results_csv_xlsx
from utils.reporter import as_status_reporter

logger = logging.getLogger(__name__)


async def smart_scroll(page: Page, stop_event: asyncio.Event, update_gui_callback=None):
    """模拟真人随机滚动，防止被识别，并确保加载更多结果"""
    status_cb = as_status_reporter(update_gui_callback)
    scrollable_div = 'div[role="feed"]'
    try:
        # 等待滚动区域出现，增加超时时间
        await page.wait_for_selector(scrollable_div, timeout=15000)

        # 使用locator替代query_selector
        feed_locator = page.locator(scrollable_div)

        # 确保滚动区域可见
        await feed_locator.wait_for(state="visible", timeout=10000)

        status_cb("开始自动下滑加载更多结果...")

        # 页面异常早停：未加载出商家卡片或被 Google 拦截时，不要无意义滚动
        article_count = await page.locator('div[role="article"]').count()
        if article_count == 0:
            body_text = ""
            try:
                body_text = await page.evaluate("() => document.body.innerText.substring(0, 500)")
            except Exception:
                pass
            if any(x in body_text for x in ["unusual traffic", "captcha", "CAPTCHA", "验证", "Verify", "机器人"]):
                status_cb("[警告] 页面疑似被 Google 拦截，停止滚动以避免额外请求。", "warning")
                return
            # 也可能是真无结果，直接返回
            status_cb("[提示] 当前关键词未加载出商家卡片，跳过滚动。")
            return

        # 获取初始高度
        last_height = await page.evaluate(f"document.querySelector('{scrollable_div}').scrollHeight")
        no_change_count = 0
        max_no_change = 5
        total_scrolls = 0
        # 动态限制最大滚动次数，避免被拦截页面无意义滚到硬上限
        max_scrolls = min(50, max(5, article_count // 5 + 5))

        status_cb(f"初始页面高度: {last_height}px，开始滚动加载...")

        while not stop_event.is_set() and no_change_count < max_no_change and total_scrolls < max_scrolls:
            total_scrolls += 1

            # 随机滚动距离，更接近真人行为
            scroll_dist = random.randint(800, 2000)

            # 尝试多种滚动方式
            try:
                # 先尝试直接滚动到页面底部附近
                await page.evaluate(f"""
                    const feed = document.querySelector('{scrollable_div}');
                    if (feed) {{
                        feed.scrollTo(0, feed.scrollHeight);
                    }}
                """)
            except Exception:
                try:
                    await page.mouse.wheel(0, scroll_dist)
                except Exception:
                    await page.evaluate(f"document.querySelector('{scrollable_div}').scrollBy(0, {scroll_dist})")

            # 增加等待时间，确保内容加载
            await asyncio.sleep(random.uniform(2, 4))

            # 再次获取高度
            new_height = await page.evaluate(f"document.querySelector('{scrollable_div}').scrollHeight")

            if total_scrolls % 5 == 0:
                status_cb(f"已滚动 {total_scrolls} 次，当前高度: {new_height}px")

            if new_height == last_height:
                no_change_count += 1
                # 尝试小幅度滚动，可能触发加载
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(1.5)
            else:
                no_change_count = 0
                last_height = new_height

                # 随机暂停，更接近真人行为
                await asyncio.sleep(random.uniform(0.5, 1.5))

        status_cb(f"滚动完成，共滚动 {total_scrolls} 次，最终高度: {last_height}px")
                
    except Exception as e:
        logger.error(f"滚动加载失败: {str(e)}")
        status_cb(f"滚动加载出现问题: {str(e)}", "error")


async def _dismiss_google_consent(page: Page) -> bool:
    consent_selectors = [
        'button[aria-label="Accept all"]',
        'button:has-text("Accept all")',
        'button:has-text("I agree")',
        'button:has-text("OK")',
        'button[aria-label="Reject all"]',
        'button:has-text("Reject all")',
        'form[action*="consent"] button',
    ]
    for selector in consent_selectors:
        try:
            btn = page.locator(selector).first
            if await btn.count() > 0 and await btn.is_visible(timeout=2000):
                await btn.click(timeout=3000)
                await page.wait_for_timeout(2000)
                logger.info(f"[Consent] dismissed via {selector}")
                return True
        except Exception:
            continue
    return False


async def _capture_page_diagnostic(page: Page, keyword: str, output_dir: str) -> str:
    import os as _os
    diag_dir = _os.path.join(output_dir, "_diagnostic")
    _os.makedirs(diag_dir, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    safe_kw = keyword.replace(" ", "_").replace("/", "_")[:30]
    screenshot_path = _os.path.join(diag_dir, f"{safe_kw}_{ts}.png")
    try:
        await page.screenshot(path=screenshot_path, full_page=False)
    except Exception:
        screenshot_path = "(failed)"
    try:
        page_title = await page.title()
        body_text = await page.evaluate("() => document.body.innerText.substring(0, 300)")
    except Exception:
        page_title = "(failed)"
        body_text = "(failed)"
    return (
        f"[诊断] '{keyword}' 超时\n"
        f"  标题: {page_title}\n"
        f"  文本(300): {body_text}\n"
        f"  截图: {screenshot_path}"
    )


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


async def _first_locator_attribute(page: Page, selectors: list[str], attribute: str) -> str:
    """依次尝试选择器，返回第一个非空属性值。"""
    for selector in selectors:
        try:
            locator = page.locator(selector)
            if await locator.count() > 0:
                value = await locator.first.get_attribute(attribute)
                if value:
                    return value
        except Exception:
            continue
    return ""


async def extract_details(page: Page):
    """从详情面板提取商家详细信息（带选择器降级）"""
    data = {"Rating": "", "Reviews": "", "Address": "", "Website": "", "Phone": ""}
    try:
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

        # 提取地址、网站、电话，使用多选择器降级
        address = await _first_locator_attribute(page, ADDRESS_SELECTORS, 'aria-label')
        if address:
            data["Address"] = address.replace("Address: ", "")

        data["Website"] = await _first_locator_attribute(page, WEBSITE_SELECTORS, 'href')

        phone = await _first_locator_attribute(page, PHONE_SELECTORS, 'aria-label')
        if phone:
            data["Phone"] = phone.replace("Phone: ", "")
    except Exception as e:
        logger.debug(f"详情提取部分失败: {str(e)}")
    return data


async def scrape_google_maps(
    browser,
    task_info,
    output_dir,
    update_gui_callback=None,
    stop_event: asyncio.Event = None,
    on_progress=None,
):
    status_cb = as_status_reporter(update_gui_callback)
    if stop_event is None:
        stop_event = asyncio.Event()
    keyword = task_info["keyword"]
    location = f"{task_info['district']}, {task_info['city']}, {task_info['country']}"
    search_query = f"{keyword} in {location}"

    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        timezone_id="America/New_York",
        permissions=["geolocation"],
        java_script_enabled=True,
    )
    page = await context.new_page()
    # 基础反检测脚本（替代 playwright_stealth）
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        window.chrome = { runtime: {} };
    """)

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
            await page.wait_for_timeout(2000)
            dismissed = await _dismiss_google_consent(page)
            if dismissed:
                await page.wait_for_timeout(1000)
            await page.wait_for_selector("div[role='article'], div.fontBodyMedium > span", timeout=25000)
        except Exception as e:
            diag_msg = await _capture_page_diagnostic(page, keyword, output_dir)
            logger.warning(f"页面加载超时或无结果: {search_query} - {e}")
            update_gui_callback(diag_msg)
            update_gui_callback(f"[{keyword}] 页面加载超时或无结果")
            return 0, 0

        # 检查是否是“无结果”页面
        no_results_el = await page.query_selector("div.fontBodyMedium > span")
        if no_results_el and "找不到" in await no_results_el.inner_text():
            update_gui_callback(f"[{keyword}] 未找到任何结果")
            return 0, 0

        await smart_scroll(page, stop_event, update_gui_callback)
        
        # 使用 locator 动态查找，避免 Stale Element 问题
        listings_locator = page.locator("div[role='article']")
        listings_count = await listings_locator.count()
        update_gui_callback(f"共找到 {listings_count} 个潜在商家，准备抓取详情...")
        if on_progress:
            on_progress("found", count=listings_count)

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
                                detail_data["Website"],
                                update_gui_callback,
                                max_pages_per_site=2,
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
                    if on_progress:
                        on_progress("business", index=i, success=True)
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
                        if on_progress:
                            on_progress("business", index=i, success=False)

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
        error_msg = str(e)
        logger.error(f"抓取过程出错: {error_msg}")
        # 区分 Connection closed 错误和其他错误
        if "Connection closed" in error_msg or "Target page, context or browser has been closed" in error_msg:
            update_gui_callback(f"[错误] {keyword} 浏览器连接断开，可能是内存不足或浏览器崩溃")
            # 重新抛出，让上层处理重试
            raise
        else:
            update_gui_callback(f"[错误] {keyword} 抓取异常: {error_msg}")
    finally:
        try:
            await context.close()
        except Exception:
            pass  # 浏览器可能已被关闭，忽略错误
        
    email_count = sum(1 for r in results if r.get("Email"))
    return len(results), email_count


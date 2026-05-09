import asyncio
import csv
import os
import random
import logging
import re
import httpx
import requests
import pandas as pd
import gspread
from googleapiclient.discovery import build
from urllib.parse import urljoin, quote
from datetime import datetime
from playwright.async_api import async_playwright, Page
from playwright_stealth import Stealth
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
raw_proxy = os.getenv("HTTP_PROXY") # 获取代理配置

# 格式化代理字符串，确保包含协议头
if raw_proxy:
    if not raw_proxy.startswith(('http://', 'https://', 'socks5://')):
        HTTP_PROXY = f"http://{raw_proxy}"
    else:
        HTTP_PROXY = raw_proxy
else:
    HTTP_PROXY = None

# 如果配置了代理，设置到环境变量中，gspread 和 google-api-client 会自动识别
if HTTP_PROXY:
    os.environ['HTTP_PROXY'] = HTTP_PROXY
    os.environ['HTTPS_PROXY'] = HTTP_PROXY
    os.environ['http_proxy'] = HTTP_PROXY # 增加小写以覆盖更多库
    os.environ['https_proxy'] = HTTP_PROXY # 增加小写以覆盖更多库
    os.environ['all_proxy'] = HTTP_PROXY # 增加 all_proxy 以覆盖更多库

logger = logging.getLogger(__name__)

def get_google_auth():
    """获取 Google Auth 凭据 (共用函数)"""
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    client_secret_path = os.path.abspath('client_secret.json')
    token_path = os.path.abspath('token.json')

    if not os.path.exists(client_secret_path):
        raise FileNotFoundError("根目录找不到 client_secret.json")

    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request, AuthorizedSession
    from google.oauth2.credentials import Credentials

    # 创建一个代理感知的 Session
    session = requests.Session()
    if HTTP_PROXY:
        session.proxies = {'http': HTTP_PROXY, 'https': HTTP_PROXY}
    google_request = Request(session=session)

    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        except Exception:
            creds = None
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                # 显式使用代理进行刷新
                creds.refresh(google_request)
            except Exception:
                # 如果刷新失败，重新授权
                flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    # 返回凭据和带代理的授权 Session
    authed_session = AuthorizedSession(creds)
    if HTTP_PROXY:
        authed_session.proxies = {'http': HTTP_PROXY, 'https': HTTP_PROXY}
    authed_session.timeout = 30 # 增加超时时间
    
    return creds, authed_session

def get_or_create_drive_folder(authed_session, folder_name="langdeng"):
    """在 Google Drive 中查找或创建文件夹 (使用 requests 提高稳定性)"""
    # 1. 查找文件夹
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    url = f"https://www.googleapis.com/drive/v3/files?q={quote(query)}&fields=files(id, name)"
    
    resp = authed_session.get(url)
    resp.raise_for_status()
    items = resp.json().get('files', [])

    if items:
        return items[0]['id']

    # 2. 不存在则创建
    create_url = "https://www.googleapis.com/drive/v3/files"
    payload = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    create_resp = authed_session.post(create_url, json=payload)
    create_resp.raise_for_status()
    return create_resp.json().get('id')

async def upload_to_google_sheets(df: pd.DataFrame, title: str, update_gui_callback, folder_name="langdeng", mode="append"):
    """将数据上传到 Google Sheets (支持覆盖和追加去重模式，默认为追加去重)"""
    try:
        update_gui_callback(f"准备同步云端: {title}")
        creds, authed_session = get_google_auth()
        
        # 1. 定位云端文件夹
        update_gui_callback(f"正在定位云端文件夹...")
        folder_id = get_or_create_drive_folder(authed_session, folder_name)
        
        # 2. 在文件夹中查找同名文件
        update_gui_callback(f"正在检查云端文件...")
        query = f"name = '{title}' and '{folder_id}' in parents and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
        search_url = f"https://www.googleapis.com/drive/v3/files?q={quote(query)}&fields=files(id, name)"
        search_resp = authed_session.get(search_url)
        search_resp.raise_for_status()
        files = search_resp.json().get('files', [])
        
        # gspread 注入带代理的 AuthorizedSession
        gc = gspread.Client(auth=creds, session=authed_session)
        
        if files:
            update_gui_callback(f"连接云端表格: {title}")
            sh = gc.open_by_key(files[0]['id'])
        else:
            update_gui_callback(f"创建新云端表格: {title}")
            sh = gc.create(title)
            file_id = sh.id
            
            # 移动到指定文件夹 (Drive v3 使用 PATCH 并带 query params)
            update_gui_callback(f"正在归类到 '{folder_name}' 文件夹...")
            move_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?addParents={folder_id}&removeParents=root"
            move_resp = authed_session.patch(move_url)
            move_resp.raise_for_status()

        # 3. 更新内容
        worksheet = sh.get_worksheet(0)
        final_df = df.copy()
        
        # 如果是追加模式且文件已存在，先读取云端数据进行合并去重
        if mode == "append" and files:
            try:
                update_gui_callback(f"正在读取云端已有数据进行合并去重...")
                # 获取所有值，包括表头
                existing_values = worksheet.get_all_values()
                if existing_values and len(existing_values) > 1:
                    existing_df = pd.DataFrame(existing_values[1:], columns=existing_values[0])
                    # 合并本地和云端数据
                    combined_df = pd.concat([existing_df, final_df], ignore_index=True)
                    # 全局去重：基于名称、电话、地址
                    final_df = combined_df.drop_duplicates(subset=['Name', 'Phone', 'Address'], keep='first')
                    update_gui_callback(f"合并完成：云端新增 {len(final_df) - len(existing_df)} 条唯一记录")
                else:
                    update_gui_callback(f"云端表格为空，直接写入数据")
            except Exception as read_err:
                logger.warning(f"读取云端数据失败，将回退到覆盖模式: {read_err}")

        # 最终确保没有任何 NaN 值，防止 JSON 解析失败 (解决 Out of range float values 报错)
        final_df = final_df.fillna("")
        # 转换为列表格式用于上传
        data = [final_df.columns.values.tolist()] + final_df.values.tolist()
        
        update_gui_callback(f"正在写入数据到云端...")
        worksheet.clear()
        worksheet.update('A1', data)
        
        update_gui_callback(f"云端同步完成！")
        return True, final_df
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Google Sheets 操作失败: {error_msg}")
        if "10060" in error_msg or "timeout" in error_msg.lower():
            update_gui_callback(f"同步失败: 网络连接超时 (30s)。")
        else:
            update_gui_callback(f"同步失败: {error_msg}")
        return False, None

async def aggregate_and_sync(dir_path: str, update_gui_callback, target_title="lengdangb2b"):
    """汇总目录下所有 CSV 并去重上传"""
    try:
        csv_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith('.csv') and f != f"{target_title}.csv"]
        if not csv_files:
            update_gui_callback("未找到可汇总的 CSV 文件")
            return False
            
        update_gui_callback(f"正在汇总 {len(csv_files)} 个文件的数据...")
        all_dfs = []
        for f in csv_files:
            try:
                df = pd.read_csv(f)
                if not df.empty:
                    all_dfs.append(df)
            except Exception as e:
                logger.warning(f"读取文件 {f} 失败: {e}")
                
        if not all_dfs:
            update_gui_callback("所有文件内容均为空，取消汇总")
            return False
            
        # 合并所有数据
        combined_df = pd.concat(all_dfs, ignore_index=True)
        original_count = len(combined_df)
        
        # 去重逻辑：基于名称和电话，或者名称和地址
        combined_df = combined_df.drop_duplicates(subset=['Name', 'Phone', 'Address'], keep='first')
        new_count = len(combined_df)
        
        update_gui_callback(f"本地汇总完成: 原始 {original_count} 条 -> 去重后 {new_count} 条")
        
        # 上传到云端 (默认使用追加模式)
        # upload_to_google_sheets 会读取云端数据进行二次合并去重
        success, final_df = await upload_to_google_sheets(combined_df, target_title, update_gui_callback)
        
        if success and final_df is not None:
            # 保存最终的、包含云端数据的最全汇总文件到项目根目录
            summary_path = os.path.abspath(f"{target_title}.csv")
            final_df.to_csv(summary_path, index=False, encoding='utf-8-sig')
            update_gui_callback(f"根目录汇总文件已更新(含云端数据): {target_title}.csv")
            return True
        return False
    except Exception as e:
        update_gui_callback(f"汇总同步失败: {str(e)}")
        logger.error(f"汇总同步失败: {e}")
        return False

async def test_connection(update_gui_callback):
    """测试当前网络环境是否能连接到 Google (用于验证代理配置)"""
    test_url = "https://www.google.com/generate_204"
    try:
        update_gui_callback(f"正在测试连接: {test_url}")
        if HTTP_PROXY:
            update_gui_callback(f"使用代理: {HTTP_PROXY}")
        
        async with httpx.AsyncClient(timeout=10.0, proxy=HTTP_PROXY, verify=False) as client:
            start_time = datetime.now()
            response = await client.get(test_url)
            duration = (datetime.now() - start_time).total_seconds()
            
            if response.status_code in [200, 204]:
                update_gui_callback(f"连接成功！延迟: {duration:.2f}s")
                return True
            else:
                update_gui_callback(f"连接异常，状态码: {response.status_code}")
                return False
    except Exception as e:
        error_msg = str(e)
        if "10060" in error_msg:
            update_gui_callback("连接失败: 代理配置错误或代理不可用 (Timeout 10060)")
        elif "10061" in error_msg:
            update_gui_callback("连接失败: 代理软件未运行或端口填写错误 (Connection Refused 10061)")
        else:
            update_gui_callback(f"连接失败: {error_msg}")
        return False

# 用于查找邮箱的正则表达式
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

async def find_emails_on_website(url, update_gui_callback):
    """访问官网并尝试寻找电子邮箱"""
    if not url or not url.startswith('http'):
        return ""
    
    try:
        update_gui_callback(f"正在尝试从官网获取邮箱: {url}")
        # 如果配置了代理，httpx 会自动识别环境变量或在这里显式传入
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, verify=False, proxy=HTTP_PROXY) as client:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
            
            # 1. 抓取主页
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return ""
            
            html = response.text
            emails = set(re.findall(EMAIL_REGEX, html))
            
            # 2. 如果主页没找到，尝试找“Contact Us”页面
            if not emails:
                contact_patterns = ['contact', 'about', 'reach', 'info', 'support']
                links = re.findall(r'href=["\']([^"\']+)["\']', html)
                contact_link = None
                for link in links:
                    if any(p in link.lower() for p in contact_patterns):
                        if link.startswith('http'):
                            contact_link = link
                        else:
                            contact_link = urljoin(url, link)
                        break
                
                if contact_link:
                    contact_resp = await client.get(contact_link, headers=headers)
                    if contact_resp.status_code == 200:
                        emails.update(re.findall(EMAIL_REGEX, contact_resp.text))
            
            filtered_emails = [e for e in emails if not any(x in e.lower() for x in ['.png', '.jpg', '.jpeg', '.gif', 'sentry.io', 'wix.com', 'example.com', 'yourname'])]
            
            if filtered_emails:
                found = ", ".join(list(filtered_emails)[:3])
                return found
                    
    except Exception as e:
        logger.debug(f"访问官网 {url} 失败: {str(e)}")
        
    return ""

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

async def scrape_google_maps(browser, task_info, output_dir, update_gui_callback, stop_event):
    keyword = task_info['keyword']
    location = f"{task_info['district']}, {task_info['city']}, {task_info['country']}"
    search_query = f"{keyword} in {location}"
    
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={'width': 1280, 'height': 800}
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
                await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_selector('div[role="feed"]', timeout=15000)
                break
            except Exception as e:
                if attempt == 0:
                    update_gui_callback(f"搜索响应慢，正在重试 ({attempt+1}/2)...")
                    await asyncio.sleep(2)
                else:
                    raise e

        await smart_scroll(page, stop_event)
        listings = await page.query_selector_all('div[role="article"]')
        update_gui_callback(f"共找到 {len(listings)} 个潜在商家，准备抓取详情...")

        for index, li in enumerate(listings):
            if stop_event.is_set(): break
            try:
                await li.scroll_into_view_if_needed()
                await li.click()
                await asyncio.sleep(random.uniform(1.5, 3.0))

                detail_data = await extract_details(page)
                detail_data["Name"] = await li.get_attribute('aria-label') or "未知商家"
                detail_data["关键词"] = keyword
                detail_data["区域"] = location
                detail_data["抓取时间"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                if detail_data.get("Website"):
                    detail_data["Email"] = await find_emails_on_website(detail_data["Website"], update_gui_callback)
                else:
                    detail_data["Email"] = ""

                results.append(detail_data)
                update_gui_callback(f"进度 ({index+1}/{len(listings)}): {detail_data['Name']}")
                await asyncio.sleep(random.uniform(0.5, 1.5))
            except Exception as e:
                logger.warning(f"跳过第 {index+1} 个商家: {str(e)}")
                continue

        if results:
            base_filename = f"{keyword}_{task_info['city']}_{datetime.now().strftime('%H%M')}"
            fieldnames = ["Name", "Rating", "Reviews", "Address", "Website", "Phone", "Email", "关键词", "区域", "抓取时间"]
            
            csv_path = os.path.join(output_dir, f"{base_filename}.csv")
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(results)
            
            try:
                excel_path = os.path.join(output_dir, f"{base_filename}.xlsx")
                df = pd.DataFrame(results)
                df = df[fieldnames]
                df.to_excel(excel_path, index=False)
                update_gui_callback(f"本地保存成功: {base_filename}.xlsx")
                
                await upload_to_google_sheets(df, base_filename, update_gui_callback)
            except Exception as ex:
                logger.error(f"Excel 或云端同步失败: {str(ex)}")
                update_gui_callback(f"同步失败: {str(ex)}")

    except Exception as e:
        logger.error(f"抓取过程出错: {str(e)}")
        update_gui_callback(f"错误: {keyword} 抓取异常中断")
    finally:
        await context.close()

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
            if data["Address"]: data["Address"] = data["Address"].replace("Address: ", "")

        website_el = await page.query_selector('a[data-item-id="authority"]')
        if website_el:
            data["Website"] = await website_el.get_attribute('href')

        phone_el = await page.query_selector('button[data-item-id^="phone:tel:"]')
        if phone_el:
            data["Phone"] = await phone_el.get_attribute('aria-label')
            if data["Phone"]: data["Phone"] = data["Phone"].replace("Phone: ", "")
    except Exception as e:
        logger.debug(f"详情提取部分失败: {str(e)}")
    return data

import asyncio
import csv
import os
import random
import logging
import httpx
import requests
import pandas as pd
import gspread
from googleapiclient.discovery import build
from urllib.parse import quote
from datetime import datetime
from playwright.async_api import async_playwright, Page
from playwright_stealth import Stealth

from config import HTTP_PROXY
from email_extractor import find_emails_on_website
from google_maps_scraper import extract_details, smart_scroll, scrape_google_maps
from google_auth import get_google_auth
from google_drive import get_or_create_drive_folder
from google_sheets_service import upload_to_google_sheets
from sheet_aggregator import aggregate_and_sync

logger = logging.getLogger(__name__)

#
# Google Sheets / Drive / OAuth 相关实现已迁移到独立模块
# （在本文件中通过 import 重导出原函数名以保持兼容）

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

async def generate_keywords_with_ai(seed_word, num=7):
    """
    异步封装 AI 关键词生成函数，调用 ai_generator.py
    """
    try:
        from ai_generator import get_keywords_from_ai
        # 使用 run_in_executor 将同步的 AI 请求放到线程池中运行，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, get_keywords_from_ai, seed_word, num)
    except Exception as e:
        logging.error(f"调用 AI 生成关键词失败: {str(e)}")
        return []

#
# scrape_google_maps 已迁移到 google_maps_scraper.py
# （通过同名 import 保持 scraper_core 对外接口兼容）

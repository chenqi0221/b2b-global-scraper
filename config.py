"""全局配置，从环境变量读取。"""

from __future__ import annotations

import os

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

HTTP_PROXY: str = os.getenv("HTTP_PROXY", "")
GOOGLE_SHEETS_ID: str = os.getenv("GOOGLE_SHEETS_ID", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
DOUBAO_API_KEY: str = os.getenv("DOUBAO_API_KEY", "")
DOUBAO_BASE_URL: str = os.getenv("DOUBAO_BASE_URL", "")
DOUBAO_MODEL_ENDPOINT: str = os.getenv("DOUBAO_MODEL_ENDPOINT", "")

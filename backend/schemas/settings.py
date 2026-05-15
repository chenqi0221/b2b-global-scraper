"""应用设置与同步请求体。"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class EnvSettingsView(BaseModel):
    """与 `gui` 同步页一致的字段（展示已脱敏）。"""

    HTTP_PROXY: str = ""
    GOOGLE_SHEETS_ID: str = ""
    GEMINI_API_KEY: str = ""
    DOUBAO_API_KEY: str = ""
    DOUBAO_BASE_URL: str = ""
    DOUBAO_MODEL_ENDPOINT: str = ""
    SYNC_BY_DATE: bool = False
    SYNC_CONFLICT_RESOLUTION: str = "keep_latest"


class EnvSettingsSave(BaseModel):
    HTTP_PROXY: Optional[str] = None
    GOOGLE_SHEETS_ID: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    DOUBAO_API_KEY: Optional[str] = None
    DOUBAO_BASE_URL: Optional[str] = None
    DOUBAO_MODEL_ENDPOINT: Optional[str] = None
    SYNC_BY_DATE: Optional[bool] = None
    SYNC_CONFLICT_RESOLUTION: Optional[str] = None


class SyncFileBody(BaseModel):
    file_path: str


class AggregateSyncBody(BaseModel):
    dir_path: str
    target_title: str = "lengdangb2b"
    by_date: bool = False
    conflict_resolution: str = Field(default="keep_latest")


class KeywordPair(BaseModel):
    en: str
    zh: str = ""


class KeywordDeleteBody(BaseModel):
    items: List[KeywordPair]


class AiGenBody(BaseModel):
    seed: str
    num: int = Field(default=7, ge=1)

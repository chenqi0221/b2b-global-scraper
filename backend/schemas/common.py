from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.2.0"
    python_path: Optional[str] = None


class LocationModel(BaseModel):
    country: str = ""
    city: str = ""
    district: str = ""


class ScrapeRequest(BaseModel):
    keywords: List[str] = Field(default_factory=list)
    location: LocationModel = Field(default_factory=LocationModel)
    concurrency: int = Field(default=3, ge=1, le=20)
    headless: bool = Field(default=True)


class ScrapeStatusResponse(BaseModel):
    """抓取状态响应"""
    is_running: bool = False
    total_found: int = 0
    email_found: int = 0
    synced_count: int = 0
    current_keyword: Optional[str] = None
    output_dir: Optional[str] = None
    keywords: List[dict] = Field(default_factory=list)  # [{keyword, status, found, processed, succeeded, skipped}]
    total_keywords: int = 0
    completed_keywords: int = 0

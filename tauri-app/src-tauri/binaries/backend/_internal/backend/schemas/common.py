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


class ScrapeStatusResponse(BaseModel):
    is_running: bool
    total_found: int
    email_found: int
    synced_count: int
    current_keyword: Optional[str] = None
    output_dir: Optional[str] = None

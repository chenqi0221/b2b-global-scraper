"""与 `gui.app.ScraperApp._prepare_location` 对齐：预设地理位置 → 英文 country/city/district。"""

from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel

from data import GEOGRAPHICAL_DATA


class ResolveLocationRequest(BaseModel):
    mode: Literal["select", "manual"] = "select"
    continent: str = ""
    country: str = ""
    city: str = ""
    district: str = "所有"
    manual_address: str = ""


class ResolvedLocation(BaseModel):
    country: str = ""
    city: str = ""
    district: str = ""


def resolve_location(body: ResolveLocationRequest) -> Optional[ResolvedLocation]:
    if body.mode == "manual":
        addr = body.manual_address.strip()
        if not addr:
            return None
        # 中文地址翻译仍由桌面端 / AI 流程处理；此处仅透传（与无翻译时的降级一致）
        return ResolvedLocation(country="", city=addr, district="")

    if not body.continent or not body.country or not body.city:
        return None

    try:
        node = GEOGRAPHICAL_DATA[body.continent][body.country]
        country_en = node["en"]
    except Exception:
        return None

    city_en_match = re.search(r"\((.*?)\)", body.city)
    city_en = city_en_match.group(1) if city_en_match else body.city

    district_full = body.district or "所有"
    if district_full and district_full != "所有":
        district_match = re.search(r"^(.*?)\s*\(", district_full)
        district = district_match.group(1) if district_match else district_full
    else:
        district = city_en

    return ResolvedLocation(country=country_en, city=city_en, district=district)

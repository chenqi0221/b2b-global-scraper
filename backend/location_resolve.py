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
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[resolve_location] received: continent={body.continent!r} country={body.country!r} city={body.city!r} district={body.district!r}")

    if body.mode == "manual":
        addr = body.manual_address.strip()
        if not addr:
            return None
        # 中文地址翻译仍由桌面端 / AI 流程处理；此处仅透传（与无翻译时的降级一致）
        return ResolvedLocation(country="", city=addr, district="")

    if not body.continent or not body.country or not body.city:
        logger.info("[resolve_location] missing required field")
        return None

    try:
        node = GEOGRAPHICAL_DATA[body.continent][body.country]
        country_en = node["en"]
        logger.info(f"[resolve_location] direct lookup OK: country_en={country_en!r}")
    except Exception as e:
        logger.info(f"[resolve_location] direct lookup failed: {e}")
        # 如果 continent/country 已经是英文，尝试反向查找
        country_en = body.country
        node = None
        for cont_data in GEOGRAPHICAL_DATA.values():
            for cn_name, cn_data in cont_data.items():
                if cn_name == body.country or cn_data.get("en") == body.country:
                    country_en = cn_data["en"]
                    node = cn_data
                    break
            if node is not None:
                break
        if node is None:
            logger.info("[resolve_location] reverse lookup also failed")
            return None
        logger.info(f"[resolve_location] reverse lookup OK: country_en={country_en!r}")

    city_en_match = re.search(r"\((.*?)\)", body.city)
    city_en = city_en_match.group(1) if city_en_match else body.city

    district_full = body.district or "所有"
    if district_full and district_full != "所有":
        district_match = re.search(r"^(.*?)\s*\(", district_full)
        district = district_match.group(1) if district_match else district_full
    else:
        district = city_en

    logger.info(f"[resolve_location] returning: country={country_en!r} city={city_en!r} district={district!r}")
    return ResolvedLocation(country=country_en, city=city_en, district=district)

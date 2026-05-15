"""静态元数据：行业、地理级联（与 `data.py` 同源）。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.location_resolve import ResolveLocationRequest, resolve_location
from backend.schemas.common import LocationModel
from data import GEOGRAPHICAL_DATA, INDUSTRY_KEYWORDS

router = APIRouter()


@router.get("/geography")
def get_geography():
    return GEOGRAPHICAL_DATA


@router.get("/industries")
def get_industries():
    return INDUSTRY_KEYWORDS


@router.post("/resolve-location", response_model=LocationModel)
def post_resolve_location(body: ResolveLocationRequest):
    loc = resolve_location(body)
    if loc is None:
        raise HTTPException(
            status_code=400,
            detail="无法解析地理位置：请检查大洲/国家/城市是否选全，或填写手动地址",
        )
    return LocationModel(country=loc.country, city=loc.city, district=loc.district)

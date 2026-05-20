from fastapi import APIRouter, Depends

from backend.deps import get_scraper_controller
from backend.schemas.common import ScrapeRequest, ScrapeStatusResponse
from backend.services.log_bus import log_bus
from core.scraper_controller import ScraperController

router = APIRouter()


@router.post("/start")
def start_scrape(
    body: ScrapeRequest,
    ctrl: ScraperController = Depends(get_scraper_controller),
):
    loc = body.location.model_dump()
    ctrl.start_scraping(body.keywords, loc, body.concurrency, body.headless)
    log_bus.publish(
        f"抓取任务已启动：关键词 {len(body.keywords)} 个，并发 {body.concurrency}",
        "info",
    )
    return {"ok": True, "output_dir": ctrl.output_dir}


@router.post("/stop")
def stop_scrape(ctrl: ScraperController = Depends(get_scraper_controller)):
    ctrl.stop_scraping()
    log_bus.publish("已请求停止抓取", "warning")
    return {"ok": True}


@router.get("/status", response_model=ScrapeStatusResponse)
def scrape_status(ctrl: ScraperController = Depends(get_scraper_controller)):
    return ScrapeStatusResponse(
        is_running=ctrl.is_running,
        total_found=ctrl.total_found,
        email_found=ctrl.email_found,
        synced_count=ctrl.synced_count,
        current_keyword=None,
        output_dir=ctrl.output_dir,
        keywords=list(getattr(ctrl, "keyword_progress", {}).values()),
        total_keywords=getattr(ctrl, "total_keywords", 0),
        completed_keywords=getattr(ctrl, "completed_keywords", 0),
    )

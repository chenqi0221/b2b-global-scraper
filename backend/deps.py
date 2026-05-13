"""共享依赖：抓取控制器、配置服务单例。"""

from __future__ import annotations

from typing import Optional

from core.config_service import ConfigService
from core.scraper_controller import ScraperController

_controller: Optional[ScraperController] = None
_config: Optional[ConfigService] = None


def get_scraper_controller() -> ScraperController:
    global _controller
    if _controller is None:
        _controller = ScraperController()
    return _controller


def get_config_service() -> ConfigService:
    global _config
    if _config is None:
        _config = ConfigService()
    return _config

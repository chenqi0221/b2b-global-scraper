"""关键词服务"""

import threading
from typing import Callable, List, Tuple, Optional
from async_utils import run_coro_in_new_loop


class KeywordService:
    """关键词服务，负责 AI 生成和关键词库管理"""
    
    def __init__(self):
        self.on_keywords_generated: Optional[Callable[[List[Tuple[str, str]]], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
    
    def generate_keywords(self, seed_word: str, num: int = 7):
        """异步生成关键词"""
        thread = threading.Thread(
            target=self._generate_worker,
            args=(seed_word, num),
            daemon=True
        )
        thread.start()
    
    def _generate_worker(self, seed_word: str, num: int):
        """生成关键词工作线程"""
        try:
            from scraper_core import generate_keywords_with_ai
            keywords = run_coro_in_new_loop(generate_keywords_with_ai(seed_word, num))
            
            if self.on_keywords_generated:
                self.on_keywords_generated(keywords)
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))

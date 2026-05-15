"""同步服务"""

import threading
from typing import Callable, Optional
from async_utils import run_coro_in_new_loop


class SyncService:
    """同步服务，负责 Google Sheets 同步"""
    
    def __init__(self):
        self.on_sync_complete: Optional[Callable[[bool, str], None]] = None
    
    def sync_file(self, file_path: str, title: str):
        """同步单个文件"""
        thread = threading.Thread(
            target=self._sync_worker,
            args=(file_path, title),
            daemon=True
        )
        thread.start()
    
    def _sync_worker(self, file_path: str, title: str):
        """同步工作线程"""
        try:
            import pandas as pd
            from scraper_core import upload_to_google_sheets
            
            df = pd.read_csv(file_path)
            success, _ = run_coro_in_new_loop(upload_to_google_sheets(df, title, lambda msg: None))
            
            if self.on_sync_complete:
                self.on_sync_complete(success, f"文件 '{title}' 同步{'成功' if success else '失败'}")
        except Exception as e:
            if self.on_sync_complete:
                self.on_sync_complete(False, str(e))

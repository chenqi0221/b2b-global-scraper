"""AI 策略页面"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from gui.pages.base_page import BasePage


class AIStrategyPage(BasePage):
    """AI 策略页面"""
    
    def _setup_ui(self):
        """设置界面"""
        tb.Label(self, text="AI 生成关键词提示词模板", font=("Helvetica", 18, "bold")).pack(pady=(20, 10))
        
        self.prompt_text = tb.Text(self, height=15, wrap=WORD, font=("微软雅黑", 10))
        self.prompt_text.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        self.save_btn = tb.Button(self, text="保存模板", bootstyle="success")
        self.save_btn.pack(pady=10)

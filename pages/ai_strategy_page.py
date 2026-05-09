import ttkbootstrap as tb
from ttkbootstrap.constants import *

class AIStrategyPage(tb.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        tb.Label(self, text="AI 生成关键词提示词模板", font=("Helvetica", 18, "bold")).pack(pady=(20, 10))
        
        self.prompt_text = tb.Text(self, height=15, wrap=WORD, font=("微软雅黑", 10))
        self.prompt_text.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        self.save_btn = tb.Button(self, text="保存模板", bootstyle="success")
        self.save_btn.pack(pady=10)

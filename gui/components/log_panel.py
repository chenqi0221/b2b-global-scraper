"""日志面板组件，带语法高亮、级别图标、时间戳格式化"""

import tkinter as tk
import ttkbootstrap as tb
from datetime import datetime
from gui.theme import LOG_COLORS, FONTS, BACKGROUND_COLORS


class LogPanel(tb.Frame):
    """日志面板组件"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置界面"""
        # 工具栏
        toolbar = tb.Frame(self)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        tb.Label(toolbar, text="运行日志", font=FONTS["subtitle"]).pack(side=tk.LEFT)
        
        # 日志级别过滤
        self.level_var = tk.StringVar(value="all")
        for level in ["all", "info", "warning", "error", "success"]:
            tb.Radiobutton(
                toolbar,
                text=level.upper(),
                variable=self.level_var,
                value=level,
                command=self._filter_logs
            ).pack(side=tk.RIGHT, padx=2)
        
        # 日志文本区域
        self.log_text = tk.Text(
            self,
            height=10,
            state=tk.DISABLED,
            font=FONTS["mono"],
            bg=BACKGROUND_COLORS["log"],
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置标签样式
        for level, color in LOG_COLORS.items():
            self.log_text.tag_configure(
                f"log_{level}",
                foreground=color,
                font=("Consolas", 10, "bold")
            )
        self.log_text.tag_configure("timestamp", foreground="#64748B")
        self.log_text.tag_configure("message", foreground="white")
    
    def append(self, message: str, level: str = "info"):
        """追加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.log_text.config(state=tk.NORMAL)
        
        # 时间戳
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # 级别标签
        level_upper = level.upper()
        self.log_text.insert(tk.END, f"{level_upper:8} ", f"log_{level}")
        
        # 消息内容
        self.log_text.insert(tk.END, f"{message}\n", "message")
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _filter_logs(self):
        """按级别过滤日志"""
        # TODO: 实现日志过滤逻辑
        pass

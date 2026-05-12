"""状态卡片组件 - Win11毛玻璃风格"""

import tkinter as tk
import ttkbootstrap as tb
from typing import Optional
from gui.theme import BRAND_COLORS, FONTS, TEXT_COLORS, BACKGROUND_COLORS, BORDER_COLORS, BORDER_RADIUS


class StatusCard(tb.Frame):
    """毛玻璃状态卡片组件"""
    
    def __init__(
        self,
        master,
        title: str,
        value: str = "0",
        icon: Optional[str] = None,
        color: str = BRAND_COLORS["primary"],
        **kwargs
    ):
        super().__init__(master, bootstyle="dark", **kwargs)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置界面"""
        # 设置卡片样式
        self.configure(
            bootstyle="dark",
            padding=15,
        )
        
        # 左侧颜色条
        self.color_bar = tk.Frame(self, width=4, bg=self.color)
        self.color_bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        
        # 内容区域
        content = tb.Frame(self, bootstyle="dark")
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 标题
        tb.Label(
            content,
            text=self.title,
            font=FONTS["small"],
            foreground=TEXT_COLORS["secondary"],
            bootstyle="inverse-dark"
        ).pack(anchor=tk.W)
        
        # 数值
        self.value_label = tb.Label(
            content,
            text=self.value,
            font=("Segoe UI", 24, "bold"),
            foreground=self.color,
            bootstyle="inverse-dark"
        )
        self.value_label.pack(anchor=tk.W, pady=(5, 0))
    
    def set_value(self, value: str):
        """更新数值"""
        self.value = value
        self.value_label.configure(text=value)
    
    def set_color(self, color: str):
        """更新颜色"""
        self.color = color
        self.color_bar.configure(bg=color)
        self.value_label.configure(foreground=color)

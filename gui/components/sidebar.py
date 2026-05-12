"""侧边栏导航组件，带图标、激活态、悬停效果"""

import tkinter as tk
import ttkbootstrap as tb
from typing import Callable, Dict
from gui.theme import FONTS


class Sidebar(tb.Frame):
    """侧边栏导航组件"""
    
    def __init__(self, master, on_page_change: Callable[[str], None], **kwargs):
        super().__init__(master, bootstyle="dark", width=220, **kwargs)
        self.on_page_change = on_page_change
        self.buttons: Dict[str, tb.Button] = {}
        self.current_page = "engine"
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置界面"""
        # Logo 区域
        logo_frame = tb.Frame(self, bootstyle="dark")
        logo_frame.pack(fill=tk.X, pady=20, padx=15)
        
        tb.Label(
            logo_frame, 
            text="LANGDENG\nB2B GLOBAL",
            font=FONTS["title"],
            bootstyle="inverse-dark"
        ).pack()
        
        # 导航按钮
        nav_frame = tb.Frame(self, bootstyle="dark")
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.nav_items = [
            {"id": "engine", "text": "获客引擎", "icon": "search"},
            {"id": "ai", "text": "AI 策略", "icon": "robot"},
            {"id": "sync", "text": "同步设置", "icon": "cloud-upload"},
        ]
        
        for item in self.nav_items:
            btn = self._create_nav_button(nav_frame, item)
            btn.pack(fill=tk.X, pady=3)
            self.buttons[item["id"]] = btn
        
        # 版本号
        version_label = tb.Label(
            self, 
            text="v1.1.0",
            font=FONTS["small"],
            bootstyle="inverse-dark"
        )
        version_label.pack(side=tk.BOTTOM, pady=10)
        
        # 设置初始激活状态
        self._set_active("engine")
    
    def _create_nav_button(self, parent, item: Dict) -> tb.Button:
        """创建导航按钮，带悬停效果"""
        btn = tb.Button(
            parent,
            text=f"  {item['text']}",
            bootstyle="dark",
            compound=tk.LEFT,
            command=lambda page=item["id"]: self._on_nav_click(page)
        )
        # 绑定悬停效果
        btn.bind("<Enter>", lambda e: self._on_hover(btn, True))
        btn.bind("<Leave>", lambda e: self._on_hover(btn, False))
        return btn
    
    def _on_nav_click(self, page_id: str):
        """导航点击事件"""
        self._set_active(page_id)
        self.on_page_change(page_id)
    
    def _set_active(self, page_id: str):
        """设置激活状态"""
        self.current_page = page_id
        for pid, btn in self.buttons.items():
            if pid == page_id:
                btn.configure(bootstyle="primary")
            else:
                btn.configure(bootstyle="dark")
    
    def _on_hover(self, btn: tb.Button, is_hover: bool):
        """悬停效果"""
        # 使用 try-except 避免 bootstyle 获取失败
        try:
            current_style = btn.cget("bootstyle")
        except Exception:
            return  # 如果获取失败，直接返回
        
        if current_style == "primary":
            return  # 激活状态不改变
        if is_hover:
            btn.configure(bootstyle="secondary")
        else:
            btn.configure(bootstyle="dark")

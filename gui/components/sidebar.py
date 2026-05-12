"""侧边栏导航组件 - Win11风格可折叠侧边栏"""

import tkinter as tk
import ttkbootstrap as tb
from typing import Callable, Dict
from gui.theme import FONTS, SIDEBAR_CONFIG, TEXT_COLORS, BACKGROUND_COLORS


class Sidebar(tb.Frame):
    """可折叠侧边栏导航组件"""
    
    def __init__(self, master, on_page_change: Callable[[str], None], **kwargs):
        super().__init__(master, width=SIDEBAR_CONFIG["expanded_width"], **kwargs)
        self.on_page_change = on_page_change
        self.buttons: Dict[str, tb.Button] = {}
        self.current_page = "engine"
        self.is_expanded = True
        self.expanded_width = SIDEBAR_CONFIG["expanded_width"]
        self.collapsed_width = SIDEBAR_CONFIG["collapsed_width"]
        
        # 设置侧边栏样式
        self.configure(bootstyle="dark")
        self.pack_propagate(False)  # 固定宽度
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置界面"""
        # 顶部区域 - 折叠按钮 + Logo
        header_frame = tb.Frame(self, bootstyle="dark")
        header_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # 折叠/展开按钮
        self.toggle_btn = tb.Button(
            header_frame,
            text="◀",
            width=3,
            bootstyle="dark",
            command=self._toggle_sidebar
        )
        self.toggle_btn.pack(side=tk.RIGHT)
        
        # Logo区域
        self.logo_frame = tb.Frame(self, bootstyle="dark")
        self.logo_frame.pack(fill=tk.X, pady=10, padx=15)
        
        self.logo_label = tb.Label(
            self.logo_frame,
            text="B2B Global",
            font=FONTS["title"],
            foreground=TEXT_COLORS["primary"],
            bootstyle="inverse-dark"
        )
        self.logo_label.pack(anchor=tk.W)
        
        self.subtitle_label = tb.Label(
            self.logo_frame,
            text="获客系统",
            font=FONTS["small"],
            foreground=TEXT_COLORS["secondary"],
            bootstyle="inverse-dark"
        )
        self.subtitle_label.pack(anchor=tk.W)
        
        # 分隔线
        separator = tb.Separator(self, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, padx=15, pady=5)
        
        # 导航按钮区域
        self.nav_frame = tb.Frame(self, bootstyle="dark")
        self.nav_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.nav_items = [
            {"id": "engine", "text": "获客引擎", "icon": "🔍"},
            {"id": "ai", "text": "AI 策略", "icon": "🤖"},
            {"id": "sync", "text": "同步设置", "icon": "☁️"},
        ]
        
        for item in self.nav_items:
            btn = self._create_nav_button(self.nav_frame, item)
            btn.pack(fill=tk.X, pady=3)
            self.buttons[item["id"]] = btn
        
        # 底部区域 - 版本号
        self.bottom_frame = tb.Frame(self, bootstyle="dark")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=15)
        
        self.version_label = tb.Label(
            self.bottom_frame,
            text="v2.0.0",
            font=FONTS["small"],
            foreground=TEXT_COLORS["muted"],
            bootstyle="inverse-dark"
        )
        self.version_label.pack(anchor=tk.W)
        
        # 设置初始激活状态
        self._set_active("engine")
    
    def _create_nav_button(self, parent, item: Dict) -> tb.Button:
        """创建导航按钮"""
        btn = tb.Button(
            parent,
            text=f"{item['icon']}  {item['text']}",
            bootstyle="dark",
            compound=tk.LEFT,
            command=lambda page=item["id"]: self._on_nav_click(page)
        )
        # 保存图标和文字用于折叠切换
        btn.icon_text = item["icon"]
        btn.full_text = f"{item['icon']}  {item['text']}"
        
        # 绑定悬停效果
        btn.bind("<Enter>", lambda e, b=btn: self._on_hover(b, True))
        btn.bind("<Leave>", lambda e, b=btn: self._on_hover(b, False))
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
        try:
            current_style = btn.cget("bootstyle")
        except Exception:
            return
        
        if current_style == "primary":
            return  # 激活状态不改变
        if is_hover:
            btn.configure(bootstyle="secondary")
        else:
            btn.configure(bootstyle="dark")
    
    def _toggle_sidebar(self):
        """切换侧边栏状态"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()
    
    def collapse(self):
        """折叠侧边栏"""
        self.is_expanded = False
        self.configure(width=self.collapsed_width)
        self.toggle_btn.configure(text="▶")
        
        # 隐藏Logo和副标题
        self.logo_frame.pack_forget()
        self.subtitle_label.pack_forget()
        
        # 隐藏版本号文字，只显示图标
        self.version_label.pack_forget()
        
        # 导航按钮只显示图标
        for btn in self.buttons.values():
            btn.configure(text=btn.icon_text)
    
    def expand(self):
        """展开侧边栏"""
        self.is_expanded = True
        self.configure(width=self.expanded_width)
        self.toggle_btn.configure(text="◀")
        
        # 显示Logo和副标题
        self.logo_frame.pack(fill=tk.X, pady=10, padx=15, before=self.nav_frame)
        
        # 显示版本号
        self.version_label.pack(anchor=tk.W)
        
        # 导航按钮显示图标+文字
        for btn in self.buttons.values():
            btn.configure(text=btn.full_text)

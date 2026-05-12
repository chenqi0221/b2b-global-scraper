# GUI 美化与代码重构计划

## 一、现状分析

### 1.1 代码结构问题

| 问题 | 具体表现 | 影响 |
|------|----------|------|
| **gui_scraper.py 过于臃肿** | 1,455 行，包含 GUI 类、工具提示、数据预览、关键词库弹窗等 | 维护困难，职责不单一 |
| **混合关注点** | GUI 渲染、业务逻辑、数据操作、文件 I/O 全部混在一起 | 代码耦合度高，测试困难 |
| **重复代码** | 关键词库的搜索、显示、选中逻辑散落在多个方法中 | 难以维护，容易出 bug |
| **魔法数字/字符串** | 颜色值、尺寸、超时时间等硬编码 | 难以统一修改 |
| **缺乏类型提示** | 大量函数没有参数和返回类型注解 | IDE 提示弱，容易传错参数 |

### 1.2 界面美观问题

| 问题 | 具体表现 | 改进方向 |
|------|----------|----------|
| **侧边栏简陋** | 纯文字按钮，无图标，无激活状态指示 | 添加图标、激活态、悬停效果 |
| **状态卡片单调** | 简单的 LabelFrame，无视觉层次 | 使用卡片式设计，添加图标和颜色区分 |
| **日志区域简陋** | 纯色背景，无语法高亮，无日志级别图标 | 添加彩色标签、时间戳格式化、级别图标 |
| **关键词标签云粗糙** | 简单的 Checkbutton 堆叠，无动画 | 使用标签云布局，添加悬停效果 |
| **整体配色单调** | 默认 ttkbootstrap 主题，无品牌色 | 自定义主题色，统一视觉风格 |
| **缺乏动画反馈** | 按钮点击、状态切换无过渡动画 | 添加微交互动画 |

---

## 二、重构目标

### 2.1 架构目标
- **单一职责**：每个模块只做一件事
- **依赖注入**：通过构造函数传入依赖，便于测试
- **事件驱动**：使用发布-订阅模式解耦组件
- **类型安全**：全面添加类型注解

### 2.2 界面目标
- **现代化设计**：卡片式布局、圆角、阴影
- **品牌一致性**：统一的配色、字体、间距
- **交互反馈**：悬停效果、加载动画、Toast 提示
- **响应式布局**：适配不同窗口大小

---

## 三、重构方案

### 3.1 目录结构重构

```
google-maps-scraper/
├── main.py                          # 新的入口文件（简化版）
├── gui/
│   ├── __init__.py
│   ├── app.py                       # 主应用类（精简版，仅负责窗口管理和页面路由）
│   ├── theme.py                     # 主题配置（颜色、字体、间距常量）
│   ├── components/                  # 可复用组件
│   │   ├── __init__.py
│   │   ├── sidebar.py               # 侧边栏导航（带图标、激活态）
│   │   ├── status_card.py           # 状态卡片（美化版）
│   │   ├── log_panel.py             # 日志面板（带语法高亮）
│   │   ├── tooltip.py               # 工具提示（提取为独立组件）
│   │   ├── keyword_tag.py           # 关键词标签（带动画效果）
│   │   ├── data_preview.py          # 数据预览窗口（提取为独立组件）
│   │   └── toast.py                 # Toast 通知封装
│   ├── pages/                       # 页面（精简职责）
│   │   ├── __init__.py
│   │   ├── base_page.py             # 页面基类（统一接口）
│   │   ├── engine_page.py           # 获客引擎（仅 UI 布局）
│   │   ├── ai_strategy_page.py      # AI 策略（仅 UI 布局）
│   │   └── sync_settings_page.py    # 同步设置（仅 UI 布局）
│   └── dialogs/                     # 弹窗对话框
│       ├── __init__.py
│       └── keyword_library_dialog.py # 关键词库弹窗（从 gui_scraper 提取）
├── core/                            # 核心业务逻辑（从 gui_scraper 提取）
│   ├── __init__.py
│   ├── scraper_controller.py        # 抓取控制器（协调抓取流程）
│   ├── keyword_service.py           # 关键词服务（AI 生成、库管理）
│   ├── sync_service.py              # 同步服务（Google Sheets）
│   └── config_service.py            # 配置服务（读写 .env）
├── scraper/                         # 抓取引擎（已有，保持不变）
│   ├── __init__.py
│   ├── google_maps.py               # google_maps_scraper.py 重命名
│   ├── email_extractor.py
│   └── file_export.py
├── services/                        # 第三方服务（已有，保持不变）
│   ├── __init__.py
│   ├── google_sheets.py
│   ├── sheet_aggregator.py
│   └── ai_generator.py
├── models/                          # 数据模型（新增）
│   ├── __init__.py
│   ├── keyword.py                   # 关键词数据类
│   ├── business.py                  # 商家数据类
│   └── config.py                    # 配置数据类
├── utils/                           # 工具函数（已有，保持不变）
│   ├── __init__.py
│   ├── async_utils.py
│   └── config_manager.py
├── tests/                           # 测试文件（已有，保持不变）
├── assets/                          # 资源文件（已有，保持不变）
├── data.py                          # 地理数据（已有，保持不变）
└── requirements.txt
```

### 3.2 代码重构步骤

#### 步骤 1：创建主题配置模块

**文件**：`gui/theme.py`

```python
"""主题配置模块，集中管理所有视觉常量"""

from typing import Dict, Tuple

# 品牌色
BRAND_COLORS = {
    "primary": "#2563EB",      # 主色调：蓝色
    "secondary": "#64748B",    # 次要色：灰蓝
    "success": "#10B981",      # 成功：绿色
    "warning": "#F59E0B",      # 警告：橙色
    "danger": "#EF4444",       # 危险：红色
    "info": "#3B82F6",         # 信息：亮蓝
}

# 背景色
BACKGROUND_COLORS = {
    "sidebar": "#1E293B",      # 侧边栏背景
    "main": "#F8FAFC",         # 主区域背景
    "card": "#FFFFFF",         # 卡片背景
    "log": "#0F172A",          # 日志背景
}

# 文字色
TEXT_COLORS = {
    "primary": "#1E293B",      # 主文字
    "secondary": "#64748B",    # 次要文字
    "inverse": "#FFFFFF",      # 反色文字
    "muted": "#94A3B8",        # 弱化文字
}

# 间距
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

# 字体
FONTS = {
    "title": ("Helvetica", 18, "bold"),
    "subtitle": ("Helvetica", 14, "bold"),
    "body": ("Helvetica", 11),
    "mono": ("Consolas", 10),
    "small": ("Helvetica", 9),
}

# 圆角
BORDER_RADIUS = 8

# 日志颜色映射
LOG_COLORS = {
    "success": "#10B981",
    "info": "#3B82F6",
    "warning": "#F59E0B",
    "error": "#EF4444",
}

# 图标尺寸
ICON_SIZES = {
    "small": (16, 16),
    "medium": (24, 24),
    "large": (32, 32),
}
```

#### 步骤 2：提取可复用组件

**A. 侧边栏组件 (`gui/components/sidebar.py`)**

```python
"""侧边栏导航组件，带图标、激活态、悬停效果"""

import tkinter as tk
import ttkbootstrap as tb
from typing import Callable, List, Dict
from gui.theme import BRAND_COLORS, BACKGROUND_COLORS, TEXT_COLORS, FONTS

class Sidebar(tb.Frame):
    """侧边栏导航组件"""
    
    def __init__(self, master, on_page_change: Callable[[str], None], **kwargs):
        super().__init__(master, bootstyle="dark", width=220, **kwargs)
        self.on_page_change = on_page_change
        self.buttons: Dict[str, tb.Button] = {}
        self.current_page = "engine"
        
        self._setup_ui()
    
    def _setup_ui(self):
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
        """创建导航按钮，带图标和悬停效果"""
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
        if btn.cget("bootstyle") == "primary":
            return  # 激活状态不改变
        if is_hover:
            btn.configure(bootstyle="secondary")
        else:
            btn.configure(bootstyle="dark")
```

**B. 状态卡片组件 (`gui/components/status_card.py`)**

```python
"""状态卡片组件，带图标、颜色、动画效果"""

import tkinter as tk
import ttkbootstrap as tb
from typing import Optional
from gui.theme import BRAND_COLORS, BACKGROUND_COLORS, TEXT_COLORS, FONTS, BORDER_RADIUS

class StatusCard(tb.Frame):
    """状态卡片组件"""
    
    def __init__(
        self, 
        master, 
        title: str, 
        value: str = "0",
        icon: Optional[str] = None,
        color: str = BRAND_COLORS["primary"],
        **kwargs
    ):
        super().__init__(master, bootstyle="light", **kwargs)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        
        self._setup_ui()
    
    def _setup_ui(self):
        # 左侧颜色条
        self.color_bar = tk.Frame(self, width=4, bg=self.color)
        self.color_bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 内容区域
        content = tb.Frame(self)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        
        # 标题
        tb.Label(
            content,
            text=self.title,
            font=FONTS["small"],
            bootstyle="secondary"
        ).pack(anchor=tk.W)
        
        # 数值
        self.value_label = tb.Label(
            content,
            text=self.value,
            font=("Helvetica", 24, "bold"),
            foreground=self.color
        )
        self.value_label.pack(anchor=tk.W, pady=(5, 0))
    
    def set_value(self, value: str):
        """更新数值，带动画效果"""
        self.value = value
        self.value_label.configure(text=value)
        # 可以添加数字滚动动画
    
    def set_color(self, color: str):
        """更新颜色"""
        self.color = color
        self.color_bar.configure(bg=color)
        self.value_label.configure(foreground=color)
```

**C. 日志面板组件 (`gui/components/log_panel.py`)**

```python
"""日志面板组件，带语法高亮、级别图标、时间戳格式化"""

import tkinter as tk
import ttkbootstrap as tb
from datetime import datetime
from typing import Optional
from gui.theme import LOG_COLORS, FONTS, BACKGROUND_COLORS

class LogPanel(tb.Frame):
    """日志面板组件"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
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
        # 实现日志过滤逻辑
        pass
```

#### 步骤 3：提取关键词库对话框

**文件**：`gui/dialogs/keyword_library_dialog.py`

将 `gui_scraper.py` 中 `open_keyword_library()` 方法（约 300 行）提取为独立对话框类：

```python
"""关键词库对话框"""

import tkinter as tk
import ttkbootstrap as tb
from typing import Callable, List, Tuple, Set
import keyword_manager
from gui.theme import FONTS, SPACING, BRAND_COLORS

class KeywordLibraryDialog(tb.Toplevel):
    """关键词库管理对话框"""
    
    def __init__(
        self, 
        parent, 
        on_load: Callable[[List[Tuple[str, str]]], None],
        **kwargs
    ):
        super().__init__(parent, title="关键词库", **kwargs)
        self.on_load = on_load
        self.geometry("600x600")
        
        self.all_keywords: List[Tuple[str, str]] = []
        self.filtered_keywords: List[Tuple[str, str]] = []
        self.selected_set: Set[str] = set()
        self.debounce_timer = None
        
        self._setup_ui()
        self._load_keywords()
    
    def _setup_ui(self):
        """设置界面"""
        # 搜索区域
        search_frame = tb.Frame(self)
        search_frame.pack(fill=tk.X, pady=SPACING["md"], padx=SPACING["md"])
        
        tb.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        tb.Entry(search_frame, textvariable=self.search_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=SPACING["sm"]
        )
        
        # 列表区域
        list_frame = tb.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING["md"])
        
        self.canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = tb.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tb.Frame(self.canvas)
        
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        ))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 控制按钮
        control_frame = tb.Frame(self)
        control_frame.pack(fill=tk.X, pady=SPACING["md"], padx=SPACING["md"])
        
        tb.Label(control_frame, textvariable=self._result_count_var()).pack(side=tk.LEFT)
        
        tb.Button(control_frame, text="全选", command=self._select_all).pack(side=tk.RIGHT, padx=SPACING["xs"])
        tb.Button(control_frame, text="反选", command=self._invert_selection).pack(side=tk.RIGHT, padx=SPACING["xs"])
        tb.Button(control_frame, text="删除选中", bootstyle="danger", command=self._delete_selected).pack(side=tk.RIGHT, padx=SPACING["xs"])
        
        # 底部按钮
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=tk.X, pady=SPACING["md"], padx=SPACING["md"])
        
        tb.Button(btn_frame, text="导入", command=self._import).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=SPACING["xs"])
        tb.Button(btn_frame, text="导出", command=self._export).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=SPACING["xs"])
        tb.Button(btn_frame, text="加载选中", bootstyle="primary", command=self._load_selected).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=SPACING["xs"])
    
    def _load_keywords(self):
        """加载关键词"""
        self.all_keywords = keyword_manager.load_keywords()
        self.filtered_keywords = self.all_keywords.copy()
        self._display_keywords()
    
    def _display_keywords(self):
        """显示关键词列表"""
        # 清空现有内容
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # 显示过滤后的关键词
        for eng, chn in self.filtered_keywords:
            self._create_keyword_item(eng, chn)
    
    def _create_keyword_item(self, eng: str, chn: str):
        """创建关键词项"""
        frame = tb.Frame(self.scroll_frame)
        frame.pack(fill=tk.X, pady=2)
        
        is_selected = eng.lower() in self.selected_set
        var = tk.BooleanVar(value=is_selected)
        
        cb = tb.Checkbutton(frame, text=eng, variable=var)
        cb.pack(side=tk.LEFT)
        cb.var = var
        
        if chn:
            tb.Label(frame, text=f"({chn})", bootstyle="secondary").pack(side=tk.LEFT, padx=5)
    
    def _on_search_change(self, *args):
        """搜索变化事件（带防抖）"""
        if self.debounce_timer:
            self.after_cancel(self.debounce_timer)
        self.debounce_timer = self.after(300, self._do_search)
    
    def _do_search(self):
        """执行搜索"""
        term = self.search_var.get().lower()
        if not term:
            self.filtered_keywords = self.all_keywords.copy()
        else:
            self.filtered_keywords = [
                kw for kw in self.all_keywords 
                if term in kw[0].lower() or (kw[1] and term in kw[1].lower())
            ]
        self._display_keywords()
    
    # ... 其他方法（全选、反选、删除、导入、导出、加载）...
```

#### 步骤 4：精简主应用类

**文件**：`gui/app.py`

```python
"""主应用类，负责窗口管理和页面路由"""

import tkinter as tk
import ttkbootstrap as tb
from typing import Dict

from gui.components.sidebar import Sidebar
from gui.components.status_card import StatusCard
from gui.components.log_panel import LogPanel
from gui.pages.engine_page import EnginePage
from gui.pages.ai_strategy_page import AIStrategyPage
from gui.pages.sync_settings_page import SyncSettingsPage
from gui.theme import BRAND_COLORS, BACKGROUND_COLORS, SPACING

from core.scraper_controller import ScraperController
from core.keyword_service import KeywordService
from core.sync_service import SyncService

class ScraperApp:
    """主应用类"""
    
    def __init__(self, root: tb.Window):
        self.root = root
        self.root.title("LANGDENG B2B GLOBAL - 获客引擎")
        self.root.geometry("1200x800")
        
        # 初始化服务
        self.scraper_controller = ScraperController()
        self.keyword_service = KeywordService()
        self.sync_service = SyncService()
        
        # 状态
        self.total_found = 0
        self.email_found = 0
        self.synced_count = 0
        
        self._setup_ui()
        self._bind_events()
    
    def _setup_ui(self):
        """设置界面"""
        # 侧边栏
        self.sidebar = Sidebar(self.root, on_page_change=self._on_page_change)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # 主内容区
        self.main_frame = tb.Frame(self.root)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=SPACING["md"], pady=SPACING["md"])
        
        # 状态卡片
        self._setup_status_cards()
        
        # 页面容器
        self.page_container = tb.Frame(self.main_frame)
        self.page_container.pack(fill=tk.BOTH, expand=True)
        
        # 页面
        self.pages: Dict[str, tb.Frame] = {
            "engine": EnginePage(self.page_container, self),
            "ai": AIStrategyPage(self.page_container, self),
            "sync": SyncSettingsPage(self.page_container, self),
        }
        
        for page in self.pages.values():
            page.pack(fill=tk.BOTH, expand=True)
        
        self._show_page("engine")
    
    def _setup_status_cards(self):
        """设置状态卡片"""
        cards_frame = tb.Frame(self.main_frame)
        cards_frame.pack(fill=tk.X, pady=(0, SPACING["md"]))
        
        self.total_card = StatusCard(
            cards_frame, 
            "今日已抓取", 
            "0",
            color=BRAND_COLORS["primary"]
        )
        self.total_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=SPACING["xs"])
        
        self.email_card = StatusCard(
            cards_frame, 
            "包含邮箱数", 
            "0",
            color=BRAND_COLORS["success"]
        )
        self.email_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=SPACING["xs"])
        
        self.sync_card = StatusCard(
            cards_frame, 
            "已同步云端数", 
            "0",
            color=BRAND_COLORS["info"]
        )
        self.sync_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=SPACING["xs"])
    
    def _on_page_change(self, page_id: str):
        """页面切换事件"""
        self._show_page(page_id)
    
    def _show_page(self, page_id: str):
        """显示指定页面"""
        for pid, page in self.pages.items():
            if pid == page_id:
                page.pack(fill=tk.BOTH, expand=True)
            else:
                page.pack_forget()
    
    def _bind_events(self):
        """绑定事件"""
        # 绑定服务事件到 UI 更新
        self.scraper_controller.on_status_update = self._update_status
        self.scraper_controller.on_progress_update = self._update_progress
    
    def _update_status(self, message: str, level: str = "info"):
        """更新状态"""
        # 更新状态栏和日志
        pass
    
    def _update_progress(self, total: int, email: int, synced: int):
        """更新进度"""
        self.total_found = total
        self.email_found = email
        self.synced_count = synced
        
        self.total_card.set_value(str(total))
        self.email_card.set_value(str(email))
        self.sync_card.set_value(str(synced))
    
    def run(self):
        """运行应用"""
        self.root.mainloop()
```

#### 步骤 5：创建核心业务服务

**文件**：`core/scraper_controller.py`

```python
"""抓取控制器，协调抓取流程"""

import asyncio
import threading
from typing import Callable, List, Optional
from playwright.async_api import async_playwright

from scraper.google_maps import scrape_google_maps
from services.sheet_aggregator import aggregate_and_sync
from config import HTTP_PROXY

class ScraperController:
    """抓取控制器"""
    
    def __init__(self):
        self.is_running = False
        self.stop_event = asyncio.Event()
        self.on_status_update: Optional[Callable[[str, str], None]] = None
        self.on_progress_update: Optional[Callable[[int, int, int], None]] = None
        
        self.total_found = 0
        self.email_found = 0
        self.synced_count = 0
    
    def start_scraping(
        self, 
        keywords: List[str], 
        location: dict,
        concurrency: int = 3
    ):
        """开始抓取"""
        if self.is_running:
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        thread = threading.Thread(
            target=self._run_scraping,
            args=(keywords, location, concurrency),
            daemon=True
        )
        thread.start()
    
    def stop_scraping(self):
        """停止抓取"""
        self.is_running = False
        self.stop_event.set()
    
    def _run_scraping(self, keywords: List[str], location: dict, concurrency: int):
        """运行抓取（在线程中）"""
        asyncio.run(self._scraping_worker(keywords, location, concurrency))
    
    async def _scraping_worker(self, keywords: List[str], location: dict, concurrency: int):
        """抓取工作协程"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,
                    proxy={"server": HTTP_PROXY} if HTTP_PROXY else None
                )
                
                # 创建信号量控制并发
                semaphore = asyncio.Semaphore(concurrency)
                
                async def worker(kw: str, index: int):
                    async with semaphore:
                        if not self.is_running:
                            return
                        
                        task_info = {
                            "keyword": kw,
                            "country": location.get("country", ""),
                            "city": location.get("city", ""),
                            "district": location.get("district", "")
                        }
                        
                        found, email = await scrape_google_maps(
                            browser, task_info, "Downloads", 
                            self._status_callback, self.stop_event
                        )
                        
                        self.total_found += found
                        self.email_found += email
                        
                        if self.on_progress_update:
                            self.on_progress_update(
                                self.total_found, 
                                self.email_found, 
                                self.synced_count
                            )
                
                # 创建任务
                tasks = [worker(kw, i) for i, kw in enumerate(keywords)]
                await asyncio.gather(*tasks)
                
                await browser.close()
                
        except Exception as e:
            self._status_callback(f"抓取错误: {str(e)}", "error")
        finally:
            self.is_running = False
    
    def _status_callback(self, message: str, level: str = "info"):
        """状态回调"""
        if self.on_status_update:
            self.on_status_update(message, level)
```

### 3.3 界面美化步骤

#### 步骤 6：应用自定义主题

```python
# gui/theme.py 补充

import ttkbootstrap as tb

def apply_custom_theme(style: tb.Style):
    """应用自定义主题配置"""
    
    # 配置 TFrame 样式
    style.configure(
        "Card.TFrame",
        background=BACKGROUND_COLORS["card"],
        relief="flat"
    )
    
    # 配置 TButton 样式
    style.configure(
        "Action.TButton",
        font=FONTS["body"],
        padding=(16, 8)
    )
    
    # 配置 TEntry 样式
    style.configure(
        "Custom.TEntry",
        padding=8,
        relief="flat"
    )
    
    # 配置 TCombobox 样式
    style.configure(
        "Custom.TCombobox",
        padding=8
    )
```

#### 步骤 7：添加动画效果

```python
# gui/animations.py

import tkinter as tk
from typing import Callable

def fade_in(widget: tk.Widget, duration: int = 300, on_complete: Callable = None):
    """淡入动画"""
    steps = 20
    interval = duration // steps
    alpha = 0.0
    
    def step():
        nonlocal alpha
        alpha += 1.0 / steps
        if alpha >= 1.0:
            alpha = 1.0
            if on_complete:
                on_complete()
        else:
            widget.after(interval, step)
    
    step()

def slide_in(widget: tk.Widget, direction: str = "left", duration: int = 300):
    """滑入动画"""
    # 实现滑动动画
    pass

def pulse(widget: tk.Widget, times: int = 3, duration: int = 1000):
    """脉冲动画（用于提示）"""
    # 实现脉冲动画
    pass
```

---

## 四、实施计划

### 阶段 1：基础设施（第 1-2 天）

| 任务 | 文件 | 说明 |
|------|------|------|
| 创建主题配置 | `gui/theme.py` | 提取所有视觉常量 |
| 创建工具提示组件 | `gui/components/tooltip.py` | 从 gui_scraper 提取 |
| 创建 Toast 封装 | `gui/components/toast.py` | 统一 Toast 样式 |

### 阶段 2：组件提取（第 3-5 天）

| 任务 | 文件 | 说明 |
|------|------|------|
| 创建侧边栏组件 | `gui/components/sidebar.py` | 带图标、激活态、悬停效果 |
| 创建状态卡片 | `gui/components/status_card.py` | 美化版，带动画 |
| 创建日志面板 | `gui/components/log_panel.py` | 带语法高亮、级别过滤 |
| 创建关键词标签 | `gui/components/keyword_tag.py` | 带动画效果 |
| 提取数据预览 | `gui/components/data_preview.py` | 从 gui_scraper 提取 |

### 阶段 3：对话框提取（第 6-7 天）

| 任务 | 文件 | 说明 |
|------|------|------|
| 提取关键词库对话框 | `gui/dialogs/keyword_library_dialog.py` | 从 gui_scraper 提取并美化 |

### 阶段 4：页面重构（第 8-10 天）

| 任务 | 文件 | 说明 |
|------|------|------|
| 创建页面基类 | `gui/pages/base_page.py` | 统一页面接口 |
| 重构获客引擎页 | `gui/pages/engine_page.py` | 仅保留 UI 布局 |
| 重构 AI 策略页 | `gui/pages/ai_strategy_page.py` | 仅保留 UI 布局 |
| 重构同步设置页 | `gui/pages/sync_settings_page.py` | 仅保留 UI 布局 |

### 阶段 5：业务逻辑提取（第 11-13 天）

| 任务 | 文件 | 说明 |
|------|------|------|
| 创建抓取控制器 | `core/scraper_controller.py` | 从 gui_scraper 提取 |
| 创建关键词服务 | `core/keyword_service.py` | 从 gui_scraper 提取 |
| 创建同步服务 | `core/sync_service.py` | 从 gui_scraper 提取 |
| 创建配置服务 | `core/config_service.py` | 从 gui_scraper 提取 |

### 阶段 6：主应用重构（第 14-15 天）

| 任务 | 文件 | 说明 |
|------|------|------|
| 创建新主应用 | `gui/app.py` | 精简版，仅负责窗口管理 |
| 创建新入口 | `main.py` | 简化入口文件 |
| 迁移旧代码 | `gui_scraper.py` | 保留备份，逐步替换 |

### 阶段 7：测试与优化（第 16-18 天）

| 任务 | 说明 |
|------|------|
| 功能测试 | 确保所有功能正常 |
| 界面测试 | 确保界面美观、交互流畅 |
| 性能测试 | 确保无内存泄漏、响应迅速 |
| 代码审查 | 检查类型注解、文档字符串 |

---

## 五、风险评估

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 功能回归 | 中 | 高 | 保留旧代码备份，逐步替换，每步测试 |
| 界面不兼容 | 低 | 中 | 使用 ttkbootstrap 主题，保持兼容性 |
| 性能下降 | 低 | 中 | 优化组件渲染，避免过度重绘 |
| 开发延期 | 中 | 低 | 分阶段实施，优先核心功能 |

---

## 六、验收标准

### 6.1 代码质量
- [ ] gui_scraper.py 行数从 1,455 行减少到 200 行以内
- [ ] 所有函数都有类型注解
- [ ] 所有模块都有文档字符串
- [ ] 无循环导入
- [ ] 测试覆盖率 > 80%

### 6.2 界面质量
- [ ] 侧边栏有图标和激活态指示
- [ ] 状态卡片有颜色区分和动画效果
- [ ] 日志面板有语法高亮和级别过滤
- [ ] 关键词标签有悬停效果
- [ ] 整体配色统一，有品牌感

### 6.3 功能完整性
- [ ] 所有原有功能正常工作
- [ ] 无功能回归
- [ ] 性能无下降

---

## 七、后续优化方向

1. **响应式布局**：适配不同分辨率和窗口大小
2. **深色/浅色主题切换**：支持主题切换
3. **键盘快捷键**：支持快捷键操作
4. **数据可视化**：添加图表展示抓取统计
5. **国际化**：支持多语言切换

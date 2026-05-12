# Win11 毛玻璃UI实现计划

> **目标:** 将现有UI改造为Windows 11风格的毛玻璃设计，添加可折叠侧边栏和自适应布局

**架构:** 使用ttkbootstrap的深色主题作为基础，通过自定义样式实现毛玻璃效果。侧边栏使用动画过渡实现折叠/展开。

**技术栈:** Python, ttkbootstrap, tkinter

---

## Task 1: 更新主题配置

**文件:**
- Modify: `gui/theme.py`

**步骤:**
- [ ] **Step 1: 更新颜色方案**

```python
# 在 gui/theme.py 中更新

# Win11 毛玻璃色彩
COLORS = {
    "bg_primary": "#0F172A",           # 主背景
    "bg_sidebar": "#0F172A",           # 侧边栏背景
    "bg_card": "#1E293B",              # 卡片背景
    "bg_card_hover": "#334155",        # 卡片悬停
    "border": "rgba(255,255,255,0.1)", # 边框
    "text_primary": "#F1F5F9",         # 主文字
    "text_secondary": "#94A3B8",       # 次文字
    "accent": "#3B82F6",               # 强调色
    "accent_hover": "#60A5FA",         # 强调悬停
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
}

# 字体更新为Segoe UI
FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "subtitle": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 11),
    "mono": ("Consolas", 10),
    "small": ("Segoe UI", 9),
}

# 圆角
BORDER_RADIUS = 12
```

- [ ] **Step 2: 添加毛玻璃样式配置**

```python
# 添加毛玻璃效果配置
GLASS_EFFECT = {
    "bg": "#1E293B",
    "alpha": 0.85,
    "border_color": "#334155",
    "border_width": 1,
    "shadow": "0 8px 32px rgba(0,0,0,0.3)",
}
```

---

## Task 2: 修改应用标题和主窗口

**文件:**
- Modify: `gui/app.py`

**步骤:**
- [ ] **Step 1: 修改窗口标题**

```python
# 在 ScraperApp.__init__ 中
self.root.title("B2B Global 获客系统")
```

- [ ] **Step 2: 设置窗口最小尺寸和响应式**

```python
# 在 __init__ 中添加
self.root.minsize(800, 600)
self.root.configure(bg=COLORS["bg_primary"])

# 绑定窗口大小变化事件
self.root.bind("<Configure>", self._on_window_resize)
```

- [ ] **Step 3: 添加窗口大小变化处理**

```python
def _on_window_resize(self, event=None):
    """窗口大小变化时调整布局"""
    width = self.root.winfo_width()
    
    # 小于900px时自动折叠侧边栏
    if width < 900 and self.sidebar.is_expanded:
        self.sidebar.collapse()
    elif width >= 1100 and not self.sidebar.is_expanded:
        self.sidebar.expand()
```

---

## Task 3: 重写侧边栏组件（可折叠）

**文件:**
- Modify: `gui/components/sidebar.py`

**步骤:**
- [ ] **Step 1: 添加折叠状态管理**

```python
class Sidebar(tb.Frame):
    def __init__(self, master, on_page_change, **kwargs):
        super().__init__(master, width=220, **kwargs)
        self.on_page_change = on_page_change
        self.buttons = {}
        self.current_page = "engine"
        self.is_expanded = True
        self.expanded_width = 220
        self.collapsed_width = 60
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置界面"""
        # 折叠按钮
        self.toggle_btn = tb.Button(
            self, text="◀", width=3,
            command=self._toggle_sidebar
        )
        self.toggle_btn.pack(anchor=tk.NE, padx=5, pady=5)
        
        # Logo区域
        self.logo_frame = tb.Frame(self)
        self.logo_frame.pack(fill=tk.X, pady=10, padx=10)
        
        self.logo_label = tb.Label(
            self.logo_frame,
            text="B2B Global",
            font=FONTS["title"],
            foreground=COLORS["text_primary"]
        )
        self.logo_label.pack()
        
        # 导航按钮
        self.nav_frame = tb.Frame(self)
        self.nav_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        self.nav_items = [
            {"id": "engine", "text": "获客引擎", "icon": "🔍"},
            {"id": "ai", "text": "AI 策略", "icon": "🤖"},
            {"id": "sync", "text": "同步设置", "icon": "☁️"},
        ]
        
        for item in self.nav_items:
            btn = self._create_nav_button(self.nav_frame, item)
            btn.pack(fill=tk.X, pady=2)
            self.buttons[item["id"]] = btn
        
        # 设置初始激活状态
        self._set_active("engine")
```

- [ ] **Step 2: 添加折叠/展开方法**

```python
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
        
        # 隐藏文字，只显示图标
        for btn in self.buttons.values():
            btn.configure(text=btn.icon_text)
        
        self.logo_label.pack_forget()
    
    def expand(self):
        """展开侧边栏"""
        self.is_expanded = True
        self.configure(width=self.expanded_width)
        self.toggle_btn.configure(text="◀")
        
        # 显示图标+文字
        for item in self.nav_items:
            btn = self.buttons[item["id"]]
            btn.configure(text=f"{item['icon']}  {item['text']}")
        
        self.logo_label.pack()
```

- [ ] **Step 3: 更新按钮创建方法**

```python
    def _create_nav_button(self, parent, item):
        """创建导航按钮"""
        btn = tb.Button(
            parent,
            text=f"{item['icon']}  {item['text']}",
            bootstyle="dark",
            compound=tk.LEFT,
            command=lambda page=item["id"]: self._on_nav_click(page)
        )
        btn.icon_text = item["icon"]  # 保存图标用于折叠时显示
        
        # 绑定悬停效果
        btn.bind("<Enter>", lambda e: self._on_hover(btn, True))
        btn.bind("<Leave>", lambda e: self._on_hover(btn, False))
        return btn
```

---

## Task 4: 更新状态卡片样式

**文件:**
- Modify: `gui/components/status_card.py`

**步骤:**
- [ ] **Step 1: 应用毛玻璃样式**

```python
class StatusCard(tb.Frame):
    """毛玻璃状态卡片"""
    
    def __init__(self, parent, title, value, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 设置毛玻璃样式
        self.configure(
            bootstyle="dark",
            padding=15,
            relief="solid",
            borderwidth=1
        )
        
        # 标题
        self.title_label = tb.Label(
            self,
            text=title,
            font=FONTS["small"],
            foreground=COLORS["text_secondary"]
        )
        self.title_label.pack(anchor=tk.W)
        
        # 数值
        self.value_label = tb.Label(
            self,
            text=str(value),
            font=FONTS["title"],
            foreground=COLORS["text_primary"]
        )
        self.value_label.pack(anchor=tk.W, pady=(5, 0))
```

---

## Task 5: 更新引擎页面布局

**文件:**
- Modify: `gui/pages/engine_page.py`

**步骤:**
- [ ] **Step 1: 应用毛玻璃背景**

```python
class EnginePage(BasePage):
    def _setup_ui(self):
        """设置界面"""
        # 设置页面背景
        self.configure(bootstyle="dark")
        
        # 状态卡片区域
        cards_frame = tb.Frame(self, bootstyle="dark")
        cards_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # 创建毛玻璃卡片
        self.total_scraped_card = StatusCard(cards_frame, "今日已抓取", "0")
        self.total_scraped_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.email_found_card = StatusCard(cards_frame, "包含邮箱数", "0")
        self.email_found_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.synced_card = StatusCard(cards_frame, "已同步云端数", "0")
        self.synced_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
```

---

## Task 6: 语法检查和测试

**步骤:**
- [ ] **Step 1: 运行语法检查**

```bash
python -m py_compile gui/theme.py gui/app.py gui/components/sidebar.py gui/components/status_card.py gui/pages/engine_page.py
```

- [ ] **Step 2: 启动应用测试**

```bash
python main.py
```

- [ ] **Step 3: 验证功能**
- 侧边栏折叠/展开
- 窗口缩放自适应
- 毛玻璃视觉效果
- 标题显示正确

---

## 文件修改清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `gui/theme.py` | 修改 | 更新颜色、字体为Win11风格 |
| `gui/app.py` | 修改 | 修改标题，添加响应式布局 |
| `gui/components/sidebar.py` | 修改 | 添加折叠功能 |
| `gui/components/status_card.py` | 修改 | 应用毛玻璃样式 |
| `gui/pages/engine_page.py` | 修改 | 更新布局 |

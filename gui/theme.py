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

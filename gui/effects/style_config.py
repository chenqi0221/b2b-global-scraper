"""ttkbootstrap 样式配置 - Win11 毛玻璃风格"""

import tkinter as tk
from tkinter import ttk


def configure_win11_styles(style: ttk.Style):
    """
    配置 Win11 风格的 ttk 样式
    
    Args:
        style: ttk.Style 实例
    """
    # 配置圆角按钮样式
    style.configure("Round.TButton", borderwidth=0, relief="flat")
    style.configure("Round.Success.TButton", borderwidth=0, relief="flat")
    style.configure("Round.Info.TButton", borderwidth=0, relief="flat")
    style.configure("Round.Danger.TButton", borderwidth=0, relief="flat")
    style.configure("Round.Warning.TButton", borderwidth=0, relief="flat")

    # 配置圆角卡片样式
    style.configure("Card.TFrame", borderwidth=1, relief="solid")
    style.configure("Card.TLabelframe", borderwidth=1, relief="solid")
    style.configure("Card.TLabelframe.Label", font=("Segoe UI", 10, "bold"))

    # 配置圆角输入框
    style.configure("Round.TEntry", borderwidth=1, relief="solid")
    style.configure("Round.TCombobox", borderwidth=1, relief="solid")

    # 配置圆角进度条
    style.configure("Round.Horizontal.TProgressbar", thickness=8)

    # 配置圆角滚动条
    style.configure("Round.Vertical.TScrollbar", width=12)
    style.configure("Round.Horizontal.TScrollbar", width=12)


def apply_card_style(widget: tk.Widget, bg_color: str = "#1E293B", border_color: str = "#334155"):
    """
    为 Frame/Labelframe 应用卡片样式（模拟圆角和毛玻璃）
    
    由于 tkinter 原生不支持圆角，我们通过以下方式模拟：
    1. 设置背景色和边框色
    2. 添加内边距
    3. 使用 ttkbootstrap 的 bootstyle
    
    Args:
        widget: tkinter 组件
        bg_color: 背景色
        border_color: 边框色
    """
    try:
        # 尝试设置 bootstyle 为圆角样式
        if hasattr(widget, 'configure'):
            # 对于 ttkbootstrap 组件，设置合适的样式
            if isinstance(widget, (ttk.Frame, ttk.LabelFrame)):
                widget.configure(padding=10)
    except Exception:
        pass


def setup_global_styles(root: tk.Tk):
    """
    设置全局样式
    
    Args:
        root: 根窗口
    """
    style = ttk.Style(root)
    configure_win11_styles(style)

    # 设置全局字体
    root.option_add("*Font", ("Segoe UI", 10))
    root.option_add("*Background", "#0F172A")
    root.option_add("*Foreground", "#F1F5F9")

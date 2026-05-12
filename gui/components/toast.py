"""Toast 通知封装"""

import ttkbootstrap as tb
from ttkbootstrap.widgets import ToastNotification


def show_toast(title: str, message: str, duration: int = 3000, bootstyle: str = "info"):
    """显示 Toast 通知
    
    Args:
        title: 通知标题
        message: 通知内容
        duration: 显示时长（毫秒）
        bootstyle: 样式主题 (info, success, warning, danger)
    """
    ToastNotification(
        title=title,
        message=message,
        duration=duration,
        bootstyle=bootstyle
    ).show_toast()

"""页面基类"""

import ttkbootstrap as tb


class BasePage(tb.Frame):
    """页面基类，所有页面继承此类"""
    
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self._setup_ui()
    
    def _setup_ui(self):
        """设置界面，子类必须实现"""
        raise NotImplementedError("子类必须实现 _setup_ui 方法")
    
    def on_show(self):
        """页面显示时调用"""
        pass
    
    def on_hide(self):
        """页面隐藏时调用"""
        pass

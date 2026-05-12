"""工具提示组件"""

import tkinter as tk


class ToolTip:
    """简单的工具提示类，用于显示组件的工具提示"""
    
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        
        # 绑定事件
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<Motion>", self.motion)
    
    def enter(self, event=None):
        """鼠标进入组件时显示工具提示"""
        if hasattr(self.widget, 'tooltip') and self.widget.tooltip:
            self.schedule()
    
    def leave(self, event=None):
        """鼠标离开组件时隐藏工具提示"""
        self.unschedule()
        self.hide()
    
    def motion(self, event=None):
        """鼠标在组件上移动时更新工具提示位置"""
        if self.tip_window:
            self.x = event.x_root + 15
            self.y = event.y_root + 15
            self.tip_window.wm_geometry("+%d+%d" % (self.x, self.y))
    
    def schedule(self):
        """安排显示工具提示"""
        self.unschedule()
        self.id = self.widget.after(500, self.show)
    
    def unschedule(self):
        """取消显示工具提示"""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
    
    def show(self):
        """显示工具提示"""
        if self.tip_window or not hasattr(self.widget, 'tooltip') or not self.widget.tooltip:
            return
        
        self.x = self.widget.winfo_pointerx() + 15
        self.y = self.widget.winfo_pointery() + 15
        
        # 创建工具提示窗口
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry("+%d+%d" % (self.x, self.y))
        
        # 创建标签并添加文本
        label = tk.Label(self.tip_window, text=self.widget.tooltip, 
                        background="#ffffe0", foreground="black", 
                        relief="solid", borderwidth=1, 
                        padx=5, pady=2, font=("Arial", 10))
        label.pack(ipadx=1)
    
    def hide(self):
        """隐藏工具提示"""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def setup_tooltips(parent_widget):
    """为所有带有 tooltip 属性的子组件添加工具提示"""
    def _add_tooltips(widget):
        # 为当前组件添加工具提示
        if hasattr(widget, 'tooltip'):
            ToolTip(widget)
        
        # 递归处理子组件
        for child in widget.winfo_children():
            _add_tooltips(child)
    
    _add_tooltips(parent_widget)

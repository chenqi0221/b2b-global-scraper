"""关键词库对话框"""

import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from typing import Callable, List, Tuple, Set
import keyword_manager
from gui.theme import FONTS, SPACING


class KeywordLibraryDialog(tb.Toplevel):
    """关键词库管理对话框"""
    
    def __init__(
        self,
        parent,
        on_load: Callable[[List[Tuple[str, str]]], None],
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.title("关键词库")
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
        
        self.result_label = tb.Label(control_frame, text="共 0 个关键词")
        self.result_label.pack(side=tk.LEFT)
        
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
        
        # 更新统计
        self.result_label.config(text=f"共 {len(self.filtered_keywords)} 个关键词")
    
    def _create_keyword_item(self, eng: str, chn: str):
        """创建关键词项"""
        frame = tb.Frame(self.scroll_frame)
        frame.pack(fill=tk.X, pady=2)
        
        is_selected = eng.lower() in self.selected_set
        var = tk.BooleanVar(value=is_selected)
        
        # 绑定变量变化事件，同步到 selected_set
        def _on_toggle(*args, e=eng.lower(), v=var):
            if v.get():
                self.selected_set.add(e)
            else:
                self.selected_set.discard(e)
        
        var.trace_add("write", _on_toggle)
        
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
    
    def _select_all(self):
        """全选"""
        for kw in self.filtered_keywords:
            self.selected_set.add(kw[0].lower())
        self._display_keywords()
    
    def _invert_selection(self):
        """反选"""
        for kw in self.filtered_keywords:
            eng = kw[0].lower()
            if eng in self.selected_set:
                self.selected_set.discard(eng)
            else:
                self.selected_set.add(eng)
        self._display_keywords()
    
    def _delete_selected(self):
        """删除选中的关键词"""
        selected = [kw for kw in self.filtered_keywords if kw[0].lower() in self.selected_set]
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的关键词")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected)} 个关键词吗？"):
            success, msg = keyword_manager.delete_keywords(selected)
            if success:
                self.selected_set.clear()
                self._load_keywords()
            else:
                messagebox.showerror("失败", msg)
    
    def _import(self):
        """导入关键词"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")],
            title="导入关键词库"
        )
        if file_path:
            success, msg = keyword_manager.import_keywords(file_path)
            if success:
                self._load_keywords()
            else:
                messagebox.showerror("失败", msg)
    
    def _export(self):
        """导出关键词"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="导出关键词库"
        )
        if file_path:
            success, msg = keyword_manager.export_keywords(file_path)
            if success:
                messagebox.showinfo("成功", msg)
            else:
                messagebox.showerror("失败", msg)
    
    def _load_selected(self):
        """加载选中的关键词"""
        selected = [kw for kw in self.filtered_keywords if kw[0].lower() in self.selected_set]
        if not selected:
            messagebox.showinfo("提示", "请先选择要加载的关键词")
            return
        
        self.on_load(selected)
        self.destroy()

"""数据预览窗口组件"""

import os
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
import pandas as pd


class DataPreviewWindow(tb.Toplevel):
    """数据预览窗口类，用于显示最近的抓取结果"""
    
    def __init__(self, parent, data_dir=None, file_path=None):
        super().__init__(parent)
        self.title("数据预览")
        self.geometry("1000x600")
        self.resizable(True, True)
        
        self.data_dir = data_dir
        self.preview_file = file_path
        self.current_file = None
        self.current_df = None
        
        self._setup_ui()
        
        if self.preview_file and os.path.exists(self.preview_file):
            # 直接预览指定文件
            self._load_single_file(self.preview_file)
        elif self.data_dir:
            self._load_csv_files()
        else:
            self.info_label.config(text="未指定数据目录或文件")
    
    def _setup_ui(self):
        """设置界面"""
        # 顶部框架 - 文件选择
        top_frame = tb.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tb.Label(top_frame, text="选择文件:").pack(side=tk.LEFT, padx=5)
        self.file_var = tk.StringVar()
        self.file_combobox = tb.Combobox(top_frame, textvariable=self.file_var, state="readonly")
        self.file_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.file_combobox.bind("<<ComboboxSelected>>", self._on_file_select)
        
        # 数据表格框架
        table_frame = tb.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建数据表格
        self.table = tb.Treeview(table_frame, show="headings")
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加垂直滚动条
        vsb = tb.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.configure(yscrollcommand=vsb.set)
        
        # 添加水平滚动条
        hsb = tb.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.table.configure(xscrollcommand=hsb.set)
        
        # 底部信息框架
        bottom_frame = tb.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.info_label = tb.Label(bottom_frame, text="")
        self.info_label.pack(side=tk.LEFT)
    
    def _load_csv_files(self):
        """加载目录中的所有 CSV 文件（递归搜索子目录）"""
        csv_files = []
        for root, dirs, files in os.walk(self.data_dir):
            for f in files:
                if f.endswith(".csv"):
                    # 使用相对路径
                    rel_path = os.path.relpath(os.path.join(root, f), self.data_dir)
                    csv_files.append(rel_path)
        
        if not csv_files:
            self.info_label.config(text="当前目录下没有 CSV 文件")
            return
        
        self.file_combobox['values'] = csv_files
        if csv_files:
            self.file_combobox.current(0)
            self._on_file_select(None)
    
    def _load_single_file(self, file_path):
        """加载单个文件并显示"""
        self.current_file = file_path
        # 隐藏文件选择器
        self.file_combobox.master.pack_forget()
        
        try:
            self.current_df = pd.read_csv(file_path)
            self._display_dataframe()
            self.info_label.config(text=f"文件: {os.path.basename(file_path)} | 共 {len(self.current_df)} 行数据")
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {str(e)}")
            self.info_label.config(text=f"加载文件失败: {str(e)}")
    
    def _display_dataframe(self):
        """显示当前数据框"""
        if self.current_df is None:
            return
        
        # 清空表格
        self.table.delete(*self.table.get_children())
        
        # 设置列名
        columns = list(self.current_df.columns)
        self.table['columns'] = columns
        
        # 设置列标题
        for col in columns:
            self.table.heading(col, text=col, anchor=tk.W)
            width = min(150, max(100, len(col) * 10))
            self.table.column(col, width=width, anchor=tk.W)
        
        # 填充数据
        for i, row in self.current_df.iterrows():
            values = [str(row[col]) if pd.notna(row[col]) else "" for col in columns]
            self.table.insert("", "end", values=values)
    
    def _on_file_select(self, event):
        """当选择文件时，加载并显示数据"""
        filename = self.file_combobox.get()
        if not filename:
            return
        
        file_path = os.path.join(self.data_dir, filename)
        self.current_file = file_path
        
        try:
            # 读取 CSV 文件
            self.current_df = pd.read_csv(file_path)
            
            # 清空表格
            self.table.delete(*self.table.get_children())
            
            # 设置列名
            columns = list(self.current_df.columns)
            self.table['columns'] = columns
            
            # 设置列标题
            for col in columns:
                self.table.heading(col, text=col, anchor=tk.W)
                # 根据列名设置合适的宽度
                width = min(150, max(100, len(col) * 10))
                self.table.column(col, width=width, anchor=tk.W)
            
            # 填充数据
            for i, row in self.current_df.iterrows():
                values = [str(row[col]) if pd.notna(row[col]) else "" for col in columns]
                self.table.insert("", "end", values=values)
            
            # 更新信息
            self.info_label.config(text=f"共 {len(self.current_df)} 行数据")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {str(e)}")
            self.info_label.config(text=f"加载文件失败: {str(e)}")

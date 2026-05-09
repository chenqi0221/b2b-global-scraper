import asyncio
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ToastNotification
from PIL import Image, ImageTk
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from scraper_core import scrape_google_maps, upload_to_google_sheets, HTTP_PROXY, test_connection, aggregate_and_sync
from data import INDUSTRY_KEYWORDS, GEOGRAPHICAL_DATA
from async_utils import new_event_loop, run_coro_in_new_loop
import keyword_manager
import config_manager
from pages.engine_page import EnginePage
from pages.ai_strategy_page import AIStrategyPage
from pages.sync_settings_page import SyncSettingsPage

class ToolTip:
    """
    简单的工具提示类，用于显示组件的工具提示
    """
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


class DataPreviewWindow(tb.Toplevel):
    """
    数据预览窗口类，用于显示最近的抓取结果
    """
    def __init__(self, parent, data_dir):
        super().__init__(parent)
        self.title("数据预览")
        self.geometry("1000x600")
        self.resizable(True, True)
        
        self.data_dir = data_dir
        self.current_file = None
        self.current_df = None
        
        self._setup_ui()
        self._load_csv_files()
    
    def _setup_ui(self):
        # 顶部框架 - 文件选择
        top_frame = tb.Frame(self)
        top_frame.pack(fill=X, padx=10, pady=10)
        
        tb.Label(top_frame, text="选择文件:").pack(side=LEFT, padx=5)
        self.file_var = tk.StringVar()
        self.file_combobox = tb.Combobox(top_frame, textvariable=self.file_var, state="readonly")
        self.file_combobox.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.file_combobox.bind("<<ComboboxSelected>>", self._on_file_select)
        
        # 数据表格框架
        table_frame = tb.Frame(self)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 创建数据表格
        self.table = tb.Treeview(table_frame, show="headings")
        self.table.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 添加垂直滚动条
        vsb = tb.Scrollbar(table_frame, orient=VERTICAL, command=self.table.yview)
        vsb.pack(side=RIGHT, fill=Y)
        self.table.configure(yscrollcommand=vsb.set)
        
        # 添加水平滚动条
        hsb = tb.Scrollbar(table_frame, orient=HORIZONTAL, command=self.table.xview)
        hsb.pack(side=BOTTOM, fill=X)
        self.table.configure(xscrollcommand=hsb.set)
        
        # 底部信息框架
        bottom_frame = tb.Frame(self)
        bottom_frame.pack(fill=X, padx=10, pady=10)
        
        self.info_label = tb.Label(bottom_frame, text="")
        self.info_label.pack(side=LEFT)
        
    def _load_csv_files(self):
        """
        加载目录中的所有 CSV 文件
        """
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith(".csv")]
        if not csv_files:
            self.info_label.config(text="当前目录下没有 CSV 文件")
            return
        
        self.file_combobox['values'] = csv_files
        if csv_files:
            self.file_combobox.current(0)
            self._on_file_select(None)
    
    def _on_file_select(self, event):
        """
        当选择文件时，加载并显示数据
        """
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
                self.table.heading(col, text=col, anchor=W)
                # 根据列名设置合适的宽度
                width = min(150, max(100, len(col) * 10))
                self.table.column(col, width=width, anchor=W)
            
            # 填充数据
            for i, row in self.current_df.iterrows():
                values = [str(row[col]) if pd.notna(row[col]) else "" for col in columns]
                self.table.insert("", "end", values=values)
            
            # 更新信息
            self.info_label.config(text=f"共 {len(self.current_df)} 行数据")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {str(e)}")
            self.info_label.config(text=f"加载文件失败: {str(e)}")


class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LANGDENG B2B GLOBAL - 获客引擎")
        
        # 加载并恢复窗口配置
        self.app_config = config_manager.load_config()
        geometry = self.app_config.get("geometry", "1000x720")
        self.root.geometry(geometry)
        
        # 绑定窗口关闭事件以保存配置
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.is_running = False
        self.stop_event = asyncio.Event()
        self.total_found = 0
        self.email_found = 0
        self.synced_count = 0
        self.version = "v1.1.0"

        self.log_colors = {
            "success": "green",
            "info": "blue",
            "warning": "gray",
            "error": "red"
        }

        self._setup_ui()
        self._setup_tooltips()

    def _load_icon(self, path, size=(16, 16)):
        try:
            drawing = svg2rlg(path)
            if drawing:
                # Scale the drawing to the desired size
                drawing.width, drawing.height = size
                drawing.scale(size[0] / drawing.width, size[1] / drawing.height)
                
                # Render to a PNG in memory
                from io import BytesIO
                png_data = BytesIO()
                renderPM.drawToFile(drawing, png_data, fmt="PNG")
                png_data.seek(0)
                
                # Open with Pillow and convert to PhotoImage
                img = Image.open(png_data)
                return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading icon {path}: {e}")
        return None

    def _setup_ui(self):
        # --- 侧边栏 ---
        sidebar = tb.Frame(self.root, bootstyle="dark", width=200)
        sidebar.pack(side=LEFT, fill=Y)

        self.search_icon = self._load_icon("assets/search.svg")
        self.cloud_icon = self._load_icon("assets/cloud-upload.svg")

        tb.Label(sidebar, text="LANGDENG\nB2B GLOBAL", font=("Helvetica", 16, "bold"), bootstyle="inverse-dark").pack(pady=20)
        
        # 功能切换按钮
        btn_style = {"bootstyle": "dark"}
        tb.Button(sidebar, text="获客引擎", **btn_style, command=lambda: self.show_page("engine")).pack(fill=X, pady=5, padx=10)
        tb.Button(sidebar, text="AI 策略", **btn_style, command=lambda: self.show_page("ai")).pack(fill=X, pady=5, padx=10)
        tb.Button(sidebar, text="同步设置", **btn_style, command=lambda: self.show_page("sync")).pack(fill=X, pady=5, padx=10)

        tb.Label(sidebar, text=f"版本: {self.version}", bootstyle="inverse-dark").pack(side=BOTTOM, pady=10)

        # --- 主面板 ---
        main_panel = tb.Frame(self.root)
        main_panel.pack(side=LEFT, fill=BOTH, expand=True, padx=15, pady=15)

        # --- 底部状态栏 ---
        status_bar = tb.Frame(main_panel)
        status_bar.pack(side=BOTTOM, fill=X, padx=5, pady=2)
        self.status_label = tb.Label(status_bar, text="就绪")
        self.status_label.pack(side=LEFT)
        self.geo_status_label = tb.Label(status_bar, text="", bootstyle="info")
        self.geo_status_label.pack(side=LEFT, padx=10)
        
        other_btn_frame = tb.Frame(status_bar)
        other_btn_frame.pack(side=RIGHT)
        sync_btn = tb.Button(other_btn_frame, text="同步到云端", command=self.manual_sync, bootstyle="info-outline", width=12, image=self.cloud_icon, compound=LEFT)
        sync_btn.pack(side=LEFT, padx=5)
        sync_btn.tooltip = "手动选择 CSV 文件同步到 Google Sheets"
        
        agg_sync_btn = tb.Button(other_btn_frame, text="汇总同步", command=self.manual_aggregate_sync, bootstyle="primary-outline", width=10)
        agg_sync_btn.pack(side=LEFT, padx=5)
        agg_sync_btn.tooltip = "汇总指定文件夹下的所有 CSV 文件并同步到 Google Sheets"
        
        test_proxy_btn = tb.Button(other_btn_frame, text="测试代理", command=self.run_test_connection, bootstyle="warning-outline", width=10)
        test_proxy_btn.pack(side=LEFT, padx=5)
        test_proxy_btn.tooltip = "测试当前代理配置是否能连接到 Google"
        
        open_folder_btn = tb.Button(other_btn_frame, text="打开文件夹", command=self.open_data_folder, bootstyle="secondary-outline", width=10)
        open_folder_btn.pack(side=LEFT, padx=5)
        open_folder_btn.tooltip = "打开本地数据文件夹，查看总表和按日期保存的数据"

        # --- 页面容器 ---
        page_container = tb.Frame(main_panel)
        page_container.pack(fill=BOTH, expand=True)

        self.pages = {}
        for PageClass, name in [(EnginePage, "engine"), (AIStrategyPage, "ai"), (SyncSettingsPage, "sync")]:
            page = PageClass(page_container)
            self.pages[name] = page
            page.pack(fill=BOTH, expand=True)

        self.show_page("engine")

        # Connect signals
        self.pages["engine"].category_cb.bind("<<ComboboxSelected>>", self._on_category_select)
        self.pages["engine"].ai_gen_btn.config(command=self.generate_ai_keywords)
        self.pages["engine"].continent_cb.bind("<<ComboboxSelected>>", self._on_continent_select)
        self.pages["engine"].country_cb.bind("<<ComboboxSelected>>", self._on_country_select)
        self.pages["engine"].city_cb.bind("<<ComboboxSelected>>", self._on_city_select)
        self.pages["engine"].start_btn.config(command=self.start_task)
        self.pages["engine"].stop_btn.config(command=self.stop_task)
        self.pages["engine"].save_lib_btn.config(command=self.save_to_library)
        self.pages["engine"].open_lib_btn.config(command=self.open_keyword_library)
        self.pages["engine"].export_log_btn.config(command=self.export_logs)
        self.pages["engine"].data_preview_btn.config(command=self.show_data_preview)

        # Load initial data
        self.pages["engine"].category_cb['values'] = list(INDUSTRY_KEYWORDS.keys())
        self.pages["engine"].continent_cb['values'] = list(GEOGRAPHICAL_DATA.keys())

        self._load_prompt_template()
        self.pages["ai"].save_btn.config(command=self._save_prompt_template)
        self.pages["ai"].save_btn.tooltip = "保存 AI 提示词模板"

        self._load_sync_settings()
        self.pages["sync"].save_btn.config(command=self._save_sync_settings)
        self.pages["sync"].save_btn.tooltip = "保存所有 API 和代理设置"
        self.pages["sync"].test_api_btn.config(command=self.test_api_connection)
        self.pages["sync"].test_api_btn.tooltip = "测试豆包 API 连接是否正常"

        # 恢复上次选中的关键词
        last_keywords = self.app_config.get("last_keywords", [])
        if last_keywords:
            self._update_ui_with_keywords(last_keywords)
            
        # 在界面初始化完成后，调整左侧区域占 2/3 宽度
        self.root.after(100, self.pages["engine"].adjust_ratios)
    
    def _setup_tooltips(self):
        """
        为所有带有 tooltip 属性的 UI 组件初始化工具提示
        """
        def _add_tooltips(widget):
            # 为当前组件添加工具提示
            if hasattr(widget, 'tooltip'):
                ToolTip(widget)
            
            # 递归处理子组件
            for child in widget.winfo_children():
                _add_tooltips(child)
        
        # 为所有页面添加工具提示
        for page in self.pages.values():
            _add_tooltips(page)
        
        # 为主窗口添加工具提示
        _add_tooltips(self.root)

    def log_message(self, message, level="info"):
        def _append():
            log_text = self.pages["engine"].log_text
            log_text.config(state=NORMAL)
            
            tag = f"log_{level}"
            log_text.tag_config(tag, foreground=self.log_colors.get(level, "white"))
            
            log_text.insert(END, f"[{datetime.now().strftime('%H:%M:%S')}] ", "log_default")
            log_text.insert(END, f"{message}\n", tag)
            
            log_text.see(END)
            log_text.config(state=DISABLED)
        self.root.after(0, _append)

    def show_page(self, page_name):
        for name, page in self.pages.items():
            if name == page_name:
                page.pack(fill=BOTH, expand=True)
            else:
                page.pack_forget()

    def _on_category_select(self, event):
        cat = self.pages["engine"].category_cb.get()
        words = "\n".join(INDUSTRY_KEYWORDS[cat])
        self.pages["engine"].kw_text.delete("1.0", END)
        self.pages["engine"].kw_text.insert(END, words)

    def _update_ui_with_keywords(self, keywords_with_translation):
        self._clear_tag_cloud()
        if keywords_with_translation:
            self.keyword_vars = []
            for eng_kw, chn_trans in keywords_with_translation:
                var = tk.BooleanVar(value=True)
                # 记录英文、翻译和变量
                self.keyword_vars.append((eng_kw, chn_trans, var))
                
                frame = tb.Frame(self.pages["engine"].tag_cloud_frame)
                frame.pack(fill=X, anchor=W)
                
                cb = tb.Checkbutton(frame, text=eng_kw, variable=var)
                cb.pack(side=LEFT, anchor=W)
                
                if chn_trans:
                    trans_label = tb.Label(frame, text=f"({chn_trans})", bootstyle="secondary")
                    trans_label.pack(side=LEFT, anchor=W, padx=5)

            self.update_status(f"AI 成功生成 {len(keywords_with_translation)} 个关键词")
            ToastNotification("成功", f"已生成 {len(keywords_with_translation)} 个新关键词", duration=3000, bootstyle='success').show_toast()
        else:
            self.update_status("AI 未能生成关键词，请检查 API 配置或代理")
            ToastNotification("失败", "AI 未能生成关键词", duration=3000, bootstyle='danger').show_toast()

    def _clear_tag_cloud(self):
        for widget in self.pages["engine"].tag_cloud_frame.winfo_children():
            widget.destroy()

    def save_to_library(self):
        if not hasattr(self, 'keyword_vars') or not self.keyword_vars:
            ToastNotification("提示", "当前没有可保存的关键词", bootstyle="warning").show_toast()
            return
            
        to_save = [(eng, chn) for eng, chn, var in self.keyword_vars if var.get()]
        if not to_save:
            ToastNotification("提示", "请勾选要保存的关键词", bootstyle="warning").show_toast()
            return
            
        success, added = keyword_manager.save_keywords(to_save)
        if success:
            ToastNotification("成功", f"成功存入关键词库！新增 {added} 个，其余已自动去重。", bootstyle="success").show_toast()
        else:
            ToastNotification("错误", "关键词保存失败", bootstyle="danger").show_toast()

    def open_keyword_library(self):
        all_kw = keyword_manager.load_keywords()
        if not all_kw:
            ToastNotification("提示", "关键词库目前是空的", bootstyle="info").show_toast()
            return
            
        # 弹出窗口 - 增大尺寸以提供更好的用户体验
        top = tb.Toplevel(title="关键词库")
        top.geometry("600x600")
        
        container = tb.Frame(top)
        container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 搜索区域
        search_frame = tb.Frame(container)
        search_frame.pack(fill=X, pady=5)
        
        tb.Label(search_frame, text="搜索关键词:").pack(side=LEFT, padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = tb.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        # 关键词显示区域
        display_frame = tb.Frame(container)
        display_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # 列表区域
        canvas = tk.Canvas(display_frame)
        scrollbar = tb.Scrollbar(display_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tb.Frame(canvas)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 控制按钮区域
        control_frame = tb.Frame(container)
        control_frame.pack(fill=X, pady=5)
        
        # 结果统计标签
        result_label = tb.Label(control_frame, text=f"共 {len(all_kw)} 个关键词")
        result_label.pack(side=LEFT)
        
        # 全选按钮功能
        def _select_all():
            """全选当前显示的关键词"""
            for widget in scroll_frame.winfo_children():
                for child in widget.winfo_children():
                    if isinstance(child, tb.Checkbutton):
                        eng = child.cget("text")
                        eng_lower = eng.lower()
                        
                        # 添加到选中集合
                        selected_kw_set.add(eng_lower)
                        
                        # 更新Checkbutton的状态
                        try:
                            if hasattr(child, 'var'):
                                child.var.set(True)
                            else:
                                var_name = child.cget("variable")
                                if var_name:
                                    child.master.winfo_toplevel().globalsetvar(var_name, True)
                        except Exception as e:
                            try:
                                if not child.instate(['selected']):
                                    child.invoke()
                            except Exception:
                                pass
        
        # 反选按钮功能
        def _invert_selection():
            """反选当前显示的关键词"""
            # 只反选当前显示的关键词的选中状态
            for widget in scroll_frame.winfo_children():
                checkbutton = None
                eng = ""
                
                # 找到当前框架中的Checkbutton和关键词
                for child in widget.winfo_children():
                    if isinstance(child, tb.Checkbutton):
                        checkbutton = child
                        eng = child.cget("text")
                        break
                
                if checkbutton and eng:
                    eng_lower = eng.lower()
                    
                    # 检查关键词是否在选中集合中
                    is_selected = eng_lower in selected_kw_set
                    
                    # 反转状态
                    new_state = not is_selected
                    
                    # 更新Checkbutton状态
                    if hasattr(checkbutton, 'var'):
                        checkbutton.var.set(new_state)
                    
                    # 更新选中集合
                    if new_state:
                        selected_kw_set.add(eng_lower)
                    else:
                        selected_kw_set.discard(eng_lower)
        
        # 删除选中的关键词
        def _delete_selected():
            """删除选中的关键词"""
            # 获取选中的关键词
            selected = []
            for widget in scroll_frame.winfo_children():
                eng = ""
                chn = ""
                
                for child in widget.winfo_children():
                    if isinstance(child, tb.Checkbutton):
                        eng = child.cget("text")
                    elif isinstance(child, tb.Label):
                        chn_text = child.cget("text")
                        if chn_text.startswith("(") and chn_text.endswith(")"):
                            chn = chn_text[1:-1]  # 去掉括号
                
                if eng.lower() in selected_kw_set:
                    selected.append((eng, chn))
            
            if not selected:
                ToastNotification("提示", "请先选择要删除的关键词", duration=3000, bootstyle='info').show_toast()
                return
            
            # 确认删除
            from tkinter import messagebox
            if messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected)} 个关键词吗？"):
                # 调用删除函数
                success, message = keyword_manager.delete_keywords(selected)
                if success:
                    ToastNotification("成功", message, duration=3000, bootstyle='success').show_toast()
                    # 从选中集合中移除已删除的关键词
                    for eng, chn in selected:
                        selected_kw_set.discard(eng.lower())
                    # 重新加载并显示关键词
                    nonlocal original_kw, filtered_kw
                    original_kw = keyword_manager.load_keywords()
                    filtered_kw = original_kw.copy()
                    # 重新应用搜索过滤
                    _search_keywords()
                else:
                    ToastNotification("失败", message, duration=3000, bootstyle='danger').show_toast()
        
        tb.Button(control_frame, text="删除选中", command=_delete_selected, bootstyle="danger-outline").pack(side=RIGHT, padx=5)
        tb.Button(control_frame, text="全选", command=_select_all, bootstyle="outline").pack(side=RIGHT, padx=5)
        tb.Button(control_frame, text="反选", command=_invert_selection, bootstyle="outline").pack(side=RIGHT, padx=5)
        
        original_kw = all_kw.copy()
        filtered_kw = all_kw.copy()
        
        # 保存选中的关键词（使用英文词的小写作为唯一标识）
        selected_kw_set = set()
        
        # 显示所有关键词
        def _display_keywords(keywords):
            """显示关键词列表"""
            # 清空现有内容
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            
            # 显示过滤后的关键词
            for eng, chn in keywords:
                f = tb.Frame(scroll_frame)
                f.pack(fill=X, anchor=W)
                
                # 检查当前关键词是否被选中
                is_selected = eng.lower() in selected_kw_set
                var = tk.BooleanVar(value=is_selected)
                
                # 创建Checkbutton并保存var到对象属性
                def _on_checkbox_toggle(kw):
                    """当复选框状态改变时更新选中集合"""
                    kw_lower = kw.lower()
                    if var.get():
                        selected_kw_set.add(kw_lower)
                    else:
                        selected_kw_set.discard(kw_lower)
                
                cb = tb.Checkbutton(f, text=eng, variable=var, command=lambda kw=eng: _on_checkbox_toggle(kw))
                cb.var = var  # 保存变量到Checkbutton属性
                cb.pack(side=LEFT)
                if chn:
                    tb.Label(f, text=f"({chn})", bootstyle="secondary").pack(side=LEFT, padx=5)
            
            # 更新结果统计
            result_label.config(text=f"共 {len(keywords)} 个关键词")
        
        # 初始显示所有关键词
        _display_keywords(all_kw)
        
        # 防抖计时器ID
        debounce_timer = None
        
        # 搜索功能
        def _search_keywords():
            """根据搜索词过滤关键词"""
            search_term = search_var.get().lower()
            if not search_term:
                filtered = original_kw.copy()
            else:
                filtered = [kw for kw in original_kw if search_term in kw[0].lower() or (kw[1] and search_term in kw[1].lower())]
            filtered_kw[:] = filtered  # 更新过滤后的关键词列表
            _display_keywords(filtered)
        
        # 防抖搜索函数
        def _debounced_search(*args):
            """带防抖的搜索函数，避免频繁触发搜索"""
            nonlocal debounce_timer
            # 清除之前的计时器
            if debounce_timer:
                top.after_cancel(debounce_timer)
            # 300毫秒后执行搜索
            debounce_timer = top.after(300, _search_keywords)
        
        # 绑定搜索事件
        search_entry.bind("<Return>", lambda e: _search_keywords())
        # 使用防抖机制，减少搜索频率，解决卡顿问题
        search_entry.bind("<KeyRelease>", _debounced_search)
        
        def _load_selected():
            selected = []
            # 遍历当前显示的Checkbutton，获取选中的关键词
            for widget in scroll_frame.winfo_children():
                # 查找每个框架内的Checkbutton和Label
                eng = ""
                chn = ""
                is_checked = False
                
                for child in widget.winfo_children():
                    if isinstance(child, tb.Checkbutton):
                        # 获取Checkbutton的状态
                        try:
                            # 方法1：使用我们保存的var属性
                            if hasattr(child, 'var'):
                                is_checked = child.var.get()
                            else:
                                # 方法2：获取变量名称并使用winfo_getvar获取值
                                var_name = child.cget("variable")
                                is_checked = widget.winfo_getvar(var_name)
                        except Exception as e:
                            # 方法3：如果以上方法都失败，尝试获取选中状态
                            is_checked = child.instate(['selected'])
                        
                        # 获取Checkbutton的文本（英文关键词）
                        eng = child.cget("text")
                    elif isinstance(child, tb.Label):
                        # 获取Label的文本（中文翻译）
                        chn_text = child.cget("text")
                        if chn_text.startswith("(") and chn_text.endswith(")"):
                            chn = chn_text[1:-1]
                
                if is_checked:
                    selected.append((eng, chn))
            
            if not selected:
                top.destroy()
                return
            
            # 合并到主界面 (去重)
            current_engs = {item[0].lower() for item in self.keyword_vars} if hasattr(self, 'keyword_vars') else set()
            new_list = []
            
            # 先保留主界面已有的
            if hasattr(self, 'keyword_vars'):
                for e, c, v in self.keyword_vars:
                    new_list.append((e, c))
            
            # 再添加库里选中的 (去重)
            for e, c in selected:
                if e.lower() not in current_engs:
                    new_list.append((e, c))
                    
            self._update_ui_with_keywords(new_list)
            top.destroy()
            ToastNotification("成功", f"已从库中加载 {len(selected)} 个关键词", bootstyle="success").show_toast()

        def _export_keywords():
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="导出关键词库"
            )
            if file_path:
                success, msg = keyword_manager.export_keywords(file_path)
                if success:
                    ToastNotification("成功", msg, bootstyle="success").show_toast()
                else:
                    ToastNotification("失败", msg, bootstyle="danger").show_toast()

        def _import_keywords():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                filetypes=[("CSV Files", "*.csv")],
                title="导入关键词库"
            )
            if file_path:
                success, msg = keyword_manager.import_keywords(file_path)
                if success:
                    ToastNotification("成功", msg, bootstyle="success").show_toast()
                    # 重新加载关键词库
                    top.destroy()
                    self.open_keyword_library()
                else:
                    ToastNotification("失败", msg, bootstyle="danger").show_toast()

        # 底部按钮区域
        btn_frame = tb.Frame(container)
        btn_frame.pack(fill=X, pady=10)
        
        tb.Button(btn_frame, text="导入关键词", command=_import_keywords, bootstyle="info").pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        tb.Button(btn_frame, text="导出关键词", command=_export_keywords, bootstyle="info").pack(side=LEFT, fill=X, expand=True, padx=(5, 5))
        tb.Button(btn_frame, text="加载选中项", command=_load_selected, bootstyle="primary").pack(side=LEFT, fill=X, expand=True, padx=(5, 0))

    def generate_ai_keywords(self):
        seed_word = self.pages["engine"].seed_kw_entry.get().strip()
        if not seed_word or seed_word == "种子词...":
            ToastNotification("提示", "请输入有效的种子词", duration=3000, bootstyle='warning').show_toast()
            return
            
        num_to_gen = self.pages["engine"].ai_kw_num_cb.get()
        try:
            num = int(num_to_gen)
        except ValueError:
            ToastNotification("提示", "请输入有效的生成数量", duration=3000, bootstyle='warning').show_toast()
            return
        
        if num <= 0 or num > 50:
            ToastNotification("提示", "生成数量必须在 1-50 之间", duration=3000, bootstyle='warning').show_toast()
            return

        self.pages["engine"].ai_gen_btn.pack_forget()
        self.pages["engine"].ai_progress.pack(side=LEFT, padx=5)
        self.pages["engine"].ai_progress.start()
        self.update_status(f"正在通过 AI 生成关于 '{seed_word}' 的关键词...")
        
        threading.Thread(target=self._ai_worker, args=(seed_word, num), daemon=True).start()

    def _ai_worker(self, seed_word, num):
        try:
            from scraper_core import generate_keywords_with_ai
            keywords = run_coro_in_new_loop(generate_keywords_with_ai(seed_word, int(num)))
            
            def _update_ui():
                self._update_ui_with_keywords(keywords)
                self.pages["engine"].ai_progress.stop()
                self.pages["engine"].ai_progress.pack_forget()
                self.pages["engine"].ai_gen_btn.pack(side=LEFT, padx=5)

            self.root.after(0, _update_ui)
                
        except Exception as e:
            error_msg = str(e)
            self.update_status(f"AI 生成失败: {error_msg}", level="error")
            def _reset_ui():
                self.pages["engine"].ai_progress.stop()
                self.pages["engine"].ai_progress.pack_forget()
                self.pages["engine"].ai_gen_btn.pack(side=LEFT, padx=5)
            self.root.after(0, _reset_ui)
        finally:
            self.root.after(0, lambda: self.pages["engine"].ai_gen_btn.config(state=NORMAL))

    def _on_continent_select(self, event):
        continent_key = self.pages["engine"].continent_cb.get()
        countries = list(GEOGRAPHICAL_DATA[continent_key].keys())
        self.pages["engine"].country_cb['values'] = countries
        self.pages["engine"].country_cb.set('')
        self.pages["engine"].city_cb['values'] = []
        self.pages["engine"].city_cb.set('')
        self.pages["engine"].district_cb['values'] = []
        self.pages["engine"].district_cb.set('')

    def _on_country_select(self, event):
        continent_key = self.pages["engine"].continent_cb.get()
        country_key = self.pages["engine"].country_cb.get()
        if not country_key: return
        cities = list(GEOGRAPHICAL_DATA[continent_key][country_key]["cities"].keys())
        self.pages["engine"].city_cb['values'] = cities
        self.pages["engine"].city_cb.set('')
        self.pages["engine"].district_cb['values'] = []
        self.pages["engine"].district_cb.set('')

    def _on_city_select(self, event):
        continent_key = self.pages["engine"].continent_cb.get()
        country_key = self.pages["engine"].country_cb.get()
        city_key = self.pages["engine"].city_cb.get()
        if not city_key: return
        districts = GEOGRAPHICAL_DATA[continent_key][country_key]["cities"][city_key]
        # 显示格式：英文名称 (中文名称)
        district_display = [f"{dist['en']} ({dist['zh']})" for dist in districts]
        self.pages["engine"].district_cb['values'] = district_display
        self.pages["engine"].district_cb.set('')

    def update_status(self, msg, is_found_update=False, level="info"):
        self.root.after(0, lambda: self.status_label.config(text=msg))
        if not is_found_update:
            self.log_message(msg, level)
        
        if "已抓取" in msg:
            pass

    def _translate_address(self, address):
        """
        将中文地址转换为英文
        如果转换失败，返回原始地址
        """
        try:
            # 简单的地址转换实现
            print(f"[DEBUG] 尝试转换地址: {address}")
            
            # 检查是否已经是英文（简单判断：是否包含中文）
            if not any('\u4e00' <= char <= '\u9fff' for char in address):
                return address.strip()
            
            # 尝试使用火山方舟API将中文地址翻译成英文
            from ai_generator import ARK_API_KEY, ARK_BASE_URL, ARK_MODEL_ENDPOINT
            
            if ARK_API_KEY and ARK_MODEL_ENDPOINT:
                try:
                    # 使用火山方舟API进行翻译（与ai_generator.py中保持一致的实现）
                    import requests
                    import json
                    
                    url = f"{ARK_BASE_URL}/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {ARK_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": ARK_MODEL_ENDPOINT,
                        "messages": [
                            {"role": "system", "content": "你是一个专业的翻译助手，请将中文地址翻译成英文地址，仅返回英文翻译结果，不要添加任何其他内容。"},
                            {"role": "user", "content": address}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 100
                    }
                    
                    response = requests.post(url, headers=headers, json=data, timeout=10)
                    response.raise_for_status()
                    
                    result = response.json()
                    if result.get("choices") and len(result["choices"]) > 0:
                        translated_address = result["choices"][0]["message"]["content"].strip()
                        print(f"[DEBUG] 地址翻译结果: {translated_address}")
                        return translated_address
                    else:
                        print(f"[DEBUG] 火山方舟 API 返回结果格式异常")
                except Exception as api_error:
                    print(f"[DEBUG] 火山方舟 API 翻译出错: {str(api_error)}")
            else:
                print(f"[DEBUG] 火山方舟 API 未配置，使用简单翻译")
            
            # 简单的音译实现作为备选方案
            # 这里可以添加简单的音译逻辑，或者直接返回原始地址
            print(f"[DEBUG] 使用简单翻译方案")
            
            # 返回原始地址
            return address.strip()
        except Exception as e:
            print(f"[DEBUG] 地址转换异常: {str(e)}")
            return address.strip()

    def start_task(self):
        # 检查地理位置选择方式
        geo_mode = self.pages["engine"].geo_mode_var.get()
        
        if geo_mode == "select":
            # 预设位置选择
            if not self.pages["engine"].continent_cb.get() or not self.pages["engine"].country_cb.get() or not self.pages["engine"].city_cb.get():
                ToastNotification("输入错误", "请选择完整的大洲、国家和城市信息", bootstyle='warning').show_toast()
                return

            display_loc = self.pages["engine"].district_cb.get() or self.pages["engine"].city_cb.get()
            if display_loc and display_loc != "所有":
                self.geo_status_label.config(text=f"当前挖掘地区: {display_loc}")
        else:
            # 手动输入地址
            manual_address = self.pages["engine"].manual_address_entry.get().strip()
            if not manual_address:
                ToastNotification("输入错误", "请输入地址", bootstyle='warning').show_toast()
                return
            
            # 显示当前挖掘地区
            self.geo_status_label.config(text=f"当前挖掘地区: {manual_address}")
        
        # 检查关键词
        keywords = []
        if hasattr(self, 'keyword_vars'):
            keywords = [eng for eng, chn, var in self.keyword_vars if var.get()]

        if not keywords:
            # Fallback to text area if no keywords from checkboxes
            keywords_str = self.pages["engine"].kw_text.get("1.0", tk.END).strip()
            if keywords_str:
                keywords = [kw.strip() for kw in keywords_str.split('\n') if kw.strip()]

        if not keywords:
            ToastNotification("输入错误", "请生成或输入关键词", bootstyle='warning').show_toast()
            return

        self.is_running = True
        self.stop_event.clear()
        self.pages["engine"].start_btn.config(state=DISABLED)
        self.pages["engine"].stop_btn.config(state=NORMAL)
        self.total_found = 0
        self.email_found = 0
        self.synced_count = 0
        self._update_status_cards()
        
        threading.Thread(target=self._run_async_loop, daemon=True).start()

    def stop_task(self):
        self.is_running = False
        self.stop_event.set()
        self.pages["engine"].stop_btn.config(state=DISABLED)
        self.update_status("正在停止...")
        self.root.after(0, lambda: self.geo_status_label.config(text=""))

    def manual_sync(self):
        file_path = filedialog.askopenfilename(
            title="选择要同步的 CSV 文件",
            filetypes=[("CSV Files", "*.csv")],
            initialdir=os.path.join(os.getcwd(), "Downloads")
        )
        if not file_path:
            return

        def _do_sync():
            try:
                self.update_status("正在读取文件并同步...")
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    self.log_message(f"文件不存在: {file_path}", level="error")
                    ToastNotification("同步失败", "选择的文件不存在", bootstyle='danger').show_toast()
                    return
                
                # 检查文件大小
                if os.path.getsize(file_path) == 0:
                    self.log_message(f"文件为空: {file_path}", level="warning")
                    ToastNotification("同步失败", "选择的文件为空", bootstyle='warning').show_toast()
                    return
                
                df = pd.read_csv(file_path)
                if df.empty:
                    self.log_message("文件内容为空")
                    ToastNotification("同步失败", "文件内容为空", bootstyle='warning').show_toast()
                    return
                
                title = os.path.splitext(os.path.basename(file_path))[0]
                self.log_message(f"开始同步文件: {title}")
                
                success, _ = run_coro_in_new_loop(upload_to_google_sheets(df, title, self.update_status))
                
                if success:
                    self.log_message(f"手动同步任务成功: {title}")
                    ToastNotification("同步成功", f"文件 '{title}' 已成功同步到云端！", bootstyle='success').show_toast()
                else:
                    self.log_message(f"手动同步任务失败: {title}", level="error")
                    ToastNotification("同步失败", f"文件 '{title}' 同步失败", bootstyle='danger').show_toast()
            except pd.errors.EmptyDataError:
                self.log_message("CSV 文件格式错误: 内容为空或格式不正确", level="error")
                ToastNotification("同步失败", "CSV 文件格式错误", bootstyle='danger').show_toast()
            except pd.errors.ParserError:
                self.log_message("CSV 文件解析错误: 格式不正确", level="error")
                ToastNotification("同步失败", "CSV 文件解析错误", bootstyle='danger').show_toast()
            except Exception as e:
                error_msg = str(e)
                self.log_message(f"手动同步失败: {error_msg}", level="error")
                ToastNotification("同步失败", f"错误详情: {error_msg}", bootstyle='danger').show_toast()

        threading.Thread(target=_do_sync, daemon=True).start()

    def manual_aggregate_sync(self):
        dir_path = filedialog.askdirectory(
            title="选择要汇总同步的文件夹",
            initialdir=os.path.join(os.getcwd(), "Downloads")
        )
        if not dir_path:
            return

        def _do_agg_sync():
            try:
                self.update_status("正在汇总数据并同步...")
                
                # 检查目录是否存在
                if not os.path.exists(dir_path):
                    self.log_message(f"目录不存在: {dir_path}", level="error")
                    ToastNotification("汇总失败", "选择的目录不存在", bootstyle='danger').show_toast()
                    return
                
                # 检查目录是否为空
                if not os.listdir(dir_path):
                    self.log_message(f"目录为空: {dir_path}", level="warning")
                    ToastNotification("汇总失败", "选择的目录为空", bootstyle='warning').show_toast()
                    return
                
                success = run_coro_in_new_loop(
                    aggregate_and_sync(
                        dir_path, 
                        self.update_status, 
                        target_title="lengdangb2b",
                        by_date=self.pages["sync"].by_date_var.get(),
                        conflict_resolution=self.pages["sync"].conflict_resolution_var.get()
                    )
                )
                if success:
                    ToastNotification("成功", "数据汇总并已同步至云端 'lengdangb2b'！", bootstyle='primary').show_toast()
                else:
                    self.log_message("汇总同步过程中出现问题", level="error")
                    ToastNotification("汇总失败", "汇总同步过程中出现问题", bootstyle='danger').show_toast()
            except Exception as e:
                error_msg = str(e)
                self.log_message(f"汇总操作异常: {error_msg}", level="error")
                ToastNotification("错误", f"汇总同步失败: {error_msg}", bootstyle='danger').show_toast()

        threading.Thread(target=_do_agg_sync, daemon=True).start()

    def run_test_connection(self):
        def _do_test():
            self.update_status("正在测试代理连接...")
            try:
                success = run_coro_in_new_loop(test_connection(self.update_status))
                if success:
                    ToastNotification("测试成功", "代理配置正确，可顺利连接 Google", bootstyle='success').show_toast()
                else:
                    ToastNotification("测试失败", "无法连接 Google，请检查代理", bootstyle='danger').show_toast()
            except Exception as e:
                self.log_message(f"测试异常: {e}")
                ToastNotification("测试异常", "测试过程中发生错误", bootstyle='danger').show_toast()

        threading.Thread(target=_do_test, daemon=True).start()
    
    def open_data_folder(self):
        """打开本地数据文件夹"""
        import os
        import platform
        import subprocess
        
        try:
            # 打开项目根目录，这里包含总表文件和date_data目录
            project_dir = os.getcwd()
            
            if platform.system() == "Windows":
                # Windows系统
                subprocess.Popen(f"explorer {project_dir}", shell=True)
            elif platform.system() == "Darwin":
                # macOS系统
                subprocess.Popen(["open", project_dir])
            else:
                # Linux系统
                subprocess.Popen(["xdg-open", project_dir])
            
            self.update_status(f"已打开数据文件夹: {project_dir}")
        except Exception as e:
            self.log_message(f"打开文件夹失败: {str(e)}", level="error")
            ToastNotification("打开失败", f"无法打开文件夹: {str(e)}", bootstyle='danger').show_toast()

    def _run_async_loop(self):
        run_coro_in_new_loop(self.main_worker())

    async def main_worker(self):
        try:
            # 获取地理位置选择方式
            geo_mode = self.pages["engine"].geo_mode_var.get()
            
            country_en = ""
            city_en = ""
            district = ""
            
            if geo_mode == "select":
                # 预设位置选择
                continent_key = self.pages["engine"].continent_cb.get()
                country_key = self.pages["engine"].country_cb.get()
                city_key = self.pages["engine"].city_cb.get()
                district_full = self.pages["engine"].district_cb.get()
                
                import re
                country_en = GEOGRAPHICAL_DATA[continent_key][country_key]["en"]
                city_en_match = re.search(r'\((.*?)\)', city_key)
                city_en = city_en_match.group(1) if city_en_match else city_key
                
                # 提取区域的英文名称，去掉中文翻译
                if district_full:
                    district_match = re.search(r'^(.*?)\s*\(', district_full)
                    if district_match:
                        district = district_match.group(1)
                    else:
                        district = district_full
                else:
                    # 如果没有选择区域，直接使用城市名称
                    district = city_en
            else:
                # 手动输入地址
                manual_address = self.pages["engine"].manual_address_entry.get().strip()
                # 将中文地址转换为英文
                translated_address = self._translate_address(manual_address)
                self.log_message(f"使用手动输入地址: {manual_address} (翻译: {translated_address})")
                
                # 简单处理：将整个地址作为城市名使用
                city_en = translated_address
                country_en = ""
                district = ""

            session_folder_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            output_dir = os.path.join("Downloads", session_folder_name)
            os.makedirs(output_dir, exist_ok=True)
            self.log_message(f"本次任务文件将保存至: {output_dir}")

            browser = None
            try:
                async with async_playwright() as p:
                    launch_kwargs = {"headless": False}
                    if HTTP_PROXY:
                        launch_kwargs["proxy"] = {"server": HTTP_PROXY}
                        self.log_message(f"Playwright 已启用代理: {HTTP_PROXY}")
                        
                    browser = await p.chromium.launch(**launch_kwargs)
                    
                    keywords = []
                    if hasattr(self, 'keyword_vars'):
                        keywords = [eng for eng, chn, var in self.keyword_vars if var.get()]

                    if not keywords:
                        # Fallback to text area if no keywords from checkboxes
                        keywords_str = self.pages["engine"].kw_text.get("1.0", tk.END).strip()
                        if keywords_str:
                            keywords = [kw.strip() for kw in keywords_str.split('\n') if kw.strip()]
                    
                    if not keywords:
                        self.update_status("没有有效的关键词可抓取", level="warning")
                        self.root.after(0, self._reset_ui)
                        return
                        
                    total_keywords = len(keywords)
                    concurrency_limit = int(self.pages["engine"].concurrency_cb.get())
                    semaphore = asyncio.Semaphore(concurrency_limit)
                    self.log_message(f"并发模式已启动: 同时处理 {concurrency_limit} 个关键词")

                    async def worker(kw_info, index):
                        async with semaphore:
                            if not self.is_running:
                                return
                            
                            kw = kw_info['keyword']
                            self.update_status(f"[{kw}] 正在抓取 ({index+1}/{total_keywords})")
                            
                            try:
                                found_count, email_count = await scrape_google_maps(browser, kw_info, output_dir, self.update_status, self.stop_event)
                                if found_count > 0:
                                    self.total_found += found_count
                                    self.email_found += email_count
                                    self.root.after(0, self._update_status_cards)
                                    self.update_status(f"已抓取: {self.total_found}", is_found_update=True)
                            except Exception as e:
                                self.log_message(f"抓取关键词 '{kw}' 时出错: {str(e)}")

                    tasks = []
                    for i, kw in enumerate(keywords):
                        task_info = {'keyword': kw, 'country': country_en, 'city': city_en, 'district': district}
                        tasks.append(worker(task_info, i))
                    
                    await asyncio.gather(*tasks)
                    
                    await browser.close()
                    
                    if self.is_running:
                        try:
                            self.update_status("正在执行自动汇总与同步...")
                            synced_now = await aggregate_and_sync(
                                output_dir, 
                                self.update_status, 
                                target_title="lengdangb2b",
                                by_date=self.pages["sync"].by_date_var.get(),
                                conflict_resolution=self.pages["sync"].conflict_resolution_var.get()
                            )
                            self.synced_count += synced_now
                            self._update_status_cards()
                            self.update_status("自动汇总与同步已完成")
                        except Exception as ae:
                            self.log_message(f"自动汇总同步失败: {str(ae)}", level="error")

            except Exception as e:
                self.log_message(f"Playwright 执行错误: {str(e)}", level="error")
                if browser:
                    await browser.close()
        except Exception as e:
            self.log_message(f"主任务执行错误: {str(e)}", level="error")
        finally:
            self.root.after(0, self._reset_ui)

    def _reset_ui(self):
        self.pages["engine"].start_btn.config(state=NORMAL)
        self.pages["engine"].stop_btn.config(state=DISABLED)
        self.update_status("任务已结束")
        self.geo_status_label.config(text="")

    def export_logs(self):
        """
        导出运行日志到文件
        """
        from tkinter import filedialog
        import os
        
        # 获取日志内容
        log_content = self.pages["engine"].log_text.get("1.0", tk.END)
        if not log_content.strip():
            messagebox.showinfo("提示", "日志内容为空")
            return
        
        # 打开文件对话框选择保存位置
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="导出日志",
            initialfile=f"scraper_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(log_content)
                ToastNotification("成功", f"日志已成功导出到 {os.path.basename(file_path)}", bootstyle="success").show_toast()
            except Exception as e:
                ToastNotification("失败", f"日志导出失败: {str(e)}", bootstyle="danger").show_toast()

    def show_data_preview(self):
        """
        显示数据预览窗口
        """
        # 获取最近的抓取结果目录
        downloads_dir = "Downloads"
        if not os.path.exists(downloads_dir):
            messagebox.showinfo("提示", "暂无抓取数据")
            return
        
        # 获取所有下载目录，按修改时间排序
        dirs = [d for d in os.listdir(downloads_dir) if os.path.isdir(os.path.join(downloads_dir, d))]
        if not dirs:
            messagebox.showinfo("提示", "暂无抓取数据")
            return
        
        # 按修改时间排序，最新的在前面
        dirs.sort(key=lambda x: os.path.getmtime(os.path.join(downloads_dir, x)), reverse=True)
        latest_dir = os.path.join(downloads_dir, dirs[0])
        
        # 创建数据预览窗口
        DataPreviewWindow(self.root, latest_dir)

    def _update_status_cards(self):
        self.pages["engine"].total_scraped_card.config(text=str(self.total_found))
        self.pages["engine"].email_found_card.config(text=str(self.email_found))
        self.pages["engine"].synced_card.config(text=str(self.synced_count))

    def _load_prompt_template(self):
        from data import AI_KEYWORD_PROMPT
        self.pages["ai"].prompt_text.delete("1.0", END)
        self.pages["ai"].prompt_text.insert(END, AI_KEYWORD_PROMPT)

    def _save_prompt_template(self):
        new_prompt = self.pages["ai"].prompt_text.get("1.0", END).strip()
        try:
            with open("data.py", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            with open("data.py", "w", encoding="utf-8") as f:
                in_prompt_section = False
                for line in lines:
                    if line.strip().startswith("AI_KEYWORD_PROMPT"):
                        f.write(f'AI_KEYWORD_PROMPT = """{new_prompt}"""\n')
                        in_prompt_section = True
                    elif in_prompt_section and line.strip().endswith('"""'):
                        in_prompt_section = False
                        continue # Skip the closing triple quotes of the old prompt
                    elif not in_prompt_section:
                        f.write(line)
            
            ToastNotification("成功", "提示词模板已成功保存！", bootstyle='success').show_toast()
        except Exception as e:
            ToastNotification("失败", f"保存失败: {e}", bootstyle='danger').show_toast()

    def _load_sync_settings(self):
        from os import getenv
        self.pages["sync"].proxy_entry.insert(0, getenv("HTTP_PROXY", ""))
        self.pages["sync"].sheets_id_entry.insert(0, getenv("GOOGLE_SHEETS_ID", ""))
        self.pages["sync"].gemini_api_key_entry.insert(0, getenv("GEMINI_API_KEY", ""))
        self.pages["sync"].doubao_api_key_entry.insert(0, getenv("DOUBAO_API_KEY", ""))
        self.pages["sync"].doubao_base_url_entry.insert(0, getenv("DOUBAO_BASE_URL", ""))
        self.pages["sync"].doubao_model_endpoint_entry.insert(0, getenv("DOUBAO_MODEL_ENDPOINT", ""))
        
        # 加载同步设置
        self.pages["sync"].by_date_var.set(getenv("SYNC_BY_DATE", "False").lower() == "true")
        self.pages["sync"].conflict_resolution_var.set(getenv("SYNC_CONFLICT_RESOLUTION", "keep_latest"))

    def _save_sync_settings(self):
        new_settings = {
            "HTTP_PROXY": self.pages["sync"].proxy_entry.get().strip(),
            "GOOGLE_SHEETS_ID": self.pages["sync"].sheets_id_entry.get().strip(),
            "GEMINI_API_KEY": self.pages["sync"].gemini_api_key_entry.get().strip(),
            "DOUBAO_API_KEY": self.pages["sync"].doubao_api_key_entry.get().strip(),
            "DOUBAO_BASE_URL": self.pages["sync"].doubao_base_url_entry.get().strip(),
            "DOUBAO_MODEL_ENDPOINT": self.pages["sync"].doubao_model_endpoint_entry.get().strip(),
            "SYNC_BY_DATE": str(self.pages["sync"].by_date_var.get()),
            "SYNC_CONFLICT_RESOLUTION": self.pages["sync"].conflict_resolution_var.get(),
        }

        try:
            env_file = ".env"
            env_vars = {}
            if os.path.exists(env_file):
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()

            # Update with new settings from the GUI
            for key, value in new_settings.items():
                env_vars[key] = f'"{value}"'

            # Write everything back
            with open(env_file, "w", encoding="utf-8") as f:
                for key, value in env_vars.items():
                    f.write(f'{key}={value}\n')
            
            ToastNotification("成功", "设置已成功保存到 .env 文件！", bootstyle='success').show_toast()
        except Exception as e:
            ToastNotification("失败", f"保存到 .env 文件失败: {e}", bootstyle='danger').show_toast()
    
    def test_api_connection(self):
        """
        测试豆包 API 连接
        """
        try:
            import requests
            import json
            
            # 获取当前 API 设置
            api_key = self.pages["sync"].doubao_api_key_entry.get().strip()
            base_url = self.pages["sync"].doubao_base_url_entry.get().strip()
            model_endpoint = self.pages["sync"].doubao_model_endpoint_entry.get().strip()
            
            # 验证必填字段
            if not api_key or not base_url or not model_endpoint:
                ToastNotification("提示", "请先填写完整的 API 设置", duration=3000, bootstyle='warning').show_toast()
                return
            
            # 显示测试中状态
            self.update_status("正在测试 API 连接...")
            
            # 构建测试请求
            url = f"{base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model_endpoint,
                "messages": [
                    {"role": "system", "content": "你是一个简单的测试助手，只需要返回'测试成功'即可。"},
                    {"role": "user", "content": "请返回'测试成功'"}
                ],
                "temperature": 0,
                "max_tokens": 10
            }
            
            # 发送测试请求
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("choices") and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"].strip()
                    if "测试成功" in content:
                        self.update_status("API 连接测试成功")
                        ToastNotification("成功", "API 连接测试成功！", duration=3000, bootstyle='success').show_toast()
                    else:
                        self.update_status(f"API 响应不符合预期: {content}", level="error")
                        ToastNotification("失败", f"API 响应不符合预期", duration=3000, bootstyle='danger').show_toast()
                else:
                    self.update_status("API 响应格式异常", level="error")
                    ToastNotification("失败", "API 响应格式异常", duration=3000, bootstyle='danger').show_toast()
            else:
                self.update_status(f"API 请求失败，状态码: {response.status_code}", level="error")
                ToastNotification("失败", f"API 请求失败，状态码: {response.status_code}", duration=3000, bootstyle='danger').show_toast()
        except Exception as e:
            self.update_status(f"API 测试失败: {str(e)}", level="error")
            ToastNotification("失败", f"API 测试失败: {str(e)}", duration=3000, bootstyle='danger').show_toast()

    def on_close(self):
        """窗口关闭时的回调"""
        # 保存窗口几何信息
        geometry = self.root.geometry()
        config_manager.save_config({"geometry": geometry})
        
        # 保存当前选中的关键词
        if hasattr(self, 'keyword_vars'):
            selected_keywords = [(eng, chn) for eng, chn, var in self.keyword_vars if var.get()]
            config_manager.save_config({"last_keywords": selected_keywords})
            
        self.root.destroy()

if __name__ == "__main__":
    root = tb.Window(themename="flatly")
    app = ScraperGUI(root)
    root.mainloop()

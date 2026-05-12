"""主应用类，负责窗口管理和页面路由"""

import os
import re
import threading
import asyncio
from datetime import datetime
import tkinter as tk
from tkinter import END, DISABLED, NORMAL, filedialog, messagebox
import ttkbootstrap as tb
from typing import Dict

from gui.components.sidebar import Sidebar
from gui.components.status_card import StatusCard
from gui.components.log_panel import LogPanel
from gui.components.data_preview import DataPreviewWindow
from gui.components.toast import show_toast
from gui.components.tooltip import setup_tooltips
from gui.pages.engine_page import EnginePage
from gui.pages.ai_strategy_page import AIStrategyPage
from gui.pages.sync_settings_page import SyncSettingsPage
from gui.theme import BRAND_COLORS, SPACING

from core.scraper_controller import ScraperController
from core.keyword_service import KeywordService
from core.sync_service import SyncService
from core.config_service import ConfigService

from data import INDUSTRY_KEYWORDS, GEOGRAPHICAL_DATA, AI_KEYWORD_PROMPT
from async_utils import run_coro_in_new_loop


class ScraperApp:
    """主应用类"""
    
    def __init__(self, root: tb.Window):
        self.root = root
        self.root.title("B2B Global 获客系统")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 绑定窗口大小变化事件
        self.root.bind("<Configure>", self._on_window_resize)
        
        # 初始化服务
        self.scraper_controller = ScraperController()
        self.keyword_service = KeywordService()
        self.sync_service = SyncService()
        self.config_service = ConfigService()
        
        # 状态
        self.total_found = 0
        self.email_found = 0
        self.synced_count = 0
        self.keyword_vars = []
        
        self._setup_ui()
        self._bind_events()
        self._load_initial_data()
        self._restore_config()
        self._setup_tooltips()
    
    def _setup_ui(self):
        """设置界面"""
        # 侧边栏
        self.sidebar = Sidebar(self.root, on_page_change=self._on_page_change)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # 主内容区
        self.main_frame = tb.Frame(self.root)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=SPACING["md"], pady=SPACING["md"])
        
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
    
    def _bind_events(self):
        """绑定事件"""
        # 绑定页面事件
        engine = self.pages["engine"]
        engine.category_cb.bind("<<ComboboxSelected>>", self._on_category_select)
        engine.continent_cb.bind("<<ComboboxSelected>>", self._on_continent_select)
        engine.country_cb.bind("<<ComboboxSelected>>", self._on_country_select)
        engine.city_cb.bind("<<ComboboxSelected>>", self._on_city_select)
        
        # 绑定按钮事件
        engine.ai_gen_btn.config(command=self._generate_ai_keywords)
        engine.start_btn.config(command=self._start_task)
        engine.stop_btn.config(command=self._stop_task)
        engine.save_lib_btn.config(command=self._save_to_library)
        engine.open_lib_btn.config(command=self._open_keyword_library)
        engine.export_log_btn.config(command=self._export_logs)
        engine.data_preview_btn.config(command=self._show_data_preview)
        
        # 绑定功能按钮事件
        engine.sync_btn.config(command=self._manual_sync)
        engine.agg_sync_btn.config(command=self._manual_aggregate_sync)
        engine.test_proxy_btn.config(command=self._test_api_connection)
        engine.open_folder_btn.config(command=self._open_data_folder)
        
        # AI 策略页面
        ai = self.pages["ai"]
        ai.save_btn.config(command=self._save_prompt_template)
        
        # 同步设置页面
        sync = self.pages["sync"]
        sync.save_btn.config(command=self._save_sync_settings)
        sync.test_api_btn.config(command=self._test_api_connection)
        
        # 绑定服务事件
        self.scraper_controller.on_status_update = self._update_status
        self.scraper_controller.on_progress_update = self._update_progress
    
    def _load_initial_data(self):
        """加载初始数据"""
        # 加载行业关键词
        self.pages["engine"].category_cb['values'] = list(INDUSTRY_KEYWORDS.keys())
        
        # 加载地理数据
        self.pages["engine"].continent_cb['values'] = list(GEOGRAPHICAL_DATA.keys())
        
        # 加载 AI 提示词模板
        self._load_prompt_template()
        
        # 加载同步设置
        self._load_sync_settings()
        
        # 调整布局
        self.root.after(100, self.pages["engine"].adjust_ratios)
    
    def _on_category_select(self, event=None):
        """行业选择事件"""
        cat = self.pages["engine"].category_cb.get()
        if cat in INDUSTRY_KEYWORDS:
            words = "\n".join(INDUSTRY_KEYWORDS[cat])
            self.pages["engine"].kw_text.delete("1.0", END)
            self.pages["engine"].kw_text.insert(END, words)
    
    def _on_continent_select(self, event=None):
        """大洲选择事件"""
        continent = self.pages["engine"].continent_cb.get()
        if continent in GEOGRAPHICAL_DATA:
            countries = list(GEOGRAPHICAL_DATA[continent].keys())
            self.pages["engine"].country_cb['values'] = countries
            self.pages["engine"].country_cb.set('')
            self.pages["engine"].city_cb['values'] = []
            self.pages["engine"].city_cb.set('')
            self.pages["engine"].district_cb['values'] = []
            self.pages["engine"].district_cb.set('')
    
    def _on_country_select(self, event=None):
        """国家选择事件"""
        continent = self.pages["engine"].continent_cb.get()
        country = self.pages["engine"].country_cb.get()
        if continent in GEOGRAPHICAL_DATA and country in GEOGRAPHICAL_DATA[continent]:
            cities = list(GEOGRAPHICAL_DATA[continent][country]["cities"].keys())
            self.pages["engine"].city_cb['values'] = cities
            self.pages["engine"].city_cb.set('')
            self.pages["engine"].district_cb['values'] = []
            self.pages["engine"].district_cb.set('')
    
    def _on_city_select(self, event=None):
        """城市选择事件"""
        continent = self.pages["engine"].continent_cb.get()
        country = self.pages["engine"].country_cb.get()
        city = self.pages["engine"].city_cb.get()
        if (continent in GEOGRAPHICAL_DATA and 
            country in GEOGRAPHICAL_DATA[continent] and 
            city in GEOGRAPHICAL_DATA[continent][country]["cities"]):
            districts = GEOGRAPHICAL_DATA[continent][country]["cities"][city]
            self.pages["engine"].district_cb['values'] = districts
    
    def _generate_ai_keywords(self):
        """生成 AI 关键词"""
        seed_word = self.pages["engine"].seed_kw_entry.get().strip()
        if not seed_word or seed_word == "种子词...":
            show_toast("提示", "请输入种子词", bootstyle="warning")
            return
        
        num = int(self.pages["engine"].ai_kw_num_cb.get())
        self.keyword_service.on_keywords_generated = self._update_ui_with_keywords
        self.keyword_service.on_error = lambda e: show_toast("错误", str(e), bootstyle="danger")
        self.keyword_service.generate_keywords(seed_word, num)
        
        self.pages["engine"].ai_progress.pack(side=tk.LEFT, padx=5)
        self.pages["engine"].ai_progress.start(10)
    
    def _update_ui_with_keywords(self, keywords_with_translation):
        """更新关键词 UI"""
        self.pages["engine"].ai_progress.stop()
        self.pages["engine"].ai_progress.pack_forget()
        
        self._clear_tag_cloud()
        self.keyword_vars = []
        
        if keywords_with_translation:
            for eng_kw, chn_trans in keywords_with_translation:
                var = tk.BooleanVar(value=True)
                self.keyword_vars.append((eng_kw, chn_trans, var))
                
                frame = tb.Frame(self.pages["engine"].tag_cloud_frame)
                frame.pack(fill=tk.X, anchor=tk.W)
                
                cb = tb.Checkbutton(frame, text=eng_kw, variable=var)
                cb.pack(side=tk.LEFT, anchor=tk.W)
                
                if chn_trans:
                    tb.Label(frame, text=f"({chn_trans})", bootstyle="secondary").pack(side=tk.LEFT, anchor=tk.W, padx=5)
            
            show_toast("成功", f"已生成 {len(keywords_with_translation)} 个关键词", bootstyle="success")
        else:
            show_toast("失败", "AI 未能生成关键词", bootstyle="danger")
    
    def _clear_tag_cloud(self):
        """清空标签云"""
        for widget in self.pages["engine"].tag_cloud_frame.winfo_children():
            widget.destroy()
    
    def _save_to_library(self):
        """保存到关键词库"""
        if not self.keyword_vars:
            show_toast("提示", "当前没有可保存的关键词", bootstyle="warning")
            return
        
        to_save = [(eng, chn) for eng, chn, var in self.keyword_vars if var.get()]
        if not to_save:
            show_toast("提示", "请勾选要保存的关键词", bootstyle="warning")
            return
        
        import keyword_manager
        success, added = keyword_manager.save_keywords(to_save)
        if success:
            show_toast("成功", f"成功存入关键词库！新增 {added} 个", bootstyle="success")
        else:
            show_toast("错误", "关键词保存失败", bootstyle="danger")
    
    def _open_keyword_library(self):
        """打开关键词库"""
        from gui.dialogs.keyword_library_dialog import KeywordLibraryDialog
        dialog = KeywordLibraryDialog(self.root, on_load=self._update_ui_with_keywords)
    
    def _export_logs(self):
        """导出日志"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.pages["engine"].log_text.get("1.0", END))
            show_toast("成功", "日志已导出", bootstyle="success")
    
    def _show_data_preview(self):
        """显示数据预览"""
        downloads_dir = "Downloads"
        if not os.path.exists(downloads_dir):
            show_toast("提示", "暂无抓取数据", bootstyle="warning")
            return
        
        # 获取所有下载目录，按修改时间排序
        dirs = [d for d in os.listdir(downloads_dir) if os.path.isdir(os.path.join(downloads_dir, d))]
        if not dirs:
            show_toast("提示", "暂无抓取数据", bootstyle="warning")
            return
        
        # 按修改时间排序，最新的在前面
        dirs.sort(key=lambda x: os.path.getmtime(os.path.join(downloads_dir, x)), reverse=True)
        latest_dir = os.path.join(downloads_dir, dirs[0])
        
        # 创建数据预览窗口
        DataPreviewWindow(self.root, data_dir=latest_dir)
    
    def _start_task(self):
        """开始任务"""
        engine = self.pages["engine"]
        
        # 检查地理位置选择方式
        geo_mode = engine.geo_mode_var.get()
        
        if geo_mode == "select":
            # 预设位置选择
            if not engine.continent_cb.get() or not engine.country_cb.get() or not engine.city_cb.get():
                show_toast("输入错误", "请选择完整的大洲、国家和城市信息", bootstyle="warning")
                return
        else:
            # 手动输入地址
            manual_address = engine.manual_address_entry.get().strip()
            if not manual_address:
                show_toast("输入错误", "请输入地址", bootstyle="warning")
                return
        
        # 检查关键词
        keywords = []
        if hasattr(self, 'keyword_vars') and self.keyword_vars:
            keywords = [eng for eng, chn, var in self.keyword_vars if var.get()]
        
        if not keywords:
            # Fallback to text area if no keywords from checkboxes
            keywords_str = engine.kw_text.get("1.0", tk.END).strip()
            if keywords_str:
                keywords = [kw.strip() for kw in keywords_str.split('\n') if kw.strip()]
        
        if not keywords:
            show_toast("输入错误", "请生成或输入关键词", bootstyle="warning")
            return
        
        # 准备地理位置信息
        location = self._prepare_location()
        if not location:
            return
        
        # 重置计数
        self.total_found = 0
        self.email_found = 0
        self.synced_count = 0
        self._update_progress(0, 0, 0)
        
        # 更新UI状态
        engine.start_btn.config(state=DISABLED)
        engine.stop_btn.config(state=NORMAL)
        
        # 获取并发数
        concurrency = int(engine.concurrency_cb.get())
        
        # 启动抓取
        self.scraper_controller.start_scraping(keywords, location, concurrency)
        self._log_message("任务已启动", "info")
    
    def _prepare_location(self):
        """准备地理位置信息"""
        engine = self.pages["engine"]
        geo_mode = engine.geo_mode_var.get()
        
        if geo_mode == "select":
            continent_key = engine.continent_cb.get()
            country_key = engine.country_cb.get()
            city_key = engine.city_cb.get()
            district_full = engine.district_cb.get()
            
            try:
                country_en = GEOGRAPHICAL_DATA[continent_key][country_key]["en"]
                city_en_match = re.search(r'\((.*?)\)', city_key)
                city_en = city_en_match.group(1) if city_en_match else city_key
                
                # 提取区域的英文名称
                if district_full and district_full != "所有":
                    district_match = re.search(r'^(.*?)\s*\(', district_full)
                    district = district_match.group(1) if district_match else district_full
                else:
                    district = city_en
                
                return {
                    "country": country_en,
                    "city": city_en,
                    "district": district
                }
            except Exception as e:
                show_toast("错误", f"地理位置解析失败: {e}", bootstyle="danger")
                return None
        else:
            # 手动输入地址
            manual_address = engine.manual_address_entry.get().strip()
            translated_address = self._translate_address(manual_address)
            self._log_message(f"使用手动输入地址: {manual_address} (翻译: {translated_address})", "info")
            
            return {
                "country": "",
                "city": translated_address,
                "district": ""
            }
    
    def _translate_address(self, address):
        """将中文地址转换为英文"""
        try:
            # 检查是否已经是英文
            if not any('\u4e00' <= char <= '\u9fff' for char in address):
                return address.strip()
            
            # 尝试使用火山方舟API将中文地址翻译成英文
            try:
                from ai_generator import ARK_API_KEY, ARK_BASE_URL, ARK_MODEL_ENDPOINT
                
                if ARK_API_KEY and ARK_MODEL_ENDPOINT:
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
                        return translated_address
            except Exception:
                pass
            
            # 返回原始地址
            return address.strip()
        except Exception:
            return address.strip()
    
    def _stop_task(self):
        """停止任务"""
        self.scraper_controller.stop_scraping()
        self.pages["engine"].stop_btn.config(state=DISABLED)
        self._log_message("正在停止任务...", "info")
        
        # 重置UI
        self.root.after(1000, self._reset_ui)
    
    def _reset_ui(self):
        """重置UI状态"""
        engine = self.pages["engine"]
        engine.start_btn.config(state=NORMAL)
        engine.stop_btn.config(state=DISABLED)
        self._log_message("任务已结束", "info")
    
    def _load_prompt_template(self):
        """加载提示词模板"""
        self.pages["ai"].prompt_text.delete("1.0", END)
        self.pages["ai"].prompt_text.insert(END, AI_KEYWORD_PROMPT)
    
    def _save_prompt_template(self):
        """保存提示词模板"""
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
                    elif not in_prompt_section:
                        f.write(line)
            
            show_toast("成功", "提示词模板已保存", bootstyle="success")
        except Exception as e:
            show_toast("失败", f"保存失败: {e}", bootstyle="danger")
    
    def _load_sync_settings(self):
        """加载同步设置"""
        sync = self.pages["sync"]
        sync.proxy_entry.insert(0, os.getenv("HTTP_PROXY", ""))
        sync.sheets_id_entry.insert(0, os.getenv("GOOGLE_SHEETS_ID", ""))
        sync.gemini_api_key_entry.insert(0, os.getenv("GEMINI_API_KEY", ""))
        sync.doubao_api_key_entry.insert(0, os.getenv("DOUBAO_API_KEY", ""))
        sync.doubao_base_url_entry.insert(0, os.getenv("DOUBAO_BASE_URL", ""))
        sync.doubao_model_endpoint_entry.insert(0, os.getenv("DOUBAO_MODEL_ENDPOINT", ""))
        sync.by_date_var.set(os.getenv("SYNC_BY_DATE", "False").lower() == "true")
        sync.conflict_resolution_var.set(os.getenv("SYNC_CONFLICT_RESOLUTION", "keep_latest"))
    
    def _save_sync_settings(self):
        """保存同步设置"""
        sync = self.pages["sync"]
        new_settings = {
            "HTTP_PROXY": sync.proxy_entry.get().strip(),
            "GOOGLE_SHEETS_ID": sync.sheets_id_entry.get().strip(),
            "GEMINI_API_KEY": sync.gemini_api_key_entry.get().strip(),
            "DOUBAO_API_KEY": sync.doubao_api_key_entry.get().strip(),
            "DOUBAO_BASE_URL": sync.doubao_base_url_entry.get().strip(),
            "DOUBAO_MODEL_ENDPOINT": sync.doubao_model_endpoint_entry.get().strip(),
            "SYNC_BY_DATE": str(sync.by_date_var.get()),
            "SYNC_CONFLICT_RESOLUTION": sync.conflict_resolution_var.get(),
        }
        
        try:
            with open(".env", "w", encoding="utf-8") as f:
                for key, value in new_settings.items():
                    f.write(f'{key}="{value}"\n')
            show_toast("成功", "设置已保存", bootstyle="success")
        except Exception as e:
            show_toast("失败", f"保存失败: {e}", bootstyle="danger")
    
    def _test_api_connection(self):
        """测试 API 连接"""
        def _do_test():
            self._log_message("正在测试代理连接...", "info")
            try:
                from scraper_core import test_connection
                success = run_coro_in_new_loop(test_connection(self._log_message))
                if success:
                    show_toast("测试成功", "代理配置正确，可顺利连接 Google", bootstyle="success")
                else:
                    show_toast("测试失败", "无法连接 Google，请检查代理", bootstyle="danger")
            except Exception as e:
                self._log_message(f"测试异常: {e}", "error")
                show_toast("测试异常", "测试过程中发生错误", bootstyle="danger")
        
        threading.Thread(target=_do_test, daemon=True).start()
    
    def _manual_sync(self):
        """手动同步文件到 Google Sheets"""
        file_path = filedialog.askopenfilename(
            title="选择要同步的 CSV 文件",
            filetypes=[("CSV Files", "*.csv")],
            initialdir=os.path.join(os.getcwd(), "Downloads")
        )
        if not file_path:
            return
        
        def _do_sync():
            try:
                self._log_message("正在读取文件并同步...", "info")
                
                if not os.path.exists(file_path):
                    self._log_message(f"文件不存在: {file_path}", "error")
                    show_toast("同步失败", "选择的文件不存在", bootstyle="danger")
                    return
                
                if os.path.getsize(file_path) == 0:
                    self._log_message(f"文件为空: {file_path}", "warning")
                    show_toast("同步失败", "选择的文件为空", bootstyle="warning")
                    return
                
                import pandas as pd
                df = pd.read_csv(file_path)
                if df.empty:
                    self._log_message("文件内容为空", "warning")
                    show_toast("同步失败", "文件内容为空", bootstyle="warning")
                    return
                
                title = os.path.splitext(os.path.basename(file_path))[0]
                self._log_message(f"开始同步文件: {title}", "info")
                
                from scraper_core import upload_to_google_sheets
                success, _ = run_coro_in_new_loop(upload_to_google_sheets(df, title, self._log_message))
                
                if success:
                    self._log_message(f"手动同步任务成功: {title}", "success")
                    show_toast("同步成功", f"文件 '{title}' 已成功同步到云端！", bootstyle="success")
                else:
                    self._log_message(f"手动同步任务失败: {title}", "error")
                    show_toast("同步失败", f"文件 '{title}' 同步失败", bootstyle="danger")
            except Exception as e:
                error_msg = str(e)
                self._log_message(f"手动同步失败: {error_msg}", "error")
                show_toast("同步失败", f"错误详情: {error_msg}", bootstyle="danger")
        
        threading.Thread(target=_do_sync, daemon=True).start()
    
    def _manual_aggregate_sync(self):
        """汇总同步文件夹到 Google Sheets"""
        dir_path = filedialog.askdirectory(
            title="选择要汇总同步的文件夹",
            initialdir=os.path.join(os.getcwd(), "Downloads")
        )
        if not dir_path:
            return
        
        def _do_agg_sync():
            try:
                self._log_message("正在汇总数据并同步...", "info")
                
                if not os.path.exists(dir_path):
                    self._log_message(f"目录不存在: {dir_path}", "error")
                    show_toast("汇总失败", "选择的目录不存在", bootstyle="danger")
                    return
                
                if not os.listdir(dir_path):
                    self._log_message(f"目录为空: {dir_path}", "warning")
                    show_toast("汇总失败", "选择的目录为空", bootstyle="warning")
                    return
                
                from services.sheet_aggregator import aggregate_and_sync
                sync = self.pages["sync"]
                success = run_coro_in_new_loop(
                    aggregate_and_sync(
                        dir_path,
                        self._log_message,
                        target_title="lengdangb2b",
                        by_date=sync.by_date_var.get(),
                        conflict_resolution=sync.conflict_resolution_var.get()
                    )
                )
                if success:
                    show_toast("成功", "数据汇总并已同步至云端 'lengdangb2b'！", bootstyle="success")
                else:
                    self._log_message("汇总同步过程中出现问题", "error")
                    show_toast("汇总失败", "汇总同步过程中出现问题", bootstyle="danger")
            except Exception as e:
                error_msg = str(e)
                self._log_message(f"汇总操作异常: {error_msg}", "error")
                show_toast("错误", f"汇总同步失败: {error_msg}", bootstyle="danger")
        
        threading.Thread(target=_do_agg_sync, daemon=True).start()
    
    def _open_data_folder(self):
        """打开本地数据文件夹"""
        import platform
        import subprocess
        
        try:
            project_dir = os.getcwd()
            
            if platform.system() == "Windows":
                subprocess.Popen(f"explorer {project_dir}", shell=True)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", project_dir])
            else:
                subprocess.Popen(["xdg-open", project_dir])
            
            self._log_message(f"已打开数据文件夹: {project_dir}", "info")
        except Exception as e:
            self._log_message(f"打开文件夹失败: {str(e)}", "error")
            show_toast("打开失败", f"无法打开文件夹: {str(e)}", bootstyle="danger")
    
    def _log_message(self, message, level="info"):
        """记录日志到界面"""
        engine_page = self.pages.get("engine")
        if engine_page and hasattr(engine_page, 'log_text'):
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # 定义日志颜色
            log_colors = {
                "success": "green",
                "info": "white",
                "warning": "yellow",
                "error": "red"
            }
            
            def _append():
                log_text = engine_page.log_text
                log_text.config(state=NORMAL)
                
                tag = f"log_{level}"
                log_text.tag_config(tag, foreground=log_colors.get(level, "white"))
                
                log_text.insert(END, f"[{timestamp}] ", "log_default")
                log_text.insert(END, f"{message}\n", tag)
                log_text.see(END)
                log_text.config(state=DISABLED)
            
            # 在主线程中执行UI更新
            if threading.current_thread() is threading.main_thread():
                _append()
            else:
                self.root.after(0, _append)
    
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
    
    def _update_status(self, message: str, level: str = "info"):
        """更新状态"""
        engine_page = self.pages.get("engine")
        if engine_page and hasattr(engine_page, 'log_text'):
            engine_page.log_text.config(state=tk.NORMAL)
            engine_page.log_text.insert(END, f"[{level.upper()}] {message}\n")
            engine_page.log_text.see(END)
            engine_page.log_text.config(state=tk.DISABLED)
    
    def _update_progress(self, total: int, email: int, synced: int):
        """更新进度"""
        self.total_found = total
        self.email_found = email
        self.synced_count = synced
        
        engine_page = self.pages.get("engine")
        if engine_page:
            if hasattr(engine_page, 'total_scraped_card'):
                engine_page.total_scraped_card.config(text=str(total))
            if hasattr(engine_page, 'email_found_card'):
                engine_page.email_found_card.config(text=str(email))
            if hasattr(engine_page, 'synced_card'):
                engine_page.synced_card.config(text=str(synced))
    
    def _on_close(self):
        """窗口关闭时的回调"""
        try:
            import config_manager
            # 保存窗口几何信息
            geometry = self.root.geometry()
            config_manager.save_config({"geometry": geometry})
            
            # 保存当前选中的关键词
            if hasattr(self, 'keyword_vars') and self.keyword_vars:
                selected_keywords = [(eng, chn) for eng, chn, var in self.keyword_vars if var.get()]
                config_manager.save_config({"last_keywords": selected_keywords})
        except Exception:
            pass
        
        self.root.destroy()
    
    def _restore_config(self):
        """恢复上次配置"""
        try:
            import config_manager
            config = config_manager.load_config()
            
            # 恢复窗口位置
            if "geometry" in config:
                self.root.geometry(config["geometry"])
            
            # 恢复上次选中的关键词
            last_keywords = config.get("last_keywords", [])
            if last_keywords:
                self._update_ui_with_keywords(last_keywords)
        except Exception:
            pass
    
    def _setup_tooltips(self):
        """设置工具提示"""
        setup_tooltips(self.root)
    
    def _on_window_resize(self, event=None):
        """窗口大小变化时调整布局"""
        if event and event.widget == self.root:
            width = self.root.winfo_width()
            
            # 小于900px时自动折叠侧边栏
            if width < 900 and hasattr(self.sidebar, 'is_expanded') and self.sidebar.is_expanded:
                self.sidebar.collapse()
            elif width >= 1100 and hasattr(self.sidebar, 'is_expanded') and not self.sidebar.is_expanded:
                self.sidebar.expand()
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

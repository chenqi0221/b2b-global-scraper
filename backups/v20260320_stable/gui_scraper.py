import asyncio
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
from scraper_core import scrape_google_maps, upload_to_google_sheets, HTTP_PROXY, test_connection, aggregate_and_sync
from data import INDUSTRY_KEYWORDS, GEOGRAPHICAL_DATA

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("浪登卫浴 - 全球 B2B 获客系统")
        self.root.geometry("700x550")
        
        self.is_running = False
        self.stop_event = asyncio.Event()
        self.task_queue = asyncio.Queue()
        self.total_found = 0

        self._setup_ui()

    def _setup_ui(self):
        # 整体框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 行业分类
        ttk.Label(main_frame, text="1. 选择行业分类:").pack(anchor=tk.W)
        self.category_cb = ttk.Combobox(main_frame, values=list(INDUSTRY_KEYWORDS.keys()), state="readonly")
        self.category_cb.pack(fill=tk.X, pady=5)
        self.category_cb.bind("<<ComboboxSelected>>", self._on_category_select)
        
        # 2. 关键词编辑
        ttk.Label(main_frame, text="2. 编辑关键词 (每行一个):").pack(anchor=tk.W)
        self.kw_text = tk.Text(main_frame, height=5)
        self.kw_text.pack(fill=tk.X, pady=5)
        
        # 3. 地理位置选择
        geo_frame = ttk.LabelFrame(main_frame, text="3. 选择地理位置", padding="10")
        geo_frame.pack(fill=tk.X, pady=10)

        # 第一行：国家和城市
        row1 = ttk.Frame(geo_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="国家:").pack(side=tk.LEFT)
        self.country_cb = ttk.Combobox(row1, values=list(GEOGRAPHICAL_DATA.keys()), state="readonly", width=15)
        self.country_cb.pack(side=tk.LEFT, padx=(5, 15))
        self.country_cb.bind("<<ComboboxSelected>>", self._on_country_select)

        ttk.Label(row1, text="城市:").pack(side=tk.LEFT)
        self.city_cb = ttk.Combobox(row1, state="readonly", width=15)
        self.city_cb.pack(side=tk.LEFT, padx=5)
        self.city_cb.bind("<<ComboboxSelected>>", self._on_city_select)

        # 第二行：区域
        row2 = ttk.Frame(geo_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Label(row2, text="区域:").pack(side=tk.LEFT)
        self.district_cb = ttk.Combobox(row2, state="readonly")
        self.district_cb.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 4. 控制按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="开始获客", command=self.start_task)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self.stop_task, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        self.sync_btn = ttk.Button(btn_frame, text="同步到云端", command=self.manual_sync)
        self.sync_btn.pack(side=tk.LEFT, padx=10)

        self.sync_all_btn = ttk.Button(btn_frame, text="同步整个文件夹", command=self.manual_sync_folder)
        self.sync_all_btn.pack(side=tk.LEFT, padx=10)

        self.agg_sync_btn = ttk.Button(btn_frame, text="数据汇总同步", command=self.manual_aggregate_sync)
        self.agg_sync_btn.pack(side=tk.LEFT, padx=10)

        self.test_btn = ttk.Button(btn_frame, text="测试代理", command=self.run_test_connection)
        self.test_btn.pack(side=tk.LEFT, padx=10)
        
        # 5. 状态显示与结果预览
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="就绪", foreground="blue", font=("微软雅黑", 10))
        self.status_label.pack(side=tk.LEFT)
        
        self.count_label = ttk.Label(status_frame, text="已抓取: 0", foreground="green", font=("微软雅黑", 10))
        self.count_label.pack(side=tk.RIGHT)

        ttk.Label(main_frame, text="抓取日志:").pack(anchor=tk.W)
        self.log_text = tk.Text(main_frame, height=10, state=tk.DISABLED, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def log_message(self, message):
        """向界面日志框添加信息"""
        def _append():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        self.root.after(0, _append)

    def _on_category_select(self, event):
        cat = self.category_cb.get()
        words = "\n".join(INDUSTRY_KEYWORDS[cat])
        self.kw_text.delete("1.0", tk.END)
        self.kw_text.insert(tk.END, words)

    def _on_country_select(self, event):
        country_key = self.country_cb.get()
        cities = list(GEOGRAPHICAL_DATA[country_key]["cities"].keys())
        self.city_cb['values'] = cities
        self.city_cb.set('')
        self.district_cb['values'] = []
        self.district_cb.set('')

    def _on_city_select(self, event):
        country_key = self.country_cb.get()
        city_key = self.city_cb.get()
        districts = GEOGRAPHICAL_DATA[country_key]["cities"][city_key]
        self.district_cb['values'] = districts
        self.district_cb.set('')

    def update_status(self, msg):
        self.root.after(0, lambda: self.status_label.config(text=msg))
        self.log_message(msg)
        if "进度" in msg and "(" in msg:
            try:
                # 尝试从 "进度 (1/20)" 中提取当前数字
                count = msg.split("(")[1].split("/")[0]
                self.root.after(0, lambda: self.count_label.config(text=f"已抓取: {count}"))
            except:
                pass

    def start_task(self):
        # 校验输入
        if not self.country_cb.get() or not self.city_cb.get():
            messagebox.showwarning("提示", "请选择完整的国家和城市信息")
            return
            
        keywords = self.kw_text.get("1.0", tk.END).strip()
        if not keywords:
            messagebox.showwarning("提示", "请在文本框中输入关键词")
            return

        self.is_running = True
        self.stop_event.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.count_label.config(text="已抓取: 0")
        
        # 开启后台线程运行异步任务
        threading.Thread(target=self._run_async_loop, daemon=True).start()

    def stop_task(self):
        self.is_running = False
        self.stop_event.set()
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("正在停止...")

    def manual_sync(self):
        """手动选择文件并同步到 Google Sheets"""
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
                df = pd.read_csv(file_path)
                if df.empty:
                    self.log_message("文件内容为空")
                    return
                
                # 运行异步同步逻辑
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # 获取文件名（不含扩展名）作为云端表格标题
                title = os.path.splitext(os.path.basename(file_path))[0]
                success, _ = loop.run_until_complete(upload_to_google_sheets(df, title, self.update_status))
                loop.close()
                
                if success:
                    self.log_message(f"手动同步任务成功: {title}")
                    messagebox.showinfo("同步成功", f"文件 '{title}' 已成功同步到云端！")
                else:
                    self.log_message(f"手动同步任务失败: {title}")
                    messagebox.showwarning("同步失败", f"文件 '{title}' 同步失败，请查看日志。")
            except Exception as e:
                self.log_message(f"手动同步失败: {str(e)}")
                messagebox.showerror("同步失败", f"错误详情: {str(e)}")

        threading.Thread(target=_do_sync, daemon=True).start()

    def manual_sync_folder(self):
        """手动选择文件夹并同步其中所有 CSV"""
        dir_path = filedialog.askdirectory(
            title="选择要同步的文件夹",
            initialdir=os.path.join(os.getcwd(), "Downloads")
        )
        
        if not dir_path:
            return

        def _do_sync_folder():
            try:
                # 寻找文件夹中的所有 CSV 文件
                csv_files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
                if not csv_files:
                    self.log_message(f"在 {dir_path} 内未找到 CSV 文件")
                    return

                self.update_status(f"准备批量同步 {len(csv_files)} 个文件...")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                success_count = 0
                for f in csv_files:
                    try:
                        file_path = os.path.join(dir_path, f)
                        title = os.path.splitext(f)[0]
                        # 检查文件是否为空
                        if os.path.getsize(file_path) < 10: 
                            continue
                        
                        df = pd.read_csv(file_path)
                        if df.empty:
                            continue
                            
                        success, _ = loop.run_until_complete(upload_to_google_sheets(df, title, self.update_status))
                        if success:
                            success_count += 1
                    except Exception as fe:
                        self.log_message(f"同步单个文件 {f} 失败: {str(fe)}")
                        continue
                
                loop.close()
                messagebox.showinfo("同步结束", f"同步完成！\n成功: {success_count}\n失败: {len(csv_files) - success_count}")
            except Exception as e:
                self.log_message(f"批量同步失败: {str(e)}")
                messagebox.showerror("同步失败", f"错误详情: {str(e)}")

        threading.Thread(target=_do_sync_folder, daemon=True).start()

    def manual_aggregate_sync(self):
        """手动选择文件夹汇总并去重上传"""
        dir_path = filedialog.askdirectory(
            title="选择要汇总同步的文件夹",
            initialdir=os.path.join(os.getcwd(), "Downloads")
        )
        
        if not dir_path:
            return

        def _do_agg_sync():
            try:
                self.agg_sync_btn.config(state=tk.DISABLED)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(aggregate_and_sync(dir_path, self.update_status, target_title="lengdangb2b"))
                loop.close()
                
                if success:
                    messagebox.showinfo("成功", "数据汇总并已同步至云端 'lengdangb2b'！")
                else:
                    messagebox.showwarning("汇总失败", "汇总同步过程中出现问题，请查看日志。")
            except Exception as e:
                self.log_message(f"汇总操作异常: {str(e)}")
                messagebox.showerror("错误", f"汇总同步失败: {str(e)}")
            finally:
                self.root.after(0, lambda: self.agg_sync_btn.config(state=tk.NORMAL))

        threading.Thread(target=_do_agg_sync, daemon=True).start()

    def run_test_connection(self):
        """运行网络测试任务"""
        def _do_test():
            self.test_btn.config(state=tk.DISABLED)
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(test_connection(self.update_status))
                loop.close()
                
                if success:
                    messagebox.showinfo("测试成功", "代理配置正确，可顺利连接 Google")
                else:
                    messagebox.showwarning("测试失败", "无法连接 Google，请检查代理端口或软件状态。")
            finally:
                self.root.after(0, lambda: self.test_btn.config(state=tk.NORMAL))

        threading.Thread(target=_do_test, daemon=True).start()

    def _run_async_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.main_worker())

    async def main_worker(self):
        # 获取当前选择的地理信息
        country_key = self.country_cb.get()
        city_key = self.city_cb.get()
        district = self.district_cb.get() or city_key

        # 提取英文名称用于搜索
        country_en = GEOGRAPHICAL_DATA[country_key]["en"]
        # 提取城市英文名，例如从 "迪拜 (Dubai)" 提取 "Dubai"
        import re
        city_en_match = re.search(r'\((.*?)\)', city_key)
        city_en = city_en_match.group(1) if city_en_match else city_key

        # 创建本次任务专属文件夹 (包含日期和精确时间戳)
        session_folder_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_dir = os.path.join("Downloads", session_folder_name)
        os.makedirs(output_dir, exist_ok=True)
        self.log_message(f"本次任务文件将保存至: {output_dir}")

        async with async_playwright() as p:
            # 如果配置了代理，传给 browser.launch
            launch_kwargs = {"headless": False}
            if HTTP_PROXY:
                launch_kwargs["proxy"] = {"server": HTTP_PROXY}
                self.log_message(f"Playwright 已启用代理: {HTTP_PROXY}")
                
            browser = await p.chromium.launch(**launch_kwargs)
            
            # 获取所有关键词行
            keywords = [k.strip() for k in self.kw_text.get("1.0", tk.END).strip().split('\n') if k.strip()]
            
            for kw in keywords:
                if not self.is_running: break
                
                # 构造任务信息
                task_info = {
                    'keyword': kw,
                    'country': country_en,
                    'city': city_en,
                    'district': district
                }
                
                try:
                    await scrape_google_maps(browser, task_info, output_dir, self.update_status, self.stop_event)
                except Exception as e:
                    self.log_message(f"抓取关键词 '{kw}' 时出错: {str(e)}")
                    continue
            
            await browser.close()
            self.root.after(0, self._reset_ui)

    def _reset_ui(self):
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("任务已结束")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class EnginePage(tb.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        # --- 1. 状态卡片 (固定在顶部) ---
        cards_frame = tb.Frame(self, style='custom.TFrame')
        cards_frame.pack(fill=X, padx=10, pady=10)

        self.total_scraped_card = self.create_status_card(cards_frame, "今日已抓取", "0")
        self.email_found_card = self.create_status_card(cards_frame, "包含邮箱数", "0")
        self.synced_card = self.create_status_card(cards_frame, "已同步云端数", "0")
        
        # --- 1.1 数据预览按钮 ---
        self.data_preview_btn = tb.Button(cards_frame, text="数据预览", bootstyle="primary-outline", width=12)
        self.data_preview_btn.pack(side=RIGHT, padx=5, pady=5)
        self.data_preview_btn.tooltip = "查看最近抓取的数据结果"

        # --- 2. 主面板 (左右分栏 Panedwindow) ---
        self.main_pane = tb.Panedwindow(self, orient=HORIZONTAL)
        self.main_pane.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # --- 3. 左侧面板 (关键词配置) ---
        kw_frame = tb.LabelFrame(self.main_pane, text="关键词配置")
        self.main_pane.add(kw_frame, weight=2)

        # --- 4. 右侧面板 (上下分栏：地理位置选择 + 运行日志) ---
        right_pane = tb.Panedwindow(self.main_pane, orient=VERTICAL)
        self.main_pane.add(right_pane, weight=1)

        # 4.1 地理位置选择框架
        geo_frame = tb.LabelFrame(right_pane, text="地理位置选择")
        right_pane.add(geo_frame, weight=1)

        # 4.2 运行日志框架
        log_frame = tb.LabelFrame(right_pane, text="运行日志")
        right_pane.add(log_frame, weight=2)

        # --- 5. 填充 [关键词配置] 内容 ---
        tb.Label(kw_frame, text="选择行业:").pack(anchor=W, pady=(0, 5), padx=10)
        self.category_cb = tb.Combobox(kw_frame, values=[], state="readonly")
        self.category_cb.pack(fill=X, pady=(0, 10), padx=10)
        self.category_cb.tooltip = "选择行业类别以获取相关关键词"

        # AI 拓展
        ai_frame = tb.Frame(kw_frame)
        ai_frame.pack(fill=X, pady=5, padx=10)
        self.seed_kw_entry = tb.Entry(ai_frame, width=10)
        self.seed_kw_entry.pack(side=LEFT, expand=True, fill=X)
        self.seed_kw_entry.insert(0, "种子词...")
        self.seed_kw_entry.tooltip = "输入种子词，AI 将基于此生成相关关键词"
        
        self.ai_kw_num_cb = tb.Combobox(ai_frame, values=list(range(1, 21)), width=3)
        self.ai_kw_num_cb.set(7)
        self.ai_kw_num_cb.pack(side=LEFT, padx=5)
        self.ai_kw_num_cb.tooltip = "设置 AI 生成关键词的数量"
        
        self.ai_gen_btn = tb.Button(ai_frame, text="AI 生成", bootstyle="info-outline")
        self.ai_gen_btn.pack(side=LEFT, padx=5)
        self.ai_gen_btn.tooltip = "使用 AI 生成基于种子词的相关关键词"
        
        self.ai_progress = tb.Progressbar(ai_frame, mode='indeterminate', length=50)

        # 并发设置
        concurrency_frame = tb.Frame(kw_frame)
        concurrency_frame.pack(fill=X, pady=(10, 0), padx=10)
        tb.Label(concurrency_frame, text="并发抓取数:").pack(side=LEFT)
        self.concurrency_cb = tb.Combobox(concurrency_frame, values=list(range(1, 11)), width=3, state="readonly")
        self.concurrency_cb.set(3)
        self.concurrency_cb.pack(side=LEFT, padx=5)
        self.concurrency_cb.tooltip = "设置同时抓取的关键词数量，建议 3-5 个"
        tb.Label(concurrency_frame, text="(建议 3-5)", bootstyle="secondary").pack(side=LEFT)

        # 关键词库按钮
        lib_btn_frame = tb.Frame(kw_frame)
        lib_btn_frame.pack(fill=X, pady=(10, 0), padx=10)
        self.save_lib_btn = tb.Button(lib_btn_frame, text="存入关键词库", bootstyle="success-outline")
        self.save_lib_btn.pack(side=LEFT, expand=True, fill=X, padx=(0, 5))
        self.save_lib_btn.tooltip = "将当前生成的关键词保存到关键词库"
        
        self.open_lib_btn = tb.Button(lib_btn_frame, text="打开关键词库", bootstyle="info-outline")
        self.open_lib_btn.pack(side=LEFT, expand=True, fill=X, padx=(5, 0))
        self.open_lib_btn.tooltip = "打开关键词库，可查看、导入、导出和加载关键词"

        tb.Label(kw_frame, text="关键词列表:").pack(anchor=W, pady=(5, 0), padx=10)
        self.kw_text = tk.Text(kw_frame, height=1, width=30) # 备用
        
        # 标签云滚动区域
        cloud_outer_frame = tb.Frame(kw_frame)
        cloud_outer_frame.pack(fill=BOTH, expand=True, pady=(5, 0), padx=10)
        self.canvas = tk.Canvas(cloud_outer_frame, highlightthickness=0)
        self.scrollbar = tb.Scrollbar(cloud_outer_frame, orient="vertical", command=self.canvas.yview)
        self.tag_cloud_frame = tb.Frame(self.canvas)
        self.tag_cloud_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.tag_cloud_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # --- 6. 填充 [地理位置选择] 内容 ---
        geo_inner_frame = tb.Frame(geo_frame)
        geo_inner_frame.pack(fill=X, padx=10, pady=10)
        
        # 添加地理位置选择方式切换
        tb.Label(geo_inner_frame, text="选择方式:").grid(row=0, column=0, sticky=W, pady=2)
        self.geo_mode_var = tk.StringVar(value="select")
        geo_mode_frame = tb.Frame(geo_inner_frame)
        geo_mode_frame.grid(row=0, column=1, sticky=EW, pady=2, padx=5)
        tb.Radiobutton(geo_mode_frame, text="选择预设位置", variable=self.geo_mode_var, value="select").pack(side=LEFT, padx=5)
        tb.Radiobutton(geo_mode_frame, text="手动输入地址", variable=self.geo_mode_var, value="manual").pack(side=LEFT, padx=5)
        
        # 预设位置选择区域
        tb.Label(geo_inner_frame, text="大洲:").grid(row=1, column=0, sticky=W, pady=2)
        self.continent_cb = tb.Combobox(geo_inner_frame, values=[], state="readonly", width=18)
        self.continent_cb.grid(row=1, column=1, sticky=EW, pady=2, padx=5)
        self.continent_cb.tooltip = "选择要抓取的大洲"
        
        tb.Label(geo_inner_frame, text="国家:").grid(row=2, column=0, sticky=W, pady=2)
        self.country_cb = tb.Combobox(geo_inner_frame, state="readonly", width=18)
        self.country_cb.grid(row=2, column=1, sticky=EW, pady=2, padx=5)
        self.country_cb.tooltip = "选择要抓取的国家"
        
        tb.Label(geo_inner_frame, text="城市:").grid(row=3, column=0, sticky=W, pady=2)
        self.city_cb = tb.Combobox(geo_inner_frame, state="readonly", width=18)
        self.city_cb.grid(row=3, column=1, sticky=EW, pady=2, padx=5)
        self.city_cb.tooltip = "选择要抓取的城市"
        
        tb.Label(geo_inner_frame, text="区域:").grid(row=4, column=0, sticky=W, pady=2)
        self.district_cb = tb.Combobox(geo_inner_frame, state="readonly", width=18)
        self.district_cb.grid(row=4, column=1, sticky=EW, pady=2, padx=5)
        self.district_cb.tooltip = "选择要抓取的具体区域，留空则抓取整个城市"
        
        # 手动输入地址区域
        tb.Label(geo_inner_frame, text="手动输入地址:").grid(row=5, column=0, sticky=W, pady=2)
        self.manual_address_entry = tb.Entry(geo_inner_frame, width=22)
        self.manual_address_entry.grid(row=5, column=1, sticky=EW, pady=2, padx=5)
        self.manual_address_entry.tooltip = "手动输入地址，系统会自动转换为英文进行搜索"
        
        btn_frame = tb.Frame(geo_inner_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        self.start_btn = tb.Button(btn_frame, text="开始获客", bootstyle="success", width=10)
        self.start_btn.pack(side=LEFT, padx=5)
        self.start_btn.tooltip = "开始执行 Google Maps 抓取任务"
        
        self.stop_btn = tb.Button(btn_frame, text="停止", state=DISABLED, bootstyle="danger-outline", width=10)
        self.stop_btn.pack(side=LEFT, padx=5)
        self.stop_btn.tooltip = "停止当前运行的抓取任务"

        # --- 7. 填充 [运行日志] 内容 ---
        log_control_frame = tb.Frame(log_frame)
        log_control_frame.pack(fill=X, padx=5, pady=5)
        self.log_text = tk.Text(log_frame, height=10, state=DISABLED, font=("Consolas", 10),
                                bg="#2d3e50", fg="white", relief="flat", padx=5, pady=5)
        self.log_text.pack(fill=BOTH, expand=True)
        
        # 日志控制按钮
        self.export_log_btn = tb.Button(log_control_frame, text="导出日志", bootstyle="info-outline", width=10)
        self.export_log_btn.pack(side=RIGHT, padx=5)
        self.export_log_btn.tooltip = "将运行日志导出为文本文件"

    def adjust_ratios(self):
        """
        在界面完全加载后，强制将左右比例设置为 2:1 (2/3 关键词区域)
        """
        self.update_idletasks() # 确保窗口大小已计算
        width = self.main_pane.winfo_width()
        if width > 100:
            sash_pos = int(width * (2/3))
            try:
                self.main_pane.sashpos(0, sash_pos)
            except:
                pass # 有些环境下可能暂不可用，忽略以防崩溃

    def create_status_card(self, parent, title, value):
        card = tb.LabelFrame(parent, text=title)
        card.pack(side=LEFT, fill=X, expand=True, padx=5)
        value_label = tb.Label(card, text=value, font=("Helvetica", 16, "bold"))
        value_label.pack(pady=10)
        return value_label

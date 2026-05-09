import ttkbootstrap as tb
from ttkbootstrap.constants import *

class SyncSettingsPage(tb.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        tb.Label(self, text="同步与 API 设置", font=("Helvetica", 18, "bold")).pack(pady=(20, 10))

        # --- HTTP 代理 ---
        proxy_frame = tb.LabelFrame(self, text="网络代理")
        proxy_frame.pack(fill=X, padx=20, pady=10)
        tb.Label(proxy_frame, text="HTTP 代理:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.proxy_entry = tb.Entry(proxy_frame, width=50)
        self.proxy_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)

        # --- Google API ---
        google_api_frame = tb.LabelFrame(self, text="Google API 设置")
        google_api_frame.pack(fill=X, padx=20, pady=10)
        tb.Label(google_api_frame, text="Sheets ID:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.sheets_id_entry = tb.Entry(google_api_frame, width=50)
        self.sheets_id_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
        tb.Label(google_api_frame, text="Gemini API Key:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.gemini_api_key_entry = tb.Entry(google_api_frame, width=50)
        self.gemini_api_key_entry.grid(row=1, column=1, sticky=EW, padx=5, pady=5)

        # --- Doubao API ---
        doubao_api_frame = tb.LabelFrame(self, text="豆包 API 设置")
        doubao_api_frame.pack(fill=X, padx=20, pady=10)
        tb.Label(doubao_api_frame, text="API Key:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.doubao_api_key_entry = tb.Entry(doubao_api_frame, width=50)
        self.doubao_api_key_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
        tb.Label(doubao_api_frame, text="Base URL:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.doubao_base_url_entry = tb.Entry(doubao_api_frame, width=50)
        self.doubao_base_url_entry.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
        tb.Label(doubao_api_frame, text="Model Endpoint:").grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.doubao_model_endpoint_entry = tb.Entry(doubao_api_frame, width=50)
        self.doubao_model_endpoint_entry.grid(row=2, column=1, sticky=EW, padx=5, pady=5)
        
        # API 测试按钮
        self.test_api_btn = tb.Button(doubao_api_frame, text="测试 API 连接", bootstyle="primary-outline", width=15)
        self.test_api_btn.grid(row=3, column=1, sticky=E, padx=5, pady=10)
        self.test_api_btn.tooltip = "测试豆包 API 连接是否正常"
        
        # --- 同步设置 ---
        sync_settings_frame = tb.LabelFrame(self, text="同步设置")
        sync_settings_frame.pack(fill=X, padx=20, pady=10)
        
        # 按日期汇总多工作表选项
        self.by_date_var = tb.BooleanVar(value=False)
        by_date_check = tb.Checkbutton(sync_settings_frame, text="按日期汇总多工作表", variable=self.by_date_var)
        by_date_check.grid(row=0, column=0, sticky=W, padx=5, pady=5, columnspan=2)
        
        # 冲突处理策略
        tb.Label(sync_settings_frame, text="数据冲突处理:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.conflict_resolution_var = tb.StringVar(value="keep_latest")
        conflict_options = [
            ("保留最新数据", "keep_latest"),
            ("保留云端数据", "keep_cloud"),
            ("保留本地数据", "keep_local")
        ]
        
        for i, (text, value) in enumerate(conflict_options):
            tb.Radiobutton(sync_settings_frame, text=text, variable=self.conflict_resolution_var, value=value).grid(row=2+i, column=0, sticky=W, padx=20, pady=2)

        self.save_btn = tb.Button(self, text="保存所有设置", bootstyle="success")
        self.save_btn.pack(pady=20)

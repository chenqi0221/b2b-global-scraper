# 修复重构后缺失功能计划

> **目标:** 修复重构后缺失的"文件同步"按钮和"数据预览"功能

**问题描述:**
1. **文件同步按钮缺失** - 原 `gui_scraper.py` 底部状态栏有"同步到云端"、"汇总同步"、"测试代理"、"打开文件夹"四个功能按钮，重构后在 `gui/app.py` 中这些方法存在但未被绑定到UI
2. **数据预览问题** - `DataPreviewWindow` 组件存在，但预览的是 `date_data` 目录，而实际数据保存在 `Downloads` 子目录中

---

## 任务1: 在 EnginePage 底部添加功能按钮栏

**文件:** `gui/pages/engine_page.py`

**分析:** 原 `gui_scraper.py` 在状态栏底部有4个功能按钮：
- "同步到云端" → `manual_sync`
- "汇总同步" → `manual_aggregate_sync`
- "测试代理" → `run_test_connection`
- "打开文件夹" → `open_data_folder`

需要在 `EnginePage` 的日志区域下方添加一个按钮栏。

**步骤:**
- [ ] 在 `EnginePage._setup_ui()` 的日志框架下方添加功能按钮框架
- [ ] 添加4个按钮：sync_btn, agg_sync_btn, test_proxy_btn, open_folder_btn
- [ ] 按钮使用 `bootstyle="outline"` 样式

```python
# 在日志控制按钮区域添加
self.sync_btn = tb.Button(log_control_frame, text="同步到云端", bootstyle="info-outline")
self.sync_btn.pack(side=tk.LEFT, padx=5)

self.agg_sync_btn = tb.Button(log_control_frame, text="汇总同步", bootstyle="primary-outline")
self.agg_sync_btn.pack(side=tk.LEFT, padx=5)

self.test_proxy_btn = tb.Button(log_control_frame, text="测试代理", bootstyle="warning-outline")
self.test_proxy_btn.pack(side=tk.LEFT, padx=5)

self.open_folder_btn = tb.Button(log_control_frame, text="打开文件夹", bootstyle="secondary-outline")
self.open_folder_btn.pack(side=tk.LEFT, padx=5)
```

---

## 任务2: 在 ScraperApp 中绑定新按钮事件

**文件:** `gui/app.py`

**步骤:**
- [ ] 在 `_bind_events()` 方法中绑定4个新按钮的事件

```python
# 绑定功能按钮事件
engine.sync_btn.config(command=self._manual_sync)
engine.agg_sync_btn.config(command=self._manual_aggregate_sync)
engine.test_proxy_btn.config(command=self._test_api_connection)
engine.open_folder_btn.config(command=self._open_data_folder)
```

---

## 任务3: 修复数据预览功能

**文件:** `gui/components/data_preview.py`

**问题:** `DataPreviewWindow` 构造函数接收 `data_dir` 参数，但 `ScraperApp._show_data_preview()` 传入的是 `"date_data"` 字符串。实际数据文件分散在 `Downloads/日期文件夹/` 子目录中。

**分析原代码:** 原 `gui_scraper.py` 中数据预览可能直接读取 `lengdangb2b.csv` 或汇总数据。

**步骤:**
- [ ] 修改 `_show_data_preview()` 方法，传入正确的数据目录或文件路径
- [ ] 或者修改 `DataPreviewWindow` 支持递归搜索 `Downloads` 下的所有 CSV 文件

**方案A - 修改 ScraperApp:**
```python
def _show_data_preview(self):
    """显示数据预览"""
    # 预览总表文件
    if os.path.exists("lengdangb2b.csv"):
        DataPreviewWindow(self.root, file_path="lengdangb2b.csv")
    else:
        show_toast("提示", "没有找到数据文件", bootstyle="warning")
```

**方案B - 修改 DataPreviewWindow 支持文件路径:**
```python
class DataPreviewWindow(tb.Toplevel):
    def __init__(self, parent, data_dir=None, file_path=None):
        # 支持传入文件路径直接预览
        if file_path and os.path.exists(file_path):
            self.preview_file = file_path
        else:
            self.data_dir = data_dir
```

---

## 任务4: 验证所有功能

**步骤:**
- [ ] 运行 `python -m py_compile gui/pages/engine_page.py gui/app.py gui/components/data_preview.py`
- [ ] 启动应用检查按钮是否正常显示
- [ ] 测试每个按钮功能是否正常

---

## 文件修改清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `gui/pages/engine_page.py` | 修改 | 添加4个功能按钮 |
| `gui/app.py` | 修改 | 绑定按钮事件 |
| `gui/components/data_preview.py` | 修改 | 修复数据预览逻辑 |

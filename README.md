# Google Maps Scraper - B2B 获客引擎

一款基于 Python + Playwright 的 Google Maps 商家数据采集工具，专为 B2B 外贸获客场景设计。支持 AI 智能关键词生成、多地区批量抓取、邮箱自动提取、Google Sheets 云端同步等功能。

## 功能特性

### 核心功能
- **Google Maps 商家抓取**：自动搜索并采集商家名称、电话、地址、网站等信息
- **AI 关键词生成**：基于种子词通过 AI 智能拓展行业关键词（支持豆包/火山方舟 API）
- **邮箱自动提取**：自动访问商家网站并提取联系邮箱
- **多地区支持**：内置中东、东南亚、欧美等地区数据，支持手动输入地址
- **关键词库管理**：支持保存、导入、导出关键词，建立行业词库

### 数据同步
- **Google Sheets 同步**：一键同步抓取结果到 Google Sheets
- **批量汇总同步**：支持按日期汇总多个 CSV 文件并同步
- **冲突处理策略**：支持保留最新数据或合并数据

### 界面特性
- **现代化 GUI**：基于 ttkbootstrap 的深色主题界面
- **实时状态看板**：显示已抓取数量、邮箱数量、同步数量
- **运行日志**：实时显示抓取进度和状态
- **数据预览**：内置 CSV 数据预览功能

## 技术栈

- **Python 3.11+**
- **Playwright**：浏览器自动化，模拟真人操作
- **ttkbootstrap**：现代化 Tkinter 主题
- **Pandas**：数据处理与导出
- **Google API**：Google Sheets / Drive 集成
- **火山方舟 API**：AI 关键词生成

## 安装部署

### 环境要求
- Python 3.11 或更高版本
- Windows 10/11 操作系统
- 稳定的网络连接（建议配置代理）

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/chenqi0221/google-maps-scraper.git
   cd google-maps-scraper
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **安装 Playwright 浏览器**
   ```bash
   playwright install chromium
   ```

4. **配置环境变量**
   复制 `.env.example` 为 `.env`，并填写以下配置：
   ```env
   # Google API（用于同步到 Google Sheets）
   GEMINI_API_KEY="your_gemini_api_key"
   GOOGLE_SHEETS_ID="your_google_sheets_id"
   
   # 代理配置（访问 Google 需要）
   HTTP_PROXY="http://127.0.0.1:7890"
   
   # 豆包 API（用于 AI 关键词生成）
   DOUBAO_API_KEY="your_doubao_api_key"
   DOUBAO_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
   DOUBAO_MODEL_ENDPOINT="your_model_endpoint"
   
   # 同步设置
   SYNC_BY_DATE="True"
   SYNC_CONFLICT_RESOLUTION="keep_latest"
   ```

5. **配置 Google OAuth**
   - 将 `client_secret.json` 放入项目根目录（从 Google Cloud Console 下载）
   - 首次运行时会自动引导完成 OAuth 授权

6. **启动程序**
   ```bash
   python gui_scraper.py
   ```

## 使用指南

### 1. 获客引擎（主界面）

#### 关键词配置
- **选择行业**：从下拉菜单选择预设行业，自动加载相关关键词
- **AI 生成**：输入种子词（如 "Bathroom Vanity"），选择生成数量，点击 AI 生成按钮
- **关键词库**：打开关键词库管理界面，支持导入/导出/删除关键词

#### 地理位置选择
- **预设位置**：选择大洲 → 国家 → 城市 → 区域
- **手动输入**：直接输入英文地址（如 "Dubai Marina, Dubai"）

#### 开始抓取
1. 配置好关键词和地理位置
2. 点击"开始任务"按钮
3. 在日志区域查看实时进度
4. 抓取完成后，数据自动保存到 `date_data/` 目录

### 2. AI 策略

- 编辑 AI 提示词模板，自定义关键词生成策略
- 保存模板后，在获客引擎页面使用

### 3. 同步设置

- **代理设置**：配置 HTTP 代理以访问 Google
- **API 配置**：设置 Google Sheets ID 和 Gemini API Key
- **豆包 API**：配置火山方舟 API 用于 AI 关键词生成
- **测试连接**：验证代理和 API 连接是否正常

### 4. 数据同步

- **手动同步**：选择单个 CSV 文件同步到 Google Sheets
- **汇总同步**：选择文件夹，汇总所有 CSV 文件后同步
- **打开文件夹**：快速打开数据目录查看本地文件

## 项目结构

```
google-maps-scraper/
├── gui_scraper.py              # 主程序入口，GUI 界面
├── scraper_core.py             # 核心逻辑封装
├── google_maps_scraper.py      # Google Maps 抓取实现
├── email_extractor.py          # 邮箱提取模块
├── file_export.py              # 文件导出功能
├── google_sheets_service.py    # Google Sheets 同步
├── sheet_aggregator.py         # 数据汇总逻辑
├── ai_generator.py             # AI 关键词生成
├── keyword_manager.py          # 关键词库管理
├── config_manager.py           # 配置管理
├── data.py                     # 地理位置数据
├── config.py                   # 环境配置
├── pages/                      # GUI 页面组件
│   ├── engine_page.py          # 获客引擎页面
│   ├── ai_strategy_page.py     # AI 策略页面
│   └── sync_settings_page.py   # 同步设置页面
├── assets/                     # 图标资源
├── date_data/                  # 按日期存储的抓取数据
├── keywords_library.json       # 关键词库文件
├── requirements.txt            # Python 依赖
└── .env                        # 环境变量配置
```

## 数据格式

### 抓取结果字段
| 字段 | 说明 |
|------|------|
| Keyword | 搜索关键词 |
| Name | 商家名称 |
| Phone | 电话号码 |
| Address | 地址 |
| Website | 网站 |
| Email | 提取的邮箱 |
| Industry | 行业 |
| Rating | 评分 |
| Reviews | 评论数 |
| Plus_Code | Plus Code |
| Google_URL | Google Maps 链接 |

## 常见问题

### Q: 无法访问 Google？
A: 请配置 HTTP 代理，在"同步设置"页面填写代理地址，格式如 `http://127.0.0.1:7890`

### Q: AI 关键词生成失败？
A: 检查豆包 API Key 和 Model Endpoint 是否正确配置，确保网络可以访问火山方舟 API

### Q: Google Sheets 同步失败？
A: 
1. 确认 `client_secret.json` 文件存在且正确
2. 检查 Google Sheets ID 是否正确
3. 确保已完成 OAuth 授权流程

### Q: 抓取结果为空？
A: 
1. 检查代理配置是否正确
2. 尝试降低同时抓取的关键词数量
3. 查看日志中的错误信息

## 注意事项

1. **合规使用**：请遵守 Google Maps 服务条款和当地法律法规
2. **频率控制**：建议合理控制抓取频率，避免对目标网站造成压力
3. **数据隐私**：妥善保管抓取的数据，遵守数据保护相关法规
4. **代理安全**：不要将代理配置提交到公共仓库

## 更新日志

### v1.1.0
- 新增 AI 关键词生成功能
- 支持关键词库管理
- 优化 GUI 界面和用户体验
- 新增数据预览功能
- 支持批量汇总同步

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎通过 GitHub Issues 反馈。

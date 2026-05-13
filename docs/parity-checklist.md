# 功能还原验收清单（Tauri + Python + WhatsApp）

> 来源：`docs/plans/2026-05-12-tauri-python-backend-refactor.md` 第 3 节矩阵。  
> 用法：每完成一条在 PR 中勾选，并附测试方式或截图。  
> **本机一键**：仓库根执行 `scripts\run_all.bat`（pytest + `npm run build` + `cargo check` + `npm run package`）；仅验证不打包可用 `scripts\smoke_test.bat`。

## P0 — 获客引擎

- [x] 行业 / 地理级联 + 手动地址（React + `/api/meta`；中文手动地址翻译接后续 AI）
- [x] 关键词输入、并发、开始 / 停止（React → `/api/scraper/start|stop`）
- [x] 实时日志、状态卡片（`EventSource /api/logs/stream` + 轮询 `/api/scraper/status`）
- [x] 底部：同步单个 CSV、汇总目录同步、测试代理、打开输出/下载（Tauri 选盘 + `reveal_path`；浏览器 CSV 用上传接口）
- [x] 数据预览（独立页 `/data`：`/api/data/downloads-sessions`、`root-csv`、`preview-csv`）

## P0 — 关键词库

- [x] 弹窗：搜索、全选当前列表、反选当前列表、导入 / 导出、删除选中、AI 生成并入库、应用到引擎

## P0 — AI 策略

- [x] 模板编辑与持久化（`/api/ai/prompt` → 项目根 `user_ai_prompt.txt`）
- [x] 豆包 / 火山关键词生成、超时与重试（`ai_generator`：`DOUBAO_*` 环境变量、connect/read 超时、失败回落预定义词库）

## P0 — 同步与 Google

- [x] 代理、Sheets ID、各 API Key、同步模式、冲突策略（表单 → `/api/config`）
- [x] 测试代理 / 连接（引擎底部 + `/api/system/test-proxy`）
- [x] OAuth、`token.json` 刷新（`/api/google/oauth/status|authorize|refresh` + 同步页按钮；`google_auth` 路径锚定仓库根）
- [x] 单文件同步、汇总同步、去重与合并（`/api/sync/file`、`upload-csv`、`aggregate` → 既有服务）

## P0 — 抓取

- [x] Playwright 反检测、滚动终止、邮箱爬取（`google_maps_scraper`：`playwright-stealth`、`smart_scroll` 高度停滞终止、`email_extractor`；深度调参属持续迭代）

## P0 — WhatsApp（集成版）

- [x] 一级入口打开模块（`/whatsapp` + iframe + 上游 JSON 轮询）
- [x] Node 服务随应用编排或显式启停（`B2B_SPAWN_WHATSAPP=1` 自动拉起；Tauri `whatsapp_service_start|stop`）
- [x] 扫码登录流程（依赖上游 Web UI；应用内 iframe + `/api/whatsapp/upstream-status` 展示 `status/qr`）
- [x] 与地图 CSV 联动（`/api/whatsapp/map-csv-phones` 号码预览；广播仍走 Node `POST /api/broadcast`，Python 侧已提供 `/api/whatsapp/broadcast` 代理）

## P1 — 系统

- [x] 窗口尺寸记忆、配置恢复（`tauri-plugin-window-state`）

## P2 — 视觉 / 其它

- [ ] Win11 毛玻璃 / 品牌动效
- [ ] `whatsapp_contacts.py` CLI 仍可从文档启动（可选）

## Phase F — 发布包（结项前须在 CI / VM 验证）

- [x] 桌面安装包：`tauri-app` 执行 `npm run package`（默认 **NSIS**，跳过 WiX MSI 以避免中文路径下 `light.exe` 失败）→ `target\release\bundle\nsis\` 与 `target\release\app.exe`
- [ ] PyInstaller `b2b-backend` sidecar + 资源清单（无本机 Python 的离线启动）
- [ ] 便携 Node + `third_party/whatsapp-service` 打入安装包
- [ ] Playwright 浏览器随包或首启下载策略落地

> 修复记录：数据预览页曾缺少 `path` 状态（`setPath` 未定义）导致进入路由即崩溃，已补全并增加预览 JSON 校验。

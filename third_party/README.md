# third_party

## whatsapp-service

来源：`E:\办公小程序\WhatsApp自动化库\whatsapp-web.js`（已剔除 `node_modules`、`.git`；**不应**提交 `.wwebjs_auth*` 会话目录）。

本地开发：

```bash
cd third_party/whatsapp-service
npm install
node web.js
```

默认端口见该项目的 `README.md`（一般为 `3003`）。地图后端的 `GET /api/whatsapp/health` 会探测该端口的 **`/api/status`**。

从 **Tauri** 启动时，若已在 `third_party/whatsapp-service` 执行过 `npm install`，可设置环境变量 **`B2B_SPAWN_WHATSAPP=1`**，由壳层尝试执行 `node web.js`（退出应用时会 `kill` 子进程）。

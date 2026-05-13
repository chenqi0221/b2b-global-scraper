# HTTP API 契约

- **OpenAPI JSON**：后端运行时访问 `http://127.0.0.1:8756/openapi.json`（端口与 `PY_BACKEND` 常量一致时可变）。
- **Swagger UI**：`http://127.0.0.1:8756/docs`
- **ReDoc**：`http://127.0.0.1:8756/redoc`

Tauri 内嵌页若需打开上述地址，请使用与 `vite` / `tauri` 一致的 `127.0.0.1` 主机名，避免与 CORS 白名单不一致。

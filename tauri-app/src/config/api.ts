/**
 * Python FastAPI 基址。开发默认 127.0.0.1:8756（与 Tauri setup 一致）。
 * 构建前可通过 `.env` / `.env.production` 覆盖 `VITE_API_BASE_URL`。
 */
export const API_BASE: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8756'

/** 与 `backend/schemas/common.py` 对齐的轻量类型 */

export type LocationModel = {
  country: string
  city: string
  district: string
}

export type ScrapeStatus = {
  is_running: boolean
  total_found: number
  email_found: number
  synced_count: number
  current_keyword: string | null
  output_dir: string | null
}

export type LogEventPayload = {
  id: number
  ts: number
  level: string
  message: string
}

export type GeoCityEntry = { en: string; zh: string }

export type GeoData = Record<
  string,
  Record<string, { en: string; cities: Record<string, GeoCityEntry[]> }>
>

/** `/api/meta/industries` → 与根目录 `data.INDUSTRY_KEYWORDS` 一致：行业名 → 英文关键词列表 */
export type IndustryMap = Record<string, string[]>

export type KeywordRow = { en: string; zh: string }

export type EnvSettingsView = {
  HTTP_PROXY: string
  GOOGLE_SHEETS_ID: string
  GEMINI_API_KEY: string
  DOUBAO_API_KEY: string
  DOUBAO_BASE_URL: string
  DOUBAO_MODEL_ENDPOINT: string
  SYNC_BY_DATE: boolean
  SYNC_CONFLICT_RESOLUTION: string
}

export type CsvPreview = {
  path: string
  columns: string[]
  rows: Record<string, string | number | boolean>[]
}

export type DownloadSession = { name: string; path: string }

export type RootCsvEntry = { name: string; path: string }

export type OauthStatus = {
  project_root: string
  client_secret_present: boolean
  token_present: boolean
  token_valid?: boolean | null
  token_expired?: boolean | null
  has_refresh_token?: boolean | null
  error?: string
}

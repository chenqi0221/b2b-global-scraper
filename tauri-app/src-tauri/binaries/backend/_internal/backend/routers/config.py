"""读写 `.env`（与 `gui` 同步设置一致），GET 时脱敏。"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.deps import get_config_service
from backend.schemas.settings import EnvSettingsSave, EnvSettingsView
from core.config_service import ConfigService

router = APIRouter()

_ENV_KEYS = [
    "HTTP_PROXY",
    "GOOGLE_SHEETS_ID",
    "GEMINI_API_KEY",
    "DOUBAO_API_KEY",
    "DOUBAO_BASE_URL",
    "DOUBAO_MODEL_ENDPOINT",
    "SYNC_BY_DATE",
    "SYNC_CONFLICT_RESOLUTION",
]

_MASK_KEYS = frozenset(
    {"GEMINI_API_KEY", "DOUBAO_API_KEY", "DOUBAO_MODEL_ENDPOINT", "GOOGLE_SHEETS_ID"}
)


def _mask(key: str, value: str) -> str:
    if not value:
        return ""
    if key in _MASK_KEYS and len(value) > 8:
        return f"{value[:4]}…{value[-4:]}"
    if key == "HTTP_PROXY" and "@" in value and "://" in value:
        return f"{value[:12]}…（已隐藏凭证）"
    return value


@router.get("/", response_model=EnvSettingsView)
def get_env_settings(svc: ConfigService = Depends(get_config_service)):
    raw = svc.load_config()
    by_date = str(raw.get("SYNC_BY_DATE", "False")).lower() == "true"
    view = EnvSettingsView(
        HTTP_PROXY=_mask("HTTP_PROXY", raw.get("HTTP_PROXY", "")),
        GOOGLE_SHEETS_ID=_mask("GOOGLE_SHEETS_ID", raw.get("GOOGLE_SHEETS_ID", "")),
        GEMINI_API_KEY=_mask("GEMINI_API_KEY", raw.get("GEMINI_API_KEY", "")),
        DOUBAO_API_KEY=_mask("DOUBAO_API_KEY", raw.get("DOUBAO_API_KEY", "")),
        DOUBAO_BASE_URL=raw.get("DOUBAO_BASE_URL", ""),
        DOUBAO_MODEL_ENDPOINT=_mask(
            "DOUBAO_MODEL_ENDPOINT", raw.get("DOUBAO_MODEL_ENDPOINT", "")
        ),
        SYNC_BY_DATE=by_date,
        SYNC_CONFLICT_RESOLUTION=raw.get("SYNC_CONFLICT_RESOLUTION", "keep_latest"),
    )
    return view


@router.post("/")
def save_env_settings(
    body: EnvSettingsSave,
    svc: ConfigService = Depends(get_config_service),
):
    existing = svc.load_config()
    patch = body.model_dump(exclude_none=True)

    def _is_masked_placeholder(v: object) -> bool:
        return isinstance(v, str) and "…" in v

    for k, v in patch.items():
        if _is_masked_placeholder(v):
            continue
        if isinstance(v, bool):
            existing[k] = str(v)
        else:
            existing[k] = str(v)
    for key in _ENV_KEYS:
        existing.setdefault(key, "")
    svc.save_config(existing)
    return {"ok": True}

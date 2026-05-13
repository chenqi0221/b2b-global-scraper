"""Google OAuth / token.json 状态与授权（委托 `google_auth.get_google_auth`）。"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException

from backend.path_utils import project_root
from backend.services.log_bus import log_bus

router = APIRouter()

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@router.get("/status")
def oauth_status():
    """不打开浏览器：检查凭证文件与 token 是否可解析、是否过期。"""
    root = project_root()
    client_secret = root / "client_secret.json"
    token_path = root / "token.json"
    out: dict = {
        "project_root": str(root),
        "client_secret_present": client_secret.is_file(),
        "token_present": token_path.is_file(),
        "token_valid": None,
        "token_expired": None,
        "has_refresh_token": None,
    }
    if not token_path.is_file():
        return out
    try:
        from google.oauth2.credentials import Credentials

        creds = Credentials.from_authorized_user_file(str(token_path), _SCOPES)
        out["token_valid"] = bool(creds.valid)
        out["token_expired"] = bool(creds.expired)
        out["has_refresh_token"] = bool(creds.refresh_token)
    except Exception as e:
        out["error"] = str(e)
    return out


@router.post("/authorize")
async def oauth_authorize():
    """
    在后台线程执行 `get_google_auth()`：若需重新授权会打开本机浏览器与临时 localhost 端口。
    请勿并发多次调用。
    """
    if not (project_root() / "client_secret.json").is_file():
        raise HTTPException(
            status_code=400,
            detail="缺少 client_secret.json，请从 Google Cloud Console 下载 OAuth 客户端 JSON 放到项目根目录并重命名。",
        )

    def run() -> None:
        log_bus.publish("开始 Google OAuth（可能弹出浏览器）…", "info")
        from google_auth import get_google_auth

        get_google_auth()
        log_bus.publish("Google OAuth 完成，token.json 已更新。", "info")

    await asyncio.to_thread(run)
    return {"ok": True}


@router.post("/refresh")
async def oauth_refresh():
    """仅尝试用 refresh_token 刷新；不会打开浏览器。若无 refresh 或失败则返回 ok=false。"""
    token_path = project_root() / "token.json"
    if not token_path.is_file():
        raise HTTPException(status_code=400, detail="缺少 token.json，请先完成授权")

    def run() -> bool:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        from config import HTTP_PROXY

        import requests

        session = requests.Session()
        if HTTP_PROXY:
            session.proxies = {"http": HTTP_PROXY, "https": HTTP_PROXY}
        google_request = Request(session=session)

        creds = Credentials.from_authorized_user_file(str(token_path), _SCOPES)
        if not creds.refresh_token:
            log_bus.publish("token 无 refresh_token，需要重新授权", "warning")
            return False
        if creds.valid:
            log_bus.publish("token 仍然有效，无需刷新", "info")
            return True
        try:
            creds.refresh(google_request)
        except Exception as e:
            log_bus.publish(f"刷新 token 失败: {e}", "warning")
            return False
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        log_bus.publish("token.json 已通过 refresh 更新", "info")
        return True

    ok = await asyncio.to_thread(run)
    return {"ok": ok}

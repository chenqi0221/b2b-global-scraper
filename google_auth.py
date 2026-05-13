from pathlib import Path

import requests

from config import HTTP_PROXY

_REPO = Path(__file__).resolve().parent


def get_google_auth():
    """获取 Google Auth 凭据 (共用函数)"""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    client_secret_path = str(_REPO / "client_secret.json")
    token_path = str(_REPO / "token.json")

    if not Path(client_secret_path).exists():
        raise FileNotFoundError(
            "根目录找不到 client_secret.json\n"
            "请从 Google Cloud Console 下载 OAuth 2.0 凭证文件并重命名为 client_secret.json\n"
            "文件路径: " + client_secret_path
        )

    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request, AuthorizedSession
    from google.oauth2.credentials import Credentials

    # 创建一个代理感知的 Session
    session = requests.Session()
    if HTTP_PROXY:
        session.proxies = {"http": HTTP_PROXY, "https": HTTP_PROXY}
    google_request = Request(session=session)

    creds = None
    if Path(token_path).is_file():
        try:
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                # 显式使用代理进行刷新
                creds.refresh(google_request)
            except Exception:
                # 如果刷新失败，重新授权
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_path, scopes
                )
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    # 返回凭据和带代理的授权 Session
    authed_session = AuthorizedSession(creds)
    if HTTP_PROXY:
        authed_session.proxies = {"http": HTTP_PROXY, "https": HTTP_PROXY}
    authed_session.timeout = 30  # 增加超时时间

    return creds, authed_session


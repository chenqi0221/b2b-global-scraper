import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def _get_app_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def _load_google_creds(scopes):
    """加载 Google 凭证：优先 OAuth token.json，其次 Service Account google_credentials.json。"""
    root = _get_app_dir()

    # 1. 尝试 OAuth token.json（用户授权方式）
    token_path = root / "token.json"
    if token_path.exists():
        from google.oauth2.credentials import Credentials as OAuthCredentials
        creds = OAuthCredentials.from_authorized_user_file(str(token_path), scopes)
        if creds.valid:
            return creds, "oauth"
        if creds.refresh_token:
            from google.auth.transport.requests import Request
            import requests
            from config import HTTP_PROXY
            session = requests.Session()
            if HTTP_PROXY:
                session.proxies = {"http": HTTP_PROXY, "https": HTTP_PROXY}
            google_request = Request(session=session)
            try:
                creds.refresh(google_request)
                with open(token_path, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
                return creds, "oauth"
            except Exception:
                pass

    # 2. 尝试 Service Account（服务账号方式）
    sa_candidates = [
        root / "google_credentials.json",
        Path.home() / ".config" / "google" / "credentials.json",
        Path.home() / "google_credentials.json",
    ]
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        sa_candidates.insert(0, Path(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]))

    for p in sa_candidates:
        if p.exists():
            from google.oauth2.service_account import Credentials as SACredentials
            return SACredentials.from_service_account_file(str(p), scopes=scopes), "service_account"

    raise FileNotFoundError(
        "未找到 Google 凭证。请完成 OAuth 授权（生成 token.json）"
        "或放置 google_credentials.json（Service Account）到项目目录。"
    )


async def upload_to_google_sheets(
    df,
    title: str,
    update_gui_callback,
    mode: str = "append",
    by_date: bool = False,
    conflict_resolution: str = "keep_latest",
):
    if df is None or df.empty:
        update_gui_callback("无数据可同步至云端")
        return False, None, None

    update_gui_callback("尝试连接 Google Sheets ...")
    try:
        import gspread

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds, cred_type = _load_google_creds(scope)
        gc = gspread.authorize(creds)
        update_gui_callback(f"已使用 {cred_type} 凭证授权")

        try:
            sheet = gc.open(title)
            update_gui_callback(f"已找到云端表格: {title}")
        except Exception:
            sheet = gc.create(title)
            sheet.share(None, perm_type="anyone", role="writer")
            update_gui_callback(f"已创建云端表格: {title}")

        ws = sheet.sheet1
        import pandas as pd

        existing_records = ws.get_all_records()
        existing_df = (
            pd.DataFrame(existing_records) if existing_records else pd.DataFrame()
        )

        if mode == "append" and not existing_df.empty:
            combined = pd.concat([existing_df, df], ignore_index=True)
            dedup_cols = [
                c for c in ["Name", "Phone", "Address"] if c in combined.columns
            ]
            if dedup_cols:
                combined = combined.drop_duplicates(subset=dedup_cols, keep="last")
                update_gui_callback(
                    f"云端去重: {len(existing_df)}条现存 + {len(df)}条新数据 → {len(combined)}条"
                )
            if dedup_cols:
                new_rows = pd.merge(
                    df, existing_df, on=dedup_cols, how="left", indicator=True
                )
                new_rows = new_rows[new_rows["_merge"] == "left_only"].drop(
                    "_merge", axis=1
                )
            else:
                new_rows = df.copy()
        else:
            combined = df.copy()
            new_rows = df.copy()

        combined = combined.fillna("")
        ws.clear()
        if not combined.empty:
            ws.update(
                [combined.columns.tolist()] + combined.values.tolist(),
                value_input_option="USER_ENTERED",
            )
        update_gui_callback(
            f"云端同步完成: {len(combined)}条总计, {len(new_rows)}条新增"
        )

        return True, combined, new_rows

    except FileNotFoundError:
        update_gui_callback("未配置 Google 凭证，跳过云端同步")
        return False, df, df
    except ModuleNotFoundError:
        update_gui_callback("未安装 gspread 库，跳过云端同步")
        return False, df, df
    except Exception as e:
        update_gui_callback(f"云端同步失败: {str(e)[:100]}")
        logger.warning(f"云端同步失败: {e}")
        return False, df, df
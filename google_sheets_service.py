import logging

logger = logging.getLogger(__name__)


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
        from google.oauth2.service_account import Credentials
        import os
        import json
        from pathlib import Path

        key_path = None
        candidates = [
            Path("google_credentials.json"),
            Path.home() / ".config" / "google" / "credentials.json",
            Path.home() / "google_credentials.json",
        ]
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            candidates.insert(0, Path(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]))

        for p in candidates:
            if p.exists():
                key_path = p
                break

        if key_path is None:
            raise FileNotFoundError("未找到 Google 凭证文件，请配置后重试")

        update_gui_callback(f"已找到凭证: {key_path.name}")

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(str(key_path), scopes=scope)
        gc = gspread.authorize(creds)

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
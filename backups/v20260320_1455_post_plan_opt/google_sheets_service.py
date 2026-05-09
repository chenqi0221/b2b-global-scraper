import asyncio
import logging
from urllib.parse import quote

import gspread
import pandas as pd

from google_auth import get_google_auth
from google_drive import get_or_create_drive_folder

logger = logging.getLogger(__name__)


async def upload_to_google_sheets(
    df: pd.DataFrame,
    title: str,
    update_gui_callback,
    folder_name: str = "langdeng",
    mode: str = "append",
):
    """将数据上传到 Google Sheets (支持覆盖和追加去重模式，默认追加去重)"""
    try:
        update_gui_callback(f"准备同步云端: {title}")
        creds, authed_session = get_google_auth()

        # 1. 定位云端文件夹
        update_gui_callback("正在定位云端文件夹...")
        folder_id = get_or_create_drive_folder(authed_session, folder_name)

        # 2. 在文件夹中查找同名文件
        update_gui_callback("正在检查云端文件...")
        query = (
            f"name = '{title}' and '{folder_id}' in parents "
            "and mimeType = 'application/vnd.google-apps.spreadsheet' "
            "and trashed = false"
        )
        search_url = f"https://www.googleapis.com/drive/v3/files?q={quote(query)}&fields=files(id, name)"
        search_resp = authed_session.get(search_url)
        search_resp.raise_for_status()
        files = search_resp.json().get("files", [])

        # gspread 注入带代理的 AuthorizedSession
        gc = gspread.Client(auth=creds, session=authed_session)

        if files:
            update_gui_callback(f"连接云端表格: {title}")
            sh = gc.open_by_key(files[0]["id"])
        else:
            update_gui_callback(f"创建新云端表格: {title}")
            sh = gc.create(title)
            file_id = sh.id

            # 移动到指定文件夹 (Drive v3 使用 PATCH 并带 query params)
            update_gui_callback(f"正在归类到 '{folder_name}' 文件夹...")
            move_url = (
                f"https://www.googleapis.com/drive/v3/files/{file_id}"
                f"?addParents={folder_id}&removeParents=root"
            )
            move_resp = authed_session.patch(move_url)
            move_resp.raise_for_status()

        # 3. 更新内容
        worksheet = sh.get_worksheet(0)
        final_df = df.copy()

        # 如果是追加模式且文件已存在，先读取云端数据进行合并去重
        if mode == "append" and files:
            try:
                update_gui_callback("正在读取云端已有数据进行合并去重...")

                # 获取所有值，包括表头
                existing_values = worksheet.get_all_values()
                if existing_values and len(existing_values) > 1:
                    existing_df = pd.DataFrame(
                        existing_values[1:], columns=existing_values[0]
                    )
                    # 合并本地和云端数据 (对齐列名)
                    combined_df = pd.concat(
                        [existing_df, final_df], ignore_index=True
                    )
                    # 全局去重：基于名称、电话、地址 (先检查列是否存在)
                    subset = [
                        c
                        for c in ["Name", "Phone", "Address"]
                        if c in combined_df.columns
                    ]
                    if subset:
                        final_df = combined_df.drop_duplicates(
                            subset=subset, keep="first"
                        )
                    else:
                        final_df = combined_df

                    update_gui_callback(
                        f"合并完成：云端新增 {len(final_df) - len(existing_df)} 条唯一记录"
                    )
                else:
                    update_gui_callback("云端表格为空，直接写入数据")
            except Exception as read_err:
                logger.warning(
                    f"读取云端数据失败，将回退到覆盖模式: {read_err}"
                )

        # 最终确保没有任何 NaN 值，防止 JSON 解析失败
        final_df = final_df.fillna("")

        # 转换为列表格式用于上传
        data = [final_df.columns.values.tolist()] + final_df.values.tolist()

        update_gui_callback("正在写入数据到云端...")

        # 指数退避重试逻辑，解决 500 内部错误
        max_retries = 3
        for attempt in range(max_retries):
            try:
                worksheet.clear()

                # 如果数据量非常大，Google API 容易报 500，分块上传更稳健
                chunk_size = 500  # 每 500 行分块上传
                if len(data) > chunk_size:
                    update_gui_callback(
                        f"数据量较大 ({len(data)}行)，采用分块上传模式..."
                    )
                    for i in range(0, len(data), chunk_size):
                        chunk = data[i : i + chunk_size]
                        range_start = f"A{i + 1}"
                        worksheet.update(range_start, chunk)
                else:
                    worksheet.update("A1", data)

                update_gui_callback("云端同步完成！")
                return True, final_df
            except Exception as update_err:
                if "500" in str(update_err) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    update_gui_callback(
                        f"云端繁忙 (500)，{wait_time}秒后进行第 {attempt + 2} 次重试..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise update_err

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Google Sheets 操作失败: {error_msg}")
        if "10060" in error_msg or "timeout" in error_msg.lower():
            update_gui_callback("同步失败: 网络连接超时 (30s)。")
        else:
            update_gui_callback(f"同步失败: {error_msg}")
        return False, None


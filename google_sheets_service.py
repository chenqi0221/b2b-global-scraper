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
    mode: str = "overwrite",
    by_date: bool = False,
    conflict_resolution: str = "keep_latest"
):
    """将数据上传到 Google Sheets 
    
    Args:
        df: 要上传的数据
        title: 表格名称
        update_gui_callback: GUI更新回调函数
        folder_name: 文件夹名称
        mode: 上传模式: "overwrite"(覆盖) 或 "append"(追加)
        by_date: 是否按日期汇总多工作表
        conflict_resolution: 冲突处理: "keep_latest"(保留最新) 或 "keep_cloud"(保留云端) 或 "keep_local"(保留本地)
    """
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
        final_df = df.copy()
        final_df = final_df.fillna("")
        header = final_df.columns.values.tolist()
        data_rows = final_df.values.tolist()

        # 根据模式处理数据
        if mode == "append" and files:
            # 真正的追加模式：读取云端数据，合并去重，然后上传
            update_gui_callback("正在读取云端已有数据进行合并去重...")
            worksheet = sh.get_worksheet(0)
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
                    # 根据冲突处理策略选择保留数据
                    if conflict_resolution == "keep_cloud":
                        # 保留云端数据
                        final_df = combined_df.drop_duplicates(
                            subset=subset, keep="first"
                        )
                    elif conflict_resolution == "keep_local":
                        # 保留本地数据
                        final_df = combined_df.drop_duplicates(
                            subset=subset, keep="last"
                        )
                    else:  # keep_latest
                        # 保留最新数据（默认）
                        final_df = combined_df.drop_duplicates(
                            subset=subset, keep="last"
                        )
                else:
                    final_df = combined_df

                update_gui_callback(
                    f"合并完成：云端新增 {len(final_df) - len(existing_df)} 条唯一记录"
                )
                
                # 重新生成数据格式
                final_df = final_df.fillna("")
                header = final_df.columns.values.tolist()
                data_rows = final_df.values.tolist()
            else:
                update_gui_callback("云端表格为空，直接写入数据")

        # 4. 写入数据到云端
        update_gui_callback("正在写入数据到云端...")
        
        # 确保总表（第一个工作表）存在并获取现有数据
        update_gui_callback("正在处理总表...")
        worksheets = sh.worksheets()
        
        # 获取或创建总表
        if len(worksheets) == 0:
            # 创建总表
            main_worksheet = sh.add_worksheet(title="总表", rows=1000, cols=len(header))
            existing_total_df = pd.DataFrame()
        else:
            # 使用第一个工作表作为总表
            main_worksheet = worksheets[0]
            # 确保总表名称正确
            if main_worksheet.title != "总表":
                main_worksheet.update_title("总表")
            
            # 读取总表现有数据
            existing_values = main_worksheet.get_all_values()
            if existing_values and len(existing_values) > 1:
                existing_total_df = pd.DataFrame(existing_values[1:], columns=existing_values[0])
            else:
                existing_total_df = pd.DataFrame()
        
        # 1. 数据去重处理：新数据先与总表数据合并去重
        update_gui_callback("正在进行数据去重...")
        
        # 合并新数据和总表数据
        if not existing_total_df.empty:
            # 总表已有数据，合并并去重
            # 确保新数据在后面，这样keep="last"会保留新数据
            combined_df = pd.concat([existing_total_df, final_df], ignore_index=True)
            
            # 基于名称、电话、地址去重
            subset = [c for c in ["Name", "Phone", "Address"] if c in combined_df.columns]
            
            if subset:
                # 根据冲突处理策略去重
                if conflict_resolution == "keep_cloud":
                    # 保留总表数据
                    final_total_df = combined_df.drop_duplicates(subset=subset, keep="first")
                elif conflict_resolution == "keep_local":
                    # 保留新数据
                    final_total_df = combined_df.drop_duplicates(subset=subset, keep="last")
                else:  # keep_latest
                    # 保留最新数据
                    final_total_df = combined_df.drop_duplicates(subset=subset, keep="last")
            else:
                final_total_df = combined_df
            
            # 计算新增数据量
            new_records_count = len(final_total_df) - len(existing_total_df)
            update_gui_callback(f"去重完成：新增 {new_records_count} 条唯一记录")
            
            # 确保新增记录数不为负数，可能是因为去重策略导致
            if new_records_count < 0:
                update_gui_callback(f"注意：由于去重策略，总记录数减少了 {-new_records_count} 条")
                new_records_count = max(0, new_records_count)
        else:
            # 总表为空，直接使用新数据
            final_total_df = final_df.copy()
            new_records_count = len(final_total_df)
            update_gui_callback(f"总表为空，新增 {new_records_count} 条记录")
        
        # 2. 更新总表：只添加去重后的新数据
        update_gui_callback("正在更新总表...")
        
        # 找出新增的数据：比较新数据和总表数据，找出真正新增的记录
        update_gui_callback("正在识别新增数据...")
        
        if not existing_total_df.empty:
            # 总表已有数据，找出新数据中真正新增的部分
            subset = [c for c in ["Name", "Phone", "Address"] if c in final_df.columns]
            
            if subset:
                # 使用新数据与总表数据比较，找出新增数据
                new_data_df = pd.merge(final_df, existing_total_df, on=subset, how='left', indicator=True)
                new_data_df = new_data_df[new_data_df['_merge'] == 'left_only'].drop('_merge', axis=1)
            else:
                # 没有合适的去重列，使用所有新数据
                new_data_df = final_df.copy()
        else:
            # 总表为空，所有新数据都是新增的
            new_data_df = final_df.copy()
        
        # 更新新增记录数
        new_records_count = len(new_data_df)
        update_gui_callback(f"已识别 {new_records_count} 条新增记录")
        
        # 处理新增数据
        new_data_df = new_data_df.fillna("")
        total_header = new_data_df.columns.values.tolist()
        
        if not existing_total_df.empty:
            # 总表已有数据，直接追加新增数据
            new_data_rows = new_data_df.values.tolist()
            
            if new_data_rows:
                # 使用append_rows方法，自动扩展工作表
                main_worksheet.append_rows(new_data_rows)
                
                update_gui_callback(f"总表已更新！新增 {len(new_data_rows)} 条记录")
            else:
                update_gui_callback("无新增数据，总表未更新")
        else:
            # 总表为空，写入完整数据（包含表头）
            total_data = [total_header] + new_data_df.values.tolist()
            
            # 清除总表并写入所有数据
            main_worksheet.clear()
            main_worksheet.update("A1", total_data)
            
            update_gui_callback(f"总表已创建！新增 {len(new_data_df)} 条记录")
        
        # 3. 如果按日期汇总，更新日期工作表
        if by_date:
            update_gui_callback("正在处理日期工作表...")
            
            # 获取当前日期
            current_date = pd.Timestamp.now().strftime("%Y-%m-%d")
            
            # 找出当天新增的数据
            if not existing_total_df.empty and new_records_count > 0:
                # 计算当天新增的数据
                subset = [c for c in ["Name", "Phone", "Address"] if c in final_total_df.columns]
                if subset:
                    # 找出新增数据
                    new_data_df = pd.merge(final_total_df, existing_total_df, on=subset, how='left', indicator=True)
                    new_data_df = new_data_df[new_data_df['_merge'] == 'left_only'].drop('_merge', axis=1)
                else:
                    # 没有合适的去重列，使用所有数据
                    new_data_df = final_total_df.copy()
            else:
                # 总表为空或没有新增数据，使用所有数据作为新增
                new_data_df = final_total_df.copy()
            
            # 处理日期工作表
            worksheet_titles = [ws.title for ws in worksheets]
            
            # 获取或创建日期工作表
            if current_date in worksheet_titles:
                # 更新现有工作表
                date_ws = sh.worksheet(current_date)
                update_gui_callback(f"正在更新工作表: {current_date}")
                
                # 读取日期工作表现有数据
                date_existing_values = date_ws.get_all_values()
                if date_existing_values and len(date_existing_values) > 1:
                    date_existing_df = pd.DataFrame(date_existing_values[1:], columns=date_existing_values[0])
                else:
                    date_existing_df = pd.DataFrame()
            else:
                # 创建新工作表
                update_gui_callback(f"正在创建新工作表: {current_date}")
                rows_needed = len(new_data_df) + 1
                cols_needed = len(total_header)
                date_ws = sh.add_worksheet(title=current_date, rows=rows_needed, cols=cols_needed)
                date_existing_df = pd.DataFrame()
            
            # 处理日期工作表数据
            if len(new_data_df) > 0:
                date_df = new_data_df.fillna("")
                date_data_rows = date_df.values.tolist()
                
                if not date_existing_df.empty:
                    # 日期工作表已有数据，使用append_rows追加数据
                    date_ws.append_rows(date_data_rows)
                    
                    update_gui_callback(f"已追加更新工作表: {current_date}，新增 {len(date_data_rows)} 条记录")
                else:
                    # 日期工作表为空，写入完整数据（包含表头）
                    date_data = [total_header] + date_data_rows
                    
                    # 清除工作表并写入所有数据
                    date_ws.clear()
                    date_ws.update("A1", date_data)
                    
                    update_gui_callback(f"已创建工作表: {current_date}，新增 {len(date_data_rows)} 条记录")
            else:
                # 当天没有新增数据，检查是否需要写入表头
                if not date_existing_df.empty:
                    update_gui_callback(f"无新增数据，工作表: {current_date} 未更新")
                else:
                    # 工作表为空，写入表头
                    date_ws.update("A1", [total_header])
                    update_gui_callback(f"当天没有新增数据，仅写入表头: {current_date}")
            
            update_gui_callback(f"云端同步完成！已更新总表和 {current_date} 工作表")
        else:
            # 不按日期汇总，仅更新总表
            update_gui_callback("云端同步完成！仅更新总表")

        # 确保返回的是完整的总表数据
        # 重新读取总表数据，确保本地文件与云端完全一致
        main_worksheet = worksheets[0]
        existing_values = main_worksheet.get_all_values()
        if existing_values and len(existing_values) > 1:
            final_total_df = pd.DataFrame(existing_values[1:], columns=existing_values[0])
            return True, final_total_df
        return True, final_df

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Google Sheets 操作失败: {error_msg}")
        if "10060" in error_msg or "timeout" in error_msg.lower():
            update_gui_callback("同步失败: 网络连接超时 (30s)。")
        else:
            update_gui_callback(f"同步失败: {error_msg}")
        return False, None


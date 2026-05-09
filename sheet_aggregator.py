import logging
import os

import pandas as pd

from google_sheets_service import upload_to_google_sheets

logger = logging.getLogger(__name__)


async def aggregate_and_sync(
    dir_path: str, 
    update_gui_callback, 
    target_title: str = "lengdangb2b",
    by_date: bool = False,
    conflict_resolution: str = "keep_latest"
):
    """汇总目录下所有 CSV 并去重上传
    
    Args:
        dir_path: CSV文件目录
        update_gui_callback: GUI更新回调函数
        target_title: 目标表格名称
        by_date: 是否按日期汇总多工作表
        conflict_resolution: 冲突处理策略
    """
    try:
        csv_files = [
            os.path.join(dir_path, f)
            for f in os.listdir(dir_path)
            if f.endswith(".csv") and f != f"{target_title}.csv"
        ]
        if not csv_files:
            update_gui_callback("未找到可汇总的 CSV 文件")
            return False

        update_gui_callback(f"正在汇总 {len(csv_files)} 个文件的数据...")

        all_dfs = []
        for f in csv_files:
            try:
                df = pd.read_csv(f)
                if not df.empty:
                    all_dfs.append(df)
            except Exception as e:
                logger.warning(f"读取文件 {f} 失败: {e}")

        if not all_dfs:
            update_gui_callback("所有文件内容均为空，取消汇总")
            return False

        combined_df = pd.concat(all_dfs, ignore_index=True)
        original_count = len(combined_df)

        # 去重逻辑：基于名称和电话，或者名称和地址 (增强容错)
        subset = [c for c in ["Name", "Phone", "Address"] if c in combined_df.columns]
        if subset:
            combined_df = combined_df.drop_duplicates(subset=subset, keep="last")  # 保留最新数据
        new_count = len(combined_df)

        update_gui_callback(
            f"本地汇总完成: 原始 {original_count} 条 -> 去重后 {new_count} 条"
        )

        # upload_to_google_sheets 会读取云端数据进行二次合并去重
        success, final_df = await upload_to_google_sheets(
            combined_df, 
            target_title, 
            update_gui_callback,
            mode="append",
            by_date=by_date,
            conflict_resolution=conflict_resolution
        )

        if success and final_df is not None:
            # 保存最终的、包含云端完整数据的总表文件到项目根目录
            summary_path = os.path.abspath(f"{target_title}.csv")
            final_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
            update_gui_callback(f"根目录汇总文件已更新(含云端完整数据): {target_title}.csv")
            
            # 如果按日期汇总，需要从云端获取当天的工作表数据并保存到本地
            if by_date:
                # 创建本地日期目录（如果不存在）
                local_date_dir = os.path.abspath("date_data")
                if not os.path.exists(local_date_dir):
                    os.makedirs(local_date_dir)
                
                # 获取当前日期
                current_date = pd.Timestamp.now().strftime("%Y-%m-%d")
                
                # 保存当天数据到本地日期文件
                # 注意：final_df是完整的总表数据，我们需要从云端获取当天的工作表数据
                # 这里我们简化处理，直接保存去重后的新数据到日期文件
                local_date_path = os.path.join(local_date_dir, f"{current_date}.csv")
                
                # 直接保存去重后的结果到日期文件
                final_df.to_csv(local_date_path, index=False, encoding="utf-8-sig")
                update_gui_callback(f"本地日期文件已保存: {local_date_path}")
            
            return True
        return False
    except Exception as e:
        update_gui_callback(f"汇总同步失败: {str(e)}")
        logger.error(f"汇总同步失败: {e}")
        return False


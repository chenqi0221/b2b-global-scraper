import logging
import os
import sys
from pathlib import Path

import pandas as pd

from google_sheets_service import upload_to_google_sheets
from utils.reporter import as_status_reporter

logger = logging.getLogger(__name__)


def _get_app_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def _local_aggregate(
    dir_path: str,
    target_title: str,
    update_gui_callback=None,
):
    status_cb = as_status_reporter(update_gui_callback)
    local_dir = _get_app_dir()
    total_path = local_dir / f"{target_title}_total.csv"

    csv_files = sorted([
        os.path.join(dir_path, f)
        for f in os.listdir(dir_path)
        if f.endswith(".csv") and f != f"{target_title}_total.csv"
    ])
    if not csv_files:
        status_cb("未找到可汇总的 CSV 文件")
        return None, None

    status_cb(f"正在读取 {len(csv_files)} 个文件...")

    all_dfs = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            if not df.empty:
                all_dfs.append(df)
        except Exception as e:
            logger.warning(f"读取文件 {f} 失败: {e}")

    if not all_dfs:
        update_gui_callback("所有文件内容均为空")
        return None, None

    new_data = pd.concat(all_dfs, ignore_index=True)
    new_data = new_data.fillna("")

    existing_df = None
    if total_path.exists():
        try:
            existing_df = pd.read_csv(total_path)
            existing_df = existing_df.fillna("")
        except Exception:
            status_cb("本地总表读取失败，将创建新总表")

    dedup_cols = [c for c in ["Name", "Phone", "Address"] if c in new_data.columns]

    if existing_df is not None and not existing_df.empty:
        combined = pd.concat([existing_df, new_data], ignore_index=True)
        original_count = len(combined)
        if dedup_cols:
            combined = combined.drop_duplicates(subset=dedup_cols, keep="last")
        deduped_count = len(combined)
        new_count = deduped_count - len(existing_df)
        status_cb(
            f"本地汇总完成: 合并 {original_count} 条 -> 去重后 {deduped_count} 条 (新增 {new_count} 条)"
        )

        # 计算真正新增的记录：用去重后的总表减去已有数据
        if dedup_cols:
            merged = pd.merge(
                combined, existing_df,
                on=dedup_cols, how="left", indicator=True
            )
            new_records = merged[merged["_merge"] == "left_only"].drop("_merge", axis=1)
        else:
            new_records = combined.iloc[len(existing_df):].copy()
    else:
        combined = new_data.copy()
        if dedup_cols:
            combined = combined.drop_duplicates(subset=dedup_cols, keep="last")
        deduped_count = len(combined)
        status_cb(f"本地汇总完成: 首次创建总表，共 {deduped_count} 条")
        new_records = combined.copy()

    combined.to_csv(str(total_path), index=False, encoding="utf-8-sig")
    status_cb(f"本地总表已更新: {total_path.name} ({deduped_count} 条)")

    if len(new_records) > 0:
        new_dir = local_dir / "new_records"
        new_dir.mkdir(exist_ok=True)
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d_%H%M%S")
        new_path = new_dir / f"{target_title}_new_{timestamp}.csv"
        new_records.to_csv(str(new_path), index=False, encoding="utf-8-sig")
        status_cb(f"新增数据已保存: {new_path.name} ({len(new_records)} 条)")
    else:
        status_cb("本次无新增数据")

    return combined, new_records


async def aggregate_and_sync(
    dir_path: str,
    update_gui_callback=None,
    target_title: str = "lengdangb2b",
    by_date: bool = False,
    conflict_resolution: str = "keep_latest",
):
    status_cb = as_status_reporter(update_gui_callback)
    try:
        total_df, new_df = _local_aggregate(dir_path, target_title, status_cb)

        if total_df is None:
            return False

        try:
            success, cloud_final, cloud_new = await upload_to_google_sheets(
                total_df,
                target_title,
                status_cb,
                mode="append",
                by_date=by_date,
                conflict_resolution=conflict_resolution,
            )
            if success:
                status_cb("云端同步完成")
            else:
                status_cb("云端同步失败（网络问题），本地数据已安全保存")
        except Exception as e:
            status_cb(f"无法连接 Google Drive ({str(e)[:80]})，本地数据已安全保存")

        return True

    except Exception as e:
        status_cb(f"汇总同步失败: {str(e)}")
        logger.error(f"汇总同步失败: {e}")
        return False
import csv
import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)


def export_results_csv_xlsx(
    results,
    base_filename: str,
    output_dir: str,
    fieldnames,
    update_gui_callback,
):
    """将抓取结果导出为 CSV + XLSX。

    行为保持与旧版一致：
    - CSV 使用 `utf-8-sig`
    - CSV 使用 `extrasaction='ignore'`
    - XLSX 通过 reindex(columns=fieldnames) 保证列齐全
    """
    csv_path = os.path.join(output_dir, f"{base_filename}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    try:
        excel_path = os.path.join(output_dir, f"{base_filename}.xlsx")
        df = pd.DataFrame(results).reindex(columns=fieldnames)
        df.to_excel(excel_path, index=False)
        update_gui_callback(f"本地保存成功: {base_filename}.xlsx")
    except Exception as ex:
        logger.error(f"Excel 保存失败: {str(ex)}")
        update_gui_callback(f"本地 Excel 保存失败: {str(ex)}")


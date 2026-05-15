import csv
import json
import os
import sys
from pathlib import Path


def _keywords_path() -> Path:
    """返回 keywords.json 的存储路径。

    优先级：
    1. B2B_REPO_ROOT 环境变量（Tauri 启动时设置）
    2. PyInstaller 模式：exe 实际所在目录
    3. 开发模式：项目根目录（与 __file__ 同级）
    """
    # 1. Tauri 设置的环境变量
    env_root = os.environ.get("B2B_REPO_ROOT")
    if env_root:
        base = Path(env_root)
        if base.exists():
            return base / "keywords.json"

    # 2. PyInstaller 模式
    if getattr(sys, "frozen", False):
        if hasattr(sys, '_MEIPASS'):
            base = Path(sys._MEIPASS).parent
        else:
            base = Path(sys.executable).parent
        return base / "keywords.json"

    # 3. 开发模式
    base = Path(__file__).resolve().parent
    return base / "keywords.json"


def load_keywords():
    kp = _keywords_path()
    if not kp.exists():
        return []
    try:
        with open(kp, "r", encoding="utf-8") as f:
            rows = json.load(f)
        if isinstance(rows, list):
            return rows
        return []
    except Exception:
        return []


def save_keywords(pairs):
    rows = load_keywords()
    existing_keys = {(r.get("en", ""), r.get("zh", "")) for r in rows}
    existing_en = {r.get("en", "") for r in rows}
    added = 0
    for en, zh in pairs:
        en_s = (en or "").strip()
        zh_s = (zh or "").strip()
        if not en_s:
            continue
        key = (en_s, zh_s)
        if key not in existing_keys and en_s not in existing_en:
            rows.append({"en": en_s, "zh": zh_s, "checked": True})
            existing_keys.add(key)
            existing_en.add(en_s)
            added += 1
    try:
        with open(_keywords_path(), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        return True, added
    except Exception as e:
        return False, str(e)


def delete_keywords(pairs):
    rows = load_keywords()
    target = {(e.strip(), z.strip()) for e, z in pairs}
    before = len(rows)
    rows = [
        r
        for r in rows
        if (r.get("en", "").strip(), r.get("zh", "").strip()) not in target
    ]
    removed = before - len(rows)
    try:
        with open(_keywords_path(), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        return True, f"已删除 {removed} 条"
    except Exception as e:
        return False, str(e)


def import_keywords(file_path):
    try:
        pairs = []
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                return False, "文件为空"
            col_map = {}
            for i, h in enumerate(header):
                h_lower = (h or "").strip().lower()
                if h_lower in ("en", "english", "keyword"):
                    col_map["en"] = i
                elif h_lower in ("zh", "chinese", "name", "名称", "中文", "关键词"):
                    col_map["zh"] = i
            if "en" not in col_map:
                idx = (col_map.get("zh", 0) + 1) if "zh" in col_map else 0
                col_map["en"] = idx % 2
                if "zh" not in col_map:
                    col_map["zh"] = 1
            for row in reader:
                if not row or all((c or "").strip() == "" for c in row):
                    continue
                en = row[col_map["en"]].strip() if col_map["en"] < len(row) else ""
                zh = (
                    row[col_map["zh"]].strip()
                    if col_map.get("zh", 0) < len(row)
                    else ""
                )
                if en:
                    pairs.append((en, zh))
        if not pairs:
            return False, "文件中无可导入的关键词"
        ok, added = save_keywords(pairs)
        if ok:
            return True, f"成功导入 {added} 条关键词"
        return False, f"保存失败: {added}"
    except Exception as e:
        return False, str(e)


def export_keywords(file_path):
    try:
        rows = load_keywords()
        if not rows:
            return False, "无关键词可导出"
        with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["en", "zh"])
            for r in rows:
                writer.writerow([r.get("en", ""), r.get("zh", "")])
        return True, f"已导出 {len(rows)} 条"
    except Exception as e:
        return False, str(e)
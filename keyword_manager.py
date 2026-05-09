import json
import os
import pandas as pd

LIBRARY_FILE = "keywords_library.json"

def load_keywords():
    """从本地 JSON 文件加载所有保存的关键词及其翻译"""
    if not os.path.exists(LIBRARY_FILE):
        return []
    try:
        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_keywords(new_keywords_with_translation):
    """
    保存关键词并自动去重。
    格式: list of [english, chinese]
    """
    existing = load_keywords()
    # 使用英文词作为 key 来去重
    existing_map = {item[0].lower(): item for item in existing}
    
    added_count = 0
    for eng, chn in new_keywords_with_translation:
        eng_lower = eng.lower()
        if eng_lower not in existing_map:
            # 如果没有中文翻译，尝试生成一个简单的翻译
            if not chn:
                try:
                    # 简单的翻译逻辑：如果关键词包含中文，则使用中文作为翻译
                    if any('\u4e00' <= char <= '\u9fff' for char in eng):
                        chn = eng
                    # 或者使用简单的关键词拆分和翻译
                    elif "ware" in eng.lower():
                        chn += "用品 "
                    elif "distributor" in eng.lower():
                        chn += "分销商"
                    elif "supplier" in eng.lower():
                        chn += "供应商"
                    elif "showroom" in eng.lower():
                        chn += "展厅"
                    elif "trading" in eng.lower():
                        chn += "贸易公司"
                    elif "contractor" in eng.lower():
                        chn += "承包商"
                    elif "importer" in eng.lower():
                        chn += "进口商"
                    elif "wholesale" in eng.lower():
                        chn += "批发商"
                    elif "retailer" in eng.lower():
                        chn += "零售商"
                    elif "gallery" in eng.lower():
                        chn += "画廊"
                    elif "center" in eng.lower() or "centre" in eng.lower():
                        chn += "中心"
                    elif "studio" in eng.lower():
                        chn += "工作室"
                    elif "collection" in eng.lower():
                        chn += "系列"
                    elif "dealer" in eng.lower():
                        chn += "经销商"
                    elif "solution" in eng.lower():
                        chn += "解决方案"
                    elif "material" in eng.lower():
                        chn += "材料"
                    
                    # 添加与浴室相关的翻译
                    if "bath" in eng.lower() or "vanity" in eng.lower():
                        chn = "浴室" + chn
                    
                    # 去除多余的空格
                    chn = chn.strip()
                except Exception as e:
                    print(f"生成简单翻译时出错: {e}")
            
            existing_map[eng_lower] = [eng, chn]
            added_count += 1
            
    # 转回列表保存
    updated_list = list(existing_map.values())
    
    try:
        with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_list, f, ensure_ascii=False, indent=2)
        return True, added_count
    except Exception as e:
        print(f"保存关键词库失败: {e}")
        return False, 0

def export_keywords(file_path):
    """
    导出关键词库到 CSV 文件
    """
    keywords = load_keywords()
    if not keywords:
        return False, "关键词库为空"
    
    try:
        df = pd.DataFrame(keywords, columns=["English Keyword", "Chinese Translation"])
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        return True, f"成功导出 {len(keywords)} 个关键词"
    except Exception as e:
        return False, f"导出失败: {str(e)}"

def import_keywords(file_path):
    """
    从 CSV 文件导入关键词库
    """
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return False, "文件内容为空"
        
        # 验证文件格式
        if "English Keyword" not in df.columns or "Chinese Translation" not in df.columns:
            return False, "文件格式不正确，缺少必要的列"
        
        # 转换为列表格式
        new_keywords = []
        for _, row in df.iterrows():
            eng = str(row["English Keyword"]).strip()
            chn = str(row["Chinese Translation"]).strip() if pd.notna(row["Chinese Translation"]) else ""
            if eng:
                new_keywords.append([eng, chn])
        
        if not new_keywords:
            return False, "没有有效的关键词可以导入"
        
        # 保存到关键词库
        success, added = save_keywords(new_keywords)
        if success:
            return True, f"成功导入 {len(new_keywords)} 个关键词，其中 {added} 个为新增关键词"
        else:
            return False, "保存关键词库失败"
    except Exception as e:
        return False, f"导入失败: {str(e)}"

def delete_keywords(keywords_to_delete):
    """
    删除指定的关键词
    :param keywords_to_delete: 要删除的关键词列表，格式为 [(english1, chinese1), (english2, chinese2), ...]
    :return: (success, message)
    """
    existing = load_keywords()
    if not existing:
        return True, "关键词库为空"
    
    # 创建现有关键词的集合（使用英文词的小写作为唯一标识）
    existing_map = {item[0].lower(): item for item in existing}
    
    # 统计删除的关键词数量
    deleted_count = 0
    
    # 删除指定的关键词
    for eng, chn in keywords_to_delete:
        eng_lower = eng.lower()
        if eng_lower in existing_map:
            del existing_map[eng_lower]
            deleted_count += 1
    
    # 转回列表保存
    updated_list = list(existing_map.values())
    
    try:
        with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_list, f, ensure_ascii=False, indent=2)
        return True, f"成功删除 {deleted_count} 个关键词"
    except Exception as e:
        return False, f"删除关键词失败: {str(e)}"

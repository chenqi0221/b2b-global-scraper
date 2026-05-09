# test_keyword_management.py
# 测试关键词管理功能

import json
import os
from keyword_manager import save_keywords, load_keywords

# 配置
LIBRARY_FILE = "keywords_library.json"

def test_keyword_management():
    """测试关键词管理功能"""
    print("开始测试关键词管理功能...")
    
    # 1. 保存一些测试关键词
    test_keywords = [
        ("Sanitary Ware Supplier", "卫浴用品供应商"),
        ("Bathroom Vanity Wholesaler", "浴室柜批发商"),
        ("New Keyword 1", ""),  # 没有中文翻译，应该自动生成
        ("New Keyword 2", ""),  # 没有中文翻译，应该自动生成
        ("Sanitary Ware Supplier", "重复的卫浴供应商")  # 重复的，应该被去重
    ]
    
    print("\n1. 保存测试关键词...")
    success, added = save_keywords(test_keywords)
    print(f"   保存结果: {'成功' if success else '失败'}")
    print(f"   新增关键词数量: {added}")
    
    # 2. 加载关键词库
    print("\n2. 加载关键词库...")
    keywords = load_keywords()
    print(f"   关键词库总数: {len(keywords)}")
    
    # 3. 显示关键词库内容
    print("\n3. 关键词库内容:")
    for i, (eng, chn) in enumerate(keywords[:10]):  # 只显示前10个
        print(f"   {i+1}. {eng} -> {chn}")
    
    if len(keywords) > 10:
        print(f"   ... 还有 {len(keywords) - 10} 个关键词")
    
    # 4. 检查是否有中文翻译
    print("\n4. 检查中文翻译:")
    no_translation = [kw for kw in keywords if not kw[1]]
    if no_translation:
        print(f"   没有中文翻译的关键词 ({len(no_translation)} 个):")
        for eng, chn in no_translation:
            print(f"   - {eng}")
    else:
        print("   ✓ 所有关键词都有中文翻译！")
    
    # 5. 测试去重功能
    print("\n5. 测试去重功能:")
    test_duplicate = [
        ("Sanitary Ware Supplier", "重复测试"),
        ("Bathroom Vanity Wholesaler", "重复测试")
    ]
    success, added = save_keywords(test_duplicate)
    print(f"   保存重复关键词结果: {'成功' if success else '失败'}")
    print(f"   新增关键词数量: {added} (应该为0，因为是重复的)")
    
    # 6. 再次加载检查数量
    keywords_after = load_keywords()
    print(f"   去重后关键词总数: {len(keywords_after)} (应该和之前一样)")
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    test_keyword_management()
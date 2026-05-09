# test_ai_prompt.py
import sys
import os

# 确保能找到同级目录下的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_generator import get_keywords_from_ai

def run_local_test():
    """
    本地模拟测试代码
    模拟输入“浴室柜”，生成 7 个关键词并输出，验证 Prompt 效果。
    """
    print("="*50)
    print("🚀 开始 AI 关键词生成本地测试")
    print("="*50)
    
    seed = "浴室柜"
    num = 7
    
    print(f"🔹 种子词: {seed}")
    print(f"🔹 期望生成数量: {num}")
    print("\n⏳ 正在调用 AI (豆包/Doubao API)...")
    
    try:
        # 调用核心生成函数
        keywords = get_keywords_from_ai(seed, num)
        
        if keywords:
            print("\n✅ 生成结果如下:")
            print("-" * 20)
            for idx, kw in enumerate(keywords, 1):
                print(f"{idx}. {kw}")
            print("-" * 20)
            print(f"\n💡 结果验证: 共生成 {len(keywords)} 个关键词。")
            print("👉 检查是否包含：批发商(Wholesale)、设计师(Design)、工程商(Contractor)等不同维度的英文词汇。")
        else:
            print("\n❌ 未能获取到结果。")
            print("💡 可能原因：")
            print("1. ai_generator.py 中的 API_KEY 或 MODEL_ENDPOINT 未正确填写。")
            print("2. 代理网络无法连接到火山引擎 (Volcengine) API 域名。")
            
    except Exception as e:
        print(f"\n💥 测试运行异常: {str(e)}")

    print("\n" + "="*50)

if __name__ == "__main__":
    run_local_test()

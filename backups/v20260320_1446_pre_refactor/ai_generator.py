import os
from openai import OpenAI
from data import AI_KEYWORD_PROMPT

# 核心配置：豆包 (Doubao) API
# 请在此处填写你的 API Key 和 Base URL
API_KEY = "78ba710b-48d2-4d68-934e-532b2011e956"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_ENDPOINT = "ep-20260320111206-rhp29" # 填写你的推理端点 ID

def get_keywords_from_ai(seed_word, num=7):
    """
    使用豆包 API 根据种子词生成 B2B 获客关键词
    """
    import httpx
    # 使用 trust_env=False 强制绕过系统代理，直接连接国内 API 服务器
    http_client = httpx.Client(trust_env=False)
    
    client = OpenAI(
        api_key=API_KEY.strip(), # 确保移除可能的空格或换行
        base_url=BASE_URL,
        http_client=http_client
    )

    system_prompt = AI_KEYWORD_PROMPT.replace("[N]", str(num))
    user_prompt = f"Seed Product (Chinese): {seed_word}"

    try:
        completion = client.chat.completions.create(
            model=MODEL_ENDPOINT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        content = completion.choices[0].message.content.strip()
        # 处理可能的空行或格式问题
        keywords = [line.strip() for line in content.split('\n') if line.strip()]
        return keywords[:num]
    except Exception as e:
        print(f"AI 生成出错: {str(e)}")
        return []

if __name__ == "__main__":
    # 测试代码
    test_keywords = get_keywords_from_ai("不锈钢浴室柜", 5)
    print("生成结果:")
    for kw in test_keywords:
        print(kw)

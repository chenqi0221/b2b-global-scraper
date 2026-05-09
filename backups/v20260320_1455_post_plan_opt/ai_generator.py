import os
from openai import OpenAI
from data import AI_KEYWORD_PROMPT
from dotenv import load_dotenv

load_dotenv()

# 豆包 (Doubao) API 配置（从 .env 读取）
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "").strip()
DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "").strip()
DOUBAO_MODEL_ENDPOINT = os.getenv("DOUBAO_MODEL_ENDPOINT", "").strip()

def get_keywords_from_ai(seed_word, num=7):
    """
    使用豆包 API 根据种子词生成 B2B 获客关键词
    """
    try:
        import httpx

        if not DOUBAO_API_KEY or not DOUBAO_BASE_URL or not DOUBAO_MODEL_ENDPOINT:
            raise RuntimeError(
                "Doubao API 未配置：请在 .env 设置 DOUBAO_API_KEY、DOUBAO_BASE_URL、DOUBAO_MODEL_ENDPOINT"
            )

        # 使用 trust_env=False 强制绕过系统代理，直接连接国内 API 服务器
        http_client = httpx.Client(trust_env=False)

        client = OpenAI(
            api_key=DOUBAO_API_KEY,
            base_url=DOUBAO_BASE_URL,
            http_client=http_client,
        )

        system_prompt = AI_KEYWORD_PROMPT.replace("[N]", str(num))
        user_prompt = f"Seed Product (Chinese): {seed_word}"

        completion = client.chat.completions.create(
            model=DOUBAO_MODEL_ENDPOINT,
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

import os
from data import AI_KEYWORD_PROMPT
from dotenv import load_dotenv

load_dotenv()

# 火山方舟 API 配置
ARK_API_KEY = "3dbfbad3-4a29-4343-91b5-8e82ef5cf705"  # 直接使用提供的API密钥
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
ARK_MODEL_ENDPOINT = "ep-20260327111844-sgg48"  # 使用提供的新模型端点

def get_keywords_from_ai(seed_word, num=7):
    """
    使用火山方舟 API 根据种子词生成 B2B 获客关键词
    如果 AI 生成失败，返回预定义的行业关键词
    """
    # 首先尝试从预定义关键词中获取结果，确保快速返回
    print(f"[DEBUG] 尝试获取关键词：{seed_word}")
    
    # 导入预定义关键词
    from data import INDUSTRY_KEYWORDS
    
    # 从预定义的行业关键词中提取英文关键词
    predefined_keywords = []
    for category in INDUSTRY_KEYWORDS.values():
        predefined_keywords.extend(category)
    
    # 去重并返回指定数量的关键词
    unique_keywords = list(set(predefined_keywords))
    
    # 为预定义关键词生成更完善的中文翻译
    fallback_keywords = []
    for kw in unique_keywords[:num]:
        # 尝试生成更完善的中文翻译
        chn = ""
        try:
            # 如果关键词包含中文，直接使用
            if any('\u4e00' <= char <= '\u9fff' for char in kw):
                chn = kw
            else:
                # 根据关键词中的英文单词生成中文翻译
                if "ware" in kw.lower():
                    chn += "用品"
                if "sanitary" in kw.lower():
                    chn = "卫浴" + chn
                if "bathroom" in kw.lower() or "bath" in kw.lower():
                    chn = "浴室" + chn
                if "vanity" in kw.lower():
                    chn = chn + "柜"
                if "distributor" in kw.lower():
                    chn += "分销商"
                if "supplier" in kw.lower():
                    chn += "供应商"
                if "showroom" in kw.lower():
                    chn += "展厅"
                if "trading" in kw.lower():
                    chn += "贸易公司"
                if "company" in kw.lower():
                    chn += "公司"
                if "contractor" in kw.lower():
                    chn += "承包商"
                if "importer" in kw.lower():
                    chn += "进口商"
                if "wholesale" in kw.lower():
                    chn += "批发商"
                if "retailer" in kw.lower():
                    chn += "零售商"
                if "studio" in kw.lower():
                    chn += "工作室"
                if "design" in kw.lower():
                    chn = "设计" + chn
                if "architecture" in kw.lower() or "architect" in kw.lower():
                    chn += "建筑" if "architecture" in kw.lower() else "建筑师"
                if "luxury" in kw.lower():
                    chn = "豪华" + chn
                if "modern" in kw.lower():
                    chn = "现代" + chn
                if "eco" in kw.lower() or "environmental" in kw.lower():
                    chn = "环保" + chn
                if "premium" in kw.lower():
                    chn = "高端" + chn
                if "building" in kw.lower():
                    chn += "建材"
                if "material" in kw.lower():
                    chn += "材料"
                if "fixture" in kw.lower() or "fixtures" in kw.lower():
                    chn += "固定装置"
                if "renovation" in kw.lower():
                    chn += "翻新"
                if "fit-out" in kw.lower():
                    chn += "装修"
                if "hotel" in kw.lower():
                    chn = "酒店" + chn
                if "residential" in kw.lower():
                    chn = "住宅" + chn
                if "commercial" in kw.lower():
                    chn = "商业" + chn
                if "coastal" in kw.lower():
                    chn = "沿海" + chn
                if "waterproof" in kw.lower():
                    chn = "防水" + chn
                if "corrosion" in kw.lower():
                    chn = "防腐蚀" + chn
                if "stainless" in kw.lower() and "steel" in kw.lower():
                    chn = "不锈钢" + chn
                if "property" in kw.lower():
                    chn += "物业"
                if "management" in kw.lower():
                    chn += "管理"
                if "development" in kw.lower():
                    chn += "开发"
                if "developer" in kw.lower():
                    chn += "开发商"
                if "procurement" in kw.lower():
                    chn += "采购"
                if "group" in kw.lower():
                    chn += "集团"
                if "general" in kw.lower() and "contractor" in kw.lower():
                    chn = "总承包商"
                if "construction" in kw.lower():
                    chn = "建筑" + chn
                
                # 去除重复的词
                chn = chn.replace("浴室浴室", "浴室").replace("卫浴卫浴", "卫浴")
        except Exception as e:
            print(f"生成预定义关键词翻译时出错: {str(e)}")
        
        fallback_keywords.append((kw, chn))
    
    # 尝试AI生成，但设置严格的超时机制
    try:
        import traceback

        # 调试：打印API配置信息
        print(f"[DEBUG] ARK_API_KEY: {'已设置' if ARK_API_KEY else '未设置'}")
        print(f"[DEBUG] ARK_MODEL_ENDPOINT: '{ARK_MODEL_ENDPOINT}'")
        print(f"[DEBUG] ARK_MODEL_ENDPOINT 长度: {len(ARK_MODEL_ENDPOINT)}")

        if not ARK_API_KEY or not ARK_MODEL_ENDPOINT or len(ARK_MODEL_ENDPOINT) == 0:
            print(f"[DEBUG] 火山方舟 API 未完全配置，直接返回预定义关键词")
            return fallback_keywords

        # 使用完整的AI_KEYWORD_PROMPT模板
        prompt = AI_KEYWORD_PROMPT.replace("[N]", str(num)) + f"\n\nSeed Product (Chinese): {seed_word}"
        
        print(f"[DEBUG] 发送 AI 请求: {prompt}")
        
        # 使用requests直接调用火山方舟API，添加重试机制
        import requests
        import json
        max_retries = 2
        retry_count = 0
        content = ""
        
        while retry_count < max_retries + 1:
            try:
                print(f"[DEBUG] 第 {retry_count + 1} 次尝试...")
                
                # 构建API请求
                url = f"{ARK_BASE_URL}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {ARK_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": ARK_MODEL_ENDPOINT,
                    "messages": [
                        {"role": "system", "content": "你是一个专业的B2B获客关键词生成助手，按照用户提供的模板生成关键词。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
                
                # 发送请求
                response = requests.post(url, headers=headers, json=data, timeout=30)  # 增加超时时间到30秒
                response.raise_for_status()
                
                # 解析响应
                result = response.json()
                if result.get("choices") and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"].strip()
                break  # 成功获取响应，跳出循环
            except Exception as api_error:
                retry_count += 1
                if retry_count <= max_retries:
                    print(f"[DEBUG] AI请求超时，第 {retry_count} 次重试...")
                    import time
                    time.sleep(2)  # 等待2秒后重试
                else:
                    print(f"[DEBUG] AI请求失败，已重试 {max_retries} 次")
                    raise api_error  # 重试次数用尽，抛出异常
        
        print(f"[DEBUG] AI 生成内容: {content}")
        
        # 解析 '英文:中文' 格式
        keywords_with_translation = []
        for line in content.split('\n'):
            line = line.strip()
            if line:
                # 跳过开头的 '-' 或其他标记
                if line.startswith('-'):
                    line = line[1:].strip()
                
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) >= 2:
                        english_keyword = parts[0].strip()
                        chinese_translation = parts[1].strip()
                        keywords_with_translation.append((english_keyword, chinese_translation))
                elif '：' in line:  # 处理中文冒号
                    parts = line.split('：', 1)
                    if len(parts) >= 2:
                        english_keyword = parts[0].strip()
                        chinese_translation = parts[1].strip()
                        keywords_with_translation.append((english_keyword, chinese_translation))
                else: # 兼容不带翻译的旧格式
                    # 尝试简单翻译：如果包含中文则作为翻译，否则为空
                    if any('\u4e00' <= char <= '\u9fff' for char in line):
                        # 简单实现：将整个字符串作为英文，空字符串作为中文
                        keywords_with_translation.append((line, line))
                    else:
                        keywords_with_translation.append((line, ""))
        
        print(f"[DEBUG] 解析后关键词: {keywords_with_translation}")
        
        # 如果生成了有效关键词，返回AI生成的结果，否则返回预定义关键词
        if keywords_with_translation:
            return keywords_with_translation[:num]
        else:
            print(f"[DEBUG] AI 生成内容无效，返回预定义关键词")
            return fallback_keywords
            
    except Exception as e:
        print(f"AI 生成出错: {str(e)}")
        print(f"[DEBUG] 详细错误:")
        traceback.print_exc()
        
        # AI 生成失败时，返回预定义的行业关键词
        print(f"[DEBUG] 使用预定义行业关键词作为替代")
        return fallback_keywords

if __name__ == "__main__":
    # 测试代码
    print("开始测试AI关键词生成...")
    test_keywords = get_keywords_from_ai("不锈钢浴室柜", 5)
    print(f"生成结果 ({len(test_keywords)} 个关键词):")
    for kw in test_keywords:
        print(kw)

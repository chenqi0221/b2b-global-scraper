"""
scraper_core.py - 提供 test_connection 和 generate_keywords_with_ai 函数

这个模块是为了兼容旧代码中 `from scraper_core import test_connection` 和
`from scraper_core import generate_keywords_with_ai` 的导入方式。
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Callable, List, Tuple

import httpx

from config import HTTP_PROXY

logger = logging.getLogger(__name__)


async def test_connection(
    update_gui_callback: Callable[[str], None] = None,
    timeout: int = 15,
) -> bool:
    """测试代理连通性（访问 Google）。"""
    msg = update_gui_callback or (lambda x: None)

    proxies = None
    if HTTP_PROXY:
        proxies = HTTP_PROXY
        msg(f"使用代理: {HTTP_PROXY}")

    msg("正在测试 Google 连通性...")
    try:
        async with httpx.AsyncClient(proxy=proxies, timeout=timeout, follow_redirects=True) as client:
            resp = await client.get("https://www.google.com")
            if resp.status_code == 200:
                msg("Google 连接成功！")
                return True
            else:
                msg(f"Google 返回状态码: {resp.status_code}")
                return False
    except Exception as e:
        msg(f"连接失败: {str(e)[:100]}")
        logger.warning(f"test_connection error: {e}")
        return False


async def generate_keywords_with_ai(
    seed_word: str,
    num: int = 7,
) -> List[Tuple[str, str]]:
    """基于种子词生成相关关键词（英文 + 中文）。

    优先使用豆包 Ark API，失败时回退到规则生成。
    """
    seed = seed_word.strip()
    if not seed:
        return []

    from config import DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_MODEL_ENDPOINT

    if DOUBAO_API_KEY and DOUBAO_MODEL_ENDPOINT:
        try:
            return await _generate_with_doubao(seed, num)
        except Exception as e:
            logger.warning(f"豆包 AI 生成失败，回退规则生成: {e}")

    return _generate_by_rules(seed, num)


def _generate_by_rules(seed: str, num: int) -> List[Tuple[str, str]]:
    import unicodedata

    suffixes = [
        ("supplier", "供应商"),
        ("manufacturer", "制造商"),
        ("wholesaler", "批发商"),
        ("factory", "工厂"),
        ("exporter", "出口商"),
        ("distributor", "经销商"),
        ("dealer", "经销商"),
        ("agent", "代理商"),
        ("trader", "贸易商"),
        ("vendor", "卖家"),
        ("wholesale supplier", "批发供应商"),
        ("manufacturer factory", "制造工厂"),
        ("products supplier", "产品供应商"),
        ("OEM manufacturer", "OEM制造商"),
        ("manufacturer and exporter", "制造商出口商"),
        ("direct factory", "直销工厂"),
        ("company", "公司"),
        ("wholesale", "批发"),
    ]

    # 判断种子词是否含中文
    has_cjk = any(
        unicodedata.category(c).startswith("Lo") and ord(c) > 0x2000
        for c in seed
    )

    if has_cjk:
        # 中文种子词：英文前缀用通用 B2B 关键词
        en_prefixes = [
            "b2b",
            "product",
            "industrial",
            "commercial",
        ]
    else:
        en_prefixes = [
            seed,
            seed + " products",
            "custom " + seed,
            "high quality " + seed,
        ]

    results: List[Tuple[str, str]] = []
    i = 0
    for pf in en_prefixes:
        for en_suffix, zh_suffix in suffixes:
            if i >= num:
                break
            en = f"{pf} {en_suffix}"
            zh = f"{seed} {zh_suffix}"
            if en not in [r[0] for r in results]:
                results.append((en, zh))
                i += 1
        if i >= num:
            break

    return results


def _project_root() -> Path:
    env_root = os.environ.get("B2B_REPO_ROOT")
    if env_root:
        p = Path(env_root)
        if p.exists():
            return p
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def _load_ai_prompt_template() -> str:
    # 1. 用户自定义提示词（AI策略页保存的）
    user_prompt_file = _project_root() / "user_ai_prompt.txt"
    if user_prompt_file.is_file():
        try:
            t = user_prompt_file.read_text(encoding="utf-8")
            if t.strip():
                logger.info("using user_ai_prompt.txt as prompt template")
                return t.strip()
        except OSError:
            pass

    # 2. data.py 中的默认提示词
    try:
        from data import AI_KEYWORD_PROMPT
        if AI_KEYWORD_PROMPT and AI_KEYWORD_PROMPT.strip():
            logger.info("using AI_KEYWORD_PROMPT from data.py")
            return AI_KEYWORD_PROMPT.strip()
    except (ImportError, AttributeError):
        pass

    # 3. 硬编码兜底
    logger.info("using built-in fallback prompt")
    return (
        "你是一个 B2B 外贸获客专家。用户要在 Google Maps 上搜索 {seed} 行业的潜在客户。\n"
        "请生成恰好 {num} 个英文搜索关键词及其对应的中文翻译。\n\n"
        "格式要求：严格按照 JSON 数组输出，每个元素是 [英文关键词, 中文翻译]，不要输出任何其他文字。\n"
        '格式示例：[["bathroom cabinet supplier", "浴室柜供应商"], ["bathroom vanity manufacturer", "浴室柜制造商"]]\n\n'
        "关键词要求：\n"
        "1. 每个关键词是英文名词短语，用于 Google Maps 搜索商家，必须包含产品词+业务类型\n"
        "2. 业务类型多样化：supplier, manufacturer, wholesale, factory, exporter, distributor, dealer, agent, trader, vendor 等\n"
        "3. 产品词要有变化，比如同义词、上下位词、相关品类词\n"
        "4. 可加入产地词如 China, Guangdong 等提升搜索精度（可选）\n"
        "5. 中文翻译要准确简洁\n"
        "6. 必须恰好 {num} 个，不多不少\n\n"
        "请立即输出恰好 {num} 个结果的 JSON 数组："
    )


async def _generate_with_doubao(seed: str, num: int) -> List[Tuple[str, str]]:
    from config import DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_MODEL_ENDPOINT

    base_url = DOUBAO_BASE_URL or "https://ark.cn-beijing.volces.com/api/v3"

    try:
        from openai import AsyncOpenAI
    except ImportError:
        raise RuntimeError("openai 库未安装，无法使用豆包 AI 生成")

    if HTTP_PROXY:
        os.environ["HTTP_PROXY"] = HTTP_PROXY
        os.environ["HTTPS_PROXY"] = HTTP_PROXY

    client = AsyncOpenAI(
        api_key=DOUBAO_API_KEY,
        base_url=base_url,
        timeout=30.0,
        max_retries=2,
    )

    template = _load_ai_prompt_template()
    prompt = template.format(seed=seed, num=num)

    response = await client.chat.completions.create(
        model=DOUBAO_MODEL_ENDPOINT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=4096,
    )

    content = response.choices[0].message.content or ""
    logger.info(f"Doubao raw response: {content[:200]}")

    pairs = _parse_ai_json_response(content, num)
    if pairs:
        return pairs

    raise RuntimeError("AI 返回内容无法解析为关键词列表")


def _parse_ai_json_response(content: str, max_num: int) -> List[Tuple[str, str]]:
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        while lines and lines[0].startswith("```"):
            lines.pop(0)
        while lines and lines[-1].startswith("```"):
            lines.pop()
        content = "\n".join(lines)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("[")
        end = content.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(content[start:end + 1])
            except json.JSONDecodeError:
                return []
        else:
            return []

    if not isinstance(parsed, list):
        return []

    results: List[Tuple[str, str]] = []
    for item in parsed:
        if isinstance(item, list) and len(item) >= 2:
            en = str(item[0]).strip()
            zh = str(item[1]).strip()
            if en and zh:
                results.append((en, zh))

    return results

import logging
import re
from urllib.parse import urljoin, urlparse

import httpx

from config import HTTP_PROXY
from utils.reporter import as_status_reporter

logger = logging.getLogger(__name__)

# 用于查找邮箱的正则表达式
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# 任务级熔断状态：失败域名缓存 + 请求计数器
_FAILED_DOMAINS: set[str] = set()
_REQUEST_COUNT = 0
_MAX_REQUESTS_PER_RUN = 200


def reset_email_extractor_state(max_requests_per_run: int = 200):
    """重置邮箱提取器状态，通常在每次新抓取任务开始时调用。"""
    global _FAILED_DOMAINS, _REQUEST_COUNT, _MAX_REQUESTS_PER_RUN
    _FAILED_DOMAINS.clear()
    _REQUEST_COUNT = 0
    _MAX_REQUESTS_PER_RUN = max_requests_per_run


def _decode_obfuscated_emails(text: str) -> str:
    """解码常见反爬虫邮箱混淆写法（大小写不敏感替换常见形式）。"""
    replacements = [
        ("[at]", "@"), ("[AT]", "@"),
        ("(at)", "@"), ("(AT)", "@"),
        (" AT ", "@"), (" at ", "@"),
        ("&#64;", "@"), ("&#46;", "."),
        ("[dot]", "."), ("[DOT]", "."),
        ("(dot)", "."), ("(DOT)", "."),
        (" DOT ", "."), (" dot ", "."),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    # 去掉 @ 和 . 两侧的多余空格，使混淆写法能匹配标准邮箱正则
    text = re.sub(r"\s*@\s*", "@", text)
    text = re.sub(r"\s*\.\s*", ".", text)
    return text


async def find_emails_on_website(
    url: str,
    update_gui_callback=None,
    max_pages_per_site: int = 2,
) -> str:
    """
    访问官网并尝试寻找电子邮箱。

    说明：
    - 采用 httpx 直连网络（如配置了代理，会通过 HTTP_PROXY 传入）。
    - 只返回前 3 个结果的逗号拼接字符串，保持与旧代码行为一致。
    - 增加域名失败缓存与全局请求上限，避免无浏览器/网络异常时流量风暴。
    - 首页无邮箱时尝试 Contact/About 页面，支持多选择器降级。
    """
    global _REQUEST_COUNT

    status_cb = as_status_reporter(update_gui_callback)

    if not url or not url.startswith("http"):
        return ""

    domain = urlparse(url).netloc.lower()
    if domain in _FAILED_DOMAINS:
        return ""
    if _REQUEST_COUNT >= _MAX_REQUESTS_PER_RUN:
        status_cb(f"[跳过] 已达到本次任务邮箱请求上限: {domain}", "warning")
        return ""

    try:
        status_cb(f"正在尝试从官网获取邮箱: {url}")

        proxies = HTTP_PROXY if HTTP_PROXY else None
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            verify=False,
            proxy=proxies,
        ) as client:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            }

            pages_fetched = 0
            seen_urls: set[str] = set()
            emails = set()

            async def fetch_and_extract(target_url: str) -> bool:
                nonlocal pages_fetched
                if pages_fetched >= max_pages_per_site:
                    return False
                if target_url in seen_urls:
                    return False
                seen_urls.add(target_url)
                _REQUEST_COUNT += 1
                pages_fetched += 1
                resp = await client.get(target_url, headers=headers)
                if resp.status_code != 200:
                    return False
                html = _decode_obfuscated_emails(resp.text)
                emails.update(re.findall(EMAIL_REGEX, html))
                return True

            # 1) 抓取首页
            await fetch_and_extract(url)

            # 2) 如果主页没找到，尝试页面中的 Contact/About/Support 链接
            if not emails:
                home_resp = await client.get(url, headers=headers)
                if home_resp.status_code == 200:
                    html = _decode_obfuscated_emails(home_resp.text)
                    contact_patterns = ["contact", "about", "reach", "info", "support", "career"]
                    links = re.findall(r'href=["\']([^"\']+)["\']', html)
                    for link in links:
                        if any(p in link.lower() for p in contact_patterns):
                            contact_link = link if link.startswith("http") else urljoin(url, link)
                            await fetch_and_extract(contact_link)
                            if emails:
                                break

            # 3) 如果仍未找到，尝试常见固定路径
            if not emails:
                for path in ["/contact", "/contact-us", "/about", "/about-us"]:
                    if pages_fetched >= max_pages_per_site:
                        break
                    await fetch_and_extract(urljoin(url, path))
                    if emails:
                        break

            # 4) 过滤掉明显无意义的地址
            blocked = {
                ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf",
                "sentry.io", "wix.com", "example.com", "yourname",
            }
            filtered_emails = [
                e for e in emails if not any(x in e.lower() for x in blocked)
            ]

            if filtered_emails:
                return ", ".join(list(filtered_emails)[:3])

    except Exception as e:
        logger.debug(f"访问官网 {url} 失败: {str(e)}")

    _FAILED_DOMAINS.add(domain)
    return ""


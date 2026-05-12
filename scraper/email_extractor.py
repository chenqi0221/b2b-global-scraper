import logging
import re
from urllib.parse import urljoin

import httpx

from config import HTTP_PROXY

logger = logging.getLogger(__name__)

# 用于查找邮箱的正则表达式
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"


async def find_emails_on_website(url: str, update_gui_callback) -> str:
    """
    访问官网并尝试寻找电子邮箱。

    说明：
    - 采用 httpx 直连网络（如配置了代理，会通过 HTTP_PROXY 传入）。
    - 只返回前 3 个结果的逗号拼接字符串，保持与旧代码行为一致。
    """
    if not url or not url.startswith("http"):
        return ""

    try:
        update_gui_callback(f"正在尝试从官网获取邮箱: {url}")

        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            verify=False,
            proxy=HTTP_PROXY,
        ) as client:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            }

            # 1) 抓取页面
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return ""

            html = response.text
            emails = set(re.findall(EMAIL_REGEX, html))

            # 2) 如果主页没找到，再尝试找 Contact/About/Support 链接
            if not emails:
                contact_patterns = ["contact", "about", "reach", "info", "support"]
                links = re.findall(r'href=["\']([^"\']+)["\']', html)
                contact_link = None

                for link in links:
                    if any(p in link.lower() for p in contact_patterns):
                        contact_link = link if link.startswith("http") else urljoin(url, link)
                        break

                if contact_link:
                    contact_resp = await client.get(contact_link, headers=headers)
                    if contact_resp.status_code == 200:
                        emails.update(re.findall(EMAIL_REGEX, contact_resp.text))

            # 3) 过滤掉明显无意义的地址
            blocked = {
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                "sentry.io",
                "wix.com",
                "example.com",
                "yourname",
            }
            filtered_emails = [
                e for e in emails if not any(x in e.lower() for x in blocked)
            ]

            if filtered_emails:
                return ", ".join(list(filtered_emails)[:3])

    except Exception as e:
        logger.debug(f"访问官网 {url} 失败: {str(e)}")

    return ""


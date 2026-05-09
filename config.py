import os
from dotenv import load_dotenv

# Load .env early so subsequent imports get consistent configuration.
load_dotenv()

raw_proxy = os.getenv("HTTP_PROXY")

# Format proxy string to include protocol prefix if user only provides host:port.
if raw_proxy:
    if not raw_proxy.startswith(("http://", "https://", "socks5://")):
        HTTP_PROXY = f"http://{raw_proxy}"
    else:
        HTTP_PROXY = raw_proxy
else:
    HTTP_PROXY = None

# Ensure third-party libs that respect environment variables also see proxy config.
if HTTP_PROXY:
    os.environ["HTTP_PROXY"] = HTTP_PROXY
    os.environ["HTTPS_PROXY"] = HTTP_PROXY
    os.environ["http_proxy"] = HTTP_PROXY
    os.environ["https_proxy"] = HTTP_PROXY
    os.environ["all_proxy"] = HTTP_PROXY


import os
import httpx
from dotenv import load_dotenv

print("Testing AI keyword generation step by step...")

# Step 1: Load environment variables
print("\nStep 1: Loading environment variables...")
load_dotenv()

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "").strip()
DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "").strip()
DOUBAO_MODEL_ENDPOINT = os.getenv("DOUBAO_MODEL_ENDPOINT", "").strip()

print(f"API Key: {'Set' if DOUBAO_API_KEY else 'Not set'}")
print(f"Base URL: {DOUBAO_BASE_URL}")
print(f"Model Endpoint: {DOUBAO_MODEL_ENDPOINT}")

# Step 2: Test HTTP client
print("\nStep 2: Testing HTTP client...")
try:
    http_client = httpx.Client(trust_env=False)
    print("HTTP client created successfully")
    
    # Test a simple GET request
    response = http_client.get("https://www.baidu.com", timeout=5)
    print(f"HTTP GET test: {response.status_code}")
    http_client.close()
except Exception as e:
    print(f"HTTP client error: {str(e)}")
    import traceback
    traceback.print_exc()

# Step 3: Test OpenAI client initialization
print("\nStep 3: Testing OpenAI client initialization...")
try:
    from openai import OpenAI
    
    http_client = httpx.Client(trust_env=False)
    
    client = OpenAI(
        api_key=DOUBAO_API_KEY,
        base_url=DOUBAO_BASE_URL,
        http_client=http_client,
    )
    print("OpenAI client initialized successfully")
    http_client.close()
except Exception as e:
    print(f"OpenAI client error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\nTest completed.")
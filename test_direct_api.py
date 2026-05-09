import os
import httpx
import json
from dotenv import load_dotenv

print("Testing direct API call...")

# Load environment variables
load_dotenv()

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "").strip()
DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "").strip()
DOUBAO_MODEL_ENDPOINT = os.getenv("DOUBAO_MODEL_ENDPOINT", "").strip()

print(f"API Key: {'Set' if DOUBAO_API_KEY else 'Not set'}")
print(f"Base URL: {DOUBAO_BASE_URL}")
print(f"Model Endpoint: {DOUBAO_MODEL_ENDPOINT}")

# Prepare API request
api_url = f"{DOUBAO_BASE_URL}/chat/completions"
headers = {
    "Authorization": f"Bearer {DOUBAO_API_KEY}",
    "Content-Type": "application/json"
}

# Simple prompt for testing
payload = {
    "model": DOUBAO_MODEL_ENDPOINT,
    "messages": [
        {
            "role": "system",
            "content": "你是一个关键词生成器，生成5个关于产品的B2B关键词，格式为'英文关键词: 中文翻译'，每行一个。"
        },
        {
            "role": "user",
            "content": "产品: 浴室柜"
        }
    ],
    "temperature": 0.7
}

print(f"\nAPI URL: {api_url}")
print(f"Headers: {headers}")
print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

# Make direct HTTP request
try:
    http_client = httpx.Client(trust_env=False)
    print("\nSending API request...")
    
    response = http_client.post(
        api_url,
        headers=headers,
        json=payload,
        timeout=10
    )
    
    print(f"\nResponse status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    # Try to parse JSON response
    try:
        response_json = response.json()
        print(f"\nResponse JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        
        # Extract generated content if available
        if response_json.get("choices"):
            content = response_json["choices"][0]["message"]["content"]
            print(f"\nGenerated content: {content}")
            
            # Parse keywords
            keywords = []
            for line in content.split('\n'):
                line = line.strip()
                if line and ':' in line:
                    parts = line.split(':', 1)
                    keywords.append((parts[0].strip(), parts[1].strip()))
            
            print(f"\nParsed keywords: {keywords}")
            
    except json.JSONDecodeError as e:
        print(f"\nFailed to parse JSON response: {str(e)}")
        print(f"Response text: {response.text}")
    
except httpx.TimeoutException:
    print("\nERROR: Request timed out after 10 seconds")
except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    http_client.close()

print("\nTest completed.")
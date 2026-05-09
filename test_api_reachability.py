import os
import httpx
from dotenv import load_dotenv

print("Testing API reachability...")

# Load environment variables
load_dotenv()

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "").strip()
DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "").strip()
DOUBAO_MODEL_ENDPOINT = os.getenv("DOUBAO_MODEL_ENDPOINT", "").strip()

print(f"Base URL: {DOUBAO_BASE_URL}")

# Test 1: Check if the base URL is reachable
try:
    http_client = httpx.Client(trust_env=False)
    
    # First, test DNS resolution and basic connectivity
    print("Test 1: Testing base URL connectivity...")
    try:
        response = http_client.get(DOUBAO_BASE_URL, timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
    except httpx.TimeoutException:
        print("  Timeout: Base URL is not responding within 5 seconds")
    except Exception as e:
        print(f"  Error: {str(e)}")
    
    # Test 2: Check if the API endpoint exists
    print(f"\nTest 2: Testing API endpoint...")
    try:
        api_url = f"{DOUBAO_BASE_URL}/chat/completions"
        print(f"  API URL: {api_url}")
        
        # Create a minimal request to test the API
        payload = {
            "model": DOUBAO_MODEL_ENDPOINT,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {DOUBAO_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = http_client.post(api_url, json=payload, headers=headers, timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
    except httpx.TimeoutException:
        print("  Timeout: API endpoint is not responding within 5 seconds")
    except Exception as e:
        print(f"  Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
finally:
    http_client.close()
    print("\nTest completed.")
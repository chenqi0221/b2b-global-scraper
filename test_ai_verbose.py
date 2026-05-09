import os
import httpx
from dotenv import load_dotenv
import traceback

print("Testing AI keyword generation with verbose output...")

# Step 1: Load environment variables
print("\nStep 1: Loading environment variables...")
load_dotenv()

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "").strip()
DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "").strip()
DOUBAO_MODEL_ENDPOINT = os.getenv("DOUBAO_MODEL_ENDPOINT", "").strip()

print(f"API Key: {'Set' if DOUBAO_API_KEY else 'Not set'}")
print(f"Base URL: {DOUBAO_BASE_URL}")
print(f"Model Endpoint: {DOUBAO_MODEL_ENDPOINT}")

# Step 2: Import OpenAI and test client
print("\nStep 2: Testing OpenAI client...")
try:
    from openai import OpenAI
    print(f"OpenAI library imported successfully")
    
    # Create HTTP client
    http_client = httpx.Client(trust_env=False)
    print(f"HTTP client created")
    
    # Create OpenAI client
    client = OpenAI(
        api_key=DOUBAO_API_KEY,
        base_url=DOUBAO_BASE_URL,
        http_client=http_client,
    )
    print(f"OpenAI client created")
    
    # Step 3: Test the actual API call
    print("\nStep 3: Testing API call...")
    
    # Define prompts
    system_prompt = "You are a helpful assistant."
    user_prompt = "Hello, can you help me generate some keywords for '浴室柜'?"
    
    print(f"Sending API request...")
    
    # Make API call with shorter timeout
    completion = client.chat.completions.create(
        model=DOUBAO_MODEL_ENDPOINT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        timeout=10,
    )
    
    print(f"API response received")
    print(f"Response type: {type(completion)}")
    print(f"Choices length: {len(completion.choices)}")
    
    if completion.choices:
        content = completion.choices[0].message.content
        print(f"Generated content: {content}")
    
    http_client.close()
    print("\nTest completed successfully!")
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    print("Traceback:")
    traceback.print_exc()
    try:
        http_client.close()
    except:
        pass
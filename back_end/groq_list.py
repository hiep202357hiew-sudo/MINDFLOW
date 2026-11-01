import httpx

API_KEY = "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"  # Thay bằng key của bạn

url = "https://api.groq.com/openai/v1/models"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

try:
    response = httpx.get(url, headers=headers, timeout=30.0)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        models = response.json()["data"]
        print(f"\n✅ Found {len(models)} models:\n")
        for model in models:
            print(f"  - {model['id']}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {str(e)}")
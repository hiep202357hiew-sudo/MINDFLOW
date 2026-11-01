import httpx
import json

# Thay bằng API Key của bạn
API_KEY ="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"
MODEL = "qwen/qwen3.8-27b"

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": "Xin chào"}
    ],
    "temperature": 0.7
}

print(f"Testing with model: {MODEL}")
print(f"API Key: {API_KEY[:10]}...")
print("-" * 50)

try:
    response = httpx.post(url, headers=headers, json=data, timeout=30.0)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS!")
        print(f"AI Reply: {result['choices'][0]['message']['content']}")
    else:
        print("\n❌ ERROR!")
        print(f"Error details: {response.text}")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {str(e)}")
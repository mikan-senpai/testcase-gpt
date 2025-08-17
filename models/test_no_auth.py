import requests

print("Testing HuggingFace API endpoints without authentication...")

# Test public endpoints that don't require auth
test_urls = [
    "https://huggingface.co/api/models/gpt2",
    "https://api-inference.huggingface.co/models/gpt2",
    "https://huggingface.co/api/whoami"
]

for url in test_urls:
    try:
        response = requests.get(url, timeout=10)
        print(f"\n{url}")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Endpoint is working")
        elif response.status_code == 401:
            print("🔐 Endpoint requires authentication (this is expected)")
        else:
            print(f"❌ Unexpected status: {response.text[:100]}")

    except Exception as e:
        print(f"❌ Connection error: {e}")

print(f"\n" + "="*50)
print("RECOMMENDATION:")
print("1. Go to https://huggingface.co/settings/tokens")
print("2. Make sure you're logged into the correct account")
print("3. Create a NEW token with 'Read' permissions")
print("4. Copy the ENTIRE token (starts with hf_)")
print("5. Update your .env file")
print("6. Wait 2-3 minutes for the token to activate")
print("="*50)

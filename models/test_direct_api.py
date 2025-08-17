import os
import requests
from dotenv import load_dotenv

load_dotenv("../.env")
api_key = os.environ.get("HF_TOKEN")

print(f"Testing token: {api_key}")

# Try different endpoints to see which one works
endpoints_to_test = [
    ("Whoami", "https://huggingface.co/api/whoami"),
    ("Model Info", "https://api-inference.huggingface.co/models/gpt2"),
    ("Simple Inference", "https://api-inference.huggingface.co/models/gpt2")
]

headers = {"Authorization": f"Bearer {api_key}"}

for name, url in endpoints_to_test:
    try:
        if name == "Simple Inference":
            # POST request for inference
            response = requests.post(url, headers=headers, json={"inputs": "Hello"})
        else:
            # GET request for info
            response = requests.get(url, headers=headers)

        print(f"\n{name}: Status {response.status_code}")

        if response.status_code == 200:
            print(f"✅ {name} SUCCESS!")
            if name == "Simple Inference":
                print(f"Response: {response.json()}")
            break
        else:
            print(f"❌ {name} failed: {response.text[:100]}")

    except Exception as e:
        print(f"❌ {name} error: {e}")

# If all fail, let's check if the token format is correct
print(f"\nToken analysis:")
print(f"Length: {len(api_key)}")
print(f"Starts with 'hf_': {api_key.startswith('hf_')}")
print(f"Contains only valid characters: {api_key.replace('hf_', '').replace('_', '').isalnum()}")

print(f"\nIf all tests fail, the token might be:")
print(f"1. Invalid or expired")
print(f"2. Created with wrong permissions")
print(f"3. From a different HuggingFace account")
print(f"4. Not yet activated (sometimes takes a few minutes)")

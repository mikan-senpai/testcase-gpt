import os
import requests
from dotenv import load_dotenv

load_dotenv("../.env")
api_key = os.environ.get("HF_TOKEN")

print(f"Token: {api_key}")

# Test with whoami endpoint to validate token
headers = {"Authorization": f"Bearer {api_key}"}

try:
    response = requests.get("https://huggingface.co/api/whoami", headers=headers)
    print(f"Whoami status: {response.status_code}")

    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ Token is valid! User: {user_info.get('name', 'Unknown')}")

        # Now try a simple model inference
        print("\nTesting model inference...")
        model_response = requests.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers=headers,
            json={"inputs": "The capital of France is"}
        )

        print(f"Model inference status: {model_response.status_code}")
        if model_response.status_code == 200:
            print("✅ Model inference working!")
            print("Response:", model_response.json())
        else:
            print(f"❌ Model inference failed: {model_response.text}")

    else:
        print(f"❌ Token validation failed: {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")

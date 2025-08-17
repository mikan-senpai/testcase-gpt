import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv("../.env")

# Test your HF token
api_key = os.environ.get("HF_TOKEN")

print(f"Testing token: {api_key[:10]}...")

# Test token validity
headers = {"Authorization": f"Bearer {api_key}"}

try:
    # Test with a simple public model
    response = requests.get(
        "https://api-inference.huggingface.co/models/gpt2",
        headers=headers
    )

    print(f"Token validation status: {response.status_code}")

    if response.status_code == 200:
        print("✓ Token is valid!")

        # Try a simple inference
        payload = {"inputs": "Hello, my name is"}
        inference_response = requests.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers=headers,
            json=payload
        )

        print(f"Inference status: {inference_response.status_code}")
        if inference_response.status_code == 200:
            print("✓ Inference API working!")
            print("Response:", inference_response.json())
        else:
            print("✗ Inference failed:", inference_response.text)

    else:
        print("✗ Token invalid or expired")
        print("Response:", response.text)
        print("\nTo fix this:")
        print("1. Go to https://huggingface.co/settings/tokens")
        print("2. Create a new token with 'Read' permissions")
        print("3. Update your .env file with the new token")

except Exception as e:
    print(f"Request failed: {e}")

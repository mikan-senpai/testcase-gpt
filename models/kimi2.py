import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv("../.env")

# Use environment variable
api_key = os.environ.get("HF_TOKEN")

if not api_key:
    print("❌ HF_TOKEN not found in environment variables!")
    print("Please set your Hugging Face token:")
    print("1. Get a token from: https://huggingface.co/settings/tokens")
    print("2. Update your .env file: HF_TOKEN=your_new_token_here")
    exit(1)

print(f"Using token: {api_key[:10]}...")

# Simple Hugging Face Inference API call
def call_huggingface_model():
    headers = {"Authorization": f"Bearer {api_key}"}

    # Using a reliable model that supports chat
    model_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

    payload = {
        "inputs": "What is the capital of France?",
        "parameters": {
            "max_length": 100,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(model_url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                print("✅ Success!")
                print("Response:", result[0].get('generated_text', 'No text generated'))
            else:
                print("Response:", result)
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ Request failed: {e}")

# Alternative: Try OpenAI-compatible endpoint (if available)
def try_openai_compatible():
    try:
        from openai import OpenAI

        # Try the TGI (Text Generation Inference) endpoint
        client = OpenAI(
            base_url="https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium/v1",
            api_key=api_key,
        )

        completion = client.chat.completions.create(
            model="microsoft/DialoGPT-medium",
            messages=[
                {"role": "user", "content": "What is the capital of France?"}
            ],
            max_tokens=50,
        )

        print("✅ OpenAI-compatible endpoint working!")
        print("Response:", completion.choices[0].message.content)
        return True

    except Exception as e:
        print(f"OpenAI-compatible failed: {e}")
        return False

print("Testing Hugging Face Inference API...")
call_huggingface_model()

print("\nTrying OpenAI-compatible endpoint...")
if not try_openai_compatible():
    print("💡 Use the direct API call above for now.")

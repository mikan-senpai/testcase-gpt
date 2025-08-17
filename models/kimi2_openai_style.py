import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv("../.env")
api_key = os.environ.get("HF_TOKEN")

print(f"Using token: {api_key[:10]}...")

# Try HuggingFace's OpenAI-compatible endpoint
# This is different from the router we tried before
client = OpenAI(
    base_url="https://api-inference.huggingface.co/v1",
    api_key=api_key,
)

# List of models to try (these are known to work with HF inference)
models_to_try = [
    "meta-llama/Llama-3.1-8B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "microsoft/DialoGPT-medium",
    "openai-community/gpt2"
]

for model_name in models_to_try:
    try:
        print(f"\nTrying model: {model_name}")

        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "What is the capital of France?"}
            ],
            max_tokens=50,
            temperature=0.7
        )

        print(f"✅ Success with {model_name}!")
        print(f"Response: {completion.choices[0].message.content}")
        break

    except Exception as e:
        print(f"❌ Failed with {model_name}: {e}")
        continue
else:
    print("\n❌ All OpenAI-style requests failed.")
    print("This might be because:")
    print("1. Your token doesn't have inference permissions")
    print("2. The models are currently loading/unavailable")
    print("3. HuggingFace inference API has different requirements")

    # Let's try a direct HTTP request approach
    print("\n=== Trying direct HTTP request ===")
    import requests

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": "What is the capital of France?",
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/openai-community/gpt2",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"HTTP Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Direct HTTP request successful!")
            print(f"Response: {result}")
        else:
            print(f"❌ HTTP request failed: {response.text}")

    except Exception as e:
        print(f"❌ HTTP request error: {e}")

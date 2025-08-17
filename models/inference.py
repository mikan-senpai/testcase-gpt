import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv("../.env")

# Get API key from environment
HF_TOKEN = os.environ.get("HF_TOKEN")

BASE_URL = "https://router.huggingface.co/v1"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def get_available_models():
    """Get list of available models from the API"""
    try:
        response = requests.get(f"{BASE_URL}/models", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting models: {e}")
        return None

def query(payload):
    try:
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        if hasattr(e.response, 'text'):
            error_data = json.loads(e.response.text)
            if 'error' in error_data:
                print(f"Error message: {error_data['error']['message']}")
        return None

# First, let's see what models are available
print("Checking available models...")
models_response = get_available_models()

if models_response and 'data' in models_response:
    print("\nAvailable models:")
    for model in models_response['data'][:5]:  # Show first 5 models
        print(f"  - {model['id']}")
    print()

# List of models to try in order of preference
models_to_try = [
    "Qwen/Qwen2.5-Coder-32B-Instruct",  # Often available
    "meta-llama/Llama-3.3-70B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "meta-llama/Llama-3.2-3B-Instruct",
    "meta-llama/Llama-3.2-1B-Instruct",
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
]

# Try each model until one works
for model_name in models_to_try:
    print(f"Trying model: {model_name}...")
    response = query({
        "messages": [
            {
                "role": "user",
                "content": "What is the capital of France? Please answer in one sentence."
            }
        ],
        "model": model_name,
        "max_tokens": 50,
        "temperature": 0.7
    })

    if response and "choices" in response:
        print(f"✓ Success with {model_name}!")
        print(f"Response: {response['choices'][0]['message']['content']}")
        break
else:
    print("\n❌ None of the models worked.")
    print("\nPlease check:")
    print("1. Your API key is valid")
    print("2. You have access to the HuggingFace Inference API")
    print("3. Visit https://huggingface.co/settings/tokens to manage your tokens")

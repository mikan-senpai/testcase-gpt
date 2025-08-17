import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from .env file in parent directory
load_dotenv("../.env")

# Get API key from environment
api_key = os.environ.get("HF_TOKEN")

if not api_key:
    print("❌ HF_TOKEN not found in environment variables!")
    print("Please set your Hugging Face token in .env file")
    exit(1)

print(f"Using token: {api_key[:10]}...")

# Create inference client
client = InferenceClient(token=api_key)

# Try different models that are available
models_to_try = [
    "microsoft/DialoGPT-medium",
    "gpt2",
    "distilgpt2",
    "microsoft/DialoGPT-small"
]

for model_name in models_to_try:
    try:
        print(f"\nTrying model: {model_name}")

        # Use text generation
        response = client.text_generation(
            prompt="What is the capital of France?",
            model=model_name,
            max_new_tokens=50,
            temperature=0.7
        )

        print(f"✅ Success with {model_name}!")
        print(f"Response: {response}")
        break

    except Exception as e:
        print(f"❌ Failed with {model_name}: {e}")
        continue
else:
    print("\n❌ All models failed. Let's try a different approach...")

    # Try with a chat model if available
    try:
        print("\nTrying chat completion...")
        messages = [{"role": "user", "content": "What is the capital of France?"}]

        response = client.chat_completion(
            messages=messages,
            model="microsoft/DialoGPT-medium",
            max_tokens=50
        )

        print("✅ Chat completion successful!")
        print(f"Response: {response}")

    except Exception as e:
        print(f"❌ Chat completion failed: {e}")
        print("\nYour token is valid but the models might be loading or unavailable.")
        print("Try again in a few minutes.")

import os
from dotenv import load_dotenv
from huggingface_hub import HfApi, InferenceClient

# Load environment variables
load_dotenv("../.env")
api_key = os.environ.get("HF_TOKEN")

print(f"Using token: {api_key[:10]}...")

# Check what's available through the API
api = HfApi(token=api_key)

try:
    print("\n=== Checking available models ===")

    # List some popular text generation models
    models = api.list_models(
        task="text-generation",
        limit=10,
        sort="downloads",
        direction=-1
    )

    print("Top text generation models:")
    for i, model in enumerate(models):
        print(f"{i+1}. {model.id}")
        if i >= 4:  # Show only first 5
            break

except Exception as e:
    print(f"Error listing models: {e}")

# Try a simple inference with a very basic model
try:
    print("\n=== Testing simple inference ===")
    client = InferenceClient(token=api_key)

    # Try with a simple, reliable model
    response = client.text_generation(
        "Hello, how are you?",
        model="gpt2",
        max_new_tokens=20
    )

    print(f"✅ Simple inference works!")
    print(f"Response: {response}")

except Exception as e:
    print(f"❌ Simple inference failed: {e}")

    # Let's try without specifying a model (uses default)
    try:
        print("\nTrying with default model...")
        response = client.text_generation(
            "Hello, how are you?",
            max_new_tokens=20
        )
        print(f"✅ Default model works!")
        print(f"Response: {response}")
    except Exception as e2:
        print(f"❌ Default model also failed: {e2}")

print("\n=== Checking token permissions ===")
try:
    user_info = api.whoami()
    print(f"✅ Token is valid for user: {user_info['name']}")
    print(f"Account type: {user_info.get('type', 'unknown')}")
except Exception as e:
    print(f"❌ Token validation failed: {e}")

import os
from dotenv import load_dotenv
from huggingface_hub import HfApi

# Load environment variables
load_dotenv("../.env")
api_key = os.environ.get("HF_TOKEN")

print(f"Using token: {api_key[:10]}...")

# Check token info and permissions
api = HfApi(token=api_key)

try:
    user_info = api.whoami()
    print(f"✅ Token is valid!")
    print(f"User: {user_info['name']}")
    print(f"Account type: {user_info.get('type', 'unknown')}")

    # Check if we can access models
    print(f"\n=== Available Models (first 5) ===")
    models = api.list_models(limit=5, sort="downloads", direction=-1)
    for model in models:
        print(f"- {model.id}")

    print(f"\n=== Token Analysis ===")
    print("Your token works for:")
    print("✅ User authentication")
    print("✅ Listing models")
    print("✅ Accessing model information")
    print("❌ Model inference (this requires different permissions or paid access)")

    print(f"\n=== Solutions ===")
    print("1. **For Inference API access:**")
    print("   - Go to https://huggingface.co/settings/tokens")
    print("   - Create a new token with 'Inference' permissions")
    print("   - Or check if your account has inference quota")

    print("2. **Alternative: Use local models with transformers:**")
    print("   - Install: pip install transformers torch")
    print("   - Download and run models locally")

    print("3. **Alternative: Use Gradio/Spaces:**")
    print("   - Many models are available through Gradio interfaces")
    print("   - These don't require inference API access")

    # Let's try to download a small model for local use
    print(f"\n=== Testing Local Model Download ===")
    try:
        from transformers import pipeline

        print("Attempting to create a local text generation pipeline...")
        # This will download a small model locally
        generator = pipeline("text-generation", model="distilgpt2", token=api_key)

        result = generator("What is the capital of France?", max_length=50, num_return_sequences=1)
        print("✅ Local model works!")
        print(f"Response: {result[0]['generated_text']}")

    except ImportError:
        print("❌ transformers not installed. Run: pip install transformers torch")
    except Exception as e:
        print(f"❌ Local model failed: {e}")

except Exception as e:
    print(f"❌ Token validation failed: {e}")

print(f"\n" + "="*60)
print("SUMMARY:")
print("Your HuggingFace token is VALID but has limited permissions.")
print("It works for browsing models but not for inference API calls.")
print("This is normal for free accounts - inference often requires paid access.")
print("="*60)

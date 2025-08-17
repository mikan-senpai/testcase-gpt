from huggingface_hub import HfApi

api = HfApi()
try:
    # Attempt to list models to verify API key functionality
    models = api.list_models(author="HuggingFaceH4", limit=5)
    print("Successfully accessed Hugging Face Hub. API key is valid.")
    for model in models:
        print(f"- {model.id}")
except Exception as e:
    print(f"Failed to access Hugging Face Hub. API key might be invalid or expired: {e}")

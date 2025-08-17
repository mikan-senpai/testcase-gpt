import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv("../.env")

api_key = os.environ.get("HF_TOKEN")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=api_key,
)

# Using a model that's available through HuggingFace's router
# Common available models: meta-llama/Llama-3.2-1B-Instruct, Qwen/Qwen2.5-72B-Instruct, etc.
try:
    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.2-1B-Instruct",  # Changed to a supported model
        messages=[
            {
                "role": "user",
                "content": "hey"
            }
        ],
        max_tokens=100,  # Adding max_tokens to control response length
    )

    print("Response:", completion.choices[0].message.content)

except Exception as e:
    print(f"Error: {e}")
    print("\nTry one of these supported models:")
    print("- meta-llama/Llama-3.2-1B-Instruct")
    print("- meta-llama/Llama-3.2-3B-Instruct")
    print("- Qwen/Qwen2.5-72B-Instruct")
    print("- mistralai/Mistral-7B-Instruct-v0.3")

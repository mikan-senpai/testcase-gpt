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

completion = client.chat.completions.create(
    model="moonshotai/Kimi-K2-Instruct",
    messages=[
        {
            "role": "user",
            "content": "hey"
        }
    ],
)

print(completion.choices[0].message)

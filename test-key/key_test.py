import os
from huggingface_hub import login
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get token from environment variable
hf_token = os.environ.get('HF_TOKEN')

if not hf_token:
    print("❌ HF_TOKEN not found in environment variables!")
    print("Please set your Hugging Face token in .env file:")
    print("HF_TOKEN=your_token_here")
    exit(1)

# Login with token from environment
login(token=hf_token)
print("✅ Successfully logged in to Hugging Face!")

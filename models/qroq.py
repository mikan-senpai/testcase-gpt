import os
import httpx
import warnings
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Suppress SSL warnings (only for development/testing)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Get API key from environment variable
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ_API_KEY not found in environment variables!")
    print("Please set your Groq API key in .env file:")
    print("GROQ_API_KEY=your_groq_key_here")
    exit(1)

# Create a custom httpx client that bypasses SSL verification
# Note: Only use this in development or if you trust the network
http_client = httpx.Client(verify=False)

try:
    client = Groq(
        api_key=api_key,
        http_client=http_client  # Use custom client with SSL verification disabled
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "hey how to parse you any markdown",
            }
        ],
        model="llama-3.3-70b-versatile",
        stream=False,
    )

    print("Response from Groq:")
    print("-" * 50)
    print(chat_completion.choices[0].message.content)

except Exception as e:
    print(f"Error: {e}")
    print("\nIf you're getting SSL errors, you might be behind a corporate firewall.")
    print("The script is configured to bypass SSL verification for development purposes.")

finally:
    # Close the HTTP client
    if 'http_client' in locals():
        http_client.close()

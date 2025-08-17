import os
from dotenv import load_dotenv

load_dotenv("../.env")
token = os.environ.get("HF_TOKEN")

print(f"Token length: {len(token) if token else 'None'}")
print(f"Token repr: {repr(token)}")
print(f"Token starts with 'hf_': {token.startswith('hf_') if token else False}")

# Check for whitespace
if token:
    stripped = token.strip()
    print(f"Has whitespace: {token != stripped}")
    print(f"Stripped token: {repr(stripped)}")

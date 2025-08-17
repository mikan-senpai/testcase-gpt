import os
from dotenv import load_dotenv

print("=== Testing Environment Variable Loading ===\n")

# Test 1: Load from parent directory
print("1. Loading from ../.env")
load_dotenv("../.env")
token = os.environ.get("HF_TOKEN")
print(f"   HF_TOKEN: {token}")
print(f"   Token length: {len(token) if token else 'None'}")
print(f"   Valid format: {token.startswith('hf_') if token else False}")

# Test 2: Check all environment variables
print("\n2. All environment variables containing 'HF' or 'TOKEN':")
for key, value in os.environ.items():
    if 'HF' in key or 'TOKEN' in key:
        print(f"   {key}: {value}")

# Test 3: Check if .env file exists
import os.path
env_path = "../.env"
print(f"\n3. .env file exists at {env_path}: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        content = f.read()
        print("   .env file content:")
        for line in content.split('\n'):
            if line.strip() and not line.startswith('#'):
                print(f"     {line}")

print("\n=== Test Complete ===")

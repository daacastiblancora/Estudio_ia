import os
import sys
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv(override=True)
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL:
    print("❌ Missing QDRANT_URL")
    sys.exit(1)

# Ensure no trailing slash
base_url = QDRANT_URL.strip().rstrip("/")
if base_url.count(":") < 2: # No port specified
    url_with_port = f"{base_url}:6333"
else:
    url_with_port = base_url

print(f"--- Connectivity Test ---")
print(f"Original URL: {base_url}")
print(f"Testing URL with port 6333: {url_with_port}")

try:
    print(f"⏳ Attempting connection to {url_with_port} ...")
    client = QdrantClient(url=url_with_port, api_key=QDRANT_API_KEY, timeout=10)
    res = client.get_collections()
    print("✅ SUCCESS with Port 6333!")
except Exception as e:
    print(f"❌ Failed with 6333: {e}")
    
    # Try 443 just in case
    try:
        print(f"⏳ Attempting connection to {base_url} (default port)...")
        client = QdrantClient(url=base_url, api_key=QDRANT_API_KEY, timeout=10)
        res = client.get_collections()
        print("✅ SUCCESS with Default Port!")
    except Exception as e2:
        print(f"❌ Failed with Default: {e2}")


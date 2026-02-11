import os
import shutil
from qdrant_client import QdrantClient
from app.core.config import settings

print(f"--- Local Qdrant Check ---")
print(f"URL/Path: {settings.QDRANT_URL}")
print(f"API Key: {settings.QDRANT_API_KEY}")

if settings.QDRANT_URL.startswith("http"):
    print("❌ Config is still pointing to Cloud/HTTP!")
else:
    print("✅ Config is pointing to a local path.")

try:
    print(f"⏳ Initializing QdrantClient(path='{settings.QDRANT_URL}')...")
    client = QdrantClient(path=settings.QDRANT_URL)
    print("✅ Client initialized!")
    
    print("⏳ Creating collection 'test_local'...")
    client.recreate_collection(
        collection_name="test_local",
        vectors_config={"size": 4, "distance": "Dot"}
    )
    print("✅ Collection created!")
    
    collections = client.get_collections()
    print(f"Collections: {[c.name for c in collections.collections]}")
    
except Exception as e:
    print(f"❌ Failed: {e}")

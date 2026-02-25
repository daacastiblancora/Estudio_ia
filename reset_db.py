import os
import shutil
from qdrant_client import QdrantClient

# Old FAISS path
DB_PATH = "faiss_index"

def reset_db():
    print("🔄 Environment variables for Qdrant (from .env):")
    
    # Try to load .env manually if dotenv not used globally
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
        
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "corporate_documents")
    
    print(f"  - URL: {qdrant_url}")
    print(f"  - Collection: {collection_name}")
    
    # 1. Clean up old FAISS if it exists
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH)
            print(f"📁 Deleted old FAISS directory: {DB_PATH}")
        except Exception as e:
            print(f"⚠️ Could not delete old FAISS dir: {e}")
            
    # 2. Reset Qdrant Collection
    if qdrant_url == "qdrant_data" or not qdrant_url.startswith("http"):
        print("⚠️ QDRANT_URL seems to be invalid or still pointing to local FAISS config.")
        print("Make sure QDRANT_URL=http://localhost:6333 in .env")
        return

    try:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        
        # Check if collection exists
        collections = [col.name for col in client.get_collections().collections]
        
        if collection_name in collections:
            client.delete_collection(collection_name=collection_name)
            print(f"✅ Deleted Qdrant collection: '{collection_name}'")
        else:
            print(f"ℹ️ Qdrant collection '{collection_name}' does not exist. Nothing to delete.")
            
        print("The collection will be re-created automatically with the correct dimensions upon server startup or first ingestion.")
            
    except Exception as e:
        print(f"❌ Failed to connect or reset Qdrant: {e}")
        print("Is the Qdrant Docker container running? (docker run -p 6333:6333 qdrant/qdrant)")

if __name__ == "__main__":
    confirm = input("⚠️ Are you sure you want to DELETE the Qdrant vector database collection? (y/n): ")
    if confirm.lower() == 'y':
        reset_db()
    else:
        print("Cancelled.")

import os
import requests
import sys

API_URL = "http://localhost:8001/api/v1"
DOCS_DIR = "documents"

def bulk_ingest():
    print(f"🚀 Starting Bulk Ingestion from '{DOCS_DIR}'")
    
    # Check if API is up
    try:
        r = requests.get(f"{API_URL}/health")
        if r.status_code != 200:
            print(f"❌ API is not healthy (Status: {r.status_code}). Please start the server first.")
            return
        print("✅ API is connected.")
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")
        print("👉 Did you start the server? (uvicorn app.main:app --reload)")
        return

    if not os.path.exists(DOCS_DIR):
        print(f"❌ Directory '{DOCS_DIR}' not found.")
        return

    files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".pdf") or f.endswith(".docx")]
    
    if not files:
        print("⚠️ No supported files found in 'documents/'")
        return

    print(f"📄 Found {len(files)} documents to ingest.")
    
    for filename in files:
        filepath = os.path.join(DOCS_DIR, filename)
        print(f"\nUploading: {filename} ...")
        
        try:
            with open(filepath, 'rb') as f:
                files = {'file': f}
                r = requests.post(f"{API_URL}/ingest", files=files)
                
                if r.status_code == 200:
                    data = r.json()
                    print(f"✅ Success! Created {data.get('chunks_created', 0)} chunks.")
                else:
                    print(f"❌ Failed: {r.text}")
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")

    print("\n✨ Bulk Ingestion Complete!")

if __name__ == "__main__":
    bulk_ingest()

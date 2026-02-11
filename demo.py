import requests
import sys
import os

API_URL = "http://localhost:8001/api/v1"

def run_demo():
    print("🚀 Starting Copiloto Core Demo")
    
    # 1. Check Health
    try:
        r = requests.get(f"{API_URL}/health")
        if r.status_code == 200:
            print("✅ API is Healthy")
        else:
            print(f"❌ API Error: {r.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is it running? (uvicorn app.main:app --reload)")
        return

    # 2. Ingest a file (if provided)
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.exists(filepath):
            print(f"📄 Uploading {filepath}...")
            with open(filepath, 'rb') as f:
                files = {'file': f}
                r = requests.post(f"{API_URL}/ingest", files=files)
                print(f"📥 Ingest Result: {r.json()}")
        else:
            print(f"⚠️ File not found: {filepath}")
    else:
        print("ℹ️ No file provided for ingestion. Skipping.")

    # 3. Chat Loop
    print("\n💬 Enter your question (or 'q' to quit):")
    while True:
        query = input("> ")
        if query.lower() in ['q', 'quit', 'exit']:
            break
        
        if not query.strip():
            continue

        try:
            r = requests.post(f"{API_URL}/chat", json={"query": query})
            if r.status_code == 200:
                resp = r.json()
                print(f"\n🤖 Answer: {resp['answer']}")
                if resp['sources']:
                    print("\n📚 Sources:")
                    for s in resp['sources']:
                        print(f"   - {s['document_name']} (Page {s['page_number']})")
                print("-" * 50)
            else:
                print(f"❌ Error: {r.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_demo()

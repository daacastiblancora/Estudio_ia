import requests
import sys
import os
import time

API_URL = "http://localhost:8001/api/v1"
TEST_FILE = "documents/manual_antigravity.pdf"

def run_test():
    print("🚀 Starting End-to-End Test (FAISS)")
    
    # 1. Health
    try:
        print("Parametric Checking API Health...")
        r = requests.get(f"{API_URL}/health")
        if r.status_code == 200:
            print("✅ API is Healthy")
        else:
            print(f"❌ API Error: {r.status_code} - {r.text}")
            return
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    # 2. Ingest
    if os.path.exists(TEST_FILE):
        print(f"📄 Ingesting {TEST_FILE}...")
        with open(TEST_FILE, 'rb') as f:
            files = {'file': f}
            r = requests.post(f"{API_URL}/ingest", files=files)
            if r.status_code == 200:
                print(f"✅ Ingest Success: {r.json()}")
            else:
                print(f"❌ Ingest Failed: {r.text}")
    else:
        print(f"⚠️ Test file {TEST_FILE} not found. Skipping ingestion test.")

    # 3. Chat
    query = "Resumen del manual"
    print(f"💬 Querying: '{query}'")
    try:
        r = requests.post(f"{API_URL}/chat", json={"query": query})
        if r.status_code == 200:
            resp = r.json()
            print(f"\n🤖 Answer: {resp['answer']}")
            print(f"📚 Sources: {len(resp.get('sources', []))}")
            if resp['sources']:
                print(f"   First source: {resp['sources'][0]['document_name']}")
        else:
            print(f"❌ Chat Failed: {r.text}")
    except Exception as e:
        print(f"❌ Chat Error: {e}")

if __name__ == "__main__":
    run_test()

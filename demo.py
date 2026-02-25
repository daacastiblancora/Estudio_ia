"""
Demo CLI — Interactive chat with the Copiloto Core API.
Requires JWT authentication.

Usage:
    python demo.py
    python demo.py path/to/document.pdf   # Ingest + Chat
"""
import requests
import sys
import os

API_URL = "http://localhost:8001/api/v1"
DEFAULT_EMAIL = "demo@copiloto.com"
DEFAULT_PASSWORD = "DemoPassword123!"


def get_auth_token():
    """Authenticate and return JWT token."""
    # Try login first
    r = requests.post(f"{API_URL}/login", data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD})
    if r.status_code == 200:
        return r.json()["access_token"]

    # Register if login fails
    r = requests.post(f"{API_URL}/register", json={"email": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD})
    if r.status_code == 200:
        return r.json()["access_token"]

    print(f"❌ Auth failed: {r.text}")
    return None


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
        print("❌ Could not connect to API. Is it running? (uvicorn app.main:app --reload --port 8001)")
        return

    # 2. Authenticate
    token = get_auth_token()
    if not token:
        return
    headers = {"Authorization": f"Bearer {token}"}
    print(f"🔑 Authenticated as {DEFAULT_EMAIL}")

    # 3. Ingest a file (if provided)
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.exists(filepath):
            print(f"📄 Uploading {filepath}...")
            with open(filepath, 'rb') as f:
                r = requests.post(f"{API_URL}/ingest", files={'file': f}, headers=headers)
                if r.status_code == 200:
                    print(f"📥 Ingest Result: {r.json()}")
                else:
                    print(f"❌ Ingest Failed ({r.status_code}): {r.text}")
        else:
            print(f"⚠️ File not found: {filepath}")
    else:
        print("ℹ️ No file provided for ingestion. Skipping.")

    # 4. Chat Loop
    import uuid
    session_id = str(uuid.uuid4())
    print(f"\n💬 Enter your question (or 'q' to quit). Session ID: {session_id}")

    while True:
        query = input("> ")
        if query.lower() in ['q', 'quit', 'exit']:
            break

        if not query.strip():
            continue

        try:
            r = requests.post(
                f"{API_URL}/chat",
                json={"query": query, "session_id": session_id},
                headers=headers
            )
            if r.status_code == 200:
                resp = r.json()
                print(f"\n🤖 Answer: {resp['answer']}")
                if resp.get('sources'):
                    print("\n📚 Sources:")
                    for s in resp['sources']:
                        print(f"   - {s['document_name']} (Page {s['page_number']})")
                print("-" * 50)
            else:
                print(f"❌ Error ({r.status_code}): {r.text}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    run_demo()

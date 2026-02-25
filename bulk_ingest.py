import os
import requests
import sys

API_URL = "http://localhost:8001/api/v1"
DOCS_DIR = "documents"

def get_auth_token():
    """Login to get JWT token for hardened /ingest endpoint."""
    email = "admin@copiloto.com"
    password = "AdminPassword123!"
    
    # Try login
    print(f"🔑 Attempting login as {email}...")
    r = requests.post(f"{API_URL}/login", data={"username": email, "password": password})
    if r.status_code == 200:
        return r.json()["access_token"]
        
    # If login fails, try register
    print("ℹ️ Login failed, attempting to register...")
    r = requests.post(f"{API_URL}/register", json={"email": email, "password": password})
    if r.status_code == 200:
        print("✅ Registered new admin user.")
        # Login again to get token via OAuth2 form
        r = requests.post(f"{API_URL}/login", data={"username": email, "password": password})
        if r.status_code == 200:
            return r.json()["access_token"]
            
    print(f"❌ Authentication failed: {r.text}")
    print("Make sure the backend is running and you have access.")
    return None

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
        print("👉 Did you start the server? (uvicorn app.main:app --reload --port 8001)")
        return

    # Get Auth Token
    token = get_auth_token()
    if not token:
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    if not os.path.exists(DOCS_DIR):
        print(f"❌ Directory '{DOCS_DIR}' not found.")
        return

    # Allowed extensions matching config
    allowed_exts = (".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".txt", ".csv", ".eml", ".msg")
    files = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith(allowed_exts)]
    
    if not files:
        print(f"⚠️ No supported files found in '{DOCS_DIR}'")
        return

    print(f"📄 Found {len(files)} documents to ingest.")
    
    for filename in files:
        filepath = os.path.join(DOCS_DIR, filename)
        print(f"\nUploading: {filename} ...")
        
        try:
            with open(filepath, 'rb') as f:
                # We need to specify the tuple (filename, file_object, mimetype) for some FastAPI versions
                # depending on how strictly they check
                files_payload = {'file': (filename, f, 'application/pdf' if filename.endswith('.pdf') else 'application/octet-stream')}
                r = requests.post(f"{API_URL}/ingest", files=files_payload, headers=headers)
                
                if r.status_code == 200:
                    data = r.json()
                    print(f"✅ Success! Created {data.get('chunks_created', 0)} chunks.")
                else:
                    print(f"❌ Failed ({r.status_code}): {r.text}")
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")

    print("\n✨ Bulk Ingestion Complete!")

if __name__ == "__main__":
    bulk_ingest()

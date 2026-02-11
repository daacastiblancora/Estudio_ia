import os
import re

def rewrite_env():
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        return

    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to find keys, handling potential quotes and newlines
    # We look for the key, optionally whitespace, =, optionally whitespace, optionally quotes, then content
    
    qdrant_key_match = re.search(r"QDRANT_API_KEY=['\"]?([^'\"\n]+)['\"]?", content)
    groq_key_match = re.search(r"GROQ_API_KEY=['\"]?([^'\"\n]+)['\"]?", content)

    qdrant_key = qdrant_key_match.group(1) if qdrant_key_match else ""
    groq_key = groq_key_match.group(1) if groq_key_match else ""

    # Hardcoded known URL parts from analysis
    url_part_1 = "https://35aba340-2010-44b3-a06a-bcc9771ee0"
    url_part_2 = "053.us-east4-0.gcp.cloud.qdrant.io"
    full_url = url_part_1 + url_part_2

    new_content = (
        f"PROJECT_NAME=Copiloto Core\n"
        f"API_V1_STR=/api/v1\n"
        f"QDRANT_URL={full_url}\n"
        f"QDRANT_API_KEY={qdrant_key}\n"
        f"QDRANT_COLLECTION_NAME=corporate_documents\n"
        f"GROQ_API_KEY={groq_key}\n"
        f"GROQ_MODEL_NAME=llama3-70b-8192\n"
        f"EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2\n"
        f"CHUNK_SIZE=1000\n"
        f"CHUNK_OVERLAP=200\n"
        f"BACKEND_CORS_ORIGINS=[\"http://localhost:3000\",\"http://localhost:8000\"]\n"
    )

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ .env file rewritten with clean values.")
    print(f"URL: {full_url}")
    print(f"API Key Found: {'Yes' if qdrant_key else 'No'}")

if __name__ == "__main__":
    rewrite_env()

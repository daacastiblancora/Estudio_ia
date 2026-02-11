import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME")

print(f"GROQ_MODEL_NAME: '{GROQ_MODEL_NAME}'")
if GROQ_API_KEY:
    print(f"GROQ_API_KEY: Starts with '{GROQ_API_KEY[:5]}...', Length: {len(GROQ_API_KEY)}")
else:
    print("GROQ_API_KEY: Not found or empty")

# Test simple imports
try:
    from langchain_groq import ChatGroq
    print("✅ langchain_groq imported")
except ImportError as e:
    print(f"❌ langchain_groq import failed: {e}")

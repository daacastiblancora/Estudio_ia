import sys
import os

# Mock settings to avoid env var errors
os.environ["GROQ_API_KEY"] = "mock_key"
os.environ["QDRANT_URL"] = "http://localhost:6333"

try:
    from app.main import app
    from app.core.guardrails import guardrails
    from slowapi import Limiter
    print("✅ Imports successful")
    print(f"✅ Rate Limiter configured: {isinstance(app.state.limiter, Limiter)}")
    print("✅ Guardrails module loaded")
except Exception as e:
    print(f"❌ Error during verification: {e}")
    sys.exit(1)

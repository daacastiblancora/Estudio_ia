import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")

try:
    import langchain
    print(f"✅ langchain imported. Location: {langchain.__file__}")
    print(f"Version: {getattr(langchain, '__version__', 'unknown')}")
    print(f"Contents: {dir(langchain)}")
except ImportError as e:
    print(f"❌ Failed to import langchain: {e}")

try:
    import langchain.chains
    print("✅ langchain.chains imported successfully")
except ImportError as e:
    print(f"❌ Failed to import langchain.chains: {e}")

try:
    from langchain.chains import create_retrieval_chain
    print("✅ create_retrieval_chain imported successfully")
except ImportError as e:
    print(f"❌ Failed to import create_retrieval_chain: {e}")

# Check pip freeze to see what's actually installed
print("\n--- PIP LIST (LangChain related) ---")
os.system(f"{sys.executable} -m pip list | findstr langchain")

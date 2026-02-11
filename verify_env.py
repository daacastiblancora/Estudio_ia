import sys

def check_import(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False

deps = [
    "langchain",
    "langchain.chains",
    "langchain_qdrant",
    "langchain_groq",
    "langchain_community",
    "qdrant_client",
    "slowapi"
]

print("--- Verifying Environment ---")
results = [check_import(dep) for dep in deps]

if all(results):
    print("\n✨ All critical dependencies are installed correctly!")
    sys.exit(0)
else:
    print("\n⚠️ Some dependencies are missing!")
    sys.exit(1)

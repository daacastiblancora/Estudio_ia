import sys
print(f"Python: {sys.executable}")

try:
    import msvcrt
    print("✅ msvcrt imported")
except ImportError as e:
    print(f"❌ msvcrt failed: {e}")

try:
    import portalocker
    print("✅ portalocker imported")
except ImportError as e:
    print(f"❌ portalocker failed: {e}")

try:
    from qdrant_client import QdrantClient
    print("✅ QdrantClient imported")
    
    print("⏳ Testing In-Memory Qdrant...")
    client = QdrantClient(":memory:")
    print("✅ In-Memory Initialized!")

    print("⏳ Testing On-Disk Qdrant...")
    client_disk = QdrantClient(path="qdrant_test_db")
    print("✅ On-Disk Initialized!")

except Exception as e:
    print(f"❌ Qdrant failed: {e}")

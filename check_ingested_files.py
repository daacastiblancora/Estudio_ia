from app.services.vector_db import vector_db_service
import sys

try:
    vector_store = vector_db_service.get_vector_store()
    
    # FAISS docstore is in memory, we can iterate over it
    print("🔍 Scanning FAISS index for ingested files...")
    
    docstore = vector_store.docstore
    all_docs = docstore._dict.values()
    
    unique_sources = set()
    for doc in all_docs:
        if "source" in doc.metadata:
            unique_sources.add(doc.metadata["source"])
            
    if not unique_sources:
        print("❌ No files found in the index.")
    else:
        print(f"✅ Found {len(unique_sources)} unique files:")
        for source in sorted(unique_sources):
            print(f"   PLEASE CHECK: {source}")

except Exception as e:
    print(f"❌ Error scanning index: {e}")

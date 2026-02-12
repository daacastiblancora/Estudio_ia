from app.services.vector_db import vector_db_service
from app.services.retriever import get_hybrid_retriever

try:
    print("🔍 Testing Hybrid Retriever...")
    retriever = get_hybrid_retriever()
    
    query = "comisión internacional"
    docs = retriever.invoke(query)
    
    if not docs:
        print("❌ No documents retrieved.")
    else:
        print(f"✅ Retrieved {len(docs)} documents.")
        for i, doc in enumerate(docs):
            print(f"-- Doc {i+1} --")
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"Content Snippet: {doc.page_content[:100]}...")

except Exception as e:
    print(f"❌ Error in retriever: {e}")

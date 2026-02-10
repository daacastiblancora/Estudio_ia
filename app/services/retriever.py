from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from rank_bm25 import BM25Okapi
from langchain_huggingface import HuggingFaceEmbeddings
from app.services.vector_db import vector_db_service
from app.core.logging import logger
import hashlib

class HybridRetriever(BaseRetriever):
    """
    Hybrid Retriever that combines:
    1. Dense Search (Qdrant with HuggingFace Embeddings)
    2. Keyword Search (BM25 on retrieved documents or separate index)
    
    For this MVP, we will implement a 'Rerank' strategy:
    - Retrieve top K*2 documents from Vector DB.
    - Re-score them using BM25 locally.
    - Return top K.
    """
    vector_store: object
    k: int = 4

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        
        # 1. Broad Retrieval (Dense)
        # Fetch more candidates than needed
        logger.info(f"Hybrid Search: Retrieving candidates for '{query}'...")
        initial_docs = self.vector_store.similarity_search(query, k=self.k * 3)
        
        if not initial_docs:
            return []

        # 2. BM25 Reranking
        # Tokenize corpus (the retrieved docs)
        tokenized_corpus = [doc.page_content.lower().split() for doc in initial_docs]
        bm25 = BM25Okapi(tokenized_corpus)
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get scores
        scores = bm25.get_scores(tokenized_query)
        
        # Combine docs with scores
        scored_docs = zip(initial_docs, scores)
        
        # Sort by BM25 score (descending)
        sorted_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)
        
        # 3. Select Top K
        final_docs = [doc for doc, score in sorted_docs[:self.k]]
        
        logger.info(f"Hybrid Search: Re-ranked {len(initial_docs)} to {len(final_docs)} documents.")
        return final_docs

def get_hybrid_retriever(k: int = 5):
    vector_store = vector_db_service.get_vector_store()
    return HybridRetriever(vector_store=vector_store, k=k)

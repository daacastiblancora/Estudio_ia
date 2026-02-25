import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings
from app.core.logging import logger

class VectorDBService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME
        )
        
        # 1. Initialize Qdrant Client
        # Fallback to local memory if no URL provided (for testing), but default to the env value
        if settings.QDRANT_URL:
            logger.info(f"Connecting to Qdrant at {settings.QDRANT_URL}")
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY
            )
        else:
            logger.warning("No QDRANT_URL provided, falling back to local FAISS or memory. Initialize FAISS here if needed. But for this phase, Qdrant is required.")
            # For this phase, we enforce Qdrant use (local or cloud)
            # Memory mode:
            self.client = QdrantClient(":memory:")
            
        self.collection_name = settings.QDRANT_COLLECTION_NAME

        # 2. Ensure collection exists
        self._ensure_collection_exists()
        
        # 3. Initialize Langchain QdrantVectorStore
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )
        logger.info(f"Initialized QdrantVectorStore with collection '{self.collection_name}'")

    def _ensure_collection_exists(self):
        """Creates the Qdrant collection if it doesn't already exist."""
        try:
            collections_response = self.client.get_collections()
            collection_names = [col.name for col in collections_response.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Collection '{self.collection_name}' not found. Creating it...")
                # Get embedding dimension
                dummy_embedding = self.embeddings.embed_query("test")
                dimension = len(dummy_embedding)
                
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=dimension,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Collection '{self.collection_name}' created with dimension {dimension}.")
        except Exception as e:
            logger.error(f"Error checking/creating Qdrant collection: {e}")
            raise

    def get_vector_store(self):
        return self.vector_store

    def save(self):
        # Qdrant saves automatically, nothing to persist manually here
        pass

vector_db_service = VectorDBService()

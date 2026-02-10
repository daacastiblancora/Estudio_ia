from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_qdrant import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings
from app.core.logging import logger

class VectorDBService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL, 
            api_key=settings.QDRANT_API_KEY
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME
        )
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if settings.QDRANT_COLLECTION_NAME not in collection_names:
                logger.info(f"Creating collection {settings.QDRANT_COLLECTION_NAME}")
                self.client.create_collection(
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    vectors_config=models.VectorParams(
                        size=384,  # Size for all-MiniLM-L6-v2
                        distance=models.Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error(f"Error checking/creating collection: {e}")
            # Depending on deployment, might want to raise here

    def get_vector_store(self):
        return Qdrant(
            client=self.client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            embeddings=self.embeddings,
        )

vector_db_service = VectorDBService()

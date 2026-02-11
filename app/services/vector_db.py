import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings
from app.core.logging import logger

class VectorDBService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME
        )
        # Directory to save the persistent FAISS index
        self.persist_directory = "faiss_index"
        
        # Initialize Vector Store
        if os.path.exists(self.persist_directory):
            try:
                self.vector_store = FAISS.load_local(
                    self.persist_directory, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Loaded FAISS index from disk.")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                self._create_empty_index()
        else:
            self._create_empty_index()

    def _create_empty_index(self):
        logger.info("Creating new empty FAISS index.")
        # Create empty index
        # 384 dimensions for all-MiniLM-L6-v2
        # If using multilingual-MiniLM-L12 it might be different (384 too for v2?)
        # Let's dynamically get dimension
        dummy_embedding = self.embeddings.embed_query("test")
        dimension = len(dummy_embedding)
        
        index = faiss.IndexFlatL2(dimension)
        self.vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )

    def get_vector_store(self):
        return self.vector_store

    def save(self):
        if self.vector_store:
            self.vector_store.save_local(self.persist_directory)
            logger.info(f"Saved FAISS index to {self.persist_directory}")

vector_db_service = VectorDBService()

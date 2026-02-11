import os
import tempfile
from typing import List
from fastapi import UploadFile
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.vector_db import vector_db_service
from app.services.parser import pdf_parser
from app.core.config import settings
from app.core.logging import logger

class IngestionService:
    def __init__(self):
        self.vector_store = vector_db_service.get_vector_store()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "ARTÍCULO", "Artículo", "CAPÍTULO", "\n", ". ", " "],
            keep_separator=True
        )

    async def ingest_file(self, file: UploadFile) -> int:
        filename = file.filename
        
        logger.info(f"Starting ingestion for file: {filename}")
        
        # Save to temp file
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            documents = []
            if filename.lower().endswith(".pdf"):
                # Use robust PDF parser with explicit source name
                documents = pdf_parser.parse(tmp_path, source_name=filename)
            elif filename.lower().endswith(".docx"):
                loader = Docx2txtLoader(tmp_path)
                documents = loader.load()
                # Basic metadata for DOCX
            else:
                logger.warning(f"Unsupported file type: {filename}")
                return 0

            # FORCE CORRECT METADATA
            for doc in documents:
                doc.metadata["source"] = filename

            if not documents:
                logger.warning(f"No content extracted from {filename}")
                return 0

            # Split text
            chunks = self.text_splitter.split_documents(documents)
            
            logger.info(f"Split {filename} into {len(chunks)} chunks")
            
            # Add to Qdrant
            if chunks:
                self.vector_store.add_documents(chunks)
                # PERSISTENCE: Save FAISS index
                vector_db_service.save()
            
            return len(chunks)

        except Exception as e:
            logger.error(f"Error during ingestion of {filename}: {str(e)}")
            raise e
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

ingestion_service = IngestionService()

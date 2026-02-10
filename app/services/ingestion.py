import os
import tempfile
from typing import List
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.vector_db import vector_db_service
from app.core.logging import logger

class IngestionService:
    def __init__(self):
        self.vector_store = vector_db_service.get_vector_store()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    async def ingest_file(self, file: UploadFile) -> int:
        filename = file.filename
        content_type = file.content_type
        
        logger.info(f"Starting ingestion for file: {filename}")
        
        # Save to temp file to use loaders
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            documents = []
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(tmp_path)
                documents = loader.load()
            elif filename.endswith(".docx"):
                loader = Docx2txtLoader(tmp_path)
                documents = loader.load()
            else:
                logger.warning(f"Unsupported file type: {filename}")
                return 0

            # Add source metadata just in case verify
            for doc in documents:
                doc.metadata["source"] = filename
                # PDF loader adds 'page', docx might not. Handle if needed.

            chunks = self.text_splitter.split_documents(documents)
            
            logger.info(f"Split {filename} into {len(chunks)} chunks")
            
            # Add to Qdrant
            self.vector_store.add_documents(chunks)
            
            return len(chunks)

        finally:
            os.remove(tmp_path)

ingestion_service = IngestionService()

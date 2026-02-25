import os
import tempfile
from typing import List
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.vector_db import vector_db_service
from app.services.parser_registry import ParserRegistry
from app.services.parsers.pdf_parser import PDFParser
from app.services.parsers.docx_parser import DOCXParser
from app.services.parsers.spreadsheet_parser import SpreadsheetParser
from app.services.parsers.pptx_parser import PPTXParser
from app.services.parsers.email_parser import EmailParser
from app.services.parsers.plaintext_parser import PlainTextParser
from app.core.config import settings
from app.core.logging import logger


def _build_registry() -> ParserRegistry:
    """Build and return a configured ParserRegistry with all parsers."""
    registry = ParserRegistry()
    registry.register(PDFParser())
    registry.register(DOCXParser())
    registry.register(SpreadsheetParser())
    registry.register(PPTXParser())
    registry.register(EmailParser())

    # PlainText is both a registered parser AND the fallback
    plaintext = PlainTextParser()
    registry.register(plaintext)
    registry.set_fallback(plaintext)

    return registry


class IngestionService:
    def __init__(self):
        self.vector_store = vector_db_service.get_vector_store()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "ARTÍCULO", "Artículo", "CAPÍTULO", "\n", ". ", " "],
            keep_separator=True
        )
        self.registry = _build_registry()

    def get_supported_formats(self) -> list:
        """Return list of supported file extensions."""
        return self.registry.get_supported_extensions()

    async def ingest_file(self, file: UploadFile) -> int:
        filename = file.filename

        logger.info(f"Starting ingestion for: {filename}")

        # Save to temp file
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            if not content:
                logger.warning(f"Empty file received: {filename}")
                return 0
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Route to correct parser via registry
            documents = self.registry.parse(tmp_path, source_name=filename)

            if not documents:
                logger.warning(f"No content extracted from {filename}")
                return 0

            # Ensure correct metadata on all documents
            for doc in documents:
                doc.metadata["source"] = filename

            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split {filename} into {len(chunks)} chunks")

            # Add to vector store
            if chunks:
                self.vector_store.add_documents(chunks)
                vector_db_service.save()

            return len(chunks)

        except Exception as e:
            logger.error(f"Error during ingestion of {filename}: {str(e)}")
            raise e
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

ingestion_service = IngestionService()

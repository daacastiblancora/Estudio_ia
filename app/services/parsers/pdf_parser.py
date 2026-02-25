import os
import pdfplumber
from typing import List
from langchain_core.documents import Document
from app.services.parser_registry import BaseParser
from app.core.logging import logger


class PDFParser(BaseParser):
    """PDF parser using pdfplumber — extracts text page by page with metadata."""
    supported_extensions = ["pdf"]

    def parse(self, file_path: str, source_name: str) -> List[Document]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        documents = []

        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text = text.replace("\x00", "")
                    content = self._inject_header(source_name, "Página", i + 1) + text

                    documents.append(Document(
                        page_content=content,
                        metadata=self._make_metadata(
                            source=source_name, page=i + 1,
                            total=total_pages, fmt="pdf"
                        ),
                    ))

        logger.info(f"PDF parsed: {source_name} → {len(documents)} pages")
        return documents

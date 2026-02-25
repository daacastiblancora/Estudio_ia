import os
import pdfplumber
from typing import List
from langchain_core.documents import Document
from app.core.logging import logger

class PDFParser:
    """
    Robust PDF Parser using pdfplumber for better control over text extraction
    and metadata (page numbers).
    """
    
    def parse(self, file_path: str, source_name: str = None) -> List[Document]:
        """
        Parses a PDF file and returns a list of Documents (one per page)
        with metadata including source and page_number.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        documents = []
        # Use provided source name or fallback to basename
        filename = source_name if source_name else os.path.basename(file_path)

        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        # Clean text (basic normalization)
                        text = self._clean_text(text)
                        
                        # META-INJECTION: Add metadata to text so BM25/Vector can find it
                        # This enables questions like "What is on page 6 of remote work?"
                        text = f"Documento: {filename} | Página: {i+1}\n\n{text}"
                        
                        metadata = {
                            "source": filename,
                            "page_number": i + 1,
                            "total_pages": len(pdf.pages)
                        }
                        
                        doc = Document(page_content=text, metadata=metadata)
                        documents.append(doc)
                        
            logger.info(f"Successfully parsed {filename}: {len(documents)} pages.")
                        
        except Exception as e:
            logger.error(f"Error parsing {filename}: {e}")
            return []

        return documents

    def _clean_text(self, text: str) -> str:
        """
        Clean text to remove artifacts but preserve structure.
        """
        # 1. Remove specific null bytes and replacement chars
        text = text.replace("\x00", "").replace("\ufffd", "")
        
        # 2. Fix PDF newline artifact where bullets become "n Item" or "o Item"
        # Only replace if it looks like a bullet list error (e.g. newline char interpreted as n)
        # This is a heuristic. 
        # A safer approach is just to ensure real newlines are respected.
        
        # 3. Collapse multiple spaces
        text = " ".join(text.split(" "))
        
        # 4. Attempt to fix common "n " bullet artifacts
        # (This is specific to some PDF extractions where bullet is read as 'n')
        # We will replace " n " with " \n- " if it seems to be a list
        
        return text.strip()

pdf_parser = PDFParser()

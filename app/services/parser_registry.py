import os
from typing import Dict, List
from langchain_core.documents import Document
from app.core.logging import logger


class BaseParser:
    """
    Contract: every parser must return List[Document] with unified metadata.
    All parsers inherit from this and implement parse().
    """
    supported_extensions: List[str] = []

    def parse(self, file_path: str, source_name: str) -> List[Document]:
        raise NotImplementedError(f"{self.__class__.__name__}.parse() not implemented")

    def _make_metadata(self, source: str, page: int, total: int, fmt: str, section: str = "") -> dict:
        """Unified metadata for all formats — enables consistent citations."""
        return {
            "source": source,
            "page_number": page,
            "total_pages": total,
            "format": fmt,
            "section": section,
        }

    def _inject_header(self, source: str, page_label: str, page_num: int) -> str:
        """Injects a searchable header into the text for BM25/vector retrieval."""
        return f"Documento: {source} | {page_label}: {page_num}\n\n"


class ParserRegistry:
    """
    Strategy pattern: routes file extensions to the correct parser.
    Usage:
        registry = ParserRegistry()
        registry.register(PDFParser())
        registry.register(SpreadsheetParser())
        docs = registry.parse("file.xlsx", "Tarifas.xlsx")
    """

    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {}
        self._fallback: BaseParser = None

    def register(self, parser: BaseParser):
        """Register a parser for its supported extensions."""
        for ext in parser.supported_extensions:
            self._parsers[ext.lower()] = parser
            logger.debug(f"Registered parser {parser.__class__.__name__} for .{ext}")

    def set_fallback(self, parser: BaseParser):
        """Set a fallback parser for unknown extensions."""
        self._fallback = parser

    def get_supported_extensions(self) -> List[str]:
        """Return all supported extensions."""
        return list(self._parsers.keys())

    def parse(self, file_path: str, source_name: str) -> List[Document]:
        """
        Route a file to the correct parser based on extension.
        Returns List[Document] with unified metadata, or empty list on error.
        """
        ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
        parser = self._parsers.get(ext, self._fallback)

        if parser is None:
            logger.warning(f"No parser registered for .{ext}, skipping: {source_name}")
            return []

        try:
            docs = parser.parse(file_path, source_name)
            logger.info(f"Parsed {source_name} (.{ext}) → {len(docs)} documents")
            return docs
        except Exception as e:
            logger.error(f"Error parsing {source_name} (.{ext}): {e}")
            return []

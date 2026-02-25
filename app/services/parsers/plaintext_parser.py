from typing import List
from langchain_core.documents import Document
from app.services.parser_registry import BaseParser
from app.core.logging import logger


class PlainTextParser(BaseParser):
    """Fallback parser for plain text files (.txt, .md, .log, .json, etc.)."""
    supported_extensions = ["txt", "md", "log", "json", "xml", "yaml", "yml"]

    def parse(self, file_path: str, source_name: str) -> List[Document]:
        # Try UTF-8 first, fallback to latin-1
        for encoding in ("utf-8", "latin-1"):
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    text = f.read()
                break
            except UnicodeDecodeError:
                continue
        else:
            logger.error(f"Could not decode {source_name}")
            return []

        if not text.strip():
            return []

        content = self._inject_header(source_name, "Página", 1) + text

        return [Document(
            page_content=content,
            metadata=self._make_metadata(
                source=source_name, page=1, total=1,
                fmt=file_path.rsplit(".", 1)[-1].lower()
            ),
        )]

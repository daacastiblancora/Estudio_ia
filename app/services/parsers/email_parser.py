import email
from email import policy
from typing import List
from langchain_core.documents import Document
from app.services.parser_registry import BaseParser
from app.core.logging import logger

try:
    import extract_msg
except ImportError:
    extract_msg = None


class EmailParser(BaseParser):
    """Parses .eml (stdlib) and .msg (Outlook) email files."""
    supported_extensions = ["eml", "msg"]

    def parse(self, file_path: str, source_name: str) -> List[Document]:
        if file_path.lower().endswith(".msg"):
            return self._parse_msg(file_path, source_name)
        return self._parse_eml(file_path, source_name)

    def _parse_eml(self, file_path: str, source_name: str) -> List[Document]:
        with open(file_path, "rb") as f:
            msg = email.message_from_binary_file(f, policy=policy.default)

        subject = msg.get("Subject", "Sin asunto")
        sender = msg.get("From", "Desconocido")
        date = msg.get("Date", "")
        body = msg.get_body(preferencelist=("plain", "html"))
        text = body.get_content() if body else ""

        content = self._inject_header(source_name, "Página", 1)
        content += f"De: {sender}\nAsunto: {subject}\nFecha: {date}\n\n{text}"

        return [Document(
            page_content=content,
            metadata=self._make_metadata(
                source=source_name, page=1, total=1,
                fmt="eml", section=subject
            ),
        )]

    def _parse_msg(self, file_path: str, source_name: str) -> List[Document]:
        if extract_msg is None:
            logger.error("extract-msg not installed. Run: pip install extract-msg")
            return []

        msg = extract_msg.Message(file_path)
        subject = msg.subject or "Sin asunto"
        sender = msg.sender or "Desconocido"
        date = str(msg.date) if msg.date else ""
        body = msg.body or ""
        msg.close()

        content = self._inject_header(source_name, "Página", 1)
        content += f"De: {sender}\nAsunto: {subject}\nFecha: {date}\n\n{body}"

        return [Document(
            page_content=content,
            metadata=self._make_metadata(
                source=source_name, page=1, total=1,
                fmt="msg", section=subject
            ),
        )]

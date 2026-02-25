"""
Ingestion endpoint — Hardened with authentication, file validation, and security checks.
"""
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status

from app.models.schemas import IngestResponse
from app.models.sql_schemas import User
from app.services.ingestion import ingestion_service
from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()

# Allowed extensions from config (parsed once)
ALLOWED_EXTENSIONS = {
    ext.strip().lower()
    for ext in settings.ALLOWED_UPLOAD_EXTENSIONS.split(",")
}

MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def _validate_file_extension(filename: str) -> str:
    """Validate file extension against the allow-list. Returns the extension."""
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no tiene nombre.",
        )
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Tipo de archivo '{ext}' no permitido. "
                f"Formatos aceptados: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )
    return ext


async def _validate_file_size(file: UploadFile) -> bytes:
    """Read and validate file size. Returns file content bytes."""
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo está vacío.",
        )
    if len(content) > MAX_UPLOAD_BYTES:
        size_mb = len(content) / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"El archivo excede el límite de {settings.MAX_UPLOAD_SIZE_MB}MB. "
                f"Tamaño recibido: {size_mb:.1f}MB."
            ),
        )
    # Reset file position so ingestion can read it
    await file.seek(0)
    return content


def _check_encrypted_pdf(content: bytes, filename: str) -> None:
    """Detect encrypted/password-protected PDFs."""
    if not filename.lower().endswith(".pdf"):
        return

    # Quick check for PDF encryption markers
    header = content[:2048]
    try:
        header_str = header.decode("latin-1")
    except Exception:
        return

    # PDF encryption is indicated by /Encrypt in the trailer/xref
    if "/Encrypt" in header_str:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"El archivo '{filename}' está protegido con contraseña. "
                "Por favor suba una versión sin protección."
            ),
        )

    # Also check if it's actually a PDF
    if not header_str.startswith("%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"El archivo '{filename}' no es un PDF válido. "
                "La cabecera del archivo no coincide con el formato PDF."
            ),
        )


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    """
    Ingest a document into the vector store.
    
    Requires JWT authentication. Validates:
    - File extension (allowed types only)
    - File size (max 10MB)
    - PDF encryption (rejects password-protected PDFs)
    """
    filename = file.filename or "unknown"

    logger.info(f"Ingest request from user '{current_user.email}' for file '{filename}'")

    # 1. Validate extension
    ext = _validate_file_extension(filename)

    # 2. Validate size and read content
    content = await _validate_file_size(file)

    # 3. Check for encrypted PDFs
    _check_encrypted_pdf(content, filename)

    # 4. Ingest the file
    try:
        chunks = await ingestion_service.ingest_file(file)
    except Exception as e:
        logger.error(f"Ingestion failed for '{filename}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el archivo: {str(e)}",
        )

    logger.info(f"Successfully ingested '{filename}': {chunks} chunks (user: {current_user.email})")

    return IngestResponse(
        filename=filename,
        status="success",
        message=f"Archivo procesado e indexado. {chunks} fragmentos creados.",
        chunks_created=chunks,
    )

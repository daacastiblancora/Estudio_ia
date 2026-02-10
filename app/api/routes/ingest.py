from fastapi import APIRouter, UploadFile, File
from app.models.schemas import IngestResponse
from app.services.ingestion import ingestion_service

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    chunks = await ingestion_service.ingest_file(file)
    return IngestResponse(
        filename=file.filename,
        status="success",
        message="File processed and indexed.",
        chunks_created=chunks
    )

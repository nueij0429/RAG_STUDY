from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.pdf import (
    PdfChunkRequest,
    PdfChunkResponse,
    PdfExtractRequest,
    PdfExtractResponse,
    PdfUploadResponse,
)
from app.services.chunk_service import chunk_pdf_text
from app.services.pdf_service import extract_text_from_pdf, save_pdf_file

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post("/upload", response_model=PdfUploadResponse)
async def upload_pdf(file: UploadFile = File(...)) -> PdfUploadResponse:
    try:
        result = await save_pdf_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PdfUploadResponse(**result)


@router.post("/extract", response_model=PdfExtractResponse)
def extract_pdf_text(request: PdfExtractRequest) -> PdfExtractResponse:
    try:
        result = extract_text_from_pdf(request.filename)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PdfExtractResponse(**result)


@router.post("/chunk", response_model=PdfChunkResponse)
def chunk_pdf(request: PdfChunkRequest) -> PdfChunkResponse:
    try:
        result = chunk_pdf_text(
            request.filename,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PdfChunkResponse(**result)

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.pdf import PdfUploadResponse
from app.services.pdf_service import save_pdf_file

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post("/upload", response_model=PdfUploadResponse)
async def upload_pdf(file: UploadFile = File(...)) -> PdfUploadResponse:
    try:
        result = await save_pdf_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PdfUploadResponse(**result)

from fastapi import APIRouter, HTTPException

from app.schemas.rag_schema import RagIndexRequest, RagIndexResponse
from app.services.vector_store_service import index_pdf_document

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/index", response_model=RagIndexResponse)
def index_document(request: RagIndexRequest) -> RagIndexResponse:
    try:
        result = index_pdf_document(
            filename=request.filename,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RagIndexResponse(**result)

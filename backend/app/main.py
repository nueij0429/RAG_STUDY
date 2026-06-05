from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.pdf_router import router as pdf_router
from app.api.rag_router import router as rag_router
from app.config import load_environment

load_environment()

app = FastAPI(
    title="RAG Study API",
    description="PDF RAG 챗봇 학습용 FastAPI 서버",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(pdf_router)
app.include_router(rag_router)

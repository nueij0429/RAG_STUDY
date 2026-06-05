from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="RAG Study API",
    description="PDF RAG 챗봇 학습용 FastAPI 서버",
    version="0.1.0",
)

app.include_router(health_router)

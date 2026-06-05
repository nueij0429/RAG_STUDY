from pydantic import BaseModel


class RagIndexRequest(BaseModel):
    filename: str
    chunk_size: int = 500
    chunk_overlap: int = 100


class RagIndexResponse(BaseModel):
    filename: str
    total_chunks: int
    collection_name: str
    persist_directory: str
    message: str

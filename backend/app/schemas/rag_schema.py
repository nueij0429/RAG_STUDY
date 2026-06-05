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


class RagSearchRequest(BaseModel):
    question: str
    top_k: int = 3


class SearchResultItem(BaseModel):
    rank: int
    content: str
    metadata: dict[str, str | int | float | bool | None]
    score: float


class RagSearchResponse(BaseModel):
    question: str
    top_k: int
    total_results: int
    results: list[SearchResultItem]
    message: str | None = None


class RagChatRequest(BaseModel):
    question: str
    top_k: int = 3


class RagChatResponse(BaseModel):
    question: str
    answer: str
    top_k: int
    retrieved_documents: list[SearchResultItem]

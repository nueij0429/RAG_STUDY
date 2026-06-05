from pydantic import BaseModel


class PdfUploadResponse(BaseModel):
    filename: str
    path: str
    message: str = "PDF 파일이 저장되었습니다."


class PdfExtractRequest(BaseModel):
    filename: str


class PdfExtractResponse(BaseModel):
    filename: str
    extracted_text: str
    text_length: int


class PdfChunkRequest(BaseModel):
    filename: str
    chunk_size: int = 500
    chunk_overlap: int = 100


class ChunkItem(BaseModel):
    index: int
    content: str
    length: int


class PdfChunkResponse(BaseModel):
    filename: str
    chunk_size: int
    chunk_overlap: int
    total_chunks: int
    chunks: list[ChunkItem]

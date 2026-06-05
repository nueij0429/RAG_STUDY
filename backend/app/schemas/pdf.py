from pydantic import BaseModel


class PdfUploadResponse(BaseModel):
    filename: str
    path: str
    message: str = "PDF 파일이 저장되었습니다."

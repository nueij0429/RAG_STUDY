from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "uploads"


def get_uploaded_pdf_path(filename: str) -> Path:
    safe_filename = Path(filename).name
    return UPLOAD_DIR / safe_filename


def is_pdf_file(filename: str | None, content: bytes) -> bool:
    if not filename or not filename.lower().endswith(".pdf"):
        return False
    if not content.startswith(b"%PDF"):
        return False
    return True


async def save_pdf_file(file: UploadFile) -> dict[str, str]:
    content = await file.read()

    if not is_pdf_file(file.filename, content):
        raise ValueError("PDF 파일만 업로드할 수 있습니다.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    filename = Path(file.filename).name
    save_path = UPLOAD_DIR / filename
    save_path.write_bytes(content)

    return {
        "filename": filename,
        "path": str(save_path),
    }


def extract_text_from_pdf(filename: str) -> dict[str, str | int]:
    pdf_path = get_uploaded_pdf_path(filename)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {Path(filename).name}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("PDF 파일만 처리할 수 있습니다.")

    reader = PdfReader(str(pdf_path))
    text_parts: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    extracted_text = "\n".join(text_parts).strip()

    if not extracted_text:
        raise ValueError("PDF에서 텍스트를 추출할 수 없습니다.")

    return {
        "filename": pdf_path.name,
        "extracted_text": extracted_text,
        "text_length": len(extracted_text),
    }

from pathlib import Path

from fastapi import UploadFile

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "uploads"


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

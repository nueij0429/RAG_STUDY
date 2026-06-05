from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.pdf_service import extract_text_from_pdf


def validate_chunk_params(chunk_size: int, chunk_overlap: int) -> None:
    if chunk_size <= 0:
        raise ValueError("chunk_size는 0보다 커야 합니다.")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap은 0 이상이어야 합니다.")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap은 chunk_size보다 작아야 합니다.")


def chunk_pdf_text(
    filename: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> dict[str, str | int | list[dict[str, int | str]]]:
    validate_chunk_params(chunk_size, chunk_overlap)

    extract_result = extract_text_from_pdf(filename)
    extracted_text = str(extract_result["extracted_text"])

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    text_chunks = splitter.split_text(extracted_text)

    chunks = [
        {
            "index": index,
            "content": content,
            "length": len(content),
        }
        for index, content in enumerate(text_chunks)
    ]

    return {
        "filename": extract_result["filename"],
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "total_chunks": len(chunks),
        "chunks": chunks,
    }

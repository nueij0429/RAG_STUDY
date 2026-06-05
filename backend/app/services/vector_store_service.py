from pathlib import Path

from langchain_chroma import Chroma

from app.services.chunk_service import chunk_pdf_text
from app.services.embedding_service import get_embedding_model

CHROMA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "chroma_db"
COLLECTION_NAME = "rag_documents"


def get_vector_store() -> Chroma:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=str(CHROMA_DIR),
    )


def build_chunk_id(filename: str, chunk_index: int) -> str:
    return f"{filename}::{chunk_index}"


def delete_document_chunks(filename: str) -> None:
    vector_store = get_vector_store()
    collection = vector_store._collection

    existing = collection.get(where={"filename": filename})
    if existing.get("ids"):
        collection.delete(ids=existing["ids"])


def save_chunks_to_chroma(filename: str, chunks: list[dict[str, int | str]]) -> int:
    if not chunks:
        raise ValueError("저장할 chunk가 없습니다.")

    delete_document_chunks(filename)

    vector_store = get_vector_store()
    texts = [str(chunk["content"]) for chunk in chunks]
    metadatas = [
        {
            "filename": filename,
            "chunk_index": int(chunk["index"]),
            "chunk_length": int(chunk["length"]),
        }
        for chunk in chunks
    ]
    ids = [build_chunk_id(filename, int(chunk["index"])) for chunk in chunks]

    vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    return len(chunks)


def index_pdf_document(
    filename: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> dict[str, str | int]:
    chunk_result = chunk_pdf_text(
        filename=filename,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = chunk_result["chunks"]
    assert isinstance(chunks, list)

    saved_filename = str(chunk_result["filename"])
    total_chunks = save_chunks_to_chroma(saved_filename, chunks)

    return {
        "filename": saved_filename,
        "total_chunks": total_chunks,
        "collection_name": COLLECTION_NAME,
        "persist_directory": str(CHROMA_DIR.resolve()),
        "message": "문서 인덱싱이 완료되었습니다.",
    }

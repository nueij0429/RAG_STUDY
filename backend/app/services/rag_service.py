from app.services.llm_service import generate_rag_answer
from app.services.search_service import search_similar_documents


def build_context_from_documents(results: list[dict]) -> str:
    context_parts: list[str] = []

    for document in results:
        metadata = document.get("metadata", {})
        filename = metadata.get("filename", "unknown")
        chunk_index = metadata.get("chunk_index", "-")
        context_parts.append(
            f"[문서: {filename} | chunk: {chunk_index}]\n{document['content']}"
        )

    return "\n\n---\n\n".join(context_parts)


def generate_rag_chat_response(question: str, top_k: int = 3) -> dict:
    search_result = search_similar_documents(question=question, top_k=top_k)

    if search_result["total_results"] == 0:
        message = search_result.get("message") or "검색 결과가 없습니다."
        raise ValueError(message)

    retrieved_documents = search_result["results"]
    assert isinstance(retrieved_documents, list)

    context = build_context_from_documents(retrieved_documents)
    answer = generate_rag_answer(
        question=str(search_result["question"]),
        context=context,
    )

    return {
        "question": search_result["question"],
        "answer": answer,
        "top_k": search_result["top_k"],
        "retrieved_documents": retrieved_documents,
    }

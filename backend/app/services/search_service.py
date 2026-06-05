from app.services.vector_store_service import get_vector_store

MAX_TOP_K = 20


def normalize_top_k(top_k: int) -> int:
    if top_k < 1:
        raise ValueError("top_k는 1 이상이어야 합니다.")
    if top_k > MAX_TOP_K:
        return MAX_TOP_K
    return top_k


def search_similar_documents(question: str, top_k: int = 3) -> dict:
    validated_top_k = normalize_top_k(top_k)
    normalized_question = question.strip()

    if not normalized_question:
        raise ValueError("question은 비어 있을 수 없습니다.")

    vector_store = get_vector_store()
    document_count = vector_store._collection.count()

    if document_count == 0:
        return {
            "question": normalized_question,
            "top_k": validated_top_k,
            "total_results": 0,
            "results": [],
            "message": "인덱싱된 문서가 없습니다. 먼저 /rag/index API로 문서를 인덱싱해주세요.",
        }

    search_results = vector_store.similarity_search_with_score(
        normalized_question,
        k=validated_top_k,
    )

    if not search_results:
        return {
            "question": normalized_question,
            "top_k": validated_top_k,
            "total_results": 0,
            "results": [],
            "message": "검색 결과가 없습니다.",
        }

    results = [
        {
            "rank": rank,
            "content": document.page_content,
            "metadata": document.metadata,
            "score": float(distance),
        }
        for rank, (document, distance) in enumerate(search_results, start=1)
    ]

    return {
        "question": normalized_question,
        "top_k": validated_top_k,
        "total_results": len(results),
        "results": results,
        "message": None,
    }

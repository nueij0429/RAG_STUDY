from datetime import datetime

from app.services.search_service import search_similar_documents

DOCUMENT_SEARCH_TOOL_NAME = "document_search"
CURRENT_TIME_TOOL_NAME = "current_time"
JSON_FORMAT_TOOL_NAME = "json_formatter"


def run_document_search_tool(question: str, top_k: int) -> dict:
    return search_similar_documents(question=question, top_k=top_k)


def run_current_time_tool() -> str:
    now = datetime.now()
    return f"현재 시간은 {now.strftime('%Y-%m-%d %H:%M:%S')} 입니다."


def build_references(search_results: list[dict]) -> list[dict]:
    references: list[dict] = []

    for document in search_results:
        metadata = document.get("metadata", {})
        content = str(document.get("content", ""))
        preview = content[:200]
        if len(content) > 200:
            preview += "..."

        references.append(
            {
                "filename": metadata.get("filename"),
                "chunk_index": metadata.get("chunk_index"),
                "score": document.get("score"),
                "content_preview": preview,
            }
        )

    return references


def run_json_format_tool(
    answer: str,
    used_tools: list[str],
    references: list[dict],
) -> dict:
    return {
        "answer": answer,
        "used_tools": used_tools,
        "references": references,
    }

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.services.agent_tools import (
    CURRENT_TIME_TOOL_NAME,
    DOCUMENT_SEARCH_TOOL_NAME,
    JSON_FORMAT_TOOL_NAME,
    build_references,
    run_current_time_tool,
    run_document_search_tool,
    run_json_format_tool,
)
from app.services.llm_service import generate_agent_answer, get_groq_api_key
from app.services.rag_service import build_context_from_documents
from app.services.search_service import normalize_top_k


class AgentState(TypedDict):
    question: str
    top_k: int
    search_results: list[dict]
    current_time: str
    answer: str
    used_tools: list[str]
    references: list[dict]
    final_response: dict


def _search_documents_node(state: AgentState) -> dict:
    search_result = run_document_search_tool(
        question=state["question"],
        top_k=state["top_k"],
    )
    search_results = search_result.get("results", [])
    assert isinstance(search_results, list)

    return {
        "search_results": search_results,
        "used_tools": [*state["used_tools"], DOCUMENT_SEARCH_TOOL_NAME],
    }


def _get_current_time_node(state: AgentState) -> dict:
    return {
        "current_time": run_current_time_tool(),
        "used_tools": [*state["used_tools"], CURRENT_TIME_TOOL_NAME],
    }


def _generate_answer_node(state: AgentState) -> dict:
    if state["search_results"]:
        context = build_context_from_documents(state["search_results"])
    else:
        context = "검색된 문서가 없습니다."

    answer = generate_agent_answer(
        question=state["question"],
        context=context,
        current_time=state["current_time"],
    )

    return {"answer": answer}


def _format_json_response_node(state: AgentState) -> dict:
    references = build_references(state["search_results"])
    used_tools = [*state["used_tools"], JSON_FORMAT_TOOL_NAME]
    final_response = run_json_format_tool(
        answer=state["answer"],
        used_tools=used_tools,
        references=references,
    )

    return {
        "references": references,
        "used_tools": used_tools,
        "final_response": final_response,
    }


def _build_agent_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node("search_documents", _search_documents_node)
    workflow.add_node("get_current_time", _get_current_time_node)
    workflow.add_node("generate_answer", _generate_answer_node)
    workflow.add_node("format_json_response", _format_json_response_node)

    workflow.add_edge(START, "search_documents")
    workflow.add_edge("search_documents", "get_current_time")
    workflow.add_edge("get_current_time", "generate_answer")
    workflow.add_edge("generate_answer", "format_json_response")
    workflow.add_edge("format_json_response", END)

    return workflow.compile()


_agent_workflow = None


def get_agent_workflow():
    global _agent_workflow

    if _agent_workflow is None:
        _agent_workflow = _build_agent_workflow()

    return _agent_workflow


def run_agent_chat(question: str, top_k: int = 3) -> dict:
    if not get_groq_api_key():
        raise ValueError(
            "GROQ_API_KEY가 설정되지 않았습니다. 프로젝트 루트의 .env 파일을 확인해주세요."
        )

    normalized_question = question.strip()
    if not normalized_question:
        raise ValueError("question은 비어 있을 수 없습니다.")

    validated_top_k = normalize_top_k(top_k)
    initial_state: AgentState = {
        "question": normalized_question,
        "top_k": validated_top_k,
        "search_results": [],
        "current_time": "",
        "answer": "",
        "used_tools": [],
        "references": [],
        "final_response": {},
    }

    final_state = get_agent_workflow().invoke(initial_state)
    final_response = final_state["final_response"]

    return {
        "question": normalized_question,
        "top_k": validated_top_k,
        "answer": final_response["answer"],
        "used_tools": final_response["used_tools"],
        "references": final_response["references"],
        "current_time": final_state["current_time"],
    }

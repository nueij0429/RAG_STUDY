from fastapi import APIRouter, HTTPException

from app.schemas.agent_schema import AgentChatRequest, AgentChatResponse
from app.services.agent_service import run_agent_chat

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(request: AgentChatRequest) -> AgentChatResponse:
    try:
        result = run_agent_chat(
            question=request.question,
            top_k=request.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AgentChatResponse(**result)

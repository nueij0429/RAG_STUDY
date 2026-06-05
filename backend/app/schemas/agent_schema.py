from pydantic import BaseModel


class AgentChatRequest(BaseModel):
    question: str
    top_k: int = 3


class AgentReference(BaseModel):
    filename: str | int | float | bool | None = None
    chunk_index: str | int | float | bool | None = None
    score: float | None = None
    content_preview: str


class AgentChatResponse(BaseModel):
    question: str
    top_k: int
    answer: str
    used_tools: list[str]
    references: list[AgentReference]
    current_time: str

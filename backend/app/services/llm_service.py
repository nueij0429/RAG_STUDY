import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

RAG_SYSTEM_PROMPT = """당신은 제공된 context만을 기반으로 답변하는 RAG 어시스턴트입니다.

규칙:
1. 반드시 제공된 context를 기반으로 답변하세요.
2. context에 없는 내용은 추측하지 마세요.
3. context에서 확인할 수 없는 경우 "제공된 문서에서 확인할 수 없습니다."라고 답하세요.
4. 답변은 반드시 한국어로 작성하세요."""

RAG_USER_PROMPT_TEMPLATE = """다음 context를 참고하여 질문에 답변해주세요.

[context]
{context}

[질문]
{question}"""

DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"


def get_groq_api_key() -> str | None:
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return api_key.strip()
    return None


def get_groq_model() -> str:
    model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
    return model.strip() if model else DEFAULT_GROQ_MODEL


def generate_rag_answer(question: str, context: str) -> str:
    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY가 설정되지 않았습니다. 프로젝트 루트의 .env 파일을 확인해주세요."
        )

    llm = ChatGroq(
        groq_api_key=api_key,
        model=get_groq_model(),
        temperature=0,
    )

    messages = [
        SystemMessage(content=RAG_SYSTEM_PROMPT),
        HumanMessage(
            content=RAG_USER_PROMPT_TEMPLATE.format(
                context=context,
                question=question,
            )
        ),
    ]

    response = llm.invoke(messages)
    content = response.content

    if isinstance(content, str):
        return content

    return str(content)

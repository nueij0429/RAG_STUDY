import httpx
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="PDF RAG Chatbot + Agent Test Page")
st.title("PDF RAG Chatbot + Agent Test Page")

if st.button("FastAPI 서버 상태 확인"):
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{API_BASE_URL}/health")
            response.raise_for_status()
            data = response.json()

        st.success("FastAPI 서버가 정상 동작 중입니다.")
        st.json(data)
    except httpx.ConnectError:
        st.error(
            "FastAPI 서버에 연결할 수 없습니다. "
            "backend에서 uvicorn 서버가 실행 중인지 확인해주세요."
        )
    except httpx.HTTPStatusError as exc:
        st.error(f"HTTP 오류가 발생했습니다. (상태 코드: {exc.response.status_code})")
    except Exception as exc:
        st.error(f"요청 중 오류가 발생했습니다: {exc}")

st.divider()
st.subheader("PDF 업로드")

uploaded_file = st.file_uploader("PDF 파일을 선택하세요", type=["pdf"])

if uploaded_file is not None and st.button("PDF 업로드"):
    try:
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf",
            )
        }
        with httpx.Client(timeout=30.0) as client:
            response = client.post(f"{API_BASE_URL}/pdf/upload", files=files)

        if response.status_code == 200:
            data = response.json()
            st.success(data.get("message", "PDF 업로드에 성공했습니다."))
            st.write(f"**저장된 파일명:** {data['filename']}")
            st.write(f"**저장 경로:** {data['path']}")
        else:
            detail = response.json().get("detail", response.text)
            st.error(f"업로드 실패: {detail}")
    except httpx.ConnectError:
        st.error(
            "FastAPI 서버에 연결할 수 없습니다. "
            "backend에서 uvicorn 서버가 실행 중인지 확인해주세요."
        )
    except Exception as exc:
        st.error(f"업로드 중 오류가 발생했습니다: {exc}")

st.divider()
st.subheader("PDF 텍스트 추출")

extract_filename = st.text_input(
    "추출할 PDF 파일명",
    placeholder="example.pdf",
)

if extract_filename and st.button("텍스트 추출"):
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_BASE_URL}/pdf/extract",
                json={"filename": extract_filename},
            )

        if response.status_code == 200:
            data = response.json()
            st.success(f"텍스트 추출 완료 (글자 수: {data['text_length']})")
            st.write(f"**파일명:** {data['filename']}")
            st.text_area("추출된 텍스트", value=data["extracted_text"], height=300)
        else:
            detail = response.json().get("detail", response.text)
            st.error(f"텍스트 추출 실패: {detail}")
    except httpx.ConnectError:
        st.error(
            "FastAPI 서버에 연결할 수 없습니다. "
            "backend에서 uvicorn 서버가 실행 중인지 확인해주세요."
        )
    except Exception as exc:
        st.error(f"텍스트 추출 중 오류가 발생했습니다: {exc}")

st.divider()
st.subheader("PDF 문서 Chunking")

chunk_filename = st.text_input(
    "Chunking할 PDF 파일명",
    placeholder="example.pdf",
    key="chunk_filename",
)

col1, col2 = st.columns(2)
with col1:
    chunk_size = st.number_input("chunk_size", min_value=1, value=500)
with col2:
    chunk_overlap = st.number_input("chunk_overlap", min_value=0, value=100)

if chunk_filename and st.button("Chunking 실행"):
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_BASE_URL}/pdf/chunk",
                json={
                    "filename": chunk_filename,
                    "chunk_size": int(chunk_size),
                    "chunk_overlap": int(chunk_overlap),
                },
            )

        if response.status_code == 200:
            data = response.json()
            st.success(
                f"Chunking 완료 (total_chunks: {data['total_chunks']}, "
                f"chunk_size: {data['chunk_size']}, "
                f"chunk_overlap: {data['chunk_overlap']})"
            )
            st.write(f"**파일명:** {data['filename']}")

            for chunk in data["chunks"]:
                preview = chunk["content"][:200]
                if len(chunk["content"]) > 200:
                    preview += "..."
                st.write(f"**Chunk {chunk['index']}** (length: {chunk['length']})")
                st.text(preview)
        else:
            detail = response.json().get("detail", response.text)
            st.error(f"Chunking 실패: {detail}")
    except httpx.ConnectError:
        st.error(
            "FastAPI 서버에 연결할 수 없습니다. "
            "backend에서 uvicorn 서버가 실행 중인지 확인해주세요."
        )
    except Exception as exc:
        st.error(f"Chunking 중 오류가 발생했습니다: {exc}")

st.divider()
st.subheader("문서 인덱싱")

index_filename = st.text_input(
    "인덱싱할 PDF 파일명",
    placeholder="example.pdf",
    key="index_filename",
)

index_col1, index_col2 = st.columns(2)
with index_col1:
    index_chunk_size = st.number_input(
        "chunk_size",
        min_value=1,
        value=500,
        key="index_chunk_size",
    )
with index_col2:
    index_chunk_overlap = st.number_input(
        "chunk_overlap",
        min_value=0,
        value=100,
        key="index_chunk_overlap",
    )

if index_filename and st.button("문서 인덱싱 실행"):
    try:
        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                f"{API_BASE_URL}/rag/index",
                json={
                    "filename": index_filename,
                    "chunk_size": int(index_chunk_size),
                    "chunk_overlap": int(index_chunk_overlap),
                },
            )

        if response.status_code == 200:
            data = response.json()
            st.success(data.get("message", "문서 인덱싱에 성공했습니다."))
            st.write(f"**파일명:** {data['filename']}")
            st.write(f"**total_chunks:** {data['total_chunks']}")
            st.write(f"**collection_name:** {data['collection_name']}")
            st.write(f"**저장 경로:** {data['persist_directory']}")
        else:
            detail = response.json().get("detail", response.text)
            st.error(f"문서 인덱싱 실패: {detail}")
    except httpx.ConnectError:
        st.error(
            "FastAPI 서버에 연결할 수 없습니다. "
            "backend에서 uvicorn 서버가 실행 중인지 확인해주세요."
        )
    except Exception as exc:
        st.error(f"문서 인덱싱 중 오류가 발생했습니다: {exc}")

st.divider()
st.subheader("질문 기반 문서 검색")

search_question = st.text_input(
    "질문을 입력하세요",
    placeholder="RAG란 무엇인가?",
    key="search_question",
)
search_top_k = st.number_input(
    "top_k",
    min_value=1,
    max_value=20,
    value=3,
    key="search_top_k",
)

if search_question and st.button("문서 검색"):
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{API_BASE_URL}/rag/search",
                json={
                    "question": search_question,
                    "top_k": int(search_top_k),
                },
            )

        if response.status_code == 200:
            data = response.json()

            if data["total_results"] == 0:
                st.warning(data.get("message", "검색 결과가 없습니다."))
            else:
                st.success(f"검색 완료 (total_results: {data['total_results']})")

            for result in data["results"]:
                metadata = result.get("metadata", {})
                filename = metadata.get("filename", "-")
                chunk_index = metadata.get("chunk_index", "-")
                preview = result["content"][:200]
                if len(result["content"]) > 200:
                    preview += "..."

                st.write(
                    f"**Rank {result['rank']}** | "
                    f"score: {result['score']:.4f} | "
                    f"filename: {filename} | "
                    f"chunk_index: {chunk_index}"
                )
                st.text(preview)
        else:
            detail = response.json().get("detail", response.text)
            st.error(f"문서 검색 실패: {detail}")
    except httpx.ConnectError:
        st.error(
            "FastAPI 서버에 연결할 수 없습니다. "
            "backend에서 uvicorn 서버가 실행 중인지 확인해주세요."
        )
    except Exception as exc:
        st.error(f"문서 검색 중 오류가 발생했습니다: {exc}")

st.divider()
st.subheader("RAG 질문 답변")

chat_question = st.text_input(
    "질문을 입력하세요",
    placeholder="RAG란 무엇인가?",
    key="chat_question",
)
chat_top_k = st.number_input(
    "top_k",
    min_value=1,
    max_value=20,
    value=3,
    key="chat_top_k",
)

if chat_question and st.button("RAG 답변 생성"):
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{API_BASE_URL}/rag/chat",
                json={
                    "question": chat_question,
                    "top_k": int(chat_top_k),
                },
            )

        if response.status_code == 200:
            data = response.json()
            st.success("RAG 답변 생성 완료")
            st.write("**LLM 답변**")
            st.write(data["answer"])

            st.write("**참고 문서**")
            for document in data["retrieved_documents"]:
                metadata = document.get("metadata", {})
                filename = metadata.get("filename", "-")
                chunk_index = metadata.get("chunk_index", "-")
                preview = document["content"][:200]
                if len(document["content"]) > 200:
                    preview += "..."

                st.write(
                    f"**Rank {document['rank']}** | "
                    f"score: {document['score']:.4f} | "
                    f"filename: {filename} | "
                    f"chunk_index: {chunk_index}"
                )
                st.text(preview)
        else:
            detail = response.json().get("detail", response.text)
            st.error(f"RAG 답변 생성 실패: {detail}")
    except httpx.ConnectError:
        st.error(
            "FastAPI 서버에 연결할 수 없습니다. "
            "backend에서 uvicorn 서버가 실행 중인지 확인해주세요."
        )
    except Exception as exc:
        st.error(f"RAG 답변 생성 중 오류가 발생했습니다: {exc}")

st.divider()
st.subheader("LangGraph Agent 테스트")

agent_question = st.text_input(
    "질문을 입력하세요",
    placeholder="RAG란 무엇인가?",
    key="agent_question",
)
agent_top_k = st.number_input(
    "top_k",
    min_value=1,
    max_value=20,
    value=3,
    key="agent_top_k",
)

if agent_question and st.button("Agent 실행"):
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{API_BASE_URL}/agent/chat",
                json={
                    "question": agent_question,
                    "top_k": int(agent_top_k),
                },
            )

        if response.status_code == 200:
            data = response.json()
            st.success("Agent 실행 완료")
            st.write("**Agent 최종 답변**")
            st.write(data["answer"])
            st.write(f"**현재 시간:** {data['current_time']}")

            st.write("**사용한 Tool 목록**")
            for tool_name in data["used_tools"]:
                st.write(f"- {tool_name}")

            st.write("**참고 문서 목록**")
            if not data["references"]:
                st.info("참고 문서가 없습니다.")
            else:
                for reference in data["references"]:
                    st.write(
                        f"- filename: {reference.get('filename', '-')} | "
                        f"chunk_index: {reference.get('chunk_index', '-')} | "
                        f"score: {reference.get('score', '-')}"
                    )
                    st.text(reference.get("content_preview", ""))
        else:
            detail = response.json().get("detail", response.text)
            st.error(f"Agent 실행 실패: {detail}")
    except httpx.ConnectError:
        st.error(
            "FastAPI 서버에 연결할 수 없습니다. "
            "backend에서 uvicorn 서버가 실행 중인지 확인해주세요."
        )
    except Exception as exc:
        st.error(f"Agent 실행 중 오류가 발생했습니다: {exc}")

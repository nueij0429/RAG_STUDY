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

import httpx
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="PDF RAG Chatbot + Agent Test Page")
st.title("PDF RAG Chatbot + Agent Test Page")

st.write("FastAPI 백엔드 서버와의 연결 상태를 확인할 수 있는 테스트 페이지입니다.")

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

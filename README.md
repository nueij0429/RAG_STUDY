# RAG_STUDY

FastAPI 기반 PDF RAG 챗봇 학습용 프로젝트입니다.

## 개발 환경

- Python 3.10+
- 가상환경(venv) 사용 권장

## 설치

```bash
# 프로젝트 루트에서
python -m venv venv

# Windows
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## FastAPI 서버 실행

```bash
# backend 디렉터리에서 실행
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Streamlit 실행

FastAPI 서버를 먼저 실행한 뒤, 별도 터미널에서 Streamlit을 실행합니다.

```bash
# 프로젝트 루트에서 실행
streamlit run frontend/streamlit_app.py
```

브라우저에서 Streamlit 페이지가 열리면 **FastAPI 서버 상태 확인** 버튼을 눌러 `/health` API 응답을 확인합니다.

| 항목 | 값 |
|------|-----|
| Streamlit 페이지 | http://localhost:8501 |

## API 테스트

서버 실행 후 브라우저 또는 curl로 확인합니다.

| 항목 | 값 |
|------|-----|
| Health Check | http://127.0.0.1:8000/health |
| PDF Upload | POST http://127.0.0.1:8000/pdf/upload |
| PDF Extract | POST http://127.0.0.1:8000/pdf/extract |
| PDF Chunk | POST http://127.0.0.1:8000/pdf/chunk |
| RAG Index | POST http://127.0.0.1:8000/rag/index |
| RAG Search | POST http://127.0.0.1:8000/rag/search |
| RAG Chat | POST http://127.0.0.1:8000/rag/chat |
| Swagger UI | http://127.0.0.1:8000/docs |

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

예상 응답:

```json
{"status": "ok"}
```

### PDF 업로드 API

- **Method:** POST
- **URL:** `/pdf/upload`
- **Content-Type:** `multipart/form-data`
- **Field:** `file` (PDF 파일)
- **저장 위치:** `backend/data/uploads/`

```bash
curl -X POST http://127.0.0.1:8000/pdf/upload -F "file=@sample.pdf"
```

성공 응답 예시:

```json
{
  "filename": "sample.pdf",
  "path": "C:\\study\\backend\\data\\uploads\\sample.pdf",
  "message": "PDF 파일이 저장되었습니다."
}
```

PDF가 아닌 파일을 업로드하면 `400` 오류와 함께 아래 메시지가 반환됩니다.

```json
{"detail": "PDF 파일만 업로드할 수 있습니다."}
```

### PDF 텍스트 추출 API

- **Method:** POST
- **URL:** `/pdf/extract`
- **Content-Type:** `application/json`
- **Body:** `{"filename": "sample.pdf"}`
- **대상 경로:** `backend/data/uploads/` 에 저장된 PDF 파일

```bash
curl -X POST http://127.0.0.1:8000/pdf/extract -H "Content-Type: application/json" -d "{\"filename\": \"sample.pdf\"}"
```

성공 응답 예시:

```json
{
  "filename": "sample.pdf",
  "extracted_text": "추출된 PDF 텍스트...",
  "text_length": 1234
}
```

에러 응답 예시:

```json
{"detail": "PDF 파일을 찾을 수 없습니다: sample.pdf"}
```

```json
{"detail": "PDF에서 텍스트를 추출할 수 없습니다."}
```

### PDF Chunking API

- **Method:** POST
- **URL:** `/pdf/chunk`
- **Content-Type:** `application/json`
- **Body:**
  - `filename` (필수): 업로드된 PDF 파일명
  - `chunk_size` (선택, 기본값 500): chunk 크기
  - `chunk_overlap` (선택, 기본값 100): chunk 겹침 크기
- **조건:** `chunk_overlap` 은 `chunk_size` 보다 작아야 합니다.

```bash
curl -X POST http://127.0.0.1:8000/pdf/chunk -H "Content-Type: application/json" -d "{\"filename\": \"sample.pdf\", \"chunk_size\": 500, \"chunk_overlap\": 100}"
```

성공 응답 예시:

```json
{
  "filename": "sample.pdf",
  "chunk_size": 500,
  "chunk_overlap": 100,
  "total_chunks": 12,
  "chunks": [
    {
      "index": 0,
      "content": "첫 번째 chunk 내용...",
      "length": 480
    }
  ]
}
```

에러 응답 예시:

```json
{"detail": "chunk_overlap은 chunk_size보다 작아야 합니다."}
```

### 문서 인덱싱 API

- **Method:** POST
- **URL:** `/rag/index`
- **Content-Type:** `application/json`
- **Body:**
  - `filename` (필수): 업로드된 PDF 파일명
  - `chunk_size` (선택, 기본값 500): chunk 크기
  - `chunk_overlap` (선택, 기본값 100): chunk 겹침 크기
- **처리 흐름:** PDF 텍스트 추출 → chunking → embedding 생성 → Chroma DB 저장
- **Embedding 모델:** `all-MiniLM-L6-v2` (sentence-transformers)
- **Chroma 저장 경로:** `backend/data/chroma_db/`
- **Collection 이름:** `rag_documents`
- **중복 처리:** 같은 PDF를 다시 인덱싱하면 해당 `filename`의 기존 chunk를 먼저 삭제한 뒤, `{filename}::{chunk_index}` id로 새로 저장합니다.

```bash
curl -X POST http://127.0.0.1:8000/rag/index -H "Content-Type: application/json" -d "{\"filename\": \"sample.pdf\", \"chunk_size\": 500, \"chunk_overlap\": 100}"
```

성공 응답 예시:

```json
{
  "filename": "sample.pdf",
  "total_chunks": 12,
  "collection_name": "rag_documents",
  "persist_directory": "C:\\study\\backend\\data\\chroma_db",
  "message": "문서 인덱싱이 완료되었습니다."
}
```

에러 응답 예시:

```json
{"detail": "PDF 파일을 찾을 수 없습니다: sample.pdf"}
```

### 유사 문서 검색 API

- **Method:** POST
- **URL:** `/rag/search`
- **Content-Type:** `application/json`
- **Body:**
  - `question` (필수): 검색 질문
  - `top_k` (선택, 기본값 3): 반환할 유사 chunk 개수 (최대 20)
- **검색 대상:** `rag_documents` collection에 저장된 chunk
- **score:** Chroma `similarity_search_with_score` 결과값 (distance, 값이 작을수록 더 유사)

```bash
curl -X POST http://127.0.0.1:8000/rag/search -H "Content-Type: application/json" -d "{\"question\": \"RAG란 무엇인가?\", \"top_k\": 3}"
```

성공 응답 예시:

```json
{
  "question": "RAG란 무엇인가?",
  "top_k": 3,
  "total_results": 3,
  "results": [
    {
      "rank": 1,
      "content": "RAG(Retrieval-Augmented Generation)는 ...",
      "metadata": {
        "filename": "sample.pdf",
        "chunk_index": 3,
        "chunk_length": 495
      },
      "score": 1.18
    }
  ],
  "message": null
}
```

검색 결과가 없을 때:

```json
{
  "question": "질문 내용",
  "top_k": 3,
  "total_results": 0,
  "results": [],
  "message": "인덱싱된 문서가 없습니다. 먼저 /rag/index API로 문서를 인덱싱해주세요."
}
```

에러 응답 예시:

```json
{"detail": "question은 비어 있을 수 없습니다."}
```

### RAG 질문 답변 API

- **Method:** POST
- **URL:** `/rag/chat`
- **Content-Type:** `application/json`
- **Body:**
  - `question` (필수): 사용자 질문
  - `top_k` (선택, 기본값 3): 참고할 유사 chunk 개수 (최대 20)
- **처리 흐름:** 질문 입력 → Chroma 유사 문서 검색 → context 구성 → Groq LLM 답변 생성
- **LLM:** LangChain `ChatGroq` (`langchain-groq`)
- **환경변수:** 프로젝트 루트 `.env` 파일
  - `GROQ_API_KEY` (필수, API 호출 시)
  - `GROQ_MODEL` (선택, 기본값 `llama-3.1-8b-instant`)

`.env` 예시:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

```bash
curl -X POST http://127.0.0.1:8000/rag/chat -H "Content-Type: application/json" -d "{\"question\": \"RAG란 무엇인가?\", \"top_k\": 3}"
```

성공 응답 예시:

```json
{
  "question": "RAG란 무엇인가?",
  "answer": "RAG(Retrieval-Augmented Generation)는 검색으로 찾은 문서를 기반으로 LLM이 답변을 생성하는 방식입니다.",
  "top_k": 3,
  "retrieved_documents": [
    {
      "rank": 1,
      "content": "RAG(Retrieval-Augmented Generation)는 ...",
      "metadata": {
        "filename": "sample.pdf",
        "chunk_index": 3,
        "chunk_length": 495
      },
      "score": 1.18
    }
  ]
}
```

에러 응답 예시:

```json
{"detail": "GROQ_API_KEY가 설정되지 않았습니다. 프로젝트 루트의 .env 파일을 확인해주세요."}
```

```json
{"detail": "인덱싱된 문서가 없습니다. 먼저 /rag/index API로 문서를 인덱싱해주세요."}
```

### Streamlit PDF 업로드 테스트

1. FastAPI 서버와 Streamlit을 각각 실행합니다.
2. Streamlit 페이지(http://localhost:8501) 에서 **PDF 파일을 선택**합니다.
3. **PDF 업로드** 버튼을 클릭합니다.
4. 성공 시 저장된 파일명과 경로가 화면에 표시됩니다.

### Streamlit PDF 텍스트 추출 테스트

1. 먼저 PDF를 업로드해 `backend/data/uploads/` 에 저장합니다.
2. Streamlit 페이지의 **PDF 텍스트 추출** 영역에 파일명을 입력합니다.
3. **텍스트 추출** 버튼을 클릭합니다.
4. 성공 시 추출된 텍스트와 글자 수가 화면에 표시됩니다.

### Streamlit PDF Chunking 테스트

1. 먼저 PDF를 업로드해 `backend/data/uploads/` 에 저장합니다.
2. Streamlit 페이지의 **PDF 문서 Chunking** 영역에 파일명을 입력합니다.
3. `chunk_size`, `chunk_overlap` 값을 설정합니다.
4. **Chunking 실행** 버튼을 클릭합니다.
5. 성공 시 `total_chunks`와 각 chunk의 일부 내용이 화면에 표시됩니다.

### Streamlit 문서 인덱싱 테스트

1. 먼저 PDF를 업로드해 `backend/data/uploads/` 에 저장합니다.
2. Streamlit 페이지의 **문서 인덱싱** 영역에 파일명을 입력합니다.
3. `chunk_size`, `chunk_overlap` 값을 설정합니다.
4. **문서 인덱싱 실행** 버튼을 클릭합니다.
5. 성공 시 `total_chunks`, `collection_name`, 저장 경로, `message`가 화면에 표시됩니다.
6. 첫 실행 시 embedding 모델 다운로드로 시간이 다소 걸릴 수 있습니다.

### Streamlit 질문 기반 문서 검색 테스트

1. 먼저 PDF를 업로드하고 **문서 인덱싱**을 완료합니다.
2. Streamlit 페이지의 **질문 기반 문서 검색** 영역에 질문을 입력합니다.
3. `top_k` 값을 설정합니다.
4. **문서 검색** 버튼을 클릭합니다.
5. 성공 시 rank, score, filename, chunk_index, content 일부가 화면에 표시됩니다.

### Streamlit RAG 질문 답변 테스트

1. `.env` 파일에 `GROQ_API_KEY`와 `GROQ_MODEL`을 설정합니다.
2. PDF를 업로드하고 **문서 인덱싱**을 완료합니다.
3. Streamlit 페이지의 **RAG 질문 답변** 영역에 질문을 입력합니다.
4. **RAG 답변 생성** 버튼을 클릭합니다.
5. 성공 시 LLM 답변과 참고 문서 목록이 함께 표시됩니다.

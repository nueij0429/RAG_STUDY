# RAG_STUDY

PDF 문서를 업로드하고, RAG(Retrieval-Augmented Generation) 파이프라인을 단계별로 구현한 학습용 프로젝트입니다.  
FastAPI 백엔드와 Streamlit 프론트엔드를 분리해 **PDF 기반 RAG 챗봇**과 **LangGraph Agent 테스트 페이지**를 함께 제공합니다.

외부 라이브러리에 전체 흐름을 위임하지 않고, `PDF 업로드 → 텍스트 추출 → chunking → embedding → Chroma 저장 → 유사 문서 검색 → Groq LLM 답변 생성`까지의 과정을 api·service·schema 단위로 구성했습니다.
또한 LangGraph `StateGraph`로 Tool 3개를 순차 실행하는 단순 Agent workflow를 추가해, RAG와 Agent의 기본 동작을 한 프로젝트에서 확인할 수 있습니다.

## 목차

1. [기술 스택](#1-기술-스택)
2. [전체 아키텍처](#2-전체-아키텍처)
3. [RAG 처리 흐름](#3-rag-처리-흐름)
4. [LangGraph Agent 처리 흐름](#4-langgraph-agent-처리-흐름)
5. [주요 기능](#5-주요-기능)
6. [프로젝트 구조](#6-프로젝트-구조)
7. [환경변수 설정](#7-환경변수-설정)
8. [설치 및 실행](#8-설치-및-실행)
9. [로컬 테스트 결과](#9-로컬-테스트-결과)
10. [API 테스트](#10-api-테스트)
11. [Streamlit 테스트](#11-streamlit-테스트)
12. [구현 중 고려한 예외 처리](#12-구현-중-고려한-예외-처리)

---

## 1. 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | Streamlit |
| Backend | FastAPI, Uvicorn |
| RAG Framework | LangChain |
| Text Splitter | LangChain `RecursiveCharacterTextSplitter` |
| PDF 처리 | pypdf |
| Embedding | HuggingFace sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector DB | Chroma |
| LLM | Groq API (`langchain-groq` / `ChatGroq`) |
| Agent | LangGraph (`StateGraph`) |
| 기타 | python-dotenv, httpx, Pydantic |

---

## 2. 전체 아키텍처

```
[Streamlit UI]  ──HTTP──▶  [FastAPI Backend]
                              │
                              ├─ PDF Router      (upload / extract / chunk)
                              ├─ RAG Router      (index / search / chat)
                              └─ Agent Router    (chat)
                              │
                              ├─ pdf_service / chunk_service
                              ├─ embedding_service / vector_store_service
                              ├─ search_service / rag_service / llm_service
                              └─ agent_service / agent_tools
                              │
                              ├─ backend/data/uploads/     (PDF 파일)
                              └─ backend/data/chroma_db/   (Chroma DB)
```

- **Streamlit**: 각 API를 호출하는 테스트 페이지 (`frontend/streamlit_app.py`)
- **FastAPI**: REST API 제공, 비즈니스 로직은 `services/`에 분리
- **Chroma**: 인덱싱된 chunk embedding 저장 및 유사도 검색
- **Groq**: RAG 답변 및 Agent LLM 호출

---

## 3. RAG 처리 흐름

| 단계 | 설명 | API |
|------|------|-----|
| 1 | PDF 업로드 및 `backend/data/uploads/` 저장 | `POST /pdf/upload` |
| 2 | pypdf로 텍스트 추출 | `POST /pdf/extract` |
| 3 | LangChain TextSplitter로 chunk 분할 | `POST /pdf/chunk` |
| 4 | embedding 생성 후 Chroma DB 저장 | `POST /rag/index` |
| 5 | 질문 embedding → 유사 chunk 검색 | `POST /rag/search` |
| 6 | 검색 결과를 context로 구성 → Groq LLM 답변 | `POST /rag/chat` |

**인덱싱 상세 흐름 (`/rag/index`)**

```
PDF 파일
  → extract_text_from_pdf()
  → chunk_pdf_text()
  → HuggingFaceEmbeddings
  → Chroma (collection: rag_documents)
```

**질문 답변 상세 흐름 (`/rag/chat`)**

```
question
  → search_similar_documents()
  → context 구성
  → ChatGroq 답변 생성
  → answer + retrieved_documents 반환
```

---

## 4. LangGraph Agent 처리 흐름

Agent는 multi-agent 구조가 아닌, **Tool 3개를 순차 실행하는 단순 workflow**로 구성했습니다.

| 순서 | 노드 | Tool | 설명 |
|------|------|------|------|
| 1 | `search_documents` | `document_search` | Chroma에서 유사 chunk 검색 |
| 2 | `get_current_time` | `current_time` | 서버 현재 시간 반환 |
| 3 | `generate_answer` | — | 검색 결과 + 시간 정보로 Groq LLM 답변 생성 |
| 4 | `format_json_response` | `json_formatter` | `answer`, `used_tools`, `references` JSON 구조화 |

```
question 입력
  → document_search
  → current_time
  → Groq LLM 답변 생성
  → json_formatter
  → 최종 응답 반환
```

API: `POST /agent/chat`

---

## 5. 주요 기능

- PDF 업로드 및 파일 형식 검증 (`.pdf` + `%PDF` 헤더)
- PDF 텍스트 추출 (pypdf)
- LangChain 기반 문서 chunking (`chunk_size`, `chunk_overlap` 설정)
- sentence-transformers embedding + Chroma DB 인덱싱
- 질문 기반 유사 문서 검색 (`top_k`, score/distance 반환)
- Groq API 기반 RAG 질문 답변 (context 기반, 한국어 응답)
- LangGraph Agent workflow (문서 검색 / 현재 시간 / JSON 변환 Tool)
- Streamlit 통합 테스트 페이지 (Health Check ~ Agent까지 단계별 UI)
- Swagger UI (`/docs`) 자동 문서화

---

## 6. 프로젝트 구조

```
RAG_STUDY/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 시작점
│   │   ├── config.py               # .env 로드
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   ├── pdf_router.py       # PDF upload / extract / chunk
│   │   │   ├── rag_router.py       # RAG index / search / chat
│   │   │   └── agent_router.py     # Agent chat
│   │   ├── schemas/                # 요청/응답 Pydantic 모델
│   │   └── services/               # 비즈니스 로직
│   │       ├── pdf_service.py
│   │       ├── chunk_service.py
│   │       ├── embedding_service.py
│   │       ├── vector_store_service.py
│   │       ├── search_service.py
│   │       ├── rag_service.py
│   │       ├── llm_service.py
│   │       ├── agent_service.py
│   │       └── agent_tools.py
│   └── data/
│       ├── uploads/                # 업로드 PDF
│       └── chroma_db/              # Chroma DB
├── frontend/
│   └── streamlit_app.py            # Streamlit 테스트 페이지
├── .env                            # API 키 등
├── requirements.txt
├── PROJECT_RULES.md
└── README.md
```

---

## 7. 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성합니다. (`GROQ_API_KEY`가 없어도 서버는 기동되며, LLM/Agent API 호출 시 에러를 반환합니다.)

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
CHROMA_DB_PATH=backend/data/chroma_db
UPLOAD_DIR=backend/data/uploads
```

| 변수 | 필수 | 설명 |
|------|------|------|
| `GROQ_API_KEY` | RAG Chat / Agent 호출 시 | Groq API 키 |
| `GROQ_MODEL` | 선택 | LLM 모델명 (기본값: `llama-3.1-8b-instant`) |
| `CHROMA_DB_PATH` | 선택 | Chroma 저장 경로 (코드 기본값: `backend/data/chroma_db/`) |
| `UPLOAD_DIR` | 선택 | PDF 업로드 경로 (코드 기본값: `backend/data/uploads/`) |

---

## 8. 설치 및 실행

### 8.1 개발 환경

- Python 3.10+
- 가상환경(venv) 사용 권장

### 8.2 설치

```bash
# 프로젝트 루트에서
python -m venv venv

# Windows
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 8.3 FastAPI 서버 실행

```bash
# backend 디렉터리에서 실행
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 8.4 Streamlit 실행

FastAPI 서버를 먼저 실행한 뒤, 별도 터미널에서 Streamlit을 실행합니다.

```bash
# 프로젝트 루트에서 실행
streamlit run frontend/streamlit_app.py
```

브라우저에서 Streamlit 페이지가 열리면 **FastAPI 서버 상태 확인** 버튼을 눌러 `/health` API 응답을 확인합니다.

| 항목 | 값 |
|------|-----|
| Streamlit 페이지 | http://localhost:8501 |

---

## 9. 로컬 테스트 결과

로컬 환경에서 아래 항목을 확인했습니다.

| 테스트 항목 | 결과 |
|-------------|------|
| `LLM_RAG_Basic_Guide_KR.pdf` chunking | `chunk_size=500`, `chunk_overlap=100` 기준 **15개 chunk** 분할 |
| `chunk_overlap >= chunk_size` 요청 | **400** 오류 (`chunk_overlap은 chunk_size보다 작아야 합니다.`) |
| `/rag/index` 인덱싱 | 15개 chunk → Chroma `rag_documents` collection 저장 |
| `/rag/search` 검색 | 질문 기준 유사 chunk 및 score 반환 |
| `/rag/chat` 답변 | Groq LLM 기반 한국어 답변 + 참고 문서 반환 |
| `/agent/chat` Agent | Tool 3개 순차 실행, `used_tools` / `references` 포함 응답 |
| 동일 PDF 재인덱싱 | `filename` 기준 기존 chunk 삭제 후 재저장 (중복 방지) |

---

## 10. API 테스트

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
| Agent Chat | POST http://127.0.0.1:8000/agent/chat |
| Swagger UI | http://127.0.0.1:8000/docs |

### 10.1 Health Check

```bash
curl http://127.0.0.1:8000/health
```

예상 응답:

```json
{"status": "ok"}
```

### 10.2 PDF 업로드 API

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

### 10.3 PDF 텍스트 추출 API

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

### 10.4 PDF Chunking API

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

### 10.5 문서 인덱싱 API

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

### 10.6 유사 문서 검색 API

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

### 10.7 RAG 질문 답변 API

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

### 10.8 LangGraph Agent API

- **Method:** POST
- **URL:** `/agent/chat`
- **Content-Type:** `application/json`
- **Body:**
  - `question` (필수): 사용자 질문
  - `top_k` (선택, 기본값 3): 문서 검색 Tool에서 참고할 chunk 개수 (최대 20)
- **처리 흐름:**
  1. 사용자 question 입력
  2. 문서 검색 Tool 실행 (`document_search`)
  3. 현재 시간 Tool 실행 (`current_time`)
  4. 검색 결과와 현재 시간을 바탕으로 Groq LLM 답변 생성
  5. JSON 변환 Tool 실행 (`json_formatter`)
  6. 최종 결과 반환
- **Tool 목록:**
  - `document_search`: Chroma DB 유사 chunk 검색
  - `current_time`: 현재 서버 시간 반환
  - `json_formatter`: answer, used_tools, references JSON 구조화

```bash
curl -X POST http://127.0.0.1:8000/agent/chat -H "Content-Type: application/json" -d "{\"question\": \"RAG란 무엇인가?\", \"top_k\": 3}"
```

성공 응답 예시:

```json
{
  "question": "RAG란 무엇인가?",
  "top_k": 3,
  "answer": "RAG(Retrieval-Augmented Generation)는 검색으로 찾은 문서를 기반으로 LLM이 답변을 생성하는 방식입니다.",
  "used_tools": ["document_search", "current_time", "json_formatter"],
  "references": [
    {
      "filename": "sample.pdf",
      "chunk_index": 3,
      "score": 1.18,
      "content_preview": "RAG(Retrieval-Augmented Generation)는 ..."
    }
  ],
  "current_time": "현재 시간은 2026-06-05 14:30:00 입니다."
}
```

에러 응답 예시:

```json
{"detail": "GROQ_API_KEY가 설정되지 않았습니다. 프로젝트 루트의 .env 파일을 확인해주세요."}
```

---

## 11. Streamlit 테스트

### 11.1 PDF 업로드

1. FastAPI 서버와 Streamlit을 각각 실행합니다.
2. Streamlit 페이지(http://localhost:8501) 에서 **PDF 파일을 선택**합니다.
3. **PDF 업로드** 버튼을 클릭합니다.
4. 성공 시 저장된 파일명과 경로가 화면에 표시됩니다.

### 11.2 PDF 텍스트 추출

1. 먼저 PDF를 업로드해 `backend/data/uploads/` 에 저장합니다.
2. Streamlit 페이지의 **PDF 텍스트 추출** 영역에 파일명을 입력합니다.
3. **텍스트 추출** 버튼을 클릭합니다.
4. 성공 시 추출된 텍스트와 글자 수가 화면에 표시됩니다.

### 11.3 PDF Chunking

1. 먼저 PDF를 업로드해 `backend/data/uploads/` 에 저장합니다.
2. Streamlit 페이지의 **PDF 문서 Chunking** 영역에 파일명을 입력합니다.
3. `chunk_size`, `chunk_overlap` 값을 설정합니다.
4. **Chunking 실행** 버튼을 클릭합니다.
5. 성공 시 `total_chunks`와 각 chunk의 일부 내용이 화면에 표시됩니다.

### 11.4 문서 인덱싱

1. 먼저 PDF를 업로드해 `backend/data/uploads/` 에 저장합니다.
2. Streamlit 페이지의 **문서 인덱싱** 영역에 파일명을 입력합니다.
3. `chunk_size`, `chunk_overlap` 값을 설정합니다.
4. **문서 인덱싱 실행** 버튼을 클릭합니다.
5. 성공 시 `total_chunks`, `collection_name`, 저장 경로, `message`가 화면에 표시됩니다.
6. 첫 실행 시 embedding 모델 다운로드로 시간이 다소 걸릴 수 있습니다.

### 11.5 질문 기반 문서 검색

1. 먼저 PDF를 업로드하고 **문서 인덱싱**을 완료합니다.
2. Streamlit 페이지의 **질문 기반 문서 검색** 영역에 질문을 입력합니다.
3. `top_k` 값을 설정합니다.
4. **문서 검색** 버튼을 클릭합니다.
5. 성공 시 rank, score, filename, chunk_index, content 일부가 화면에 표시됩니다.

### 11.6 RAG 질문 답변

1. `.env` 파일에 `GROQ_API_KEY`와 `GROQ_MODEL`을 설정합니다.
2. PDF를 업로드하고 **문서 인덱싱**을 완료합니다.
3. Streamlit 페이지의 **RAG 질문 답변** 영역에 질문을 입력합니다.
4. **RAG 답변 생성** 버튼을 클릭합니다.
5. 성공 시 LLM 답변과 참고 문서 목록이 함께 표시됩니다.

### 11.7 LangGraph Agent

1. `.env` 파일에 `GROQ_API_KEY`와 `GROQ_MODEL`을 설정합니다.
2. PDF를 업로드하고 **문서 인덱싱**을 완료합니다.
3. Streamlit 페이지의 **LangGraph Agent 테스트** 영역에 질문을 입력합니다.
4. **Agent 실행** 버튼을 클릭합니다.
5. 성공 시 Agent 최종 답변, 사용한 Tool 목록, 참고 문서 목록이 함께 표시됩니다.

---

## 12. 구현 중 고려한 예외 처리

- PDF가 아닌 파일 업로드 시 400 오류 반환
- 존재하지 않는 PDF 파일명 요청 시 에러 메시지 반환
- 텍스트 추출이 불가능한 PDF에 대한 예외 처리
- chunk_overlap >= chunk_size인 경우 400 오류 반환
- 문서 인덱싱 전 검색/답변 요청 시 안내 메시지 반환
- GROQ_API_KEY 미설정 시 서버가 죽지 않고 API 호출 시 명확한 에러 반환
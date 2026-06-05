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

### Streamlit PDF 업로드 테스트

1. FastAPI 서버와 Streamlit을 각각 실행합니다.
2. Streamlit 페이지(http://localhost:8501)에서 **PDF 파일을 선택**합니다.
3. **PDF 업로드** 버튼을 클릭합니다.
4. 성공 시 저장된 파일명과 경로가 화면에 표시됩니다.

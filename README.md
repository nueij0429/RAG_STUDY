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

## 서버 실행

```bash
# backend 디렉터리에서 실행
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## API 테스트

서버 실행 후 브라우저 또는 curl로 확인합니다.

| 항목 | 값 |
|------|-----|
| Health Check | http://127.0.0.1:8000/health |
| Swagger UI | http://127.0.0.1:8000/docs |

```bash
curl http://127.0.0.1:8000/health
```

예상 응답:

```json
{"status": "ok"}
```

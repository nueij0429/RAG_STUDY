# RAG_STUDY Project Rules

이 프로젝트는 FastAPI 기반 PDF RAG 챗봇 학습용 프로젝트이다.

## 전체 구성
- Frontend: Streamlit
- Backend: FastAPI
- RAG Framework: LangChain
- Embedding Model: HuggingFace sentence-transformers
- Vector DB: Chroma
- LLM: Groq API

## 목표
- PDF 업로드
- PDF 텍스트 추출
- 문서 chunking
- embedding 생성 및 저장
- Chroma 기반 유사 문서 검색
- Groq API 기반 LLM 답변 생성
- 참고 문서 출력
- 간단한 Streamlit 테스트 페이지 구현
- Agent 기능 1개 구현

## 개발 원칙
- 한 번에 모든 기능을 구현하지 않는다.
- 단계별로 기능을 추가한다.
- API, service, schema 역할을 분리한다.
- 초보자가 이해할 수 있는 구조를 우선한다.
- LangChain은 RAG 기본 흐름 구현에 사용한다.
- LangGraph는 기본 RAG 기능 완성 후, Agent 테스트 기능 구현에 사용한다.
- 처음부터 복잡한 multi-agent 구조로 가지 않고, Tool 3개를 가진 단순 Agent workflow부터 구현한다.
- API 키는 .env에 저장한다.
- .env, venv, 업로드 파일, Chroma DB 파일은 GitHub에 올리지 않는다.
- README.md에 실행 방법과 API 사용법을 계속 업데이트한다.

## 프로젝트 구조
- Streamlit 화면은 frontend/
- FastAPI 백엔드는 backend/
- FastAPI 시작점은 backend/app/main.py
- 라우터는 backend/app/api/
- 비즈니스 로직은 backend/app/services/
- 요청/응답 모델은 backend/app/schemas/
- 업로드 파일은 backend/data/uploads/
- Chroma DB 데이터는 backend/data/chroma_db/

## 구현 순서
1. 개발 환경 정리 및 기본 폴더 구조 생성
2. FastAPI 기본 서버와 /health
3. Streamlit 기본 화면
4. PDF 업로드
5. PDF 텍스트 추출
6. 문서 chunking
7. embedding 생성
8. Chroma에 embedding 저장
9. 질문 기반 유사 문서 검색
10. Groq API 기반 LLM 답변 생성
11. 참고 문서 출력
12. Agent Tool 3개 구현
13. Agent 테스트 API 구현
14. Streamlit에서 Agent 테스트 기능 연결
15. README 정리

## 주의사항
- 내가 요청하지 않은 기능을 임의로 추가하지 않는다.
- 기존 동작이 깨질 수 있는 변경은 먼저 설명한다.
- 수정 후 실행 명령어와 테스트 방법을 알려준다.
- 에러가 발생하면 원인, 해결 방법, 수정 코드를 순서대로 설명한다.
- 코드 생성 후에는 어떤 파일이 생성/수정되었는지 요약한다.
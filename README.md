# Customer Manager

FastAPI, SQLAlchemy, SQLite 기반 고객관리 서비스입니다.

## 실행

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- 서비스: <http://127.0.0.1:8000/>
- 상태 확인: <http://127.0.0.1:8000/health>
- Swagger UI: <http://127.0.0.1:8000/docs>

## 테스트

```powershell
python -m pytest -q
```

데이터베이스 및 개발 규칙은 `AGENTS.md`를 확인하세요.

# Customer Manager 개발 규칙

이 저장소는 하나의 Customer Manager 서비스를 S1부터 S5까지 이어서 개발한다. 매 단계에서 기존 코드를 우선 재사용하고, 호환성을 유지하며 필요한 기능만 확장한다.

## 실행법

가상환경을 만들지 않고 로컬 Python에 의존성을 설치한다.

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

확인 주소:

- 서비스: `http://127.0.0.1:8000/`
- 상태 확인: `http://127.0.0.1:8000/health`
- API 문서: `http://127.0.0.1:8000/docs`

## 테스트법

```powershell
python -m pytest -q
```

테스트 전후에 `customer.db`의 기존 데이터가 유지되어야 한다. API를 직접 확인할 때는 서버 실행 후 다음 명령을 사용한다.

```powershell
Invoke-WebRequest http://127.0.0.1:8000/ -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:8000/health -UseBasicParsing
```

## 금지 규칙

- `models.py`, `database.py`, `customer.db`를 새 파일로 대체하지 않는다.
- 테이블이나 컬럼을 삭제하거나 기존 컬럼의 타입을 변경하지 않는다.
- 기존 데이터를 삭제·초기화·재시드하지 않는다.
- `drop_all`, `DROP TABLE`, 파괴적 마이그레이션을 사용하지 않는다.
- 사용자 요청 없이 `customer.db`를 Git에 추가하지 않는다.
- 가상환경을 생성하거나 프로젝트 내부에 의존성 패키지를 복사하지 않는다.
- API 코드에서 전역 세션을 공유하지 않는다. 요청마다 `get_db()` 세션을 사용한다.

## Git 작업 규칙

- `main` 브랜치에서 직접 코드를 수정하거나 커밋하지 않는다.
- 작업 시작 전에 `main`을 기준으로 목적에 맞는 작업 브랜치를 만든다.
- 브랜치 이름은 `feat/`, `fix/`, `chore/`, `docs/`, `test/` 중 하나의 접두사를 사용한다.
- 변경 사항은 테스트 후 작업 브랜치에 커밋하고, Pull Request를 통해 `main`에 병합한다.
- `main` 브랜치에 강제 푸시하지 않는다.
- 커밋에는 해당 작업과 관계있는 파일만 포함한다.
- `customer.db`, 환경변수 파일, 인증정보, 캐시 및 로컬 실행 산출물을 커밋하지 않는다.

## 허용되는 스키마 확장

- 새 테이블 추가
- 기존 데이터와 호환되는 nullable 컬럼 추가
- 기존 API와 데이터의 의미를 깨뜨리지 않는 인덱스·제약조건 추가

스키마 변경이 필요하면 먼저 기존 DB 구조와 데이터 보존 여부를 확인하고, 안전한 마이그레이션 절차와 테스트를 함께 추가한다.

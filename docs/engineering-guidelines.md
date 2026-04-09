# Engineering Guidelines

프로젝트: Public Property Deliberation Eligibility Checker  
한글 명칭: 공유재산 심의·관리계획 대상 판별 도구  
작성일: 2026-02-22  
최종 수정일: 2026-04-09

## 문서 목적과 범위
- 이 문서는 현재 코드베이스의 테크 스택, 코딩 철학, 코딩 스타일, 품질 게이트의 단일 기준(Source of Truth)이다.
- 적용 범위:
  - `backend/app/*`
  - `backend/rules/catalogs/SEOSAN.yaml`
  - `frontend/src/*`
  - `backend/tests/*`
- 다른 문서(`goals.md`, `architecture.md`, `maintenance.md`)는 본 문서를 참조하고 중복 규칙을 반복하지 않는다.
- 규칙 강도:
  - `MUST`: 반드시 준수. 위반 시 수정 또는 근거 있는 예외 기록이 필요하다.
  - `SHOULD`: 기본 권장. 예외 허용 가능하지만 사유를 남긴다.
  - `AVOID`: 특별한 이유가 없으면 지양한다.

## Canonical Tech Stack (MUST)
- Backend: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic
- Frontend: React 18, TypeScript, Vite
- Database: SQLite (`diagnostic.db`)
- Rule source: YAML (`backend/rules/catalogs/SEOSAN.yaml`) + loader validation
- Test/품질:
  - Backend: pytest, FastAPI TestClient
  - Frontend: `tsc -b`, `vite build`

## Coding Philosophy
- `MUST`: API 계약은 Pydantic 스키마(`backend/app/schemas.py`)를 기준으로 유지한다.
- `MUST`: 판정 로직은 `backend/app/rules.py`에 집중하고, 카탈로그 로딩/검증은 `backend/app/rule_catalog_loader.py`에 집중한다.
- `MUST`: 규칙 원본은 Python 상수 하드코딩 대신 YAML 카탈로그를 우선 사용한다.
- `MUST`: 설정은 환경변수(`APP_NAME`, `DB_URL`, `CORS_ALLOW_ORIGINS`) 중심으로 관리하고 비밀정보 하드코딩을 금지한다.
- `MUST`: 카탈로그 검증 실패 시 앱 시작 단계에서 명시적으로 실패해야 한다.
- `SHOULD`: 라우트 핸들러는 입력/출력/오케스트레이션 중심으로 유지하고, 복잡한 계산은 전용 모듈 함수로 분리한다.
- `SHOULD`: 변경은 작은 단위로 나누고 회귀 테스트를 함께 유지한다.

## Backend Style Rules
- `MUST`: 공개 API 응답은 스키마에 정의된 필드만 노출한다.
- `MUST`: 요청 입력값은 경계(엔드포인트)에서 검증한다.
- `MUST`: DB 스키마 불일치 시 런타임 오류를 숨기지 않고 명시적 오류로 실패시킨다.
- `MUST`: 시간 정보는 응답 정책(현재 KST 변환)을 일관되게 유지한다.
- `SHOULD`: 함수 경계를 명확히 하고 타입 힌트를 유지한다.
- `SHOULD`: 임계값/그룹/예외 규칙은 YAML/상수로 중앙 관리한다.
- `AVOID`: 라우트 내부에 카탈로그 판정 로직과 데이터 변환 로직을 과도하게 혼합하는 패턴.
- `AVOID`: 동일 규칙 데이터를 백엔드와 프론트엔드에 중복 하드코딩하는 패턴.

## Frontend Style Rules
- `MUST`: API 호출은 `frontend/src/api.ts` 경유로 수행한다.
- `MUST`: 서버 계약(API 필드명/타입)에 맞춰 `frontend/src/types.ts`를 유지한다.
- `MUST`: 규칙 항목은 `/api/v1/source-rule-items` 응답을 사용한다(하드코딩 금지).
- `MUST`: 출력 문서(브라우저 인쇄/PDF 저장)에는 최종 결정, 사유, 단계별 판정, 관련 법규가 누락되지 않아야 한다.
- `SHOULD`: UI 상태 처리와 가공 로직(`useMemo`, 유틸 함수)을 분리해 가독성을 유지한다.
- `AVOID`: 컴포넌트 내 중복 fetch/오류 처리 로직 복붙.

## Security & Config Handling Rules
- `MUST`: CORS 허용 출처는 환경변수(`CORS_ALLOW_ORIGINS`)로 관리한다.
- `MUST`: 비밀값 및 내부 민감 정보는 로그/응답에 노출하지 않는다.
- `MUST`: 운영 배포 전 DB 마이그레이션(`alembic upgrade head`) 선적용 원칙을 따른다.
- `SHOULD`: 운영 환경에서 CORS는 명시 허용 목록만 사용하고 와일드카드 사용을 지양한다.
- `SHOULD`: 설정 변경 시 README의 실행/운영 지침과 함께 검토한다.

## Testing & Definition of Done
### MUST (현재 기준선)
- 변경 범위에 맞는 테스트를 추가/수정한다.
- 아래 검증을 통과한다.
  - `PYTHONPATH=/usr/lib/python3/dist-packages:backend pytest -q backend/tests/test_rule_catalog_loader.py backend/tests/test_rules.py backend/tests/test_seed_sync.py`
  - `cd frontend && npm run build`
- 카탈로그 YAML 변경 시 로더 검증 테스트(정상/필수키/중복/허용값/laws)를 유지한다.

### TARGET (도입/안정화 목표)
- `pytest -q backend/tests` 전체 통과를 목표로 유지한다.
- 정적 품질 게이트(`ruff`, `mypy`)를 도입하고 CI 필수 단계로 편입한다.

### Known Gap
- 현재 환경에서 `backend/tests/test_api.py`는 TestClient 실행 이슈로 비결정적 정지 가능성이 있어 안정화가 필요하다.

## Code Review Checklist
- 데이터 계약:
  - `schemas.py` 변경이 API 응답/프론트 타입과 동기화되었는가?
- 규칙 정합성:
  - 카탈로그 YAML과 로더 검증이 일치하는가?
  - 임계값/예외 규칙 변경 시 회귀 테스트가 갱신되었는가?
- 운영 영향:
  - CORS/DB URL/마이그레이션 관련 영향이 문서화되었는가?
- 출력 품질:
  - 인쇄 문서(PDF 저장 포함)에서 핵심 정보가 누락되지 않는가?
- 품질 검증:
  - 실행한 테스트 명령과 결과, 잔여 리스크가 변경 설명에 포함되었는가?

## Change Control
- 코딩 원칙/스타일 기준 변경 시 이 문서를 우선 수정한다.
- 기능 변경 시 관련 문서(`architecture.md`, `maintenance.md`, `README.md`)를 함께 갱신한다.
- API/환경변수/운영 절차 변경 시 `README.md`와 문서 포털 링크 정합성을 점검한다.
- 본 작업의 문서 수정 범위는 `engineering-guidelines.md` 단일 파일로 한정한다.

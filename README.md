# Public Property Deliberation Eligibility Checker

공식 한글 명칭은 `공유재산 심의·관리계획 대상 판별 도구`입니다. 원격 저장소 권장 명칭은 `public-property-deliberation-checker`입니다.

`plan.md` 요구사항을 기반으로 구현한 내부용 웹앱으로, 공유재산 관련 안건이 심의 또는 관리계획 수립 대상인지 판별하고 감사 이력을 저장합니다.

## 구조
- `backend`: FastAPI + Pydantic + SQLAlchemy + Alembic + SQLite3
- `frontend`: React + TypeScript (Vite)

## 주요 기능
- 규칙 카탈로그 기반 대상 판별
- API 구현
  - `POST /api/v1/diagnoses`
  - `POST /api/v1/diagnoses/{id}/answers`
  - `POST /api/v1/diagnoses/{id}/evaluate`
  - `GET /api/v1/diagnoses/{id}`
  - `GET /api/v1/diagnoses?from=&to=&department=&decision=`
  - `GET /api/v1/rule-profiles`
  - `GET /api/v1/source-rule-items`
- SQLite 운영 기준 반영
  - WAL 모드
  - Foreign Key 강제
- 감사 이력 저장
  - 단계별 판단 흔적(`diagnosis_trace`)

## 데이터 모델
- `diagnosis_case`
- `diagnosis_answer`
- `diagnosis_trace`
- `rule_profile`

## 실행 방법
네트워크가 가능한 환경에서 의존성 설치 후 실행하세요.

### 백엔드
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
alembic upgrade head
cd ..
uvicorn app.main:app --reload --app-dir backend
```

운영/개발 CORS 허용 출처 설정(쉼표 구분):
```bash
export CORS_ALLOW_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
```

### 프론트엔드
```bash
cd frontend
npm install
npm run dev
```

기본 연결 주소:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## 테스트
```bash
cd backend
pytest -q tests
```

## 결과 문서 출력
- `2) 문답 입력` 영역에서 `진단` 버튼을 누르면 답변 저장과 평가 실행이 일괄 처리됩니다.
- `2) 문답 입력` 영역의 `초기화` 버튼을 누르면 사례 유형/예외 사유/기준가격/토지 면적 입력값이 기본 상태로 초기화됩니다.
- 대상 판별 결과(최종 결정) 생성 후 `3) 결과 및 감사 이력` 영역의 `문서 출력` 버튼을 사용하세요.
- 브라우저 인쇄 창에서 프린터를 선택하거나 `PDF로 저장`을 선택할 수 있습니다.
- 인쇄 결과서에는 최종 결정/사유와 함께 선택 항목의 `관련 법령`이 표시됩니다.
- 인쇄 결과서에는 사용자가 입력한 `사례 유형`이 표시되며, 취득/처분 관련 항목인 경우 `1건당 기준가격`, `토지 면적`, `예외 사유`(한글 라벨)도 함께 표시됩니다.

## 규칙 카탈로그 수정
- 규칙 원본 파일: `backend/rules/catalogs/SEOSAN.yaml`
- 개발자는 YAML에서 항목을 수정/추가/삭제한 뒤 테스트를 실행하면 됩니다.
- 웹 화면의 `사례 유형` 콤보 상자 순서는 YAML `source_rule_items` 입력 순서를 그대로 따릅니다.
- 필수 필드:
  - `schema_version: 1`
  - `municipality_code`
  - `thresholds` (`amount_threshold`, `acquisition_area_threshold`, `disposal_area_threshold`, `seosan_private_sale_threshold`)
  - `source_rule_items` (`label`, `group`, `laws`)
  - `exception_reason_options` (`code`, `label`)
  - `exception_disabled_items`
- `group` 허용값: `deliberation`, `plan_setup`, `plan_change`
- 앱 시작 시 `SEOSAN` 활성 규칙 프로파일의 임계값(`config`)은 YAML `thresholds` 값으로 동기화됩니다.
- 로딩/검증 실패 시 앱 시작 시점에 에러가 발생합니다.

## 마이그레이션 주의사항
- 백엔드 코드가 갱신되면 서버 실행 전 Alembic 마이그레이션을 먼저 적용하세요.
- 스키마가 오래된 상태에서 실행하면 브라우저에 CORS처럼 보이는 오류가 나더라도, 실제 원인은 서버 `500`일 수 있습니다.

## Purpose
이 문서는 이 저장소에서 작업하는 모든 에이전트/기여자가 따라야 하는 실행 규칙이다. 현행 기준 문서와 코드 구조를 일관되게 유지하는 것이 목적이다.

## Source Of Truth
- 최우선 기준: `docs/engineering-guidelines.md`
- 보조 기준:
  - `docs/index.md`
  - `docs/architecture.md`
  - `docs/maintenance.md`
  - `docs/stride-lite.md`
  - `docs/TODO.MD`
  - `README.md`

## How To Resolve Conflicts
- 본 문서와 `docs/engineering-guidelines.md`가 충돌하면 `docs/engineering-guidelines.md`를 우선한다.
- 본 문서는 현행 강제 규칙과 함께 운영 규칙 및 목표 구조를 보조적으로 설명한다.
- 현재 저장소 구조와 맞지 않는 규칙은 목표 구조 또는 조건부 적용 규칙으로 해석한다.
- `docs/refactoring-strategy.md`, `docs/reports/*`는 아카이브/기준선 참고용이며 현행 강제 규칙으로 사용하지 않는다.

## Mandatory Pre-Check (필수)
- 계획 수립/구현/리뷰 전에 `docs/engineering-guidelines.md`를 먼저 확인한다.
- 답변/PR 설명에 아래를 명시한다:
  - 가이드라인 준수 여부
  - 충돌 지점(있다면)과 사유/대안

## Current Mandatory Rules
### Architecture / Backend
- 판정 로직은 `backend/app/rules.py`에 집중한다.
- 카탈로그 로딩/검증은 `backend/app/rule_catalog_loader.py`에 집중한다.
- 공개 API 계약은 Pydantic 스키마를 기준으로 유지한다.
- 설정은 환경변수 중심으로 관리하고 비밀정보 하드코딩을 금지한다.
- DB 스키마 불일치 시 런타임 오류를 숨기지 않고 명시적 오류로 실패시킨다.

### Frontend
- 현행 기준은 `docs/engineering-guidelines.md`를 따른다.
- 현재 저장소에서는 네트워크 호출을 `frontend/src/api.ts` 경유로 수행한다.
- 서버 계약(API 필드명/타입)에 맞춰 프런트 타입을 유지한다.
- 규칙 항목은 `/api/v1/source-rule-items` 응답을 사용한다.
- 중복 fetch/에러 처리 로직 복붙을 금지한다.
- 출력 문서(브라우저 인쇄/PDF 저장)에는 최종 결정, 사유, 단계별 판정, 관련 법규가 누락되지 않아야 한다.

### Security
- CORS 허용 출처는 환경변수로 관리한다.
- 비밀값(`SECRET_KEY`, 비밀번호 해시 등)은 로그/응답에 노출하지 않는다.
- 운영 배포 전 DB 마이그레이션(`alembic upgrade head`) 선적용 원칙을 따른다.

### API & Contract
- 현행 공개 계약은 현재 구현된 API 경로를 기준으로 유지한다.
- API 계약(필드/상태코드/의미) 변경 시 운영 절차와 문서 영향을 함께 검토한다.
- `/api/*`와 `/api/v1/*` 동등성 규칙은 해당 경로가 함께 존재하는 경우에만 적용한다.

## Target Architecture / Direction
- 새 비즈니스 로직은 가능하면 Router에서 분리한다.
- 목표 구조는 Router -> Service -> Repository/Client 계층 분리다.
- DB 접근/SQL은 Repository 계층으로 이동하는 방향을 우선한다.
- 외부 API 호출은 Client 계층으로 이동하는 방향을 우선한다.
- 지도 페이지 전용 구조 규칙(`frontend/src/map.ts` + `frontend/src/map/*`)은 해당 구조가 존재하는 경우에만 적용한다.
- 관리자 보호 경로, 세션 인증, CSRF, 프록시 신뢰 정책은 해당 기능이 존재하는 경우 명확히 유지한다.

## Change Control (문서 동기화 필수)
기능/정책 변경 시 아래 문서를 함께 갱신한다:
- 구조/흐름 변경: `docs/architecture.md`
- 운영/절차 변경: `docs/maintenance.md`
- 보안 통제 변경: `docs/stride-lite.md`
- 사용자/운영 요약: `README.md`
- 문서 허브 링크: `docs/index.md`
- 리스크/개선 항목 영향: `docs/TODO.MD`

## Testing & DoD
- 변경 범위에 맞는 테스트를 추가/수정한다.
- 최소 강제 기준은 `docs/engineering-guidelines.md`의 MUST 검증을 따른다.
- 배포 전 기본 검증 기준:
  - `python -m compileall -q app tests`
  - `mypy app tests create_hash.py`
  - `ruff check app tests`
  - `scripts/check_quality_warnings.sh`
  - `cd frontend && npm run typecheck && npm run build`
  - `pytest -m unit -q`
  - `pytest -m integration -q`
  - `pytest -m e2e -q`
  - `pytest -q`
- 저장소 구조 또는 환경과 맞지 않는 항목은 현행 Source of Truth 기준으로 해석하고, 필요 시 문서 정리 작업으로 분리한다.

## Operational Notes
- 설정 변경은 `.env` 갱신만으로 즉시 반영되지 않을 수 있으므로 재시작 필요성을 명시한다.
- 로그인/이벤트 레이트리밋은 인메모리 기반이므로 멀티 인스턴스 한계를 설명한다.

## TODO Governance
- 리스크/개선 작업을 다룰 때 `docs/TODO.MD`를 함께 업데이트한다.
- 상태(`todo/doing/blocked/done`), 목표일, 리뷰 로그를 최신화한다.

## Response Requirements
- 저장소 파일을 수정한 작업의 최종 답변에는 적절한 git commit title을 제안한다.
- 저장소 파일 변경에는 코드와 문서 변경을 모두 포함한다.
- 변경 설명에는 실행한 테스트 결과와 잔여 리스크를 포함한다.

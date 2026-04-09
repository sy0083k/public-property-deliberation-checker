# 아키텍처 및 흐름

프로젝트: Public Property Deliberation Eligibility Checker  
한글 명칭: 공유재산 심의·관리계획 대상 판별 도구  
작성일: 2026-02-11  
최종 수정일: 2026-04-09

## 시스템 개요
이 애플리케이션은 공유재산 안건의 심의 및 관리계획 대상 여부를 판별하는 FastAPI + React 웹앱이다. 사용자가 사례 정보를 생성한 뒤 원문 항목, 예외 사유, 금액, 면적을 입력하면 서버가 규칙 카탈로그와 활성 규칙 프로파일을 기준으로 최종 결정을 계산하고, 그 결과와 단계별 판정 흔적을 SQLite에 저장한다.

## 레이어 구성
- 백엔드
  - `backend/app/main.py`: FastAPI 앱 생성, API 라우트 정의, 초기 시드 수행
  - `backend/app/config.py`: 환경변수 기반 설정 로딩
  - `backend/app/db.py`: SQLAlchemy 엔진/세션 생성
  - `backend/app/models.py`: `diagnosis_case`, `diagnosis_answer`, `diagnosis_trace`, `rule_profile`
  - `backend/app/schemas.py`: 공개 API 계약
  - `backend/app/rules.py`: 판정 로직
  - `backend/app/rule_catalog.py`: 카탈로그 노출용 상수 및 그룹 매핑
  - `backend/app/rule_catalog_loader.py`: YAML 로더/검증
- 프런트엔드
  - `frontend/src/App.tsx`: 단일 화면 UI, 입력/조회/출력 오케스트레이션
  - `frontend/src/api.ts`: 백엔드 API 호출 유틸
  - `frontend/src/ruleCatalog.ts`: 예외 사유 옵션과 보조 규칙 정보
  - `frontend/src/types.ts`: API 응답 타입

## 데이터 모델
### `diagnosis_case`
- 사례 메타데이터와 최종 판정 결과 저장
- 주요 필드: `department`, `project_name`, `manager_name`, `admin_phone`, `municipality_code`, `final_decision`, `final_reason`

### `diagnosis_answer`
- 사례별 답변 저장
- 고유 제약: `(case_id, question_code)`
- 주요 질문 코드: `selected_rule_item`, `exception_reason_code`, `amount_won`, `area_sqm`

### `diagnosis_trace`
- 단계별 판정 근거 저장
- 주요 필드: `step_key`, `prompt`, `decision`, `snapshot`

### `rule_profile`
- 지자체별 활성 규칙 프로파일 저장
- 기본값: `SEOSAN` 활성 프로파일 1건

## 공개 엔드포인트
- `POST /api/v1/diagnoses`
- `POST /api/v1/diagnoses/{case_id}/answers`
- `POST /api/v1/diagnoses/{case_id}/evaluate`
- `GET /api/v1/diagnoses/{case_id}`
- `GET /api/v1/diagnoses`
- `GET /api/v1/rule-profiles`
- `GET /api/v1/source-rule-items`

## 핵심 데이터 흐름
### 1. 사례 생성
1. 프런트가 `POST /api/v1/diagnoses`로 기초정보를 전송한다.
2. 서버가 `diagnosis_case`를 생성하고 상세 응답을 반환한다.

### 2. 답변 저장 및 판정
1. 프런트가 `selected_rule_item`, `exception_reason_code`, `amount_won`, `area_sqm`를 `POST /api/v1/diagnoses/{case_id}/answers`로 전송한다.
2. 서버는 기존 답변을 upsert한다.
3. 프런트가 `POST /api/v1/diagnoses/{case_id}/evaluate`를 호출한다.
4. 서버는 활성 `rule_profile`을 조회하고 `rules.evaluate_answers()`로 최종 결정을 계산한다.
5. 기존 `diagnosis_trace`를 대체 저장하고 결과를 반환한다.

### 3. 결과 조회 및 출력
1. 프런트가 `GET /api/v1/diagnoses/{case_id}`로 상세 정보를 조회한다.
2. 화면은 최종 결정, 사유, 관련 법령, 단계별 감사 이력을 렌더링한다.
3. 사용자는 브라우저 인쇄 기능으로 결과서를 출력하거나 PDF로 저장한다.

### 4. 목록 조회
1. 프런트가 `GET /api/v1/diagnoses?from=&to=&department=&decision=`를 호출한다.
2. 서버가 필터 조건에 맞는 `diagnosis_case`를 생성일시 역순으로 반환한다.

## 규칙 처리 원칙
- 카탈로그 원본은 `backend/rules/catalogs/SEOSAN.yaml`이다.
- 원문 항목의 그룹이 `deliberation`, `plan_setup`, `plan_change` 중 무엇인지에 따라 기본 판정이 결정된다.
- `공유재산의 취득`, `공유재산의 처분`은 취득/처분별 금액 임계값과 면적 임계값을 각각 계산한다.
- 예외 사유는 `공유재산의 취득`, `공유재산의 처분` 두 항목에만 적용된다.
- 카탈로그 검증 실패 시 앱 시작은 중단된다.

## 설정
### 환경변수
- `APP_NAME`: FastAPI title 기본값
- `DB_URL`: SQLite 연결 문자열
- `CORS_ALLOW_ORIGINS`: 쉼표 구분 허용 출처 목록

## 운영 참고
- 앱 시작 시 스키마 필수 컬럼을 검증한다.
- 앱 시작 시 활성 규칙 프로파일이 없으면 `SEOSAN` 기본 프로파일을 생성한다.
- 날짜/시간 응답은 KST로 직렬화된다.

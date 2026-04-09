# STRIDE-lite 위협 모델

프로젝트: Public Property Deliberation Eligibility Checker  
한글 명칭: 공유재산 심의·관리계획 대상 판별 도구  
작성일: 2026-02-11  
최종 수정일: 2026-04-09  
담당: Engineering

## 범위
- FastAPI API
  - `POST /api/v1/diagnoses`
  - `POST /api/v1/diagnoses/{case_id}/answers`
  - `POST /api/v1/diagnoses/{case_id}/evaluate`
  - `GET /api/v1/diagnoses`
  - `GET /api/v1/diagnoses/{case_id}`
  - `GET /api/v1/rule-profiles`
  - `GET /api/v1/source-rule-items`
- React 단일 페이지 앱
- SQLite DB (`diagnostic.db`)
- 규칙 카탈로그 (`backend/rules/catalogs/SEOSAN.yaml`)

## 자산
- 사례 메타데이터(`department`, `project_name`, `manager_name`, `admin_phone`)
- 답변 데이터와 판정 결과
- 단계별 감사 이력(`diagnosis_trace`)
- 지자체별 규칙 프로파일
- 환경변수 기반 설정값

## 신뢰 경계
- 브라우저 클라이언트 -> FastAPI API
- FastAPI API -> SQLite
- FastAPI API -> 로컬 규칙 카탈로그 파일

## STRIDE-lite 분석
### S: 스푸핑
- 위험: 내부 사용자가 아닌 주체가 API를 직접 호출
  - 현재 통제: 제한적인 CORS 설정과 내부 운영 전제
  - 잔여 위험: 별도 인증/인가가 없으므로 네트워크 경계에 의존

### T: 변조
- 위험: 비정상 입력으로 사례/답변 데이터 변조
  - 현재 통제: Pydantic 입력 검증, `(case_id, question_code)` 고유 제약
  - 잔여 위험: 업무 의미 수준의 검증은 규칙 로직에 의존
- 위험: 규칙 카탈로그 임의 변경
  - 현재 통제: 로더 검증과 앱 시작 실패
  - 잔여 위험: 파일 변경 자체에 대한 운영 승인 절차는 별도 관리 필요

### R: 부인
- 위험: 누가 어떤 입력으로 판정했는지 추적 부족
  - 현재 통제: `diagnosis_case`, `diagnosis_answer`, `diagnosis_trace` 영속 저장
  - 잔여 위험: 사용자 인증이 없으므로 행위 주체 식별은 업무 절차에 의존

### I: 정보 노출
- 위험: 사례 메타데이터 노출
  - 현재 통제: API 응답 필드가 스키마로 제한됨
  - 잔여 위험: 내부망 외 노출에 대한 별도 접근통제는 없음
- 위험: 환경변수 또는 비밀값 노출
  - 현재 통제: 설정은 코드 기본값 + 환경변수 사용, 비밀 하드코딩 금지

### D: 서비스 거부
- 위험: 대량 API 호출 또는 비정상 DB 파일 상태
  - 현재 통제: SQLite와 단일 인스턴스 전제
  - 잔여 위험: 별도 rate limit, 큐, 멀티 인스턴스 보호장치 없음

### E: 권한 상승
- 위험: 일반 사용자가 규칙 프로파일이나 사례 데이터에 광범위 접근
  - 현재 통제: 별도 관리자 기능 없음
  - 잔여 위험: 앱이 내부용이라는 운영 전제에 의존

## 권장 후속 조치
1. 내부망 또는 리버스 프록시 수준 접근 통제 정책 명문화
2. 사례 생성/조회에 대한 사용자 식별 또는 감사 보강 여부 검토
3. 규칙 카탈로그 변경 승인 절차와 리뷰 로그 정립
4. 필요 시 API 인증/인가 도입 검토

## 구현 규칙 참조
- 보안 관련 코딩 규칙은 [`engineering-guidelines.md`](engineering-guidelines.md)의 Security 섹션을 기준으로 유지한다.

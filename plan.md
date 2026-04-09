# Public Property Deliberation Eligibility Checker Plan (SQLite 확정)

## Summary
`graph.md`의 5단계 판단 트리를 그대로 구현하는 내부용 웹앱을 구축한다.  
기술 스택은 기존 계획을 유지하되 DB만 `SQLite3`로 확정한다.

## Fixed Decisions
1. 백엔드: `Python + FastAPI + Pydantic + SQLAlchemy + Alembic`
2. 프론트엔드: `React + TypeScript`
3. DB: `SQLite3` (v1)
4. 배포: 내부 웹(사내망)
5. 언어: 한국어 UI
6. 감사이력: 저장 필수
7. 규칙 범위: 지자체별 설정 가능(초기값 서산시)

## API / Interface
- `POST /api/v1/diagnoses`
- `POST /api/v1/diagnoses/{id}/answers`
- `POST /api/v1/diagnoses/{id}/evaluate`
- `GET /api/v1/diagnoses/{id}`
- `GET /api/v1/diagnoses?from=&to=&department=&decision=`
- `GET /api/v1/rule-profiles`

## Data Model (SQLite)
- `diagnosis_case`
- `diagnosis_answer`
- `diagnosis_trace`
- `rule_profile`

권장 인덱스:
- `diagnosis_case(created_at)`
- `diagnosis_case(final_decision)`
- `diagnosis_case(department)`
- `rule_profile(municipality_code, is_active)`

## SQLite 운영 기준 (v1)
1. WAL 모드 활성화 (`PRAGMA journal_mode=WAL`)
2. 외래키 강제 (`PRAGMA foreign_keys=ON`)
3. 일 단위 DB 파일 백업
4. 초기에는 단일 앱 인스턴스 운영

## Rule Logic (graph.md 반영)
1. 사업 유형 분류
- 대상 유형이 아니면 `심의 불필요`

2. 중요재산 여부
- 취득/처분 10억 이상 또는
- 취득 1,000㎡ 이상 또는 처분 2,000㎡ 이상
- 해당 시 5단계(심의 제외 사유)로 이동

3. 성격 변화/감면 여부
- 용도폐지·변경, 무상 이관, 사용료·대부료 감면이면 5단계 이동

4. 서산시 특례
- 5,000만 원 이상 재산의 수의매각 가격사정이면 5단계 이동
- 아니면 `심의 불필요`

5. 심의 제외 사유
- 예외 해당 시 `심의 생략 가능`
- 예외 없으면 `심의 대상 확정` (공유재산심의회 상정 추진)

## Testing
1. 규칙 단위 테스트: Q1~Q5 모든 분기
2. 경계값 테스트: 10억 / 1,000㎡ / 2,000㎡ / 5,000만
3. 통합 테스트: 입력→평가→저장→조회 일관성
4. 감사 조회 테스트: 날짜/결정/부서 필터
5. SQLite 동시성 테스트: 동시 저장 요청 시 처리 확인

## Assumptions
1. v1은 내부 사용자 중심으로 SQLite로 충분하다.
2. 동시접속/데이터 증가 시 PostgreSQL로 이관한다.
3. 지자체 규칙은 설정 파일 기반으로 확장한다.

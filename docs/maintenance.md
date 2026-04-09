# 유지보수 가이드

프로젝트: Public Property Deliberation Eligibility Checker  
한글 명칭: 공유재산 심의·관리계획 대상 판별 도구  
작성일: 2026-02-11  
최종 수정일: 2026-04-09

## 목적
운영 중인 판별 도구의 실행 방법, 검증 절차, 문서 동기화 기준을 정의한다.

## 환경 변수
### 기본
- `APP_NAME`
- `DB_URL`
- `CORS_ALLOW_ORIGINS`

## 실행 절차
### 백엔드
1. `python3 -m venv .venv`
2. `. .venv/bin/activate`
3. `pip install -r backend/requirements.txt`
4. `cd backend && alembic upgrade head && cd ..`
5. `uvicorn app.main:app --reload --app-dir backend`

### 프런트엔드
1. `cd frontend`
2. `npm install`
3. `npm run build` 또는 `npm run dev`

## 배포 전 체크리스트
1. `docs/engineering-guidelines.md` 기준 준수 여부 확인
2. 앱 표시명, README, `docs/*` 제품명이 동일한지 확인
3. `cd backend && alembic upgrade head`
4. `PYTHONPATH=/usr/lib/python3/dist-packages:backend pytest -q backend/tests/test_rule_catalog_loader.py backend/tests/test_rules.py backend/tests/test_seed_sync.py`
5. 필요 시 `PYTHONPATH=/usr/lib/python3/dist-packages:backend pytest -q backend/tests/test_api.py backend/tests/test_source_rule_items_order.py`
6. `cd frontend && npm run build`

## 주기적 점검
- `backend/rules/catalogs/SEOSAN.yaml`와 앱 동작이 일치하는지 확인
- 활성 규칙 프로파일의 임계값이 카탈로그와 동기화되는지 확인
- SQLite DB 파일 백업 상태 점검
- 결과서 출력 시 제목, 최종 결정, 관련 법령, 단계별 이력이 정상 노출되는지 확인
- 문서에 남은 옛 제품명 또는 잘못된 저장소명 잔존 여부 점검

## 장애 대응
### 앱 시작 실패
- Alembic 마이그레이션 누락 여부 확인
- 카탈로그 YAML 스키마 오류 여부 확인
- `DB_URL` 경로 및 파일 권한 확인

### 판정 결과가 비정상
- 선택한 원문 항목이 카탈로그에 존재하는지 확인
- 활성 `rule_profile`의 임계값이 예상과 일치하는지 확인
- `diagnosis_answer`와 `diagnosis_trace` 저장 결과를 확인

### 프런트 빌드 실패
- Node 의존성 설치 여부 확인
- API 타입 변경 후 `frontend/src/types.ts` 누락 여부 확인

## 운영 메모
- `APP_NAME`, `DB_URL`, `CORS_ALLOW_ORIGINS` 변경은 프로세스 재시작 후 반영된다.
- SQLite 기반이므로 초기 운영은 단일 인스턴스를 전제로 한다.
- 브라우저 인쇄 결과는 사용자의 프린터 설정에 따라 여백과 페이지네이션이 달라질 수 있다.

## 코드 변경 가이드
- 기능 또는 정책 변경 시 `README.md`, `docs/architecture.md`, `docs/index.md`를 함께 갱신한다.
- 보안 통제 변경 시 `docs/stride-lite.md`를 함께 갱신한다.

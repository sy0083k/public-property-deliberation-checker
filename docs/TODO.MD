# TODO 백로그 (Risk & Improvement Tracker)

프로젝트: Public Property Deliberation Eligibility Checker  
한글 명칭: 공유재산 심의·관리계획 대상 판별 도구  
작성일: 2026-02-23  
최종 수정일: 2026-04-09  
운영 주기: 매주 1회

## 목적
- 코드베이스 주요 리스크와 개선 과제를 추적한다.
- 상태, 목표일, 리뷰 로그를 최신화해 실행 우선순위를 명확히 한다.

## 우선순위 백로그
| id | priority | title | status | owner | target_date | success_criteria | notes |
|---|---|---|---|---|---|---|---|
| RISK-001 | P0 | 앱 인증/접근 통제 부재 | todo | unassigned | 2026-04-30 | 내부 운영 전제만으로 부족한 환경에서 인증 또는 네트워크 경계 정책이 문서화된다. | 현재 API는 내부 운영 가정에 의존 |
| RISK-002 | P0 | 규칙 카탈로그 변경 승인 절차 미정 | todo | unassigned | 2026-04-30 | YAML 변경의 리뷰/승인/배포 체크리스트가 문서화된다. | 관련: `backend/rules/catalogs/SEOSAN.yaml` |
| RISK-003 | P1 | 결과서 출력 포맷 회귀 위험 | todo | unassigned | 2026-05-07 | 인쇄/PDF 결과서의 핵심 항목 누락 여부를 수동 또는 자동 검증하는 절차가 정리된다. | 관련: `frontend/src/App.tsx` |
| RISK-004 | P1 | 테스트 명령 문서와 실제 환경 차이 | todo | unassigned | 2026-05-07 | 실행 가능한 기본 검증 명령과 확장 검증 명령이 문서 기준으로 정리된다. | 관련: `docs/engineering-guidelines.md`, `docs/maintenance.md` |
| RISK-005 | P2 | 지자체 규칙 확장 UX 미정 | todo | unassigned | 2026-05-21 | 다중 규칙 프로파일 선택/관리 UX 방향이 정의된다. | 현재는 `SEOSAN` 기본 프로파일 중심 |

## 리뷰 로그
- 2026-02-23 | reviewer: team | 초기 백로그 문서 생성
- 2026-04-09 | reviewer: codex | 제품 정체성 문서를 현재 판별 도구 기준으로 재정렬하고 리스크 항목을 현행 구조에 맞게 교체

# 문서 포털 (Documentation Hub)

프로젝트: Public Property Deliberation Eligibility Checker  
한글 명칭: 공유재산 심의·관리계획 대상 판별 도구  
작성일: 2026-02-22  
최종 수정일: 2026-04-09

## 빠른 시작 경로
1. 왜 만드는가: [`goals.md`](goals.md)
2. 어떻게 동작하는가: [`architecture.md`](architecture.md)
3. 어떤 기준으로 구현하는가: [`engineering-guidelines.md`](engineering-guidelines.md)
4. 어떻게 운영하는가: [`maintenance.md`](maintenance.md)
5. 어떤 보안 위협을 관리하는가: [`stride-lite.md`](stride-lite.md)
6. 어떤 리스크를 추적하는가: [`TODO.MD`](TODO.MD)

## 현행 기준 문서
- `goals.md`
  - 제품 목적, 사용자 가치, 비목표
- `architecture.md`
  - 시스템 구조, 데이터 모델, API 흐름
- `engineering-guidelines.md`
  - 기술 스택, 코딩 규칙, 품질 게이트
- `maintenance.md`
  - 실행/배포/검증/운영 절차
- `stride-lite.md`
  - 위협 모델과 보안 통제
- `TODO.MD`
  - 우선순위 리스크/개선 백로그

## Archive / 참고 문서
- `refactoring-strategy.md`
  - 아카이브/기준선 참고용 문서이며 현행 강제 규칙은 아님

## 기능 변경 시 동시 갱신 대상
| 변경 유형 | 필수 갱신 문서 | 비고 |
|---|---|---|
| 앱 명칭/제품 설명 변경 | `README.md`, `docs/goals.md`, `docs/index.md` | 영문/국문 공식 명칭과 저장소 식별자 동기화 |
| API 경로/요청/응답 변경 | `README.md`, `docs/architecture.md` | 공개 계약과 예시 동기화 |
| 규칙 카탈로그/판정 기준 변경 | `README.md`, `docs/architecture.md`, `docs/TODO.MD` | 규칙 설명과 리스크 영향 갱신 |
| 환경변수/운영 절차 변경 | `README.md`, `docs/maintenance.md` | 실행 명령과 재시작 필요성 명시 |
| 보안 통제 변경 | `docs/stride-lite.md`, `docs/maintenance.md`, `README.md` | 운영 통제와 잔여 위험 분리 기재 |

## 문서 운영 원칙
- 코딩 원칙/스타일 변경은 `engineering-guidelines.md`를 먼저 갱신한다.
- 사용자/운영자에게 보이는 제품 정체성은 본 문서 허브와 `README.md`에서 동일하게 유지한다.
- 기능 변경 시 구조/운영/보안 문서를 함께 갱신한다.
- 주요 릴리스 전 문서 제목, 링크, 명칭 정합성을 점검한다.

# ADR-0006 대상별 6단계 조사 절차와 REA 역할
- 상태: 승인 (2026-10-31, 사용자)
## 결정
| 단계 | 내용 | 도구 | 산출물 |
|---|---|---|---|
| 1 | 사용자 시나리오 | 튜토리얼 읽기 | `user-scenarios.md` (S1, S2 …) |
| 2 | 소스 흐름 추적 | grep / Read (REA 안 씀 — 소스가 있으므로) | `code-trace.md` (파일:줄 + 커밋) |
| 3 | 배포본 대조 | diff, REA `analyze_javascript_application` / `trace_application_feature` | `bundle-diff.md`, `evidence/` |
| 4 | 원본 동작 기록 | REA `capture_browser_scenario`(필요시 `capture_electron_scenario`), psql 전후 비교, `inspect_sqlite_database` | `baseline/S*/` |
| 5 | 설계 문서 | 종합 (ADR-0002 클린룸) | `design.md` |
| 6 | 사용자 검토 | — | 수정 반영 |
## 결과
폴더: `common/A*/`, `menus/NN-*/` 아래 위 산출물. 설계 문서 양식: 목적 / 사용자 시나리오 / 화면 / API / 데이터 모델 / 상태·저장 / 의존 / 비교 테스트 항목 / 모르는 점 / 근거.

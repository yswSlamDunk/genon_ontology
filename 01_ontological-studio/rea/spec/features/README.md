# 기능 명세 (features)

| 파일 | 메뉴 | 원본 기준 동작 (분석 design.md) |
|---|---|---|
| [F1-ontology-build.md](F1-ontology-build.md) | 온톨로지 구축 (Ontology Manager + 에이전트 구축) | `menus/01-ontology-build/` |
| [F2-query-action.md](F2-query-action.md) | 질의·액션 | `menus/02-query-action/` |
| [F3-datasources.md](F3-datasources.md) | 데이터소스 | `menus/03-datasources/` |
| [F4-graph-console.md](F4-graph-console.md) | 그래프 콘솔 (원본 Ontological Portal) | `menus/04-portal/` |
| [F5-ontology-apps.md](F5-ontology-apps.md) | 온톨로지 앱 (대시보드·코드 앱·Object view) | `menus/05-ontology-app/` |
| [F6-quality.md](F6-quality.md) | 품질 검수 | `menus/06-quality/` |
| [F7-systems.md](F7-systems.md) | 시스템 등록 | `menus/07-systems/` |
| [F8-settings.md](F8-settings.md) | 설정 | `menus/08-settings/` |
| [P-platform.md](P-platform.md) | 플랫폼 공통 (셸·부팅·홈·탭) | `common/A1-shell/`, `A2-storage/`, `A3-agent-mcp/` |

(원본 기준 동작 경로는 `../../analysis/ontological-studio/` 기준)

## 기능 명세 양식
1. 목적
2. 원본 기준 동작 요약 [원본] — 분석 design.md를 출발점으로 핵심만, 링크
3. 새 설계에서 달라지는 점 [제안] — 02 온톨로지 모델·03 보안·04 에이전트 반영, 결정 대기(D-xx) 연결
4. 사용자 시나리오 (원본 시나리오 번호와 대응, 새 시나리오는 N-번호)
5. 화면 구성과 상호작용
6. API (`/api/v1/...`, Object API 우선)
7. 데이터 (02 문서의 개념으로)
8. 에이전트 연동 (모드·도구)
9. 보안·권한
10. 오류·예외 (원본 문구 유지 여부)
11. 원본과 비교할 테스트 — "같아야 함" / "의도된 차이(D-12)" 구분
12. 열린 질문

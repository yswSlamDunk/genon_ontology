# 기능 지도 (feature-map)

- 기준: 배포본 Ontological Studio 0.1.1 (ADR-0008)
- 상태: **초안 v0.1** (2026-10-31). "추정"이라고 적힌 칸은 해당 대상을 분석할 때 확정한다.

## 1. 사용자 메뉴 = 홈 화면 카드 8개

정의 위치: `extracted-app-asar/src/renderer/shell/shell.js` L39–48 (`CARDS`). 클릭 처리는 L137–143:
`action`이 있으면 `liteShell.open(action)`, 없으면 `openTarget(target)` → 탭으로 연다.

| # | 카드 | 카드 설명(원문) | 여는 대상 | 표시 조건 |
|---|---|---|---|---|
| M1 | 온톨로지 구축 | 문서와 데이터소스에서 클래스·관계를 만듭니다. | Studio 탭 `view=build` | `llm: true` (에이전트 필요 배지) |
| M2 | 질의·액션 | 온톨로지에 묻고, 지시하면 액션을 계획·실행합니다. | Studio 탭 `view=act` | `llm: true` |
| M3 | 데이터소스 | 원천 DB 를 연결하고 가상 노드로 노출합니다. | Studio 탭 `view=datasources` | |
| M4 | Ontological Portal | Cypher 콘솔 · 스키마 지도 · 시점 조회. | 포털 탭 `kind=portal` | |
| M5 | 온톨로지 앱 | 대시보드나 코드 앱을 말로 만듭니다. | Studio 탭 `view=board` (화면 이름은 「대시보드」) | |
| M6 | 품질 검수 | 구축이 남긴, 사람이 판단할 것. | Studio 탭 `view=quality` | |
| M7 | 시스템 등록 | 키네틱 액션이 부를 서비스. | Studio 탭 `view=systems` | `kinetic: true` |
| M8 | 설정 | studio.env — 에이전트 · LLM 키. | `liteShell.open('settings')` → `studio.env` 파일을 OS 기본 앱으로 엶 (`src/main/index.js` L271–272) | |

참고: Studio 화면 안의 내비게이션(`VIEW_LABEL`, shell.js L36)은 M1·M2·M3·M5(대시보드)·M6·M7·Portal 7개이고, 「설정」은 셸 기능이며 메뉴바 「런타임 › 에이전트」(index.js `agentMenu`)도 설정에 포함된다(추정 — M8에서 확정).

## 2. 메뉴 ↔ 튜토리얼 ↔ 배포본 코드

튜토리얼: `~/Desktop/workplace/ontology/01_ontology-studio/tutorials/`. 공통으로 01(설치), 02(화면 둘러보기), 04(구성), 22(치트시트), 23(FAQ) 참조.

| # | 튜토리얼 장 | 프런트(압축 번들) | 백엔드·서비스 후보 (추정) |
|---|---|---|---|
| M1 온톨로지 구축 (클래스·관계 **+ 액션**, 사용자 확인) | 03 개념, 11 골든 퀘스천·커맨드, 12 문서로 구축, 15 골든 커맨드로 액션 만들기 | `runtime/frontend/assets/index-*.js` view `build` | `studio/app/backend/src/modules/{ontology, document_indexing, agent_session, files}` |
| M2 질의·액션 | 13 질의, 16 액션 실행 (15는 M1과 경계 확인 필요) | view `act` | `modules/{agent_session, ontology_runtime, kinetic, ontology_mcp}`, `runtime/kinetic` |
| M3 데이터소스 | 05 데이터소스 연결, 06 가상 노드·관계 | view `datasources` | 셸 `src/main/fabric-bridge.js`, `services.js`(repointFabric/seedFabric), PG FDW 확장 |
| M4 Ontological Portal | 07–09 Cypher, 10 시간 여행 | 포털 자체 UI `runtime/portal/web` | `runtime/portal/server/{index.js, release.js}`, `runtime/bin/ontological-bolt`, 셸 `nl2cypher.js` (IPC `lite:nl2cypher`) |
| M5 온톨로지 앱 | 17 대시보드, 18 코드 앱, 19 SDK, 20 앱 액션 버튼, 21 종합 과제 | view `board` | `modules/board`, 셸 `codeapps.js`, `resources/codeapp/`, `code_app_turn.py` |
| M6 품질 검수 | 12 (구축 결과 검수 부분) | view `quality` | `modules/quality` |
| M7 시스템 등록 | 14 업무 시스템 등록 | view `systems` | `modules/kinetic`, 셸 `kinetic.js`(registerSystems/repointSystems), `resources/sample/services` |
| M8 설정 | 01, 14, 23 (studio.env 언급) | 셸 홈 `shell.js` | 셸 `index.js`(shellOpen, agentMenu, switchAgent), `services.js`(readUserEnv/updateUserEnv/resolveAgent), `resources/studio.env.example` |

기타 백엔드 모듈(소속 메뉴 미정): `agent_bridge_mcp`, `ontological_admin`, `release`.

## 3. 공통 기반

| # | 범위 | 주 코드 |
|---|---|---|
| A1 셸·부팅·프로세스 | 부팅 순서, 프로세스 기동·종료·고아 정리, 포트 할당, 탭·창, 트레이, 로컬 웹 오리진(리버스 프록시), 사용자 데이터 폴더 | `src/main/{index, procs, ports, tabs, tray, web}.js`, `src/preload`, `src/renderer` |
| A2 저장소 | PostgreSQL(initdb·bootstrap·마이그레이션), 그래프 저장(`pg.GRAPH`), Bolt 게이트웨이, 비밀값 | `src/main/postgres.js`, `runtime/pg`, `runtime/bin/ontological-bolt`, `resources/sample/*.sql` |
| A3 에이전트·MCP | 에이전트 선택(cliagents/deepagents), CLI 실행 방식, Studio MCP 서버, 스크립트 실행(agent_turn.py 등) | `services.js`(resolveAgent/startStudio/runStudioScript), `modules/{agent_session, ontology_mcp, agent_bridge_mcp}`, `runtime/studio/app/cliagents` |

## 4. 분석 순서 (ADR-0009)
A1 → A2 → A3 → M8 설정 → M3 데이터소스 → M4 Portal → M7 시스템 등록 → M1 온톨로지 구축 → M6 품질 검수 → M2 질의·액션 → M5 온톨로지 앱

## 5. 열린 질문 — 해결 기록 (2026-11-01)
- 액션 생성 경계 → **M1이 액션 정의를 맡음**(구축 에이전트가 골든 커맨드마다 생성·발행·dry-run 검증, 또는 오른쪽 「정보」 패널의 액션 편집기). 질의·액션 에이전트엔 정의 도구 없음. 단 오른쪽 패널이 act 화면에도 떠서 편집기는 거기서도 열리고, 편집기의 dry-run이 실제 계획을 만들어 승인·실행 카드가 뜸 (M1 notes).
- `release`, `ontological_admin` 모듈 → **M1 「배포」 탭** (M1). `agent_bridge_mcp` → **A3** (CLI 에이전트용 모드별 도구 브리지).
- 「설정」 범위 → studio.env 파일 열기 + 메뉴바 「런타임 › 에이전트」 전환. 앱 안 설정 편집 화면은 없음 (M8).

### 이전 질문 목록
- 액션 생성(튜토리얼 15)은 M1 화면에서 하는가, M2에서도 하는가 — 경계 확인
- `agent_bridge_mcp`, `ontological_admin`, `release` 모듈은 어느 메뉴에 속하는가
- 「설정」의 범위: studio.env만인가, 메뉴바 에이전트 전환까지인가
- 압축 번들 안에서 각 view의 컴포넌트 경계와 호출 API (M 단계 2에서 REA로 확인)

# A1 셸·부팅·프로세스 — 코드 추적 (원본 근거, 구현 세션에 넘기지 않음)

기준: 배포본 0.1.1. 경로는 `extracted-app-asar/src/` 기준(app.asar 내부 `src/`와 동일).

## 0. 배포본 동일성 (관찰)
- DMG(`artifacts/Ontological-Studio-0.1.1-mac-arm64.dmg`, SHA-256 d49694ba…) 안의 앱과 `/Applications/Ontological Studio.app`의 파일 17,572개 SHA-256이 **전부 일치**(차이 0). 목록: `artifacts/app-0.1.1-file-manifest.sha256` (목록 파일 SHA-256 7816c909…).
- app.asar SHA-256 d7d70070…, `package.json` name `ontology-studio-lite` 0.1.1, main `src/main/index.js`, 의존성 `neo4j-driver` 5.28.1 하나.

## 1. 경로와 데이터 폴더 — `main/index.js`
- L27–37 런타임 위치: 패키지 시 `process.resourcesPath` 아래 `runtime/{pg,bin,portal,studio/python,studio/app,frontend}`, `resources/`.
- L40–66 데이터 폴더 이전: 옛 이름 "Ontology Studio Lite" 폴더에 `pgdata`가 있고 새 폴더엔 없으면 옮김. 옛 앱이 실행 중이면(postmaster.pid / run/postgres.pid 살아 있음) 옛 폴더를 그대로 사용.
- L67–69 `ONTOLOGICAL_STUDIO_USER_DATA` 또는 `ONTOLOGY_LITE_USER_DATA`로 데이터 폴더 지정(지정 시 이전 로직 생략).
- L72 `requestSingleInstanceLock()` — 데이터 폴더당 1개 인스턴스. L360–363 두 번째 실행 시 첫 창 복원·포커스.
- L74–81 하위 폴더: `pgdata`, `logs`, `run`, `sandbox`, `studio.env`.
- L112–116 `studio.env` 없으면 `resources/studio.env.example` 복사 후 chmod 0600.
- 실측(사용자 폴더 `~/Library/Application Support/Ontological Studio`): 위 외에 `secrets.json`(0600), `ports.json`, `sessions.db`(+wal), `kinetic.db`, `codeapps/`, Electron 자체 캐시 폴더들.

## 2. 부팅 순서 — `main/index.js` `boot()` L118–184
1. 데이터 폴더 생성, 이전 로그, `ensureUserEnv`
2. `procs.reapOrphans(runtimeRoot)` — 이전 실행의 고아 프로세스 정리
3. `ports.json` 읽기 → `ports_.allocate(saved)` → 저장
4. `pg.secrets(userData)` 비밀값 로드/생성, `kinetic.ensureSecrets` 보강
5. progress `postgres` — `pg.initdb`(fresh 여부) → `pg.start` → `pg.waitReady`
6. fresh 또는 `pgdata/.ontology-lite-bootstrap` 없으면 progress `bootstrap` — `pg.bootstrap`
7. `pg.migrateServices`
8. progress `ontological` — `services.startBolt` ‖ `services.startPortal` 병렬
9. neo4j 드라이버 `bolt://127.0.0.1:<bolt>` (계정 = PG 슈퍼유저, 비밀번호 = pgPassword, pool 4)
10. `services.repointFabric`, (마이그레이션 시) `resetSampleFabric`, `services.seedFabric`
11. progress `studio` — fabric bridge 생성, `createCodeApps`, `web.start`(로컬 오리진)
12. kinetic 시작(외부 KINETIC_URL 없을 때) ‖ `services.startStudio`(백엔드+MCP) 병렬 → kinetic 성공 시 `repointSystems`·`registerSystems`
13. kinetic 성공 시 `seedSampleOntology()` (L191–203: `resources/sample/seed_ontology.py` 실행, 마커 `pgdata/.ontology-lite-sample-ontology`)
14. phase `ready` → `tabs.ready()` (모든 창이 부팅 페이지에서 셸로 전환) → UI 로드 대기 → `logs/boot-timings.json` 기록
- 진행 표시: `progress(step, detail)` L103–110 — 로그 + 트레이 갱신 + 부팅 페이지 `window.setStep(step, detail)` 호출(`renderer/boot.html` L71–).
- 실패: L387–397 phase `error`, 로그 `BOOT FAILED`, 부팅 페이지 `window.setError(msg, logDir)`.
- 실측 부팅 시간(재시작, fresh=false): postgres 502ms, ontological 697ms, kinetic 2586ms, studio 3075ms, uiLoaded 3129ms.

## 3. 포트 — `main/ports.js`
- L17 선호 포트: pg 27432, bolt 27687, portal 27474, backend 27800, mcp 27810, web 27900, kinetic 27830, erp 27841, wms 27842, crm 27843.
- L20–31 우선순위: 환경변수 `ONTOLOGY_LITE_<KEY>_PORT` > 지난번 값(ports.json) > 선호 포트 > 임의 빈 포트. 모두 127.0.0.1에서 exclusive listen으로 시험.

## 4. 프로세스 관리 — `main/procs.js`
- L36–51 고아 정리: `run/*.pid`의 PID가 살아 있고 명령줄에 런타임 경로 또는 `ontology-lite`가 포함되면 종료(postgres는 SIGINT, 그 외 SIGTERM → 10초 후 SIGKILL), pid 파일 삭제. 명령줄 조회는 `ps -p <pid> -o command=` (Windows는 PowerShell CIM).
- L53–66 시작: stdout/stderr → `logs/<name>.log`(append, 시작 줄 기록), `run/<name>.pid`, 종료 시 pid 파일 삭제.
- L68–76 정지: 지정 신호 → timeout 후 SIGKILL.
- L82–107 준비 확인: TCP 연결 / HTTP GET(<500이면 OK) / `waitFor`(기본 120초, 150ms 간격, 프로세스가 죽으면 즉시 실패 메시지 "…프로세스가 종료됐습니다 (로그: logs/<name>.log)").
- 실측 pid 파일: backend, bolt, crm, erp, kinetic, mcp, portal, postgres, wms (9개).

## 5. 종료 — `main/index.js` L340–370
- `before-quit` 가로채 `shutdown()` 후 재종료. 순서: 트레이 제거 → 코드 앱 중지 → 웹 서버 close → 드라이버 close → backend·mcp(8s)·kinetic(5s)·예제 서비스(5s) 병렬 → portal·bolt(5s) → `pg.stopFast`(Windows용) → postgres(20s).
- `window-all-closed` → quit. SIGINT/SIGTERM → quit.

## 6. 로컬 웹 오리진 — `main/web.js`
127.0.0.1:<web> 단일 HTTP 서버(L53–89):
| 경로 | 처리 |
|---|---|
| `/lite-shell/*` | 셸 페이지 정적 파일(revalidate) |
| `/kinetic-idp/jwks.json` | kinetic 토큰 검증용 JWKS |
| `GET /api/act/health`, `GET /api/act/systems` (kinetic 미가동 시) | 200 `{url:'시작하지 않음', identity:null, reachable:false, error:…}` / 503 `{detail:…}` |
| `/app/portal-info` | `{url, graph}` |
| `/app/status` | `{phase, timings, ports, userData, error, pids}` |
| `/fabric-bridge/*`, `/api/gateway/data-fabric/*`, `/api/gateway/text2sql/*` | fabric bridge (M3) |
| `/codeapps/api/*`, `/apps/*` | 코드 앱 (M5) |
| `/api`, `/api/*` | 백엔드로 프록시 (SSE 그대로 통과) |
| `/mcp*` | MCP 서버로 프록시 |
| `/analyzer*` | "포함되지 않은 화면" 안내 HTML |
| 그 외 | 프런트엔드 정적 파일, 없으면 index.html (SPA) |
- 캐시: `/assets/*`만 1년 immutable, 나머지 no-cache. 프록시 오류 시 502 `{error:"upstream :<port> <code>"}`.

## 7. 창·탭 — `main/tabs.js`
- 창(L37–62): 1440×900(최소 1024×640), 배경 #14171c, macOS hiddenInset 타이틀바(신호등 14,13), 렌더러 contextIsolation·sandbox·nodeIntegration false + preload. 서비스 준비 전엔 `renderer/boot.html`, 후엔 셸 URL.
- 탭 = WebContentsView, 탭 바 높이 38px 아래에 배치(L166–169).
- 탭 종류와 URL(L20–27): studio → `http://127.0.0.1:<web>/?view=&session=&ds=`, portal → `http://127.0.0.1:<portal>/`, app → `/apps/<id>/` (id `^[a-z0-9-]{4,64}$`, preload 없음 — 생성 코드에 셸 API를 주지 않음).
- 탭 제목: Studio 문서 제목을 따르되 기본은 뷰 이름(L17 `STUDIO_VIEWS`), 포털은 고정 "Ontological Portal".
- 새 창 요청(L67–73): 포털/앱/Studio URL은 탭으로, 그 밖은 외부 브라우저. 탭 안 이동(L111)도 Studio·포털 밖이면 막고 외부 브라우저.
- 탭 분리(L145–153): 탭을 다시 로드하지 않고 새 창으로 이동.
- IPC(L210–222): 탭 조회·전환·닫기·메뉴는 **창 자신의 셸 페이지에서만**(`shellOnly`), 탭 열기·새 창·open·info·fullscreen은 우리 창/탭 어디서나.
- 메뉴 「탭」(L225–238): 홈 ⌘T, 새 창 ⌘N, 탭 닫기 ⌘W(홈이면 창 닫기), 새로고침 ⌘R, 다음/이전 Ctrl(+Shift)+Tab, ⌘1–9(숨김), 개발자 도구 ⌥⌘I.

## 8. 셸 홈 — `renderer/shell/shell.js`, `index.html`, `shell.css`
- 카드(L39–48) → feature-map 참조. 클릭 L137–143.
- 최근 항목(L211–246 `load`): `GET /api/sessions`, `/api/schemas`, `/api/board/dashboards`, `/fabric-bridge/fabric/overview`, `/api/neo4j/status`, `/codeapps/api/apps` + IPC `lite:info`. 항목 종류 session(구축/질의·액션 대화), schema(온톨로지, 클래스 수), board(대시보드), 코드 앱, datasource(엔진·테이블 수·노드 수). 날짜 내림차순.
  - 'default' 세션은 스키마·제목 변화가 없으면 숨김. mode 없는 옛 세션은 schema_name이 있으면 구축 대화로 간주.
- 필터(L50–56): 전체(최근 항목)·온톨로지·대화·앱·데이터소스. 검색: 이름+정보 부분 일치.
- 빠른 이동(L148–153): 포털 탭, 로그 폴더, 데이터 폴더.
- 상태(L198–206): Ontological 연결(`/api/neo4j/status` status==='connected', "그래프 <graph> · PostgreSQL 16 · 127.0.0.1"), 에이전트(준비/라벨/메모, 미준비 시 「설정」 버튼).
- 테마: localStorage `os-theme`(light/dark), Studio와 공유(storage 이벤트).
- 홈으로 돌아오거나 창 포커스 시 다시 로드.

## 9. 트레이 — `main/tray.js`
- 단계 라벨(L8): starting 시작하는 중 / postgres PostgreSQL 시작 중 / bootstrap 첫 실행 준비 중 / ontological Ontological 시작 중 / studio Studio 시작 중 / ready 실행 중 / error 시작하지 못함.
- 메뉴(L29–42): 상태, 에이전트 라벨, 홈·포털 탭·데이터소스 탭·새 창(준비 후), 설정 파일·로그 폴더, 종료.

## 10. 메뉴바 — `main/index.js` L319–338
앱 메뉴, 편집, 탭, 보기(확대·축소·전체화면), 런타임(포털 탭/브라우저, 에이전트 ▸ Claude Code·Codex·내장 에이전트(라디오, 설치 여부 표시), 설정 파일·로그·데이터 폴더), 창. 에이전트 전환 상세는 A3/M8.

## 11. preload — `preload/index.js`
`window.liteShell`: platform, open(what), info(), isFullScreen(), onFullScreen(cb), newWindow(), openTab(target), nl2cypher(question, graph), tabs.{get, activate, close, menu, onChange}.

## 12. 보안 관련 관찰
- Electron fuse: RunAsNode·NODE_OPTIONS·--inspect 허용, ASAR 무결성 미강제, OnlyLoadAppFromAsar 꺼짐 (REA `inspect_electron_fuses`, 1차 분석).
- 서명: ad-hoc, 공증 없음.
- 모든 서버 127.0.0.1. 웹 오리진에 인증 없음 — 같은 PC의 다른 프로세스가 `/api`, `/mcp`, `/app/status`에 접근 가능(추정, 4단계에서 확인).
- `lite:nl2cypher` IPC는 owner 확인 없이 등록(index.js L288) — preload가 있는 Studio·포털 탭에서 호출 가능.

# M8 설정 — 코드 추적 (원본 근거, 구현 세션에 넘기지 않음)

- 기준: 배포본 0.1.1. 경로 약어 `E/` = `extracted-app-asar/src/`, `R/` = `shared/app/resources/`, `B/` = `shared/app/runtime/studio/app/backend/src/`
- 에이전트 선택·실행 세부는 `common/A3-agent-mcp/code-trace.md` §1–§5 참고(중복 생략).

## S1. 「설정」 카드 → studio.env 열기

화면 → IPC → 메인 → OS

1. 카드 정의 `E/renderer/shell/shell.js:47` — `{title:'설정', desc:'studio.env — 에이전트 · LLM 키.', icon:'gear', c:'slate', action:'settings'}`
2. 클릭 `shell.js:137-143` — `action` 있으면 `window.liteShell.open('settings')`
3. preload `E/preload/index.js:10` — `ipcRenderer.invoke('lite:open', 'settings')`
4. IPC 등록 `E/main/tabs.js:219` — `anyOfOurs`(셸 페이지 또는 우리 탭이면 허용)
5. 처리 `E/main/index.js:271-277` `shellOpen('settings')` → `shell.openPath(dirs.userEnv)` → `true`. 그 밖: `logs`→로그 폴더, `data`→userData, `portal`→브라우저로 포털, 나머지 `false`
6. 경로 `E/main/index.js:74-81` — `userEnv = <userData>/studio.env`, userData = `ONTOLOGICAL_STUDIO_USER_DATA`(또는 `ONTOLOGY_LITE_USER_DATA`) 아니면 Electron 기본(`~/Library/Application Support/Ontological Studio`), 옛 이름 폴더 이전 `index.js:41-69`

같은 동작의 다른 입구:
- 상태 줄 「설정」 버튼 `shell.js:211-213` (에이전트 ready=false일 때만 렌더)
- 메뉴 `E/main/index.js:331` 「설정 파일 열기 (studio.env)」, 332 로그, 333 데이터
- 트레이 `E/main/tray.js:38-39` 「설정 파일 열기 (studio.env)」·「로그 폴더 열기」
- 홈 왼쪽 바로가기 `shell.js:149-153,161-166` — Ontological Portal(탭), 로그 폴더, 데이터 폴더 (설정은 없음)

## 파일 생성·권한

| 동작 | 위치 | 내용 |
|---|---|---|
| 첫 생성 | `E/main/index.js:112-116` `ensureUserEnv` (boot 첫 단계 `index.js:121`) | 없을 때만 `R/studio.env.example` 복사 + `chmod 0600` |
| 갱신 | `E/main/services.js:207-217` `updateUserEnv` | 줄 단위; 키마다 정규식 `^\s*#?\s*KEY\s*=`에 맞는 **첫 줄**을 `KEY=value`로 교체(주석 해제 효과), 없으면 끝(마지막 빈 줄 앞)에 추가; `writeFileSync(..., {mode: 0o600})` — mode는 새로 만들 때만 적용(기존 파일 권한 유지, Node 동작) |
| 읽기 | `E/main/services.js:34-42` `readUserEnv` | 파일 없으면 `{}`; 줄 정규식 `^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$`; 빈 값 무시; 값 양끝 따옴표 1개 제거; `#` 주석 줄은 키 패턴에 안 맞아 자동 무시; 인라인 주석은 값에 포함; 소문자 키·`export` 무시 |
| 비교: secrets.json | `E/main/postgres.js:19-28` | `mode: 0o600`; pgdata `0o700` (`postgres.js:51`), pg 비밀번호 파일 0600 (`postgres.js:53`) |

## S2. 홈 상태·배지

1. 로드 `shell.js:218-252` `load()` — 병렬 fetch: `/api/sessions`, `/api/schemas`, `/api/board/dashboards`, `/fabric-bridge/fabric/overview`, `/api/neo4j/status`, `liteShell.info()`, `/codeapps/api/apps`
2. 다시 읽는 시점 `shell.js:257-262`(홈 탭으로 돌아올 때), `shell.js:270`(창 focus이고 홈일 때), 에이전트 전환 후 메인이 `load()` 실행(`index.js:242`)
3. 정보 IPC `E/main/index.js:306-316` → `{graph, ports, phase, agent:{backend,agentId,label,ready,note}, llmConfigured: a.ready, kineticConfigured: kineticUp || !!env.KINETIC_URL, version}` — `agent`가 아직 없으면(부팅 중) 그 자리에서 `resolveAgent(studio.env)` 계산. `kineticConfigured`는 studio.env를 매번 다시 읽음
4. 그래프 상태 `B/modules/ontology/api.py:60-69` `GET /api/neo4j/status` → `{"status":"connected"}` 또는 `{"status":"disconnected","error":…}`
5. 상태 줄 `shell.js:204-212`:
   - 1행 점 `ok` iff `status==='connected'`, 문구 `Ontological 연결됨/연결 안 됨`, 부제 `그래프 <info.graph||'ontology'> · PostgreSQL 16 · 127.0.0.1`
   - 2행 점 `ok` iff `a.ready && !a.note` 아니면 `warn`; `에이전트 <a.ready ? label : '사용할 수 없음'>`; 부제 = `a.note` || (cli ? "이 PC 의 CLI 가 Studio 스킬로 구축·질의합니다" : "OpenAI 호환 LLM 으로 구축·질의합니다"); `!a.ready`면 `<button data-settings>설정</button>`
6. 배지 `shell.js:124-136`: `c.llm && info.llmConfigured === false` → `<span class="badge warn">에이전트 설정 필요</span>`(구축·질의·액션 카드, `shell.js:40-41`), `c.kinetic && info.kineticConfigured === false` → `<span class="badge">별도 서비스</span>`(시스템 등록, `shell.js:46`). `=== false` 비교라 info 실패(빈 객체)면 배지 없음

## S3/S4. 에이전트 바꾸기

- 파일 직접 수정 → 다음 시작 때 `startStudio` → `resolveAgent(readUserEnv())` (`services.js:167-168`). 실행 중엔 반영 안 됨 (studio.env 예제 3행 "바꾼 뒤에는 앱을 다시 시작한다")
- 메뉴 `E/main/index.js:253-268` `agentMenu()`: `detectAgentClis()`로 설치 여부, studio.env 요청값으로 체크. 항목 라벨 `Claude Code`/`Claude Code (설치 안 됨)`, `Codex`/`Codex (설치 안 됨)`, `내장 에이전트 (OpenAI 호환 키)`. 미설치 CLI 비활성, 전환 중 전부 비활성
- 메뉴 구성 `index.js:319-338` — 「런타임」: 포털 탭 열기 / 포털을 브라우저에서 열기 / — / 에이전트 ▸ / — / 설정 파일 열기 (studio.env) / 로그 폴더 열기 / 데이터 폴더 열기. 메뉴는 앱 시작 시와 전환 직후에만 다시 만들어짐(`buildMenu` 호출 `index.js:249,375`) → CLI를 새로 설치해도 메뉴 표시는 갱신 안 됨(추정)
- 전환 `index.js:226-251` (A3 code-trace §3)
- 진행 표시 `index.js:103-110` `progress()` — 창 URL이 `file:`일 때만(부팅 화면) `setStep` 실행. 준비 후 셸 페이지는 로컬 웹 오리진에서 로드되는지 여부에 따라 표시되지 않을 수 있음(모르는 점). 트레이 상단 `Ontological Studio — <단계>` 갱신(`tray.js:30`)

## studio.env 키별 추적

| 키 | 예제 기본 | 셸 처리 (`services.js`) | 읽는 곳 |
|---|---|---|---|
| `AGENT_BACKEND` | `cliagents` | `resolveAgent` 입력(92); 결정값으로 **덮어씀**(140) | 백엔드 `B/shared/kernel/settings.py:159` → `B/modules/agent_session/service.py:1203`, `B/modules/board/ask.py:376,466`, `B/modules/board/compose.py:130` |
| `EXTERNAL_AGENT_ID` | `claude-code` | `codex`만 인식(93); 결정값으로 덮어씀(140) | `settings.py:160`, cliagents 어댑터, `R/agent_turn.py:24`, `R/code_app_turn.py:33`, `board/ask.py:188,238` |
| `OPENAI_API_KEY` | 빈 값 | `llm` 판정(94); 빈 값이면 env에 안 들어감 | `settings.py:185` → 내장 에이전트 모델(`service.py:1012-1033`), 대시보드 API 경로(`board/ask.py:336-366`), OCR(`B/modules/document_indexing/ocr_service.py:189-192`), 문서 임베딩(`document_indexing/service.py:435,812`), 그래프 임베딩·HyDE(`B/modules/ontology/embedding.py:38-48,130-170`), 품질 추출(`B/modules/quality/extraction.py:146-160`), 그래프 자연어 질의 `POST /api/graph/nl-query`(`ontology/api.py:523-580`) |
| `OPENAI_BASE_URL` | 빈 값 | `llm` 판정(94) | `settings.py:184`; 있으면 내장 에이전트는 그 주소 + Responses API 미사용 + 스트림 모드 `updates`만(`service.py:1870-1871`); 임베딩은 OpenAI 모드가 아니게 됨 → Ollama 경로(`embedding.py:38-48`) |
| `MAJOR_MODEL` | 빈 값(→무시) | 통과 | `settings.py:164` 기본 `openai:gpt-5.4-2026-03-05`; 구축 모드 모델, 대시보드 API 경로 모델 |
| `MINOR_MODEL` | 빈 값(→무시) | 통과 | `settings.py:169` 기본 `gpt-5.4-mini-2026-03-17`; 답변·액션·브리프 모델, 임베딩 HyDE, 품질 추출 기본, nl-query |
| `KINETIC_URL` | 주석 | 있으면 번들 kinetic 미기동(`index.js:151,164-165`) + 앱 KINETIC_* 미주입(135); `kineticConfigured` 판정(`index.js:313`) | `B/modules/kinetic/client.py:71` |
| `KINETIC_MCP_URL` | 주석 | `KINETIC_URL` 없으면 앱 값으로 덮어씀 | `B/modules/kinetic/mcp_tools.py:34` |
| `KINETIC_STUDIO_TOKEN` | 주석 | 〃 | `kinetic/client.py:91` |
| `KINETIC_AGENT_TOKEN` | 주석 | 〃 | `kinetic/client.py:101`, `mcp_tools.py:35` |
| `MCP_ALLOW_DATASOURCE_EXPANSION` | 주석(`true`) | 사용자 값 || `'true'`(148) | `settings.py:200`(백엔드 자체 기본 false) → 검색 MCP 서버 도구 등록(`B/modules/ontology_mcp/server.py:200`), 확장 게이트(`runtime_adapters.py:71-85`), `ontology_query`의 answer/answer_nods(`adapters.py:75-82`) |

예제에 없지만 studio.env로 바꿀 수 있는 것(사용자 env가 그대로 Studio 프로세스에 전달되므로, 관찰): `MAJOR_MODEL_REASONING_EFFORT`, `MINOR_MODEL_REASONING_EFFORT`, `OCR_MODEL`, `OCR_MODEL_REASONING_EFFORT`, `OCR_EMBEDDING_MODEL`, `USE_OCR_CACHE`, `OLLAMA_BASE_URL`, `OLLAMA_EMBEDDING_MODEL`, `EMBEDDING_CHUNK_MAX_TOKENS`, `MCP_MAX_RESULTS`, `MCP_MAX_EXCERPT_CHARS`, `MCP_EXTRA_ALLOWED_HOSTS`, `ANSWER_TOOLS_VIA_MCP`, `DATASOURCE_ENABLED`, `DATASOURCE_MAX_ROWS`, `DATASOURCE_AGENT_ROW_PREVIEW`, `DATASOURCE_NL_FALLBACK_ENABLED`, `DATAFABRIC_TIMEOUT_SECONDS`, `DATAFABRIC_CATALOG_TTL_SECONDS`, `TEXT2SQL_TIMEOUT_SECONDS`, `TEXT2SQL_REACT_TIMEOUT_SECONDS`, `DOMAIN_LAYER_URL`/`WHATIF_API_URL`, `DOMAIN_LAYER_TIMEOUT_SECONDS`, `ER_RERANK_URL`(앱 기본 막힘 주소), `ER_*` 임계값들, `QUALITY_EXTRACT_MODEL`, `QUALITY_EXTRACT_LOGPROBS`, `QUALITY_CHUNK_CHARS`, `QUALITY_HEADER_CHARS`, `INGEST_GATE`, `AGENT_HISTORY_MAX_TOKENS`, `KINETIC_MCP_TIMEOUT`, `KINETIC_ROLE_CATALOG`(KINETIC_URL 있을 때만 유효), `ONTOLOGICAL_ADMIN_PROD_URL`, `BOARD_STORAGE_DIR`, `BOARD_SAMPLE_LIMIT`, `ONTOLOGY_RELEASE_DIR`, `SMART_LOGGER_BLACKLIST_MESSAGES` (목록: `grep os.environ.get` 결과, `settings.py:157-234`).

**앱이 덮어써서 studio.env로 못 바꾸는 것** (`services.js:124-157`, MCP 프로세스는 171-173 추가): `PATH`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`, `ONTOLOGICAL_ADMIN_DEV_URL`, `DATAFABRIC_BASE_URL`, `TEXT2SQL_BASE_URL`, `AGENT_BACKEND`, `EXTERNAL_AGENT_ID`, `SANDBOX_BACKEND`, `LOCAL_SANDBOX_ROOT`, `SANDBOX_WORKDIR`, `BACKEND_HOST`, `BACKEND_PORT`, `ANSWER_MCP_TRANSPORT`, `ANSWER_MCP_URL`, `BOARD_MCP_TRANSPORT`, `BOARD_MCP_URL`, `MAIN_LOG_PATH`, `DETAIL_LOG_DIR`, `SESSION_DB_PATH`, `PYTHONPATH`, `PYTHONUNBUFFERED`, `PYTHONDONTWRITEBYTECODE`, `PYTHON_DOTENV_DISABLED`, (`baseEnv`) `PYTHONUTF8`, `PYTHONIOENCODING`, (MCP 프로세스) `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT`, (KINETIC_URL 없을 때) `KINETIC_URL`·`KINETIC_MCP_URL`·`KINETIC_STUDIO_TOKEN`·`KINETIC_AGENT_TOKEN`·`KINETIC_ROLE_CATALOG`.

studio.env가 **전달되지 않는** 프로세스(관찰): Bolt 게이트웨이(`services.js:9-19`), 포털(`services.js:22-32`), kinetic-action·예제 서비스(`E/main/kinetic.js:58-66,68-90` — `pyEnv`+`secretsEnv`만), PostgreSQL. 셸 자신의 nl2cypher·codeapps는 studio.env를 직접 읽지 않고 Studio 스크립트 env를 통해 간접 사용.

## 튜토리얼 대조
- 01장: "CLI → 없으면 내장(키 필요)", "홈 왼쪽 아래 에이전트", "런타임 › 에이전트", "「설정」 카드 → studio.env" — 코드와 일치.
- 02장 카드 표 "설정 | studio.env — 에이전트와 LLM 키" — 일치.
- 23장 "「에이전트 설정 필요」 → CLI 설치·로그인 후 메뉴에서 고르거나 앱 재시작; 또는 OPENAI_API_KEY" — 일치. 단 CLI를 새로 설치한 직후 메뉴의 `(설치 안 됨)` 표시는 메뉴를 다시 만들기 전까지 남을 수 있음(추정) → 재시작이 확실.
- 14장 "등록 시스템 비밀 값은 studio.env에" — **불일치 의심**: kinetic-action 프로세스는 studio.env를 받지 않는다(위). M7에서 확인.
- studio.env 예제 21-22행 "키네틱 액션은 … 이 패키지에는 들어 있지 않다" — 0.1.1은 번들 실행 → 낡은 설명.

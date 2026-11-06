# M8 설정 — 설계 문서 (클린룸)

- 대상: Ontological Studio 0.1.1과 같은 동작을 하는 새 구현
- 원본 코드·파일 경로·내부 이름은 넣지 않는다. 설정 키 이름, 화면 문구, 파일 이름처럼 밖에서 보이는 계약만 적는다.
- 에이전트 선택 규칙과 실행 방식은 A3 설계 문서(§4, §5)를 따른다. 여기서는 사용자가 보는 설정 표면을 정한다.

---

## 1. 목적
사용자가 (1) 어떤 에이전트로 구축·질의할지, (2) 내장 에이전트용 LLM 접속 정보, (3) 외부 액션 실행기 주소, (4) 로컬 MCP 실데이터 노출 여부를 정한다. 앱 안에 설정 편집 화면은 두지 않고, **사용자 데이터 폴더의 텍스트 파일 `studio.env`** 를 OS 기본 앱으로 열어 고치게 한다. 에이전트 선택만은 메뉴로도 바꿀 수 있다.

## 2. 사용자 시나리오 (요약)
- 홈 「설정」 카드 → studio.env가 OS 기본 앱으로 열림 → 고치고 저장 → 앱 재시작 시 반영.
- 메뉴 「런타임 › 에이전트」에서 Claude Code / Codex / 내장 에이전트 선택 → 즉시 반영(Studio만 재시작).
- 홈 왼쪽 아래 상태 줄로 그래프 연결과 에이전트 상태를 본다. 에이전트를 쓸 수 없으면 「설정」 버튼과 카드 배지가 보인다.
- 로그 폴더·데이터 폴더를 바로 연다.

## 3. 화면 구성과 상호작용

### 3.1 홈 카드 (8개 중 마지막)
- 제목 `설정`, 설명 `studio.env — 에이전트 · LLM 키.`, 톱니 아이콘, 회색 계열.
- 누르면 셸 동작 `settings` 실행 → studio.env를 OS 기본 앱으로 연다. 탭은 열지 않는다.

### 3.2 홈 상태 줄 (왼쪽 아래, 2행)
| 행 | 점 | 굵은 글씨 | 뒤 글씨 | 작은 글씨 | 버튼 |
|---|---|---|---|---|---|
| 그래프 | 초록(연결) / 빨강 | `Ontological` | `연결됨` / `연결 안 됨` | `그래프 <그래프 이름(없으면 ontology)> · PostgreSQL 16 · 127.0.0.1` | – |
| 에이전트 | 초록(준비됨이고 안내 문구 없음) / 노랑(그 밖) | `에이전트` | 준비됨이면 표시 이름(`Claude Code`·`Codex`·`내장 에이전트`), 아니면 `사용할 수 없음` | 안내 문구가 있으면 그것, 없으면 CLI 방식 `이 PC 의 CLI 가 Studio 스킬로 구축·질의합니다` / 내장 `OpenAI 호환 LLM 으로 구축·질의합니다` | 준비 안 됨일 때만 `설정`(누르면 3.1과 같음) |
- 그래프 연결 여부는 백엔드 `GET /api/neo4j/status`의 `status === "connected"`.
- 에이전트 정보는 셸 정보 API(§4.1).

### 3.3 카드 배지
- 에이전트 정보의 `llmConfigured`가 **정확히 false**일 때 「온톨로지 구축」·「질의·액션」 카드 제목 옆에 경고 배지 `에이전트 설정 필요`.
- `kineticConfigured`가 정확히 false일 때 「시스템 등록」 카드에 일반 배지 `별도 서비스`.
- 정보를 못 받으면(값 없음) 배지를 달지 않는다.
- 다시 그리는 시점: 홈을 처음 열 때, 다른 탭에서 홈으로 돌아올 때, 창이 포커스를 얻었는데 홈이 활성일 때, 에이전트 전환이 끝났을 때.

### 3.4 메뉴 「런타임」
순서대로: `Ontological 포털 탭 열기` · `Ontological 포털을 브라우저에서 열기` · 구분선 · `에이전트` ▸ · 구분선 · `설정 파일 열기 (studio.env)` · `로그 폴더 열기` · `데이터 폴더 열기`.

`에이전트` 하위(라디오 3개):
| 항목 | 라벨 | 활성 | 체크 조건 |
|---|---|---|---|
| Claude Code | `Claude Code`, 미설치면 `Claude Code (설치 안 됨)` | 설치됨 && 전환 중 아님 | studio.env의 방식이 `cliagents`이고 CLI id가 claude-code |
| Codex | `Codex` / `Codex (설치 안 됨)` | 〃 | 방식 `cliagents` && id `codex` |
| 내장 | `내장 에이전트 (OpenAI 호환 키)` | 전환 중 아님 | 방식이 `cliagents`가 아님 |
- 체크는 **파일에 적힌 요청값** 기준이다(실제 실행값과 다를 수 있음 — 예: CLI가 없어 내장으로 실행 중이어도 Claude Code에 체크).
- 설치 여부는 A3 §4.2의 보충 PATH 탐색으로 판단. 메뉴는 앱 시작 때와 전환 직후에만 다시 만든다.
- 선택 시 동작은 A3 §4.4(파일 갱신 → Studio 두 프로세스 재시작 → 탭 새로고침).

### 3.5 트레이 메뉴 (설정 관련 항목)
맨 위 비활성 `Ontological Studio — <단계>`, 에이전트가 정해졌으면 비활성 `에이전트: <표시 이름>`, … , `설정 파일 열기 (studio.env)`, `로그 폴더 열기`, 구분선, `종료`.

### 3.6 홈 왼쪽 바로가기
`Ontological Portal`(포털 탭), `로그 폴더`, `데이터 폴더` — 설정 파일은 없다(카드로 대신).

## 4. API·IPC 명세

### 4.1 셸 정보 (렌더러 → 메인, 요청-응답)
요청 인자 없음. 응답:
```json
{
  "graph": "<그래프 이름>",
  "ports": { "...": 0 },
  "phase": "starting|postgres|bootstrap|ontological|studio|ready|error",
  "agent": { "backend": "cliagents|deepagents", "agentId": "claude-code|codex",
             "label": "Claude Code|Codex|내장 에이전트", "ready": true, "note": null },
  "llmConfigured": true,
  "kineticConfigured": true,
  "version": "0.1.1"
}
```
- `agent`: Studio가 시작돼 있으면 그때 결정된 값, 아직이면 현재 studio.env로 즉석 계산(A3 §4.3).
- `llmConfigured` = `agent.ready` (이름과 달리 "에이전트 준비됨"을 뜻함; CLI가 있으면 키가 없어도 true).
- `kineticConfigured` = 번들 액션 실행기가 떠서 시스템 등록까지 끝났음 **또는** studio.env에 `KINETIC_URL`이 있음(파일을 매번 다시 읽음).
- 셸 페이지와 앱의 탭 모두에서 호출 가능.

### 4.2 셸 동작 열기 (렌더러 → 메인)
인자 `what`: `settings` → studio.env를 OS 기본 앱으로, `logs` → 로그 폴더, `data` → 사용자 데이터 폴더, `portal` → 포털을 외부 브라우저로. 성공 시 `true`, 모르는 값이면 `false`. 셸 페이지와 탭 모두 호출 가능. 대상은 고정 목록뿐(임의 경로 금지).

### 4.3 백엔드
- `GET /api/neo4j/status` → `{"status":"connected"}` 또는 `{"status":"disconnected","error":"…"}`.
- 홈은 그 밖에 최근 항목용 API를 함께 부른다(A1·각 메뉴 범위).

## 5. 데이터 모델 — studio.env

### 5.1 위치·생성·권한
- `<사용자 데이터 폴더>/studio.env`. 사용자 데이터 폴더 = 환경 변수 `ONTOLOGICAL_STUDIO_USER_DATA`(옛 이름 `ONTOLOGY_LITE_USER_DATA`)가 있으면 그 경로, 없으면 OS 앱 데이터 위치의 `Ontological Studio`(macOS `~/Library/Application Support/Ontological Studio/`).
- 앱 시작 첫 단계에서 파일이 없으면 번들의 예제 파일을 복사하고 권한을 **0600**으로 바꾼다. 있으면 건드리지 않는다.
- 같은 폴더의 비밀 파일(`secrets.json`)도 0600, DB 데이터 폴더 0700 — 설정 파일과 같은 정책.

### 5.2 읽기 규칙
- 줄 단위. 한 줄이 `공백* KEY 공백* = 공백* VALUE` 이고 KEY가 대문자·숫자·밑줄만이면 항목. 그 밖의 줄(`#` 주석, 빈 줄, 소문자 키, `export KEY=…`)은 무시.
- VALUE가 빈 문자열이면 **항목 없음**으로 본다(→ 백엔드 기본값이 쓰임).
- VALUE 양끝의 따옴표(`"` 또는 `'`) 한 쌍을 벗긴다(각 끝에서 한 글자). 이스케이프·인라인 주석 처리 없음(`KEY=a # b`의 값은 `a # b`). 뒤쪽 공백은 남는다(원본 그대로; 재현 여부는 구현 결정).
- 같은 키가 여러 번 나오면 뒤의 것이 이긴다.

### 5.3 쓰기 규칙 (메뉴 전환에서만 사용)
- 키마다 `^공백* #? 공백* KEY 공백* =` 에 맞는 **첫 줄**을 `KEY=value`로 바꾼다(주석 처리된 줄도 대상 → 주석이 풀림). 없으면 파일 끝에 추가하되, 마지막 줄이 빈 줄이면 그 앞에 넣는다.
- 파일이 없으면 새로 만들고 0600. 다른 줄·주석·순서는 보존.

### 5.4 키 목록 (예제 파일에 있는 것)
예제 파일 머리말(뜻): 이 파일은 사용자 데이터 폴더에 복사되어 쓰인다 / 그래프 접속·데이터 패브릭 주소·포트는 앱이 정하므로 여기서 못 바꾼다 / 바꾼 뒤에는 앱을 다시 시작한다 / 에이전트는 메뉴 「런타임 → 에이전트」에서 바꿔도 된다.

| 키 | 예제 값 | 뜻 | 기본값(비었을 때) | 쓰는 쪽 |
|---|---|---|---|---|
| `AGENT_BACKEND` | `cliagents` | 구축·질의 대화를 누가 실행하나. `cliagents`=이 PC의 코딩 CLI(기본, 키 불필요, CLI가 없으면 내장으로), `deepagents`=내장(키 필요) | `cliagents` | 셸의 에이전트 결정(A3 §4.3) → 결정값이 Studio에 강제 전달 |
| `EXTERNAL_AGENT_ID` | `claude-code` | cliagents일 때 쓸 CLI: `claude-code` 또는 `codex` | `claude-code` (`codex` 외 값은 모두 claude-code) | 셸 결정, Studio 백엔드, 단발 스크립트 |
| `OPENAI_API_KEY` | (빈 값) | 내장 에이전트용 키. CLI 방식에서도 일부 부가 기능이 직접 씀: 스캔 문서 OCR, 임베딩, 품질 추출(그 밖에 대시보드 대체 경로, 그래프 자연어 질의 API). 비우면 그 기능만 안 됨 | 없음 | Studio 백엔드 |
| `OPENAI_BASE_URL` | (빈 값) | OpenAI 호환 엔드포인트 주소. 키 없이 이것만 있어도 "LLM 설정됨"으로 봄. 있으면 임베딩은 OpenAI 대신 로컬 Ollama 경로를 씀(원본 동작) | 없음(OpenAI 공식) | Studio 백엔드 |
| `MAJOR_MODEL` | (빈 값) | 큰 모델 — 구축 모드, 대시보드 API 경로. `provider:model` 또는 `model` | `openai:gpt-5.4-2026-03-05` | Studio 백엔드 |
| `MINOR_MODEL` | (빈 값) | 작은 모델 — 답변·액션·브리프 모드, HyDE, 품질 추출 기본, 그래프 자연어 질의 | `gpt-5.4-mini-2026-03-17` | Studio 백엔드 |
| `KINETIC_URL` | (주석) `http://127.0.0.1:9000` | 따로 띄운 액션 실행기 주소. 있으면 번들 실행기·예제 서비스를 띄우지 않고 이 주소를 씀 | 번들 실행기 주소(앱이 넣음) | 셸(기동 여부·배지), Studio 백엔드 |
| `KINETIC_MCP_URL` | (주석) `http://127.0.0.1:9000/mcp/kinetic/` | 실행기의 MCP 주소 | 번들 값 | Studio 백엔드(act 모드 도구) |
| `KINETIC_STUDIO_TOKEN` | (주석) 빈 값 | 화면·대시보드·코드 앱 버튼이 계획을 만들 때 쓰는 토큰 | 번들: 셸이 발급(관리자·승인자·예제 역할) | Studio 백엔드 |
| `KINETIC_AGENT_TOKEN` | (주석) 빈 값 | 에이전트가 실행기를 부를 때 쓰는 토큰 | 번들: 셸이 발급(운영자 역할) | Studio 백엔드 |
| `MCP_ALLOW_DATASOURCE_EXPANSION` | (주석) `true` | 로컬 MCP 서버(127.0.0.1)의 실데이터 도구(그래프 Cypher·데이터소스 스키마·SQL·엔티티 해석)를 켤지. 대시보드와 질의 에이전트가 씀. 끄면 다른 AI 클라이언트가 원천 행을 못 읽지만 대시보드 자동 구성도 안 됨 | 앱이 `true`를 넣음 | 검색 MCP 서버, 백엔드 |

- `KINETIC_*` 규칙: `KINETIC_URL`이 **없으면** 나머지 `KINETIC_*`를 studio.env에 적어도 앱 값으로 덮어쓴다. `KINETIC_URL`이 **있으면** 앱은 아무 `KINETIC_*`도 넣지 않는다(사용자가 네 개 모두 책임).

### 5.5 예제에 없지만 통하는 키
studio.env의 모든 항목은 Studio 백엔드·검색 MCP 서버 환경에 그대로 들어가므로(§5.6 제외), 백엔드가 읽는 다른 설정도 바꿀 수 있다. 구현은 최소한 다음을 같은 이름·같은 기본값으로 받는다:
- 모델: `MAJOR_MODEL_REASONING_EFFORT`(medium), `MINOR_MODEL_REASONING_EFFORT`(medium), `OCR_MODEL`(gpt-5.4-mini-2026-03-17), `OCR_MODEL_REASONING_EFFORT`(none), `OCR_EMBEDDING_MODEL`(openai:text-embedding-3-small), `USE_OCR_CACHE`(false), `OLLAMA_BASE_URL`(http://localhost:11434), `OLLAMA_EMBEDDING_MODEL`(qwen3-embedding), `EMBEDDING_CHUNK_MAX_TOKENS`(1000), `QUALITY_EXTRACT_MODEL`(MINOR_MODEL)
- MCP: `MCP_MAX_RESULTS`(20), `MCP_MAX_EXCERPT_CHARS`(500), `MCP_EXTRA_ALLOWED_HOSTS`(없음), `ANSWER_TOOLS_VIA_MCP`(true)
- 데이터소스: `DATASOURCE_ENABLED`(true), `DATASOURCE_MAX_ROWS`(500), `DATASOURCE_AGENT_ROW_PREVIEW`(30), `DATASOURCE_NL_FALLBACK_ENABLED`(true), 시간 제한들
- 기타: `AGENT_HISTORY_MAX_TOKENS`(48000), `ER_RERANK_URL`(앱 기본: 닿지 않는 자리표시 주소), `ONTOLOGICAL_ADMIN_PROD_URL`(앱 기본: 닿지 않는 자리표시 주소)
- 불리언 해석: `1/true/yes/on`(대소문자 무관)만 참.

### 5.6 앱이 정해 studio.env로 못 바꾸는 값
Studio 프로세스 환경을 만들 때 순서는 "OS 환경 → studio.env → 앱 고정값"이며 앱 고정값이 이긴다.
- 그래프 접속: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`
- 데이터 패브릭·SQL 브리지 주소: `DATAFABRIC_BASE_URL`, `TEXT2SQL_BASE_URL`
- 관리 API 개발 주소: `ONTOLOGICAL_ADMIN_DEV_URL`
- 에이전트 결정값: `AGENT_BACKEND`, `EXTERNAL_AGENT_ID` (사용자 값은 결정의 입력으로만 쓰임)
- 샌드박스: `SANDBOX_BACKEND`(local), `LOCAL_SANDBOX_ROOT`(<데이터>/sandbox), `SANDBOX_WORKDIR`(/workspace)
- 백엔드 주소: `BACKEND_HOST`(127.0.0.1), `BACKEND_PORT`
- 내부 MCP 클라이언트: `ANSWER_MCP_TRANSPORT`, `ANSWER_MCP_URL`, `BOARD_MCP_TRANSPORT`, `BOARD_MCP_URL`
- 검색 MCP 서버 자신: `MCP_TRANSPORT`(http), `MCP_HOST`(127.0.0.1), `MCP_PORT`
- 로그·DB 위치: `MAIN_LOG_PATH`, `DETAIL_LOG_DIR`, `SESSION_DB_PATH`
- 실행 환경: `PATH`(보충 경로), `PYTHONPATH`, `PYTHONUNBUFFERED`, `PYTHONDONTWRITEBYTECODE`, `PYTHONUTF8`, `PYTHONIOENCODING`, 그리고 `.env` 자동 탐색 끄기(설치 위치 위의 엉뚱한 `.env`를 읽지 않도록)
- `KINETIC_URL`이 없을 때의 `KINETIC_URL`, `KINETIC_MCP_URL`, `KINETIC_STUDIO_TOKEN`, `KINETIC_AGENT_TOKEN`, `KINETIC_ROLE_CATALOG`
- 포트는 별도 파일(`ports.json`)로 앱이 관리(A1).

studio.env가 **전달되지 않는** 프로세스: 그래프 Bolt 게이트웨이, 포털 서버, 번들 액션 실행기, 예제 업무 서비스, PostgreSQL.

## 6. 상태·저장
- 설정은 파일 하나가 원천. 앱은 메모리에 "현재 실행 중인 에이전트 결정값"만 둔다(정보 API·트레이용).
- 파일 직접 수정은 앱 재시작 때 반영. 예외: `kineticConfigured`는 정보 요청마다 파일을 다시 읽으므로 배지는 즉시 바뀔 수 있다(실제 실행기 연결은 재시작 후).
- 메뉴 전환은 파일을 고친 뒤 Studio를 재시작하므로 즉시 반영.

## 7. 다른 기능과의 의존
- A1: 사용자 데이터 폴더 결정, 부팅 순서(설정 파일 보장은 부팅 첫 단계), 탭·창·트레이, 셸 IPC 경로 검사.
- A3: 에이전트 결정·전환·실행.
- M7: `KINETIC_*`와 번들 실행기, 「시스템 등록」 배지.
- M1·M2: 「에이전트 설정 필요」 배지 대상 카드.
- M4: 포털 자연어→Cypher는 CLI 방식일 때만 동작.
- M5: `MCP_ALLOW_DATASOURCE_EXPANSION`이 대시보드 자동 구성에 영향.

## 8. 오류·예외
| 상황 | 동작 |
|---|---|
| studio.env가 실행 중 삭제됨 | 읽기는 빈 설정으로(→ 기본값). 다음 시작 때 예제 다시 복사. 메뉴 전환을 하면 두 줄짜리 새 파일 생성(0600) |
| 파일에 알 수 없는 키·잘못된 줄 | 조용히 무시(검증·오류 표시 없음) |
| CLI 없음 + 키 없음 | 홈 `에이전트 사용할 수 없음`, `설정` 버튼, 배지. 앱은 계속 동작(에이전트 불필요 기능 사용 가능) |
| 메뉴 전환이 준비 전·전환 중 | 무시 |
| 전환 중 Studio 재시작 실패 | 셸 상태의 마지막 오류에 기록, 로그 `agent switch failed: …` |
| OS에 `.env` 연결 앱이 없음 | OS 동작에 맡김(원본은 결과를 확인하지 않고 true 반환) |

## 9. 원본과 비교할 테스트 항목
1. 첫 실행 후 studio.env 내용이 예제와 바이트 단위로 같고 권한 0600.
2. 「설정」 카드·상태 줄 버튼·메뉴·트레이 네 입구가 같은 파일을 연다.
3. 정보 API 응답의 키 집합과, 결정 표 다섯 경우의 `agent`·`llmConfigured` 값.
4. `KINETIC_URL` 유무에 따른 `kineticConfigured`와 「시스템 등록」 배지.
5. 홈 상태 줄 문구·점 색(정상, 키 없음+CLI 없음, CLI 없음+키 있음).
6. 메뉴 「런타임」 항목 순서와 「에이전트」 하위 라벨·활성·체크.
7. 메뉴 전환 후 studio.env diff: (a) 키가 있으면 같은 줄 교체, (b) 주석 처리된 키는 주석 해제, (c) 없으면 끝(마지막 빈 줄 앞)에 추가, (d) 나머지 줄 보존.
8. §5.6의 키를 studio.env에 넣어도 Studio 프로세스 환경 값이 바뀌지 않는다.
9. §5.2 읽기 규칙: 빈 값 무시, 따옴표 제거, 인라인 주석 미처리, 소문자 키 무시.
10. `MCP_ALLOW_DATASOURCE_EXPANSION=false`에서 검색 MCP 도구가 4개.

## 10. 모르는 점 (4단계 실행 기록에서 확인)
- macOS에서 `.env` 파일을 OS 기본 앱으로 열 때 실제로 무엇이 뜨는가(연결 앱 없으면 오류 대화상자인지).
- 메뉴 전환 중 진행 문구가 화면 어디에 보이는가(부팅 화면이 아니므로 표시 안 될 가능성). 트레이 첫 줄은 바뀜.
- 내장 에이전트 + 키 없음에서 Studio가 정상 기동하는가, 그때 Studio 탭 동작.
- CLI를 새로 설치한 뒤 메뉴의 `(설치 안 됨)` 표시가 앱 재시작 없이 바뀌는가(메뉴 재구성 시점 추정상 안 바뀜).
- 비활성 라디오가 체크된 채로 표시되는 경우(요청은 Claude Code인데 미설치)의 실제 모습.
- 튜토리얼 14장의 "등록 시스템 비밀 값은 studio.env에" 안내가 실제로 동작하는가(액션 실행기는 studio.env를 받지 않음 — M7).
- 기존 studio.env 권한이 0600이 아닐 때 메뉴 전환이 권한을 고치지 않는지(정적 분석상 안 고침).

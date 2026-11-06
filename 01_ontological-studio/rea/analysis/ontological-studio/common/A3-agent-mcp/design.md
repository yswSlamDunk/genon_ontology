# A3 에이전트·MCP — 설계 문서 (클린룸)

- 대상: Ontological Studio 0.1.1과 같은 동작을 하는 새 구현
- 이 문서만으로 구현할 수 있게 쓴다. 원본 코드·파일 경로·내부 함수 이름은 넣지 않는다. 외부에서 관찰되는 계약(환경 변수 이름, HTTP 경로, MCP 도구 이름, CLI 인자, 화면 문구)은 비교 테스트를 위해 적는다.
- 관련 문서: M8 설정(에이전트 선택 화면·studio.env), M1 구축, M2 질의·액션, M4 포털(자연어→Cypher), M5 온톨로지 앱(대시보드·코드 앱)

---

## 1. 목적

온톨로지 구축·질의·액션·대시보드·코드 앱·자연어→Cypher의 "생각하는 부분"을 **에이전트**에게 맡긴다. 에이전트는 두 종류 중 하나다.

1. **외부 CLI 에이전트 (기본, 이름 `cliagents`)** — 사용자의 PC에 설치·로그인된 코딩 CLI(Claude Code 또는 Codex)를 자식 프로세스로 띄운다. CLI가 자기 모델·로그인을 쓰므로 API 키가 필요 없다. 앱의 도구는 **MCP(HTTP)** 로, 지시문은 **스킬 파일 + 추가 시스템 프롬프트**로 넘긴다.
2. **내장 에이전트 (이름 `deepagents`)** — 백엔드 프로세스 안에서 OpenAI 호환 API로 모델을 부르는 도구 사용 에이전트. 같은 도구를 파이썬 함수로 직접 쥔다. `OPENAI_API_KEY` 또는 `OPENAI_BASE_URL`이 필요하다.

두 방식은 같은 스킬(지시문)과 같은 모드별 도구 목록을 쓰며, 화면에는 같은 스트리밍 이벤트로 보인다.

또한 앱은 외부 AI 클라이언트용 **읽기 전용 검색 MCP 서버**를 하나 띄운다.

## 2. 사용자 시나리오 (요약)
- 첫 실행: CLI가 있으면 자동으로 그것을 쓴다. 없으면 내장 에이전트로 내려가고, 키도 없으면 "사용할 수 없음"으로 보인다.
- 메뉴 「런타임 › 에이전트」로 Claude Code / Codex / 내장 에이전트를 바꾼다 → 설정 파일에 기록하고 Studio 프로세스 둘만 재시작한다.
- 구축·질의 대화 한 턴 = CLI 프로세스 하나(또는 내장 에이전트 실행 하나). 진행은 SSE로 화면에 흐른다.
- Claude Code 사용 중에는 턴 실행 중 추가 지시를 끼워 넣을 수 있다(steering).
- 앱 종료 시 실행 중인 에이전트 프로세스는 모두 정리된다.
- 외부 AI 클라이언트는 로컬 MCP 서버에 붙어 온톨로지를 검색할 수 있다.

## 3. 화면 구성과 상호작용 (A3 범위)
A3 자체 화면은 없다. 노출 지점:
- 홈 상태 줄·카드 배지 — M8 설정 문서에 상세.
- 트레이 메뉴의 비활성 항목 `에이전트: <표시 이름>`.
- 메뉴 「런타임 › 에이전트」 라디오 3개 — M8에 상세.
- 대화 화면의 스트리밍 표시(도구 칩, 끼어들기 표시, 질문 카드) — M1·M2에 상세. 여기서는 이벤트 계약만 정한다(§5.4).

## 4. 에이전트 선택 규칙

### 4.1 입력
사용자 설정 파일(studio.env, M8)의 `AGENT_BACKEND`, `EXTERNAL_AGENT_ID`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`.

### 4.2 CLI 찾기
- 찾을 실행 파일: Claude Code → `claude`, Codex → `codex`.
- 앱이 Finder/시작 메뉴에서 열리면 PATH가 짧다. 현재 PATH 뒤에 흔한 설치 위치를 덧붙여 찾는다.
  - macOS/Linux: `/opt/homebrew/bin`, `/usr/local/bin`, `~/.local/bin`, `~/.bun/bin`, `~/.deno/bin`, `~/.volta/bin`, `~/.npm-global/bin`, `~/.claude/local`
  - Windows: `%APPDATA%\npm`, `~/.local/bin`, `~/scoop/shims` (확장자는 PATHEXT)
- 실행 권한이 있는 일반 파일이면 "설치됨". 같은 보충 PATH를 Studio 프로세스에도 넘겨, 백엔드도 같은 결과를 얻게 한다.

### 4.3 결정 표
`EXTERNAL_AGENT_ID`가 정확히 `codex`면 Codex, 그 밖(빈 값·오타 포함)은 Claude Code. `llm` = `OPENAI_API_KEY` 또는 `OPENAI_BASE_URL` 중 하나라도 비어 있지 않음.

| `AGENT_BACKEND` | 선택된 CLI 존재 | llm | 실행 방식 | 표시 이름 | 준비됨 | 안내 문구 |
|---|---|---|---|---|---|---|
| 없음 또는 `cliagents`(대소문자 무관) | 예 | – | cliagents | `Claude Code` / `Codex` | 예 | 없음 |
| 〃 | 아니오 | 예 | deepagents | `내장 에이전트` | 예 | `` `<cli>` 를 찾지 못해 내장 에이전트로 실행합니다. <표시 이름> 를 설치하면 다음 시작부터 씁니다.`` |
| 〃 | 아니오 | 아니오 | deepagents | `내장 에이전트` | 아니오 | `` `<cli>` 를 찾지 못했고 LLM 키도 없습니다. <표시 이름> 를 설치하거나 studio.env 에 OPENAI_API_KEY 를 넣으세요.`` |
| 그 밖의 값(예 `deepagents`) | – | 예 | deepagents | `내장 에이전트` | 예 | 없음 |
| 〃 | – | 아니오 | deepagents | `내장 에이전트` | 아니오 | `AGENT_BACKEND=deepagents 인데 LLM 접속 정보(OPENAI_API_KEY 또는 OPENAI_BASE_URL)가 비어 있습니다.` |

- 이 결정은 Studio 프로세스 시작 때 한 번(그리고 단발 스크립트를 띄울 때마다) 내린다. 결정 결과(실행 방식·CLI id)를 Studio 프로세스 환경에 **강제로** 넣는다 — 사용자가 적은 값과 다를 수 있다(예: CLI가 없으면 `cliagents`를 적어도 `deepagents`로 실행).
- 이유: CLI 방식으로 시작했는데 CLI가 없으면 백엔드가 기동 단계에서 실패하므로, 셸이 미리 내린다.
- 로그 한 줄: `에이전트: <표시 이름> (AGENT_BACKEND=<방식>[, <cli id>])[ — <안내 문구>]`.

### 4.4 실행 중 전환
- 입력: `claude-code` | `codex` | `deepagents`.
- 앱이 준비 완료 상태가 아니거나 이미 전환 중이면 무시.
- 설정 파일 갱신: `deepagents`면 `AGENT_BACKEND=deepagents`만, 아니면 `AGENT_BACKEND=cliagents`와 `EXTERNAL_AGENT_ID=<id>`. 갱신 규칙은 M8 §데이터 모델 참고(같은 키 줄 또는 주석 처리된 같은 키 줄을 대체, 없으면 끝에 추가, 권한 0600).
- 진행 표시 `에이전트를 바꾸어 Studio 를 다시 시작합니다` → Studio 백엔드와 검색 MCP 서버만 정지(각 8초 유예) → §4.3으로 다시 결정해 둘 다 시작 → `준비 완료`.
- 열린 Studio 탭은 다시 로드, 셸 홈은 상태를 다시 읽는다. DB·그래프 게이트웨이·포털·액션 실행기는 계속 돈다.
- 실패하면 마지막 오류로 기록(상태 API에 노출)하고 메뉴를 다시 그린다.
- 결과적으로 진행 중이던 CLI 대화의 이어짐(세션 id)은 끊긴다(백엔드 메모리에만 있으므로).

## 5. 외부 CLI 에이전트 실행 계약

### 5.1 모드
대화 한 줄기(thread)는 `<세션 id>:<모드>`로 구분한다. 모드와 스킬·도구 표면:

| 모드 | 쓰임 | 지시문(스킬) | MCP 엔드포인트 | 쓰기 권한 |
|---|---|---|---|---|
| `build` | 온톨로지 구축(M1) | 구축 스킬 | `/mcp/agent-bridge/build/` | 그래프·스키마·파일·실행 |
| `brief_draft` | 구축 의도·골든 퀘스천 초안(M1) | 브리프 초안 스킬 | `/mcp/agent-bridge/brief_draft/` | 없음(가장 좁음) |
| `answer` | 질문 답변 | 답변 스킬(§7) | `/mcp/agent-bridge/answer/` | 없음 |
| `answer_nods` | 실데이터 도구를 뺀 답변(외부 MCP 질의 시) | 답변 스킬 | `/mcp/agent-bridge/answer_nods/` | 없음 |
| `act` | 질의·액션(M2) | 답변+액션 합본(§7) | `/mcp/agent-bridge/act/` | 외부 시스템(실행기 경유), 승인 불가 |
| `dashboard` | 대시보드 편집(M5) | 대시보드 스킬 | `/mcp/agent-bridge/dashboard/` | 대시보드 명세 패치 |

HTTP API의 `mode` 파라미터로 화면이 직접 고르는 것은 `build`, `answer`, `act` 셋이다.

### 5.2 작업 폴더
- 대화마다 하나: `<사용자 데이터>/sandbox/sessions/<세션 id 정리값>/`. 정리값 = 세션 id에서 영숫자·`-`·`_`만 남기고 64자로 자름, 비면 `_shared`. thread의 `:<모드>` 꼬리는 떼고 세션 단위로 공유한다(업로드 API와 같은 폴더여야 하므로).
- 하위에 `uploads/`(사용자 업로드), `output/`(파서·결과물)을 만든다.
- 그 대화에서 처음 턴을 돌릴 때 스킬 폴더 전체(본문+참조 파일)를 CLI가 읽는 위치에 쓴다:
  - Claude Code: `.claude/skills/<스킬 이름>/SKILL.md` (+ 같은 폴더에 참조 파일)
  - Codex: `.agents/skills/<스킬 이름>/SKILL.md` — frontmatter에 `name`·`description`이 없으면 채워 넣는다.
- CLI 프로세스의 작업 디렉터리 = 이 폴더.

### 5.3 시스템 프롬프트
`<스킬 본문>` + 빈 줄 + 아래 세 줄짜리 환경 블록(호스트 실제 경로):
```
[환경]
스킬 폴더: <작업 폴더>/<CLI별 스킬 폴더>
업로드: <작업 폴더>/uploads
출력: <작업 폴더>/output
```
환경 블록에는 값만 넣고 지시문은 넣지 않는다(지시문의 원천은 스킬 파일 하나).

### 5.4 Claude Code 실행
명령줄:
```
claude -p
  --input-format stream-json --output-format stream-json --verbose
  --mcp-config '{"mcpServers":{"ontology-studio":{"type":"http","url":"http://127.0.0.1:<백엔드 포트>/mcp/agent-bridge/<모드>/"}}}'
  --strict-mcp-config
  --permission-mode bypassPermissions
  --append-system-prompt '<§5.3>'
  ( --session-id <새 UUIDv4>   ← 이 thread의 첫 턴
  | --resume <기억한 id> )     ← 후속 턴
```
- 도구 허용 목록을 주지 않는다(파일·셸 도구를 작업 폴더에서 그대로 쓰게 하려는 원본의 선택. 보안은 §11).
- 환경: 백엔드 프로세스 환경 전체 + `TERM=xterm-256color`, `COLORTERM=truecolor`(없을 때만).
- 프로세스는 자기 프로세스 그룹으로 띄우고, stderr는 계속 비워 둔다(버퍼가 차서 멈추지 않게).
- 입력: stdin에 사용자 메시지를 JSON 한 줄로 쓴다 — `{"type":"user","message":{"role":"user","content":[{"type":"text","text":"…"}]}}`.
- 출력(stdout JSON 줄) 해석:
  - `type=assistant` 안의 `text` 블록 → `token`; `tool_use` 블록 → `tool_start{tool_call_id, name, args}`. 이름에서 `mcp__<서버>__` 접두를 떼고 표시. CLI 내부 도구 `ToolSearch`, `TodoWrite`는 숨긴다. `AskUserQuestion`이면 `ask_user{tool_call_id, questions}`.
  - `type=user` 안의 `tool_result` → 우리가 보고한 호출에 한해 `tool_result{tool_call_id, content(텍스트로 평탄화)}`.
  - `type=result` → `is_error`면 `error{message}`(단 우리가 일으킨 중단의 결과는 무시), 아니면 최종 텍스트로 기억. 보낸 메시지 수만큼 결과를 받았고 대기 중인 끼어들기가 없으면 stdin을 닫는다.
- 끼어들기(steering): 실행 중 새 메시지가 오면 → `steered{text}` 이벤트를 내고 → stdin에 `{"type":"control_request","request_id":"steer-<8hex>","request":{"subtype":"interrupt"}}` → 이어서 사용자 메시지 한 줄 → 기다릴 결과 수 +1.
- 끝: 프로세스 종료 대기(최대 1800초). 시간 초과 → `error "agent turn exceeded 1800s"`; 비정상 종료 → `error "<cli id> exited with <코드>: <stderr 앞 2000자>"`; 정상 → `final{text}`. 어떤 경우든 프로세스 그룹 정리.
- 새 세션 id를 만들면 thread별로 메모리에 기억한다(재시작하면 잊는다). 고정 파생 id를 쓰지 않는 이유: 재시작 뒤 같은 id로 `--session-id`를 주면 CLI가 거부한다.

### 5.5 Codex 실행
```
codex exec [resume] --json --skip-git-repo-check
  --output-last-message <작업 폴더>/.ontology-studio-last-message.txt
  --dangerously-bypass-approvals-and-sandbox
  -c 'mcp_servers.ontology_studio.url="http://127.0.0.1:<백엔드 포트>/mcp/agent-bridge/<모드>/"'
  -c 'mcp_servers.ontology_studio.tool_timeout_sec=180'
  [<이전 세션 id>]   ← resume일 때만
  '<스킬 본문+환경 블록>\n\n---\n\n<사용자 메시지>'
```
- stdin은 즉시 닫는다. 작업 디렉터리는 프로세스 cwd로 준다.
- 출력 JSON 줄에서 `session_id`/`conversation_id`/`thread_id`(최상위·`msg`·`item`·`thread` 안)를 찾아 세션 id로 기억.
- 이벤트 해석(최선): `item.completed`의 `agent_message` 계열 → `token`(started는 무시), `mcp_tool_call`/`command_execution`/`function_call` → started=`tool_start`, completed=`tool_result`(error.message 우선), 구형 `mcp_tool_call_begin`/`_end`/`function_call_output`, `error` → `error`.
- 최종 답은 `--output-last-message` 파일에서 읽는다.
- 끼어들기 불가(요청 시 "전달 안 됨" 반환).

### 5.6 백엔드 HTTP API (대화)
| 메서드 | 경로 | 입력 | 출력 |
|---|---|---|---|
| GET | `/api/stream` | query `prompt`(필수), `session_id`(기본 `default`), `mode`(`build`·`answer`·`act`, 기본 build), `build_context`(JSON 문자열, build만) | `text/event-stream`, 헤더 `Cache-Control: no-cache, no-store, must-revalidate, no-transform`, `X-Accel-Buffering: no`. prompt가 비면 JSON `{"error":"prompt is required"}` |
| POST | `/api/agent/steer?session_id=&mode=` | body `{"text": "..."}` | `{"delivered": true|false, "reason": ""}`; 빈 text면 `{"delivered": false, "reason": "empty"}` |
| GET | `/api/agent/running?session_id=&mode=` | | `{"running": bool}` |
| POST | `/api/session/reset?session_id=` | | `{"status":"ok"}` — 그 세션의 대화 기억(체크포인트·CLI 세션 id·준비 표시)과 작업 파일 삭제 |
세션 목록·메시지 저장 API는 A2·M1·M2 문서 범위.

### 5.7 SSE 이벤트 계약
형식: `event: <이름>\ndata: <JSON>\n\n`.
| 이벤트 | data | 비고 |
|---|---|---|
| `status` | `{message}` | 시작 시 1회: build 첫 턴 `온톨로지 구축 에이전트를 시작합니다... (<n>개 Golden Question)`, build 이어짐 `이전 대화를 이어서 진행합니다...`, 그 밖 `<모드 라벨> 모드 실행 시작...` (act=`질의·액션`, answer=`질문 응답`) |
| `token` | `{text, node:"agent"}` | 누적 텍스트와 겹치는 부분은 뺀 증분 |
| `tool_start` | `{tool_call_id, name, node, args, description}` | description = 사람이 읽는 한 줄 |
| `tool_result` | `{tool_call_id, name, content(최대 3000자), node}` | |
| `steered` | `{text}` | |
| `ask_user` | `{tool_call_id, questions}` | |
| `error_event` | `{message}` | |
| 부수 이벤트 | `todos{items}`, `ref_file{name,path}`, `neo4j_update{tool}`, `datasource_update{…}`, `schema_created{schema_name}`, `traversed_nodes{tool,node_ids}`, `node_update{node}`, `skill_loaded{name}` | 도구 이름에 따라 냄. 의미는 M1·M2 |
| `done` | `{message:"완료!", files, text, build_report}` | 마지막. build 성공이면 바로 앞에 4단계 완료 todos(스키마 설계 / 소스 파싱 + 적재 / 검증 / 검수) |

### 5.8 대화 이어짐
- 내장 에이전트: 대화 기록을 SQLite 체크포인트로 저장. build·answer 모드는 기록이 있으면 새 하위 thread를 열고 "이어서" 프롬프트(사명·이전 요약·산출물)를 보낸다. act는 같은 thread를 유지(앞 턴의 계획 id를 이어받아야 하므로).
- CLI 에이전트: 체크포인트를 쓰지 않는다 → 매 턴 "첫 턴"으로 취급되어 build는 매번 전체 구축 프롬프트를 다시 만들고, CLI 쪽은 `--resume`으로 자기 기록을 잇는다(추정, 실행 기록 필요).
- 초기화·삭제 시 CLI 세션 id 기억과 스킬 준비 표시를 함께 지운다(안 지우면 CLI가 옛 대화를 이어 "이미 했다"고 답함).

## 6. MCP 서버

### 6.1 에이전트 브리지 (백엔드 내장, 에이전트 전용)
- 백엔드 HTTP 서버에 모드마다 MCP(streamable HTTP) 엔드포인트를 붙인다: `/mcp/agent-bridge/{build,answer,answer_nods,brief_draft,dashboard,act}/`. 서버 이름 `ontology-studio-agent-bridge-<모드>`.
- 각 엔드포인트의 도구는 **내장 에이전트가 그 모드에서 쥐는 것과 정확히 같은 목록**이어야 한다(모드별 권한을 넓히지 않는 것이 원칙).
- 도구 이름 목록(의미·인자는 해당 메뉴 문서):
  - build: `neo4j_cypher`, `schema_create_class`, `schema_create_relationship_type`, `schema_get`, `schema_group_create`, `schema_group_list`, `entity_create`, `entity_search`, `relationship_create`, `batch_ingest`, `graph_stats`, `execute`, `sandbox_ls`, `sandbox_read`, `sandbox_write`, `datasource_list`, `datasource_describe`, `datasource_query_preview`, `datasource_view_create`, `datasource_view_drop`, `class_bind_datasource`, `class_unbind_datasource`, `class_binding_get`, `schema_ontology_generate`, `build_strategy_recommend`, `reverse_bind_preview`, `reverse_bind_apply`, `causal_discover`, `behavior_create`, `behavior_delete`, `behavior_list`, `behavior_invoke`, `action_create`, `action_list`, `action_delete`, `system_list`, `system_operations`, `system_query`, `schema_publish`, `action_dry_run`, `entity_fetch`, `extract_triples`, `table_ingest`, `quality_checkup`, `quality_report` (인과 가설을 관계로 승격하는 도구, 검수 결정·재처리 도구는 **일부러 없음**)
  - brief_draft: `datasource_list`, `datasource_describe`, `schema_get`, `graph_stats`, `sandbox_ls`, `sandbox_read`
  - answer(기본, 표준 MCP 경유): `sandbox_read` + 검색 MCP 서버 도구의 대리 호출 `ontology_graph_schema`(리소스 `graph://schema`를 도구로 감쌈), `ontology_list_schemas`, `ontology_get_schema`, `ontology_list_entities`, `ontology_resolve_entity`, `ontology_graph_cypher`, `ontology_get_datasource_schema`, `ontology_query_datasource_sql` — 기동 시 검색 서버에 실제 등록된 도구만 남긴다(닿지 못하면 전부 두고 호출 시 오류를 JSON으로 반환). `ontology_query`는 자기 자신을 부르게 되므로 제외.
  - answer(`ANSWER_TOOLS_VIA_MCP=false`): `schema_get`, `entity_search`, `neo4j_cypher_readonly`, `graph_stats`, `vector_search`, `sandbox_read`, `behavior_list`, `behavior_invoke`, `entity_fetch`, `datasource_sql_query`
  - answer_nods: answer에서 실데이터 도구 제외
  - act: answer(실데이터 포함) + `query_system`, `list_actions`, `plan_action`, `plan_action_ids`, `get_plan`, `execute_plan`, `get_run`, `list_runs`, `compensate_run` — **승인 도구 없음**(승인은 사람이 화면에서)
  - dashboard: `dashboard_get`, `widget_recommend`, `dashboard_patch`
- 대리 호출 도구의 실패는 예외 대신 `{"error": "...", "hint": "..."}` JSON 문자열로 돌려준다(에이전트가 사용자에게 이유를 옮길 수 있게). 모든 도구 반환은 JSON 문자열.

### 6.2 검색 MCP 서버 (별도 프로세스, 외부 클라이언트용)
- 전송: streamable HTTP, `127.0.0.1:<mcp 포트>/mcp`. 로컬 웹 오리진의 `/mcp…`도 이 서버로 리버스 프록시. 서버 이름 `ontology-studio-search`. (설정으로 stdio·SSE도 가능.)
- DNS 리바인딩 보호: 기본 켜짐(127.0.0.1·localhost·[::1] 호스트만). `MCP_EXTRA_ALLOWED_HOSTS`(쉼표 목록)로 허용 호스트 추가.
- 인증 없음.
- 항상 있는 것:
  - 도구 `ontology_query(question, schema_hint="")` — 답변 에이전트를 한 번 돌려 `{answer, sources[{node id, labels, name, excerpt…}], meta{session_id, referenced_node_count, streamed:true, note?}}` 반환. 진행(상태·도구 시작/결과·참고 노드 수·답변 조각·경고)을 MCP 로그/진행 알림으로 흘린다. 내부적으로 임시 세션(`mcp-<12hex>`)을 쓰고 끝나면 지운다. 실데이터 확장이 켜져 있으면 answer, 꺼져 있으면 answer_nods 모드. **이 도구는 내부에서 §5의 CLI 에이전트를 띄운다.**
  - `ontology_list_entities(class_name, schema_name, criteria, semantic_query, limit)` — 선택자 하나로 엔티티 묶음
  - `ontology_list_schemas()` — 스키마 그룹·클래스·엔티티 수
  - `ontology_get_schema(schema_name="")` — 통합 스키마 또는 그룹 하나
  - 리소스 `graph://schema`(JSON) — 발행된 온톨로지 지도(클래스·관계·데이터소스 연결 여부, 컬럼 제외)
  - 프롬프트 1개 — "그래프+데이터소스 2단계 질의" 지시문(답변 스킬 본문)
- `MCP_ALLOW_DATASOURCE_EXPANSION`이 참일 때만 추가(앱 기본 참):
  - `ontology_resolve_entity(text, class_name="", limit=5, context="")` — 이름→실제 인스턴스·키, `resolution.status` ∈ resolved/ambiguous/no_match
  - `ontology_graph_cypher(query, params="{}", as_of="", known_at="")` — 읽기 전용 Cypher(쓰기 절·CALL·LOAD CSV 거부, 데이터 패브릭 카탈로그·발행 레지스트리 라벨 거부), 결과 노드에 데이터소스 참조 표시, 시점 조회
  - `ontology_get_datasource_schema(class_name, schema_name="")` — 클래스 하나의 컬럼·키·기본 조건·behavior(SQL 템플릿 비공개), 동명 클래스는 ambiguous
  - `ontology_query_datasource_sql(sql, limit=0)` — 발행 클래스에 바인딩된 테이블만, 단일 SELECT/WITH, 결과 행은 에이전트용으로 30행까지
- 백엔드가 이 서버에 붙는 클라이언트 설정: 접두사별 환경 변수 `<P>_TRANSPORT`(http|stdio, 기본 http), `<P>_URL`(없으면 `http://127.0.0.1:<MCP_PORT>`; 무엇을 주든 `…/mcp`로 정규화), `<P>_COMMAND`(stdio용), `<P>_TIMEOUT`(초, 60), `<P>_SAMPLE_LIMIT`(50). 접두사: 답변 `ANSWER_MCP`, 대시보드 `BOARD_MCP`.

## 7. 지시문(스킬) — 의도와 구조 요약

스킬 = 폴더 하나(`SKILL.md` + 참조 파일). `SKILL.md` 앞에 YAML frontmatter(`name` = 폴더 이름, 소문자·숫자·하이픈 64자 이내; `description` 1024자 이내; `version` 필수; 그 밖 메타 허용). 본문이 시스템 프롬프트가 된다. 같은 폴더를 (1) 런타임 지시문, (2) 사용자가 자기 Claude Code에 복사하는 스킬, (3) 플러그인 배포에 쓴다. 배포용 메타 파일(`.mcp.json`, `.claude-plugin/`)은 런타임 복사에서 뺀다. 형식 위반은 조용히 건너뛰지 않고 오류로 낸다.

| 스킬 | 의도 | 본문 구조(요약) |
|---|---|---|
| 구축 | 업로드 문서·데이터소스·등록 시스템에서 스키마를 설계하고 그래프를 채우고 검증 | 언제 쓰나 / 도구가 없으면 시작하지 말 것 / 권한 경계(쓰기 가능, 전역 삭제 금지, 개인정보 컬럼) / 입력 점검(라벨 블록: 작업 요청·구축 의도·골든 퀘스천·소스·전략·대상 스키마·피드백·골든 커맨드·연결 시스템; 빠진 것만 최대 2회 묻기, 골든 퀘스천 문장 고치지 말 것) / 작업 경로(환경 블록) / 4단계 흐름: 1 스키마 설계(전략 추천 먼저) → 2 소스별 파싱·적재(가상 클래스는 적재 금지) → 2.5 골든 커맨드→액션 정의 → 3 실제 실행으로 검증(최대 3회 반복) → 4 품질 검수 안내(결정은 사람) / 스키마 그룹 규칙 / 핵심 도구 / 핵심 규칙(클래스는 사물·질문은 behavior, 관계 0개면 미완성 등) / 완료 기준(마지막에 구축 리포트 JSON 블록). 상세는 참조 파일 8개로 미룸 |
| 브리프 초안 | 고른 소스로 답할 수 있는 구축 의도·골든 퀘스천 3~5개 초안 제시 | 지위(사용자가 고칠 재료) / 권한(읽기 전용, 임의 SQL 없음) / 입력 / 흐름(소스를 실제로 보기 → 의도 한 문단 → 질문 3~5개) / 고정 출력 형식 / 규칙 |
| 답변(MCP 경유, 기본) | 그래프 토폴로지 탐색 + 데이터소스 집계를 결합해 근거와 함께 답 | 언제 / 도구 없으면 답하지 말 것 / 권한(조회 전용) / 흐름: 지도 읽기 → 이름을 키로 해석 → 그래프 탐색 → 필요한 클래스 하나의 스키마만 받기 → DB가 집계하게 SQL / 작업 경로 / 핵심 규칙 / 완료 기준. 참조 파일 1개 |
| 답변(내장 도구용) | 같은 목적, 내장 도구 이름 기준 | 같은 골격, 검색 전략 참조 파일 1개 |
| 액션 | 의도를 키네틱 액션 계획으로 옮기고, 사람 승인·명시적 확인 뒤에만 실행, 취소 시 역순 보상 | 언제 / 도구 없으면 실행 안 함 / 절대 규칙(승인 우회 금지·확인 없이 실행 금지) / 8단계 흐름(의도 → 액션 고르기 → 조건을 구조화 필터로 → 계획 → 표로 보여 주기 → 분기 → 실행 → 결과 표) / 취소(보상) 5단계 / 완료 기준 |
| 질의·액션 합본 | act 모드 전용 | 머리말(한국어, 질문은 1부·변경 요청은 2부·취소는 2부의 보상·섞인 요청은 1부로 조회 후 2부, 2부 규칙이 항상 우선) + `# 1부 — 질문 답변` + 답변 본문 + `# 2부 — 액션 실행` + 액션 본문. 참조 파일은 두 스킬 것을 합침 |
| 대시보드 편집·구성 | 발행 온톨로지로 대시보드를 만들거나 대화로 고침 | 언제 / 도구 전제 / 권한 / 위젯 종류는 추천 도구에 맡김 / 현재 상태 먼저 보기 → 항상 dry-run 패치 먼저 / 하지 말 것 (M5) |
| 트리플 추출 | 문서 청크 하나에서 스키마가 허용하는 사실 후보를 원문 인용과 함께 JSON으로 | 입력 값 블록 / 규칙(허용 관계 이름 그대로, 모든 항목에 글자 그대로 인용, 지시어를 이름으로 쓰지 않기 등) / JSON 출력 (M6) |

내장 에이전트는 스킬 폴더를 샌드박스 작업 폴더의 `.skills/<이름>/`에 복사해(내용이 같으면 건너뜀) 참조 파일을 읽을 수 있게 하고, 환경 블록의 스킬 폴더를 그 경로로 준다.

## 8. 내장 에이전트 (deepagents)
- 모델: build 모드는 `MAJOR_MODEL`, 나머지는 `MINOR_MODEL`. 값은 `provider:model` 또는 `model`(접두 없으면 openai). 기본값 `openai:gpt-5.4-2026-03-05` / `gpt-5.4-mini-2026-03-17`. 추론 강도 `MAJOR_MODEL_REASONING_EFFORT`·`MINOR_MODEL_REASONING_EFFORT`(기본 medium, `none`이면 생략). 온도 0. `OPENAI_BASE_URL`이 있으면 그 주소, 없고 GPT-5 계열이면 OpenAI Responses API.
- 도구 사용 루프 + 대화 기록 압축(기본 상한 토큰 `AGENT_HISTORY_MAX_TOKENS`=48000) + 모델이 텍스트로 낸 원시 도구 호출을 파싱해 실행하는 보정(최대 10회).
- 샌드박스: 호스트 로컬 모드(격리 없음). 논리 경로 `/workspace/uploads`, `/workspace/output`을 실제 작업 폴더로 바꿔 `bash -lc`로 실행, 120초 제한, 출력 3000자. 파일 읽기 기본 200줄·3000자.
- 백엔드 기동 시 샌드박스 확인 실패면 기동 실패, build·answer 에이전트를 미리 만든다.

## 9. 셸의 단발 스크립트 실행
- 셸은 Studio와 **같은 인터프리터·같은 환경 변수(§M8의 앱 고정값 포함)·같은 세션 DB**로 파이썬 스크립트를 띄울 수 있어야 한다. 작업 디렉터리 = 사용자 데이터 폴더.
- 완료형: stdout을 결과로, 0이 아니면 stderr 마지막 3줄을 ` | `로 이은 오류. stderr 마지막 20줄은 셸 로그에 남김. 출력 상한 16MB, 제한 300초, 필요하면 stdin으로 입력 전달.
- 스트리밍형: 자식 프로세스를 넘겨 호출자가 stdout을 읽게 한다.
- 쓰임 3가지:
  1. **단발 질의**(포털 자연어→Cypher, M4): stdin `{"system","user"}` → 도구 없이 한 번 묻고 텍스트 답. Claude: `claude -p '<system>\n\n---\n\n<user>' --output-format text --allowed-tools ""`; Codex: `codex exec --skip-git-repo-check '<prompt>'`. 빈 임시 폴더에서 실행, 180초. 종료 코드 3=CLI 없음, 4=시간 초과, 5=CLI 실패(메시지는 stderr). 내장 에이전트가 선택돼 있으면 호출자(포털 기능)가 "CLI 에이전트로 동작합니다. 메뉴 「런타임 › 에이전트」에서 고르세요." 오류를 낸다.
  2. **코드 앱 한 턴**(M5): stdin `{"prompt","cwd","session_id","resume"}`. Claude: `claude -p '<prompt>' --output-format stream-json --verbose --allowed-tools Read,Write,Edit,MultiEdit,Glob,Grep,Bash(curl:*),Bash(node --check:*) --permission-mode acceptEdits --setting-sources project --strict-mcp-config` + 첫 턴 `--session-id <앱이 정한 uuid>` / 이후 `--resume <같은 uuid>`. Codex: `codex exec --skip-git-repo-check --full-auto -C <앱 폴더> '<prompt>'`(세션 안 이음). 20분 제한. stdout에 JSON 줄: 시작 `{"kind":"token","text":"","agent":<id>}`, `token{text}`, `tool_start{tool_call_id,name,args}`, `tool_result{tool_call_id,name,content(600자),is_error}`, `error{message}`, `usage{duration_ms,turns,cost_usd}`, 마지막 `final{text,exit_code}`.
  3. **첫 실행 예제 온톨로지 생성**(A2/M1).
- 대시보드(M5)도 같은 CLI를 쓴다: 단발 JSON 응답(Claude는 도구 없음, 180초), 스트리밍 편집(Claude는 dashboard 브리지만 연결하고 그 세 도구만 허용). 내장 에이전트면 OpenAI 채팅 API의 JSON 모드. CLI가 실패하면 API 키 경로로 한 번 더 시도하고, 그것도 안 되면 결정적(규칙 기반) 순서로 채운다.

## 10. 프로세스 수명
- Studio 백엔드와 검색 MCP 서버는 셸이 함께 시작·정지한다. 시작 대기: 백엔드 `GET /openapi.json` 성공, MCP 포트 TCP 연결(각 120초).
- 에이전트 CLI는 턴을 시작한 요청에 속한다. 턴이 어떻게 끝나든(정상·예외·클라이언트 끊김) 프로세스 그룹을 SIGTERM → 유예 → SIGKILL. 백엔드 종료 시 남은 것을 모두 정리하고 개수를 로그.
- 코드 앱 턴은 셸이 자식 프로세스를 직접 kill(앱 종료 시 전부).

## 11. 보안 설계 고려 (새 구현에서 결정할 것)
원본 동작을 그대로 재현하면 아래 위험도 재현된다. 비교 테스트는 원본 계약 기준으로 하되, 구현에서 완화 옵션을 두는 것을 권한다.
1. **권한 우회 실행**: 구축·질의의 CLI 턴이 Claude Code `bypassPermissions`, Codex `--dangerously-bypass-approvals-and-sandbox`로 돈다. 작업 폴더가 cwd일 뿐 파일 시스템 제한이 없다. → 옵션: 허용 도구 목록 + 작업 폴더 밖 쓰기 금지(예: Claude `acceptEdits` + `--add-dir`, Codex `workspace-write` 샌드박스), 기본값은 원본과 같게 둘지 결정 필요.
2. **비밀 상속**: CLI 프로세스가 백엔드 환경 전체를 물려받는다 — 그래프/PostgreSQL 슈퍼유저 비밀번호, 액션 실행기 토큰, OpenAI 키 등. 권한 우회와 합쳐지면 에이전트 셸이 DB에 직접 붙을 수 있다. → 옵션: CLI에는 필요한 변수만 화이트리스트로 넘김.
3. **사용자 CLI 설정 상속**: Claude는 MCP만 엄격(`--strict-mcp-config`)하고 사용자 설정·훅·전역 지시문은 그대로 읽힌다. Codex는 사용자 전역 설정의 다른 MCP 서버도 그대로 붙는다(추정). → 옵션: 코드 앱처럼 설정 출처를 프로젝트로 한정.
4. **실데이터 확장 기본 켬**: 검색 MCP 서버(인증 없음, 루프백)는 앱에서 실데이터 도구를 기본으로 켠다. 같은 PC의 다른 프로세스·AI 클라이언트가 원천 DB 행을 읽을 수 있다. 원본 백엔드 자체 기본값은 꺼짐이다. 설정으로 끌 수 있으나 그러면 대시보드 자동 구성이 동작하지 않는다(M8 설명 문구).
5. **에이전트 브리지 인증 없음**: 백엔드의 `/mcp/agent-bridge/build/`는 쓰기 도구(그래프 변경·셸 실행 `execute`)를 인증 없이 노출한다. 루프백 바인딩과 MCP SDK의 DNS 리바인딩 보호(Host/Origin 검사)에 기대고 있다. 백엔드 CORS는 모든 오리진 허용. → 옵션: 턴마다 발급하는 일회용 토큰을 MCP 설정의 헤더로 넘김.
6. **로컬 샌드박스 무격리**: 내장 에이전트의 `execute`도 호스트 사용자 권한으로 `bash -lc` 실행.

## 12. 데이터 모델
- 에이전트 결정 결과: `{backend: "cliagents"|"deepagents", agentId: "claude-code"|"codex", label, ready: bool, note: string|null}` — 셸 정보 API(M8)로 노출.
- CLI 세션 기억: thread(`<세션>:<모드>`) → CLI 세션 id. 메모리만.
- 작업 폴더 트리: `<사용자 데이터>/sandbox/sessions/<세션>/{uploads/, output/, .claude/skills/…|.agents/skills/…, .ontology-studio-last-message.txt(Codex)}`. 내장 에이전트는 `.skills/<이름>/`.
- 대화 기록(내장): `<사용자 데이터>/sessions.db`(SQLite, 체크포인트·메시지) — A2 범위.

## 13. 다른 기능과의 의존
- A1: 포트 할당(백엔드·MCP·웹), 프로세스 시작·정지, 로컬 웹 오리진의 `/api`·`/mcp` 프록시, 트레이.
- A2: 그래프 접속 정보(셸이 주입), 세션 DB.
- M8: studio.env 읽기·쓰기, 홈 상태 표시, 메뉴.
- M1·M2·M5·M4·M6: 모드·스킬·도구를 소비.
- 키네틱 실행기(M7): act 모드 도구가 그 MCP·HTTP를 부름.

## 14. 오류·예외
| 상황 | 동작 |
|---|---|
| CLI 미설치(요청은 cliagents) | 셸이 내장으로 내리고 안내 문구(§4.3). 백엔드에 cliagents가 강제되면 기동 실패(설치 힌트 포함 오류) |
| 지원 안 하는 CLI id가 백엔드에 들어옴 | 에이전트 생성 실패: "cannot be driven headlessly (supported: claude-code, codex)" |
| 턴 1800초 초과 | `error_event` "agent turn exceeded 1800s" |
| CLI 비정상 종료 | `error_event` "<id> exited with <코드>: <stderr>" |
| CLI의 result가 오류 | `error_event`(메시지 = result 텍스트 또는 "agent run failed") |
| 검색 MCP 서버에 못 닿음(답변 도구) | 도구 결과 JSON `{"error":"온톨로지 …","hint":"ontology_mcp 서버(기본 8100)가 떠 있는지 …"}` |
| 실데이터 확장 꺼짐에서 확장 도구 호출 | `{"error":"데이터소스 확장이 비활성화되어 있습니다 (MCP_ALLOW_DATASOURCE_EXPANSION=false).","disabled":true}` |
| 읽기 전용 Cypher에 쓰기 절 | `{"error":"읽기 전용 조회만 허용됩니다. …"}` |
| 전환 중 실패 | 셸 마지막 오류에 기록, 메뉴 재구성 |
| 단발 스크립트 실패 | 종료 코드 3/4/5, 호출자에 stderr 마지막 줄들 |

## 15. 원본과 비교할 테스트 항목 (구조·계약, ADR-0010)
1. 결정 표(§4.3)의 다섯 경우마다 셸 정보 API 응답 `agent`와 홈 표시 문구가 같다.
2. 메뉴 전환 후 studio.env diff(키·값·줄 위치), 재시작되는 프로세스 집합(백엔드·MCP만)이 같다.
3. Claude 턴의 명령줄 플래그 집합이 같다(시스템 프롬프트 내용 제외). 첫 턴 `--session-id`, 후속 `--resume` 같은 id.
4. Codex 턴의 명령줄 플래그·`-c` 키가 같다.
5. CLI 작업 폴더 구조와 스킬 파일 위치가 같다.
6. 각 브리지 엔드포인트의 `tools/list` 이름 집합이 같다(모드 6개).
7. 검색 MCP 서버의 tools/resources/prompts 목록이 확장 켬·끔에서 각각 같다.
8. `/api/stream` 이벤트 이름 순서 패턴(`status` → … → `done`)과 각 data 필드 키가 같다.
9. `/api/agent/steer` 응답: Claude 실행 중 true, 실행 없음·Codex·내장에서 false, 빈 text면 reason `empty`.
10. `/api/session/reset` 뒤 다음 턴이 새 CLI 세션으로 시작한다.
11. 단발 스크립트: stdin/stdout 형식, 종료 코드 3/4/5 의미, 코드 앱 JSON 줄 `kind` 어휘가 같다.
12. 앱 종료 후 CLI 프로세스가 남지 않는다.

## 16. 모르는 점 (4단계 실행 기록에서 확인)
- 내장 에이전트 선택 + 키 없음일 때 백엔드가 정상 기동하는가(빈 키로 모델 객체 생성이 실패하는지). 홈은 "사용할 수 없음"이지만 Studio 탭이 열리는지.
- CLI 경로에서 build 후속 턴이 정말 매번 전체 구축 프롬프트를 보내는지(체크포인트 미사용 추정).
- 백엔드 기동 시 검색 MCP 서버가 아직 안 떠 있으면 answer 브리지 도구 목록이 "전부"로 고정되는지, 그 결과 확장 끔 상태에서 존재하지 않는 도구가 노출되는지.
- Codex가 사용자 전역 `config.toml`의 MCP 서버를 함께 붙이는지, `exec resume`가 위 옵션 집합을 실제로 받는지.
- Claude Code 턴에 사용자 `~/.claude` 설정(훅·플러그인·전역 CLAUDE.md)이 적용되는지.
- `AskUserQuestion`이 헤드리스에서 정말 안 나오는지(원본 주석은 "실측상 안 나옴").
- steering 시 interrupt 결과가 오류 result로 오는 순서(원본 가정)가 현재 Claude Code 버전에서도 같은지.
- 웹 오리진 프록시를 거친 `/mcp` 요청의 Host 헤더가 리바인딩 보호를 통과하는지.
- `ontology_query`(외부 MCP)가 CLI 에이전트를 띄울 때 실제 체인(검색 서버 → CLI → 백엔드 브리지 → 검색 서버)의 지연과 성공 여부.

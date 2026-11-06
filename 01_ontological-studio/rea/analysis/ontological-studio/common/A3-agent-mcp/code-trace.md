# A3 에이전트·MCP — 코드 추적 (원본 근거, 구현 세션에 넘기지 않음)

- 기준: 배포본 0.1.1. 경로 약어
  - `E/` = `extracted-app-asar/src/`
  - `R/` = `shared/app/resources/`
  - `A/` = `shared/app/runtime/studio/app/` (`A/backend/src/…`, `A/cliagents/…`, `A/skills/…`)
  - `PY/` = `shared/app/runtime/studio/python/lib/python3.12/site-packages/`
- 표기: 관찰(코드 확인) / 추정 / 모름

## 0. 전체 구조 (관찰)

```
Electron 메인 ──spawn──▶ [mcp]     python -m backend.src.modules.ontology_mcp   (127.0.0.1:<mcp>, streamable HTTP /mcp)
               └─spawn──▶ [backend] python -m uvicorn backend.src.host.app:app (127.0.0.1:<backend>)
                                     ├─ /api/stream (SSE) …  agent_session
                                     ├─ /mcp/agent-bridge/{build,answer,answer_nods,brief_draft,dashboard,act}/  (FastMCP mount)
                                     └─ 턴마다 CLI 자식 프로세스: claude / codex  ──HTTP MCP──▶ /mcp/agent-bridge/<mode>/
                                                                                     (answer·act 의 읽기 도구는 다시 MCP 클라이언트로 [mcp] 를 부름)
               └─execFile/spawn ─▶ python R/agent_turn.py · R/code_app_turn.py · R/sample/seed_ontology.py (Studio 와 같은 env)
```

## 1. 에이전트 선택 (셸)

| 항목 | 위치 | 내용 |
|---|---|---|
| CLI 이름 표 | `E/main/services.js:50-51` | `claude-code→claude`, `codex→codex`, 표시 이름 |
| PATH 보충 | `E/main/services.js:58-68` | Finder 실행 시 PATH가 짧음 → `/opt/homebrew/bin`, `/usr/local/bin`, `~/.local/bin`, `~/.bun/bin`, `~/.deno/bin`, `~/.volta/bin`, `~/.npm-global/bin`, `~/.claude/local` 추가 (Windows: `%APPDATA%\npm`, `~/.local/bin`, `~/scoop/shims`) |
| which | `E/main/services.js:71-80` | 실행 권한 있는 파일 탐색 (Windows는 PATHEXT) |
| 감지 | `E/main/services.js:82-84` | `detectAgentClis()` → `{claude-code: path|null, codex: path|null}` |
| 결정 | `E/main/services.js:91-104` | `resolveAgent(user)` — 아래 표 |
| 사용자 env 읽기 | `E/main/services.js:34-42` | 정규식 `^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$`, 빈 값은 **무시**, 양끝 따옴표 하나 제거, 주석·`export` 미지원 |

`resolveAgent` 결과 (관찰):

| 요청 `AGENT_BACKEND` | CLI 존재 | `OPENAI_API_KEY`/`OPENAI_BASE_URL` | 결과 backend | label | ready | note |
|---|---|---|---|---|---|---|
| (없음)/`cliagents` | 있음 | – | `cliagents` | Claude Code / Codex | true | null |
| `cliagents` | 없음 | 있음 | `deepagents` | 내장 에이전트 | true | "`claude` 를 찾지 못해 내장 에이전트로 실행합니다. …" |
| `cliagents` | 없음 | 없음 | `deepagents` | 내장 에이전트 | false | "`claude` 를 찾지 못했고 LLM 키도 없습니다. …" |
| 그 밖의 값 | – | 있음 | `deepagents` | 내장 에이전트 | true | null |
| 그 밖의 값 | – | 없음 | `deepagents` | 내장 에이전트 | false | "AGENT_BACKEND=deepagents 인데 LLM 접속 정보…" |

- `EXTERNAL_AGENT_ID`는 정확히 `codex`일 때만 codex, 나머지는 모두 `claude-code` (`services.js:93`).
- 결정 시점: `startStudio`(부팅·전환), `runStudioScript`/`spawnStudioScript`(매 호출마다 다시 계산) (`services.js:168,190,203`).
- 주석: cliagents인데 CLI가 없으면 백엔드 `warm_up_agent`가 `AgentNotInstalledError`로 죽기 때문에 셸에서 미리 내린다 (`services.js:86-90`).

## 2. Studio 프로세스 환경 (셸 → 백엔드·MCP)

`studioEnv()` `E/main/services.js:117-159` — 순서: `baseEnv()`(process.env − PATH + `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`) → **사용자 studio.env 전체** → 앱 고정값(덮어씀).

앱 고정값(사용자가 못 바꿈): `PATH`(보충 경로), `NEO4J_URI/USER/PASSWORD/DATABASE`, `ONTOLOGICAL_ADMIN_DEV_URL`, `DATAFABRIC_BASE_URL`·`TEXT2SQL_BASE_URL`(=`http://127.0.0.1:<web>/fabric-bridge`), `AGENT_BACKEND`·`EXTERNAL_AGENT_ID`(결정 결과), `SANDBOX_BACKEND=local`, `LOCAL_SANDBOX_ROOT=<userData>/sandbox`, `SANDBOX_WORKDIR=/workspace`, `BACKEND_HOST=127.0.0.1`, `BACKEND_PORT`, `ANSWER_MCP_TRANSPORT=http`, `ANSWER_MCP_URL=http://127.0.0.1:<mcp>/mcp`, `BOARD_MCP_TRANSPORT/URL`(같은 값), `MAIN_LOG_PATH`, `DETAIL_LOG_DIR`, `SESSION_DB_PATH=<userData>/sessions.db`, `PYTHONPATH`, `PYTHONUNBUFFERED`, `PYTHONDONTWRITEBYTECODE`, `PYTHON_DOTENV_DISABLED=1`.

사용자 값 우선, 없으면 앱 기본: `ONTOLOGICAL_ADMIN_PROD_URL`(기본 `http://127.0.0.1:9` = 막힌 주소), `ER_RERANK_URL`(같음), `ANSWER_TOOLS_VIA_MCP`(기본 `true`), `MCP_ALLOW_DATASOURCE_EXPANSION`(기본 `true` — 백엔드 자체 기본값은 false, `A/backend/src/shared/kernel/settings.py:200`).

키네틱: 사용자 `KINETIC_URL`이 **있으면** 앱 값 미주입(사용자 KINETIC_* 그대로), **없으면** 번들 kinetic 값(`KINETIC_URL`, `KINETIC_MCP_URL`, `KINETIC_STUDIO_TOKEN`, `KINETIC_AGENT_TOKEN`, `KINETIC_ROLE_CATALOG` — `E/main/kinetic.js:94-103`)이 사용자 값을 덮음. kinetic 시작 실패여도 kineticEnv는 이미 계산됨 (`E/main/index.js:164`).

MCP 프로세스에만 추가: `MCP_TRANSPORT=http`, `MCP_HOST=127.0.0.1`, `MCP_PORT` (`services.js:171-173`).

## 3. 프로세스 기동·재시작

| 동작 | 위치 |
|---|---|
| 기동 | `E/main/services.js:167-182` — `mcp`(cwd=userData) 먼저 spawn, `backend`(uvicorn, `--timeout-graceful-shutdown 3`), 대기: backend `GET /openapi.json` 120초, mcp TCP 120초 |
| 부팅 순서 내 위치 | `E/main/index.js:149-176` — kinetic과 병렬, `agent = await startStudio(...)`, `logAgent()` |
| 에이전트 로그 | `E/main/index.js:217-219` |
| 전환 | `E/main/index.js:226-251` `switchAgent(choice)`: `switching`/`phase!=='ready'`면 무시 → `updateUserEnv` (deepagents면 `AGENT_BACKEND`만, 아니면 `AGENT_BACKEND=cliagents`+`EXTERNAL_AGENT_ID`) → progress('studio') → backend·mcp stop(8초) → startStudio → studio 탭 reload + 셸 `load()` 실행 → 실패 시 `lastError` 기록 → `buildMenu()` |
| 메뉴 | `E/main/index.js:253-268` — 라디오 3개, 미설치 CLI는 `(설치 안 됨)`·비활성, 체크는 studio.env의 요청값 기준(실제 결정값 아님) |
| 종료 | `E/main/index.js:341-358` — codeapps.stopAll → backend·mcp·kinetic 등 stop |
| 백엔드 종료 시 CLI 정리 | `A/backend/src/host/app.py:24-45` lifespan finally `cliagents.shutdown_all()` |
| 프로세스 그룹 | `A/cliagents/processes.py:121-140,247-281` — `start_new_session`(POSIX), SIGTERM→SIGKILL, stderr 상시 드레인 |

## 4. 백엔드의 에이전트 전략 선택

| 항목 | 위치 |
|---|---|
| 설정 | `A/backend/src/shared/kernel/settings.py:157-201` (`AGENT_BACKEND` 기본 `deepagents` — 셸이 항상 주입하므로 실효 없음) |
| 선택 | `A/backend/src/modules/agent_session/service.py:1190-1217` `get_agent(mode)`: cliagents면 모드별 `CliAgentAdapter(mode)`, 아니면 LangChain `create_agent` 그래프 (build/brief_draft/answer_nods/act/answer) |
| 기동 시 준비 | `service.py:1262-1298` `warm_up_agent`: DB·체크포인터 setup, 샌드박스 확인(실패 시 raise → 백엔드 기동 실패), `get_agent("build")`, `get_agent("answer")` |
| 내장 모델 | `service.py:991-1033` — build=`MAJOR_MODEL`, 나머지=`MINOR_MODEL`, `temperature=0`, GPT-5 계열·base_url 없음이면 Responses API, `reasoning_effort` |
| 모델 이름 해석 | `A/backend/src/shared/kernel/model_profiles.py:33-66` — `provider:model`, 접두 없으면 openai |
| 기본 모델 | `settings.py:164-182` — MAJOR `openai:gpt-5.4-2026-03-05`, MINOR·OCR `gpt-5.4-mini-2026-03-17`, OCR 임베딩 `openai:text-embedding-3-small` |

## 5. CLI 에이전트 실행 (구축·질의·액션·브리프 초안)

파일: `A/backend/src/modules/agent_session/cliagents_backend.py`

| 항목 | 줄 | 내용 |
|---|---|---|
| MCP 서버 이름 | 36 | `ontology-studio` (Codex 키는 `ontology_studio`, 535) |
| 턴 제한 | 39 | 1800초 |
| AskUserQuestion | 49, 260-268 | `ask_user` 이벤트로 변환 (헤드리스에선 실측상 안 나옴 — 주석) |
| 도구 이름 정리 | 94-104 | `mcp__ontology-studio__x` → `x` |
| 숨기는 도구 | 138 | `ToolSearch`, `TodoWrite` |
| Claude Code argv | 208-234 | `-p --input-format stream-json --output-format stream-json --verbose --mcp-config {"mcpServers":{"ontology-studio":{"type":"http","url":…}}} --strict-mcp-config --permission-mode bypassPermissions --append-system-prompt <prompt>` + `--resume <id>` 또는 `--session-id <uuid4>` |
| 입력 | 186-192, 238 | stdin에 `{"type":"user","message":{"role":"user","content":[{"type":"text","text":…}]}}` 한 줄 |
| 출력 파싱 | 247-305 | `assistant`(text→token, tool_use→tool_start), `user`(tool_result, 보고한 call만), `result`(is_error→error / 최종 텍스트) |
| steering | 307-316, 335-347 | `control_request`(`subtype: interrupt`) 후 새 user 메시지 write, outstanding 카운트 |
| 종료 | 318-326 | stdin close → wait → `proc.close()` |
| Codex argv | 362-387 | `codex exec [resume] --json --skip-git-repo-check --output-last-message <ws>/.ontology-studio-last-message.txt --dangerously-bypass-approvals-and-sandbox -c mcp_servers.ontology_studio.url="…" -c mcp_servers.ontology_studio.tool_timeout_sec=180 [<session>] <system+"\n\n---\n\n"+prompt>`; stdin 즉시 close |
| Codex 이벤트 | 413-486 | `session_id`/`conversation_id`/`thread_id` 추출, `item.started/completed`(agent_message, mcp_tool_call, command_execution, function_call), 구형 `msg` 형식 |
| 종료 판정 | 489-514 | timeout→error, rc≠0→`"<agent> exited with <rc>: <stderr 2000자>"`, 성공→`final` |
| steer 가능 | 541 | claude-code만 |
| 모드→스킬 | 611-644 | build→`ontology-build`, brief_draft→`ontology-brief-draft`, act→(답변+액션 합본), 그 밖(answer/answer_nods/dashboard)→`answer_skill_name()` |
| 시스템 프롬프트 | 646-649 | 스킬 본문 + `[환경]` 블록(스킬 폴더·업로드·출력 = 호스트 실경로) |
| MCP URL | 651-657 | `http://<BACKEND_HOST>:<BACKEND_PORT>/mcp/agent-bridge/<mode>/` |
| 작업 폴더 | 659-689 | thread_id `<session>:<mode>` → session 부분으로 `<LOCAL_SANDBOX_ROOT>/sessions/<safe session>/`, `uploads/`·`output/` 생성 |
| 스킬 배치 | 691-720 | 스레드당 1회 `provider.emit()` → Claude `.claude/skills/<name>/SKILL.md`+references, Codex `.agents/skills/<name>/SKILL.md`(frontmatter 보정) |
| env | 743 | `provider.launch_env(os.environ)` = 백엔드 env 전체 + `TERM=xterm-256color`, `COLORTERM=truecolor` |
| CLI 세션 기억 | 600, 752-753 | `_cli_sessions[thread_id]` 메모리만 (재시작 시 소실) |
| 세션 잊기 | 817-833 | `forget_session` — clear_session에서 호출 |

세션 id 규칙 (`A/backend/src/modules/files/workspace.py:57-79`): 영숫자·`-`·`_`만, 64자, 비면 `_shared`.

CLI provider (`A/cliagents/`): `providers/claude_code.py:19-39`(executable `claude`, 설치 힌트 `npm install -g @anthropic-ai/claude-code`, `.mcp.json` 프로젝트 범위), `providers/codex.py:37-64`(executable `codex`, `.agents/skills`, MCP는 사용자 전역 `$CODEX_HOME/config.toml`), `registry.py:82-123`(resolve: 지정 id → 설치 확인, 미설치면 install hint 예외), `detection.py:46-54`(shutil.which + TTL 캐시).

## 6. 대화 API와 SSE

`A/backend/src/modules/agent_session/api.py`

| 메서드·경로 | 줄 | 요청 | 응답 |
|---|---|---|---|
| GET `/api/stream` | 31-50 | query `prompt`, `session_id`(기본 default), `mode`∈build/answer/act, `build_context`(JSON 문자열) | `text/event-stream`; prompt 없으면 `{"error":"prompt is required"}` |
| POST `/api/agent/steer` | 53-71 | query `session_id`, `mode`; body `{"text": …}` | `{"delivered": bool, "reason": ""|"empty"}` |
| GET `/api/agent/running` | 74-78 | `session_id`, `mode` | `{"running": bool}` (번들에서 호출 문자열 미발견) |
| POST `/api/session/reset` | 81-87 | `session_id` | `{"status":"ok"}` — 세션 기억 삭제 + 작업 파일 삭제 |
| GET/POST/DELETE/PATCH `/api/sessions…` | 94-127 | — | 세션 CRUD (A2/M1·M2 참고) |
| GET/PUT `/api/sessions/{id}/messages` | 134-155 | mode | 화면 메시지 상태 저장 |

SSE 생성 `service.py:1987-2527` `generate_sse`. CLI 경로 매핑 `service.py:2273-2339`.
이벤트 이름: `status`, `token{text,node}`, `tool_start{tool_call_id,name,node,args,description}`, `tool_result{tool_call_id,name,content(3000자),node}`, `steered{text}`, `ask_user{tool_call_id,questions}`, `error_event{message}`, 부수 효과 `todos`, `ref_file`, `neo4j_update`, `datasource_update`, `schema_created`, `traversed_nodes`(`service.py:1660-1735`), `node_update`, `skill_loaded`, 마지막 `done{message:"완료!",files,text,build_report}` (`service.py:2519-2527`). 구축 성공 시 `done` 앞에 완료 todos 4단계(`service.py:2504-2517`).
- 체크포인트 판정 `service.py:1243-1253`: CLI 경로는 체크포인터에 쓰지 않으므로 항상 "첫 턴"으로 판정 → 구축 모드는 매 턴 전체 구축 프롬프트를 보냄 (추정, `service.py:2013-2022`).
- 모드 표시 라벨: build "온톨로지 구축", act "질의·액션", 그 밖 "질문 응답" (`service.py:2060`).

## 7. agent-bridge MCP (백엔드 내장)

- 마운트 `A/backend/src/modules/agent_bridge_mcp/router.py:15-35` — 모드 6개, 경로 `/mcp/agent-bridge/<mode>`, FastMCP `streamable_http_path="/"`; lifespan에서 세션 매니저 실행(`router.py:38-50`, `host/app.py:32`).
- 서버 `A/backend/src/modules/agent_bridge_mcp/server.py:33-62` — 이름 `ontology-studio-agent-bridge-<mode>`, 도구 목록은 내장 에이전트와 같은 함수 객체.
- 모드별 도구 (`service.py`):
  - build `152-218` (45개): neo4j_cypher, schema_create_class, schema_create_relationship_type, schema_get, schema_group_create, schema_group_list, entity_create, entity_search, relationship_create, batch_ingest, graph_stats, execute, sandbox_ls, sandbox_read, sandbox_write, datasource_list, datasource_describe, datasource_query_preview, datasource_view_create, datasource_view_drop, class_bind_datasource, class_unbind_datasource, class_binding_get, schema_ontology_generate, build_strategy_recommend, reverse_bind_preview, reverse_bind_apply, causal_discover, behavior_create, behavior_delete, behavior_list, behavior_invoke, action_create, action_list, action_delete, system_list, system_operations, system_query, schema_publish, action_dry_run, entity_fetch, extract_triples, table_ingest, quality_checkup, quality_report
  - brief_draft `220-227`: datasource_list, datasource_describe, schema_get, graph_stats, sandbox_ls, sandbox_read
  - answer (`ANSWER_TOOLS_VIA_MCP=true`, 기본) `1108-1125` + `mcp_answer_tools.py:270-327`: sandbox_read + ontology_graph_schema(리소스 래퍼), ontology_list_schemas, ontology_get_schema, ontology_list_entities, ontology_resolve_entity, ontology_graph_cypher, ontology_get_datasource_schema, ontology_query_datasource_sql — 단, 마운트 시점에 MCP 서버에 물어 **서버가 등록한 것만** 남김(닿지 못하면 전부)
  - answer (false) `229-240`: schema_get, entity_search, neo4j_cypher_readonly, graph_stats, vector_search, sandbox_read, behavior_list, behavior_invoke, entity_fetch, datasource_sql_query
  - answer_nods: answer에서 데이터소스 도구 제외
  - act `1128-1136`: answer(데이터소스 포함) + kinetic: query_system, list_actions, plan_action, plan_action_ids, get_plan, execute_plan, get_run, list_runs, compensate_run (`A/backend/src/modules/kinetic/mcp_tools.py:232-242`) — 승인 도구 없음
  - dashboard: dashboard_get, widget_recommend, dashboard_patch (`A/backend/src/modules/board/tools.py:85`)
- 도구 목록은 프로세스 기동 시 결정 → MCP 서버가 늦게 뜨면 answer 표면이 전체 목록으로 고정 (추정).

## 8. Studio 검색 MCP 서버 (`ontology_mcp`, 별도 프로세스)

- 진입 `A/backend/src/modules/ontology_mcp/__main__.py:14-34` — `MCP_TRANSPORT` http/streamable-http→streamable-http, sse, 그 밖 stdio. 앱은 http, 127.0.0.1:<mcp>, 경로 `/mcp`(FastMCP 기본).
- 서버 `server.py:61-289` — 이름 `ontology-studio-search`; `MCP_EXTRA_ALLOWED_HOSTS`가 있으면 DNS 리바인딩 허용 호스트 추가(70-82). 없으면 FastMCP 기본(호스트 127.0.0.1 → 리바인딩 보호 자동 켜짐, `PY/mcp/server/fastmcp/server.py:161,177-180`).
- 항상: `ontology_query(question, schema_hint)`(84-125, 진행을 MCP log/progress로 흘림), `ontology_list_entities(class_name, schema_name, criteria, semantic_query, limit)`(127-149), `ontology_list_schemas()`(151-155), `ontology_get_schema(schema_name)`(157-161), 리소스 `graph://schema`(170-184, application/json), 프롬프트 `ontologic_agentic_rag`(189-198, 스킬 본문).
- 확장(`MCP_ALLOW_DATASOURCE_EXPANSION`): `ontology_resolve_entity(text, class_name, limit=5, context)`, `ontology_graph_cypher(query, params="{}", as_of, known_at)`, `ontology_get_datasource_schema(class_name, schema_name)`, `ontology_query_datasource_sql(sql, limit)` (203-287).
- `ontology_query` 내부: 같은 프로세스에서 `generate_sse`를 돌림, 세션 id `mcp-<12hex>`, 모드 answer/answer_nods(확장 여부), 끝나면 세션 삭제 (`adapters.py:75-82,159-237`). 반환 `{answer, sources[], meta{session_id, referenced_node_count, streamed, note?}}`.
- 쓰기 차단: `runtime_adapters.py:48-52` 정규식 CREATE/MERGE/DELETE/DETACH/SET/REMOVE/DROP/FOREACH/CALL/LOAD CSV; 카탈로그·레지스트리 라벨 차단 `55-68`; SQL은 바인딩 테이블만·행 수 `DATASOURCE_AGENT_ROW_PREVIEW`(30)로 자름 `442-480`.
- 백엔드 → 이 서버 클라이언트: `A/backend/src/shared/kernel/mcp_client.py:89-116` (`<PREFIX>_TRANSPORT/URL/COMMAND/TIMEOUT(60)/SAMPLE_LIMIT(50)`, URL 정규화 `…/mcp`).
- 로컬 웹 오리진도 `/mcp*`를 이 서버로 프록시 (`E/main/web.js:77`).

## 9. 보조 스크립트

| 스크립트 | 위치 | 호출자 | 동작 |
|---|---|---|---|
| `agent_turn.py` | `R/agent_turn.py:22-47` | 포털 자연어→Cypher `E/main/index.js:288-302`, `E/main/nl2cypher.js:69-71`(cliagents 아니면 오류) | stdin `{"system","user"}` → claude: `-p <system\n\n---\n\nuser> --output-format text --allowed-tools ""`, codex: `exec --skip-git-repo-check <prompt>`; 빈 임시 폴더 cwd; 180초; 종료코드 3(미설치)·4(시간초과)·5(실패) |
| `code_app_turn.py` | `R/code_app_turn.py:31-107` | `E/main/codeapps.js:157,258,289` | stdin `{"prompt","cwd","session_id","resume"}` → claude: `-p … --output-format stream-json --verbose --allowed-tools Read,Write,Edit,MultiEdit,Glob,Grep,Bash(curl:*),Bash(node --check:*) --permission-mode acceptEdits --setting-sources project --strict-mcp-config` + `--session-id`/`--resume`; codex: `exec --skip-git-repo-check --full-auto -C <cwd> <prompt>`(세션 안 이음); 20분; stdout JSON 줄 `token/tool_start/tool_result(600자)/error/usage/final` |
| `seed_ontology.py` | `R/sample/` | `E/main/index.js:191-203` | 첫 실행 예제 온톨로지 (A2/M1) |
| `runStudioScript` | `E/main/services.js:189-199` | | `execFile(python, [script])`, cwd=userData, Studio env, maxBuffer 16MB, timeout 300초, stderr 마지막 20줄 로그, 실패 시 stderr 마지막 3줄로 reject, stdin 입력 선택 |
| `spawnStudioScript` | `E/main/services.js:202-205` | | 같은 env로 spawn, 자식 반환(스트리밍) |

대시보드의 CLI 호출 (`A/backend/src/modules/board/ask.py`): 단발 `_call_cli` 186-221 (claude `--allowed-tools ""`, cwd 지정 없음 → 백엔드 cwd=userData), 스트리밍 `stream_cli` 227-300 (claude `--mcp-config` dashboard 브리지 + `--strict-mcp-config` + `--allowed-tools mcp__ontology-studio__{dashboard_get,widget_recommend,dashboard_patch}`), 내장이면 OpenAI chat completions JSON 모드(`_call_openai` 336-366, 모델 `MAJOR_MODEL`의 콜론 뒤, 없으면 gpt-4.1), CLI 실패 시 API 키 경로로 대체(370-385).

## 10. 스킬

| 항목 | 위치 |
|---|---|
| 스킬 폴더 | `A/skills/` — dashboard-compose, dashboard-edit, ontologic-agentic-rag, ontology-act, ontology-answer, ontology-brief-draft, ontology-build, triple-extract (+README) |
| 로더 | `A/backend/src/modules/agent_session/skill_registry.py:40-218` — frontmatter 필수(name=폴더명, 소문자-하이픈 ≤64자, description ≤1024자, version), 본문 비면 오류, `.mcp.json`·`.claude-plugin/` 제외, 텍스트 파일만 |
| `[환경]` 블록 | `skill_registry.py:204-218` — "스킬 폴더 / 업로드 / 출력" 세 줄 |
| 내장 에이전트용 동기화 | `skill_sync.py:23-48` — `<workdir>/.skills/<name>/`에 내용이 다를 때만 씀 |
| 내장 프롬프트 조립 | `service.py:1044-1078` |
| 질의·액션 합본 | `mcp_answer_tools.py:73-113` — 머리말(라우팅 규칙) + 1부 답변 지시문 + 2부 액션 지시문, 참조 파일 합침 |
| 답변 스킬 선택 | `mcp_answer_tools.py:59-68` — via MCP면 `ontologic-agentic-rag`, 아니면 `ontology-answer` |

## 11. 샌드박스

- `A/backend/src/shared/sandbox/__init__.py:13-41` — docker/local 선택(앱은 local 고정).
- `local_backend.py:1-80` — 호스트에서 `bash -lc`, `/workspace` 경로를 `<root>`로 다시 씀, `<root>/workspace → <root>` 심볼릭 링크, "DEV-ONLY: 격리 없음" 주석, 실행 timeout 120초.
- 내장 에이전트 도구 `sandbox_tools.py:20-75` — execute(출력 3000자), sandbox_ls(기본 `/workspace/uploads`), sandbox_read(offset/limit 200, 3000자), sandbox_write.

## 12. 홈·트레이 노출 (M8과 공유)

- IPC `lite:info` `E/main/index.js:306-316` → `{graph, ports, phase, agent{backend,agentId,label,ready,note}, llmConfigured=a.ready, kineticConfigured=kineticUp||!!KINETIC_URL, version}`; `tabs.js:220`.
- 트레이 `E/main/tray.js:28-31` `에이전트: <label>`.

## 13. 프런트엔드 번들 (문자열 확인만)
- `api/stream`, `api/agent/steer`, `api/session/reset`, `steered`(3), `ask_user`(1) 존재; `api/agent/running`, `/mcp` 미발견 (`shared/app/runtime/frontend/assets/index-Bnym06ph.js` grep).

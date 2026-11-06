# M2 질의·액션 — 코드 추적 (원본 근거, 구현 세션에 넘기지 않음)

- 기준: 배포본 0.1.1. 경로 약어:
  - `FE` = `shared/app/runtime/frontend/assets/index-Bnym06ph.js` (압축 번들, 위치는 바이트 오프셋 `@N`)
  - `BE` = `shared/app/runtime/studio/app/backend/src/modules`
  - `SK` = `shared/app/runtime/studio/app/skills`
  - `KA` = `shared/app/runtime/kinetic/app/app`
  - `SH` = `extracted-app-asar/src/main`
- 관련 문서: A3(에이전트 실행·브리지 MCP·SSE 공통), M7(실행기 레지스트리·호출 계약·토큰), M1(액션 정의·발행).

## 0. 전체 흐름

```
[act 화면] --EventSource GET /api/stream?prompt&session_id&mode=act--> [Studio 백엔드]
   generate_sse → 에이전트(act 모드)
     ├ cliagents: claude/codex 자식 프로세스 → MCP /mcp/agent-bridge/act/ (백엔드)
     └ deepagents: 같은 도구 함수를 프로세스 안에서 호출
   act 도구 = 답변 도구(검색 MCP 서버 대리) + 키네틱 도구(실행기 MCP 대리, KINETIC_AGENT_TOKEN)
   도구 결과 → SSE tool_start/tool_result/traversed_nodes/kinetic_plan/kinetic_run → done
[계획 카드] --REST /api/act/plans/{id}, /approve, /execute, /runs/{id}, /compensate--> [백엔드 프록시, KINETIC_STUDIO_TOKEN]
   → [kinetic-action /api/kinetic/...] → 업무 시스템(M7 호출 계약)
```

## 1. 화면 (FE)

| 항목 | 위치 | 내용 |
|---|---|---|
| 모드 정의 | `@2271800` 부근 `J9.act` | label `질의·액션`, description, inputPlaceholder, `allowsFiles:!1`, examples 4개(고정 문자열) |
| 내비 | `@2304800` 부근 `Nt` | `{id:'act',label:'질의·액션',icon:'💬',conversational:!0}`. `?view=act&session=<id>` 처리 |
| 대화 모드 묶음 | 같은 곳 `It=['build','answer','act']`; 세션 열 때 answer/act → act 뷰 |
| 세션 목록 분리 | `@2273900` 부근 `j = sessions.filter(mode==='act')`, `A`=answer, `k`=그 밖 |
| 스트림 URL | `@2287035` `ht(prompt, mode, ctx)` → `/api/stream?prompt&session_id&mode[&build_context]` |
| 그래프 로드 | `@2288310` `Ct()` → `GET /api/schema` → `GET /api/graph?limit=0` 등 |
| SSE 처리 | `@2290500`–`@2294700` `Bt()` | 리스너: token, tool_start, tool_result, **kinetic_plan**, **kinetic_run**, neo4j_update(그래프 재로드), datasource_update, schema_created, **traversed_nodes**(강조 노드 id 누적), preprocess_*, todos, skill_loaded, ref_file, status, node_update, steered(「사용자 지시를 반영해 방향을 바꿉니다...」), ask_user, done |
| 세션 생성 | 같은 구역 `zt()` | `pending_` 세션이면 `POST /api/sessions?title=새 대화&mode=<m>` |
| 제목 | `Rt()` | 첫 사용자 메시지 30자(+`...`) → `PATCH /api/sessions/{id}?title=` |
| 메시지 저장 | `ft()` | `PUT /api/sessions/{id}/messages?mode=<m>` 본문 = 화면 메시지 배열(JSON) |
| 초기화 | `Kt()` | `POST /api/session/reset?session_id=` |
| 끼어들기 | `Vt()` | `POST /api/agent/steer?session_id&mode` `{text}` |
| 단계→카드 묶기 | `@231000` 부근 `p(e)` | assistant 메시지 steps에서 kinetic_plan(plan_id별 1개) / kinetic_run(같은 plan에 runId 붙임, 없으면 run 단독 카드) |
| 빈 화면 | `@232300` 부근 | 제목 `ONTOLOGIC Studio`, 모드 라벨·설명, 예시 버튼(클릭=전송) |
| API 클라이언트 | `@117800` 부근 | `createPlan(class,action,where,params)`→POST `/api/act/plans`; `getPlan`; `approvePlan(id,note)`→POST `{note}`; `executePlan`; `getRun`; `compensateRun(id,reason)`→POST `{reason}`; 상태 라벨 표 `cie`(planned 계획됨, awaiting_approval 승인 대기, approved 승인됨, executed 실행됨, expired 만료, rejected 거부), `lie`(running 실행 중, succeeded 성공, partial 일부 실패, failed 실패, compensated 보상 완료, partially_compensated 일부 보상), `uie`(대상: succeeded 성공, failed 실패, compensated 보상됨, dead 사람 처리 필요, skipped …) |
| 계획 카드 `KineticPlanCard` | `@175600`–`@186800` | props planId/initialPlan/runId/runStatus/apiBase. 최대 표시 행 50(`Wo`), 실행 중 폴링 1500ms(`Kse`). 마운트 시 `GET /api/act/health`로 identity(sub, roles). `p`=작성자==화면 sub, `m`=화면이 approver. 실행 버튼 조건 `h`: (approved 또는 planned&&!requires_approval) && allowed>0, 그리고 작성자==화면이고 run 없음. 그 밖이면 안내문 「에이전트가 만든 계획입니다. [승인되었습니다 — ]대화에서 “실행해”라고 요청하면 에이전트가 실행합니다.」. 승인 UI는 status=awaiting_approval일 때만(메모 입력 + 「승인」). approver 없으면 경고 「현재 스튜디오 신원(<sub>)에 kinetic_approver 역할이 없어 승인이 거부될 수 있습니다.」. 승인 403 → 「승인 권한이 없습니다 (kinetic_approver 역할 필요): …」. 취소 버튼 조건 `x`: run이 succeeded/partial이고 성공 대상이 있고 (화면이 작성자 또는 approver). 확인창 문구, 단계 칩(시스템 이름 대문자, 접두 `mock-` 제거) 범례 「✓ 성공 · ✗ 실패 · – 건너뜀 · ↺ 보상(되돌림) 완료 · ⚠ 보상 실패」, 「보상 이력 (호출 순서)」 표(#/시각/대상/단계/시스템/결과/계기), 「자동 보상 N건」, 「취소 요청 — <sub> · 사유 “…” · <시각>」. 표 속성 열은 첫 행들에서 `$key`·`_*`·created_at·updated_at·embedding 제외 최대 3개 |
| 홈 최근 항목 | `SH/../renderer/shell/shell.js:219–231` | `/api/sessions`의 세션 → 종류 「질의·액션 대화」(mode가 build가 아니고 schema 없는 것), target `view=act, session` |

## 2. 백엔드 — 대화(SSE)와 세션 (BE/agent_session)

- `api.py:31` `GET /api/stream` (mode ∈ build/answer/act), `:53` steer, `:74` running, `:81` reset(+작업 파일 삭제), `:94` `GET /api/sessions`, `:101` `POST /api/sessions?title&mode&schema_name` → id = uuid hex 12자, `:110` DELETE, `:119` PATCH(title, schema_name), `:134`/`:145` 메시지 GET/PUT(`frontend_state` 표).
- `session_store.py:39–75` SQLite(`SESSION_DB_PATH` = `<userData>/sessions.db`) 표 `sessions(id,title,mode,schema_name,created_at,updated_at)`, `messages`, `build_context`, `frontend_state(session_id,mode,state_json,updated_at)`.
- `service.py:97–101` act 모드 정의. `:1128` `act_mode_tools()` = `answer_mode_tools(include_datasource=True)` + 키네틱 9개. `:1139` 내장 act 에이전트(스킬 `ontology-act`, 공유 체크포인터). `:1190` `get_agent` cliagents면 `CliAgentAdapter("act")`.
- `service.py:1853` `_run_agent_in_thread`: `:1890` **act는 같은 thread 유지**(다른 모드는 체크포인트가 있으면 새 하위 thread) — 앞 턴 plan id를 이어받으려고.
- `service.py:1987` `generate_sse`: act는 프롬프트 가공 없음(`effective_prompt = prompt`), 시작 `status` 「질의·액션 모드 실행 시작...」(`:2062`). 끝 `done{message:"완료!", files, text, build_report:null}`.
- `service.py:1627` `_kinetic_event`: 도구 결과 JSON이 오류가 아니고, plan 계열(`plan_action`,`plan_action_ids`,`get_plan`)이면서 `id`·`allowed`가 있으면 `kinetic_plan{plan_id,status,requires_approval,tool}`; run 계열(`execute_plan`,`get_run`,`compensate_run`)이면서 `id`·`targets`가 있으면 `kinetic_run{run_id,plan_id,status,tool}`. tool_result는 3000자에서 잘리므로 id만 보내고 화면이 REST로 다시 읽음.
- `service.py:1660` `_emit_tool_side_effects`: FastMCP 봉투 벗김 → … → kinetic 이벤트 → `_QA_NODE_TOOLS`(`:272`: entity_search, neo4j_cypher_readonly, vector_search, ontology_graph_cypher, ontology_list_entities, ontology_resolve_entity)면 `traversed_nodes{tool,node_ids}`.
- `service.py:1744–1790` 노드 id 추출: 결과가 리스트이거나 dict의 `nodes/entities/results/rows/matches/candidates/items/records` 배열; 항목의 `node_id`, `_element_id`, `id`(문자열이고 `:` 포함), 한 단계 중첩 dict의 같은 키. 순서 유지 중복 제거.
- `service.py:1487` `clear_session`: 메모리·체크포인트 삭제 대상이 `build`, `answer`뿐 — **act thread 체크포인트(`<sid>:act`)는 지우지 않음**(내장 에이전트에서 삭제한 세션 id를 다시 쓸 일은 드묾). CLI 세션 기억은 `forget_session`이 접두 `<sid>:`로 모두 지움(`cliagents_backend.py:817`).
- `cliagents_backend.py:611–645` 모드→스킬: act → `ontology-act`이지만 실제 패키지는 `mcp_answer_tools.act_skill_package()`(합본). `:651` MCP URL `http://<host>:<backend_port>/mcp/agent-bridge/act/`. `:223` `--permission-mode bypassPermissions`, `:375` Codex `--dangerously-bypass-approvals-and-sandbox`. `:743` env = `launch_env(dict(os.environ))` → 백엔드 환경 전체 상속.
- `mcp_answer_tools.py:63` 답변 스킬 선택(`ANSWER_TOOLS_VIA_MCP` 참 → `ontologic-agentic-rag`, 거짓 → `ontology-answer`; 셸 기본 true). `:79` `ACT_PREAMBLE`(라우팅 규칙), `:95` 합본 = 머리말 + `# 1부 — 질문 답변` + 답변 본문 + `# 2부 — 액션 실행` + 액션 본문. `:104` 참조 파일 합침.
- `agent_bridge_mcp/server.py:49` act 모드 도구 = `act_mode_tools()`, `router.py:15` 모드 6개.

## 3. 스킬 (SK) — 구조만
- `ontologic-agentic-rag/SKILL.md`(111줄, v1.3.0) + `references/two-step-retrieval.md`: 전제(도구 없으면 멈춤), 권한(조회 전용, 카탈로그·레지스트리 라벨 금지), 흐름 0–5(의미 검색 → 스키마 1회 → 이름→키 해석 → Cypher 탐색 → 클래스 스키마 → DB 집계 SQL), 규칙(근거 밝히기: 그래프는 노드 이름/번호, 데이터는 `datasource.table`+행 수; 조회 실패를 "없다"로 말하지 않기; truncated 표시), 완료 기준.
- `ontology-act/SKILL.md`(149줄, v1.1.0): 언제/맡지 않는 것(승인), 전제(키네틱 도구 8+1), 절대 규칙 7개, 워크플로 8단계, 취소 5단계(+여러 건 `list_runs` 최근 것부터), 완료 기준. 화면 표 형식(허용/거부 표, 보상 seq 표) 지시.

## 4. 백엔드 — 키네틱 도구(에이전트용)와 프록시(화면용) (BE/kinetic)

- `mcp_tools.py:30–42` 실행기 MCP 클라이언트: URL `KINETIC_MCP_URL`(셸이 `http://127.0.0.1:<kinetic>/mcp/` 주입), 헤더 `Authorization: Bearer $KINETIC_AGENT_TOKEN`, 시간 제한 `KINETIC_MCP_TIMEOUT`(60). `:78` 연결 실패 → `{"error":"키네틱 …","hint":"kinetic-action(8030)과 api-gateway(9000)가 떠 있는지, KINETIC_MCP_URL·KINETIC_AGENT_TOKEN 이 맞는지 확인하세요."}`.
- 도구(`:100–228`): `list_actions(class_name="")`, `plan_action(class_name, action, where="[]", params="{}")`(JSON 문자열 또는 구조 허용), `plan_action_ids(class_name, action, ids="[]", params="{}")`, `execute_plan(plan_id)`, `get_plan(plan_id)`, `get_run(run_id)`, `list_runs(limit=10)`, `compensate_run(run_id, reason="")`, `query_system(system, operation_id, path_params="{}", query="{}")`. **승인 도구 없음.** `:232` 순서, `:247–248` plan/run 도구 이름 집합.
- `client.py`: `:90` `KINETIC_STUDIO_TOKEN`, `:94` `KINETIC_AGENT_TOKEN`(비면 스튜디오 토큰으로 대체 — 내장 실행기에서는 항상 설정됨), `:112` `token_identity`(서명 미검증), `:136` 오류 변환(401/403 문구), `:279–321` plan/approve/execute/run/compensate.
- `api.py:360` `GET /api/act/health`, `:464` `GET /api/act/actions?class_name=`, `:471` `POST /api/act/plans`(body `{class, action, where, params}`), `:480` `/plans/by-ids`(`{class, action, ids, params}`), `:487` GET plan, `:492` **approve**(`{note}`), `:499` execute, `:506` GET run, `:511` compensate(`{reason}`). 모두 스튜디오 토큰으로 실행기 호출. 오류는 실행기 상태코드 + `{error:{code,message}}` 그대로(`:265` `_proxy`). 백엔드 자체 인증 없음(`host/app.py:52` CORS `allow_origins=["*"]`).

## 5. 실행기 (KA) — 계획·승인·실행·취소

- `main.py:35–56` `/mcp*`는 Bearer JWT 검증 후 MCP로(actor를 scope에), 나머지 FastAPI. `:105` REST actor 의존성. `:220–261` 계획·승인·반려·실행·run 목록·조회·재시도·취소 라우트. `:270` 감사 조회(admin/approver만). REST에는 `/plans/{id}/reject`, `/runs/{id}/retry`, `/runs`, `/audit`가 있으나 Studio 프록시·화면에는 없다.
- `mcp_tools.py:56–168` 실행기 MCP(무상태, JSON 응답, **DNS 리바인딩 보호 꺼짐**), 도구 9개(계약상 인자 이름 `class`), 승인 도구 없음.
- `auth.py:53–82` RS256/JWKS 검증, aud·iss, `sub`·`exp` 필수, 여유 30초; `require_role`.
- `plans.py`:
  - `:130` `list_actions`: 정책 규칙 중 actor 역할에 적용되는 것이 하나라도 있으면 보임(`policy.visible`).
  - `:165` `plan`: 액션 조회(없으면 404 `not_found` 「액션 '<C>.<A>' 이 발행되지 않았습니다.」, 안 보이면 403) → 파라미터 검사 → 필터 검사(ids 모드면 비어 있지 않은 배열) → 단계·보상 시스템/operation 확인 → 그래프에서 `max_targets+1`개 조회(초과면 422 `too_many_targets`) → 대상마다 정책 평가(허용/거부+사유) → 허용 대상×단계 미리보기(비밀 헤더 제외, `compensable`) → `requires_approval = 허용 수 > confirm_threshold` → status `awaiting_approval`|`planned`, `expires_at = now + KINETIC_PLAN_TTL(600초)` → 저장·감사 `plan`.
  - `:210` `_load`: 살아 있는 상태(planned/awaiting_approval/approved)인데 만료 시각이 지났으면 `expired`로 바꾸고 감사 `expire`.
  - `:223` `approve`(반려 겸용): **`kinetic_approver` 역할만 검사**. 작성자와 승인자가 같아도 거부하지 않음(직무 분리 없음). 만료 409, 상태가 planned/awaiting_approval이 아니면 409 `conflict`. `approved_by`=actor sub, `approved_at`, `approval_note`.
  - `:243` `execute`: **작성자(sub 일치)만** 실행(403 `not_plan_owner`). 이미 run이 있으면 그것 반환(plan당 run 하나, DB unique). 만료 409, 반려 403, 승인 필요인데 미승인 409 `approval_required`, 허용 0건 409 `nothing_to_execute`. 실행 직전 허용 키로 다시 조회 → 없어졌으면 `skipped`(「대상이 더 이상 존재하지 않습니다」), 정책 재평가 실패면 `skipped`(「재평가 거부: …」), 통과면 `before`=현재 속성. run 저장 → plan `executed` → 대상별 사가 병렬 → 상태 집계 → 감사 `execute`.
  - `:324` `_saga`: 단계 순서대로, 각 호출 Idempotency-Key `<plan>:<key>:<step>:a<attempt>`; 실패 시 남은 단계 skipped, 성공 단계가 있으면 역순 자동 보상(`trigger:auto`, 사유 「자동 보상: '<단계>' 단계 실패」) → `compensated`/`dead`; 시도 수 ≥ `KINETIC_MAX_ATTEMPTS`(3)면 `dead`. 성공 시 되쓰기.
  - `:355` `_undo`: 성공 단계 역순, 보상 정의 없으면 `{status:"none"}`. 보상 키 끝 `:c`. `compensations[]`에 `{seq, at(ms), target_key, step, system, operation_id, status, http_status, trigger}`.
  - `:384` `_writeback`: `writeback_property`가 있으면 성공 시 첫 단계 응답의 `status`(없으면 `"done"`)를, 취소 시 `before`의 값을 그래프 노드 속성에 SET. 실패해도 결과 유지(`writeback_error`).
  - `:403` `list_runs`: 호출자가 작성한 plan의 run만, 최신순, 1–50, `cancellable` = succeeded|partial.
  - `:440` `compensate`: **작성자 또는 approver**. 이미 취소된 run이면 그대로 반환. 성공 대상만 `finished_seq` 내림차순으로 하나씩 보상(사유 없으면 「사용자 취소」), 되쓰기 원복, `compensated`/`partially_compensated`, 감사 `compensate`.
  - `_run_status`(`:45`): 성공만 → succeeded, 성공+실패 → partial, 그 밖 → failed.
- `policy.py`: 규칙 OR, 기본 거부(「정책 규칙이 없습니다 (기본 거부)」, 「호출자 역할에 적용되는 정책 규칙이 없습니다」), `roles` 비면 모두, `when`은 CEL(`actor`,`target`,`params`,`now`), 평가 오류 거부, 사유 「조건 불충족: <description 또는 식>」.
- `targeting.py`: 필터 → 파라미터화 Cypher. 속성·라벨 이름 정규식 `^[A-Za-z_가-힣][A-Za-z0-9_가-힣]*$`, 연산자 11개, 라벨은 카탈로그(액션이 있는 클래스)만, ids는 `toString(n.<key>) IN $ids` 또는 elementId, 키 속성으로 정렬.
- `mapping.py`: 값 식 `$this.*`, `$this.$key`, `$params.*`, `$actor.*`, `$run.id`, `$plan.id`, `$before.*`, `$steps.<s>.response.<path>`, `$cancel.*`, `{"$literal":v}`; 미리보기에서 미정 값은 `"<식>"`. 파라미터 검사(required, 기본 타입, enum).
- `catalog.py`: 그래프의 발행 액션(`_OntologyModel-HAS_CLASS->_OntologyClass-HAS_ACTION->_OntologyBehavior{behavior_type:'action'}`)을 메모리에, 30초마다 갱신(`KINETIC_CATALOG_REFRESH`), 같은 이름이면 높은 version. `summary()` 필드.
- `dispatch.py:43–68` Idempotency 키, `X-Kinetic-Run`, 미리보기 비밀 헤더 제외, 내부 비밀 헤더·시스템 인증(직접 모드).
- `store.py:75–102` 표 `kinetic_plans(id, doc, status, actor_sub, created_at)`, `kinetic_runs(id, plan_id unique, doc, calls, status)`, `kinetic_audit(id, ts, event, actor_sub, request_id, plan_id, run_id, detail)`. DB = `<userData>/kinetic.db`(SQLite, `SH/kinetic.js:80`).
- `errors.py` 상태 표: unauthenticated 401, forbidden/not_plan_owner 403, not_found 404, invalid_filter/invalid_params/too_many_targets/not_executable/not_readonly 422, plan_expired/approval_required/conflict/nothing_to_execute 409, bad_gateway 502, 그 밖 400.

## 6. 셸 — 토큰·환경 (SH)
- `kinetic.js:18–20` aud `kinetic-action`, iss `ontology-studio-lite`, 30일. `:24` 역할 카탈로그 `scm_operator`. `:38` 서명키(RSA 2048)를 `secrets.json`의 `kineticKey`에 보관. `:94–103` Studio 환경: `KINETIC_URL`, `KINETIC_MCP_URL`(`/mcp/`), `KINETIC_STUDIO_TOKEN`=sub `lite-user`, roles `kinetic_admin, kinetic_approver, scm_operator`; `KINETIC_AGENT_TOKEN`=sub `lite-agent`, roles `scm_operator`; `KINETIC_ROLE_CATALOG`.
- `services.js:117–155` `studioEnv`: 앱 프로세스 환경 + studio.env + `NEO4J_PASSWORD`(PG 슈퍼유저) + KINETIC_* + `BACKEND_PORT` 등 → 백엔드와 검색 MCP 서버 환경. CLI 에이전트는 이를 그대로 상속(A3).
- `postgres.js:19–29` `<userData>/secrets.json`(0600): pgPassword, fabricPassword, + kinetic 비밀(svcPassword, 예제 서비스 키, kineticInternal, **kineticKey 개인키**).
- `codeapps.js:152–189` 코드 앱 경로의 승인·실행·취소는 `Sec-Fetch-Mode` 헤더가 있어야 통과(「승인·실행·취소는 앱 화면에서 사람이 눌러야 합니다.」) — 헤더 존재만 검사. Studio 백엔드 `/api/act/*` 직접 경로에는 이런 검사가 없음.
- `web.js:63` 실행기 미기동 시 `/api/act/health`·`/api/act/systems` 대체 응답(M7).

## 7. 예제 데이터 (resources/sample/seed_ontology.py)
- `:75–131` 액션 3개: Shipment.expediteShipment(key shipment_no, 정책 scm_operator + `target.ship_status != 'DELIVERED'` 「입고가 끝난 선적은 제외」, writeback priority), PurchaseOrder.holdPurchaseOrder(key po_id, `target.status == 'OPEN'` 「미결 발주만」, writeback status), Customer.notifyCustomer(key cust_no, scm_operator만, writeback 없음). `:197` confirm_threshold 0, max_targets 20, effect write. `:206` 시드 후 드라이런 검증.

## 8. 보안 질문 추적 — 에이전트가 사람 승인 없이 실행할 수 있는가

| # | 사실 | 근거 | 구분 |
|---|---|---|---|
| 1 | 에이전트 도구 표면(브리지 act, 내장 act, 실행기 MCP)에 승인 도구가 없다 | `BE/kinetic/mcp_tools.py:232`, `KA/mcp_tools.py:160` | 관찰 |
| 2 | 에이전트 도구는 `lite-agent`(scm_operator) 토큰을 쓴다 → 실행기 승인 API는 approver 역할이 없어 403 | `SH/kinetic.js:101`, `KA/plans.py:225` | 관찰 |
| 3 | 화면 승인은 백엔드 `/api/act/plans/{id}/approve` → `lite-user`(approver) 토큰 | `BE/kinetic/api.py:492`, `client.py:302` | 관찰 |
| 4 | 실행은 plan 작성자만 → 에이전트 계획은 에이전트만 실행, 승인 필요 plan은 미승인 시 409 | `KA/plans.py:245,256` | 관찰 |
| 5 | 실행기는 승인자≠작성자를 검사하지 않는다(직무 분리 없음). 승인 근거는 "approver 역할"뿐 | `KA/plans.py:223–237` | 관찰 |
| 6 | Studio 백엔드는 인증이 없고(CORS *), 127.0.0.1에서 승인 프록시를 연다 | `host/app.py:52`, `api.py:492` | 관찰 |
| 7 | CLI 에이전트는 권한 우회 모드로 셸 도구를 쓰며, 백엔드 환경 전체(`KINETIC_STUDIO_TOKEN`, `KINETIC_URL`, `BACKEND_PORT`, `NEO4J_PASSWORD`)를 상속한다. MCP 설정에도 백엔드 포트가 들어 있다 | `cliagents_backend.py:223,375,651,743`, `services.js:117–150` | 관찰 |
| 8 | `secrets.json`(서명 개인키 포함)이 에이전트 작업 폴더의 상위(사용자 데이터 폴더)에 같은 OS 사용자 소유로 있다 | `postgres.js:19–29`, `kinetic.js:38` | 관찰 |
| 9 | 따라서 에이전트가 셸로 ① 백엔드 approve 경로를 토큰 없이 호출, ② 실행기 approve를 `$KINETIC_STUDIO_TOKEN`으로 호출, ③ 개인키로 임의 역할 토큰 발급 — 중 하나로 자기 plan을 승인한 뒤 `execute_plan` 도구로 실행할 수 있다 | 1–8의 조합 | **추정**(실행 검증 안 함) |
| 10 | 그렇게 승인돼도 감사 기록은 `approve, actor_sub=lite-user`로 사람 승인과 구별되지 않는다 | `KA/plans.py:235` | 관찰(기록 형식) / 추정(구별 불가) |
| 11 | 이를 막는 것은 스킬 지시문(「승인을 우회하지 않습니다」)뿐이다 | `SK/ontology-act/SKILL.md` 절대 규칙 | 관찰 |
| 12 | 내장 에이전트(deepagents)의 act 모드 도구에는 셸·HTTP 도구가 없어 이 경로가 없다. 단 build 모드의 `execute`(호스트 `bash -lc`, 같은 환경)는 같은 위험 | `service.py:1128`, A3 §8 | 관찰 |

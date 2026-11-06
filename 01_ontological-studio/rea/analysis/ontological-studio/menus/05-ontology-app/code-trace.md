# M5 온톨로지 앱 — 코드 흐름 추적 (원본 근거, 구현 세션에 넘기지 않음)

- 기준: 배포본 0.1.1 (ADR-0008). 정적 분석만(앱 실행 안 함).
- 약어
  - `B/` = `shared/app/runtime/studio/app/backend/src/` (Python 백엔드)
  - `BD/` = `B/modules/board/`
  - `SK/` = `shared/app/runtime/studio/app/skills/`
  - `E/` = `extracted-app-asar/src/` (Electron 셸)
  - `R/` = `shared/app/resources/`
  - `F@N` = 프런트엔드 번들 `shared/app/runtime/frontend/assets/index-Bnym06ph.js`의 **바이트 오프셋** N (번들은 459줄짜리 압축 파일이라 줄 번호 대신 `grep -bo`로 얻은 오프셋을 쓴다)
  - `DATA/` = `shared/app/runtime/studio/app/backend/data/` (앱 패키지 안)

## 0. 전체 구조

```
홈 카드 「온톨로지 앱」 → Studio 탭 ?view=board  (E/renderer/shell/shell.js:44)
  BoardPanel (F@2156888)
   ├─ gallery 모드: BoardGallery(F@901246) = AppMaker(F@893154) + 자동 구성 + CodeAppList(F@899137) + 대시보드 목록
   ├─ editor 모드: 팔레트 ObjectPalette(F@908834) · FilterBar(F@905223) · 격자(gridstack 13.0.1) + WidgetChart(F@2137733, ECharts)
   │               · WidgetInspector(F@912783) · AskPanel(F@886069) · WidgetActions(F@2150477, 계획 카드는 M2 부품)
   └─ codeapp 모드: CodeAppView(F@2143942)
  대시보드 API 클라이언트 mGe (F@2140000) → /api/board/*  ─(웹 오리진 /api 프록시)→ 백엔드 BD/api.py
  코드 앱 API 클라이언트 (F@896705)        → /codeapps/api/*  ─(웹 오리진)→ 셸 E/main/codeapps.js
  액션 클라이언트 co (F@117328)            → /api/act/*, /api/schema/classes/{c}/actions → B/modules/kinetic/api.py (M2/M7)

백엔드 board ──(MCP 클라이언트, BOARD_MCP_URL=http://127.0.0.1:<mcp>/mcp)──▶ 검색 MCP 서버(A3)
    도구: ontology_graph_cypher · ontology_query_datasource_sql · ontology_get_datasource_schema, 리소스 graph://schema
백엔드 board ask/compose ──▶ CLI 에이전트(claude/codex) 또는 OpenAI 호환 API
    스트리밍 편집 시 CLI가 백엔드 자신의 /mcp/agent-bridge/dashboard/ 에 붙음(도구 3개)
셸 codeapps ──(Bolt 드라이버, READ 세션, 그래프 pg.GRAPH='ontology')──▶ Ontological 엔진
셸 codeapps ──spawn──▶ python R/code_app_turn.py ──spawn──▶ claude -p … / codex exec …  (cwd=앱 폴더)
```

라우트 마운트: `B/host/app.py:14,60-62` (board 라우터 `/api/board`). 셸 웹 오리진: `E/main/web.js:71-72` (`/codeapps/api/*` → `codeapps.handle`, `/apps*` → `codeapps.serve`), 나머지 `/api/*` → 백엔드 프록시(`web.js:76`).

---

## 1. 대시보드 — 백엔드 API (`BD/api.py`, prefix `/api/board`, 19개)

| # | 메서드 경로 | 줄 | 처리 | 요청 | 응답 |
|---|---|---|---|---|---|
| 1 | GET `/health` | 48 | `service.health` (`BD/service.py:50-58`) | — | `{transport, target, mcp:"ok"\|"unreachable", datasource_expansion, tools[], error?, row_budget:{cypher, sql}, cached_profiles}` (`B/shared/kernel/mcp_client.py:299-313`) |
| 2 | GET `/models` | 53 | `fetch_map` | — | `{models, counts, note}`; MCP 불통 503 |
| 3 | GET `/classes?schema_name=` | 64 | `service.list_classes` (`service.py:85-100`) | — | `{models, classes, counts, note}` (graph://schema 그대로) |
| 4 | GET `/classes/{c}/profile?schema_name=&refresh=` | 72 | `profile.build_profile` | — | ObjectProfile(별칭 `class`, `schema`); 동명 클래스 409 `{error, ambiguous:true, schema_names}`; 없음 404 |
| 5 | GET `/classes/{c}/related` | 89 | 프로파일의 `datasource_refs` | — | `{related:[{from_class,class,datasource,schema,table,via_relationship,join_on}]}` |
| 6 | POST `/classes/{c}/recommend?schema_name=&refresh=` | 100 | `service.recommend_for` (`service.py:108-130`) | — | `{primary: WidgetSpec, secondary: [WidgetSpec], profile}` 또는 가드 `{guard, reason, profile}` |
| 7 | POST `/widgets/query` | 114 | `service.run_widget` (`service.py:245-289`) | `{widget, params{}, global_filters[], selection}` | QueryOutcome `{columns, rows, returned_count, total_count, truncated, aggregation_promoted, badge, fallback, context[], error}` (항상 200, 오류는 `error`) |
| 8 | GET `/classes/{c}/values?property=&schema_name=&limit=50` | 122 | `service.distinct_values` (`service.py:327-365`) | — | `{class_name, property, type, role, values[], truncated, distinct_count}` |
| 9 | POST `/filters/applicability` | 136 | `service.filter_applicability` (`service.py:368-382`) | `{source_class, property, class_names[]}` | `{source, applies_to{클래스:{how,property,via?}}, not_applicable[]}` |
| 10 | GET `/dashboards` | 153 | `spec_store.listing` (`spec_store.py:123-133`) | — | `{dashboards:[{id, name, widgets(개수), updated_at}]}` (파일명순) |
| 11 | GET `/dashboards/{id}` | 158 | `spec_store.load` + `resolve` | — | `{dashboard, resolution:[{widget_id, class_name, status, reason?, schema_names?}]}`; 없음 404 |
| 12 | PUT `/dashboards/{id}` | 171 | `spec_store.save` | DashboardSpec | `{dashboard}`; 검증 실패 422 `{errors:[{path, reason}]}` |
| 13 | DELETE `/dashboards/{id}` | 181 | `spec_store.delete` | — | `{deleted: bool}` |
| 14 | POST `/dashboards/{id}/patch` | 186 | `tools.dashboard_patch` (`BD/tools.py:46-81`) | `{patch[], dry_run=true}` | `{valid, diff[], errors[], applied}` |
| 15 | POST `/dashboards/{id}/ask` | 192 | `ask.ask` (`BD/ask.py:388-436`) | `{question, widget_id}` | `{valid, applied:false, diff, errors, patch, note, question, no_patch?}`; 503 AskUnavailable |
| 16 | POST `/dashboards/{id}/ask/stream` | 206 | `ask.ask_stream` (`ask.py:439-506`) | 같음 | SSE `data: {kind, …}`: `token{text}`, `tool_start{tool_call_id,name,args}`, `tool_result{tool_call_id,content(400자)}`, `error{message}`, 마지막 `result{…15와 같음}` |
| 17 | POST `/compose` | 235 | `compose.compose` (`BD/compose.py:199-257`) + 저장 | `{schema_name, dashboard_id, use_agent=true}` | SSE: `tool_start{name:"widget_recommend", args:{class_name}}`, `tool_result{content}`, 에이전트 이벤트, `token`, `error`, 마지막 `result{created, dashboard_id, dashboard, skipped, note}` 또는 `{created:false, skipped, reason}` / `{created:false, errors}` |
| 18 | POST `/dashboards/{id}/export/superset` | 307 | `superset_export.export` (`BD/superset_export.py:103-146`) | — | `{charts:[{slice_name, viz_type, datasource_id:null, datasource_type:"table", source{datasource,schema,table}, params(JSON 문자열)}], excluded:[{widget_id, class_name?, reason, detail?}]}` |
| 19 | POST `/cache/clear` | 329 | 프로파일 캐시·확장 여부 캐시 비움 | — | `{cleared: true}` |

### 1.1 데이터 계약 (`BD/models.py`)
- 위젯 종류 닫힌 목록 17개 (`models.py:14-24`): kpi, kpi_group, table, bar, bar_h, pie, timeseries_line, box_plot, treemap, sunburst, word_cloud, heatmap, scatter, pivot_table, geo_point, geo_path, geo_polygon
- 역할 5종(identifier/temporal/numeric/categorical/unknown), 타입 6종(boolean/integer/float/date/string/geojson), 집계 5종(count/sum/avg/min/max) (`26-32`)
- PropertyProfile `35-52`, DatasourceRef `55-66`, ObjectProfile `69-95`, Measure `98-101`, Filter `104-109`(op eq/ne/gt/gte/lt/lte/contains/in, **값이 아니라 `param_key`**), Layout `112-116`(기본 w6 h2), WidgetSpec `119-140`(대입 시 검증), GlobalFilter `143-158`(kind time/category, op eq/gte/lte/between/in/contains), Selection `161-167`, DashboardSpec `170-179`(format_version 1), QueryOutcome `182-195`
- 원칙(주석 `models.py:3-4`): 저장물에 질의문이 없다 — Cypher·SQL은 조회 시점에 만든다.

### 1.2 저장 (`BD/spec_store.py`)
- 저장 폴더 `storage_dir` `34-38`: 환경 변수 `BOARD_STORAGE_DIR`, 없으면 `<백엔드 패키지>/data/boards` = **앱 패키지 안** `DATA/boards/`. 셸은 이 변수를 넣지 않는다(`E/main/services.js:124-157` 환경 조립에 없음 — M8 code-trace 69행과 일치).
- 실측: `DATA/boards/`에 배포 시점 파일 12개(2026-10-24~26 생성): `공급망-현황판.json`, `-2`~`-4`, `공급망-조치판.json`, `발주-조치판.json`·`-2`~`-4`, `조치판-2`·`-3`, `공급망_운영___늦어진_입고는_어느_협력사_발주_건이고__품질_클레임은_어느_고객_주문에서_나왔나.json`(자동 구성 결과, 위젯 6·전역 필터 3). `DATA/releases/`는 사용자 실행 시 생성(2026-10-29) — 같은 문제(release 모듈 `B/modules/release/api.py:36`).
- 키 `storage_key` `91-94`: `[^A-Za-z0-9_가-힣-]` → `_`, 80자. 파일 `<키>.json`, UTF-8, 들여쓰기 2.
- 검증 `validate` `55-84`: 금지 키(password, passwd, secret, token, host, port, user, username — 대소문자 무시, 어느 깊이든), 문자열 값에 `SELECT|MATCH|MERGE|INSERT|UPDATE|DELETE` + 공백이 있으면 거부, 위젯 종류 목록 밖, 위젯 id 중복, 위젯 필터의 `param_key`가 `params`에 없음.
- 저장 `save` `104-113`: updated_at=지금(UTC, 초), created_at 없으면 지금.
- 열기 해소 `resolve` `148-189`: 위젯별 `ok | missing_class | ambiguous_class | expansion_disabled | missing_property` + 한국어 사유. 일부가 깨져도 연다.
- 패치 `apply_patch` `196-280`: 항목 `{op: set|add|append|remove, widget_id, field, value}`. `add`+field 없음 = 위젯 추가(값은 WidgetSpec), `add`+field = 목록 필드에 덧붙임, `set`은 필드 대입(대입 검증), set/add로 손댄 위젯은 `pinned=true`. 끝에 참조 무결성(없는 클래스·속성) + `validate`. 결과 `{valid, diff[{op, widget_id, field?, before?, after?, widget_kind?}], errors[{path, reason}], draft}`.

### 1.3 프로파일 (`BD/profile.py`)
- `fetch_map` `284-288`: MCP 리소스 `graph://schema` (필드: `models[{schema_id, name, description, intent, golden_questions, golden_commands, format_version, published_at}]`, `classes[{schema_name, class_name, description, binding_kind, property_names, property_source, native, native_key, behavior_count, source{datasource,schema,table}?, orphaned?}]`, `relationships[{schema_name, name, from_class, to_class, description, properties[], observed_in_graph}]`, `counts`, `note?` — `B/modules/ontology_mcp/runtime_adapters.py:118-157`, `B/modules/ontology_runtime/graph_schema.py:77-104,301-420`).
- `build_profile` `298-374`: 동명 클래스(다른 모델) → AmbiguousClass. 캐시 키 `<schema_id>@<published_at>` (TTL 없음, 재발행이 무효화, `refresh=true` 수동). count Cypher `MATCH (n:_Entity:<C>) RETURN count(n) AS c`; 가상이면 `_profile_virtual`(377-404: `ontology_get_datasource_schema` → 선언 타입, 표본 `SELECT <cols> FROM <schema.table>` limit 200 + `COUNT(*)`), 물리면 `_profile_materialized`(460-508: `MATCH (n:_Entity:<C>) RETURN n LIMIT <BOARD_MCP_SAMPLE_LIMIT=50>` → 값에서 타입 추론, 시스템 속성·`_` 접두 제외); `MATCH … RETURN n LIMIT 1`의 `_datasource_refs` 수집.
- 타입 추론 `infer_type` `102-134`(모두 일치해야 함: geojson → boolean → 숫자 문자열(앞자리 0이면 문자열 유지) → integer → float → date(ISO 문자열 포함) → string), 역할 `assign_role` `137-159`(geojson→unknown, date→temporal, 키·참조·이름 꼬리 `_id/_no/_code/_key`→identifier, 수→numeric, 불·문자→categorical), 좌표 `_looks_like_coordinate` `162-178`(이름 패턴 lat/latitude/위도·lng/lon/long/longitude/경도 **그리고** 값 범위).

### 1.4 위젯 추천 엔진 (`BD/widget_map.py`, 결정적)
- 상수 `20-23`: 범주 최대 25, 계열 최대 8, 행렬 15, 긴 텍스트 평균 40자. 시계열 최소 시점 5 (`143`).
- 가드 `check_guards` `39-59`: G8 가상+확장 꺼짐, G2 데이터 행 0, G5 속성 30개 초과. (G6 없음 → 표로 떨어짐)
- 범주 후보 `_categoricals` `86-103`: 긴 텍스트 제외, 고유값 <2 제외, 행 ≥5이고 고유값 ≥ 행×0.9면 이름표로 보고 제외, 고유값 오름차순.
- 지표 묶음 `_compatible_scale` `106-130`: 첫 지표 크기의 100배 안쪽만, 최대 3개.
- 규칙 순서 `RULES` `382`: O5(경로) → O6(구역) → O4(위경도 점) → O1(시계열: 키에 있는 시간 또는 시점 ≥5, 수치 ≥1, 행 ≥3, 계열 범주 ≤8, 입도 day, 지표 avg) → O2(box_plot: 범주 1+수치 정확히 1, 범주 ≤25, 수치 고유값 ≥ 4×범주) → O3(treemap: 범주 ≥2 카디널리티 단조 증가 또는 자기참조, 곱 ≤400, 최대 4단) → O7(word_cloud: 긴 텍스트, 고유값 ≥ 행×0.6) → O8(heatmap: 범주 2개 각 ≤15 + 수치) → O9(kpi/kpi_group: 행 1, 수치 1–6, 범주·시간 없음) → R6/R7(범주×수치: 2≤k≤25; 지표 1개·k≤7·이름이 비율/건수 힌트·최소 ≥0이면 pie, 아니면 k>12 bar_h 그 외 bar) → R10/R11(scatter: 수치 ≥2, 행 ≥10, 계열 범주 ≤8이면 R11). 아무것도 아니면 O10(table, 속성 앞 8개).
- 첫 판정 = 주 위젯, 나머지 = 보조. id `w_<8hex>`, 제목=클래스 이름, layout w6 h2 (`408-424`). 이유 문장은 한국어 템플릿(사용자 표시).

### 1.5 질의 생성·실행 (`BD/query_gen.py`, `BD/service.py`)
- 식별자 검사 `_ident` `31,72-77`: `^[A-Za-z_가-힣][A-Za-z0-9_가-힣]*$` 아니면 UnsafeIdentifier. SQL은 비ASCII 식별자를 큰따옴표로(`80-93`).
- 원시 위젯(집계 안 함) `RAW_KINDS` `36`: table, scatter, geo_point, geo_path, geo_polygon. 원시 열 = 키 + 차원 + 지표 속성, 최대 14 (`43-63`).
- Cypher(물리) `build_cypher` `118-161`: `MATCH (n:_Entity:<C>) [WHERE …] WITH <차원>, <집계> RETURN … ORDER BY <첫 차원>`; 첫 차원이 시간이면 `substring(toString(x), 0, k)` (year 4, month 7, day 10, hour 13; week·quarter는 문자열 절단 불가 → 승격 시 건너뜀); 문자열로 저장된 수치는 `toFloat()`; 필터 값은 항상 `$param`; `contains`는 소문자 비교.
- SQL(가상) `build_sql` `185-243`: 컬럼명 사용, `SUBSTRING(CAST(x AS CHAR(32)), 1, k)`, `GROUP BY … ORDER BY …`, LIMIT 없음(도구 인자). 필터 값은 타입별 렌더, 문자열에 `' " \` ; \\ -- /* */ 제어문자`가 있으면 **그 필터를 버림**(`_sql_where` 246-271, `_render_sql_value` 274-288).
- 실행 `run_widget` `service.py:245-289`: 전역 필터·선택 적용(`apply_context` 194-242, 연결 규칙 `BD/linkage.py:71-103` same_class → same_name → 관계 `join` 속성 한 홉) → 상한에 잘리면 최대 2회 축소(`_reduce` 26-47: 시간축+계열이면 마지막 계열 버림, 아니면 입도 한 칸 승격) → `normalize_rows`(집계 열은 count=integer 그 외 float) → `outcome_from`(잘린 시계열은 `fallback:"table"`, 배지 `"{total}건 중 {returned}건"`).
- 실행 경로 `_execute` `292-319`: 가상 → `ontology_query_datasource_sql(sql, limit=500)`(`row_count`가 참값, `truncated_for_agent`가 잘림); 물리 → `ontology_graph_cypher(query, params=JSON)` + 그룹 수 count 질의(`_count_cypher` 153-172).
- 행 예산 측정 `_probe_row_budget` `64-82`: `MATCH (n:_Entity) WITH n LIMIT 5000 RETURN id(n) AS i`의 반환 행 수를 1회 캐시.
- 값 목록 `distinct_values` `327-365`: 가상은 `SELECT DISTINCT <col> FROM <table> ORDER BY <col>`(문자열 조립, 식별자 검사 없음 — notes), 물리는 Cypher DISTINCT.
- 연결 `BD/linkage.py`: 관계의 속성 목록 중 이름 `join`인 항목의 description `"a = b"`를 파싱, 양방향 홉.

### 1.6 자연어 편집 (`BD/ask.py`) — LLM 부분
- 지시문: 스킬 `dashboard-edit` (`SK/dashboard-edit/SKILL.md`, 76줄), 자동 구성은 `dashboard-compose` (`SK/dashboard-compose/SKILL.md`, 62줄). 로딩 `ask.py:64-75` (`agent_session.skill_registry.load_skill`).
- 사용자 블록 `_context_block` `78-116`: `[사용자 요청]` + `[대시보드]`(name, widgets[id,class_name,widget_kind,rule,dimensions,measures,time_grain,pinned,title,selected?], params 키, global_filters) + `[선택된 위젯]` + `[사용 가능한 클래스와 속성]`(프로파일 있는 클래스는 속성별 role·type·distinct_count, 6000자 자름) + `[응답 형식]`(`_RESPONSE_CONTRACT` 48-57: `{"patch":[…], "note":"…"}`, 항목 4형).
- 프런트는 질문 본문 뒤에 `[사람이 고른 자원]` 목록과 `[대시보드 id]`를 덧붙인다(`Fve` F@~884000, `Qe` F@2166663).
- JSON 추출 `_extract_json` `119-168`: 첫 `{`부터 괄호 균형으로 자르고 파싱, 실패하면 다음 `{`. 없으면 산문 답(거절)으로 취급 → `no_patch:true, note=<산문 600자>`.
- 후처리: `_engine_owns_widget_kind` `544-584`(위젯 추가 패치는 클래스 이름만 받아 엔진 추천으로 대체, 에이전트가 정한 layout·title만 유지), `_kind_follows_axes` `509-541`(시계열 위젯의 첫 축을 시간 아닌 속성으로 바꾸면 `widget_kind=bar`, `time_grain=null` 패치를 덧붙임) → `apply_patch` dry-run → 항상 `applied:false`.
- 실행 경로 선택(`ask_stream` 466-480): `AGENT_BACKEND=deepagents` → `_call_openai`(339-367: chat.completions JSON 모드, 모델 `MAJOR_MODEL` 콜론 뒤 or `gpt-4.1`, `OPENAI_BASE_URL` 지원); 아니면 `stream_cli_async`(322-336, 스레드에서 한 줄씩) → 실패 시 OpenAI 경로로 대체.
- CLI 스트리밍 `stream_cli` `226-319`: claude `-p <system\n\n---\n\nuser> --output-format stream-json --verbose --mcp-config {"mcpServers":{"ontology-studio":{"type":"http","url":"http://<BACKEND_HOST>:<BACKEND_PORT>/mcp/agent-bridge/dashboard/"}}} --strict-mcp-config --allowed-tools mcp__ontology-studio__dashboard_get,mcp__ontology-studio__widget_recommend,mcp__ontology-studio__dashboard_patch`; codex `exec --skip-git-repo-check <prompt>`(텍스트 줄을 token으로). cwd 지정 없음(백엔드 cwd = 사용자 데이터 폴더), **제한 시간 없음**(Popen, 단발 `_call_cli`만 180초).
- 단발 `_call_cli` `171-223`: claude `--output-format text --allowed-tools ""`(도구 없음), 180초. `ask()`(비스트리밍)에서만 사용 — 프런트는 스트리밍만 씀.
- 브리지 도구(`BD/tools.py:15-85`, A3 `/mcp/agent-bridge/dashboard/` 서버 이름 `ontology-studio-agent-bridge-dashboard`): `dashboard_get(dashboard_id)`, `widget_recommend(class_name, schema_name="", hint="")`(힌트 무시), `dashboard_patch(dashboard_id, patch, dry_run=True)` — **`dry_run=False`면 바로 저장**(77-81). 에이전트가 턴 안에서 스스로 적용할 수 있다(notes §2).

### 1.7 자동 구성 (`BD/compose.py`)
- `_recommend_all` `51-89`: 모델의 모든 클래스를 프로파일·추천(가드면 skipped). 진행 이벤트를 `widget_recommend` 도구 이벤트 모양으로 흘림.
- 결정적 순서 `_order_key` `33-48`: 규칙 우선순위(O1 0, O4/O5/O6 1, O2/O8 2, O3 3, R6/R7/R10/R11 4, O7/O9 5, 기타 6, O10 9) → 데이터 행 많은 순 → 클래스 이름.
- 에이전트 선택 `_agent_selection` `92-149`: 사용자 블록 `[모델]{name,intent,golden_questions}` + `[담을 수 있는 클래스]{class_name, display(설명의 " — " 앞), rows, properties(12)}`(5000자) + `[응답 형식]{"title","widgets":[{"class_name","title"}],"note"}`, 최대 8. 실패·파싱 실패 → 결정적 순서(문구 이벤트 `token`).
- 결과 `compose` `199-257`: 최대 8 위젯, 배치 `x=(i%2)*6, y=(i//2)*2, w6 h2`, 제목 기본 `<모델명> 대시보드`, `model={schema_id, schema_name}`, 전역 필터 후보 `propose_filters` `161-196`(시간·범주(고유값 2–50) 속성 중 2개 이상 위젯에 걸리는 것, 최대 3개, 값 없음). 저장 키 = 요청 `dashboard_id` 또는 제목.

### 1.8 Superset 내보내기 (`BD/superset_export.py`)
- 종류 대응표 `12-30`, 물리 클래스 위젯은 `materialized_not_exportable`로 제외, `kpi_group`은 지표별 kpi로 분해, 대응 없음 `no_superset_equivalent`. `form_data`는 컬럼명 기준.

---

## 2. 대시보드 — 프런트엔드 (번들)

| 부품 | 위치 | 내용 |
|---|---|---|
| 자원 라벨 | F@~879000 (`AC`, `Nve`, `MC`, `NC`, `PC`, `FC`, `LC`, `RC`, `Fve`) | 사람 이름 = 설명에서 ` — `/` – `/` - ` 앞, 끝 괄호 제거. 멘션 ref `class:<모델>/<클래스>`, `prop:<모델>/<클래스>.<속성>`, `widget:<id>` |
| PromptComposer | F@879404 | contenteditable, 칩(`@이름`, 삭제 시 통째로), `@` 뒤 글자로 후보 최대 8개, ↑↓/Enter/Tab/Esc, 드래그 드롭(caret 위치), 붙여넣기는 평문 3000자, ⌘/Ctrl+Enter 제출(옵션: Enter 제출) |
| AskPanel | F@886069 | 「AI 로 고치기」, 대상(「대시보드 전체」/위젯), 이벤트 줄, 결과 배지 「바꿀 것 없음/적용됨/승인 대기/거부됨」, diff 목록(값 60자), 「취소」·「적용」, 「생각 중…」, placeholder 「예) @지역 별로 쪼개줘 · 평균 말고 합계로」 |
| MentionTree | F@890122 | 자원 트리(모델별), 검색, 「가상」 배지(설명 「데이터소스에 바인딩됨 — 질의하면 원천 데이터가 나옵니다」) |
| AppMaker | F@893154 | 18장 화면. 모드 board/code, 골든 퀘스천 최대 6, 버튼 문구, 안내 문구 4종 |
| 코드 앱 클라이언트 | F@896705 | `/codeapps/api` 래퍼(오류 시 `body.error` 또는 `HTTP n`), 목록·조회·생성·턴·삭제·파일, SSE 리더 |
| 도구 줄 해석 `Kye` | F@897890 | Write/Edit/MultiEdit/Read/Glob/Grep/Bash 아이콘·문구. Bash 명령에 `codeapps/api/query`와 `"cypher":"…"`가 있으면 「질의 시험 · <cypher>」, `codeapps/api/schema`면 「온톨로지 구조 읽기」. 결과가 `{rows}`면 「N행」, `{error}`면 오류 |
| CodeAppList | F@899137 | 「코드 앱 N」, 카드 상태 문구, 삭제 확인 |
| BoardGallery | F@901246 | 갤러리 전체(위 S1 문구), 0.4초 뒤 모델 기본 선택 |
| FilterBar | F@905223 | 「+ 필터 추가」(클래스별 optgroup, `속성 (기간|범주)`), 기간 입력 placeholder `2025-01`/`2025-12`, 범주 `(전체)`, `hit/total 위젯`, 선택 표시 |
| ObjectPalette | F@908834 | 「온톨로지 객체」, 「새로고침」, 확장 꺼짐·MCP 불통·note 안내, 클래스 드래그(`{kind:"ontology-class"}`)/더블클릭 추가, 속성 드래그는 멘션 |
| WidgetInspector | F@912783 | 위젯 종류 17, 입도 hour/day/month/quarter/year(week 없음), 차원 추가(역할 unknown 제외)·삭제, 지표(속성·집계) 추가·삭제, 「자동 추천으로 되돌리기」, 「고정됨」 |
| 차트 옵션 | F@~2120000–2137733 | 한국·미국 GeoJSON 내장(지도 자동 선택: 점 평균 좌표가 범위 안이면 그 지도, 기본 korea; `options.map`으로 지정), 팔레트 10색, 낮/밤 축 색, 숫자 표기(억·만 단위) |
| WidgetChart | F@2137733 | `tGe` 종류→ECharts 옵션(box_plot·word_cloud는 실제로 막대로 그림, pivot_table·kpi·table은 HTML), 오류 「…」, 빈 「데이터가 없습니다.」, 클릭 이벤트 → 선택, `data-theme` 변경 시 다시 그림 |
| 대시보드 API `mGe` | F@2140000 | 19개 중 18개 사용(`/models`, `/cache/clear` 미사용 — 확인), ask는 SSE(`/ask/stream`), compose SSE |
| WidgetActions | F@2150477 | 액션 창(S8), 선택값 → 조건, 계획 후 M2 계획 카드 부품(`Go`) 표시, 1.5초 폴링으로 실행 상태 변하면 `changed` |
| BoardPanel | F@2156888 | 상태: gallery/editor/codeapp. 격자 12칸·셀 높이 190·여백 8, 860px 이상 2열(w6) 아니면 1열(w12), 위젯 높이 2 |

### 2.1 BoardPanel 주요 흐름
- 시작(`me`): `/api/board/health` → `/api/board/classes` → `GET /api/act/actions`(클래스별로 묶어 위젯 「액션 N」 버튼) → `/api/board/dashboards`. `composeFor` prop이 있으면 바로 자동 구성(M1 연계).
- 「앱 만들기」(`Me` F@2162614): 코드 모드면 `De`(F@2162056: `POST /codeapps/api/apps {name,text,resources}` → `POST /codeapps/api/apps/<id>/turns {text,resources}` → codeapp 모드). 대시보드 모드면: 이름 = 입력 이름 또는 (멘션 뺀 문장/원문에서 `@` 제거, 24자) 또는 「새 앱」 → 키 `je` = 공백을 `-`로, 기존 id와 겹치면 `-2`,`-3`… → 편집 화면 → 멘션된 클래스마다 `recommend` 후 위젯 추가·`widgets/query` → `PUT dashboards/<키>` → (멘션 뺀 나머지 말이 있거나, 속성 멘션이 있거나, 위젯이 0개면) AI 편집 `Qe`(말이 없으면 「고른 자원으로 앱 화면을 구성해 주세요.」) → 결과가 유효하면 안내.
- AI 편집 `Qe` F@2166663: 매번 먼저 `PUT`으로 현재 화면을 저장 → `POST ask/stream` (질문 + `[사람이 고른 자원]` + `[대시보드 id]`, widget_id = 선택 위젯 또는 멘션 위젯).
- 적용 `$e` F@2167449: `POST patch {patch, dry_run:false}` → `GET dashboards/<키>`로 위젯 다시 읽기 → 전체 `widgets/query`.
- 저장 `rt`: `PUT dashboards/<nt()>` 본문 `{format_version:1, name, description:"", model:{}, widgets, global_filters, params:{}}` — **화면에서 저장하면 model이 빈 객체로 덮임**(자동 구성이 넣은 model 정보 사라짐). 키 `nt` = 처음 정한 키, 없으면 이름의 공백을 `-`로(F@2167841).
- 선택 `ze` F@2146733(문자 오프셋 기준 근처): 클릭한 행에서 프로파일 키 속성 값이 있으면 그것, 없으면 첫 차원 값.
- 되돌리기: 위젯 배열 스냅숏 스택(화면 메모리).
- Superset: 저장 후 `POST export/superset` → 대화상자.

---

## 3. 코드 앱 — 셸 (`E/main/codeapps.js`, 402줄)

### 3.1 연결 (`E/main/index.js:152-158`)
- `dir=<userData>/codeapps`, `driver`(셸의 Bolt 드라이버), `graph=pg.GRAPH`('ontology'), `webPort`, `backendPort`, `runtimeDir=R/codeapp/runtime`, `templateDir=R/codeapp/template`, `rulesFile=R/codeapp/AGENTS.md`, `spawnTurn=services.spawnStudioScript(…, R/code_app_turn.py)` (`E/main/services.js:201-204`: 백엔드와 같은 환경·인터프리터, cwd=userData).
- 종료 시 `codeapps.stopAll()` (`index.js:346`) — 실행 중 턴 자식 프로세스 kill.
- 탭: `E/main/tabs.js:76-81,87` — `kind:'app'`, id `^[a-z0-9-]{4,64}$`, preload 없음(셸 API 없음), `contextIsolation, sandbox`. URL `http://127.0.0.1:<web>/apps/<id>/`. 새 창 요청 중 `/apps/` URL은 앱 탭으로(`routeOpen` 64-70).

### 3.2 HTTP (`handle` 321-376, `serve` 379-395)
| 메서드 경로 | 줄 | 동작 | 응답 |
|---|---|---|---|
| POST `/codeapps/api/query` | 325-330 | `{cypher, params}` → 쓰기 검사 → READ 세션 실행 | 200 `{columns, rows(≤5000)}`; 400 `cypher 가 없습니다.`; 403 `읽기 전용입니다 — CREATE·MERGE·SET·DELETE 같은 쓰기 절은 쓸 수 없습니다.`; 400 `{error: 엔진 메시지(앞의 "…ERROR:" 제거, 600자)}` |
| GET `/codeapps/api/schema` | 331 | `schema()` 98-121 | `{graph, classes:[{name, count, properties, example}], relationships:[{from, type, to, description}]}` |
| `/codeapps/api/act/*` | 157-202 | 아래 3.4 | |
| GET `/codeapps/api/apps` | 339-344 | 폴더 중 `.app.json` 있는 것 | `{apps:[{id, name, updated_at, turns, running, ok}]}` (updated_at 내림차순) |
| POST `/codeapps/api/apps` | 335-338 | `create` 225-239 | `{id, name}` |
| GET `/codeapps/api/apps/<id>` | 355-358 | 메타 + 파일 | `{id, name, prompt, resources, created_at, updated_at, session_id, turns:[{text, resources, ok, report, started_at, finished_at}], running, files:[{path,size}], url:"/apps/<id>/"}` |
| DELETE `/codeapps/api/apps/<id>` | 349-354 | 실행 중이면 kill, 폴더 삭제 | `{deleted:true}` |
| POST `/codeapps/api/apps/<id>/turns` | 360-364 | `startTurn` 241-292 | `{started:true}`; 400 `무엇을 만들지 적어 주세요.`; 409 `에이전트가 아직 일하는 중입니다.` |
| GET `/codeapps/api/apps/<id>/events?from=n` | 302-319 | SSE | 메모리의 턴 이벤트 from부터 + 이후 실시간, 15초 `: ping`. 메모리에 없으면(재시작) 마지막 저장 턴을 `user`+이벤트로 재생하고 `{kind:"done", ok, replay:true}` |
| GET `/codeapps/api/apps/<id>/file?path=` | 366-371 | 앱 폴더 안 파일(숨김 제외) | `{path, text(400000자)}`; 404 `그 파일이 없습니다.` |
| 그 밖 | | | 404 `{error:"not found"}` / `그 앱이 없습니다.`; 예외 500 `{error}` |
| GET `/apps/_runtime/*` | 384 | `R/codeapp/runtime` 정적 | cache `max-age=3600` |
| GET `/apps/<id>/*` | 385-394 | 앱 폴더 정적, `/apps/<id>` → 302 `/apps/<id>/`, `/` → index.html, 숨김(`.app.json`, CLAUDE.md, AGENTS.md, 점 파일) 404 | `cache-control: no-store`, MIME html/js/css/json/svg/png 그 외 octet-stream |

- 쓰기 검사 `isWrite` 36-42: 주석·문자열 리터럴을 지운 뒤 `CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|FOREACH|LOAD CSV` 단어 또는 `CALL dbms…|og_…|apoc.(create|merge|refactor|periodic)…`. 실행은 `defaultAccessMode: READ` 세션(91).
- 값 변환 `plain` 45-64: 정수 → 숫자(안전 범위 밖이면 문자열), 노드 → 속성(시스템 속성 `_id,_type,_source_id,_parent_source_id,created_at,updated_at,embedding` 제외) + `_labels`(`_` 접두 제외) + `_id`(elementId), 관계 → 속성 + `_type`, `_id`, 경로 → 구간 목록, 시간·공간 값 → 문자열.

### 3.3 생성·턴 (`create` 225-239, `startTurn` 241-292)
- id `app-<8hex>`, 템플릿 3개 복사(`R/codeapp/template/{index.html, app.js, style.css}`), 규칙 파일의 `{{QUERY_URL}}`·`{{ACTIONS_URL}}`을 `http://127.0.0.1:<web>/codeapps/api/query`·`…/act/actions`로 바꿔 `CLAUDE.md`와 `AGENTS.md` 둘 다로 저장.
- 메타 `.app.json`: `{id, name(입력 이름 또는 문장에서 @ 제거 28자 또는 "새 앱"), prompt, resources, created_at, updated_at, session_id(UUID), turns[]}`. 턴: `{text, resources, started_at, finished_at, ok, report, events(토큰 빈 것 제외, 마지막 400개)}`.
- 첫 턴 프롬프트(247-249): `# 만들 앱: <이름>` / `## 사람의 요청` / 원문 / `## 사람이 고른 자원 (★) — 재검토하지 말고 실제로 쓰세요`(클래스·속성) / `## 발행된 온톨로지 (그래프 ontology)` + 클래스 줄(`- <라벨> [★] (<건수>건) 속성: …` + `예: {속성 8개}`) + `관계:` 줄(`(:A)-[:T]->(:B) — 설명`) / `## 이 온톨로지의 액션 — 앱에 버튼으로 연결할 수 있다 (CLAUDE.md 「액션」)` + 액션 줄(`- C.a — 설명 / 대상 키: k · 입력: p*(설명) / 골든 커맨드: "…"`) / 마무리 지시 1줄(curl로 시험 후 세 파일 완성, 한국어). 이후 턴(250): 원문 + 자원 블록 + `(같은 앱을 고칩니다. 바뀐 질의는 curl 로 다시 시험하세요. 말과 보고는 한국어로.)`.
- 스키마 수집 `schema()` 98-121: `CALL db.labels()`의 비`_` 라벨마다 예시 1건·건수, 관계 `MATCH (a)-[r]->(b) RETURN DISTINCT … LIMIT 200`, 설명은 `_OntologyRelationship` 노드에서. **발행 레지스트리가 아니라 그래프에 있는 라벨 기준**.
- 액션 목록 `actionList` 205-211: 백엔드 `GET /api/act/actions` + 클래스별 `GET /api/schema/classes/<c>/actions`에서 `golden_command` 결합(`withGolden` 170-179).
- 자식 표준입력 `{"prompt", "cwd":<앱 폴더>, "session_id", "resume": 첫 턴 아님}`(289). 표준출력 JSON 줄 → 이벤트(빈 token 제외). 종료 시 exit≠0이고 error 이벤트가 없으면 `에이전트 실행이 끝나지 못했습니다 (exit N) <stderr 300자>` 추가 → 메타에 턴 저장 → `{kind:"done", ok}`.

### 3.4 액션 프록시 (`ACT` 157-167, `act` 181-202)
| 앱 경로 | 백엔드 경로 | 사람 확인(`sec-fetch-mode` 헤더 필요) |
|---|---|---|
| GET `/act/health` | `/api/act/health` | 아니오 |
| GET `/act/actions?class=` | (셸이 직접) `actionList()` 후 class로 거름 | 아니오 |
| POST `/act/plans` | `/api/act/plans` | 아니오 |
| POST `/act/plans/by-ids` | `/api/act/plans/by-ids` | 아니오 |
| GET `/act/plans/<id>` | `/api/act/plans/<id>` | 아니오 |
| POST `/act/plans/<id>/approve` | `/api/act/plans/<id>/approve` | **예** |
| POST `/act/plans/<id>/execute` | `/api/act/plans/<id>/execute` | **예** |
| GET `/act/runs/<id>` | `/api/act/runs/<id>` | 아니오 |
| POST `/act/runs/<id>/compensate` | `/api/act/runs/<id>/compensate` | **예** |
- 헤더 없음 → 403 `승인·실행·취소는 앱 화면에서 사람이 눌러야 합니다.`; 백엔드 포트 없음 → 503 `액션 실행기에 연결되지 않았습니다.`; 연결 실패 → 502 `액션 실행기에 닿지 못했습니다: …`; 그 밖 404 `없는 액션 경로입니다.`
- 백엔드 쪽(`B/modules/kinetic/api.py:464-517`): `/api/act/*` 자체에는 브라우저 확인이 없다(웹 오리진 `/api/*` 프록시로 누구나 호출 가능). 계획 본문 `{class, action, where[], params{}}`(`api.py:57-72`), by-ids `{class, action, ids[], params{}}`, 승인 `{note}`, 보상 `{reason}`.

### 3.5 한 턴 실행기 (`R/code_app_turn.py`, 111줄)
- 에이전트 id: 환경 `EXTERNAL_AGENT_ID`(기본 claude-code), `cliagents.registry.resolve(…, Surface.TERMINAL)`로 실행 파일 찾기; 실패 시 `error` 후 exit 3.
- claude(47-50): `-p <prompt> --output-format stream-json --verbose --allowed-tools Read,Write,Edit,MultiEdit,Glob,Grep,Bash(curl:*),Bash(node --check:*) --permission-mode acceptEdits --setting-sources project --strict-mcp-config` + 첫 턴 `--session-id <uuid>` / 이후 `--resume <uuid>`. codex(42-45): `exec --skip-git-repo-check --full-auto -C <앱 폴더> <prompt>`(세션 안 이음, 텍스트 줄).
- cwd=앱 폴더, stdin 닫음, 20분 타이머 kill(22,56).
- 출력: 처음 `{"kind":"token","text":"","agent":<id>}`, `token{text}`, `tool_start{tool_call_id,name,args}`, `tool_result{tool_call_id,name,content(600자),is_error}`, `error{message}`, `usage{duration_ms,turns,cost_usd}`, 마지막 `final{text,exit_code}`. 종료 코드 0 또는 5.

### 3.6 SDK·런타임 (`R/codeapp/runtime/`)
- `og.js`(207줄): `query(cypher, params)` → `POST /codeapps/api/query`, 실패 시 `Error(out.error || "HTTP n")`; `schema()` → `GET /codeapps/api/schema`; `theme()`(localStorage `os-theme` → 없으면 시스템), `onTheme(fn)`(해제 함수 반환; `storage` 이벤트·시스템 테마 변경 감지, `<html data-theme>` 설정), `color(name)`(CSS 변수 `--og-<name>`); `actions(className?)`(오류면 빈 배열); `act(opts)`(106-206: 앱 문서에 DOM 대화상자 삽입, 상태 문구표 95-96, 계획 → `plans/by-ids`(ids 있음) 또는 `plans`(where), 승인(메모), 실행(허용 N건, 승인 필요 없고 planned면 바로 실행 가능), 실행·보상 중 1.2초 폴링, 취소(사유), 닫으면 `{executed, cancelled, plan, run}`).
- `og.css`(91줄): 낮/밤 토큰 `--og-bg, panel, raised, line, line-2, fg, dim, mute, accent, on-accent, blue, warn, danger, ok, purple, soft, shadow` + 액션 대화상자 스타일.
- `vue.js` = Vue 3.5.31(템플릿 컴파일러 포함, MIT), `echarts.min.js` = ECharts(Apache-2.0; 규칙 문서는 ECharts 6이라 함).
- 템플릿: `index.html`(og.css·style.css·echarts 로드, `#app`, `app.js` 모듈), `app.js`(「에이전트가 앱을 만들고 있습니다…」 자리표시), `style.css`(`.pending` 가운데 정렬).
- 규칙 `R/codeapp/AGENTS.md`(67줄) — 요지는 design.md §8.5.

### 3.7 프런트엔드 CodeAppView (F@2143942)
- 열 때 `GET /codeapps/api/apps/<id>` → SSE `events?from=0`. `done` 이벤트면 메타 다시 읽고 미리보기 새로 고침. `tool_result` 중 Write/Edit/MultiEdit면 0.6초 뒤 미리보기 새로 고침(`?v=<시각>`).
- 이전 턴은 요청+보고(간단 마크다운: `**굵게**`, `` `코드` ``만 HTML로, 나머지 이스케이프), 진행 턴은 이벤트 렌더. 경과 시간 1초 갱신.
- 「앱 탭으로 열기」: `window.liteShell.openTab({kind:'app', app:id, title})`, 없으면 `window.open('/apps/<id>/')`.
- 미리보기 iframe: `src=/apps/<id>/?v=…`, **sandbox 속성 없음**, 같은 오리진.

---

## 4. 홈 연계 (`E/renderer/shell/shell.js`)
- 카드 44: `{title:'온톨로지 앱', desc:'대시보드나 코드 앱을 말로 만듭니다.', target:{kind:'studio', view:'board'}}`; VIEW_LABEL 36 `board:'대시보드'`; 필터 「앱」 53.
- 최근 항목 219-243: `/api/board/dashboards` 항목 → 종류 「대시보드」, 이름 `title||name||id`, 정보 `schema_name||schema||''`(목록에 없음 → 빈 값), 대상 `{kind:'studio', view:'board'}`(특정 대시보드 아님); `/codeapps/api/apps` 항목 → 「코드 앱」, 정보 `에이전트 작업 중`/`수정 N회`, 대상 `{kind:'app', app:id, title:name}`.

## 5. 설정값 (환경 변수)
| 변수 | 기본 | 쓰는 곳 |
|---|---|---|
| `BOARD_MCP_TRANSPORT` / `BOARD_MCP_URL` | 셸이 `http` / `http://127.0.0.1:<mcp>/mcp` 강제 | `BD/settings.py`, `B/shared/kernel/mcp_client.py` |
| `BOARD_MCP_TIMEOUT` | 60초 | 같음 |
| `BOARD_MCP_SAMPLE_LIMIT` (옛 이름 `BOARD_SAMPLE_LIMIT`) | 50 | 물리 클래스 표본 수 (`BD/settings.py:33-44`) |
| `BOARD_STORAGE_DIR` | 없음 → 앱 패키지 안 `data/boards` | `BD/spec_store.py:34-38` |
| `MCP_ALLOW_DATASOURCE_EXPANSION` | 앱이 `true` | 가상 클래스 위젯 가능 여부(도구 목록으로 판정) |
| `AGENT_BACKEND`, `EXTERNAL_AGENT_ID` | 셸 결정값 | 편집·구성·코드 앱 에이전트 |
| `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `MAJOR_MODEL` | 빈 값 | 대시보드 내장/대체 경로 |
| `BACKEND_HOST`, `BACKEND_PORT` | 셸 | 브리지 MCP URL |

## 6. 시나리오 ↔ 흐름
| 시나리오 | 화면 → API → 백엔드 → 저장/외부 |
|---|---|
| S1 | BoardPanel `me` → board health/classes(MCP graph://schema) → act/actions(kinetic) → dashboards(파일 목록) + codeapps apps(폴더 목록) |
| S2 | AppMaker `make` → recommend(MCP 프로파일·추천) → widgets/query(MCP cypher/sql) → PUT(파일) → ask/stream(CLI ↔ 브리지 MCP 도구) → patch dry_run=false(파일) |
| S3 | Inspector → 메모리 수정 → widgets/query; 저장 → PUT |
| S4 | FilterBar → classes/values, filters/applicability, widgets/query(global_filters/selection, linkage) |
| S5 | gallery compose → POST compose(SSE, 프로파일·추천·에이전트 선택) → 파일 저장 → GET dashboards/{id} |
| S6 | ObjectPalette drop → recommend → widgets/query |
| S7 | PUT → export/superset |
| S8 | WidgetActions → /api/act/plans → approve/execute → runs 폴링 → compensate (kinetic, M2/M7) |
| S9 | GET/DELETE dashboards |
| S10–S11 | codeapps POST apps → POST turns → spawn code_app_turn.py → claude/codex(앱 폴더, curl → /codeapps/api/query·schema·act/actions) → SSE events → .app.json |
| S12 | GET file, 정적 /apps/<id>/ |
| S13 | liteShell.openTab → tabs.js app 탭(프리로드 없음) |
| S14 | og.js act() → /codeapps/api/act/* → /api/act/* |
| S15 | DELETE apps/<id>, stopAll, events 재생 |
| S16 | isWrite 403, sec-fetch-mode 403 |

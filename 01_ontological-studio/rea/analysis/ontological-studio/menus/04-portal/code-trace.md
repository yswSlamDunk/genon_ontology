# M4 Ontological Portal — 코드 추적 (원본 근거, 구현 세션에 넘기지 않음)

- 기준: 배포본 0.1.1. 정적 분석만(실행 안 함), 2026-10-31.
- 약어:
  - `SRV` = `shared/app/runtime/portal/server/index.js` (775줄)
  - `REL` = `shared/app/runtime/portal/server/release.js` (375줄)
  - `WEB` = `shared/app/runtime/portal/web/` (`index.html` 190, `app.js` 1041, `designer.js` 504, `release.js` 133, `benchmark.*`, `lite/lite-cypher.js` 178, `lite/lite-nl.js` 74, `lite/lite.css` 45)
  - `SH` = `extracted-app-asar/src/` (Electron 셸)
  - `EXT` = `shared/app/runtime/pg/lib/postgresql/ontological.dylib` (엔진 확장, 문자열만 확인)
  - `PKG` = `shared/app/runtime/portal/package.json` — 이름 `ontological-studio` 0.1.0, 설명 "Neo4j-Browser-style console for Ontological", 의존성 `pg ^8.13.0` 하나

## 0. 핵심 사실 요약
1. **포털 서버는 Bolt를 쓰지 않는다.** PostgreSQL에 직접 연결 풀(`pg.Pool`, max 8)을 두고 엔진 SQL 함수(`og_cypher` 등)를 호출한다 (SRV:34–42, 381–433). 튜토리얼 04장 그림("포털 ──Bolt──▶ DB")과 다르다 → 배포본이 우선(ADR-0003).
2. 포털 서버의 DB 인증 = 셸이 넘긴 환경 변수 `PGUSER=og`(슈퍼유저)·`PGPASSWORD=<secrets.json의 pgPassword>`, DB `ogstudio` (SH main/services.js:22–31, main/postgres.js:14–16,22). 포털 HTTP 자체엔 인증이 없다(루프백 바인드 + 동일 출처 검사만).
3. Bolt는 **자연어→Cypher**에서만 쓰인다: 메인 프로세스의 neo4j 드라이버가 `bolt://127.0.0.1:<bolt>`에 basic 인증(`og` / pgPassword)으로 붙어 스키마 보강(`SHOW VIRTUAL …`)과 시험 실행을 한다 (SH main/index.js:143, main/nl2cypher.js:107–142). Bolt 게이트웨이는 PG 접속 비밀번호 환경 변수를 받지 않으므로(SH services.js:9–19) HELLO의 자격 증명으로 PG에 로그인하는 것으로 **추정**(바이너리에 SCRAM·`principal`/`credentials` 문자열 존재).
4. 패브릭 문장(`SHOW DATASOURCES`, `SHOW TABLES FROM`, `EXPLAIN FABRIC`, `CREATE GRAPH`, `CREATE/DROP VIRTUAL …` 등)은 포털이 따로 처리하지 않고 `og_cypher`로 그대로 보낸다 → 엔진 확장 내부(`fabric::sqlish`)가 처리 (EXT 문자열: `not a fabric statement`, `expected NODES or RELATIONSHIPS after SHOW VIRTUAL`, 토큰 `CREATE REFRESH MATERIALIZE EXPLAIN FABRIC DATASOURCE DATASOURCES TABLES COLUMNS VIRTUAL GRAPHS USE`, 감사 기록 `lang='fabric'`).
5. 앱 안에서 기본으로 **꺼진** 기능: raw SQL(`:sql`, 검사기 history 버튼) — `OG_STUDIO_ALLOW_RAW_SQL` 미설정(SRV:30, 660–677); 스키마 AI assist — `OPENAI_API_KEY`가 포털 프로세스 환경에 없음(셸은 studio.env를 process.env에 넣지 않음; SH services.js:22–31은 `...process.env`만 전달) → 앱을 터미널에서 키를 export한 채 띄운 경우만 켜짐(추정).

## 1. 기동·여는 경로

| 항목 | 근거 |
|---|---|
| 부팅 순서에서 Bolt와 포털 병렬 기동 | SH main/index.js:142 `Promise.all([startBolt, startPortal])` |
| 포털 프로세스: Electron 실행 파일을 Node로(`ELECTRON_RUN_AS_NODE=1`) `server/index.js` 실행, cwd=포털 폴더, env `PORT`, `OG_STUDIO_HOST=127.0.0.1`, `PGHOST=127.0.0.1`, `PGPORT`, `PGDATABASE=ogstudio`, `PGUSER=og`, `PGPASSWORD` | SH main/services.js:22–29 |
| 준비 판정: `GET /api/health` HTTP 응답, 30초 제한 | SH main/services.js:31 |
| 포트 선호값 portal 27474(사용 중이면 다른 포트), 환경 변수 `ONTOLOGY_LITE_PORTAL_PORT`로 지정 가능 | SH main/ports.js:17,24 |
| 종료: 포털·Bolt 5초 안에 정지 | SH main/index.js:352 |
| 홈 카드 `{kind:'portal'}` → 탭 열기 | SH renderer/shell/shell.js:43, 137–143, 64–67 |
| 홈 사이드 빠른 링크 「Ontological Portal」 | SH renderer/shell/shell.js:150, 164 |
| 트레이 메뉴 「Ontological Portal 탭」 | SH main/tray.js:34 |
| 메뉴바 런타임 › 포털 탭 열기 / 브라우저에서 열기 | SH main/index.js:326–327 |
| `liteShell.open('portal')` → 시스템 브라우저 `http://127.0.0.1:<portal>/` | SH main/index.js:275 |
| 탭 URL, 탭 제목 고정 "Ontological Portal"(페이지 제목 무시) | SH main/tabs.js:21, 29, 103–106 |
| 포털 탭에도 preload(`liteShell`) 부여 — `app` 종류 탭만 제외 | SH main/tabs.js:89 |
| 포털/Studio 이외 URL로 이동 시 외부 브라우저 | SH main/tabs.js:111 |
| 포털 URL로 새 창 요청 → 포털 탭으로 | SH main/tabs.js:68 |
| Studio SPA 「Ontological Portal」 뷰 = iframe(`OntologicalPortalPanel`), `/app/portal-info`로 URL·그래프를 받고 `/api/health`를 no-cors로 확인 | 번들 `index-Bnym06ph.js`(문자열 `OntologicalPortalPanel`, `/app/portal-info`), SH main/web.js:67 |
| preload 주석: iframe 안 포털은 아무 브리지도 못 받음 | SH preload/index.js:2–4 |

## 2. 서버 공통 (SRV)

| 항목 | 근거 |
|---|---|
| 기본 포트 7474(단독 실행 시), 바인드 기본 127.0.0.1; 루프백이 아니면 `OG_STUDIO_ALLOW_REMOTE=1` 없이는 거부·종료 | SRV:18–26, 749–756 |
| PG 접속 기본값(단독): localhost:28816/og, user dev | SRV:34–42 |
| 풀 오류 시 로그만 남기고 계속 | SRV:48–50 |
| `/api/*` 동일 출처 검사: `Sec-Fetch-Site`가 same-origin/none이 아니면 403, `Origin` 호스트가 `Host`와 다르면 403. 헤더 둘 다 없으면 통과(curl 허용) | SRV:67–79, 720–723 |
| GET/HEAD 외에는 `Content-Type: application/json` 필수, 아니면 415 | SRV:88–91, 724–726 |
| 본문 상한 `OG_STUDIO_MAX_BODY`(기본 64MB), 바이트 모아 한 번에 UTF-8 디코드 | SRV:110–133 |
| 오류 응답 형식 `{error, code, detail, hint, where}` (PG 오류 필드) | SRV:136–144 |
| 라우트 표 조회 `"<METHOD> <path>"`, 예외 500 `{error}` | SRV:716–736 |
| 정적 파일: `/`→index.html, 경로 정규화 후 web 폴더 밖이면 404, MIME 표 | SRV:93–99, 738–747 |
| 시작 로그 문구, raw SQL 켜짐 경고 | SRV:758–771 |

## 3. API 목록 (SRV + REL)

| 메서드·경로 | 요청 | 엔진 호출 | 응답 | 근거 |
|---|---|---|---|---|
| GET `/api/health` | — | `ontological_version()`, `current_database()`, `version()`, 그래프 목록(카탈로그 graph 표, 이름순) | 200 `{ok:true, version, database, server, graphs:[{name, graph_id}]}` / 503 `{ok:false, …pgError}` | SRV:350–364 |
| GET `/api/schema?graph=` | graph 기본 `default` | `og_schema(graph)`, `og_graph_stats(graph)` | `{schema, stats}` | SRV:367–378 |
| POST `/api/cypher` | `{graph, query, params:{}, at:{valid_at?, system_at?}}` | 연결 하나 확보 → `set_config('og.valid_at'/'og.system_at', v, false)` → `og_cypher(graph, query, params_json)` (행마다 jsonb 한 개) → `og_cypher_columns(query)` → `og_cypher_sql(graph, query)`(쓰기면 실패→null) → finally `RESET og.valid_at; RESET og.system_at` | `{rows, columns, elapsed_ms, compiled_sql, sql_fingerprint(md5 앞 12자), at(설정한 것 or null), graph:{nodes, edges}}` / 400 `{…pgError, elapsed_ms}`; 빈 질의 400 `{error:'empty query'}` | SRV:381–433, 300–309 |
| GET `/api/temporal?graph=` | | `og_temporal_types(graph)`; 감사 표에서 오류 없고 쓰기 키워드(CREATE/SET/DELETE/MERGE/REMOVE) 포함한 최근 30건 `at, actor, source, query` — **그래프 필터 없음** | `{types, writes}` | SRV:439–452 |
| POST `/api/schema-type` | `{graph, name, parents[], kind:'entity'|'relation'}` | `og_create_type(graph, name, kind, parents)` | `{type_id, name, kind, parents, elapsed_ms}`; 이름이 식별자가 아니면 400 | SRV:458–470 |
| POST `/api/schema-assist` | `{graph, prompt}` | `og_schema_snapshot(graph)` → 카탈로그 요약 → OpenAI Responses API(`OG_STUDIO_LLM_MODEL` 기본 `gpt-4.1`, JSON 객체 형식) → 변경 검사 | `{explanation, changes:[{change, ok, problem}], model, elapsed_ms}`; 키 없으면 503 `AI assist is off — start the server with OPENAI_API_KEY`; 모델 오류 502 | SRV:212–297, 480–505 |
| GET `/api/schema-changes?graph=` | | `og_schema_changes(graph)` 최신순 | `[{change_id, kind, phase, spec, report, created_at, updated_at}]` | SRV:508–518 |
| GET `/api/schema-snapshot?graph=&version=&at=` | | `og_schema_snapshot(graph, version, at)` | 스냅샷 객체(`version`, `description`, `types:[{name, kind, parents, properties:{name:{type, column, required, key}}, temporal, abstract}]`) | SRV:521–532 |
| POST `/api/schema-change` | `{graph, action: plan|apply|expand|migrate|validate|contract|abort, change, change_id, batch=10000}` | plan→`og_schema_plan`, apply→`og_schema_apply`, 나머지 `og_schema_<action>(id[, batch])`; plan 직전 트랜잭션 id 기록해 "그 후 다시 쓰인 행 수" 계산 | `{change_id, action, phase, report, elapsed_ms, storage:{rows, written, tables}}` | SRV:299–337, 541–574 |
| POST `/api/explain` | `{graph, query, analyze=false}` | `og_cypher_explain(graph, query, analyze)` | 엔진 결과(`sql`, `plan`, `columns`) | SRV:577–589 |
| POST `/api/diagnose` | `{graph, query}` | `og_explain_error`, `og_diagnose_empty`, `og_estimate` 병렬 | `{error, empty, estimate}` | SRV:592–612 |
| POST `/api/expand` | `{id, limit=50}` | `og_expand(id, NULL, 'o')` / `'i'` 각 LIMIT, `og_node_json`, `og_edge_json` — **graph 인자 없음** | `{nodes, edges}` | SRV:615–639 |
| GET `/api/audit` | | 감사 표 최근 100건 (`audit_id, principal, at, query, lang, rows_out, duration_ms, error_code`) — 전역 | 배열 | SRV:642–652 |
| POST `/api/sql` | `{sql}` | 그대로 실행 | `{rows, columns, rowCount}`; 꺼져 있으면 403 | SRV:660–677 |
| GET `/api/benchmark` | | 파일 시스템 `OG_BENCH_DIR`(기본 `../../bench/results`, 배포본엔 없음) | `{scales, source}` | SRV:155–207, 341–347 |
| POST `/api/schema-temporal` | `{graph, type}` | `og_enable_temporal` | `{type, temporal:true}` — **UI에서 호출 안 함** | REL:302–308 |
| POST `/api/schema-diff` | `{graph, snapshot, hints[]}` | `og_schema_diff` | `{changes}` — UI 미사용 | REL:311–317 |
| POST `/api/release/export` | `{graph, keys:{Type:prop}, name, origin}` | 스냅샷·변경 기록·타입별 키·`og_timeline` 슬라이스·관계는 `og_cypher`로 `MATCH (a)-[r:T]->(b) RETURN id(a), id(b)` | `{package, skipped, counts:{types, instances, slices, edges}}` — UI 미사용 | REL:70–123, 320–328 |
| POST `/api/release/plan` | `{graph, package}` | `og_schema_diff`, 인스턴스별 `og_timeline` 비교, `og_releases`에서 같은 hash applied 검색 | `{schema, instances:{create, update, same, slices, items}, edges, hash_ok, already_applied}` | REL:143–169, 331–339 |
| POST `/api/release/apply` | `{graph, package, actor}` | hash 재계산 검증 → `og_release_begin` → 스키마 변경 단계 실행(drop_property는 건너뜀) → 인스턴스 슬라이스별 쓰기(트랜잭션마다 `og.valid_from/valid_to/source=release:<id>/actor`) → 관계 생성 → `og_release_commit` (실패 시 실패 기록) | `{release, plan, log, elapsed_ms}` / 400 `{…, release_id, log, samples}` | REL:171–298, 342–351 |
| GET `/api/releases?graph=` | | `og_releases(graph)` | 배열 | REL:354–359 |
| GET `/api/timeline?graph&type&key_prop&key&from&to&system_at` | | `og_timeline(...)` | `{slices:[{type_name, id, valid_from, valid_to, props, recorded_at, superseded_at, source, actor, op}]}` | REL:362–371 |

### 그래프 투영 (Graph 보기용)
- 행 값을 재귀로 훑어 `_id`가 있으면 노드, `_src`·`_dst`까지 있으면 관계. 양 끝이 화면에 있는 관계만 남김. SRV:686–711.
- 노드·관계 JSON 형태: `{_id, _type, (_src, _dst), …속성}` (WEB app.js:253–268 `renderValue`, 637–667 검사기에서 확인).

### 스키마 AI assist 프롬프트·검사 (SRV:212–297)
- 시스템 지시: 요청을 스키마 변경 JSON 하나로 바꾸라 — `{explanation, changes[]}`, 허용 변경 9종(`create_type`, `rename_property`, `rename_type`, `add_parent`, `remove_parent`, `drop_property`, `alter_property_type`, `set_required`, `add_property`)과 각 필드, 규칙(속성은 선언한 타입에서만 변경, 중간 타입 끼우기 순서, 기존 이름 그대로, 새 이름은 식별자, 불가능하면 빈 변경+이유), 끝에 현재 카탈로그 텍스트(타입 [entity/relation] extends … (temporal): `prop:type (declared)`).
- 서버 검사: 변경을 순서대로 가상 적용하며 종류·타입 존재·선언 여부·식별자·부모 존재를 확인하고 `{change, ok, problem}`로 표시.

### 릴리스 패키지 형식 (REL:13–24, 31–44, 119–121)
- `{format:'og-release/1', name, origin, graph, created_at, schema_version, snapshot, changes, instances:[{type, key_prop, key, slices:[{valid_from, valid_to, props, source}]}], edges:[{type, from:{type,key_prop,key}, to:{…}}], hash}`
- hash = `sha256:` + SHA-256(정렬된 키의 정규 JSON `{types, instances, edges}`) — name·created_at·버전 제외.
- 키 속성: 요청 `keys` > 스냅샷에서 `key` 표시된 속성 > 부모의 키. 추상·관계 타입 제외, 키 없는 타입은 skipped.

## 4. 프런트엔드 (WEB)

| 기능 | 근거 |
|---|---|
| 화면 골격: 레일(schema·saved·audit·evolve·help 패널 버튼 + benchmark 링크 + 연결 점), 사이드바 패널 5개, 입력칸·⏱·▶, 시간 막대, 결과 스트림, 디자이너 영역, 검사기 | WEB index.html:13–182 |
| 상태: graph, schema, stats, saved(localStorage `og.saved`), history(`og.history`), at, params(메모리만) | app.js:13–25 |
| 라벨 색: 10색 팔레트, 이름 해시 | app.js:27–40 |
| fetch 래퍼 (본문 있으면 JSON 헤더) | app.js:44–52 |
| 시작: health → 그래프 목록(localStorage `og.graph` 또는 첫 그래프) → schema 칩/계층 → temporal, evo | app.js:56–76, 78–113, 1040 |
| 칩: 라벨 `MATCH (n:T) RETURN n LIMIT 50`, 관계 `MATCH (a)-[r:T]->(b) RETURN a, r, b LIMIT 50`, 계층 들여쓰기 | app.js:85–144 |
| 질의 기록 패널(`/api/audit`, 앞의 `[...]` 접두 제거) | app.js:146–161 |
| 결과 카드: 시점 배지, 질의 텍스트, 탭, ★ 저장(최대 50, 중복 제외), ✕ | app.js:178–203 |
| 표 보기, 값 렌더(노드는 `(타입) {props}`) | app.js:234–268 |
| 오류 보기: 메시지의 `did you mean: a, b` 후보를 칩으로, 누르면 따옴표 속 틀린 이름을 치환해 재실행 | app.js:286–318 |
| Graph 보기: 범례, 캔버스 힘 기반 배치, 맞춤·멈춤, 캡션 우선순위 name/title/label/model/id, 클릭→검사기, 더블클릭→`/api/expand`(limit 40) | app.js:320–635 |
| 검사기: expand neighbours(Cypher), history(`:sql SELECT * FROM og_history(id)`) | app.js:637–667 |
| `:param`/`:params`/`:params clear` (JSON 파싱, 아니면 따옴표 하나 제거한 문자열, 히스토리 제외) | app.js:675–703 |
| 실행 분기: `:clear`, `:sql`, `:explain`, `:why`, `:schema`, `:changes`, `:snapshot`, `:releases`, `:timeline`, 나머지 `/api/cypher`. 히스토리 최대 100. 성공 후 loadSchema·loadAudit 갱신 | app.js:705–770 |
| 결과 탭 순서 Graph(노드 있을 때)·Table·JSON·SQL(compiled_sql 있을 때), 상태줄 | app.js:745–769 |
| `:explain`→SQL·Plan, `:why`→Compile check·Pattern walk·Estimate, `:changes`, `:snapshot [숫자=version | 문자열=at]`, `:schema`→Schema·Storage | app.js:788–882 |
| 시간 여행: at 구성, 배지 `⏱ valid … · known …`, 입력칸 `asof` 클래스, 「as known at」 옵션 = 감사 쓰기 시각(`after HH:MM:SS.mmm · actor — 질의 54자`), 안내 문구 | app.js:902–938, 1002–1017 |
| 키: ⌘/Ctrl+Enter 실행, 한 줄일 때 ↑/↓ 히스토리 | app.js:956–976 |
| 그래프 바꾸기: 저장 후 schema·temporal·evo·디자이너 다시 읽기 | app.js:993–1000 |
| `data-run` 요소 클릭 = 즉시 실행 | app.js:1023–1038 |
| 디자이너: 스냅샷+통계로 지도, 쌓은 변경 가상 적용·표시, 트리 배치, 카드·속성 행, plan 목록, review(=plan 호출), run(create_type은 `/api/schema-type`, 나머지 plan→expand→(다시 쓰는 종류면 migrate 반복)→validate→contract), blocked/Retry/Abort, AI 요청, 메뉴, 끌어 놓기, Clear 시 미완료 변경 abort | designer.js 전체 (37–79, 81–111, 141–184, 186–197, 218–251, 263–357, 359–374, 405–459, 474–503) |
| 다시 쓰는 종류(REWRITES) = alter_property_type, set_required, add_property; batch 입력 기본 100000 | designer.js:216; index.html:86 |
| `:releases` 표 / `:timeline <Type> <prop>=<key> [from] [to] [@system_at]` 막대·표 | release.js:19–133 |
| 자동완성·문법 색(키워드·함수 목록, `/api/schema`로 라벨·관계·속성, `_`로 시작하는 이름 숨김, 600ms 뒤 첫 로드) | lite/lite-cypher.js:14–28, 30–50, 61–90, 98–177 |
| 자연어: `liteShell.nl2cypher` 있을 때만 활성. 질문 판정 = 주석 제거 후 `:`·`(`로 시작하지 않고 Cypher 키워드로 시작하지 않음. ▶/⌘Enter를 캡처 단계에서 가로채 번역, ⇧⌘Enter·✨는 강제 번역. 결과에 따라 ok/warn/bad 막대, ok면 우회 플래그 세우고 ▶ 자동 클릭 | lite/lite-nl.js:8–74 |

## 5. 자연어 → Cypher (셸)

| 단계 | 근거 |
|---|---|
| preload `liteShell.nl2cypher(question, graph)` → IPC `lite:nl2cypher` `{question, graph}` | SH preload/index.js:17–18 |
| 핸들러: 부팅 완료 전이면 "아직 시작하는 중입니다.", 번역 후 로그 `nl2cypher <graph>: N ms (고침 1회) — 실패: …` | SH main/index.js:287–302 |
| 에이전트 호출 = `runStudioScript(agent_turn.py, stdin JSON {system, user})`, Python 자식 프로세스, cwd=userData, 5분 타임아웃, maxBuffer 16MB | SH main/index.js:293–294, main/services.js:189–199 |
| `agent_turn.py`: `EXTERNAL_AGENT_ID`(기본 claude-code)로 cliagents 해석, 프롬프트=`system + "\n\n---\n\n" + user`, Claude Code는 `-p <prompt> --output-format text --allowed-tools ""`(도구 없음), Codex는 `exec --skip-git-repo-check <prompt>`, 빈 임시 폴더에서 180초 제한, 종료 코드 3/4/5 | `shared/app/resources/agent_turn.py`:19–48 |
| 입력 검사: 질문 비면 "질문이 비어 있습니다.", 그래프 이름 `^[a-z_][a-z0-9_]*$`(대소문자 무시) 아니면 "그래프를 고르세요.", 에이전트 backend가 cliagents 아니면 "자연어 → Cypher 는 CLI 에이전트(Claude Code · Codex)로 동작합니다. 메뉴 「런타임 › 에이전트」에서 고르세요." | SH main/nl2cypher.js:64–72 |
| 스키마: 포털 `GET /api/schema?graph=` (HTTP, 실패 시 "그래프 X 의 스키마를 읽지 못했습니다 (status)"), 압축(내부 `_` 타입·`_source_id`, `_parent_source_id`, `created_at`, `updated_at`, `embedding` 속성 제외 → `{node_types:[{label, extends?, properties:["name:type"]}], relationship_types:[{type, from?, to?}]}`), 노드 타입 0개면 오류 | SH main/nl2cypher.js:14–15, 37–51, 74–77 |
| 보강(Bolt 세션, database=graph): `SHOW VIRTUAL RELATIONSHIPS IN g` → 관계 from/to 타입과 `join: "A.x = B.y"`; `SHOW VIRTUAL NODES IN g` → 노드 `source`; 끝점 미상 저장 관계는 `MATCH (a)-[r:T]->(b) RETURN labels(a), labels(b) LIMIT 1`; 오류는 무시 | SH main/nl2cypher.js:107–128 |
| 시스템 프롬프트(요지): Ontological DB용 Cypher 한 문장, ```cypher 블록 + 한국어 한 줄 설명만; 스키마의 라벨·관계·방향·속성만; 허용 절(MATCH, OPTIONAL MATCH, WHERE, WITH, RETURN, ORDER BY, SKIP, LIMIT, UNWIND, DISTINCT, 집계), 허용 함수 34개만(head/last/nodes/리스트·패턴 내포/CASE/APOC/db.* 금지); 모든 노드에 라벨; 관계 방향 준수; WHERE 라벨 조건 금지; 문자열 비교 연산 한정·대소문자 구분; 명시 요청 없으면 읽기 전용; 이름 붙은 컬럼 반환; 큰 결과면 LIMIT 100 | SH main/nl2cypher.js:10–12, 17–35 |
| 사용자 메시지: `Schema (JSON):\n<압축 스키마>\n\nQuestion: <질문>` | SH main/nl2cypher.js:80 |
| 응답 추출: 첫 ```cypher/```sql/``` 블록(없으면 전체), 끝 `;` 제거, 블록 뒤 첫 줄 = note | SH main/nl2cypher.js:53–58 |
| 쓰기 판정: 따옴표 문자열 제거 후 `CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|REFRESH|ALTER|GRANT|REVOKE|LOAD|FOREACH` 단어 → 시험 실행 안 함 | SH main/nl2cypher.js:13, 84 |
| 시험 실행: Bolt READ 세션으로 1회 실행(행 버림), 20초 넘으면 컴파일된 것으로 보고 성공 처리, 오류 메시지는 `ERROR:` 이후 400자 | SH main/nl2cypher.js:131–142 |
| 수리 1회: 사용자 메시지 + "이 질의가 실패했다 / 질의 / 오류 / 고쳐라, 같은 형식" → 재추출 → 재시험; 또 실패면 `error` 포함 반환(checked=false) | SH main/nl2cypher.js:87–97 |
| 반환: `{cypher, note, agent(라벨), ms, repaired, checked, write}` (+`error`) | SH main/nl2cypher.js:94, 98 |

## 6. 저장 위치·설정값

| 항목 | 값/위치 |
|---|---|
| 브라우저 저장소(포털 출처별) | `og.saved`(최대 50), `og.history`(최대 100), `og.graph` |
| 메모리만 | `:param` 값, 시간 여행 선택, 디자이너 plan |
| DB(엔진 소유) | 감사 표(`og_data.og_audit`), 스키마 변경 기록, 릴리스 기록, 이력(`og_history`), 카탈로그 |
| 포털 환경 변수 | `PORT`, `OG_STUDIO_HOST`, `OG_STUDIO_ALLOW_REMOTE`, `OG_STUDIO_ALLOW_RAW_SQL`, `OG_STUDIO_MAX_BODY`, `OG_BENCH_DIR`, `OPENAI_API_KEY`, `OG_STUDIO_LLM_MODEL`, `PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD` |
| 셸 쪽 | `ports.json`(portal 포트), `secrets.json`(pgPassword), `ONTOLOGY_LITE_PORTAL_PORT` |
| 다른 모듈의 포털 참조 | Studio 백엔드 env `ONTOLOGICAL_ADMIN_DEV_URL=http://127.0.0.1:<portal>` (SH services.js:128) → 백엔드 `modules/ontological_admin/client.py`(기본 7481) — M1/M6 등에서 포털 관리 API를 부르는 것으로 추정, 해당 메뉴에서 확인 |

## 7. 튜토리얼과의 차이·충돌
- 04장: 포털이 Bolt로 DB 접근 → 실제는 PG 직결(SQL 함수). Bolt는 NL 기능만.
- 07장·치트시트: `CASE` 사용 가능(실측 결과 있음) ↔ NL 시스템 프롬프트는 CASE 금지. 프롬프트가 보수적인 것(모순 아님, 기록만).
- 07장 함수 표에 `vector.similarity`·`vector.distance`·`genai.vector.encode` 있음 ↔ 포털 자동완성·NL 프롬프트의 함수 목록엔 없음.
- 09장 "시계 아이콘 목록에는 이 그래프에서 최근 쓰기" ↔ 코드상 감사 쿼리에 그래프 필터 없음(전역 최근 30건).
- 10장: 시간 버전 켜기는 "SQL 세션에서" ↔ 서버에 `POST /api/schema-temporal`이 있으나 UI 미연결.

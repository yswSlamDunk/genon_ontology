# M1 온톨로지 구축 — 코드 추적 (원본 근거, 구현 세션에 넘기지 않음)

- 기준: 배포본 0.1.1, 정적 분석만(실행 안 함), 2026-10-31~11-01.
- 약어
  - `A` = `shared/app/runtime/studio/app/backend/src/`
  - `SK` = `shared/app/runtime/studio/app/skills/`
  - `FE` = `shared/app/runtime/frontend/assets/index-Bnym06ph.js` (압축 번들 — **바이트 오프셋**으로 표기, `grep -bo`)
  - `E` = `extracted-app-asar/src/`
  - `R` = `shared/app/resources/`
- 에이전트 실행 계약(CLI 명령줄, 브리지 MCP, SSE 기본 이벤트)은 A3(`common/A3-agent-mcp/code-trace.md`)를 따른다. 시스템 레지스트리·실행기는 M7.

## 0. 핵심 결론 (요약)
1. **스키마 원천 = SQLite(`<userData>/sessions.db`)**. 스키마 그룹·클래스·관계·바인딩·behavior·액션·출처·인과 가설이 여기 있다. 그래프(`ontology`)에는 (a) 인스턴스 노드 `:_Entity:<Class>`와 관계, (b) **발행** 시에만 `_Ontology*` 레지스트리 노드와 `ont_pub_*` 제약이 쓰인다 (`A/modules/agent_session/session_store.py:391-602`, `A/modules/ontology/publish.py:1-60`).
2. **액션 정의는 M1에서 만든다** — 두 경로: (a) 구축 에이전트 도구 `action_create`(build 브리지 전용), (b) 정보 탭 ⛁ → `DataSourceBindingPanel` → 「액션」 탭 `ClassActionsPanel`(REST `PUT /api/schema/classes/{c}/actions/{a}`). act 모드 도구에는 정의 도구가 없다(A3 §6.1). 단 오른쪽 패널은 질의·액션 화면에도 같은 컴포넌트로 뜨므로 편집기는 거기서도 열린다 (`FE` 2316704 부근 AppShell 템플릿).
3. 화면에 발행 버튼 없음. 발행은 에이전트 도구 `schema_publish` 또는 미사용 REST `POST /api/schema/{id}/publish`.
4. 문서 인덱싱(OCR·청크·하이브리드 검색) 모듈은 구축 흐름에 연결되지 않음(호출자 없음). 프런트의 `preprocess_*` 수신기는 잔재.
5. 데이터소스 바인딩 behavior·쿼리 미리보기·뷰는 `TEXT2SQL_BASE_URL/text2sql/direct-sql` 또는 `DATAFABRIC_BASE_URL/api/query`로 가는데, 두 주소 모두 셸 패브릭 브리지이고 브리지는 임의 SQL을 501로 거절 → 이 패키지에서 패턴 D(가상 클래스+SQL behavior) 경로는 실패할 가능성이 높다 (`A/modules/ontology/datasource_exec.py:559, 762`, `E/main/fabric-bridge.js:12, 245`, `E/main/services.js:136`).

## 1. 화면 구성 (프런트)
| 요소 | 근거 |
|---|---|
| 뷰 목록 `Nt`: build/act/board/quality/datasources/systems/browser, `?view=`·`?session=` 쿼리 처리 | FE AppShell(2302018~) setup |
| 대화형 뷰(build/act/answer)는 같은 레이아웃: 사이드바(모드별 세션 목록) + main(브리프 또는 ChatPanel) + 오른쪽 패널 | FE 2316704 주변 |
| main: `mode==='build' && messages.length===0` → `OntologyBuildBriefPanel`, 아니면 `ChatPanel` | 같은 위치 |
| 오른쪽 탭 graph/info/release/review, 검수 배지 = `to_review+held` | 같은 위치 |
| info 탭 구성: TodoPanel → OntologySchemaPanel → (선택 클래스) DataSourceBindingPanel → (스키마 선택+데이터소스 스키마 선택 시) BindingCandidatePanel(역바인딩), CausalEdgeReviewPanel → ContextPanel | 같은 위치 |
| 사이드바 하단: FilePanel, FileViewer(md/txt/csv/json/sql/yaml는 미리보기), 「초기화」(샌드박스 / Ontological 데이터) | AppShell `pn()` |
| 컴포넌트 오프셋: GoldenQuestionReviewPanel 172757, KineticPlanCard 176010, ChatPanel 229793, BindingCandidatePanel 241693, CausalEdgeReviewPanel 246810, ClassActionsPanel 253476, DataSourceBindingPanel 274921, FilePanel 290429, ReleasePanel 294444, OntologyBuildBriefPanel 305099, OntologyGraphPanel 759073, BuildReviewPanel 2201450, OntologySchemaPanel 2258808, AppShell 2302018 | `grep -bo '__name:'` |

### 1.1 워크스페이스 스토어 (`h$e`, FE ~2273500–2300300)
- 모드 메타 `J9`(build/answer/act 라벨·설명·placeholder·예시), 기본 프롬프트 `c$e`(「업로드된 문서를 바탕으로 Golden Question에 답할 수 있는 온톨로지를 구축해줘.」, 2270541), 피드백 프롬프트 `l$e`.
- 칩 분류 목록 `u$e`(ONTOLOGICAL), `d$e`(DATA).
- 브리프 상태 `{intent, goldenQuestions[''], goldenCommands[''], datasources[], systems[]}`.
- 세션 id 초기값 `default`(2273914); 모드 전환 시 `pending_<ts>` → 첫 업로드·전송 때 `POST /api/sessions?title=새 대화&mode=&schema_name=`.
- 초안 `ot()`(2282508): 900ms 디바운스(`at()`), 문서·데이터소스 없으면 생략, 의도와 질문이 모두 사용자 입력이면 생략(force 제외), `POST /api/build-brief/draft {datasources, documents, target_schema, intent, golden_questions}`; 빈 칸만 채우고 draft 표식.
- `st()`(2284679): build_context = `{intent, golden_questions, review_feedback, golden_commands?, systems?, documents?, datasources?, target_schema | new_schema_name}`.
- `Bt()`(2291824): `EventSource(/api/stream?prompt&session_id&mode&build_context)`; 처리 이벤트: token, tool_start, tool_result, kinetic_plan, kinetic_run, neo4j_update(→스키마·그래프 재조회), datasource_update, schema_created(→세션 PATCH schema_name), traversed_nodes, preprocess_progress/complete, todos, skill_loaded, ref_file, status, node_update, steered, ask_user, done(→build_report 파싱 `m$e`, 메시지 PUT 저장, 첫 메시지면 제목 PATCH, 전체 갱신), error_event(「\n오류: …」).
- `Wt()`(2295588): 스트리밍 중이면 steer, build 첫 턴은 브리프 준비(`ie` = 의도+질문≥1+소스≥1) 필요, 대상/새 이름 있으면 `It()`로 `PUT /api/schemas/{id}/brief`(기존 스키마일 때만).
- `V()`(2296560): 피드백 재구축 — `prompt=l$e`, buildContext에 review_feedback.
- `Ft()`(2290396): 대상 스키마 선택 시 그 스키마의 intent/질문/커맨드로 브리프 채움.
- `Gt()` 중단: EventSource 닫고 「[중단됨] "계속해"를 입력하면 이어서 진행합니다.」 (서버 프로세스 정리는 A3: 클라이언트 끊김 시).
- 메시지 저장: `PUT /api/sessions/{id}/messages?mode=` (화면 상태 JSON 그대로).

### 1.2 브리프 패널 (FE 305099)
- 단계 `[{1,'소스'},{2,'대상'},{3,'의도'}]`, 완료 판정·요약 문자열, 전략 라벨 맵(306812): doc_reverse_bind/causal_discovery/catalog_schema/document_only/none.
- 시스템 목록: 마운트 시 `co().listSystems()` → `GET /api/act/systems`, 칩 `API n`(operations_count).
- 권장 전략: 업로드 수·데이터소스·의도 변화마다 `GET /api/build-strategy/recommend?has_documents&datasource&schema&intent&max_lag=2`(첫 선택 스키마만).
- 「테이블 구조로 바로 생성」: `POST /api/schema/generate-from-catalog {datasource, source_schema, schema_name?, dry_run}`.
- 질문 파일 불러오기: 텍스트 줄 단위(FileReader).

### 1.3 ChatPanel·보고서
- 도구 칩 분류 DATA/ONTOLOGICAL/TOOL, `execute`는 command 원문 표시 (FE 229793~).
- 보고서: `GoldenQuestionReviewPanel`(맞다/틀리다/피드백/「피드백 반영 요청」, 173304), Golden Command 표(238067), 검수 현황 줄과 「검수 탭에서 보기」(`open-review` → 검수 탭).
- kinetic_plan/run 이벤트는 KineticPlanCard 렌더(M2 공용).

### 1.4 ClassActionsPanel (FE 253476, dry-run 버튼 272904)
- 연산자 목록 `= != > >= < <= in contains starts_with is_null not_null`.
- 새 액션 기본: 단계 `main` 1개, parameters `{"type":"object","properties":{}}`, effect write, confirm_threshold 0, max_targets 50.
- operation 선택 시 인자 자동 채움 규칙(기본값 제안) — 본문 배열 속성은 `body.<arr>.0.<필드>`.
- 저장 `saveAction` → `PUT /api/schema/classes/{c}/actions/{a}` (118408 `co()` 클라이언트), 목록 `GET …/actions`, 삭제 `DELETE`, dry-run `POST /api/act/plans {class, action, where, params}` → KineticPlanCard(승인·실행 버튼 포함, 스튜디오 토큰 신원).
- 실행기 상태 `GET /api/act/health`: 불통/토큰 미설정 경고.

### 1.5 기타
- OntologyGraphPanel: 보기 schema/entity, 배치 cose/circle/concentric/breadthfirst/grid(759904), API `/api/graph?…`, `/api/graph/search`, `/api/graph/nl-query`, `/api/graph/neighbors`, `/api/graph/entities`(POST/PATCH/DELETE), `/api/graph/relationships`.
- OntologySchemaPanel: 속성 타입 목록 string/integer/float/boolean/date/list, ⛁ `open-binding`, ✎, 삭제 확인 문구.
- BuildReviewPanel: `GET /api/schemas/{id}`, `/api/quality/review-status?schema_id=`, `/api/quality/policy/{id}` (M6).
- ReleasePanel: `/api/release/overview|export|plan|apply`.
- 스키마 삭제(`un`): 엔티티 삭제 후 `DELETE /api/schemas/{id}` — **발행 레지스트리는 거두지 않음**.

## 2. 백엔드 API (M1이 쓰는 것)
| 메서드 경로 | 근거 | 요청 | 응답 / 동작 |
|---|---|---|---|
| GET `/api/stream` 외 대화 4종 | `A/modules/agent_session/api.py:31-90` | A3 | A3 |
| GET/POST/DELETE/PATCH `/api/sessions…` | api.py:94-127 | POST query `title, mode, schema_name`; PATCH query `title, schema_name` | 세션 `{id(12hex), title, mode, schema_name, created_at, updated_at}`; DELETE는 대화 기억도 지움 |
| GET/PUT `/api/sessions/{id}/messages?mode=build|answer|act` | api.py:134-155 | PUT body = 화면 메시지 배열 | `{messages}` / `{status:'ok'}` |
| POST `/api/upload` | `A/modules/files/api.py:14` | multipart `files[]`, `session_id` | `{uploaded:[{name, path:'/workspace/uploads/<name>', local_path, size}|{name,error}]}` |
| GET `/api/files?session_id` | files/api.py:29 | | `{uploads:[{name,size}], output:[{name,size}]}` (size는 사람이 읽는 문자열) |
| DELETE `/api/files/{name}?session_id` | :37 | | `{status:'ok'|'not_found', filename}` |
| GET `/api/uploads/{name}?session_id&download` | :47 | | 파일(텍스트 계열 inline) |
| GET `/api/download/{name}?session_id` | :74 | | output 파일 |
| POST `/api/sandbox/clear?session_id` | :89 | | `{status, message:'샌드박스 파일이 모두 삭제되었습니다.'}` |
| GET `/api/neo4j/status` | `A/modules/ontology/api.py:60` | | `{status:'connected'|'disconnected', error?}` |
| GET `/api/schema` | api.py:72 → tools.py:391 | | 통합 스키마 `{classes[{name, description, properties, binding_kind, binding?, behaviors?}], relationships[], schemas[{name, description, class_names}]}` (behavior SQL 제외) |
| PUT `/api/schema/classes` | api.py:102 | `{name, original_name, description, properties[], schema_name, binding_kind}` | 이름 변경 시 모든 그룹·그래프 라벨 변경 |
| DELETE `/api/schema/classes/{name}` | api.py:127 | | 관련 관계 타입·엔티티 함께 |
| PUT/DELETE `/api/schema/relationships` | api.py:134,146 | `{name, from_class, to_class, description, properties, schema_name}` / query from_class,to_class | |
| POST/PATCH/DELETE `/api/graph/entities`, POST `/api/graph/relationships` | api.py:166-215 | `{class_name, properties, match_keys}`, `{properties}`, `{from_id,to_id,rel_type,properties}` | |
| POST `/api/neo4j/clear-all` | api.py:222 | | 그래프 전체 `DETACH DELETE` |
| GET `/api/schemas` | api.py:237 | | `{schemas:[…+classes[].entity_count, total_entity_count]}` |
| GET `/api/schemas/{id}` | :266 | | 스키마 상세 |
| PUT `/api/schemas/{id}/brief` | :285 | `{intent, golden_questions[], golden_commands?[]}` (생략 시 보존) | `{status:'ok'}` |
| POST `/api/build-brief/draft` | :312 → service.py:1388 | `{datasources[{name,schemas}], documents[], target_schema, intent, golden_questions}` | `{intent, questions[{question,evidence}], note, error}` — 저장 안 함, 실패도 200 |
| DELETE `/api/schemas/{id}` | :348 | | 메타데이터만 |
| DELETE `/api/schemas/{id}/entities` | :361 | | `{status, deleted}` |
| POST `/api/schemas/{id}/rebuild` | :388 | | `{status, classes, relationships}` (무작업) |
| GET `/api/graph?class_name&schema_name&limit=100` | :407 | | `{nodes, edges}` |
| GET `/api/graph/search?q&class_name&limit` · POST `/api/graph/nl-query` · GET `/api/graph/neighbors?node_id&depth` | :484, :523, :629 | nl-query는 OpenAI chat completions 직접 호출 | |
| GET `/api/datasources[?refresh=true]`, `/{ds}/schemas`, `/tables?schema`, `/tables/{t}/columns`, `/tables/{t}/sample?limit` | `A/modules/ontology/datasource_api.py:43-105` | | 브리지 프록시(M3) |
| GET/PUT/DELETE `/api/schema/classes/{c}/binding`, GET `…/binding/validate` | :142-179 | BindingBody `{datasource, table, source_schema, schema_name, column_map, key_columns, base_conditions, label_property, extra_tables, default_limit, notes}` | |
| GET/PUT/DELETE `…/behaviors[/{b}]`, POST `…/{b}/invoke`, POST `…/behaviors/preview`, POST `…/fetch` | :265-356 | BehaviorBody `{sql_template, description, parameters, output_columns, result_kind, max_rows, golden_question, schema_name}` | |
| POST `/api/schema/generate-from-catalog` | :382 | `{datasource, source_schema, schema_name, tables, bind, include_relationships, dry_run}` | 계획 `{classes, relationships, counts}` / 오류 `{error, catalog_empty}` |
| GET `/api/build-strategy/recommend` | :413 → build_strategy.py:180-249 | | `{inputs, recommended, reason, available[], unavailable[{strategy, reason}]}` |
| POST `/api/schema/{id}/reverse-bind/preview|apply` | :486, :498 | `{datasource, source_schema, limit}` / `{…, bindings, include_auto, document_refs}` | |
| POST `/api/schema/{id}/causal/discover|decide|apply`, GET `…/causal/hypotheses?decision` | :531-582 | | |
| POST/DELETE `/api/schema/{id}/publish[?dry_run]` | :584, :604 | | publish.py:520 결과 — **화면 미사용** |
| GET/PUT/DELETE `/api/schema/classes/{c}/actions[/{a}]` | `A/modules/kinetic/api.py:304-357` | ActionBody(:38-55) | `{status, action, warnings, next}` / 422 `{error, action_name}` / 404 |
| POST `/api/act/plans` | kinetic/api.py:471 | `{class, action, where, params}` | 실행기 plan (M2) |
| GET `/api/release/overview`, POST `/export|plan|apply`, GET `/package/{name}`, `/timeline` | `A/modules/release/api.py:92-183` | | 관리 API dev/prod 중계 |

## 3. 구축 흐름 (S5)
1. FE `Wt` → `Bt` → `/api/stream?mode=build&build_context=…`.
2. `generate_sse`(service.py:1987): build_context 파싱(:372-460) → 컨텍스트가 있으면 세션 보장+`build_context` 테이블 저장, 없으면 저장본 복원(:2002-2011) → 체크포인트 없으면 `_compose_build_prompt`(:463-555), 있으면 `_compose_continuation_prompt`(:627-697). CLI 경로는 체크포인트가 없어 매번 전자(A3 §5.8 추정).
3. 라벨 블록(값 있을 때만): `[사용자 작업 요청]`, `[구축 의도]`, `[연결 데이터소스]`(번호, `(스키마: …)`), `[업로드 문서]`(`- /workspace/uploads/<이름>`), `[대상 스키마]` 또는 `[새 스키마 이름]`, `[골든 퀘스천]`(번호), `[연결 시스템]`, `[인스턴스 원천]`(시스템만일 때), `[실행 역할] — 액션 정책 roles 에는 이 이름만 쓴다`(골든 커맨드 있고 `KINETIC_ROLE_CATALOG` 있을 때), `[골든 커맨드]`, `[검토 피드백]`(질문·이전 판정·상태·기존 답변·사용자 피드백). 스킬이 기대하는 `[전략]` 라벨은 만들지 않는다.
4. 상태 이벤트 문구(:2059-2071), 도구 설명 문구(:1576-1624), 부수 이벤트(:1660-1741; neo4j_update 대상 :142-150).
5. 종료: 최종 텍스트에서 ```` ```ontology_build_report ```` 블록 추출(:284 패턴, :762), 없으면 골든 키를 가진 ```` ```json ```` 블록 허용(:744), 질문 정규화(누락 시 기본 status `answerable`, confidence `medium`; 블록에 질문이 없으면 모든 질문 `not_yet_answerable/low`), 커맨드 정규화(:863-938: 저장소 액션의 `golden_command` 문장 매칭, 취소형 정규식 `취소|되돌|원복|원래대로|롤백|undo|cancel` → 모든 단계에 보상 있는 액션을 「보상(역순)」으로, `verified`는 저장소 `verified_at`로 덮음, 누락 커맨드는 「액션이 만들어지지 않았습니다.」), `_persist_golden_commands`(:827, 스키마에 커맨드가 비어 있을 때만), `quality` = `review_status` + schema_name(:713).
6. todos 4단계 완료 + `done{message:'완료!', files, text, build_report}`(:2504-2527).

## 4. 스킬 (지시문) — 구조 근거
| 스킬 | 파일 | 요점 |
|---|---|---|
| 구축 | `SK/ontology-build/SKILL.md`(271줄, v1.2.0) + references 8개(datasource-binding 252, golden-commands 166, validation 92, parser-rules 75, ingestion-patterns 55, strategies 35, quality-review 34, source-types 25) | 입력 점검 표·되묻기 2회·금지 사항, Phase 1/2/2.5/3/4, 스키마 그룹 규칙, 핵심 규칙, 완료 기준·리포트 |
| 브리프 초안 | `SK/ontology-brief-draft/SKILL.md`(127줄) | 읽기 전용·한 턴·`ontology_brief_draft` 블록 |
| 트리플 추출 | `SK/triple-extract/SKILL.md` | M6 파이프라인용 |
- 리포트 스키마: `SK/ontology-build/references/validation.md` 6절; 골든 커맨드 → 액션 규칙: golden-commands.md 0–6절.

## 5. 저장 구조 (SQLite `sessions.db`, `session_store.py`)
| 테이블 | 줄 | 키·주요 열 |
|---|---|---|
| sessions | 39 | id, title, mode, schema_name, created_at, updated_at |
| messages | 48 | 내장 에이전트 기록 |
| build_context | 62 | session_id → context_json |
| frontend_state | 69 | (session_id, mode) → state_json |
| ontology_schemas | 396 | id(uuid 12hex), name UNIQUE, description, intent, golden_questions(JSON), golden_commands(JSON, 마이그레이션) |
| schema_classes | 406 | (schema_id, class_name), description, properties JSON, binding_kind(`materialized` 기본) |
| schema_relationships | 416 | (schema_id, name, from_class, to_class), description, properties |
| class_datasource_bindings | 430 | datasource, source_schema, table_name, extra_tables, key_columns, column_map, base_conditions, label_property, default_limit 100, notes |
| class_behaviors | 450 | behavior_name, parameters, sql_template, output_columns, result_kind, max_rows 200, golden_question, verified_at, verify_row_count, behavior_type `sql` |
| class_actions | 476 (+마이그레이션 steps, golden_command, verified_at, verify_summary) | parameters, key_property, system, operation_id, arg_mapping, effect, confirm_threshold, max_targets, policy, compensate, writeback_property, version |
| element_provenance | 502 | element_kind class/property/relationship, strategy, evidence_kind, evidence_ref (첫 기록 우선) |
| causal_hypotheses | 518 | 통계값·significant·decision |
- `get_schema_by_name`(:749): 정확 일치 없으면 LIKE 부분 일치(최근 것) — 이름이 비슷한 다른 스키마로 잘못 갈 수 있음.
- `add_class_to_schema`(:777): upsert가 description·properties를 **덮어씀** → `batch_ingest(schema_name)`가 사용 클래스마다 빈 값으로 호출(tools.py:756-764) → 기존 클래스 설명·속성 정의가 지워짐(코드상 추정, 예제 시드도 해당: `R/sample/seed_ontology.py:177-186` 후 `batch_ingest`).
- `upsert_class_action`(:1400): 저장 전 `kinetic/definition.validate_action`, 갱신마다 version+1, `verified_at`·`verify_summary` 초기화; key_property 비면 `default_action_key_property`(:1368: 속성 `key:true` → 바인딩 첫 키 컬럼의 속성명 → "").

## 6. 그래프 쓰기
- 인스턴스: `batch_ingest`(tools.py:617-783): 파일 경로 또는 JSON, parser_screen(품질)으로 걸러 DLQ, 노드 `MERGE (:_Entity:<class> {_source_id})`, 문자열 2000자 자르기, `parent_id` → `CONTAINS` 관계, 명시 관계 `MERGE`, 임베딩(OpenAI 키 있을 때, `entity_embedding_vector` 인덱스), 응답 `{status, nodes_created, relationships_created, nodes_embedded, quarantined?, errors?(20)}`.
- 발행: publish.py — 레지스트리 라벨(:42-46), 수집(:136), 계획(:170 counts), 레지스트리 재작성(:303: 모델 하위 삭제 후 Model→HAS_CLASS→Class→HAS_ACTION→Behavior{type:'action'}, Class→HAS_BINDING→Binding→HAS_BEHAVIOR→Behavior{type:'sql'}, Model→HAS_RELATIONSHIP), 액션 노드 속성(:250-300, steps는 다단계일 때만), 네이티브 제약 `ont_pub_*`(:469-518), 실행기 카탈로그 새로고침(실패 무시) (:553).
- 그래프 통계 `graph_stats`(tools.py:875).

## 7. 액션 정의 계약 (kinetic/definition.py)
- 패턴 :18-37, 기본값 :44-46(confirm 0, max 50), parameters :67-95, 표현식 뿌리 :98-134, arg_mapping :137-168, steps :171-239, policy :242-279, validate_action :294-366(steps가 있으면 첫 단계로 system/operation_id/arg_mapping 덮음).
- 에이전트 도구 `action_create`(tools.py:1718-1846): 스키마 해석(:1649, 지정 없으면 클래스를 가진 첫 그룹), operation 존재 확인(:1698), 경고 문구, `next` 문구. `action_dry_run`(:2131-2200): 에이전트 토큰으로 plan, 허용≥1이면 `mark_action_verified`. `system_query`(:2011, GET만, save_path `/workspace/output/`). `schema_publish`(:1899).
- 역할 목록·토큰: `A/modules/kinetic/client.py:51-101`, 셸 `E/main/kinetic.js:22-25, 100-102` (studio=`lite-user`{kinetic_admin, kinetic_approver, scm_operator}, agent=`lite-agent`{scm_operator}).

## 8. 전략·기타 도구
- 전략 추천 결정 표: `A/modules/ontology/build_strategy.py:180-249`, 시계열 전제(:60-110, 최소 행 = max_lag*2+10).
- 카탈로그 생성: schema_ontology.py — 이름 규칙 :73(PascalCase), :91(`REFERENCES_<대상 테이블 대문자>`), 라벨 열 힌트 name/title/label/code/description, 참조 열 접미 `_id/_no/_code/_key`, 타입 매핑, 카탈로그는 그래프의 `:Table`/`:Column` 노드에서 읽음(:111-), 비면 CatalogEmpty.
- 역바인딩 점수: entity_matcher.py 머리말(열 0.6/타입 0.2/이름 0.2, 판정 auto/needs_review/conflict/no_match).
- 인과: 통계 서비스 `DOMAIN_LAYER_URL`(기본 127.0.0.1:8001, 셸 미설정) — `A/shared/kernel/settings.py:225`.
- 엔티티 해소(ER): `A/modules/ontology_runtime/entity_resolution.py`(후보→재순위→판정), 품질 파이프라인에서 호출(quality/pipeline.py:40), 재순위 서비스 `ER_RERANK_URL`=127.0.0.1:9(셸) → unavailable.
- extract_triples / table_ingest / quality_*: `A/modules/quality/tools.py:16-120` (자동 적재 ≥0.85, 검수 0.60–0.85, 그 미만·위반 DLQ) — M6.
- 문서 인덱싱 `A/modules/document_indexing/*` — 외부 호출자는 quality/api.py:63(텍스트 읽기)뿐.

## 9. 파일 작업 공간
- `files/workspace.py:147-212` `write_upload`: 이름 NFC 정규화, `sandbox/sessions/<세션>/uploads/<이름>`과 `sandbox/uploads/<이름>`(에이전트용 루트) **두 곳**에 저장. 파일 이름을 경로로 정리하지 않음(`../` 미검사 — 보안 관찰).
- 목록 `list_uploads/list_outputs`(:227-270).

## 10. 배포(릴리스)
- `A/modules/release/api.py`: dev/prod 관리 API 중계, 패키지 형식 `og-release/1`, 이름 규칙 `^[A-Za-z0-9._-]{1,64}$`, 기본 이름 `R<n>`, 키 후보 `clause_key, version_id, doc_id, code, grade, key, name`, 패키지 디렉터리 기본 = 백엔드 패키지 안 `data/releases`(앱 번들 내부, `ONTOLOGY_RELEASE_DIR` 미설정).
- 셸: dev=`http://127.0.0.1:<portal>`, prod=`studio.env`의 값 또는 `http://127.0.0.1:9`(없음) — `E/main/services.js:128-131`. 포털 관리 API 계약은 M4.

## 11. 예제 온톨로지 시드 (`R/sample/seed_ontology.py`)
- 셸이 첫 실행에 Studio 인터프리터로 실행(`E/main/index.js:188-203`, 표식 `.ontology-lite-sample-ontology`).
- 순서: 스키마 생성(+intent, 질문) → 브리프 갱신(+커맨드) → 클래스 7(키 속성 `key:true`) → 관계 6 → `sample` 그래프 가상 노드 읽기 → 노드 id `sample:<Class>:<key>`, `name` 없으면 subject 또는 키 → 관계는 대상 키가 있을 때만 → batch_ingest → 액션 3(`upsert_class_action`, effect write, confirm 0, max 20) → publish → 액션별 dry-run(모두 verified 아니면 종료 코드 2). 출력 JSON 한 줄.
- 정의 값(액션·정책·dry-run 조건)은 파일 :55-140.

## 12. 환경 변수 (M1 관련)
`SESSION_DB_PATH`, `LOCAL_SANDBOX_ROOT`, `SANDBOX_WORKDIR=/workspace`, `NEO4J_URI/USER/PASSWORD/DATABASE(=ontology)`, `DATAFABRIC_BASE_URL`·`TEXT2SQL_BASE_URL`(=셸 브리지), `KINETIC_URL`, `KINETIC_STUDIO_TOKEN`, `KINETIC_AGENT_TOKEN`, `KINETIC_ROLE_CATALOG`, `ONTOLOGICAL_ADMIN_DEV_URL/PROD_URL`, `ONTOLOGY_RELEASE_DIR`, `DOMAIN_LAYER_URL`, `ER_RERANK_URL`, `DATASOURCE_MAX_ROWS`(500), `DATASOURCE_AGENT_ROW_PREVIEW`(30), `OPENAI_API_KEY`(임베딩·nl-query), `MAJOR_MODEL`(내장 build) — `E/main/services.js:117-160`, `A/shared/kernel/settings.py`.

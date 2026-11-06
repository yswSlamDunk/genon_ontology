# M6 품질 검수 — 코드 추적 (원본 근거, 구현 세션에 넘기지 않음)

- 기준: 배포본 0.1.1. 경로 약어
  - `Q/` = `shared/app/runtime/studio/app/backend/src/modules/quality/`
  - `BE/` = `shared/app/runtime/studio/app/backend/src/`
  - `SK/` = `shared/app/runtime/studio/app/skills/`
  - `FE` = `shared/app/runtime/frontend/assets/index-Bnym06ph.js` (압축 번들, 위치는 **바이트 오프셋** `@NNNNNNN`)
- 모듈 머리 주석에 "spec 013"(신뢰도 게이트·HITL·DLQ)이 언급된다(`Q/__init__.py:1-5`). spec 문서 자체는 배포본에 없다.

## 0. 전체 구조

```
[구축 에이전트(M1)] --도구--> extract_triples / table_ingest / batch_ingest(파서) / quality_checkup / quality_report
        │                                  │
        ▼                                  ▼
  LLM 추출(OpenAI 직접 호출)       원천 검증(CSV 규칙)
        └─────→ 후보 → 온톨로지 게이트 → 복합 신뢰도 S_c → 분기
                     ├ auto  → 그래프 MERGE (Bolt) + 후보 status=auto_ingested
                     ├ review→ 후보 status=pending  ───→ [확인하기] approve/edit/reject
                     └ dlq   → 후보 status=dlq + DLQ 항목 ──→ [보류함] redrive/discard/고치기
  점검(checkup) = 형상 검증 + 고립 린팅 + 식별자 해소 + 결측 보정 → DLQ/후보 생성
  저장: Studio SQLite(sessions.db) 품질 테이블 8개, 그래프(Bolt)
```

- 라우터 등록: `BE/host/app.py:19, 69` (`/api/quality` 접두사, `Q/api.py:20`).
- 에이전트 도구 등록: `BE/modules/agent_session/service.py:94`(import), `:152` `_BUILD_MODE_TOOLS` 안 `:205-211` (주석: 검수 결정·DLQ 재처리 도구는 일부러 없음). 외부 CLI 에이전트에는 같은 목록이 `BE/modules/agent_bridge_mcp/server.py:22-37`로 MCP 노출.
- 파서 경로 선별: `BE/modules/ontology/tools.py:617`(`batch_ingest`), `:649-660`(`parser_screen.screen` 호출, `INGEST_GATE` 환경 변수로 끔), `:772`(응답 `quarantined`).
- 구축 보고서에 검수 현황 부착: `BE/modules/agent_session/service.py:714-736` (`_quality_status_for` → `checkup.review_status`).

## 1. 프런트엔드 컴포넌트 (FE)

| 컴포넌트 | 위치 | 역할 |
|---|---|---|
| (헬퍼) 카드 문장·이유·배지·버튼 문구 | `@2174515`(이유 문구) `@2175866`(배지) `@2176115`(버튼 문구) | `HKe`/`UKe`/`WKe` |
| (헬퍼) 보류 묶음 정의 10개 | `@2176483` (`B9`), 원천 사유 문구 `@2178796`, 보류 항목 문장 `@2179118` | 원인 코드 → 묶음·아이콘·도움말·fix 종류 |
| (헬퍼) fetch 래퍼 | `@2180248` (`H9`) — 실패 시 `detail` 문자열을 오류로 | |
| `HoldView` | `@2181457` | 보류함 + 「지금 점검하기」 |
| `GraphMini` | `@2188881` | 후보 주변 1홉 그래프(cytoscape) |
| `ReviewDeck` | `@2191951` | 확인하기(카드 덱, 키보드 Y/N/E/→) |
| `BuildReviewPanel` | `@2201450` | 구축 화면 오른쪽 「검수」 탭 |
| `HomeView` | `@2204768` | 한눈에 |
| `QualityExpertPanel` | `@2213683` | 「⚙ 고급」 8개 탭 |
| `QualityPanel` | `@2253345` | `view=quality` 최상위(「지식 품질」) |

- 내비게이션 항목 `{id:'quality', label:'품질 검수', icon:'✅'}`: `@2305199`. 마운트 `@2310700` 부근 (`initial-schema-id`=선택된 스키마 이름에 맞는 id, `onOpenBuild` → 구축 뷰 전환 `@2306659`).
- 구축 오른쪽 탭 「검수」(`data-testid=build-tab-review`, 배지 = to_review+held): `@2317103`. 응답 스트리밍 종료 시 `refreshKey++` `@2306659` 부근.
- 구축 보고서 카드 「검수 탭에서 보기」(`build-report-open-review`): `@239189` → `open-review` 이벤트(schema_id) → 오른쪽 탭 전환.

### 1.1 화면별 API 호출 (FE)
| 화면 동작 | 요청 |
|---|---|
| QualityPanel 열기/탭 전환 | `GET /api/schemas/{id}` + `GET /api/quality/summary?schema_id=` |
| ReviewDeck 로드 | `GET /api/quality/candidates?schema_id&status=pending&kind&limit=300` |
| 카드 판단 | `POST /api/quality/candidates/{id}/decide` `{decision, reviewer:"studio-user", edit?}` |
| 자세히(그래프) | `GET /api/quality/candidates/{id}/neighborhood` (tbox 제외) |
| HoldView 로드 | `GET /api/quality/dlq?schema_id&status=open` |
| 지금 점검하기 | `POST /api/quality/checkup {schema_id}` |
| 다시 시도/모두 다시 시도/원문에서 연결 | `POST /api/quality/dlq/redrive {ids}` |
| 관계를 지도에 추가하고 넣기 | `PUT /api/schema/relationships {name, from_class, to_class, description:"", schema_name}` → `POST …/dlq/redrive {ids:[id]}` |
| 값 저장 | `POST /api/quality/manual-value {schema_id, key, name, class_name, property, value}` |
| 대표 값 | `POST /api/quality/identity/conflicts/{dlq_id}/resolve {value, source, reviewer}` |
| 그래도 넣기 | `POST /api/quality/candidates/{candidate_id}/decide {decision:"approve"}` |
| 버리기 | `POST /api/quality/dlq/{id}/discard` |
| BuildReviewPanel | `GET /api/schemas/{id}`, `GET /api/quality/review-status?schema_id`, `GET /api/quality/policy/{id}` |
| 고급: 공통 | `GET /api/quality/codes`(마운트 시), `GET /api/quality/summary` |
| 고급: 검수 큐/이력 | `GET …/candidates?status=pending` / `status=auto_ingested,approved,edited,rejected`, `POST …/bulk-decide {ids, decision, reviewer}` |
| 고급: DLQ | `GET …/dlq?schema_id&status=open&reason_code`, `POST …/dlq/redrive {ids}`(선택 없으면 표시된 전부), `POST …/dlq/{id}/discard` |
| 고급: 추출 | `GET /api/files?session_id=`(업로드 목록), `POST …/extract {schema_id, text, filename, session_id, doc}` |
| 고급: 검증 | `POST /api/upload`(multipart files, session_id), `POST …/source/preview {filename, session_id}`, `POST …/source/ingest {schema_id, filename, session_id, mapping, dry_run}`, `GET …/shapes?schema_id`, `POST …/shapes/run`, `POST …/lint` |
| 고급: 식별자 | `POST …/identity/run`, `GET …/identity/clusters?schema_id`, `GET …/dlq?schema_id&reason_code=ER_CONFLICT`, `POST …/identity/conflicts/{id}/resolve`, `POST …/impute` |
| 고급: KGE | `GET …/kge?schema_id`, `POST …/kge/train`, `GET …/kge/score?schema_id&h&r&t`, 링크(새 창) `…/export/feedback.jsonl?schema_id`, `…/export/kge-triples.tsv?schema_id`; 「링크 예측 후보 만들기」 = `POST …/impute` |
| 고급: 정책 | `PUT /api/quality/policy/{id} {policy:{…}}` |

- 화면이 쓰지 않는 라우트: `GET/POST /rules`, `DELETE /rules/{id}`, `GET /reports`, `POST /source/check-table`, `GET /candidates/{id}` (번들에 문자열 없음 확인).

## 2. 백엔드 라우트 (`Q/api.py`) — 35개

| 줄 | 메서드 경로 | 처리 |
|---|---|---|
| 32 | GET `/policy/{schema_id}` | `{schema_id, policy}` |
| 38 | PUT `/policy/{schema_id}` | 기존 정책에 본문(`policy` 또는 본문 자체) 병합 → `validate()` 실패 시 422(`; `로 연결) |
| 82 | POST `/extract` | `ExtractRequest{schema_id, text, filename, session_id, doc, samples(1-10), max_chunks(1-500, 기본 50)}`; 파일이면 업로드 폴더에서 읽음(PDF는 pdfplumber) `:62-79`; 텍스트 없으면 422; RuntimeError(키 없음) → 503 |
| 104 | GET `/candidates` | `status`(기본 pending, 쉼표 다중), `kind`, `limit`≤500, `offset` → `{items, count}` |
| 113 | GET `/candidates/{id}` | 단건, 없으면 404 「후보를 찾을 수 없습니다」 |
| 121 | GET `/candidates/{id}/neighborhood` | 엔터티 키(관계면 양 끝) → 1홉 서브그래프; 그래프 오류면 `{nodes:[],edges:[],error,keys}` |
| 144 | POST `/candidates/{id}/decide` | `{decision, reviewer="reviewer", edit}` → `pipeline.decide`; DecisionError → 422 |
| 160 | POST `/candidates/bulk-decide` | approve/reject만(그 외 422); 항목별 결과 또는 `{id, error}` |
| 179 | GET `/dlq` | `status`(기본 open), `reason_code`, `limit`≤1000 → `{items(+reason_description), counts(원인별)}` |
| 196 | POST `/dlq/redrive` | `ids` 비면 `schema_id`+`reason_code`의 열린 항목 전부; 둘 다 없으면 422 「재처리할 항목이 없습니다」. stage=extract 항목은 재추출(max_chunks 5) |
| 239 | POST `/dlq/{id}/discard` | 없으면 404 |
| 250 | GET `/summary` | `pipeline.summary` |
| 256 | GET `/codes` | `{codes, hard, soft}` |
| 270/276/294 | GET·POST·DELETE `/rules` | layer `source`(expectations 검증) / `shape`(kind 검증), 그 외 422 |
| 308 | POST `/source/ingest` | `tabular.ingest`; MappingError/ValueError → 422 |
| 328 | POST `/source/check-table` | 바인딩된 원천 테이블 집계 SQL 검사 → 보고서 저장, blocked면 DLQ(SRC_TABLE_BLOCKED) |
| 350 | GET `/shapes` | 스키마에서 생성한 shape + 설명 |
| 363 | POST `/shapes/run` | `shapes.run` |
| 371 | POST `/lint` | `lint.run` |
| 379 | GET `/reports` | 최근 검증 보고서(≤100) |
| 387 | POST `/identity/run` | `identity.run` |
| 395 | GET `/identity/clusters` | `identity.clusters` |
| 409 | POST `/identity/conflicts/{id}/resolve` | `{value, source, reviewer}` → 대표 값 기록, ValueError → 422 |
| 419 | POST `/impute` | `imputation.run` |
| 429 | POST `/kge/train` | ValueError → 422 |
| 440 | GET `/kge` | `kge.status` |
| 448 | GET `/export/feedback.jsonl` | 판정 이력 → JSONL(`decision`, `label`, `messages[user=근거 인용, assistant=정답 또는 원본 JSON]`) |
| 472 | GET `/export/kge-triples.tsv` | `h\tr\tt` 줄 |
| 491 | POST `/source/preview` | `{columns, rows(앞 8), row_count}` |
| 505 | GET `/kge/score` | `{h,r,t,probability,distance,top_tails[3]}` |
| 520 | POST `/checkup` | `checkup.run` |
| 530 | GET `/review-status` | `checkup.review_status` |
| 548 | POST `/manual-value` | 사람 입력을 property 후보(s_c=1.0, method=manual)로 만들고 즉시 approve → 실패 시 후보를 rejected로 표시하고 422 → 성공 시 `shapes.run` 재실행 `{…decide 결과, resolved}` |

모든 스키마 지정 라우트는 스키마가 없으면 404 「스키마를 찾을 수 없습니다: …」(`:23-27`).

## 3. 시나리오별 흐름

### S1 한눈에
FE `QualityPanel`(@2253345) → `GET /api/quality/summary` → `Q/pipeline.py:483-496` `summary`: `candidates`(kind별 status별 수, `Q/store.py:405-413`), `totals`, `dlq_open`(원인별), `dlq_open_total`, `reason_descriptions`, `policy`, `runs`(최근 10, `Q/store.py:226-234`). `HomeView`(@2204768): 확인된 사실 = totals.auto_ingested+approved+edited, 「점검하지 않았어요」 = runs 중 source_kind=identity 없음, 활동 문구는 source_kind별 사전(`llm_extract`→문서에서 뽑기, `structured`→표 가져오기, `identity`/`impute`→점검, `manual`→직접 입력, `redrive`→다시 시도, `parser`→파일 파싱).

### S2–S4 확인하기·결정
- 목록: `Q/store.py:385-402` — `ORDER BY s_c DESC, created_at ASC`.
- 카드 배지 `@2175866`: reasons가 있고 s_c≥review → 「확인 필요」, s_c≥auto → 「확실함」, ≥review → 「애매함」, 그 외 「약함」. 이유 문구 `@2174515`: tbox → 새 종류, identity/SAME_AS_PROPOSAL → 이름이 비슷, LINK_PREDICTED, IMPUTED(method same_as / neighbor_pattern / 기본값), PREDICATE_SYNONYM, PROP_DATATYPE, ENTITY_AMBIGUOUS, freq<1(「3번 중 round(freq×3)번」 — 3 고정), lexical<1, distance>20, s_graph<0.5, 그 외 기본 문구.
- 결정: `Q/pipeline.py:282-359` `decide`
  - 이미 approved/edited/rejected/auto_ingested → DecisionError 「이미 처리된 후보입니다 (…)」 (status `dlq`는 결정 가능 → 「그래도 넣기」 경로)
  - reject: status=rejected, 피드백 기록, 이 후보에 묶인 열린 DLQ를 discarded로 `:298-302`
  - tbox: 이름 검사 → `_apply_tbox` `:254-279`(스키마에 클래스/관계 추가 + provenance `strategy=manual, evidence_kind=human, evidence_ref=hitl:tbox_proposal`), `applied:"schema"`
  - identity의 edit 금지 `:317-318`
  - 그 외: edit 병합(subject/object 부분 갱신, predicate, value) → 게이트 재검사 → hard 위반이면 DecisionError 「스키마 제약 위반으로 적재할 수 없습니다: CODE(설명), … — 메모」 → 쓰기(확신값 = max(기존 s_c, auto_threshold), reason `hitl:approve|edit`, actor = reviewer) → status approved/edited, 피드백, 이 후보의 열린 DLQ → redriven. `applied:"graph"`.
  - 주의: `decide`의 기본 의존성은 `Deps()`라 KGE·엔터티 모호성 없이 게이트만 재검사.
- 그래프 쓰기: `Q/ingest_gate.py:102-151` (아래 §5).
- 주변 그래프: `Q/ingest_gate.py:222-249` (`_source_id IN keys`, 1홉, LIMIT 40).

### S5 점검
`Q/checkup.py:14-37` → `shapes.run` → `lint.run` → `identity.run` → `imputation.run`, 결과 요약 `missing_values`(min_count 위반), `wrong_format`(datatype), `link_rules`(max_count+min_rel+disjoint), `resolved`(shape+lint 해소), `unlinked`, `same_entity_linked`, `same_entity_to_confirm`, `value_conflicts`, `suggestions` + `details`. 보고서 layer=`checkup` 저장. FE 토스트의 "고칠 것" = missing_values+unlinked+value_conflicts, "확인할 제안" = same_entity_to_confirm+suggestions (`wrong_format`·`link_rules`는 알약에 없음).

### S6 보류함·재처리
- 묶음 `@2176483`: unknown_relation[ONTO_PREDICATE_UNKNOWN]→add_relation; schema_mismatch[ONTO_DOMAIN, ONTO_RANGE, ONTO_CLASS_UNKNOWN, ONTO_PROPERTY_UNKNOWN, ONTO_INVALID_NAME, ONTO_CARDINALITY]→retry; source_row[SRC_NULL_RATIO, SRC_UNIQUE, SRC_RANGE, SRC_FK, SRC_IN_SET, ID_MISSING]→retry; source_table[SRC_TABLE_BLOCKED]→retry; missing_value[SHAPE_MIN_COUNT, SHAPE_DATATYPE]→enter_value; link_rule[SHAPE_MAX_COUNT, SHAPE_DISJOINT]→retry; orphan[ORPHAN_NODE]→reextract; conflict[ER_CONFLICT]→pick_value; weak[LOW_CONFIDENCE]→force; other[]→retry. 분류 키는 DLQ 항목의 `reason_code`(첫 원인)뿐.
  - 관찰: PARSE_JSON, REL_ENDPOINT_MISSING, WRITE_FAILED는 「처리 중 오류」로 떨어진다. SHAPE_DATATYPE 위반은 「값 입력」으로 고치지만 입력란 placeholder는 속성 이름.
- 재처리 `Q/api.py:196-236` + `Q/pipeline.py:373-417` `redrive`:
  - open이 아니면 `skipped`
  - payload.source=parser → `_redrive_parser` `:447-468`(같은 `batch_ingest`로 다시 넣음)
  - stage ∈ source/shape/lint/identity → `_redrive_stage` `:420-444` → `tabular.redrive_item`(`Q/tabular.py:159-198`, 현재 파일 재읽기), `shapes.redrive_item`(`Q/shapes.py:164-175`, 재검사), `lint.redrive_item`(`Q/lint.py:74-100`, 근거 원문 최대 3개 재추출 max_chunks 5), identity(충돌 재탐지; 대표 값을 고르지 않으면 still_failing 「대표 값을 고르면 해소됩니다」)
  - payload.kind 없음 → `unsupported_stage`
  - 그 외(gate/write) → 후보를 pending으로 되돌리고 `process` 재실행, 시도+1, 여전히 dlq면 `still_failing{reason_code, attempts, exhausted(attempts≥3)}`, 아니면 redriven + `ingested`/`queued_for_review`
  - stage=extract(PARSE_JSON) → api에서 재추출(max_chunks 5): parse_errors 있으면 still_failing, 아니면 redriven `reextracted{run_id}`
  - MAX_ATTEMPTS=3은 **보고만** 하고 재처리를 막지 않음(`:370, 405-410`).
- 폐기 `Q/pipeline.py:471-480`: DLQ discarded, 묶인 후보가 dlq면 rejected(reviewer `dlq:discard`). 피드백은 남기지 않음.

### S7 값 직접 입력 — `Q/api.py:548-570` (위 표).
### S8 고립 노드 — `Q/lint.py:17-55`(클래스별 `_Entity:Class` 중 SAME_AS 외 관계 0, virtual 바인딩 클래스 제외, LIMIT 500/클래스), 재처리 `:74-100`(근거 텍스트는 후보 evidence에서 이름 포함·`row` 없는 것).
### S9 대표 값 — `Q/identity.py:226-234` (stage=identity 아니면 422 「식별자 충돌 항목이 아닙니다」), 선호값 저장 `Q/store.py:596-606`.
### S10 구축 검수 탭 — FE `BuildReviewPanel`(@2201450): to_review=0 & held>0이면 hold 탭 자동. 백엔드 `Q/checkup.py:40-50` `review_status`: `to_review`(모든 kind pending 합), `held`(열린 DLQ 합), `held_by_reason`, `in_graph`(auto_ingested+approved+edited 후보 수), `pending_by_kind`. 보고서 부착 `BE/modules/agent_session/service.py:714-736`(세션의 schema_name → 없으면 이번 턴 도구 호출 인자 `schema_name` 마지막 값).
### S11–S15 고급 — FE `QualityExpertPanel`(@2213683). 매핑 초안 생성 로직 `@2213683` 이후 setup(`Be`): 원천 `ERP`, 첫 클래스, 키 = `/(^|_)(id|code|key)$/i` 첫 컬럼, 이름 = `/name|명$/i`, 클래스 속성명과 같은 컬럼, `not_null` row 규칙 1개.

## 4. 판정 규칙 (결과를 좌우 — ADR-0014)

### 4.1 정책 기본값 `Q/policy.py:13-39`, 검증 `:70-84`
w_llm 0.3, w_ground 0.5, w_graph 0.2, combine linear|harmonic, auto_threshold 0.85, review_threshold 0.60, alpha 0.5, decay_lambda 0.02, samples 3, cos_floor 0.15, cos_ceil 0.60, graph_prior 0.5, open_vocabulary_when_empty true, synonym_min_ratio 0.82, identity_auto 0.95, identity_review 0.80, kge_weight 0.5, impute_min_share 0.6, impute_min_support 2. 검증: 가중치 합=1(±1e-6), 0≤review≤auto≤1, alpha 0~1, samples 1~10, cos_ceil>cos_floor. 모르는 키·형 변환 실패 값은 무시(`from_dict` `:47-68`).

### 4.2 원인 코드 `Q/codes.py`
- HARD(즉시 DLQ) `:93-97`: ID_MISSING, REL_ENDPOINT_MISSING, ONTO_CLASS_UNKNOWN, ONTO_DOMAIN, ONTO_RANGE, ONTO_PREDICATE_UNKNOWN, ONTO_PROPERTY_UNKNOWN, ONTO_CARDINALITY, ONTO_INVALID_NAME, PARSE_JSON
- SOFT(자동 적재 금지) `:100-101`: PROP_DATATYPE, ENTITY_AMBIGUOUS, PREDICATE_SYNONYM, TBOX_PROPOSAL, IMPUTED, LINK_PREDICTED, SAME_AS_PROPOSAL, ENTITY_GENERIC
- ALWAYS_REVIEW `:104`: TBOX_PROPOSAL, IMPUTED, LINK_PREDICTED, SAME_AS_PROPOSAL, ENTITY_GENERIC
- 기타: SRC_* 6, SHAPE_* 4, ORPHAN_NODE, ER_CONFLICT, WRITE_FAILED, LOW_CONFIDENCE. 설명 문구 `:57-90`. "이름 바꾸지 말고 추가만" 원칙 `:3-4`.

### 4.3 게이트 `Q/gate.py:164-286`
- 이름 규칙 `:23` 영문/한글/밑줄로 시작, 영문·숫자·한글·밑줄.
- 지시어 이름 `:28-30` (본/동/당/해당/이/그/위 + 증권·사채·상품·회사·계약·파생결합…·투자설명서·펀드·기초자산·발행인, 또는 당사·발행인·발행회사·투자자·증권사·회사·상품·기초자산·금융투자상품) — id 없는 엔터티에만 ENTITY_GENERIC.
- 엔터티 검사 `:172-186`: 이름·id 둘 다 없음 → ID_MISSING; 클래스 없음 → ONTO_CLASS_UNKNOWN; 이름 규칙 위반 → ONTO_INVALID_NAME; 스키마에 클래스가 하나라도 있으면(closed) 미등록 클래스 → ONTO_CLASS_UNKNOWN.
- tbox `:188-193`: 항상 TBOX_PROPOSAL, 이름 규칙 위반이면 hard.
- identity `:197-206`: 양쪽 엔터티 검사, 클래스 다르면 ONTO_RANGE, 항상 SAME_AS_PROPOSAL.
- property `:211-224`: 속성명 규칙 위반 → hard; 클래스에 선언 속성이 있는데 그 속성이 없으면 ONTO_PROPERTY_UNKNOWN; 선언 타입과 안 맞으면 PROP_DATATYPE(soft).
- 타입 판정 `:118-139`: string류·빈 값은 통과; int = 부호+숫자+쉼표; float류 = 숫자/소수/지수; bool = true/false/0/1/y/n/yes/no/예/아니오; date·datetime = ISO(구분자 `/` `.` 허용, 공백→T) 또는 「YYYY년 M월 (D일)」. 적재 시 int/float/bool로 변환 `:142-159`.
- relation `:230-280`: 술어 없음 → ONTO_PREDICATE_UNKNOWN. 스키마 관계 0개면 이름 규칙만 맞으면 통과(부트스트랩). 아니면 술어 매칭 `:86-106`: 정확 → 공백·`_`·`-` 제거 소문자 비교 → difflib 유사도(관계명과 설명 대상, 설명에 포함되면 0.9 보정) ≥ 0.82. 실패 → ONTO_PREDICATE_UNKNOWN. 유사어면 m_vocab = 유사도 + PREDICATE_SYNONYM. 정의역: 같은 술어 정의 중 from_class 일치; 공역: 정의역이 맞으면 그 쌍의 to_class, 아니면 아무 정의의 to_class. 카디널리티: `max_counts`에 (클래스, 술어) 한도가 있을 때만 — **배포본에서는 한도를 넣는 곳이 없어 사실상 비활성**(`Q/pipeline.py:31` 기본 빈 dict, `default_deps` `:53-58`도 미설정).

### 4.4 점수 `Q/confidence.py`, 조합 `Q/pipeline.py:70-149`
- S_llm `:52-55`: logprob 없으면 freq, 있으면 α·logprob + (1−α)·freq. freq = M번 샘플 중 같은 사실이 나온 비율. logprob = 항목 토큰 로그확률의 기하평균(`QUALITY_EXTRACT_LOGPROBS=1`이고 모델 지원 시만).
- S_ground `:146-147` = 거리감쇠 × (½·어휘근거 + ½·정규화 cos). 어휘근거 `:136-143` = 언급(주어 이름, 관계면 목적어 이름, 속성이면 값)이 근거 텍스트(+문서 머리말)에 있는 비율. cos는 「사실 문장」 vs 「인용이 든 원문 문장(없으면 청크)」 임베딩 코사인을 [0.15, 0.60] → [0,1]로 늘림 `:71-74`; 임베딩 없으면 어휘근거로 대체 `Q/pipeline.py:101-105`. 거리감쇠 = e^(−λ·d), d = 주어·목적어 가장 가까운 출현 쌍 사이 단어 수(관계만) `:116-133`. 신호에 `ground`가 있으면(정형·식별자·보정) 그 값으로 덮음 `Q/pipeline.py:111-112`.
- S_graph `:152-167`: 같은 관계가 이미 있으면 1; 양 끝이 그래프에 있고 2~3홉 우회 경로가 있으면 max(prior, 1−e^(−Σ경로곱)) (엣지 확신 없으면 0.7, 경로 25개까지 `Q/ingest_gate.py:186-219`); 없으면 prior 0.5. KGE 모델이 있고 직접 관계가 없으면 (1−w)·S_graph + w·KGE확률 `Q/pipeline.py:119-122`.
- 결합 `:172-184`: linear = Σw·v; harmonic = 1/Σ(w/v), 한 값이라도 0이면 0.
- S_c `:219-229` = G_onto(hard 있으면 0) × m_vocab × 결합.
- 분기 `:208-216`: hard → dlq; S_c < review → dlq(원인 LOW_CONFIDENCE); S_c ≥ auto 이고 soft 없음 → auto; 그 외 review.
- 강제 검수 `Q/pipeline.py:132-136`: hard 없고 (tbox 이거나 ALWAYS_REVIEW 플래그 포함) → 점수와 무관하게 review.
- 엔터티 모호성 `Q/pipeline.py:36-50, 125-128`: 엔터티 후보에 대해 발행 그래프 엔터티 해소 상위 1·2위 점수 차 < 0.15 → ENTITY_AMBIGUOUS.
- 처리 `Q/pipeline.py:179-245`: 지문이 같은 후보가 이미 approved/edited/rejected면 근거만 합치고 `preserved`; 이전 dlq였는데 이번엔 통과면 열린 DLQ를 redriven(「재실행에서 통과」). auto → 쓰기 성공 시 auto_ingested, 실패 시 dlq + DLQ(stage write, WRITE_FAILED). review → pending. dlq → DLQ(stage gate, 첫 hard 코드).

### 4.5 지문(중복 판정) `Q/store.py:239-262`
엔터티 키 = `클래스:(id 또는 이름).lower()`. 관계 = kind|주어키|술어|목적어키, 속성 = kind|주어키|속성|값(소문자), 엔터티 = kind|주어키, tbox = kind|name|from|to, identity = 정렬된 두 키. 스키마 id 포함 SHA-1. 근거는 (chunk_id, start) 기준 합침, 최대 20개 `:298-345`.

### 4.6 LLM 추출 `Q/extraction.py`
- 청크 `:53-86`: 빈 줄 단락을 1800자(`QUALITY_CHUNK_CHARS`)까지 묶음, 원문 오프셋 유지, id `문서#cNNNN`. 머리말 = 문서명 + 앞 400자(`QUALITY_HEADER_CHARS`) `:425`.
- 값 블록 `:101-139`: [문서 머리말], [허용 클래스](설명·속성:타입), [허용 관계](이름: from -> to — 설명), [검수 예시](최근 피드백 8개: 승인/수정 후 승인/기각 + JSON), [청크]. 지시문 = 스킬 `SK/triple-extract/SKILL.md`.
- 모델 `:144-184`: `QUALITY_EXTRACT_MODEL` → `MINOR_MODEL`(기본 `gpt-5.4-mini-2026-03-17`, `BE/shared/kernel/settings.py:169`) 접두사 제거; OpenAI SDK chat completions, `response_format=json_object`; `OPENAI_API_KEY` 없으면 RuntimeError(→503). `OPENAI_BASE_URL` 지원. logprobs 거부 시 끄고 재시도.
- 샘플 `:298-350`: 청크당 M회 호출, 한 샘플 안 중복 제거, 지문별 빈도·logprob·인용 수집. 근거 = {doc, chunk_id, page, quote, text(청크), chunk_start, header, start/end/sentence(인용을 원문에서 찾았을 때)}. 신호 = {freq, logprob, quote_found}.
- 파싱 실패: 한 샘플 실패는 빈도만 낮춤; M회 모두 실패하고 후보 0 → DLQ(stage extract, PARSE_JSON, payload {chunk_id, doc, text}) `:433-438`.
- 임베딩 `:368-394`: `BE/modules/ontology/embedding.py:105` `embed_texts` — OpenAI 모드면 `text-embedding-3-small`, 아니면 Ollama. 실패·0벡터면 cos 없음.
- 실행 통계 `:427-450`: `{run_id, chunks, samples, total, auto_ingested, pending, dlq, preserved, write_failed, parse_errors, by_reason}`.
- 스킬 요지(`SK/triple-extract/SKILL.md`): 청크에 명시된 사실만, 관계 술어는 허용 목록 그대로, 없으면 tbox_proposals로, 모든 항목에 원문 그대로 인용, 지시어 이름 금지(머리말 정식 이름으로), 표 머리말·예시는 사실로 내지 않음, 숫자 타입이면 숫자만, 출력 JSON 키 `entities/relations/properties/tbox_proposals`.

### 4.7 정형(CSV) `Q/tabular.py`, `Q/expectations.py`
- 인코딩 utf-8-sig → cp949 → euc-kr `:45-57`. 매핑 필수 `class, key, source_system`, 없는 컬럼 422 `:60-69`.
- 규칙 `Q/expectations.py:41-141`: not_null(max_ratio 기본 0, 관측 = 빈 비율), between(min/max, 숫자 아님도 실패), unique(중복 행 모두), in_set(values), fk(ref.values 또는 그래프 `ref.class.ref.property` 값 집합). severity row(실패 행만 격리, 기본) / block(테이블 전체 중단).
- 적재 `Q/tabular.py:110-156`: block 실패 → DLQ(stage source, SRC_TABLE_BLOCKED, candidate_id `table:파일`) 아무것도 안 넣음. 행 실패 또는 키 없음 → 행별 DLQ(candidate_id `row:파일:i`). 통과 행 → 엔터티(id `원천:키`, source_system, source_key), 속성(빈 값 제외), 관계(목적어 키 `클래스:이름`), 신호 freq=1·ground=1 → `process`. 통계 + `rows_quarantined`, `rows_loaded`.
- 바인딩 테이블 집계 SQL `Q/expectations.py:163-224`(식별자 정규식, 위험 문자 포함 값 거부, 기존 datasource 실행 경로 경유) — 화면 없음.

### 4.8 파서 선별 `Q/parser_screen.py:28-112`
id 없음 → ID_MISSING, 클래스 없음/이름 규칙 → ONTO_CLASS_UNKNOWN/ONTO_INVALID_NAME, 관계 타입 이름 규칙, 양 끝이 이번 묶음에도 그래프에도 없음 → REL_ENDPOINT_MISSING, 스키마에 **선언된** 관계면 아는 쪽 정의역/공역 검사. 미등록 클래스는 막지 않음. 걸린 것은 DLQ(stage gate, payload.source=parser). 부모가 걸러진 자식은 남기고 `parent_missing` 메모. 점수 계산 없음.

### 4.9 형상 `Q/shapes.py`
자동: 속성 `required:true` → min_count, 타입이 string류 아님 → datatype(파이썬 판정, 2000개까지). 규칙(저장된 shape 규칙): max_count{class,predicate,max}, min_rel{class,predicate,min=1}, disjoint{classes[2]}. `virtual` 속성 제외. 위반 노드마다 DLQ(stage shape, candidate_id `shape:<shape id>:<노드키>`), 이번에 안 걸린 열린 shape DLQ는 redriven(「재검증에서 해소됨」). 클래스당 500(min_count) 한도.

### 4.10 식별자 `Q/identity.py`
- 이름 정규화 `:24-30`: (주)/㈜/주식회사/(유)/유한회사/co.,ltd/inc/corp/corporation 제거, 공백·`-_.,·()[]` 제거, 소문자.
- 식별 속성 `:33-42`: 선언 `identifier:true` 또는 이름이 biz_no/business_no/duns/lei.
- 쌍 점수 `:65-77`: 식별 속성 둘 다 있으면 (숫자만 비교 또는 문자열 동일) 1.0 / 불일치 0.0; 아니면 정규화 이름 같으면 0.97, 다르면 difflib 비율.
- 실행 `:90-147`: 클래스별 노드(최대 5000) 모든 쌍, 같은 원천 시스템끼리는 건너뜀(원천이 「문서 추출」인 경우 제외), 이미 SAME_AS면 건너뜀. ≥0.95 → SAME_AS 즉시 쓰기 + 후보 auto_ingested; ≥0.80 → identity 후보 → `process`(강제 검수). 이어서 충돌 탐지.
- 클러스터 `:152-200`: SAME_AS 합집합-찾기, 속성별 원천 값, 서로 다른 값이 2개 이상이면 conflict, 선호값 있으면 대표, 값이 하나면 그 값.
- 충돌 `:203-223`: 선호값 없는 conflict마다 DLQ(stage identity, ER_CONFLICT, candidate_id `conflict:<묶음>:<속성>`), 사라진 것은 redriven.

### 4.11 결측 보정 `Q/imputation.py:160-192`
순서(같은 (노드, 속성)에는 하나만): ① SAME_AS 상대의 값(method same_as) ② 이웃 패턴 — 같은 이웃에 같은 관계 타입으로 붙은 같은 클래스 노드들의 최빈값, 지지 ≥2 이고 비율 ≥0.6(neighbor_pattern) ③ 클래스 선언 `default`(class_default) ④ KGE 링크: 선언 관계가 없는 노드에 상위 5 꼬리 중 클래스 맞고 확률 ≥0.7 첫 하나, 최대 20건. 모두 flags IMPUTED/LINK_PREDICTED, ground 0 → 강제 검수.

### 4.12 KGE `Q/kge.py`
TransE, 차원 32, 300 에폭, lr 0.02, 마진 1, 시드 7, 삼중주 4개 미만 거부, SAME_AS 제외. 확률 = 시그모이드(k·(m−d)), m=(μ⁺+μ⁻)/2, k=4/(μ⁻−μ⁺). 통계 MRR·Hits@3(학습 집합). 모델은 스키마당 하나 SQLite에 JSON.

## 5. 그래프 쓰기 계약 `Q/ingest_gate.py`
- 엔터티 `:81-99`: `MERGE (n:_Entity:<Class> {_source_id: key})` ON CREATE `created_at, _confidence, _run_id, _evidence_ref, _source_system, _source_key`, 항상 `updated_at`, `name = coalesce(name, $name)`. key = 명시 id 또는 `클래스:이름` `:37-43`.
- 관계 `:119-135`: 양 끝 MERGE 후 `MERGE (s)-[r:<PRED>]->(o)` ON CREATE `created_at, _confidence, _run_id, _evidence_ref`.
- 속성 `:137-144`: 주어 MERGE 후 `SET s.<prop> = value`(덮어씀).
- SAME_AS `:154-174`: 두 키 사전순 방향, `MATCH`(없으면 REL_ENDPOINT_MISSING), `MERGE`, ON CREATE `created_at, _confidence, method, _run_id, since`. 자기 자신이면 ER_CONFLICT.
- `_evidence_ref` 형식 `doc#chunk_id@page:start-end` `:46-57`.
- 트랜잭션 메타데이터 `{actor, source: "extract:<run_id>"|"identity:<run_id>", reason}` `:33-34, 111` — A2 Bolt 게이트웨이가 감사 로그로 남김.

## 6. 저장 (`Q/store.py:26-161`) — Studio 관리 DB(sessions.db, A2/A3)에 테이블 추가, 모두 스키마 삭제 시 CASCADE
| 테이블 | 키 필드 |
|---|---|
| quality_policy | schema_id PK, policy_json |
| extraction_runs | run_id(`run_<12hex>`), source_kind(llm_extract/structured/parser?/redrive/identity/impute/manual), source_ref, policy_json, stats_json, actor, started/finished_at |
| triple_candidates | id(`cand_<16hex>`), fingerprint UNIQUE(schema), kind(entity/relation/property/tbox/identity), subject/object/value/evidence/scores/edit JSON, s_c, reasons, status(auto_ingested/pending/approved/edited/rejected/dlq), reviewer, decided_at |
| review_feedback | decision, before_json, after_json, reviewer — few-shot·학습 원천 |
| dlq_items | id(`dlq_<16hex>`), stage(source/extract/gate/shape/identity/lint/write), candidate_id(후보 id 또는 `shape:`/`orphan:`/`conflict:`/`row:`/`table:` 표식), payload_json, reason_code, reasons, detail, attempts, status(open/redriven/discarded), first_seen, last_attempt |
| quality_rules | layer(source/shape), target, rule_json, enabled |
| validation_reports | layer(source/shape/lint/identity/impute/kge/checkup), target, report_json |
| identity_preferences | (schema, cluster_key, property) PK, value_json, source, reviewer |
| kge_models | schema PK, model_json, stats_json |

- 관찰: parser 경로는 `extraction_runs`에 run을 남기지 않는다(FE 사전엔 `parser`가 있으나 백엔드에서 `parser` source_kind로 start_run 하는 곳 없음).
- DLQ `add_dlq`는 같은 candidate_id의 열린 행이 있으면 새 행 대신 갱신 `:440-468`(candidate_id가 빈 파서 항목은 매번 새 행).

## 7. 에이전트 도구 (`Q/tools.py`)
| 도구 | 인자 | 동작 |
|---|---|---|
| `extract_triples` | source(텍스트 또는 `/workspace/` 경로), schema_name, samples | 샌드박스 파일 다운로드 → `run_extraction`(actor `studio:agent`, max_chunks 50) → 통계 + note 「검수 대기(pending)와 DLQ 항목은 사용자가 품질 화면에서 판단합니다. 대신 승인하거나 재처리하지 마세요.」 |
| `quality_report` | schema_name | summary(정책 제외) |
| `table_ingest` | source, mapping_json, schema_name, dry_run | 업로드 폴더 → `/workspace/` 다운로드 → 로컬 경로 순으로 파일 찾기 → `tabular.ingest`(actor `studio:agent`) → `{blocked, dry_run, rows, stats, failed_rules, note}` |
| `quality_checkup` | schema_name | `checkup.run` + `review` = review_status |
- 결정·재처리·폐기·정책·대표 값 도구는 없음. 스킬 `SK/ontology-build/SKILL.md:133-139, 195-198, 222-224`, `SK/ontology-build/references/quality-review.md` — Phase 4에서 `quality_checkup` 한 번, 3–5줄 안내, 승인·재처리 대행 금지, 규칙 완화 금지.

## 8. 환경 변수
`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `MINOR_MODEL`(studio.env 노출), `QUALITY_EXTRACT_MODEL`, `QUALITY_EXTRACT_LOGPROBS`, `QUALITY_CHUNK_CHARS`(1800), `QUALITY_HEADER_CHARS`(400), `INGEST_GATE`(기본 true) — 뒤 5개는 studio.env 예시에 없음.

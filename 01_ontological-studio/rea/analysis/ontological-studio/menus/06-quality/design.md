# M6 품질 검수 — 설계 문서

- 기준: Ontological Studio 0.1.1 관찰 결과(정적 분석). 클린룸 문서(ADR-0002, 0011): 원본 코드·파일 경로·내부 함수 이름을 담지 않는다. 화면 문구·API 경로·요청/응답 필드·원인 코드·그래프 속성 이름은 외부에서 관찰 가능한 계약이라 적는다.
- 상태: 초안 v1 (정적 분석). "모르는 점"은 4단계 실행 기록에서 확정한다.

## 1. 목적
온톨로지 구축(M1)이 문서·표·파서에서 뽑은 **지식 요소(엔터티·관계·속성·스키마 제안·동일 개체 제안)를 그래프에 바로 쓰지 않고**, 결정적 스키마 검사와 복합 신뢰도 점수로 세 갈래로 나눈다.

| 갈래 | 조건 | 처리 |
|---|---|---|
| 자동 적재 | 스키마 위반 없음, 점수 ≥ 자동 하한, 검수 플래그 없음 | 즉시 그래프에 MERGE |
| 확인하기(검수 대기) | 점수가 두 하한 사이, 또는 검수 플래그(추론·유사어·타입 불일치 등) | 사람이 승인/수정/기각 |
| 보류함(DLQ) | 스키마 위반, 점수 < 검수 하한, 원천 규칙 위반, 쓰기 실패, 사후 점검 문제 | 원인별로 사람이 고치고 다시 시도/버리기 |

또한 이미 들어간 지식 지도를 **점검**(필수 값 누락·타입·연결 규칙·고립 노드·다른 원천의 같은 대상·값 충돌·빠진 값 제안)한다. **판단은 항상 사람이 한다**: 에이전트에게는 추출 요청·점검·현황 조회 도구만 주고 결정·재처리 도구는 주지 않는다(구조적으로 강제). 사람의 판정은 다음 추출의 예시(few-shot)와 학습 데이터 내보내기에 쓰인다.

## 2. 사용자 시나리오 (요약)
`user-scenarios.md` S1–S15.
- 기본 화면: S1 한눈에 · S2 확인하기(카드 판단) · S3 고쳐서 넣기 · S4 스키마 제안 승인 · S5 지금 점검하기 · S6 보류함 원인별 고치기 · S7 빠진 값 입력 · S8 고립 노드 재추출 · S9 대표 값 선택 · S10 구축 화면 「검수」 탭·보고서 카드
- 고급: S11 검수 큐·일괄·판정 이력 · S12 추출 실행 · S13 원천 CSV 검증·형상·고립 · S14 식별자·결측 보정 · S15 KGE·내보내기·정책

## 3. 구성 요소와 통신
```
[Studio 화면: 품질 검수 뷰 / 구축 화면 「검수」 탭] --HTTP JSON--> [Studio 백엔드 /api/quality/*]
[구축 에이전트(M1, 내장 또는 외부 CLI via MCP)] --도구 4개--> [같은 품질 파이프라인]
품질 파이프라인 ── 관리 DB(SQLite, 스키마 정의와 같은 DB): 후보·DLQ·판정·정책·규칙·보고서·대표 값·임베딩 모델
               ── 그래프(Bolt, A2): 통과한 것만 MERGE, 점검용 읽기 질의
               ── OpenAI 호환 API: LLM 추출(채팅 JSON 모드), 문장 임베딩
```
- 그래프 쓰기는 파이프라인 안의 **단일 쓰기 경로**만 사용한다(자동 적재, 사람 승인, 사람 입력, 동일 개체 링크 모두).
- 인증 없음(로컬 백엔드, A1/A3와 같음). 검토자 이름은 화면이 `studio-user`로 보낸다.

## 4. 데이터 모델

### 4.1 후보 (candidate) — API 응답 형태
```
{ id, schema_id, run_id, fingerprint,
  kind: "entity"|"relation"|"property"|"tbox"|"identity",
  subject: {name, class, id?, source_system?, source_key?, aliases?},
  predicate: string,            // 관계 술어 / 속성 이름 / identity면 "SAME_AS"
  object: {name, class, id?} | tbox 제안 {kind:"class"|"relationship", name, description, from_class, to_class, reason},
  value: any,                   // property
  evidence: [ {doc, chunk_id, page, quote, text, chunk_start, start?, end?, sentence?, header?, row?} ],  // 최대 20
  scores: {s_llm, s_ground, s_graph, g_onto, m_vocab, s_c, route, hard[], soft[],
           logprob, freq, lexical, cos, cos_norm, distance, graph_paths, graph_endpoints_known,
           graph_direct, kge, flags[], method, notes[], policy:{w:[3], combine, auto, review}},
  s_c: number, reasons: [code], status: "auto_ingested"|"pending"|"approved"|"edited"|"rejected"|"dlq",
  reviewer, decided_at, edit: {}, created_at, updated_at }   // 시각은 epoch 초(실수)
```
- **지문(중복 키):** 스키마 + 종류 + 주어 키(클래스:id 또는 이름, 소문자) + 술어 + (관계면 목적어 키) + (속성이면 값 소문자). tbox는 종류·이름·from·to, identity는 두 키를 정렬한 쌍. 같은 사실을 다시 뽑으면 같은 행이 되고 근거만 합쳐진다(근거 = (chunk_id, start) 기준 중복 제거, 20개 한도).
- **사람 판정 보존:** 이미 approved/edited/rejected인 지문은 재추출·재처리에서 점수를 다시 매기지 않고 그대로 둔다(근거만 추가, 통계 `preserved`).

### 4.2 보류 항목 (DLQ item)
```
{ id, schema_id, stage: "source"|"extract"|"gate"|"shape"|"identity"|"lint"|"write",
  source_ref, candidate_id, payload, reason_code, reasons[], detail, attempts,
  status: "open"|"redriven"|"discarded", first_seen, last_attempt,
  reason_description }  // 목록 응답에서 추가
```
- `candidate_id`는 후보 id이거나 사후 점검 항목의 표식: `shape:<shape id>:<노드 키>`, `orphan:<노드 키>`, `conflict:<묶음 키>:<속성>`, `row:<파일>:<행 index>`, `table:<파일>`. 같은 표식의 열린 항목이 있으면 새로 만들지 않고 갱신한다(점검을 반복해도 중복 없음).
- payload 종류: 후보 자체(`kind` 있음), `{source:"tabular", filename, session_id, mapping, row?, row_index?}`, `{source:"shape", shape, node{key,name,source_system}, value?}`, `{source:"lint", node{key,name,source_system,class}}`, `{source:"identity", cluster_key, class, property, values[{value,source,key}], members[]}`, `{source:"parser", node | relationship}`, 추출 실패 `{chunk_id, doc, text}`.

### 4.3 기타 저장 (스키마 삭제 시 함께 삭제)
- 정책(스키마당 1), 실행 기록 `{run_id, source_kind, source_ref, stats, actor, started_at, finished_at}` — source_kind: `llm_extract`, `structured`, `identity`, `impute`, `manual`, `redrive`.
- 판정 이력 `{decision: approve|edit|reject, before, after, reviewer, created_at}`.
- 사용자 규칙(원천/형상), 검증 보고서(layer: source/shape/lint/identity/impute/kge/checkup), 대표 값 `(묶음, 속성) → {value, source, reviewer}`, KGE 모델(스키마당 1, JSON).

### 4.4 정책 (스키마별, `GET/PUT /api/quality/policy/{schema_id}`)
| 필드 | 기본 | 뜻 |
|---|---|---|
| w_llm / w_ground / w_graph | 0.3 / 0.5 / 0.2 | 세 지표 가중치(합 1) |
| combine | `linear` | `linear` 가중합 / `harmonic` 가중 조화평균 |
| auto_threshold / review_threshold | 0.85 / 0.60 | 자동 적재 하한 / 검수 하한 |
| alpha | 0.5 | S_llm 안 logprob 비중 |
| decay_lambda | 0.02 | 단어 거리 감쇠 |
| samples | 3 | 청크당 추출 반복 수 |
| cos_floor / cos_ceil | 0.15 / 0.60 | 코사인 늘림 구간 |
| graph_prior | 0.5 | 그래프 지지 근거가 없을 때 S_graph |
| open_vocabulary_when_empty | true | 스키마에 관계가 0개면 술어 자유 |
| synonym_min_ratio | 0.82 | 술어 유사어 인정 하한 |
| identity_auto / identity_review | 0.95 / 0.80 | 동일 개체 자동 연결 / 검수 제안 하한 |
| kge_weight | 0.5 | 임베딩 확률의 S_graph 비중 |
| impute_min_share / impute_min_support | 0.6 / 2 | 이웃 패턴 보정 최소 비율·건수 |

검증(실패 시 422, 메시지를 `; `로 연결): 가중치 합 1(오차 1e-6) 「가중치 합이 1 이어야 합니다 (현재 x.xxx)」, combine 값, `0 ≤ review ≤ auto ≤ 1`, alpha 0~1, samples 1~10, cos_ceil > cos_floor. PUT 본문은 `{policy:{…}}` 또는 필드 자체, 기존 값에 병합, 모르는 키·형 변환 불가 값은 무시. 변경은 이후 실행부터 적용.

## 5. 판정 규칙 (결과를 좌우 — 반드시 같은 동작으로)

### 5.1 원인 코드 (문자열이 계약 — 이름 변경 금지, 추가만)
- **hard(즉시 보류):** ID_MISSING, REL_ENDPOINT_MISSING, ONTO_CLASS_UNKNOWN, ONTO_DOMAIN, ONTO_RANGE, ONTO_PREDICATE_UNKNOWN, ONTO_PROPERTY_UNKNOWN, ONTO_CARDINALITY, ONTO_INVALID_NAME, PARSE_JSON
- **soft(자동 적재 금지 → 검수):** PROP_DATATYPE, ENTITY_AMBIGUOUS, PREDICATE_SYNONYM, TBOX_PROPOSAL, IMPUTED, LINK_PREDICTED, SAME_AS_PROPOSAL, ENTITY_GENERIC
- **항상 검수(점수 무관):** TBOX_PROPOSAL, IMPUTED, LINK_PREDICTED, SAME_AS_PROPOSAL, ENTITY_GENERIC
- 그 밖: LOW_CONFIDENCE, WRITE_FAILED, SRC_NULL_RATIO, SRC_RANGE, SRC_UNIQUE, SRC_FK, SRC_IN_SET, SRC_TABLE_BLOCKED, SHAPE_MIN_COUNT, SHAPE_MAX_COUNT, SHAPE_DATATYPE, SHAPE_DISJOINT, ORPHAN_NODE, ER_CONFLICT
- 설명 문구(`GET /api/quality/codes`의 `codes`, 화면 툴팁): 예) ONTO_DOMAIN 「관계 정의역(domain) 위반」, LOW_CONFIDENCE 「복합 신뢰도 S_c 가 하한 미만」, TBOX_PROPOSAL 「스키마(TBox) 변경 제안 — 항상 전문가 승인」, ENTITY_GENERIC 「‘본 증권’·‘당사’ 같은 지시어를 이름으로 씀 — 문서마다 다른 대상을 가리킨다」 (전체 목록은 4단계 기록에서 그대로 채록).

### 5.2 스키마 게이트 (결정적)
- 이름 규칙: 영문·한글·밑줄로 시작하고 영문·숫자·한글·밑줄만.
- 엔터티(관계의 양 끝 포함): 이름과 id가 모두 없으면 ID_MISSING; 클래스가 없으면 ONTO_CLASS_UNKNOWN; 클래스 이름이 규칙 위반이면 ONTO_INVALID_NAME; 스키마에 클래스가 하나라도 있으면 미등록 클래스는 ONTO_CLASS_UNKNOWN. id 없이 이름이 **문서 지시어**(본/동/당/해당/이/그/위 + 증권·사채·상품·회사·계약·파생결합…·투자설명서·펀드·기초자산·발행인, 또는 당사·발행인·발행회사·투자자·증권사·회사·상품·기초자산·금융투자상품 단독)이면 ENTITY_GENERIC.
- tbox: 항상 TBOX_PROPOSAL, 제안 이름이 규칙 위반이면 ONTO_INVALID_NAME.
- identity: 두 엔터티 검사, 클래스가 다르면 ONTO_RANGE, 항상 SAME_AS_PROPOSAL.
- property: 속성 이름 규칙 위반이면 hard; 클래스에 선언 속성 목록이 있는데 없는 속성이면 ONTO_PROPERTY_UNKNOWN; 선언 타입과 값이 안 맞으면 PROP_DATATYPE.
  - 타입 판정: 타입이 없거나 문자열류(string/str/text/varchar/char/any/unknown)·값이 비면 통과. 정수: 부호·숫자·쉼표. 실수: 숫자·소수점·지수(숫자 하나 이상). 불리언: true/false/0/1/y/n/yes/no/예/아니오. 날짜·일시: ISO 형식(`/` `.`을 `-`로, 첫 공백을 T로 바꿔 해석) 또는 「YYYY년 M월 (D일)」.
  - 적재할 때는 선언 타입으로 변환(정수·실수는 쉼표 제거, 불리언).
- relation: 술어가 비면 ONTO_PREDICATE_UNKNOWN. 스키마에 관계가 하나도 없으면 이름 규칙만 맞으면 통과(부트스트랩). 아니면 술어 맞추기: ① 정확히 같음 ② 공백·`_`·`-` 제거·소문자 비교 ③ 관계 이름과 관계 설명들에 대한 문자열 유사도(설명에 술어가 포함되면 최소 0.9) 최고값 ≥ synonym_min_ratio → 그 관계로 바꿔 읽고 m_vocab = 유사도, PREDICATE_SYNONYM. 실패하면 ONTO_PREDICATE_UNKNOWN. 같은 이름의 관계가 여러 (from, to)로 선언될 수 있다: 주어 클래스가 어떤 정의의 from과 같으면 정의역 통과, 그 정의들 중 to가 목적어 클래스와 같으면 공역 통과(정의역 실패 시엔 아무 정의의 to와 비교). 실패 시 ONTO_DOMAIN / ONTO_RANGE와 메모 「REL 정의역: [..], 받은 값: X」.
  - 카디널리티(ONTO_CARDINALITY): 원본엔 (클래스, 술어) 최대 개수 검사 자리가 있으나 한도를 설정하는 경로가 없어 동작하지 않는다. 재구현 시 코드만 예약해 둔다.

### 5.3 복합 신뢰도
`S_c = G_onto × m_vocab × 결합(S_llm, S_ground, S_graph)`, G_onto = hard 위반 있으면 0 아니면 1. 모든 값은 0~1로 자른다.
- **S_llm:** 같은 청크를 M번 추출해 그 사실이 나온 비율(freq). 토큰 로그확률을 쓸 수 있으면 α·exp(평균 logprob) + (1−α)·freq. 기본은 logprob 미사용.
- **S_ground:** 감쇠 × (½·어휘 근거 + ½·정규화 코사인).
  - 어휘 근거 = 언급(주어 이름; 관계면 목적어 이름; 속성이면 값)들 중 근거 텍스트(+문서 머리말)에서 대소문자·공백 차이 무시하고 찾은 비율.
  - 코사인 = 「사실 문장」(관계: `주어 술어 목적어`, 속성: `주어의 속성은(는) 값단위`, tbox: `이름: 설명`, 엔터티: `이름 (클래스)`) 임베딩과 「인용이 들어 있는 원문 문장(못 찾으면 청크)」 임베딩의 코사인을 (cos − 0.15)/(0.60 − 0.15)로 늘림. 임베딩이 없거나 실패하면 어휘 근거로 대신.
  - 감쇠 = e^(−λ·d), d = 원문에서 주어·목적어의 **가장 가까운** 출현 사이 단어 수(관계만, 못 찾으면 1).
  - 정형 원천·식별자·보정처럼 근거 값을 직접 주는 경로는 그 값을 쓴다(정형 1, 보정·링크 예측 0).
- **S_graph(관계만 의미):** 같은 관계가 이미 그래프에 있으면 1. 양 끝이 그래프에 있고 2~3홉 우회 경로가 있으면 max(prior, 1 − e^(−Σ 경로별 엣지 확신의 곱)) (확신 기록이 없는 엣지는 0.7, 경로 25개까지). 그 외 prior(0.5). 학습된 임베딩 모델이 있고 직접 관계가 없으면 (1 − kge_weight)·S_graph + kge_weight·임베딩 확률. 그래프 읽기 실패 시 prior.
- **결합:** linear = Σ wᵢ·vᵢ; harmonic = 1/Σ(wᵢ/vᵢ)(가중치 0인 항 제외, 값 하나라도 0이면 0).
- **엔터티 모호성:** 엔터티 후보는 발행된 그래프의 엔터티 해소(M2 계열 기능)로 상위 2개 점수 차가 0.15 미만이면 ENTITY_AMBIGUOUS. 해소 서비스가 없으면 생략.
- **분기:** hard 있음 → 보류; S_c < review → 보류(원인 LOW_CONFIDENCE); S_c ≥ auto 이고 soft 없음 → 자동; 나머지 → 검수. 단 hard가 없고 (tbox 이거나 항상-검수 플래그가 있으면) 점수와 무관하게 검수.
- 쓰기 실패 시 후보 status `dlq` + 보류(stage write, WRITE_FAILED).
- 이전에 보류됐던 지문이 이번엔 보류가 아니면 그 열린 보류 항목을 `redriven`(「재실행에서 통과」)으로 닫는다.

### 5.4 문서 추출 (LLM)
- 텍스트를 빈 줄 단락 단위로 묶어 청크(기본 1800자, 너무 긴 단락은 공백 기준으로 자름, 원문 문자 오프셋 유지, id `<문서이름 정리>#cNNNN`). 문서 머리말 = `문서: <이름>` + 앞 400자.
- 요청당 최대 청크 수(화면 기본 50, 에이전트 50, 재처리 5).
- 모델 입력: **지시문**(아래 규칙) + **값 블록**: [문서 머리말], [허용 클래스](클래스 — 설명 (속성: 이름:타입, …) / 없으면 「(없음 — 부트스트랩)」), [허용 관계](`이름: from -> to — 설명`), [검수 예시](최근 판정 8개: 「승인/수정 후 승인/기각: {JSON(근거 제외)}」, 승인·수정은 고친 뒤 값, 기각은 원래 값), [청크].
- 지시문 요지(자기 말로 재작성할 것): 청크에 명시된 사실만; 관계 술어는 허용 목록 이름 그대로; 맞는 관계·클래스가 없으면 데이터로 만들지 말고 스키마 제안으로; 모든 항목에 원문을 글자 그대로 복사한 최소 인용(없으면 내지 않음); 이름은 원문 표기(정식 명칭 우선, 약어는 aliases); 추론한 관계 금지; 값은 원문 그대로, 단위 분리; 지시어를 이름으로 쓰지 말고 머리말의 정식 이름으로 바꾸거나 생략; 표 머리말·예시는 사실이 아님; 숫자 타입이면 숫자만. 출력 JSON 객체 하나:
  ```
  {"entities":[{"name","class","aliases":[],"quote"}],
   "relations":[{"subject":{"name","class"},"predicate","object":{"name","class"},"quote"}],
   "properties":[{"subject":{"name","class"},"property","value","unit","quote"}],
   "tbox_proposals":[{"kind":"class|relationship","name","description","from_class","to_class","reason","quote"}]}
  ```
- JSON 모드로 M번 호출. 코드 펜스는 벗긴다. 한 샘플 파싱 실패는 빈도만 낮춤. M번 모두 실패하고 후보가 0이면 그 청크를 보류(stage extract, PARSE_JSON, payload `{chunk_id, doc, text}`).
- 인용을 청크에서 찾으면 근거에 start/end(문서 기준 오프셋)와 그 문장(문장 경계 `. ! ? 。`·「다.」·줄바꿈, 600자 넘으면 인용 앞뒤 120자)을 넣는다.
- 스키마 제안은 kind가 class/relationship이고 이름이 있을 때만 후보가 된다.
- 모델: 설정 변수 `QUALITY_EXTRACT_MODEL` → 없으면 보조 모델 설정(`MINOR_MODEL`). OpenAI 호환 API 키 없으면 503 「OPENAI_API_KEY 가 없어 LLM 추출을 할 수 없습니다.」 임베딩은 같은 API(또는 로컬 임베딩 서버).
- 응답(실행 통계): `{run_id, chunks, samples, total, auto_ingested, pending, dlq, preserved, write_failed, parse_errors, by_reason{code:n}}`.

### 5.5 정형 파일(CSV) 적재
- 매핑: `{source_system, class, key, name?, properties{열:속성}, relations[{column, predicate, target_class}], expectations[규칙]}`. source_system·class·key 필수, 매핑이 가리키는 열이 파일에 없으면 422 「파일에 없는 컬럼: [...]」. 인코딩 UTF-8(BOM 허용) → CP949 → EUC-KR.
- 원천 규칙: `not_null`(column, max_ratio 기본 0: 빈 값 비율 ≤ 기준), `between`(min/max 중 하나 이상, 숫자 아니면 실패, 빈 값 무시), `unique`(중복된 행 전부), `in_set`(values 목록), `fk`(ref.values 또는 그래프의 ref.class·ref.property 값). `severity`: `row`(기본, 실패 행만 격리) / `block`(실패 시 파일 전체 중단). 규칙 오류는 422(「알 수 없는 규칙: …」 등).
- 결과 보고서: `{rows, rules[{type, column, severity, code, passed, observed, threshold, failing_rows(50), failing_count}], blocked, failing_rows{행:코드[]}, passed_rows, file}`. `dry_run`이면 보고서만.
- block 실패 → 보류 1건(stage source, SRC_TABLE_BLOCKED), 아무것도 넣지 않음. 행 실패 또는 키 빈 행 → 행별 보류(첫 원인 코드, 키 없음은 ID_MISSING).
- 통과 행 → 후보: 엔터티(id `원천시스템:키`, 이름 열, source_system, source_key), 빈 값이 아닌 속성마다 property, 관계 열마다 relation(목적어 `{name: 값, class: target_class}` → 키 `클래스:이름`). 근거 `{doc: 파일, chunk_id: "파일#row<줄>", row: 줄번호(헤더 포함 1부터 → 데이터 i는 i+2), text: "열=값, …"}`. 신호 freq 1·ground 1 → 게이트·S_graph는 그대로 적용.
- 응답 `{report, blocked, stats(+rows_loaded, rows_quarantined), run_id}`.

### 5.6 파서 경로(M1의 일괄 적재 도구) 선별
점수 없이 구조만 본다: 노드 id 없음 → ID_MISSING, 클래스 없음/이름 규칙 → ONTO_CLASS_UNKNOWN/ONTO_INVALID_NAME, 관계 타입 이름 규칙, 양 끝이 이번 묶음에도 그래프에도 없음 → REL_ENDPOINT_MISSING, 스키마에 선언된 관계면 아는 쪽의 정의역·공역. **미등록 클래스는 막지 않는다**(파서 적재 뒤 스키마를 등록하는 흐름 보존). 걸린 것은 보류(stage gate, payload.source=parser)로, 도구 응답에 `quarantined{count, by_reason, samples(5)}`. 설정으로 끌 수 있음(기본 켬).

### 5.7 사후 점검
「지금 점검하기」와 에이전트 점검 도구는 **같은 동작**을 한다: 형상 → 고립 → 동일 개체 → 결측 보정 순서.
- **형상:** 스키마 속성의 `required: true` → 「필수」(값이 null인 노드), 문자열류가 아닌 `type` → 「타입」(값이 타입 판정 실패). `virtual` 속성은 제외. 사용자 규칙(현재 화면 없음): `max_count{class, predicate, max}`(나가는 관계 수 초과), `min_rel{class, predicate, min=1}`(미만 → SHAPE_MIN_COUNT), `disjoint{classes:[A,B]}`(두 라벨 동시). 대상은 `_Entity` 라벨을 가진 노드. 위반 노드마다 보류(stage shape). 이번 실행에서 안 걸린 열린 형상 보류는 해소 처리. 응답 `{shapes, violations, resolved, results[{shape, description, violations, samples(5)} | {shape, error}]}`. 설명 문구: `C.p 필수`, `C.p : type`, `C -R-> 최대 n`, `C -R-> 최소 n`, `A ⊥ B 배타`.
- **고립:** 스키마 클래스(가상 바인딩 클래스 제외)의 노드 중 SAME_AS 외 관계가 하나도 없는 것 → 보류(stage lint, ORPHAN_NODE, 상세 「C 'name' — 관계 없음, 관계 재추출 대상」). 응답 `{orphans, resolved, samples(10)}`.
- **동일 개체:** 클래스별 노드 모든 쌍(같은 정형 원천 시스템끼리는 제외, 「문서 추출」 노드끼리는 비교). 이미 SAME_AS면 건너뜀. 점수: 식별 속성(선언 `identifier: true` 또는 이름 biz_no/business_no/duns/lei)이 양쪽 다 있으면 숫자만 비교 또는 문자열 동일 → 1.0, 다르면 0.0; 없으면 이름 정규화(법인 표기 「(주)·㈜·주식회사·(유)·유한회사·co.,ltd·inc·corp·corporation」 및 공백·구두점 제거, 소문자) 같으면 0.97, 다르면 문자열 유사도. ≥ identity_auto → SAME_AS 즉시 연결(후보 기록 auto_ingested), ≥ identity_review → identity 후보(검수). 응답 `{auto_linked, auto(20), proposals, conflicts}`.
- **값 충돌:** SAME_AS로 이어진 묶음(연결 요소)에서 같은 속성에 서로 다른 값이 2개 이상이고 대표 값이 없으면 보류(stage identity, ER_CONFLICT, 상세 `이름.속성: 원천=값 / …`). 그래프 값은 절대 덮지 않는다.
- **결측 보정 제안**(한 (노드, 속성)에 하나, 우선순위 순): ① SAME_AS 상대가 가진 값 ② 같은 이웃에 같은 관계 타입으로 붙은 같은 클래스 노드들의 최빈값(지지 ≥ 2, 비율 ≥ 0.6) ③ 속성 선언의 `default` ④ 임베딩 링크 예측: 선언 관계의 출발 클래스 노드 중 그 관계가 없는 것에 대해 상위 5 꼬리 중 도착 클래스가 맞고 확률 ≥ 0.7인 첫 하나(최대 20건). 모두 IMPUTED/LINK_PREDICTED로 검수행. 근거 문구 예: 「동일 개체 ERP '…' 의 p='v'」, 「'X' 에 R 로 연결된 C n건 중 k건이 p='v'」, 「C.p 클래스 기본값 'v'」, 「TransE 링크 예측: (h, R, ?) → t p=0.83」. 응답 `{same_as, class_default, neighbor_pattern, kge_links, pending, dlq}`.
- **점검 요약 응답:** `{missing_values, wrong_format, link_rules, resolved, unlinked, same_entity_linked, same_entity_to_confirm, value_conflicts, suggestions, details{shapes, lint, identity, impute}}`.

### 5.8 사람의 결정 `POST /api/quality/candidates/{id}/decide`
요청 `{decision: "approve"|"reject"|"edit", reviewer, edit?}`.
- 이미 approved/edited/rejected/auto_ingested면 422 「이미 처리된 후보입니다 (status)」. `dlq` 상태 후보도 결정할 수 있다(「그래도 넣기」).
- reject: 상태 rejected, 판정 기록(before), 이 후보의 열린 보류를 discarded. 응답 `{status:"rejected", id}`.
- tbox approve/edit(`edit.tbox`로 이름·설명 덮기): 이름 규칙 검사 후 **스키마에 클래스/관계 추가**(출처 = 사람 검수로 기록), 상태 approved/edited. 응답 `{status, id, applied:"schema"}`.
- identity: edit 불가(422 「동일 개체 제안은 승인·기각만 됩니다」). 승인 시 SAME_AS 쓰기.
- 그 외 approve/edit: edit 병합(subject·object는 필드 단위 덮기, predicate, value) → **스키마 게이트 재검사**, hard가 있으면 422 「스키마 제약 위반으로 적재할 수 없습니다: CODE(설명), … — 메모」(사람이 승인해도 스키마를 어기는 사실은 쓰지 않는다) → 유사어면 정규 술어로 → 그래프 쓰기(확신값 = max(후보 S_c, 자동 하한), 감사 reason `hitl:approve`/`hitl:edit`, actor = reviewer). 쓰기 실패면 422 「그래프 쓰기 실패: …」. 성공 시 상태 approved/edited, 후보 내용 갱신, 판정 기록(before/after), 묶인 보류 redriven. 응답 `{status, id, applied:"graph"}`.
- 일괄 `POST /candidates/bulk-decide {ids, decision(approve|reject), reviewer}` → `{results:[결정 응답 | {id, error}]}`; 그 외 decision 422 「일괄 처리는 approve | reject 만 됩니다」.

### 5.9 보류 다시 시도 `POST /api/quality/dlq/redrive`
요청 `{ids?, schema_id?, reason_code?}` — ids가 비면 그 스키마(·코드)의 열린 항목 전부(1000), 대상 없으면 422 「재처리할 항목이 없습니다」. 응답 `{results:[{id, outcome, …}]}`. 항목별(실패가 묶음을 멈추지 않음), 시도 수 +1:

| 항목 | 다시 시도의 뜻 | outcome |
|---|---|---|
| 열려 있지 않음 | — | `skipped` |
| 추출 실패(stage extract) | 저장된 청크 텍스트로 재추출(최대 5청크) | `reextracted{run_id}` / `still_failing` |
| 파서 항목 | 같은 일괄 적재 도구로 다시 넣음(같은 선별) | `ingested` / `still_failing`(다시 걸리면 새 보류가 생기고 이 항목은 닫힘) |
| 원천 행 | **현재 파일**을 다시 읽어 같은 키(없으면 같은 위치) 행을 재검사 → 통과면 그 행만 적재 | `ingested{stats}` / `still_failing{reasons}` / 「행을 찾지 못함」 |
| 원천 파일 전체 차단 | 현재 파일로 전체 적재 재실행 | `ingested` / `still_failing` |
| 형상 | 그 shape를 다시 검사, 그 노드가 더는 안 걸리면 해소 | `resolved` / `still_failing` |
| 고립 | 그 이름이 나온 원문(문서 근거, 최대 3개)을 재추출 → 여전히 고립인데 새 검수 후보가 생기면 항목 닫음 | `queued_for_review{pending}` / `reextracted` / `still_failing`(원문 없음: 「이 엔터티를 언급한 원문이 없습니다 — 문서를 추가하세요」) |
| 값 충돌 | 충돌 재탐지(대표 값을 골랐으면 해소) | `resolved` / `still_failing` 「대표 값을 고르면 해소됩니다」 |
| 후보(gate/write) | 후보를 대기로 돌리고 **현재** 스키마·정책으로 전체 판단 재실행 | `ingested` / `queued_for_review` / `still_failing{reason_code, attempts, exhausted(≥3)}` |
| 그 밖 | — | `unsupported_stage` |
- 3회 한도는 표시용(`exhausted`)이며 재시도를 막지 않는다(원본과 같게).
- 버리기 `POST /dlq/{id}/discard` → `{id, status:"discarded"}`; 묶인 후보가 dlq면 rejected. 없으면 404.

### 5.10 사람 입력·대표 값
- `POST /api/quality/manual-value {schema_id, key, name, class_name, property, value, reviewer}`: 노드 키(`_source_id`)·클래스·속성으로 property 후보를 만들어(근거 「사람 입력 / reviewer 가 직접 입력」, S_c 1.0) 즉시 승인 경로(§5.8)로 쓴다. 실패하면 그 후보를 rejected로 남기고 422. 성공하면 형상 검증을 다시 돌려 응답에 `resolved` 수 추가.
- `POST /api/quality/identity/conflicts/{dlq_id}/resolve {value, source, reviewer}`: 값 충돌 항목이 아니면 422 「식별자 충돌 항목이 아닙니다」. 대표 값 기록, 항목 redriven(상세 「대표 값 선택: v (source)」). 응답 `{id, preferred, source}`. 그래프는 바꾸지 않는다.
- `GET /api/quality/identity/clusters` → `[{cluster_key(묶음 대표 키), class, members[{key,name,source_system}], properties{p:{values[{value,source,key}], conflict, preferred, canonical}}}]` (2개 이상인 묶음만; canonical = 대표 값, 없으면 값이 하나일 때 그 값).

### 5.11 그래프 임베딩 (선택 기능)
- 학습 `POST /kge/train`: 스키마 클래스 노드 사이 관계(SAME_AS 제외) 삼중주로 TransE(차원 32, 300 에폭, 학습률 0.02, 마진 1, 고정 시드). 4개 미만이면 422. 확률 보정: 양성 거리 평균 μ⁺, 무작위 음성 평균 μ⁻ → p = 1/(1+e^(−k(m−d))), m=(μ⁺+μ⁻)/2, k=4/(μ⁻−μ⁺). 응답 통계 `{triples, entities, relations, epochs, final_loss, first_loss, mu_pos, mu_neg, seconds, mrr, hits_at_3}`.
- `GET /kge` → `{trained:false}` 또는 통계 + `trained_at, entity_keys[], relation_names[]`. `GET /kge/score?h&r&t` → `{h, r, t, probability, distance, top_tails[{t, probability}]×3}`, 모델 없음/모르는 키는 422.
- 순수 언어 구현으로 충분(수천 삼중주, 수 초). 재구현 시 외부 라이브러리 사용 가능.

### 5.12 내보내기
- `GET /export/feedback.jsonl?schema_id` (application/jsonl): 판정 1건 = `{"decision", "label": 승인·수정이면 true, "messages":[{"role":"user","content": 근거 인용(없으면 텍스트 앞 300자) 공백 연결}, {"role":"assistant","content": JSON(승인·수정은 after, 기각은 before, 근거 제외)}]}`.
- `GET /export/kge-triples.tsv?schema_id`: `h\tr\tt` 줄(그래프의 현재 관계).

## 6. 그래프 쓰기 계약 (M1·M2와 공유)
- 엔터티: 라벨 `_Entity` + 클래스 라벨, 키 속성 `_source_id` = 명시 id(정형은 `원천:키`) 또는 `클래스:이름`. 생성 시 `created_at`, `_confidence`, `_run_id`, `_evidence_ref`, `_source_system`, `_source_key`; 매번 `updated_at`; `name`은 비어 있을 때만 채움.
- 관계: 양 끝 MERGE 후 술어 타입 관계 MERGE, 생성 시 `created_at`, `_confidence`, `_run_id`, `_evidence_ref`; 매번 `updated_at`.
- 속성: 주어 MERGE 후 그 속성을 값으로 SET(덮어씀). 값은 선언 타입으로 변환.
- 동일 개체: 두 키를 사전순으로 정렬해 앞 → 뒤 방향 `SAME_AS`(중복 방지), 생성 시 `created_at`, `_confidence`, `method`(key:<속성>/name/fuzzy), `_run_id`, `since`. 양 끝이 없으면 REL_ENDPOINT_MISSING, 같은 노드면 ER_CONFLICT.
- `_evidence_ref` = `문서[#청크][@쪽][:시작-끝]`.
- 트랜잭션 메타데이터 `{actor, source, reason}`(A2 게이트웨이가 감사로 남김): actor = `studio:auto`(자동)·`studio:ui`·`studio:agent`·`studio:redrive`·`studio:lint`·검토자 이름; source = `extract:<run_id>` 또는 `identity:<run_id>`; reason = `S_c=0.91`, `hitl:approve`, `ER name 0.97` 등.
- 그래프 예약 이름(`_id`, `_type`, `_src`, `_dst`, `__*`)은 쓰지 않는다.

## 7. 화면 구성과 상호작용

### 7.1 품질 검수 뷰 (`view=quality`)
- 머리: 제목 「지식 품질」, 온톨로지 선택(「온톨로지 선택」, 초기값 = 셸이 넘긴 현재 온톨로지, 없으면 첫 항목), 탭 「🏠 한눈에」「🙋 확인하기」「🗂️ 보류함」(배지: 대기 후보 수 / 열린 보류 수), 오른쪽 「⚙ 고급」. 토스트(오류 9초, 일반 6초). 온톨로지가 없으면 「위에서 온톨로지를 고르세요.」
- 탭을 바꾸거나 온톨로지를 바꿀 때마다 스키마 상세 + summary를 다시 읽는다.
- 「온톨로지 구축으로」 계열 버튼은 같은 탭에서 구축 뷰로 전환하며 온톨로지를 넘긴다.

### 7.2 한눈에
`user-scenarios.md` S1 문구 그대로. 「확인된 사실」 = 후보 중 auto_ingested+approved+edited 수. 「점검하지 않았어요」는 최근 실행 10건 중 동일 개체 실행이 없을 때. 최근 활동은 6건, 종류별 문구: `llm_extract` 문서에서 뽑기, `structured` 표 가져오기(— a줄 넣음, b줄 보류), `identity` 점검 (같은 대상 찾기)(— 자동 연결·확인 요청·값 충돌), `impute` 점검 (빠진 값 제안)(— 제안 n건을 확인하기로 보냄), `manual` 직접 입력, `redrive` 다시 시도. 원천 표시가 `dlq_`/`run`으로 시작하면 생략.

### 7.3 확인하기 (카드 덱)
- 대기 후보를 300개까지 불러 **S_c 높은 순, 같으면 오래된 순**. 종류 칩 전체/관계/값/항목/같은 대상/새 종류. 「확인할 내용 i / n」, 「전체 목록」(목록 행: 확신 점 + 문장).
- 카드 문장: 관계 `주어 · (관계 설명 또는 이름, 스키마에 없으면 「X (지도에 없는 관계)」) · 목적어`; 값 `주어의 · (속성 label/description 또는 기본 한글 이름표 credit_score 신용점수 등) · 값`; 항목 `이름 · 은(는) · (클래스 설명 짧게 또는 클래스명)`; 같은 대상 `A · 와(과) 같은 대상 · B`; 새 종류 `새로운 관계 · 설명(A → B)` / `새로운 종류 · 설명`.
- 확신 배지: reasons가 있고 S_c ≥ 검수 하한 → 「확인 필요」, S_c ≥ 자동 하한 → 「확실함」, ≥ 검수 하한 → 「애매함」, 그 외 「약함」.
- 이유 한 줄 우선순위: 새 종류 → 「지금 지식 지도에 없는 새로운 종류예요. 추가할지 정해 주세요.」 / 같은 대상 → 「이름이 비슷해서 같은 대상일 수 있어요.」 / 링크 예측 → 「AI가 지식 지도의 패턴을 보고 추측한 연결이에요. 원문 근거는 없어요.」 / 보정(같은 대상 값 → 「같은 대상의 다른 시스템 값을 가져온 제안이에요.」, 이웃 → 「비슷한 항목들이 대부분 이 값이라서 추정했어요.」, 그 외 「기본값으로 채운 제안이에요.」) / 유사어 → 「비슷한 관계 이름으로 바꿔 읽었어요. 맞는지 봐 주세요.」 / 타입 → 「값의 형식이 예상과 달라요.」 / 모호 → 「비슷한 이름이 여러 개 있어서 헷갈려요.」 / freq<1 → 「AI가 같은 문단을 세 번 읽었는데 {round(freq×3)}번만 이 내용을 찾았어요.」 / 어휘<1 → 「원문에서 이름을 그대로 찾지 못했어요.」 / 거리>20 → 「두 이름이 원문에서 멀리 떨어져 있어요.」 / S_graph<0.5 → 「지금 지식 지도와 잘 맞지 않아요.」 / 그 외 「근거가 조금 부족해서 확인을 부탁드려요.」 (원본은 "세 번"을 샘플 수와 무관하게 고정 — 재구현은 샘플 수를 쓰는 것을 권장, 비교 테스트에서 차이로 기록)
- 근거 상자 머리: 근거 문서가 same_as/graph/kge/schema/identity이면 「판단 근거」, 행 번호가 있으면 「원본 표 <파일> <줄>번째 줄」, 그 외 「원문 — <문서>」. 인용 구간 강조, 앞뒤 220자(앞쪽은 줄 시작까지), 잘리면 「…」.
- 버튼 문구: 기본 「맞아요 / 고쳐서 맞아요 / 틀려요」, 보정 「이 값 쓰기 / 다른 값 입력 / 쓰지 않기」, 같은 대상 「같은 대상 맞아요 / (없음) / 서로 달라요」, 새 종류 「지도에 추가 / 이름 고쳐서 추가 / 추가 안 함」 + 「나중에(→)」. 단축키 Y/N/E/→(편집 중이거나 입력 요소에 포커스면 무시).
- 고치기 양식: 관계(누가·어떤 관계(스키마 관계 select, 설명 표시)·누구에게/무엇을), 값(값), 항목(이름), 새 종류(이름·설명) → 「이렇게 고쳐서 넣기」/「취소」.
- 결과 토스트: 기각 「넣지 않았어요: 문장」, 스키마 반영 「지식 지도에 새 종류를 추가했어요: 문장」, 그 외 「지식 지도에 넣었어요: 문장」, 오류 「넣을 수 없어요 — 메시지」. 처리한 카드는 목록에서 빠지고 같은 위치의 다음 카드.
- 「자세히 보기 — 점수, 주변 지식 지도, 원인 코드」: 막대 5개(여러 번 읽어도 같은가/원문에 근거가 있는가/지식 지도와 맞는가/규칙을 지켰는가(G×m)/종합 점수, 힌트에 가중치·횟수·이름 일치·임베딩·「바로 넣는 기준 0.85」), 종류·술어·원인·S_c(소수 셋째), 펼칠 때 주변 그래프(1홉, 후보 관계는 점선, 그래프에 없는 끝은 「이름 (새로)」).
- 비었을 때 「🎉 / 지금은 확인할 내용이 없어요.」 + 「온톨로지 구축으로」.

### 7.4 보류함
- 위 상자 「🩺 지식 지도 점검」 + 설명 + 「지금 점검하기」(진행 중 「점검 중…」), 결과 알약(§5.7 요약값; 빠진 값·연결 없음·값 충돌은 >0이면 빨강, 같은 대상 확인은 주황, 자동 연결·제안은 고정색, 해결됨은 있을 때만) + 「제안 확인하러 가기 →」. 토스트 「점검을 마쳤어요 — 고칠 것 {빠진 값+연결 없음+값 충돌}건, 확인할 제안 {같은 대상 확인+제안}건」.
- 열린 보류를 `reason_code`(첫 원인)로 10개 묶음에 나눈다(표는 `user-scenarios.md` S6; 매핑: 없는 관계=ONTO_PREDICATE_UNKNOWN; 규칙 불일치=ONTO_DOMAIN/RANGE/CLASS_UNKNOWN/PROPERTY_UNKNOWN/INVALID_NAME/CARDINALITY; 표의 행=SRC_NULL_RATIO/UNIQUE/RANGE/FK/IN_SET/ID_MISSING; 파일 전체=SRC_TABLE_BLOCKED; 값=SHAPE_MIN_COUNT/DATATYPE; 연결 규칙=SHAPE_MAX_COUNT/DISJOINT; 고립=ORPHAN_NODE; 충돌=ER_CONFLICT; 약함=LOW_CONFIDENCE; 나머지=처리 중 오류). 묶음 도움말 문구는 S6 표의 원문을 그대로 쓴다(4단계에서 채록 확인).
- 항목 문장: 후보면 카드 문장; 표 행이면 「파일 N번째 줄 (값 4개 · 연결) — 원인 쉬운 말(코드 비어 있어요/두 번 나와요/허용 범위를 벗어났어요/지식 지도에 없는 대상을 가리켜요/허용되지 않은 값이에요/코드나 이름이 없어요)」; 파일 전체 「파일 전체」; 형상 「이름의 속성 값이 없어요」 / 「이름의 속성 값 'v' 형식이 틀려요」 / 「이름 — 상세」; 고립 「클래스 'name' 은(는) 아무것과도 연결되어 있지 않아요」; 충돌 「A = B 의 속성」; 파서 노드 「Class 항목 (코드 없음)」, 파서 관계 「from → to」.
- 버튼 동작: 관계 추가(스키마 관계 추가 API: name=술어, from=주어 클래스, to=목적어 클래스 → 그 항목 다시 시도, 토스트 「‘X’ 관계를 지도에 추가했어요 — 결과」, 실패 「관계를 추가하지 못했어요」), 값 입력(입력 칸 placeholder 「<속성 표시명> 입력」, 「저장」은 값이 있어야 켜짐), 대표 값 버튼들(「대표로 쓸 값:」 값 (원천)), 원문에서 연결 다시 찾기, 그래도 넣기(묶인 후보 승인), 다시 시도, 「버리기」. 2건 이상 retry/reextract 묶음은 「모두 다시 시도」. 묶음별 8건 표시, 「N건 더 보기」로 +20.
- 다시 시도 결과 문구(outcome별, 여러 개면 「 · 」로, 2건 이상은 「(N건)」): ingested 지식 지도에 넣었어요 / resolved 해결됐어요 / redriven 다시 넣었어요 / reextracted 원문에서 연결을 찾았어요 / queued_for_review 찾은 연결을 확인하기로 보냈어요 / still_failing 아직 같은 문제가 있어요 / skipped 이미 처리됐어요 / unsupported_stage 자동으로 다시 시도할 수 없는 항목이에요.
- 어떤 동작이든 끝나면 목록을 다시 읽고 상위(배지)를 갱신. 동작 중엔 모든 버튼 비활성.

### 7.5 구축 화면 오른쪽 「검수」 탭 (M1과의 접점)
- 탭 이름 「검수」(title 「빌드가 남긴 것 중 사람이 판단할 것」), 배지 = to_review + held.
- 머리: 온톨로지 select(title 「검수할 온톨로지」), 요약 「지도에 {in_graph}개 · 확인 필요 {to_review} · 보류 {held}」. 하위 탭 「🙋 확인하기」(배지)·「🗂️ 보류함」(배지). 확인 대기 0·보류 >0이면 보류함 먼저. 내용은 7.3·7.4와 같은 컴포넌트(좁은 배치).
- 에이전트 응답 스트리밍이 끝날 때마다 다시 읽음. 구축 보고서 카드 「🙋 확인이 필요한 내용 N건 · 🗂️ 보류 M건 — 사람이 판단해야 지식 지도에 들어갑니다.」 + 「검수 탭에서 보기」(그 온톨로지로 탭 전환). 카드는 둘 중 하나라도 >0일 때만.
- 온톨로지 미선택: 「구축을 시작하면 이곳에 사람이 판단할 내용이 모입니다.」

### 7.6 고급 화면
머리 「추출 품질 검수」, 탭 「검수 큐 · DLQ · 검증 · 식별자 · KGE · 판정 이력 · 추출 실행 · 정책」(검수 큐·DLQ 배지), 「새로고침」, 상단 메시지 줄. 각 탭 구성·문구는 `user-scenarios.md` S11–S15. 주요 규칙:
- 검수 큐: 체크박스 일괄 승인/기각, 항목 클릭 시 상세(원인 칩 「코드 · 설명」, 게이트 메모, 「점수 분해 — S_c = G × m × (결합)」 막대, 원문 근거 최대 3개, 인용 미발견 경고, 주변 그래프), 「수정 후 승인」은 양식 값이 원래와 다를 때만 켜짐(엔터티는 클래스도 수정 가능). 판정 이력 탭은 같은 화면에서 상태 `auto_ingested,approved,edited,rejected` 목록 + 상태 칩(자동 적재/승인/수정 승인/기각).
- DLQ: 원인 코드 칩(전체 n / 코드 n), 「선택 재처리 (n)」 또는 「표시된 항목 재처리 (n)」, 표(원인·단계·내용·시도(≥3이면 「(한도)」)·상세·「폐기」), 결과 「재처리 결과: outcome n, …」.
- 추출 실행·검증·식별자·KGE·정책: S12–S15. 정책 숫자 입력 단계값(가중치 0.05, 하한 0.01, λ 0.005, α 0.05, prior 0.05, 샘플 1~10)과 「가중치 합: x」 표시.
- CSV 매핑 초안(파일을 고르면 미리보기 후 자동): 원천 `ERP`, 클래스 = 스키마 첫 클래스, key = 이름이 `id`/`code`/`key`로 끝나는 첫 열(없으면 첫 열), name = `name`을 포함하거나 「명」으로 끝나는 열(없으면 key), properties = 첫 클래스 속성 이름과 같은 열, relations 비움, expectations = key `not_null` row.

## 8. API 명세 요약 (`/api/quality`, JSON)
| 메서드 경로 | 요청 | 응답 |
|---|---|---|
| GET `/summary?schema_id` | | `{candidates{kind:{status:n}}, totals{status:n}, dlq_open{code:n}, dlq_open_total, reason_descriptions{code:설명}, policy, runs[최근10]}` |
| GET `/review-status?schema_id` | | `{schema_id, to_review, held, held_by_reason, in_graph, pending_by_kind}` |
| GET `/codes` | | `{codes{code:설명}, hard[], soft[]}` |
| GET·PUT `/policy/{schema_id}` | PUT `{policy}` | `{schema_id, policy}` |
| POST `/extract` | `{schema_id, text?, filename?, session_id?, doc?, samples?(1-10), max_chunks?(1-500, 기본 50)}` | 실행 통계 §5.4 |
| GET `/candidates?schema_id&status=pending&kind&limit≤500&offset` | status 쉼표 다중 | `{items, count}` |
| GET `/candidates/{id}` | | 후보 / 404 |
| GET `/candidates/{id}/neighborhood` | | `{nodes[{id,name,focus,labels}], edges[{id,type,source,target,confidence}], keys, error?}` |
| POST `/candidates/{id}/decide` | §5.8 | §5.8 |
| POST `/candidates/bulk-decide` | `{ids, decision, reviewer}` | `{results}` |
| GET `/dlq?schema_id&status=open&reason_code&limit≤1000` | | `{items(+reason_description), counts{code:n}}`(최근 순) |
| POST `/dlq/redrive` | `{ids?, schema_id?, reason_code?}` | `{results}` |
| POST `/dlq/{id}/discard` | | `{id, status:"discarded"}` |
| POST `/checkup` · `/shapes/run` · `/lint` · `/identity/run` · `/impute` · `/kge/train` | `{schema_id}` | §5.7, §5.11 |
| GET `/shapes?schema_id` | | `{items[{id, kind, class, property?, datatype?, predicate?, max?, min?, classes?, origin:"schema"|"rule", description}]}` |
| GET `/identity/clusters?schema_id` | | `{items}` §5.10 |
| POST `/identity/conflicts/{id}/resolve` | `{value, source, reviewer}` | `{id, preferred, source}` |
| POST `/manual-value` | §5.10 | 결정 응답 + `resolved` |
| POST `/source/preview` | `{filename, session_id}` | `{columns, rows(8), row_count}` |
| POST `/source/ingest` | `{schema_id, filename, session_id, mapping, dry_run}` | §5.5 |
| POST `/source/check-table` | `{schema_id, datasource, table, rules}` | `{datasource, table, rules[{…, passed, observed, rows, sql}], blocked}` — 바인딩된 원천 테이블을 규칙별 집계(전체/위반 수)로 검사, 실행 실패도 차단, 차단이면 보류 1건. 화면 없음 |
| GET·POST `/rules`, DELETE `/rules/{id}` | POST `{schema_id, layer:"source"|"shape", rule, target}` | `{items}` / `{id}` / `{id, deleted:true}` — 화면 없음 |
| GET `/reports?schema_id&limit≤100` | | `{items[{id, layer, target, report, created_at}]}` — 화면 없음 |
| GET `/kge?schema_id`, `/kge/score?schema_id&h&r&t` | | §5.11 |
| GET `/export/feedback.jsonl?schema_id`, `/export/kge-triples.tsv?schema_id` | | 텍스트 §5.12 |

공통 오류: 스키마 없음 404 「스키마를 찾을 수 없습니다: <id>」, 검증 422(`detail` 문자열 — 화면은 `detail`이 문자열이면 그대로, 아니면 `HTTP <code>`로 표시), LLM 키 없음 503. 업로드 파일은 세션 업로드 폴더 안만 허용(경로 탈출 차단, 404 「업로드 파일을 찾을 수 없습니다: …」). PDF는 텍스트 추출, 실패 시 422.

다른 기능의 API(이 화면이 부름): `GET /api/schemas/{id}`(M1 스키마), `PUT /api/schema/relationships`(M1 관계 추가), `GET /api/files?session_id`, `POST /api/upload`(파일).

## 9. 에이전트 도구 (구축 모드, 내장·외부 CLI 공통, ADR-0010 구조 기준)
| 도구 | 인자 | 결과 |
|---|---|---|
| `extract_triples` | `source`(텍스트 또는 샌드박스 `/workspace/…` 한 줄 경로), `schema_name`, `samples`(0=정책) | 추출 통계 + `note` 「검수 대기(pending)와 DLQ 항목은 사용자가 품질 화면에서 판단합니다. 대신 승인하거나 재처리하지 마세요.」 |
| `table_ingest` | `source`, `mapping_json`, `schema_name`, `dry_run` | `{blocked, dry_run, rows, stats, failed_rules[{type,column,severity,failing_count,observed}], note}` |
| `quality_checkup` | `schema_name` | 점검 요약(details 제외) + `review`(review-status) |
| `quality_report` | `schema_name` | summary(policy 제외) |
- 오류는 `{"error": "…"}` 문자열 JSON(예외를 던지지 않음). 스키마는 **이름**으로 찾는다.
- **결정·재처리·폐기·정책·대표 값 도구는 만들지 않는다.** 구축 스킬은 마지막 단계에서 점검 도구를 한 번 부르고 사람이 판단할 건수·원인을 3~5줄로 알리며, 승인 대행·규칙 완화를 하지 않도록 지시한다(M1 설계에서 프롬프트로 다룸).
- 구축 보고서에는 백엔드가 실제 숫자(review-status + `schema_name`)를 `quality`로 붙인다. 대상 온톨로지 = 세션에 기록된 스키마, 없으면 이번 턴 도구 호출 인자의 마지막 `schema_name`.
- 파서 일괄 적재 도구(M1)는 §5.6 선별을 통과한 것만 쓴다.

## 10. 상태·저장
- 관리 DB(SQLite, 스키마 정의와 같은 파일, 사용자 데이터 폴더)에 §4의 9개 저장소. 스키마 삭제 시 함께 삭제.
- 그래프: 통과한 것만. 대표 값·정책·판정은 그래프에 없다.
- 화면 상태(선택 탭·필터·토스트)는 저장하지 않는다.
- 동시성: 원본은 요청마다 순차 처리(작업 스레드), 잠금 없음. 같은 후보를 두 화면에서 동시에 결정하면 두 번째가 「이미 처리된 후보」로 거절되는 것이 기대 동작.

## 11. 다른 기능과의 의존
- **M1 온톨로지 구축:** 스키마(클래스·속성 선언 `type`/`required`/`identifier`/`default`/`virtual`, 관계 from/to/description, 클래스 바인딩 종류)를 읽고, 스키마 제안 승인과 「관계를 지도에 추가」로 스키마를 쓴다. 구축 에이전트 도구·보고서·오른쪽 「검수」 탭. 속성 선언 플래그를 M1이 실제로 만드는지는 M1 분석과 맞출 것.
- **A2 저장소:** Bolt 그래프 읽기·쓰기, 트랜잭션 메타데이터 감사.
- **A3 에이전트·MCP:** 도구 노출, 샌드박스 파일 다운로드, 세션 업로드 폴더.
- **M8 설정:** OpenAI 호환 키·주소·보조 모델(추출·임베딩). 키가 없으면 추출·재추출만 불가, 나머지(점검·결정·CSV)는 동작.
- **M2:** 엔터티 해소 서비스(모호성 검사). 품질 검수 승인 사실은 발행(M1) 뒤 질의에 쓰인다.
- **M3 데이터소스:** 원천 테이블 검사(화면 없음)는 데이터소스 SQL 실행 경로를 쓴다.

## 12. 오류·예외
- 그래프가 꺼져 있어도 검수 화면은 열려야 한다: 주변 그래프 오류는 빈 그래프 + `error`, 그래프 지지도는 prior로, 형상 하나 실패는 그 결과에 `error`만.
- 한 항목의 실패가 묶음(재처리·일괄 결정·형상)을 멈추지 않는다.
- 출처 기록(스키마 제안 승인 시) 실패는 승인을 막지 않는다.
- LLM 응답이 JSON이 아니면 샘플 실패로 셈. logprob을 거부하는 모델이면 끄고 재호출.
- 바인딩 테이블 검사의 값에 `'` `;` `\` `--`가 있으면 거부, 식별자는 영문·숫자·밑줄만.

## 13. 원본과 비교할 테스트 항목
결정적 규칙은 **값까지** 같아야 한다. LLM 추출은 구조·계약만(ADR-0010).
1. 정책: 기본값 응답 동일; 가중치 합 0.9 저장 시 422와 문구; review>auto 422.
2. 게이트 표(입력 후보 → hard/soft 코드): 미등록 클래스(스키마 있음/없음), 이름 규칙(공백·하이픈·숫자 시작·한글), 지시어 이름 「본 증권」·「당사」(id 있음/없음), 미선언 속성, 타입(「1,200」 int 통과, 「12a」 실패, 「2026년 9월」 date 통과, 「예」 bool 통과), 술어 정확/대소문자·밑줄 차이/설명 포함/유사도 0.82 경계, 정의역·공역(다중 정의), 부트스트랩(관계 0개).
3. 점수: 신호를 고정한 후보로 S_c·route 재현(linear/harmonic, 0이 있는 harmonic, m_vocab<1, 이미 있는 관계 S_graph=1, 경로 없음 prior). ALWAYS_REVIEW가 점수 0.95여도 review.
4. 분기 경계: S_c 0.85 정확히 → auto(soft 없음), 0.5999 → dlq LOW_CONFIDENCE.
5. 지문: 같은 사실 재추출 시 행 1개·근거 누적; 기각 후 재추출 시 `preserved` 증가·status 유지.
6. 결정: 승인 → 그래프 노드/관계 속성(`_Entity`, `_source_id`, `_confidence`=max(S_c, 0.85), `_run_id`, `_evidence_ref`), 감사 actor; 이미 처리 재결정 422; identity edit 422; 스키마 위반 승인 422 문구; tbox 승인 → 스키마에 추가 + `applied:"schema"`.
7. CSV: block 실패 → 0행 적재·보류 1; row 실패 → 해당 행만 보류(`row:` 표식); 키 `원천:키`; 같은 파일 고쳐서 다시 시도 → ingested.
8. 점검: 필수 속성 누락 노드 수 = missing_values; 값 넣은 뒤 재점검 resolved 증가; 고립 노드; 이름 「(주)가나」·「가나 주식회사」 → SAME_AS 자동(0.97), 방향 사전순; 값 충돌 보류 → 대표 값 선택 → 재점검 시 다시 안 생김, 그래프 값 불변.
9. 결측 보정 우선순위와 지지 2·비율 0.6 경계.
10. 재처리 outcome 종류별 1건씩, 시도 수 증가, 3회 초과도 재처리 허용.
11. 파서 선별: id 없는 노드·끝점 없는 관계가 DLQ로 가고 나머지는 적재, 응답 `quarantined`.
12. 화면: 보류 묶음 분류(코드 → 묶음), 카드 배지·이유 문구, 버튼 문구 세트, 키보드 Y/N/E/→, 구축 탭 배지 합, 보고서 카드 표시 조건.
13. 에이전트(구조): 구축 모드 도구 목록에 품질 도구 4개가 있고 결정 도구가 없음; 도구 응답 키와 `note` 문구.
14. KGE: 삼중주 3개 → 422; 학습 응답 키; 같은 시드 동일 그래프에서 확률이 원본과 근사(정확 일치는 요구하지 않음).
15. 내보내기: JSONL 한 줄 구조, TSV 줄 형식.

## 14. 모르는 점 (4단계 실행 기록에서 확인)
1. 실제 구축(M1 튜토리얼 12장)에서 에이전트가 `extract_triples`/`table_ingest`를 쓰는지, 파서(`batch_ingest`)만 쓰는지 — 후자면 확인하기에 아무것도 안 쌓이고 보류함만 생긴다. 튜토리얼 캡처는 0건.
2. 기본 모델로 문서 1장 추출 시 실제 auto/pending/dlq 분포와 소요 시간, 임베딩 호출 성공 여부(OpenAI 모드 판정: 키 있고 base URL 없음일 때만 OpenAI 임베딩, 아니면 로컬 임베딩 서버 — 로컬이 없으면 cos 없이 동작하는지).
3. M1이 클래스 속성에 `required`/`type`/`identifier`/`default`를 실제로 넣는지(넣지 않으면 형상·식별·기본값 보정이 거의 동작하지 않음).
4. 예제 온톨로지(가상 노드 기반)에서 점검을 돌렸을 때 결과 — 가상 노드는 `_Entity` 라벨이 없어 점검 대상이 아닐 것으로 추정.
5. 엔터티 모호성 검사(발행 그래프 엔터티 해소)가 실제로 값을 돌려주는지.
6. 「관계를 지도에 추가하고 넣기」의 스키마 API 요청·응답(M1 범위)과 실패 문구.
7. 토스트·묶음 도움말·근거 표시 등 문구의 실제 렌더링(이 문서는 번들 문자열 기준).
8. 그래프 쓰기 시 트랜잭션 메타데이터가 A2 감사 로그에 어떻게 남는지(포털 시점 조회와 연계).
9. 대량(수백 건) 보류·후보에서의 화면 성능(목록 300개 한도, 묶음 8개 표시).
10. 구축 대화 응답의 `quality` 첨부가 외부 CLI 에이전트에서도 붙는지(세션 스키마 이름 기록 여부).

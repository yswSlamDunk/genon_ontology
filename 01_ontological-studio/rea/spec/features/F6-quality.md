# F6. 품질 검수

- 상태: 초안 v0.1 (2026-11-01, Claude 작성) — 사용자 보정 전
- 원본 기준 동작: `../../analysis/ontological-studio/menus/06-quality/design.md`(이하 **M6 설계**), `user-scenarios.md`(S1–S15)
- 근거 문서: [02 온톨로지 모델](../02-ontology-model.md) §6(Value type·required), §7.4(편집 레이어), §7.6(병합·sameAs), §8(카디널리티), [03 보안](../03-security.md) §4·§9, [04 에이전트](../04-agent-integration.md) §3(단일 LLM 클라이언트)·§4(`extract` 모드)
- 관련 결정: **D-16**(고급 화면 범위), **D-06**(편집 레이어 충돌), D-05, D-12
- 함께 읽는 기능 명세: [F1](F1-ontology-build.md)(구축·작업본·문서 원천), F3(데이터소스), F8(LLM·추출 모델 설정)

---

## 1. 목적

문서·표·파서·동기화에서 들어오는 **사실(객체·링크·속성·정의 제안·동일성)** 을 객체 저장소에 바로 쓰지 않고, 결정적 정의 검사와 복합 신뢰도 점수로 세 갈래로 나눈다. 그리고 이미 들어간 객체를 **온톨로지 제약**(필수·값 타입·Value type·카디널리티·링크·동일성·원천 충돌·편집 충돌)으로 점검한다.

| 갈래 | 조건 | 처리 |
|---|---|---|
| 자동 적재 | 정의 위반 없음, S_c ≥ 자동 하한(0.85), 검수 플래그 없음 | 단일 쓰기 경로로 즉시 반영 |
| 확인하기 | 두 하한 사이, 또는 항상-검수 플래그 | 사람이 승인/수정/기각 |
| 보류함(DLQ) | 정의 위반(hard), S_c < 검수 하한(0.60), 원천 규칙 위반, 쓰기 실패, 사후 점검 문제 | 원인별로 사람이 고치고 다시 시도/버리기 |

**판단은 항상 사람이 한다.** 에이전트에게는 추출·점검·현황 도구만 있고 결정·재처리 도구는 없다(구조적 강제). 사람의 판정은 다음 추출의 예시(few-shot)와 학습 데이터 내보내기에 쓰인다. — 원본 원칙 그대로.

---

## 2. 원본 기준 동작 요약 [원본]

근거: M6 설계 전체.
- **세 갈래 게이트**(§5.2–5.3): 원인 코드(hard/soft/항상-검수), 결정적 스키마 게이트(이름 규칙, 미등록 클래스·속성, 타입 판정, 술어 맞추기·유사어 0.82, 정의역·공역, 문서 지시어), 복합 신뢰도 `S_c = G_onto × m_vocab × 결합(S_llm, S_ground, S_graph)`, 기본 가중치 0.3/0.5/0.2, linear/harmonic, 자동 0.85·검수 0.60.
- **문서 추출**(§5.4): 청크 1800자, 샘플 M=3, 허용 클래스·관계·최근 판정 8개(few-shot) 블록, JSON 출력, 인용 필수. OpenAI 호환 API를 **선택한 에이전트와 무관하게 직접 호출**.
- **정형 CSV 적재**(§5.5): 매핑·원천 규칙(not_null/between/unique/in_set/fk, row/block).
- **파서 일괄 적재 선별**(§5.6): 점수 없이 구조만.
- **사후 점검**(§5.7): 형상(required·type·사용자 규칙) → 고립 → 동일 개체(SAME_AS 자동 ≥0.95, 검수 ≥0.80) → 값 충돌 → 결측 보정 제안.
- **사람의 결정**(§5.8), **보류 다시 시도**(§5.9, outcome 9종, 3회 한도 표시만), **사람 입력·대표 값**(§5.10), KGE(§5.11), 내보내기(§5.12).
- **화면**: 「지식 품질」 — 「🏠 한눈에」「🙋 확인하기」「🗂️ 보류함」 + 「⚙ 고급」(8개 탭), 구축 화면 오른쪽 「검수」 탭.
- **알려진 결함**(REVIEW #14·#15·#16): 카디널리티 검사 미동작, 3회 한도가 막지 않음, 규칙 API는 있으나 화면 없음, `table_ingest`가 로컬 임의 경로 파일을 읽음, 추출 LLM이 별도 공급자 직접 호출, 검토자 이름 고정 `studio-user`.

---

## 3. 새 설계에서 달라지는 점 [제안]

### 3.1 모델 대응 (원본 개념 → 02 개념)
| 원본 | 새 모델 | 비고 |
|---|---|---|
| 스키마(schema_id) | Ontology(rid) | 판정 기준 = 해당 온톨로지 **작업본**(§3.3) |
| 클래스 | Object type | 원인 코드 이름(`ONTO_CLASS_UNKNOWN` 등)은 계약이라 유지, 설명 문구만 새 용어 |
| 관계 유형(술어) | Link type (apiName·표시 이름·방향 이름·별칭·설명으로 술어 맞추기) | 쓰기는 `stored` 조인 방식 Link type만 |
| 엔터티 후보(entity) | 객체 후보 | |
| 관계 후보(relation) | 링크 후보 | |
| 속성 후보(property) | 속성 값 후보 | |
| tbox 제안 | **정의 제안**(Object type / Link type) → 승인 시 **작업본 변경** | 원본은 스키마에 즉시 추가 |
| identity(SAME_AS) | **동일성 링크 `sameAs`**(02 §7.6) | 자동 ≥0.95, 검수 ≥0.80 유지 |
| 속성 선언 `required`·`type` | Property `required`·`baseType`·`array`·**Value type 제약** | |
| 속성 선언 `identifier`·`default` | 02 §6에 추가됨 | |
| 그래프 `_Entity` + 클래스 라벨, `_source_id` | Object 모듈 단일 쓰기 경로, 객체 키 = Object type 기본 키 | 아래 §7.4 |
| 관리 DB(SQLite) | `workbench.runtime`의 quality 테이블(01 §3) | |
| OpenAI 호환 API 직접 호출 | **Agent 모듈 단일 LLM 클라이언트**(04 §3), 없으면 CLI 에이전트 `extract` 모드 | 원본 M6 결함 수정 |

### 3.2 검사 확장 (새 모델에서 생기는 것)
| 검사 | 근거 | 원인 코드 | 갈래 |
|---|---|---|---|
| Value type 제약(regex·enum·range·length) | 02 §6 | 게이트: `PROP_DATATYPE`(soft, 메모에 제약 이름) / 점검: ★`VALUE_TYPE_VIOLATION` | 확인하기 / 보류함 ✏️ |
| 기본 키 결측·중복 | 02 §5 | `ID_MISSING`(hard), `SRC_UNIQUE` | 보류함 📄 |
| 카디널리티(Link type의 one 쪽 초과) | 02 §8 — 원본은 미동작 | 게이트: `ONTO_CARDINALITY`(hard, **이제 동작**) / 점검: `SHAPE_MAX_COUNT` | 보류함 🧩 / 🔗 |
| 계산 링크에 쓰기 시도(foreign-key·join-source) | 02 §8 | ★`LINK_NOT_WRITABLE`(hard). 단 같은 링크가 원천에서 이미 성립하면 S_graph=1 + 「이미 있음」으로 자동 처리(쓰기 없음) | 보류함 🧩 |
| 문서 원천이 없는 타입에 사실 쓰기 | 02 §7.1 document 원천 | ★`BACKING_MISSING`(hard) | 보류함 🧭(버튼: 문서 원천 연결) |
| live 타입에 사실 쓰기 | 02 §7.3 | ★`PROP_NOT_WRITABLE`(hard) | 보류함 🧩 |
| 다원천 값 충돌(priority로 고른 값과 다른 원천 값) | 02 §7.6 | ★`SRC_VALUE_CONFLICT` (stage `sync`) | 보류함 ⚖️ |
| 편집 레이어 충돌(정책 `flag`) | 02 §7.4, D-06 | ★`EDIT_CONFLICT` (stage `edit`) | 보류함 ⚖️ |
| 링크 외래키 미일치(대상 없음) | 02 §8 | `SRC_FK` (stage `sync`) | 보류함 📄 |
| 매핑 표현식 평가 실패 | 02 §7.5 | ★`MAPPING_EXPR_ERROR` (stage `sync`) | 보류함 📄 |
| sameAs 대상 타입 불일치 | 02 §7.6 | `ONTO_RANGE`(같은 타입 또는 같은 Interface 구현이 아니면) | 보류함 🧩 |

★ = 새 원인 코드. 원인 코드는 **추가만** 한다(원본 계약: 이름 변경 금지).

### 3.3 판정 기준과 쓰기 대상
- **판정 기준은 작업본**: 구축 중에는 아직 발행되지 않은 Object type·Link type에 사실을 넣어야 하므로, 게이트는 그 온톨로지의 작업본 정의로 검사한다.
- **쓰기 대상**: 사실이 가리키는 정의가 발행본에 있으면 객체 저장소에 바로 반영. 작업본에만 있으면 **대기 적재(staged)** 로 저장하고 다음 발행 때 반영(발행 컴파일 단계, F1 §5.15.2). 화면에서는 「발행 대기」 배지. [제안 — 02 §14·§16에 반영 필요]
- 문서·CSV에서 온 통과 사실은 온톨로지의 **문서 컬렉션**에 기록되고, Object type의 `document` 원천(02 §7.1)을 통해 객체가 된다: native 타입은 즉시 객체 생성·갱신, indexed 타입은 enrichment 병합(즉시 부분 동기화). 링크는 `stored` Link type의 간선으로.

### 3.4 결정 대기 반영
- **D-16 (고급 화면 8개 탭)** — 권장안 「v1 이후, 규칙 편집만 우선」 적용: v1에는 기본 화면(한눈에·확인하기·보류함) + **「규칙」 화면**(형상·원천 규칙 편집 — 원본엔 API만 있고 화면 없음) + 정책 **읽기 전용** 표시. 나머지 고급 탭(검수 큐·DLQ 표·검증·식별자·KGE·판정 이력·추출 실행·정책 편집)은 v1 이후. API는 v1에 모두 둔다(에이전트·스크립트·비교 테스트용).
- **D-06 (편집 레이어 충돌 기본 edit-wins)** — 기본은 F6 항목을 만들지 않고 동기화 보고서에만 집계. Object type이 `flag`면 `EDIT_CONFLICT` 항목.
- **D-05** — live 타입은 원천 값을 그대로 읽으므로 원천 충돌·편집 충돌 검사 대상이 아니다(같은 데이터소스 병합만).
- **D-12** — 결정적 규칙은 값까지 원본과 같게, 결함(카디널리티 미동작·임의 경로·별도 LLM 호출·고정 검토자)은 고치고 §11에 표시. **3회 한도는 원본처럼 표시만**(막지 않음) 유지 — 사람이 판단한다는 원칙상 막을 이유가 약함.

### 3.5 범위 (00 §5)
F6 전체가 **v1**. MVP에는 없다(단, MVP의 indexed 동기화가 내는 `SRC_*`·`MAPPING_EXPR_ERROR`는 v1 전까지 동기화 보고서로만 보임).

---

## 4. 사용자 시나리오

### 4.1 원본 대응
| 번호 | 시나리오 | 원본과 같아야 할 것 | 달라지는 것 |
|---|---|---|---|
| S1 | 「품질 검수」 → 한눈에 | 큰 문장·카드 3개·「지금 할 일」·최근 활동 문구·탭 배지 | 「발행 대기 n」 보조 줄 |
| S2 | 확인하기 카드 판단(Y/N/→) | 카드 순서(S_c 내림, 같으면 오래된 순)·문장·확신 배지·이유 문구·근거 상자·토스트·단축키 | 문장의 관계 이름 = Link type 표시 이름 |
| S3 | 고쳐서 넣기 | 양식 종류·버튼 문구, 게이트 재검사 | 「어떤 관계」 선택지 = 쓰기 가능한(stored) Link type |
| S4 | 새 종류 제안 승인 | 「지도에 추가 / 이름 고쳐서 추가 / 추가 안 함」 | 결과가 **작업본 변경**, 토스트 「작업본에 새 종류를 추가했어요 — 발행하면 지식 지도에 보여요: …」 |
| S5 | 지금 점검하기 | 순서(형상 → 고립 → 동일 개체 → 값 충돌 → 결측 보정), 알약 7개·토스트 문구, 해결됨 자동 닫기 | 형상에 Value type·카디널리티·기본 키 추가 |
| S6 | 보류함 원인별 고치기 | 10개 묶음·버튼·다시 시도 결과 문구·「버리기」·「N건 더 보기」 | 묶음 매핑에 새 코드 추가(§5.4) |
| S7 | 빠진 값 직접 넣기 | 문구, 게이트 재검사, 형상 재검증 | 값은 문서 컬렉션(사람 입력)으로 |
| S8 | 고립 객체 연결 다시 찾기 | 원문 최대 3개 재추출, outcome 문구 | LLM 경로 = 단일 클라이언트 |
| S9 | 값 충돌에서 대표 값 고르기 | 「대표로 쓸 값:」, 원천 값 불변 | 원천 충돌(SRC_VALUE_CONFLICT)도 같은 화면 |
| S10 | 구축 화면 「검수」 탭·보고서 카드 | 머리·요약·하위 탭 규칙·배지 합·빈 문구 | — |
| S11–S15 | 고급 화면 | API 계약 | **D-16**: v1은 「규칙」만, 나머지는 v1 이후 |

### 4.2 새 시나리오
| 번호 | 시나리오 | 기대 결과 |
|---|---|---|
| N1 | Value type `CountryCode`(`^[A-Z]{2}$`)를 쓰는 속성에 문서에서 「대한민국」 추출 | 게이트 `PROP_DATATYPE`(메모 「CountryCode: 정규식 불일치」) → 확인하기, 「고쳐서 맞아요」로 `KR` 입력 → 통과 |
| N2 | `Shipment → PurchaseOrder`(many-to-one, stored)에 한 선적이 발주 둘을 가리키는 추출 | 두 번째 링크 `ONTO_CARDINALITY` → 보류함 🧩 「선적 'SH-1' 은(는) 발주를 하나만 가질 수 있어요」 |
| N3 | `PurchaseOrder`(indexed)가 erp(우선 10)·wms(우선 5)에서 `amountUsd`를 다르게 받음 | 동기화 후 `SRC_VALUE_CONFLICT` → 보류함 ⚖️, 대표 값 선택 → 해소(원천 값 불변). 「우선순위 바꾸기」 링크 → F1 백킹 |
| N4 | `Shipment.priority`가 편집 정책 `flag`인데 원천에서 값이 바뀜 | `EDIT_CONFLICT` → 보류함 ⚖️ 「편집 값 유지」/「원천 값 따르기」 → 편집 레이어 유지 또는 삭제 |
| N5 | 문서에서 뽑은 `Supplier` 「(주)한빛정밀」과 ERP `Supplier` 「한빛정밀 주식회사」 | 점검 → 이름 정규화 일치 0.97 ≥ 0.95 → `sameAs` 자동 연결 |
| N6 | 「규칙」 화면에서 형상 규칙 `Shipment -shipmentPurchaseOrder-> 최소 1` 추가 → 점검 | 링크 없는 선적 `SHAPE_MIN_COUNT` 보류 |
| N7 | 작업본에만 있는 Object type에 문서 추출 | 통과 사실이 「발행 대기」로 남고, 발행 후 객체로 보임 |
| N8 | 에이전트 경로만 있음(LLM API 키 없음, Claude Code 선택) | 추출이 `extract` 모드로 수행, logprob 없이 freq만 |

---

## 5. 화면 구성과 상호작용

화면 문구는 **원본 그대로**가 기본이다(M6 설계 §7, user-scenarios S1–S10). 아래는 달라지는 곳과 새 모델 반영만 적는다.

### 5.1 품질 검수 뷰 (`view=quality`)
- 머리 「지식 품질」, 온톨로지 선택(「온톨로지 선택」), 탭 「🏠 한눈에」「🙋 확인하기」「🗂️ 보류함」(배지), 오른쪽 「규칙」(D-16; 원본 「⚙ 고급」 자리. v1 이후 고급 탭이 생기면 「⚙ 고급」으로 되돌림). 토스트(오류 9초·일반 6초), 온톨로지 없음 「위에서 온톨로지를 고르세요.」 — 원본 그대로.
- 탭·온톨로지 전환 시 다시 읽기(작업본 정의 + summary). 「온톨로지 구축으로」는 F1 구축 대화 공간으로.

### 5.2 한눈에
원본 S1 그대로(「지식 지도에 확인된 사실이 **N**개 들어 있어요.」, N = auto_ingested+approved+edited 후보 수, 카드 3개, 「지금 할 일」, 「어떻게 동작하나요?」 — 「AI가 직접 승인하거나 보류를 풀 수는 없습니다. 판단은 항상 사람이 합니다.」, 최근 활동 6건). 추가:
- 「발행 대기 n건 — 발행하면 지식 지도에 들어가요」(staged가 있을 때) + 「제안 보기」(F1).
- 최근 활동 종류 추가: `sync` 「동기화 점검 (원천 충돌·편집 충돌)」 — a·b건.

### 5.3 확인하기 (카드 덱)
원본 §7.3 규칙 그대로: 300개, 정렬, 종류 칩(전체/관계/값/항목/같은 대상/새 종류), 「확인할 내용 i / n」, 「전체 목록」, 카드 문장 규칙, 확신 배지(확인 필요/확실함/애매함/약함), 이유 한 줄 우선순위·문구, 근거 상자(앞뒤 220자), 버튼 세트, 단축키 Y/N/E/→, 결과 토스트, 「자세히 보기 — 점수, 주변 지식 지도, 원인 코드」(막대 5개, 「바로 넣는 기준 0.85」).
- 새 모델 반영:
  - 관계 문장의 관계 이름 = Link type 정방향 표시 이름(없으면 apiName). 작업본에 없는 술어면 「X (지도에 없는 관계)」 — 원본 그대로.
  - 값 문장의 속성 이름 = Property 표시 이름. Value type이 있으면 「(형식: CountryCode)」 꼬리표.
  - 항목 문장의 종류 = Object type 표시 이름.
  - 대상 정의가 작업본에만 있으면 카드에 「발행 대기」 배지, 승인 토스트 「승인했어요 — 발행하면 지식 지도에 들어가요: …」.
  - 「AI가 같은 문단을 세 번 읽었는데 …」 문구는 **샘플 수 M**을 쓴다(원본은 "세 번" 고정 — 원본 M6 설계가 권장한 수정, 의도된 차이).
- 고치기 양식(원본 종류별) — 「어떤 관계」 선택지는 쓰기 가능한(`stored`) Link type 중 주어·목적어 타입이 맞는 것, 설명 표시.

### 5.4 보류함
원본 §7.4 그대로: 「🩺 지식 지도 점검」 상자·「지금 점검하기」·결과 알약·토스트, 원인별 10개 묶음(첫 원인 코드 기준), 항목 문장, 버튼, 다시 시도 결과 문구, 「모두 다시 시도」, 8건 + 「N건 더 보기」(+20).

**묶음 매핑(원본 + 새 코드)**:
| 묶음 (원본 제목·아이콘) | 원인 코드 | 항목 버튼 |
|---|---|---|
| 🧭 지식 지도에 없는 관계 | `ONTO_PREDICATE_UNKNOWN`, ★`BACKING_MISSING` | 「‘X’ 관계를 지도에 추가하고 넣기」 → **작업본**에 `stored` Link type 추가 후 다시 시도 / ★「문서 원천을 연결하고 넣기」(대상 타입에 document enrichment 추가) |
| 🧩 지도의 규칙과 맞지 않음 | `ONTO_DOMAIN`, `ONTO_RANGE`, `ONTO_CLASS_UNKNOWN`, `ONTO_PROPERTY_UNKNOWN`, `ONTO_INVALID_NAME`, `ONTO_CARDINALITY`, ★`LINK_NOT_WRITABLE`, ★`PROP_NOT_WRITABLE` | 「다시 시도」 (+ 정의 원인이면 「설계에서 고치기」 → F1 해당 정의) |
| 📄 원본 표의 잘못된 행 | `SRC_NULL_RATIO`, `SRC_UNIQUE`, `SRC_RANGE`, `SRC_FK`, `SRC_IN_SET`, `ID_MISSING`, ★`MAPPING_EXPR_ERROR` | 「다시 시도」 (CSV면 현재 파일 다시 읽기, 동기화 항목이면 그 행만 다시 동기화) |
| ⛔ 파일 전체를 가져오지 않음 | `SRC_TABLE_BLOCKED` | 「다시 시도」 |
| ✏️ 꼭 있어야 할 값이 빠졌거나 형식이 틀림 | `SHAPE_MIN_COUNT`(필수), `SHAPE_DATATYPE`, ★`VALUE_TYPE_VIOLATION` | 값 입력란 + 「저장」 |
| 🔗 연결 규칙 위반 | `SHAPE_MAX_COUNT`, `SHAPE_DISJOINT` | 「다시 시도」(재검사) |
| 🏝️ 다른 항목과 연결이 없음 | `ORPHAN_NODE` | 「원문에서 연결 다시 찾기」 |
| ⚖️ 같은 대상인데 값이 서로 다름 | `ER_CONFLICT`, ★`SRC_VALUE_CONFLICT`, ★`EDIT_CONFLICT` | 「대표로 쓸 값:」 값 버튼들 / EDIT_CONFLICT는 「편집 값 유지」·「원천 값 따르기」 |
| 🌫️ 근거가 너무 약함 | `LOW_CONFIDENCE` | 「그래도 넣기」 |
| ⚠️ 처리 중 오류 | 그 밖(`WRITE_FAILED`, `PARSE_JSON` …) | 「다시 시도」 |

- 항목 문장 추가: 카디널리티 「<이름> 은(는) <링크 표시 이름>을(를) 하나만 가질 수 있어요」, 원천 충돌 「<이름>의 <속성>: erp=4.5 / wms=4.2」, 편집 충돌 「<이름>의 <속성>: 편집 값 'URGENT' / 원천 값 'NORMAL'」, 표현식 오류 「<원천> <키>번 행 — 매핑 식을 계산하지 못했어요」.
- 「‘X’ 관계를 지도에 추가하고 넣기」 결과 토스트: 「‘X’ 관계를 작업본에 추가했어요 — <다시 시도 결과>」(원본 「…지도에 추가했어요…」, 의도된 차이). 추가되는 Link type: apiName = 술어 camelCase, from = 주어 타입, to = 목적어 타입, 카디널리티 `many-to-many`(사람이 나중에 좁힘), 조인 `stored`, 출처 `quality_review`.

### 5.5 구축 화면 「검수」 탭
원본 §7.5와 S10 그대로(F1 오른쪽 패널). 머리 「검수할 온톨로지」, 「지도에 {in_graph}개 · 확인 필요 {to_review} · 보류 {held}」, 하위 탭 규칙, 스트리밍 종료마다 다시 읽기, 빈 문구.

### 5.6 규칙 화면 (D-16, v1 신규 화면)
원본은 규칙 API만 있고 화면이 없었다. 두 묶음:
- **형상 규칙**: 행 = 종류(`max_count`·`min_rel`·`disjoint`·★`value_in`)·대상(Object type, Link type 선택)·한도·설명(원본 형식 `C -R-> 최대 n`, `C -R-> 최소 n`, `A ⊥ B 배타`)·출처(「정의에서」 읽기 전용 / 「사용자 규칙」 편집 가능). 정의에서 나오는 형상(필수·baseType·Value type·카디널리티·기본 키)은 자동으로 목록에 보이고 편집은 F1 링크.
- **원천 규칙**: 백킹 원천(table/sql)·CSV 매핑별 `not_null`·`between`·`unique`·`in_set`·`fk`, severity `row`/`block`. 「지금 검사」(원천 검사 API) → 결과 표(원본 S13 표 형식).
- **정책**(읽기 전용): 원본 기본값 표 + 「가중치 합: 1.00」. 편집은 v1 이후(D-16).

---

## 6. API

경로 `/api/v1/quality/...`, 세션 토큰 필수. 원본 `schema_id` 자리는 `ontology`(apiName 또는 rid). 요청·응답 필드는 원본(M6 설계 §8)과 같고, 달라지는 것만 적는다. 오류 형식은 원본처럼 `detail` 문자열(화면이 의존)과 함께 `{error:{code, message}}`도 준다.

| 메서드 경로 | 원본 대비 |
|---|---|
| GET `/summary?ontology` | 같음 + `staged{objects, links, properties}`, `runs[].source_kind`에 `sync` |
| GET `/review-status?ontology` | 같음(키 `schema_id`→`ontology`, `schema_name`→`ontologyName`; F1 보고서 `quality`가 사용) |
| GET `/codes` | 같음 + 새 코드 설명(§7.2) |
| GET·PUT `/policy/{ontology}` | 같음(검증·문구 동일). PUT은 v1 화면 없음, API만 |
| POST `/extract` | `{ontology, fileId?, text?, doc?, samples?(1-10), maxChunks?(1-500, 기본 50)}`. `filename`+`session_id` 대신 `fileId`(업로드 API가 준 id). **경로 문자열 받지 않음**(03 §9) |
| GET `/candidates`, `/candidates/{id}`, `/candidates/{id}/neighborhood` | 같음. 후보에 `target{objectType, linkType?, property?, staged:bool}` 추가 |
| POST `/candidates/{id}/decide` | 같음. `reviewer`는 **받지 않음** — 세션의 사람 신원으로 기록. 에이전트 턴 토큰이면 403 |
| POST `/candidates/bulk-decide` | 같음. 20건 이상이면 네이티브 확인 증표 필요(03 §4 「대량」) [제안] |
| GET `/dlq`, POST `/dlq/redrive`, POST `/dlq/{id}/discard` | 같음. 새 stage `sync`·`edit` |
| POST `/checkup` · `/shapes/run` · `/lint` · `/identity/run` · `/impute` | 같음. `/checkup` 응답에 `cardinality`, `value_types`, `primary_keys` 세부 추가 |
| GET `/shapes?ontology` | 같음. `origin: "definition"|"rule"`(원본 `schema`→`definition`), `kind`에 `required`·`datatype`·`value_type`·`primary_key`·`cardinality` |
| GET `/identity/clusters`, POST `/identity/conflicts/{id}/resolve` | 같음(`reviewer` 제외). 원천 충돌·편집 충돌 항목도 resolve 가능: 편집 충돌은 `{choice: "keep_edit"|"use_source"}` |
| POST `/manual-value` | `{ontology, objectType, key, property, value}`(원본 `class_name`·`name`·`reviewer` → 정리) |
| POST `/source/preview`, `/source/ingest` | `fileId` 사용, 매핑 `class`→`objectType`, `properties{열: 속성 apiName}`, `relations[{column, linkType, targetObjectType}]` |
| POST `/backing/check` | 원본 `/source/check-table`의 후계: `{ontology, objectType, backingId, rules}` — 원천을 규칙별 집계 질의(Data 모듈 읽기 전용 경로). **v1에 화면 있음**(규칙 화면) |
| GET·POST `/rules`, DELETE `/rules/{id}` | 같음. `layer: "source"|"shape"`, `target`은 Object type/Link type apiName 또는 백킹 id |
| GET `/reports` | 같음, layer에 `sync` |
| GET `/kge`, `/kge/score`, POST `/kge/train` | 같음(v1 이후 화면) |
| GET `/export/feedback.jsonl`, `/export/kge-triples.tsv` | 같음 |

공통 오류: 온톨로지 없음 404 「온톨로지를 찾을 수 없습니다: <id>」, 검증 422(`detail` 문자열), LLM 없음 503(§10), 파일 없음 404 「업로드 파일을 찾을 수 없습니다: …」.

---

## 7. 데이터

### 7.1 후보·보류 항목 (원본 §4 형태 유지)
- 후보: 원본 필드 그대로(`id, ontology, run_id, fingerprint, kind, subject, predicate, object, value, evidence(≤20), scores{…}, s_c, reasons, status, decided_by, decided_at, edit, created_at, updated_at`) + `target{objectType, linkType?, property?, staged}`.
  - `kind`: `entity|relation|property|tbox|identity` 문자열 유지(계약).
  - `subject.class`·`object.class` = Object type apiName, `predicate` = Link type apiName(유사어로 바꿔 읽으면 정규 apiName), identity면 `"SAME_AS"`.
  - `reviewer`(문자열) → `decided_by{kind: human, id}`(03 §4). 응답 호환을 위해 `reviewer`에 사람 표시 이름도 넣는다.
- 지문(중복 키)·근거 합치기·**사람 판정 보존**(approved/edited/rejected는 재추출에서 다시 매기지 않음, 통계 `preserved`) — 원본 그대로.
- 보류 항목: 원본 필드 그대로, `stage`에 `sync`·`edit` 추가. `candidate_id` 표식 추가: `sync:<objectType>:<backingId>:<key>`, `edit:<objectType>:<key>:<property>`, `card:<linkType>:<key>`. 같은 표식의 열린 항목은 갱신(중복 없음) — 원본 규칙.
- 정책·실행 기록(`source_kind`에 `sync`)·판정 이력·사용자 규칙·검증 보고서·대표 값·KGE — 원본 그대로, 온톨로지 삭제 시 함께 삭제.

### 7.2 원인 코드
원본 목록을 그대로 두고 추가만 한다.
- **hard**: 원본 10개(`ID_MISSING, REL_ENDPOINT_MISSING, ONTO_CLASS_UNKNOWN, ONTO_DOMAIN, ONTO_RANGE, ONTO_PREDICATE_UNKNOWN, ONTO_PROPERTY_UNKNOWN, ONTO_CARDINALITY, ONTO_INVALID_NAME, PARSE_JSON`) + ★`LINK_NOT_WRITABLE`, ★`PROP_NOT_WRITABLE`, ★`BACKING_MISSING`
- **soft**: 원본 8개(`PROP_DATATYPE, ENTITY_AMBIGUOUS, PREDICATE_SYNONYM, TBOX_PROPOSAL, IMPUTED, LINK_PREDICTED, SAME_AS_PROPOSAL, ENTITY_GENERIC`)
- **항상 검수**: 원본 5개(`TBOX_PROPOSAL, IMPUTED, LINK_PREDICTED, SAME_AS_PROPOSAL, ENTITY_GENERIC`)
- **그 밖**: 원본(`LOW_CONFIDENCE, WRITE_FAILED, SRC_*, SHAPE_*, ORPHAN_NODE, ER_CONFLICT`) + ★`VALUE_TYPE_VIOLATION`, ★`SRC_VALUE_CONFLICT`, ★`EDIT_CONFLICT`, ★`MAPPING_EXPR_ERROR`
- 새 설명 문구: `ONTO_CARDINALITY` 「링크 카디널리티 위반 — 한쪽이 하나만 허용됨」, `LINK_NOT_WRITABLE` 「원천에서 계산되는 링크(외래키·조인 원천)라 직접 넣을 수 없음」, `PROP_NOT_WRITABLE` 「live 저장 방식이라 값을 쓸 수 없음」, `BACKING_MISSING` 「이 Object type에 문서 원천이 연결되어 있지 않음」, `VALUE_TYPE_VIOLATION` 「값 타입(Value type) 제약 위반」, `SRC_VALUE_CONFLICT` 「여러 원천이 같은 속성에 다른 값을 줌」, `EDIT_CONFLICT` 「사람이 편집한 값과 원천 값이 엇갈림」, `MAPPING_EXPR_ERROR` 「매핑 식을 계산하지 못함」. 원본 코드의 설명은 원본 문구에서 「클래스」→「Object type」, 「관계」→「링크」만 바꾼다(전체 목록은 원본 실행 기록에서 채록 [확인 필요]).

### 7.3 판정 규칙 (원본 §5.2–5.3을 새 모델로 — 값은 바꾸지 않음)
**정의 게이트 (결정적)**
- 이름 규칙: 원본 규칙(영문·한글·밑줄 시작, 영문·숫자·한글·밑줄) 그대로. — 후보 이름은 객체 이름(제목 값)이라 02의 apiName 규칙과 별개.
- 객체: 이름과 id 모두 없으면 `ID_MISSING`; Object type 없음/작업본에 미등록 → `ONTO_CLASS_UNKNOWN`(작업본에 타입이 하나도 없으면 부트스트랩 — 원본 규칙); 문서 지시어 이름 → `ENTITY_GENERIC`(원본 단어 목록 그대로).
  - ★ 대상 타입이 live면 `PROP_NOT_WRITABLE`, 대상 타입에 document 원천이 없으면 `BACKING_MISSING`(native이고 원천이 0개면 자동으로 document 주 원천을 붙여도 되는지 → §12).
- 정의 제안(tbox): 항상 `TBOX_PROPOSAL`, 이름 규칙 위반 `ONTO_INVALID_NAME`. 제안 이름은 02 규칙으로 변환해 보여 준다(클래스 → PascalCase, 관계 → camelCase).
- identity: 두 객체 검사, **같은 Object type 또는 같은 Interface 구현 타입**이 아니면 `ONTO_RANGE`, 항상 `SAME_AS_PROPOSAL`.
- property: 미선언 속성 `ONTO_PROPERTY_UNKNOWN`; 타입 판정(원본 규칙 그대로: 문자열류 통과, 정수 「1,200」, 실수, 불리언 「예/아니오」 포함, 날짜 ISO·「YYYY년 M월 (D일)」) — 새 baseType 대응: `integer`·`long` = 정수, `double`·`decimal` = 실수, `date`·`timestamp` = 날짜·일시, `geopoint` = 「위도,경도」, `struct`·`attachment`·`vector`는 문서 추출 대상 아님(`ONTO_PROPERTY_UNKNOWN`). 불일치 `PROP_DATATYPE`. ★ Value type 제약 위반도 `PROP_DATATYPE`(soft) + 메모 「<ValueType>: <제약> 불일치」. 적재 시 선언 타입으로 변환(원본 규칙).
- relation: 술어 빈 값 `ONTO_PREDICATE_UNKNOWN`; 작업본에 Link type이 없으면 이름 규칙만(부트스트랩); 술어 맞추기 ① 정확 일치 ② 공백·`_`·`-` 제거·소문자 비교 ③ 문자열 유사도 ≥ `synonym_min_ratio`(0.82) — 비교 대상 = Link type **apiName·표시 이름·양 방향 이름·별칭·설명**(설명 포함 시 최소 0.9) → `PREDICATE_SYNONYM`, `m_vocab` = 유사도. 정의역·공역 = Link type `from`/`to` 타입(역방향 이름으로 맞으면 주어·목적어를 바꿔 읽음) — 실패 시 `ONTO_DOMAIN`/`ONTO_RANGE`와 원본 메모 형식.
  - ★ 맞춘 Link type의 조인이 `stored`가 아니면: 원천에서 이미 성립하면 「이미 있음」(S_graph=1, 쓰기 없이 `auto_ingested`, 메모 「원천 링크로 이미 연결됨」), 아니면 `LINK_NOT_WRITABLE`.
  - ★ **카디널리티**(`ONTO_CARDINALITY`, 이제 동작): Link type의 one 쪽(many-to-one의 from, one-to-many의 to, one-to-one 양쪽)에 이미 다른 상대가 있으면 hard. 같은 상대면 MERGE라 위반 아님.

**복합 신뢰도·분기** — 원본 §5.3 그대로: `S_c = G_onto × m_vocab × 결합`, S_llm(freq, logprob 사용 시 α 결합), S_ground(감쇠 × (½어휘 + ½정규화 코사인), cos 0.15~0.60 늘림, λ 0.02), S_graph(이미 있으면 1, 2~3홉 우회 경로, prior 0.5, KGE 비중 0.5), linear/harmonic, 엔터티 모호성(상위 2개 차 < 0.15 → `ENTITY_AMBIGUOUS`, 해소는 Object 모듈 검색), 분기 규칙(hard → 보류, < review → `LOW_CONFIDENCE` 보류, ≥ auto 이고 soft 없음 → 자동, 나머지 → 검수, tbox·항상-검수는 점수 무관 검수), 쓰기 실패 → `WRITE_FAILED`, 이전 보류 지문이 이번에 통과하면 `redriven`. S_graph의 「그래프」는 **발행본 객체 + 대기 적재(staged)** 를 함께 본다.

**정책 기본값** — 원본 표 그대로: w 0.3/0.5/0.2, linear, auto 0.85, review 0.60, α 0.5, λ 0.02, samples 3, cos 0.15/0.60, prior 0.5, open_vocabulary_when_empty true, synonym 0.82, **identity_auto 0.95**, identity_review 0.80, kge_weight 0.5, impute 0.6/2. 검증·422 문구 그대로.

### 7.4 단일 쓰기 경로 (원본 §6을 새 모델로)
모든 반영(자동 적재·사람 승인·사람 입력·sameAs·다시 시도)은 Object 모듈의 한 경로를 지난다.
- **객체**: 대상 Object type의 기본 키로 식별. 문서 추출은 원본 규칙대로 키 = 명시 id(정형은 `원천:키`) 또는 `타입:이름` → 기본 키 속성이 1개이고 string이면 그 값으로, 아니면 대기 적재 후 사람이 키를 채우게 `ID_MISSING`. 생성 시 출처 메타(`confidence`, `runId`, `evidenceRef`, `sourceSystem`, `sourceKey`, `createdAt`), 매번 `updatedAt` — 원본 `_confidence`·`_run_id`·`_evidence_ref`… 의 후계(02 §18 「객체 수준 원천 표시」). 제목 속성은 비어 있을 때만 채움(원본 `name` 규칙).
- **링크**: `stored` Link type 간선 MERGE, 같은 메타.
- **속성**: 문서 컬렉션에 (객체 키, 속성, 값, 근거) 기록 → native는 즉시, indexed는 enrichment 병합(priority: document 원천의 priority, 기본 0 = 가장 낮음 [제안]).
- **sameAs**: 두 객체 키를 사전순 정렬해 앞 → 뒤(원본 방향 규칙), 메타 `method`(`key:<속성>`/`name`/`fuzzy`), `confidence`, `since`. 양끝 없으면 `REL_ENDPOINT_MISSING`, 같은 객체면 `ER_CONFLICT`. **객체를 합치지 않는다**(02 §7.6).
- **감사**(01 §7): `actor{kind, id}` — 자동 `system:quality-auto`, 사람 승인 `human:<id>`, 에이전트가 시작한 추출의 자동 적재 `agent:<세션>`(결정은 아님), 다시 시도 `human:<id>`(누른 사람), 점검 `system:quality-lint`; `source` = `extract:<run>`·`identity:<run>`·`sync:<job>`; `reason` = `S_c=0.91`·`hitl:approve`·`ER name 0.97`(원본 형식).
- 그래프 예약 이름은 쓰지 않는다(원본 규칙).

### 7.5 사후 점검 (원본 §5.7 순서·응답 유지, 새 모델 형상)
「지금 점검하기」와 에이전트 `quality_checkup`은 같은 동작: **형상 → 고립 → 동일 개체 → 값 충돌 → 결측 보정**.
- **형상** — 대상: 그 온톨로지 발행본의 indexed·native 객체 + 대기 적재. live 타입은 제외(원본의 가상 노드 제외와 같음 — 원천 검사는 규칙 화면의 「원천 검사」로).
  - 정의에서 자동 생성되는 형상: `required` → 필수(`SHAPE_MIN_COUNT`, 설명 `C.p 필수`), baseType → 타입(`SHAPE_DATATYPE`, `C.p : type`), ★Value type → `VALUE_TYPE_VIOLATION`(`C.p : CountryCode`), ★기본 키 결측·중복 → `ID_MISSING`/`SRC_UNIQUE`(`C 기본 키`), ★Link type 카디널리티 → `SHAPE_MAX_COUNT`(`C -link-> 최대 1`).
  - 사용자 규칙: 원본 `max_count`·`min_rel`·`disjoint` + ★`value_in`(속성 값 목록).
  - 이번에 안 걸린 열린 형상 보류는 해소(원본 규칙). 응답 원본 형식.
- **고립**: 링크 타입이 하나 이상 정의된 Object type의 객체 중 sameAs 외 링크가 하나도 없는 것 → `ORPHAN_NODE`(상세 원본 형식 「C 'name' — 관계 없음, 관계 재추출 대상」). live 타입 제외, 링크 타입이 없는 타입 제외(원본은 클래스 전부 — 링크를 정의하지 않은 타입까지 고립으로 잡는 것은 소음이라 **의도된 차이**).
- **동일 개체**: 원본 규칙 그대로 — 같은 타입(★또는 같은 Interface 구현 타입끼리) 모든 쌍, 같은 정형 원천끼리 제외·문서 추출끼리는 비교, 이미 sameAs면 건너뜀. 점수: 식별 속성(★Property `identifier: true`, 없으면 원본 이름 목록 biz_no/business_no/duns/lei) 양쪽 있으면 숫자만 비교 또는 동일 → 1.0, 다르면 0.0; 없으면 이름(제목 속성) 정규화(법인 표기 「(주)·㈜·주식회사·(유)·유한회사·co.,ltd·inc·corp·corporation」, 공백·구두점 제거, 소문자) 같으면 0.97, 다르면 문자열 유사도. **≥ 0.95 자동 sameAs**, ≥ 0.80 검수. 응답 원본 형식.
- **값 충돌**: sameAs 묶음에서 같은 속성(★Interface 공유 속성은 매핑을 따라 비교)에 다른 값 2개 이상, 대표 값 없으면 `ER_CONFLICT`. 원천 값은 덮지 않음.
- ★**동기화 점검**(indexed 동기화가 끝날 때마다 자동, 점검 버튼에서도): `SRC_VALUE_CONFLICT`(priority로 버려진 원천 값이 이긴 값과 다름 — 원천별 값 기록, 대표 값 선택 시 해소; 대표 값은 **표시·질의 값에 쓰지 않고 기록만**[원본 원칙] — 쓰고 싶으면 F1에서 priority 변경), `EDIT_CONFLICT`(D-06 `flag` 타입만: 편집 이후 원천 값이 바뀐 속성), `MAPPING_EXPR_ERROR`, `SRC_FK`(foreign-key 링크 대상 없음 — 원본 「대상 키가 없는 값은 잇지 않음」을 기록으로 남김; 링크 정의에 「미일치 보고」 켬일 때만 [제안]).
- **결측 보정 제안**: 원본 우선순위 그대로 ① sameAs 상대 값 ② 이웃 패턴(지지 ≥ 2, 비율 ≥ 0.6) ③ ★Property `default` ④ KGE 링크 예측(≥ 0.7, 최대 20). 모두 `IMPUTED`/`LINK_PREDICTED`로 검수행, 근거 문구 원본 형식.
- 점검 요약 응답 원본 키 그대로 + `details.sync`.

### 7.6 사람의 결정·다시 시도·사람 입력
원본 §5.8–5.10 그대로. 차이:
- tbox approve/edit → **작업본**에 Object type/Link type 추가(출처 `quality_review`), 응답 `applied: "draft"`(원본 `"schema"` — 의도된 차이). 이 정의를 기다리던 보류는 원본처럼 자동으로 풀리지 않는다(다시 시도 필요).
- 승인·수정 → 게이트 재검사(hard면 422 「스키마 제약 위반으로 적재할 수 없습니다: CODE(설명), … — 메모」 원본 문구 유지) → 쓰기(확신값 = max(S_c, 0.85)).
- identity edit 422 「동일 개체 제안은 승인·기각만 됩니다」, 이미 처리 422 「이미 처리된 후보입니다 (status)」, 일괄은 approve|reject만 — 원본 그대로.
- 다시 시도 outcome 표(원본 §5.9) 그대로 + `sync` 항목(그 행만 재동기화 → `ingested`/`resolved`/`still_failing`), `edit` 항목(재검사 → `resolved`/`still_failing`). 3회 한도는 `exhausted` 표시만.
- 「그래도 넣기」 = 묶인 후보 승인(원본).
- `EDIT_CONFLICT` resolve: `keep_edit` → 편집 레이어 유지·항목 해소 / `use_source` → 그 편집 레이어 값 삭제(감사에 사람·이유)·해소.

### 7.7 문서 추출 (원본 §5.4, LLM 경로만 교체)
- 청크(1800자·단락 단위·오프셋 유지·id `<문서>#cNNNN`), 머리말(`문서: <이름>` + 앞 400자), 요청당 청크 상한(화면 50, 에이전트 50, 재처리 5), 값 블록(문서 머리말 · **허용 Object type**(표시 이름 — 설명 (속성: apiName:baseType[:ValueType], …), 쓰기 불가 타입은 제외) · **허용 Link type**(`apiName: From -> To — 설명`, stored만) · 검수 예시(최근 판정 **8개**) · 청크), 지시문 요지·출력 JSON 형식·M번 샘플·파싱 실패 규칙·인용 위치 찾기 — 원본 그대로.
- **LLM 호출**(04 §3): Agent 모듈의 단일 클라이언트. 순서 — ① F8에 설정한 API 공급자(추출 모델 설정, 없으면 기본 모델; JSON 모드, logprob 지원 시 사용) ② API 공급자가 없고 CLI 에이전트만 있으면 `extract` 모드 1회 실행으로 M번 샘플(logprob 없음, freq만) ③ 둘 다 없으면 503. 임베딩(S_ground 코사인)도 같은 클라이언트, 없으면 어휘 근거로 대신(원본 규칙).
- 문서 텍스트: 업로드 파일(PDF 텍스트 추출, D-15⑤ OCR 켜졌으면 OCR 텍스트). 파일은 **fileId로만** 지정.

### 7.8 정형 CSV 적재·파서 선별
- CSV: 원본 §5.5 그대로(매핑 필수 키, 「파일에 없는 컬럼: [...]」, 인코딩 UTF-8(BOM)→CP949→EUC-KR, 원천 규칙·severity·보고서 형식, 행별/파일 보류, 통과 행 → 후보, 근거 `파일#row<줄>`, freq 1·ground 1). 매핑 이름만 새 모델(§6).
- 파서 일괄 적재(F1 `batch_ingest`): 원본 §5.6 그대로(구조만, 미등록 타입은 막지 않음 — 단 발행 전엔 staged, 응답 `quarantined{count, by_reason, samples(5)}`).
- **경로 규칙**(03 §9): 파일은 대화 작업 공간의 업로드·출력 폴더 안만. 에이전트 도구의 `source`가 경로면 작업 폴더 상대 경로만 허용(`uploads/a.csv`, 원본 호환으로 `/workspace/…` 접두는 작업 폴더로 해석), 다른 절대 경로·`..`·심볼릭 링크는 400 「작업 폴더 밖의 파일은 읽을 수 없습니다: <경로>」(원본 결함 수정).

---

## 8. 에이전트 연동

| 도구 (build 모드) | 원본 | 계약 |
|---|---|---|
| `document_extract(fileId | text, ontology, targetTypes?, samples=0)` | `extract_triples` | 실행 통계(원본 §5.4 응답 키) + `note` 원본 문구 「검수 대기(pending)와 DLQ 항목은 사용자가 품질 화면에서 판단합니다. 대신 승인하거나 재처리하지 마세요.」 |
| `table_ingest(source, mapping_json, ontology, dry_run)` | 같음 | 원본 응답 키, 경로 규칙 §7.8 |
| `batch_ingest(source, ontology)` | 같음(M1) | 선별 §7.8 |
| `quality_checkup(ontology)` | 같음 | 점검 요약(details 제외) + `review` |
| `quality_report(ontology)` | 같음 | summary(policy 제외) |
- 오류는 `{"error": "…"}` JSON(예외 없음). 온톨로지는 이름(정확 일치)으로 찾는다.
- **결정·재처리·폐기·정책·대표 값·규칙 도구는 만들지 않는다**(원본 원칙). `decide`·`redrive`·`discard`·`resolve`·`manual-value` API는 에이전트 턴 토큰으로 403(03 §5 — 원본은 인증이 없어 우회 가능했던 경로).
- 구축 스킬 Phase 4(F1 §8.3)가 점검 1회 후 사람이 판단할 건수·원인을 3~5줄로 알리고, 승인 대행·규칙 완화를 하지 않는다.
- F1 보고서 `quality`는 백엔드가 review-status로 붙인다(원본 규칙).
- 내부 `extract` 모드(04 §4): 도구 없음, 입력 = 지시문 + 값 블록, 출력 = 원본 추출 JSON 하나. CLI 경로에서만 쓰인다.

---

## 9. 보안·권한

| 항목 | 규칙 |
|---|---|
| 결정 주체 | 결정·다시 시도·버리기·사람 입력·대표 값은 **사람 세션**만. 검토자 = 세션 신원(원본 고정 `studio-user` 대체). 감사에 `actor.kind=human` |
| 대량 처리 | 일괄 결정 20건 이상·「모두 다시 시도」 50건 이상은 네이티브 확인 증표(03 §4 「대량」) [제안 — 한도는 §12] |
| 에이전트 | 추출·적재·점검·현황 도구만, 결정 계열 API 403 |
| 파일 | §7.8 경로 규칙, 업로드 이름 정규화(03 §9) |
| LLM | 단일 클라이언트만(04 §3). 문서 텍스트가 외부 LLM으로 나간다는 사실을 F8 공급자 설정 화면에 표시. PII 속성 값은 few-shot 예시에서 마스킹 |
| 원천 검사 | 규칙 값에 `'` `;` `\` `--` 거부, 식별자 영문·숫자·밑줄(원본 규칙) + 질의는 코어가 생성(사용자 SQL 없음), `fabric_ro` 역할·시간 제한 |
| 편집 충돌 해소 | `use_source`는 편집 레이어 삭제 = 데이터 변경이므로 감사에 사람·이유·이전 값 |

---

## 10. 오류·예외

- 원본 §12 그대로: 그래프가 꺼져도 화면은 열림(주변 그래프는 빈 그래프 + error, S_graph는 prior, 형상 하나 실패는 그 결과에 error), 한 항목 실패가 묶음을 멈추지 않음, 출처 기록 실패가 승인을 막지 않음, JSON 아닌 응답 = 샘플 실패, logprob 거부 모델이면 끄고 재호출.
- 문구 변경(의도된 차이):

| 상황 | 원본 | 새 |
|---|---|---|
| LLM 없음 | 503 「OPENAI_API_KEY 가 없어 LLM 추출을 할 수 없습니다.」 | 503 「LLM이 설정되지 않아 추출을 할 수 없습니다. 설정에서 AI 공급자를 지정하거나 에이전트(Claude Code·Codex)를 설치하세요.」 |
| 스키마 없음 | 404 「스키마를 찾을 수 없습니다: <id>」 | 404 「온톨로지를 찾을 수 없습니다: <id>」 |
| 작업 폴더 밖 파일 | (검사 없음) | 400 「작업 폴더 밖의 파일은 읽을 수 없습니다: <경로>」 |
| 에이전트가 결정 API 호출 | (가능) | 403 「품질 판단은 사람만 할 수 있습니다.」 |
| 관계 추가 토스트 | 「‘X’ 관계를 지도에 추가했어요 — …」 | 「‘X’ 관계를 작업본에 추가했어요 — …」 |
| tbox 승인 토스트 | 「지식 지도에 새 종류를 추가했어요: …」 | 「작업본에 새 종류를 추가했어요 — 발행하면 지식 지도에 보여요: …」 |

- 새 상황: 대상 정의가 작업본에서 삭제된 대기 적재 → 다음 다시 시도에서 `ONTO_CLASS_UNKNOWN`/`ONTO_PREDICATE_UNKNOWN` 보류. 발행 시 staged 반영 실패 → 해당 항목 `WRITE_FAILED` 보류, 발행은 성공(staged 반영은 발행 원자성 범위 밖 [제안 — §12]).

---

## 11. 원본과 비교할 테스트

결정적 규칙은 **값까지** 같아야 한다(원본 M6 설계 §13). LLM 추출은 구조·계약만.

### 11.1 같아야 함
1. 정책 기본값 응답, 가중치 합 0.9 → 422와 문구, review > auto → 422. (#1)
2. 게이트 표: 미등록 타입(작업본에 타입 있음/없음), 이름 규칙, 지시어 이름(「본 증권」「당사」, id 있음/없음), 미선언 속성, 타입(「1,200」 int 통과, 「12a」 실패, 「2026년 9월」 date 통과, 「예」 bool 통과), 술어 정확/대소문자·밑줄 차이/설명 포함/유사도 0.82 경계, 정의역·공역, 부트스트랩 — 같은 hard/soft 코드. (#2)
3. 점수: 신호 고정 후보로 S_c·route 재현(linear/harmonic, 0 포함 harmonic, m_vocab<1, 이미 있는 링크 S_graph=1, 경로 없음 prior). 항상-검수는 0.95여도 review. (#3)
4. 분기 경계: S_c 0.85 → auto(soft 없음), 0.5999 → dlq `LOW_CONFIDENCE`. (#4)
5. 지문: 재추출 시 행 1개·근거 누적, 기각 후 재추출 `preserved` 증가. (#5)
6. 결정: 이미 처리 422, identity edit 422, 정의 위반 승인 422 문구, 승인 시 확신값 max(S_c, 0.85). (#6)
7. CSV: block → 0행·보류 1, row → 해당 행만(`row:` 표식), 키 `원천:키`, 고쳐서 다시 시도 → ingested. (#7)
8. 점검: 필수 누락 수 = missing_values, 값 입력 후 resolved 증가, 고립, 「(주)가나」·「가나 주식회사」 → sameAs 자동(0.97, 사전순 방향), 값 충돌 → 대표 값 → 재점검 시 재발 안 함, 원천 값 불변. (#8)
9. 결측 보정 우선순위, 지지 2·비율 0.6 경계. (#9)
10. 다시 시도 outcome 종류별 1건, 시도 수 증가, 3회 초과도 허용. (#10)
11. 파서 선별: id 없는 노드·끝점 없는 링크 → 보류, 나머지 적재, `quarantined`. (#11)
12. 화면: 보류 묶음 분류(원본 코드 → 원본 묶음), 카드 배지·이유 문구, 버튼 세트, Y/N/E/→, 구축 탭 배지 합, 보고서 카드 표시 조건. (#12)
13. 에이전트: build 도구 목록에 품질 도구가 있고 결정 도구 없음, 도구 응답 키와 `note` 문구. (#13)
14. KGE 422(삼중주 < 4)·응답 키, 내보내기 JSONL·TSV 형식. (#14, #15)

### 11.2 의도된 차이 (D-12)
| # | 원본 | 새 | 테스트 |
|---|---|---|---|
| 1 | 카디널리티 검사 미동작 | Link type 카디널리티로 `ONTO_CARDINALITY`·`SHAPE_MAX_COUNT` 동작 | N2 |
| 2 | 추출 LLM이 OpenAI 호환 API 직접 호출 | 단일 LLM 클라이언트, CLI `extract` 모드 대체 경로 | 키 없음 + CLI 있음 → 추출 성공(logprob 없음) |
| 3 | `table_ingest`가 임의 경로 파일 읽음 | 작업 폴더 안만 | `/etc/passwd` → 400 |
| 4 | 검토자 `studio-user` 고정, 결정 API 무인증 | 세션 사람 신원, 에이전트 403 | 감사 actor |
| 5 | tbox 승인 = 스키마에 즉시 | 작업본 변경(`applied:"draft"`) | 승인 후 제안 diff에 나타남 |
| 6 | 이유 문구 「세 번」 고정 | 샘플 수 M | samples=5 → 「다섯 번」 |
| 7 | 고급 8개 탭 | v1은 기본 3탭 + 규칙 화면(D-16) | 화면 목록 |
| 8 | 고립 = 클래스 전부 | 링크 타입이 정의된 타입만 | 링크 없는 타입의 객체는 고립 아님 |
| 9 | 형상 = required·type·사용자 규칙 | + Value type·기본 키·카디널리티 | N1·N2 |
| 10 | 다원천 충돌은 SAME_AS 묶음만 | + 백킹 원천 충돌(`SRC_VALUE_CONFLICT`)·편집 충돌(`EDIT_CONFLICT`) | N3·N4 |
| 11 | 계산 관계 개념 없음 | foreign-key 링크에 쓰기 → 「이미 있음」 또는 `LINK_NOT_WRITABLE` | 게이트 표 추가 행 |
| 12 | 오류 메시지 용어 「스키마」 | 「온톨로지」 | §10 표 |

---

## 12. 열린 질문

1. **식별 속성·기본값 선언**: 원본 동일성 판정과 결측 보정은 Property의 `identifier`·`default`를 쓴다. → **해결: 02 §6에 추가됨.**
2. **staged(대기 적재)의 위치**: 02 §14·§16에 「발행 전 정의에 대한 객체·링크는 대기 적재로 두고 발행 시 반영」을 넣을지, 아니면 문서 추출은 발행된 타입에만 허용할지(구축 흐름이 막힘). staged 반영 실패를 발행 원자성에 포함할지.
3. **native 타입 자동 document 원천**: 원천이 0개인 native 타입에 문서 사실이 오면 document 주 원천을 자동으로 붙일지(`BACKING_MISSING` 대신). 작업본 변경이 자동 발생하는 것이 「사람이 결정」 원칙과 맞는지.
4. **대량 처리 증표 한도**(일괄 20건·다시 시도 50건) — 03 §4의 「대량 삭제」 정의와 맞출 것.
5. **원천 충돌의 대표 값**을 질의 값으로 쓸지: 원본 원칙(그래프 값 불변)을 따라 기록만 하기로 했다. 사용자가 「대표 값을 실제로 쓰고 싶다」면 priority 변경으로 유도 — 충분한지.
6. **sameAs 교차 타입 범위**: 같은 Interface 구현이면 허용으로 했다. 02 §7.6 예(문서 Supplier ↔ ERP Supplier)는 같은 타입인데, 다른 타입끼리를 더 넓게 허용할지.
7. 원인 코드 설명 문구 전체(원본 `GET /codes`)는 실행 기록에서 채록 [확인 필요].
8. `extract` 모드(CLI)로 M번 샘플을 돌릴 때 비용·시간 — 기본 samples를 CLI 경로에서는 1로 낮출지(점수 분포가 달라짐).

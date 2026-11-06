# 02. 온톨로지 메타모델 (Palantir식 Object type 모델)

> 이 문서가 SoT의 중심이다. 다른 문서는 여기의 개념 이름을 그대로 쓴다.

## 1. 왜 바꾸나 — 원본 모델의 한계 [원본]
원본은 온톨로지를 **클래스**로 정의하고, 데이터 연결을 **가상 노드**로 한다: 데이터소스 테이블 하나를 노드 타입 하나로 노출하고(`CREATE VIRTUAL NODE … FROM ds.table KEY col`), 행 하나가 인스턴스 하나다. 근거: 분석 `menus/03-datasources/design.md` §4, `menus/01-ontology-build/design.md` §3·§7.

| 한계 | 결과 |
|---|---|
| 노드 타입 = 테이블 1개 | "협력사"가 ERP·WMS에 나뉘어 있으면 타입이 둘(또는 하나만 선택). 업무 객체가 시스템 구조에 끌려감 |
| 키 = 컬럼 1개, 변환 없음 | 같은 발주 번호가 ERP `po_id`, WMS `ref_po_no`로 형식까지 다르면 잇기 어려움 |
| 속성 = 컬럼 그대로(이름 바꾸기 정도) | 단위 변환·코드값 매핑·계산 속성 불가 |
| 가상 관계 = 두 컬럼 같음 조인만 | N:N(조인 테이블), 관계 자체의 속성, 변환 조인 불가 |
| 가상(읽기 전용) ↔ 물리(복사본)가 클래스 단위 양자택일 | 원천을 읽으면서 일부 속성만 업무용으로 편집하는 구성 불가 |
| 정의는 SQLite, 그래프는 발행 사본, 클래스 이름이 그래프 전역 라벨 | 같은 이름 클래스가 온톨로지끼리 섞임, 발행 = 전체 덮어쓰기, 변경 이력 없음 |
| 다형성·재사용 없음 | "거래처(협력사·고객 공통)" 같은 공통 형태를 표현 못 함 |

## 2. 핵심 개념 [조사 → 제안]
[조사] Palantir는 온톨로지를 **Semantic**(무엇이 있는가)과 **Kinetic**(무엇을 할 수 있는가)으로 나눈다. 새 모델도 같은 구분을 쓴다.

| 구분 | 개념 | 한 줄 정의 | 원본 대응 |
|---|---|---|---|
| 컨테이너 | **Ontology** | 개념들의 묶음(이름공간·버전 단위) | 스키마 그룹 |
| | Type group | 업무 도메인별 묶음(표시용) | 없음 |
| Semantic | **Object type** | 현실 업무 객체의 스키마. 기본 키·제목 속성·속성·백킹 데이터를 가짐 | 클래스 |
| | **Object** | Object type의 인스턴스 | 인스턴스(그래프 노드) / 가상 노드의 행 |
| | **Property** | 타입이 있는 속성 | 클래스 속성 |
| | **Shared property** | 여러 Object type이 같은 의미로 재사용하는 속성 정의 | 없음 |
| | **Value type** | 값 제약이 붙은 의미 타입(이메일, 통화 금액, 국가 코드 …) | 없음 |
| | **Link type** | 두 Object type 사이 관계. 카디널리티·조인 방식 | 관계 유형 / 가상 관계 |
| | **Interface** | 여러 Object type이 구현하는 공통 형태(다형성) | 없음 |
| | **Backing source** | Object type에 데이터를 공급하는 원천과 매핑 | 바인딩 / 가상 노드 정의 |
| Kinetic | **Action type** | 객체·링크 변경과 업무 시스템 호출의 묶음 + 파라미터·규칙·제출 조건·승인 | 액션 |
| | **Function** | 온톨로지를 읽고 계산하는 로직(질의형·계산형·LLM형) | behavior(SQL) |
| | **Object set** | 필터·탐색·검색으로 정의한 객체 집합 | (질의 결과) |
| 표현 | **Object view** | Object type별 기본 상세 화면(객체 360°) | 없음 |
| 관리 | **Proposal / Version** | 변경 제안 → 검토 → 발행(버전) | 발행(덮어쓰기) |
| 검증 | **Golden question / Golden command** | 온톨로지가 답해야 할 질문 / 실행해야 할 지시 (테스트 케이스) | 같음 |

## 3. 공통 규칙
- **이름**: 모든 정의는 `apiName`(코드용, 변경 불가에 가깝게 취급)과 `displayName`(화면용, 한국어 가능)을 가진다.
  - Object type·Interface·Value type: `PascalCase` (`^[A-Z][A-Za-z0-9]*$`)
  - Property·Shared property·파라미터: `camelCase` (`^[a-z][A-Za-z0-9]*$`)
  - Link type 방향 이름: `camelCase` (예: `supplier`, `purchaseOrders`)
  - Action type·Function: `camelCase` 동사형 (예: `expediteShipment`)
- **이름공간**: 정의의 전체 이름 = `<ontology apiName>.<apiName>`. 그래프 라벨·API 경로는 전체 이름을 쓴다 → **원본의 "같은 이름 클래스가 온톨로지끼리 섞이는" 문제 해결**.
- **식별자**: 모든 정의는 불변 `rid`(UUID)를 가진다. 이름을 바꿔도 참조는 rid로 유지.
- **상태**: `experimental` / `active` / `deprecated`. deprecated는 새 참조 불가, 기존 동작 유지.
- **설명**: `description`(사람용), `aiDescription`(에이전트 도구 설명용, 없으면 description 사용) [조사: Action type의 Tool description].

## 4. Ontology와 Type group
```yaml
Ontology:
  rid, apiName: SupplyChain, displayName: 공급망 운영
  description, intent            # 구축 의도 (원본 브리프)
  goldenQuestions: [GoldenQuestion]   # §15
  goldenCommands:  [GoldenCommand]
  typeGroups: [{apiName, displayName, color, members:[rid]}]
  publishedVersion: int | null   # §14
```

## 5. Object type
```yaml
ObjectType:
  rid, apiName: Shipment, displayName: 선적, pluralDisplayName: 선적들
  description, aiDescription, aliases: [입고 선적]
  status: active
  icon, color
  primaryKey: [shipmentNo]        # 1개 이상 (복합 키 허용 — 원본은 1개만)
  titleKey: shipmentNo            # 화면 표시 이름
  properties: [Property]          # §6
  implements: [Interface rid]     # §9
  storage: live | indexed | native   # §7.3
  backing: [BackingSource]        # §7
  editable: [propertyApiName]     # 액션으로 편집 가능한 속성 (§7.4)
  searchable: { fullText: [prop], vector: { enabled, fields: [prop] } }
  groups: [typeGroup]
```
규칙:
- 기본 키 속성은 `required`, 값이 객체 안에서 유일해야 한다.
- 제목 속성은 문자열로 표시 가능한 속성이어야 한다.
- 속성 0개, 백킹 0개인 Object type은 `native`일 때만 허용(액션·수동 입력으로만 객체 생성).

## 6. Property · Shared property · Value type
```yaml
Property:
  apiName: delayDays, displayName: 지연일
  baseType: integer               # 아래 표
  array: false
  valueType: rid | null           # 값 제약
  sharedProperty: rid | null      # 공유 속성을 쓰면 타입·제약을 상속
  required: false
  identifier: false               # 동일성 판정(sameAs, F6)에 쓰는 자연 키 — 기본 키와 별개 (F1·F6 제안 반영)
  default: null                   # 결측 보정·생성 시 기본값 (F6 결측 보정에서 사용)
  pii: false                      # 화면·에이전트 노출 규칙에 사용 (03 문서)
  formatter: { kind: number, unit: 일 }
  computed: null | { function: rid, inputs: {...} }   # 계산 속성 (§11)
  description
```
| baseType | 설명 | 원본 대응 |
|---|---|---|
| string, boolean | | string, boolean |
| integer, long, double, decimal | decimal은 정밀 금액용 | integer, float |
| date, timestamp | | date |
| geopoint | 위도·경도 | 없음 |
| struct | 이름 있는 하위 필드 묶음 | 없음 |
| attachment | 문서·파일 참조 | 없음 |
| vector | 임베딩 (검색용, 화면 비표시) | 내부 embedding |
| `array: true` | 위 타입의 배열 | list |

**Value type** — 재사용 값 제약:
```yaml
ValueType: { rid, apiName: CountryCode, baseType: string,
             constraints: { regex: '^[A-Z]{2}$' | enum: [...] | range: {min,max} | length: {min,max} },
             description }
```
**Shared property** — 여러 타입에 같은 의미로 쓰는 속성 정의(이름·타입·Value type·설명). Interface의 구성 요소가 된다.

## 7. 백킹 데이터 (Backing source) — 새 모델의 핵심
### 7.1 개념
Object type은 저장 방식과 분리된 **의미 타입**이다. 실제 데이터는 하나 이상의 **Backing source**가 공급한다.
- **주 원천(primary)**: 객체의 **존재**를 결정한다. 주 원천의 한 행(레코드) = 객체 하나.
- **보강 원천(enrichment)**: 키 매핑으로 같은 객체를 찾아 **속성을 덧붙인다**. 보강 원천에만 있는 행은 객체를 만들지 않는다.
- [조사] Palantir의 "데이터셋 행 → 객체, 열 → 속성, 속성 편집기의 컬럼 매핑·Automap"에 해당. 새 모델은 여기에 다원천 보강과 변환을 더한다.

```yaml
BackingSource:
  id, role: primary | enrichment
  kind: table | sql | system | document | manual
  ref:                                  # kind별
    table:    { datasource: erp, table: purchase_order }
    sql:      { datasource: erp, select: "SELECT …" }        # 읽기 전용 단일 SELECT, 검증 필수
    system:   { system: wms, operation: listShipments, recordsPath: data.items }
    document: { collection: rid }       # 문서 추출 결과 (품질 게이트 통과분, F6)
    manual:   {}                        # 액션·화면 입력 (native 전용)
  key:                                   # 이 원천의 행 → 객체 기본 키
    - property: poId
      expr: "trim(upper(po_id))"         # §7.5 표현식
  match:                                 # enrichment 전용: 객체를 어떻게 찾나
    - { property: poId, expr: "replace(ref_po_no, 'PO-', '')" }
  mappings:
    - { property: amountUsd, expr: "amount_usd" }
    - { property: statusLabel, expr: "map(status, {'O':'열림','C':'닫힘'})" }
  filter: "status <> 'X'"               # 원본의 기본 조건(base conditions)
  priority: 10                          # 같은 속성을 여러 원천이 줄 때 높은 쪽 우선 (§7.6)
  refresh: { mode: live | schedule | manual, cron?: "0 * * * *" }   # indexed일 때
```

### 7.2 예: 튜토리얼 공급망을 새 모델로 [제안]
| Object type | 주 원천 | 보강 원천 | 비고 |
|---|---|---|---|
| Supplier (협력사) | `erp.supplier` (key `supplier_id`) | — | WMS의 `vendor_code`는 Link로 연결 |
| PurchaseOrder (발주) | `erp.purchase_order` (key `po_id`) | `wms.shipment`에서 "최근 선적 상태" 계산 속성 | |
| Shipment (선적) | `wms.shipment` (key `shipment_no`) | — | `ref_po_no` → PurchaseOrder 링크(변환 조인) |
| Item (품목) | `erp.item` (key `item_id`) | `crm.sales_order.sku_code`로 판매 집계(계산 속성) | ERP `item_id` = CRM `sku_code` |
| Customer (고객) | `crm.customer` (key `cust_no`) | — | |
| Partner (거래처, **Interface**) | — | — | Supplier·Customer가 구현: `name`, `country` 공유 |

원본에서 "컬럼 이름이 시스템마다 다르다(po_id vs ref_po_no, item_id vs sku_code)"는 튜토리얼의 핵심 문제가, 원본에선 같은 값일 때만 가상 관계로 이어졌다. 새 모델에선 **키 표현식과 Link 조인 변환**으로 정식으로 다룬다.

### 7.3 저장 방식 (storage)
| 방식 | 데이터 위치 | 신선도 | 편집 | 검색·벡터 | 용도 | 원본 대응 |
|---|---|---|---|---|---|---|
| **live** | 원천에 그대로(질의 때 읽음) | 질의 순간 | 불가(읽기 전용). 쓰기는 액션의 시스템 호출로 원천에 | 제한(원천 질의) | 큰 테이블, 항상 최신 | 가상 노드 |
| **indexed** | 그래프에 동기화된 사본(병합된 객체) | 마지막 동기화 | `editable` 속성만 액션으로 편집(편집 레이어, §7.4) | 가능 | 다원천 병합, 빠른 탐색·검색 | 물리화 (원본은 단순 복사) |
| **native** | 그래프에만 존재 | — | 액션·화면으로 생성·편집·삭제 | 가능 | 원천 없는 업무 객체(예: 조치 요청, 메모), 문서 추출 객체 | 문서 구축 인스턴스(materialized 클래스) |
- `live`는 주 원천이 `table`/`sql`이고 보강 원천이 0개 또는 같은 데이터소스일 때만 허용(다른 원천과의 실시간 병합은 비용이 커서 `indexed` 권장). [제안]
- 저장 방식은 Object type 단위로 바꿀 수 있다(제안·발행 필요). 바꾸면 동기화 작업이 돈다.

### 7.4 편집 레이어 (indexed의 사용자 편집)
[조사] Palantir는 원천 데이터 위에 사용자 편집(액션 결과)을 겹쳐 보관한다. 새 모델:
- `editable`로 지정한 속성만 액션이 바꿀 수 있다. 바꾼 값은 **편집 레이어**(객체 키 + 속성 + 값 + 액션 실행 id)에 저장되고, 화면·질의에서는 편집 값이 원천 값보다 우선한다.
- 원천이 같은 속성을 바꾸면 충돌 정책: `edit-wins`(기본) / `source-wins` / `flag`(품질 대기열로, F6).
- 원천 시스템에도 반영해야 하면 액션에 **시스템 호출 규칙**을 함께 둔다(원본의 writeback 개념, §10).

### 7.5 표현식
매핑·키·필터·계산에 쓰는 작은 식 언어. SQL 부분집합 수준으로 제한한다.
- 참조: 원천 컬럼 이름(`po_id`), 객체 속성(`$this.poId`), 파라미터(`$params.x`)
- 함수: `trim, upper, lower, concat, substr, replace, regexExtract, cast(x, type), coalesce, map(x, {…}), round, dateParse, dateFormat, now()`
- 연산: 비교, `and/or/not`, 산술, `in`, `isNull`
- 평가 위치: live는 원천 SQL로 번역, indexed는 동기화 시 코어에서 평가. 번역 불가 함수가 쓰이면 live를 거부하고 이유를 보여 준다.

### 7.6 병합과 식별
- 같은 속성을 여러 원천이 주면 `priority`가 높은 원천 값(같으면 주 원천). 값이 다르면 F6 품질 "값 충돌"로 기록(원본 M6의 대표 값 선택과 연결).
- 서로 다른 Object type이지만 같은 실체인 경우(예: 문서에서 뽑은 Supplier와 ERP Supplier)는 **동일성 링크**(`sameAs`)로 연결한다. 점수 ≥ 0.95 자동, 그 미만은 검수(원본 M6 규칙 계승). 자동 병합은 하지 않는다(설명 가능성).

## 8. Link type
```yaml
LinkType:
  rid, apiName: shipmentPurchaseOrder
  from: { objectType: Shipment, apiName: purchaseOrder, displayName: 발주 }      # 정방향
  to:   { objectType: PurchaseOrder, apiName: shipments, displayName: 선적들 }    # 역방향
  cardinality: many-to-one          # one-to-one | one-to-many | many-to-one | many-to-many
  join:
    method: foreign-key | join-source | link-object | stored
    foreign-key: { fromExpr: "replace(ref_po_no,'PO-','')", toProperty: poId }   # 변환 허용
    # 대상이 복합 키면 쌍 목록: pairs: [{ fromExpr, toProperty }, …] — 대상 기본 키의 모든 속성을 덮어야 함
    join-source: { source: BackingSource(kind table/sql), fromKey: expr, toKey: expr }   # N:N
    link-object: { objectType: rid }   # 링크 자체가 객체(속성 보유) — 예: 계약
    stored:      {}                    # 액션·추출이 만든 간선 (native/indexed)
  description, aiDescription, status
```
| 조인 방식 | [조사] Palantir | 원본 대응 |
|---|---|---|
| foreign-key | Foreign key | 가상 관계(같음 조인만, 변환 불가) |
| join-source | Dataset(조인 테이블) | 없음 |
| link-object | Object type | 없음 |
| stored | (액션으로 링크 생성) | 문서 구축의 관계 적재 |
- 카디널리티는 검증 규칙이 된다(F6 점검에서 위반 검출 — 원본은 카디널리티 검사가 동작하지 않았음).

## 9. Interface
```yaml
Interface:
  rid, apiName: Partner, displayName: 거래처
  properties: [SharedProperty rid]     # 구현 타입이 반드시 가져야 하는 속성
  links: [{ apiName, targetInterfaceOrType, cardinality }]   # 선택
  implementedBy: [ObjectType rid]
```
- Object set·Function·Action 파라미터·앱 위젯에서 Interface를 타입처럼 쓸 수 있다(예: "모든 거래처 중 국가=JP").
- 구현 타입은 Interface 속성을 자기 속성에 매핑한다(이름이 달라도 됨).

## 10. Action type
원본 액션 계약(분석 `menus/01-ontology-build/design.md` §7.4, `menus/02-query-action/design.md`)을 **포함**하고, Palantir식 편집 규칙·제출 조건을 더한다.

```yaml
ActionType:
  rid, apiName: expediteShipment, displayName: 선적 긴급 처리
  description, aiDescription            # 에이전트 도구 설명
  target: { objectType: Shipment, mode: single | set, maxTargets: 50 }
  parameters:                           # 타입 있는 입력
    - { apiName: reason, baseType: string, required: true }
    - { apiName: newPriority, baseType: string, valueType: Priority, default: HIGH }
    - { apiName: owner, objectType: Employee }        # 객체 참조 파라미터
  rules:                                 # 순서대로 적용 (한 트랜잭션 + 시스템 호출 사가)
    - modifyObject: { object: $target, set: { priority: $params.newPriority } }      # 편집 레이어
    - createObject: { objectType: ExpediteRequest, set: {...}, link: { shipment: $target } }
    - createLink / deleteLink / deleteObject
    - callSystem:                         # 원본 steps (시스템 operation 호출)
        name: setPriority, system: wms, operation: updateShipmentPriority
        args: { path.shipmentNo: $target.shipmentNo, body.priority: $params.newPriority }
        compensation: { operation: updateShipmentPriority, args: { body.priority: $before.priority } }
  submissionCriteria:                    # [조사] 누가·어떤 조건에서 제출 가능
    - { when: "$target.status == 'IN_TRANSIT'", message: "운송 중인 선적만 처리할 수 있습니다" }
    - { roles: [scm_operator] }
  approval:
    required: true | false | { when: "count($targets) > 3" }    # 원본 confirm_threshold 일반화
    approverRoles: [scm_manager]
    separationOfDuties: true             # 계획자 ≠ 승인자 (에이전트 포함) — 원본 결함 수정
  sideEffects:                           # 실행 후 (실패해도 액션은 성공 처리, 기록)
    - notify: { channel: in-app, to: $target.owner }
    - webhook: { system: crm, operation: postNotice }
  effect: write | read
  writeback: { property: status, value: "$steps.setPriority.response.status" }   # 원본 writeback_property 일반화
  compensate: cancelExpedite | null      # 취소용 액션 (원본 compensate)
  goldenCommand: rid | null              # 이 액션이 해결하는 골든 커맨드
  version, verifiedAt, verifySummary
```
실행 단계(원본 M2 흐름 유지): **계획(dry-run: 대상 해석·조건 평가·허용/거부 대상·미리보기 호출)** → **승인(필요 시, 사람만, 증명 필요 — 03 문서)** → **실행(규칙 순서, 시스템 호출은 사가: 실패 시 앞 단계 보상)** → **결과 기록(감사·편집 레이어·writeback)** → **취소(보상)**.
- 원본 표현식 뿌리(`$this`, `$params`, `$actor`, `$run`, `$plan`, `$before`, `$steps`, `$cancel`)와 인자 매핑 키 형식(`path.|query.|header.|body.`)을 **그대로 유지**(원본과 비교 가능). `$this`는 `$target`의 별칭.
- 원본 정책(`policy[{roles, when}]`)은 `submissionCriteria`로 변환.
- 검증 오류·경고 문구는 원본 문구를 기본으로 한다(F1 명세).

## 11. Function
```yaml
Function:
  rid, apiName: openShipmentsBySupplier, kind: query | compute | llm
  inputs:  [{ apiName, type }]          # 원시 타입, Object, ObjectSet
  output:  { type }                     # 원시 타입, Object, ObjectSet, table, struct
  body:
    query:   { objectSet: <Object set DSL> }            # 원본 behavior(SQL)의 후계 — SQL 대신 객체 질의
    compute: { expr: <§7.5 표현식> }                      # 계산 속성
    llm:     { prompt: "...", context: { objects: ... }, outputSchema: {...}, model?: ... }   # [조사] AIP Logic
  description, aiDescription, version
```
- 사용처: 계산 속성(§6), 액션 규칙·조건, 대시보드 위젯, 에이전트 도구, Object view.
- 원본 behavior(파라미터 SQL 템플릿)는 `query` Function으로 옮기되, SQL 직접 실행은 **고급 옵션**으로만(원본 0.1.1에서 직접 SQL 경로가 막혀 있던 점, 보안). [결정 대기 D-07]
- `code` 종류(사용자 코드 실행)는 v2 이후, 샌드박스 전제.

## 12. Object set
```yaml
ObjectSet:                      # 저장하면 rid를 가짐
  base: { objectType: Shipment } | { interface: Partner } | { set: rid }
  filter: "delayDays > 3 and shipStatus == 'CUSTOMS_HOLD'"
  traverse: [{ link: purchaseOrder }, { link: supplier }]     # 링크 따라가기
  search: { text?: "...", vector?: { query: "...", k: 20 } }
  setOps: { union|intersect|subtract: [ObjectSet] }
  orderBy, limit
  asOf: timestamp | null        # 시점 조회 (그래프 엔진 지원 시)
```
- 모든 소비자(화면, 대시보드, 코드 앱 SDK, 에이전트, 외부 MCP)는 Cypher/SQL 대신 Object set으로 질의한다. 코어가 저장 방식에 맞게 번역(live → 원천 SQL/가상 노드 질의, indexed/native → 그래프 Cypher). 원본처럼 각 기능이 Cypher·SQL을 직접 조립하던 구조를 대체.
- Cypher 직접 실행은 콘솔(F4)과 고급 사용자용으로 남긴다(읽기 전용 기본).

## 13. Object view
Object type마다 기본 상세 화면 구성: 헤더(제목·주요 속성), 속성 섹션, 링크된 객체 목록(링크별), 타임라인(시점 데이터·액션 이력), 실행 가능한 액션 버튼. 한 번 설정하면 검색 결과·대시보드·질의 답변의 객체 클릭에서 모두 쓴다. [조사: Core Object Views]

## 14. 수명 주기 — 작업본 · 제안 · 발행
| 단계 | 설명 | 원본 대비 |
|---|---|---|
| 작업본(draft) | 온톨로지마다 하나. 화면·에이전트 편집은 작업본에 쌓임 | 원본은 정의를 바로 저장 |
| 제안(proposal) | 작업본 ↔ 발행본 차이(diff) + 검증 결과 + **영향 분석**(이 변경으로 깨지는 대시보드·액션·앱·Function) + 골든 퀘스천/커맨드 회귀 실행 결과 | 없음 |
| 승인 | 사람이 승인(1인 사용 시 본인 승인 허용, 단 명시적 클릭). 에이전트는 제안만 만들 수 있음 | 원본은 에이전트가 「발행해 줘」로 바로 발행 |
| 발행(version n) | 컴파일(§16) 후 버전 고정. Object API·에이전트 도구·액션 카탈로그가 새 버전으로 바뀜 | 원본 발행(전체 덮어쓰기) |
| 되돌리기 | 이전 버전으로 재발행 | 없음 |
| 내보내기/가져오기 | 온톨로지 정의를 YAML 묶음으로 (Git 관리 가능) | 원본 포털의 릴리스 패키지 API(화면 없음) |
[조사] Palantir의 브랜치·Proposals·History를 단일 사용자 규모로 단순화(브랜치 = 작업본 1개).

## 15. 골든 퀘스천 · 골든 커맨드 (검증 자산)
```yaml
GoldenQuestion: { rid, text: "3일 넘게 늦은 선적은 어느 협력사의 어느 발주 건인가?",
                  expected?: { objectSet: <DSL> | answerContains: [...] }, lastResult }
GoldenCommand:  { rid, text: "그 선적을 긴급 처리해 줘", actionType: rid?, expectedPlan?: {...}, lastResult }
```
- 원본: 구축 브리프의 입력이자 에이전트 지시문의 재료. 새 모델: 여기에 더해 **회귀 테스트**(제안 단계에서 자동 실행)로 쓴다.

## 16. 발행 컴파일 (그래프 엔진으로)
| 정의 | live | indexed | native |
|---|---|---|---|
| Object type | 주 원천별 가상 타입 + 코어의 매핑·변환 계층 | 그래프 노드 라벨 `<Ontology>.<Type>`(이름공간), 동기화 작업 등록 | 그래프 노드 라벨 |
| 기본 키 | 키 표현식 | 유일 제약 | 유일 제약 |
| Link (foreign-key) | 가상 관계(변환이 있으면 코어 질의 번역) | 동기화 시 간선 생성 | 간선 |
| Link (join-source / link-object) | 코어 질의 번역 | 간선(+링크 객체 노드) | 간선 |
| Action type | 액션 카탈로그(Action 모듈) + 에이전트 도구 | 같음 | 같음 |
| Function / Object set(저장) | 코어 레지스트리 | 같음 | 같음 |
- **live 타입의 변환식 컴파일**: 매핑이 컬럼 그대로·이름 바꾸기뿐이면 가상 타입의 속성 목록으로 컴파일한다. 변환 표현식(§7.5)이 있으면 원천 쪽에 **읽기 전용 뷰**(표현식을 SQL로 번역)를 만들고 가상 타입을 그 뷰에 연결한다 → 그래프 콘솔(F4)의 Cypher도 원천 컬럼이 아니라 **매핑된 속성 이름**을 본다. 번역할 수 없는 표현식은 live를 거부한다(§7.3). (F4 질문 반영)
- 발행 레지스트리(에이전트·외부 MCP가 읽는 온톨로지 지도)도 그래프에 쓴다(원본 `_Ontology*` 노드의 후계, 이름공간·버전 포함).
- 발행은 **원자적**: 컴파일 단계 하나라도 실패하면 이전 버전 유지(원본은 라벨 규칙 위반 시 전체 중단 — 같은 원칙).

## 17. 검증 규칙 (작업본 저장·제안 시)
1. 이름 규칙(§3), 이름공간 내 유일
2. 기본 키 존재, 키 속성 required
3. 백킹: 주 원천 정확히 1개(live/indexed), 키 표현식 타입 = 키 속성 타입, 매핑 대상 속성 존재, 원천 컬럼 존재(카탈로그 확인)
4. live 제약(§7.3), 표현식 번역 가능성
5. Link: 양끝 타입 존재, 조인 표현식 타입 일치, 카디널리티와 키 유일성 모순 없음
6. Interface: 구현 타입이 모든 공유 속성을 매핑
7. Action: 원본 액션 검증 전부(이름·시스템·operation·표현식 뿌리·단계 참조·정책 키) + 편집 규칙 대상 속성이 `editable`, 객체 참조 파라미터 타입 존재
8. Function: 입출력 타입, 순환 참조 없음(계산 속성 ↔ Function)
9. 영향 분석: 삭제·이름 변경 시 의존 대상 목록, 깨지는 의존이 있으면 경고(발행은 사용자 확인 후)

## 18. 원본 개념 → 새 모델 이행표
| 원본 | 새 모델 |
|---|---|
| 스키마 그룹 (intent, golden_questions, golden_commands) | Ontology (+ GoldenQuestion/Command 객체화) |
| 클래스 `binding_kind: virtual` + 바인딩(테이블, key_columns, column_map, base_conditions, label_property) | Object type `storage: live` + BackingSource(primary, table) — key → key, column_map → mappings, base_conditions → filter, label_property → titleKey |
| 클래스 `materialized` (문서 구축) | Object type `storage: native` (+ BackingSource document) |
| 가상 노드 (`CREATE VIRTUAL NODE`) | live Object type 컴파일 결과(내부) |
| 관계 유형 / 가상 관계 | Link type (foreign-key / stored) |
| behavior (SQL 템플릿) | Function `query` (Object set) — SQL은 고급 옵션 |
| 액션 (steps, arg_mapping, policy, confirm_threshold, max_targets, compensate, writeback_property) | Action type (rules.callSystem, submissionCriteria, approval, target.maxTargets, compensate, writeback) |
| 발행 레지스트리 `_Ontology*` | 발행 레지스트리(이름공간·버전) |
| 인스턴스 `:_Entity:<클래스>` | 객체 라벨 `<Ontology>.<Type>` |
| 출처 기록(provenance) | 정의마다 `provenance`(전략·근거) 유지 + 객체 수준 원천 표시 |
| 인과 가설 | Link type 후보(제안) — v2 |

## 19. 이 문서의 결정 대기
D-02 그래프 엔진, D-05 live 다원천 허용 범위, D-06 편집 레이어 충돌 기본값, D-07 SQL Function 허용, D-08 브랜치(작업본 1개 vs 여러 개) — `90-open-decisions.md`.

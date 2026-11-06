# 온톨로지란 무엇인가

*분류: 온톨로지 개념 · 3장 · 원문: <https://www.uengine.org/docs/ontological-studio/ontology-basics.html>*

> 클래스·속성·관계·인스턴스라는 네 가지 핵심 개념을 살펴보고, 테이블로 데이터를 다루는 방식과 온톨로지를 예제로 비교합니다.

[▶ 영상: 온톨로지란 무엇인가 — 영상 3:56](https://www.youtube.com/watch?v=3Zcwo-X5TrI)

## 한 문장으로

**온톨로지는 업무에 필요한 개념과 그 개념 사이의 관계를 정의한 모델입니다.**

ER 다이어그램처럼 업무의 대상과 관계를 표현합니다. 여기에 실제 데이터를 연결해 **질의와 업무 실행의 기준**으로 활용할 수 있습니다.

## 네 가지 핵심 개념

| 개념 | 설명 | 예시 |
| --- | --- | --- |
| **클래스** (class, 노드 타입·라벨) | 업무에 등장하는 것의 종류 | `Supplier`(협력사), `PurchaseOrder`(발주), `Shipment`(선적) |
| **속성** (property) | 클래스가 가진 값 | `Supplier.name`, `Shipment.delay_days` |
| **관계** (relationship) | 두 클래스 사이의 연결, 방향과 이름이 있음 | `(PurchaseOrder)-[:ORDERED_FROM]->(Supplier)` — 발주는 협력사에게 낸다 |
| **인스턴스** (instance, 노드) | 클래스에 속한 개별 데이터 | 협력사 `S-CN-01 Shenzhen Goldline PCB`, 발주 `PO-002` |

클래스와 관계가 **스키마**, 인스턴스와 그 연결이 **데이터**입니다. 그래프 데이터베이스에서는 인스턴스를 **노드**, 연결을 **엣지(관계)**라고 부릅니다.

## 예제 온톨로지 한눈에 보기

![예제 온톨로지 「공급망 운영 (예제)」의 스키마 — 클래스 7개와 그 사이의 관계](images/build-source.webp)

*예제 온톨로지 「공급망 운영 (예제)」의 스키마 — 클래스 7개와 그 사이의 관계*

| 클래스 | 설명 | 원천 시스템 |
| --- | --- | --- |
| `Supplier` | 협력사 (5곳) | ERP |
| `Item` | 품목 (4개) | ERP |
| `PurchaseOrder` | 구매 발주 (8건) | ERP |
| `Shipment` | 입고 선적 (8건) | WMS |
| `Customer` | 고객 (3곳) | CRM |
| `SalesOrder` | 판매 주문 (5건) | CRM |
| `Claim` | 고객 클레임 (3건) | CRM |

| 관계 | 읽는 법 |
| --- | --- |
| `(Shipment)-[:SHIPS]->(PurchaseOrder)` | 선적은 발주를 싣고 온다 |
| `(PurchaseOrder)-[:ORDERED_FROM]->(Supplier)` | 발주는 협력사에게 냈다 |
| `(SalesOrder)-[:PLACED_BY]->(Customer)` | 판매 주문은 고객이 냈다 |
| `(SalesOrder)-[:FOR_ITEM]->(Item)` | 판매 주문은 품목에 대한 것이다 |
| `(Claim)-[:ABOUT]->(SalesOrder)` | 클레임은 판매 주문에 대한 것이다 |
| `(Shipment)-[:SHIPPED_BY]->(Supplier)` | 선적은 협력사가 보냈다 (구축된 온톨로지에만 있습니다 — [4장](04-architecture.md) 참고) |

## 테이블과 무엇이 다른가

같은 질문을 SQL과 그래프로 비교해 봅시다. **“3일 넘게 늦은 선적은 어느 협력사의 어느 발주 건인가?”**

SQL로는 세 테이블을 조인합니다. 게다가 선적은 WMS에, 발주와 협력사는 ERP에 있으니, 원래는 두 DB를 하나로 모으는 작업부터 해야 합니다.

```
SELECT sh.shipment_no, po.po_id, s.name
FROM wms.shipment sh
JOIN erp.purchase_order po ON po.po_id = sh.ref_po_no
JOIN erp.supplier s       ON s.supplier_id = po.supplier_id
WHERE sh.delay_days > 3;
```

Cypher(그래프 질의 언어)로는 **관계 이름을 사용해 연결된 데이터를 조회합니다.**

```cypher
MATCH (sh:Shipment)-[:SHIPS]->(po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)
WHERE sh.delay_days > 3
RETURN sh.shipment_no, po.po_id, s.name
```

조인 조건(`po.po_id = sh.ref_po_no`)이 사라지고 `SHIPS`, `ORDERED_FROM`이라는 **업무에서 사용하는 관계 이름**이 남았습니다. 조인 키를 아는 일은 관계를 정의할 때 한 번만 하면 되고, 그다음부터는 사람도 AI 에이전트도 관계 이름만 알면 됩니다.

> **[참고] 온톨로지의 가치는 ‘다음 질문’에 있습니다**
>
> 질문마다 SQL 뷰를 만들면 질문 수만큼 유지보수할 것이 늘어납니다. 엔티티와 관계로 모델링해 두면, 처음 받는 질문도 **이미 있는 관계를 따라** 답할 수 있습니다. “그 협력사의 다른 미결 발주는?”, “그 발주의 품목을 산 고객 중 클레임을 낸 곳은?” 같은 질문에도 새로 설계하지 않고 답할 수 있습니다.

## 왜 AI 에이전트에게 온톨로지가 필요한가

LLM 에이전트에게 테이블 수백 개의 DDL을 주면, `TB507.C041` 같은 코드명이 무엇인지, 어느 컬럼으로 조인해야 하는지를 매번 추측해야 합니다. 온톨로지는 그 추측을 **한 번, 사람이 검수한 형태로** 고정해 둡니다.

1. **의미** — `Shipment.delay_days`는 “도착 예정일보다 늦어진 일수”라는 설명과 함께 있습니다.
2. **경로** — 선적에서 협력사로 가는 길이 관계로 정해져 있습니다.
3. **행위** — 선적에 할 수 있는 일(“긴급 처리”)과 그 일을 되돌리는 방법이 **액션**으로 붙어 있습니다(6부).

그래서 Ontological Studio에서는 같은 온톨로지가 **질의의 기준, 실행의 기준, 앱의 기준**이 됩니다.

> **[확인 문제]**
>
> 1. 예제에서 `Claim`과 `Customer`를 연결하려면 어떤 관계를 어떤 방향으로 거쳐야 하나요?
> 2. “PCB 기판을 산 고객”을 찾으려면 어떤 클래스들을 지나야 하나요?
> 3. 다음 중 클래스, 속성, 관계, 인스턴스는 각각 무엇인가요? — `Item`, `PO-005`, `FOR_ITEM`, `safety_stock`

> **▼ 정답 보기**
>
> 1. `(Claim)-[:ABOUT]->(SalesOrder)-[:PLACED_BY]->(Customer)` — ABOUT을 따라 판매 주문으로, PLACED\_BY를 따라 고객으로 갑니다.
> 2. `Item` ← `FOR_ITEM` — `SalesOrder` — `PLACED_BY` → `Customer`
> 3. `Item` 클래스, `PO-005` 인스턴스(발주 하나), `FOR_ITEM` 관계, `safety_stock` 속성(품목의 안전재고)

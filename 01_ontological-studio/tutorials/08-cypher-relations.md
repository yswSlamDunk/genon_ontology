# 관계 따라가기와 집계

*분류: Cypher 익히기 · 8장 · 원문: <https://www.uengine.org/docs/ontological-studio/cypher-relations.html>*

> 관계 패턴을 따라 노드를 조회하고, 여러 데이터베이스를 하나의 질의로 연결해 count·sum·collect로 집계합니다. Cypher가 SQL보다 편해지는 지점입니다.

[▶ 영상: 관계 따라가기와 집계 — 영상 3:53](https://www.youtube.com/watch?v=iPnPTb-6QA0)

## 관계 패턴

```cypher
MATCH (po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)
RETURN po.po_id, po.status, s.name
```

| po.po\_id | po.status | s.name |
| --- | --- | --- |
| PO-001 | OPEN | Shenzhen Goldline PCB |
| PO-002 | OPEN | Shenzhen Goldline PCB |
| PO-003 | CLOSED | 한빛정밀 |
| PO-004 | CLOSED | 대성케이블 |
| PO-005 | OPEN | Ningbo Magnetics |
| PO-006 | OPEN | Hanoi Assembly |
| PO-007 | OPEN | Ningbo Magnetics |
| PO-008 | OPEN | 한빛정밀 |

발주는 ERP의 `purchase_order`, 협력사는 ERP의 `supplier`입니다. 관계 `ORDERED_FROM`이 `purchase_order.supplier_id = supplier.supplier_id` 조인을 대신했습니다.

### 방향

| 패턴 | 뜻 |
| --- | --- |
| `(a)-[:R]->(b)` | a에서 b로 |
| `(a)<-[:R]-(b)` | b에서 a로 — 같은 관계를 반대편에서 읽기 |
| `(a)-[:R]-(b)` | 방향 상관없이 |

관계에는 정의된 방향이 있습니다(`PurchaseOrder → Supplier`). 협력사에서 출발하고 싶으면 화살표를 반대로 씁니다.

```cypher
MATCH (s:Supplier)<-[:ORDERED_FROM]-(po:PurchaseOrder)
RETURN s.name, collect(po.po_id) AS orders
```

| s.name | orders |
| --- | --- |
| 대성케이블 | ["PO-004"] |
| Shenzhen Goldline PCB | ["PO-001", "PO-002"] |
| 한빛정밀 | ["PO-003", "PO-008"] |
| Ningbo Magnetics | ["PO-005", "PO-007"] |
| Hanoi Assembly | ["PO-006"] |

> **[주의] 노드마다 라벨을 붙이세요**
>
> Ontological DB에서는 패턴의 **노드마다 라벨**을 적어야 빠르고 정확합니다. `(s:Supplier)<-[:ORDERED_FROM]-(po)`보다 `(po:PurchaseOrder)`처럼 쓰세요. 특히 데이터 패브릭의 가상 관계는 라벨 없이 `-[r]->`(관계 이름도 없이)로 찾으면 결과가 비어 나옵니다. 관계 이름과 양쪽 라벨을 모두 적는 습관을 들이세요.

## 여러 걸음 — 다른 데이터베이스를 건너서

[2장](03-ontology-basics.md)에서 본 질문입니다. 선적(WMS) → 발주(ERP) → 협력사(ERP).

```cypher
MATCH (sh:Shipment)-[:SHIPS]->(po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)
WHERE sh.delay_days > 0
RETURN sh.shipment_no, sh.ship_status, sh.delay_days, po.po_id, s.name
ORDER BY sh.delay_days DESC
```

| sh.shipment\_no | sh.ship\_status | sh.delay\_days | po.po\_id | s.name |
| --- | --- | --- | --- | --- |
| SHP-03 | CUSTOMS\_HOLD | 9 | PO-002 | Shenzhen Goldline PCB |
| SHP-02 | IN\_TRANSIT | 7 | PO-001 | Shenzhen Goldline PCB |
| SHP-06 | IN\_TRANSIT | 3 | PO-005 | Ningbo Magnetics |
| SHP-05 | DELIVERED | 1 | PO-004 | 대성케이블 |

노드 전체를 반환하면 그래프로 볼 수 있습니다. 관계에도 변수(`r`, `o`)를 붙여 함께 반환합니다.

```cypher
MATCH (sh:Shipment)-[r:SHIPS]->(po:PurchaseOrder)-[o:ORDERED_FROM]->(s:Supplier)
WHERE sh.delay_days > 3
RETURN sh, r, po, o, s
```

![결과 카드의 Graph 보기 — 늦은 선적 두 건이 각자의 발주를 거쳐 같은 협력사로 모입니다](images/portal-graph.webp)

*결과 카드의 Graph 보기 — 늦은 선적 두 건이 각자의 발주를 거쳐 같은 협력사로 모입니다*

선적 두 건이 서로 다른 발주를 거쳐 **같은 협력사로 연결되는** 모습을 볼 수 있습니다. 테이블에서는 알아보기 어려웠던 사실입니다. 지연된 선적이 한 협력사에 집중되어 있습니다.

### 고객 쪽으로

CRM 안에서 클레임 → 판매 주문 → 고객:

```cypher
MATCH (c:Claim)-[:ABOUT]->(so:SalesOrder)-[:PLACED_BY]->(cu:Customer)
RETURN c.ticket_no, c.severity, c.subject, so.so_no, cu.name
```

| c.ticket\_no | c.severity | c.subject | so.so\_no | cu.name |
| --- | --- | --- | --- | --- |
| T-1 | HIGH | 컨트롤러 전원 불량 | SO-01 | 서울전자 |
| T-2 | LOW | 케이블 포장 파손 | SO-04 | Berlin Motion |
| T-3 | HIGH | PCB 납땜 불량 | SO-05 | Tokyo Devices |

### 갈래가 둘인 패턴

쉼표로 여러 패턴을 적고 **같은 변수**를 사용하면 패턴을 연결할 수 있습니다. “납땜 불량 클레임이 난 품목을 공급한 협력사는?”이라는 질문에 답하려면 CRM의 클레임에서 품목을 찾고, 그 품목을 ERP의 발주 품목과 협력사에 연결합니다. ([6장](06-virtual-graph.md)에서 만든 `PoLine`이 필요합니다.)

```cypher
MATCH (i:Item)<-[:FOR_ITEM]-(so:SalesOrder)<-[:ABOUT]-(c:Claim),
      (i:Item)<-[:OF_ITEM]-(l:PoLine)-[:IN_ORDER]->(po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)
WHERE c.subject CONTAINS '납땜'
RETURN DISTINCT i.name, s.name
```

| i.name | s.name |
| --- | --- |
| PCB 기판 | Hanoi Assembly |
| PCB 기판 | Shenzhen Goldline PCB |

두 데이터베이스(CRM·ERP)에 걸친 다섯 종류의 노드를 하나의 질의로 조회했습니다.

## 없는 짝도 남기기 — OPTIONAL MATCH

SQL의 `LEFT JOIN`에 해당합니다. 연결된 데이터가 없어도 행을 유지하며, 데이터가 없는 쪽은 `null`이 됩니다.

```cypher
MATCH (sh:Shipment)
OPTIONAL MATCH (sh:Shipment)-[:SHIPS]->(po:PurchaseOrder)
RETURN sh.shipment_no, po.po_id
ORDER BY sh.shipment_no
```

8건 중 `SHP-08`만 `po.po_id`가 `null`입니다. 이 선적은 ERP에 없는 발주 `PO-999`를 가리키고 있습니다 — 일부러 넣어 둔 **데이터 품질 문제**입니다. 연결된 데이터가 없는 항목만 고르려면:

```cypher
MATCH (sh:Shipment)
OPTIONAL MATCH (sh:Shipment)-[:SHIPS]->(po:PurchaseOrder)
WITH sh, po WHERE po IS NULL
RETURN sh.shipment_no, sh.ref_po_no
```

조회 결과는 `SHP-08`, `PO-999`입니다.

> **[참고] NOT EXISTS 대신**
>
> Neo4j의 `WHERE NOT EXISTS { MATCH … }` 하위 질의는 아직 지원하지 않습니다. 위처럼 `OPTIONAL MATCH` + `IS NULL`로 씁니다.

## 묶어서 세기 — 집계

`RETURN`에 집계 함수와 보통 값이 함께 있으면, **일반 컬럼의 값이 같은 행이 한 그룹**이 됩니다(SQL의 `GROUP BY`를 따로 쓰지 않습니다).

```cypher
MATCH (po:PurchaseOrder)
RETURN po.status, count(*) AS n, sum(po.amount_usd) AS total,
       avg(po.amount_usd) AS average, max(po.amount_usd) AS biggest
```

| po.status | n | total | average | biggest |
| --- | --- | --- | --- | --- |
| CLOSED | 2 | 24000 | 12000 | 15000 |
| OPEN | 6 | 255000 | 42500 | 82000 |

협력사별 미결 발주 금액:

```cypher
MATCH (po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)
WHERE po.status = 'OPEN'
RETURN s.name AS supplier, count(po) AS open_orders, sum(po.amount_usd) AS open_amount
ORDER BY open_amount DESC
```

| supplier | open\_orders | open\_amount |
| --- | --- | --- |
| Shenzhen Goldline PCB | 2 | 123000 |
| Ningbo Magnetics | 2 | 72000 |
| Hanoi Assembly | 1 | 33000 |
| 한빛정밀 | 1 | 27000 |

협력사별 최장 지연 일수:

```cypher
MATCH (s:Supplier)<-[:ORDERED_FROM]-(po:PurchaseOrder)<-[:SHIPS]-(sh:Shipment)
RETURN s.name, max(sh.delay_days) AS worst
ORDER BY worst DESC
```

Shenzhen Goldline PCB 9일, Ningbo Magnetics 3일, 대성케이블 1일, 나머지 0일.

## 단계를 나누기 — WITH

`WITH`는 질의를 두 단계로 나눕니다. 앞 단계의 결과를 다음 단계가 이어받습니다. 집계한 값으로 다시 거를 때(SQL의 `HAVING`) 씁니다.

```cypher
MATCH (po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)
WITH s, count(po) AS n
WHERE n >= 2
RETURN s.name, n
```

발주가 두 건 이상인 협력사 — Ningbo Magnetics, Shenzhen Goldline PCB, 한빛정밀(각 2건).

`collect()`로 모은 목록의 길이는 `size()`로 확인합니다.

```cypher
MATCH (po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)
WITH s, collect(po.po_id) AS pos
RETURN s.name, size(pos) AS n, pos
ORDER BY n DESC
```

> **[주의] 알려진 제약 — 금액 합계로 거르기**
>
> `WITH s, sum(po.amount_usd) AS total WHERE total > 50000`처럼 **소수 타입 컬럼의 합계로 다시 거르면** 현재 버전에서는 `invalid input syntax for type bigint` 오류가 납니다. `sum(toFloat(po.amount_usd))`로 실수로 바꿔 더하면 됩니다.
>
> ```cypher
> MATCH (po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)
> WITH s, sum(toFloat(po.amount_usd)) AS total
> WHERE total > 50000
> RETURN s.name, total ORDER BY total DESC
> ```

## 목록에서 시작하기 — UNWIND

목록을 행으로 펼칩니다. 여러 키를 한 번에 조회할 때 편합니다.

```cypher
UNWIND ['SHP-02', 'SHP-03'] AS no
MATCH (sh:Shipment {shipment_no: no})
RETURN sh.shipment_no, sh.eta
```

> **[확인 문제]**
>
> 1. 미결(`OPEN`) 판매 주문을 고객별로 모아, 고객 이름과 주문 번호 목록을 보여 주세요.
> 2. 선적이 두 건 이상인 발주는 무엇인가요?
> 3. 심각도 `HIGH` 클레임을 낸 고객과 그 판매 주문을 찾으세요.
> 4. (도전) 협력사마다 미결 발주가 몇 건인지, **미결 발주가 없는 협력사도 0으로** 나오게 쓰세요.

> **▼ 정답 보기**
>
> ```cypher
> MATCH (cu:Customer)<-[:PLACED_BY]-(so:SalesOrder)
> WHERE so.status = 'OPEN'
> RETURN cu.name, collect(so.so_no) AS open_orders
> ```
>
> Tokyo Devices `["SO-03", "SO-05"]`, 서울전자 `["SO-02"]`.
>
> ```cypher
> MATCH (po:PurchaseOrder)<-[:SHIPS]-(sh:Shipment)
> WITH po, count(sh) AS shipments WHERE shipments >= 2
> RETURN po.po_id, shipments
> ```
>
> PO-001 (SHP-01, SHP-02).
>
> ```cypher
> MATCH (cu:Customer)<-[:PLACED_BY]-(so:SalesOrder)<-[:ABOUT]-(c:Claim)
> WHERE c.severity = 'HIGH'
> RETURN cu.name, so.so_no, c.subject
> ```
>
> 서울전자 SO-01 「컨트롤러 전원 불량」, Tokyo Devices SO-05 「PCB 납땜 불량」.
>
> ```cypher
> MATCH (s:Supplier)
> OPTIONAL MATCH (s:Supplier)<-[:ORDERED_FROM]-(po:PurchaseOrder)
> WHERE po.status = 'OPEN'
> RETURN s.name, count(po) AS open_n ORDER BY open_n DESC
> ```
>
> 대성케이블이 0으로 나옵니다. `count(po)`는 `null`을 세지 않기 때문입니다(`count(*)`였다면 1이 됩니다).

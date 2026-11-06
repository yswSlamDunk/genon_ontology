# Cypher 심화 — 실행 들여다보기, 말로 묻기, 직접 쓰기

*분류: Cypher 익히기 · 9장 · 원문: <https://www.uengine.org/docs/ontological-studio/cypher-advanced.html>*

> 질의가 실제로 어떻게 실행되는지(SQL 변환과 패브릭 실행 계획)를 살펴보고, 자연어로 Cypher를 만들고, 내 그래프를 만들어 노드와 관계를 직접 써 봅니다.

[▶ 영상: Cypher 심화 — 실행 들여다보기, 말로 묻기, 직접 쓰기 — 영상 3:59](https://www.youtube.com/watch?v=6KcsUciRcq0)

## 번역된 SQL 보기

Ontological DB는 Cypher를 PostgreSQL SQL로 **변환**해 실행합니다. 결과 카드의 **SQL** 탭에서 변환 결과를 볼 수 있습니다.

```cypher
MATCH (po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)
WHERE po.status = 'OPEN'
RETURN s.name AS supplier, count(po) AS open_orders, sum(po.amount_usd) AS open_amount
ORDER BY open_amount DESC
```

![SQL 탭 — Cypher 한 문장이 PostgreSQL 질의로 번역된 모습](images/portal-sql.webp)

*SQL 탭 — Cypher 한 문장이 PostgreSQL 질의로 번역된 모습*

결과 카드 아래의 `compiled SQL 668a5ee48536` 같은 값은 변환된 SQL을 식별하는 값입니다. 같은 Cypher면 시점(10장)을 바꿔도 지문이 같습니다 — 질의는 그대로이고 조건만 바뀐다는 뜻입니다.

## 패브릭 실행 계획 — EXPLAIN FABRIC

원천이 여러 DB에 걸친 질의는 **어느 시스템에서 어떤 작업을 실행하는지**가 성능을 좌우합니다. 질의 앞에 `EXPLAIN FABRIC`을 붙이면 단계별 계획을 보여 줍니다.

```cypher
EXPLAIN FABRIC
MATCH (sh:Shipment)-[:SHIPS]->(po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)
WHERE sh.delay_days > 3
RETURN sh.shipment_no, s.name
```

| step | place | operation | rows | detail |
| --- | --- | --- | --- | --- |
| 1 | remote:erp | join | 8 | `SELECT r10.po_id, r12.name FROM (erp.purchase_order r10 INNER JOIN erp.supplier r12 ON …)` |
| 2 | remote:wms | scan | 2 | `SELECT shipment_no, ref_po_no FROM wms.shipment WHERE ((delay_days > 3))` |
| 3 | local | Hash Join | 2 | `(purchase_order.po_id = (shipment.ref_po_no)::text)` |

![EXPLAIN FABRIC — 원천마다 내려 보낸 SQL과 넘어온 행 수](images/portal-explain.webp)

*EXPLAIN FABRIC — 원천마다 내려 보낸 SQL과 넘어온 행 수*

읽는 법:

1. **ERP 안의 조인은 ERP에서** 했습니다(발주 ⋈ 협력사). 같은 DB 안의 일은 원천에 맡깁니다.
2. **WMS에는 조건을 붙여** 보냈습니다(`delay_days > 3`). 8행 전부가 아니라 2행만 넘어왔습니다.
3. 서로 다른 DB를 잇는 마지막 조인만 Ontological DB가 했습니다.

원천 데이터가 많을수록 이 차이가 커집니다. 조건이 원천으로 내려가지 않는 질의(예: 두 DB의 값을 서로 비교하는 조건)는 계획에서 `local`로 보입니다. 그런 질의는 원천에서 많은 행을 가져올 수 있으므로 조건을 조정해 보는 것이 좋습니다.

## 말로 묻기 — 자연어 → Cypher

입력칸에 Cypher 대신 **한국어 문장**을 쓰고 실행하면, 에이전트가 이 그래프의 스키마를 읽고 Cypher를 만들어 줍니다(첫 단어가 Cypher 키워드가 아니면 자연어로 인식합니다. ✨ 버튼이나 ⇧⌘Enter로도 됩니다).

```
3일 넘게 늦어진 입고 선적은 어느 협력사의 어느 발주 건이야?
```

![자연어 질의 — 에이전트가 만든 Cypher와 설명, 그래프에서 미리 실행해 확인했다는 표시](images/portal-nl.webp)

*자연어 질의 — 에이전트가 만든 Cypher와 설명, 그래프에서 미리 실행해 확인했다는 표시*

에이전트가 만든 Cypher는 화면에 그대로 보이고, 실행하기 전에 그래프에서 **먼저 시험 실행**해 봅니다. 실패하면 엔진의 오류 메시지를 참고해 한 번 수정합니다. 쓰기 문장(`CREATE`, `SET` 등)은 실행하지 않고 입력칸에만 둡니다. 이 예에서는 Claude Code가 8.7초 만에 다음을 만들었습니다.

```cypher
MATCH (sh:Shipment)-[:SHIPS]->(po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)
WHERE sh.delay_days > 3
RETURN s.name AS supplier, po.po_id AS po_id, sh.shipment_no AS shipment_no,
       sh.delay_days AS delay_days, sh.ship_status AS ship_status
ORDER BY sh.delay_days DESC LIMIT 100
```

> **[팁] 자연어 질의를 활용해 보세요**
>
> 만들어진 Cypher를 읽고 고쳐 쓰는 연습을 하세요. 에이전트가 어떤 관계를 골랐는지 보면 스키마를 이해하는 데도 도움이 됩니다. 이 기능은 앱 안의 포털에서만 동작합니다(코딩 에이전트가 필요합니다).

## 직접 쓰기 — 내 그래프 만들기

가상 노드는 읽기 전용이지만, Ontological DB에 **저장되는 노드**는 Cypher로 직접 생성하고 수정할 수 있습니다. 예제를 건드리지 않도록 연습용 그래프를 만듭시다. 그래프 선택과 상관없이 실행됩니다.

```cypher
CREATE GRAPH tut
```

이제 그래프 선택에서 `tut`을 고르고(목록에 안 보이면 포털을 새로 고침), 노드를 만듭니다.

```cypher
CREATE (:Employee {emp_no: 'E1', name: '김하늘', dept: '구매', salary: 4200})
```

```cypher
CREATE (:Employee {emp_no: 'E2', name: '박바다', dept: '물류', salary: 3900})
```

관계를 만들려면, 먼저 양쪽 노드를 `MATCH`로 찾은 뒤 `CREATE`합니다. 관계에도 속성을 붙일 수 있습니다.

```cypher
MATCH (a:Employee {emp_no: 'E1'}), (b:Employee {emp_no: 'E2'})
CREATE (a)-[:MENTORS {since: '2025-03'}]->(b)
```

```cypher
MATCH (a:Employee)-[m:MENTORS]->(b:Employee)
RETURN a.name, m.since, b.name
```

결과: `김하늘 · 2025-03 · 박바다`.

### 고치기·지우기

| 하고 싶은 일 | 문장 |
| --- | --- |
| 값 바꾸기 | `MATCH (e:Employee {emp_no:'E1'}) SET e.salary = 4500 RETURN e.salary` |
| 없으면 만들기 | `MERGE (d:Dept {name:'구매'}) RETURN d.name` |
| 없으면 관계 만들기 | `MATCH (e:Employee), (d:Dept {name:'구매'}) WHERE e.dept = d.name MERGE (e)-[:WORKS_IN]->(d)` |
| 노드와 그 관계 지우기 | `MATCH (e:Employee {emp_no:'E2'}) DETACH DELETE e` |

`MERGE`는 같은 모양이 이미 있으면 그것을 쓰고, 없으면 만듭니다. 두 번 실행해도 `Dept` 노드가 하나만 생깁니다. `DETACH DELETE`는 노드에 붙은 관계까지 함께 지웁니다(관계가 남아 있으면 `DELETE`만으로는 삭제할 수 없습니다).

> **[참고] 온톨로지 그래프는 Studio에게**
>
> `ontology` 그래프는 Studio가 관리합니다. 클래스 정의(`_OntologyClass` 같은 노드)와 액션 정의가 함께 들어 있으므로, 포털에서 직접 고치지 말고 「온톨로지 구축」 화면과 에이전트로 다루세요. 직접 쓰기 연습은 이렇게 따로 만든 그래프에서 합니다.

## 저장과 기록

- 결과 카드의 ★는 질의를 **저장**합니다. 왼쪽 레일의 책갈피 아이콘에서 다시 꺼냅니다.
- 입력칸에서 ↑↓로 **이전 질의**를 불러옵니다. 시계 아이콘 목록에는 이 그래프에서 최근에 수행한 쓰기 작업(감사 기록)가 보입니다.

## Ontological DB의 Cypher — 알아 둘 차이

Neo4j의 Cypher를 이미 안다면 다음 차이만 기억하세요.

| 항목 | Ontological DB 0.1 |
| --- | --- |
| 라벨 | 패턴의 노드마다 라벨을 적는 것이 원칙. `WHERE n:Label` 형태의 라벨 조건은 쓰지 않습니다. |
| 하위 질의 | `EXISTS { … }`, `CALL { … }`는 아직 없습니다 → `OPTIONAL MATCH … IS NULL` |
| 가변 길이 경로 | `-[:R*1..3]->`는 저장된 관계에서만 됩니다. 가상 관계에는 아직 안 됩니다. |
| 날짜 | `date()` 함수가 없습니다 → 날짜 컬럼과 `'YYYY-MM-DD'` 문자열을 바로 비교 |
| 함수 | [7장의 목록](07-cypher-basics.md#값-바꿔-보여-주기-함수와-case)만. 없는 함수를 쓰면 오류가 지원 목록을 알려 줍니다. |
| 가상 노드 | 읽기 전용 — 값은 원천 시스템(또는 액션)으로 바꿉니다 |
| 더 있는 것 | `SHOW …` 패브릭 문장, `EXPLAIN FABRIC`, 시간 여행(10장), 상위 라벨로 하위 타입까지 찾기 |

> **[확인 문제]**
>
> 1. `EXPLAIN FABRIC`으로 “클레임 → 판매 주문 → 고객” 질의(8장)의 계획을 보세요. 이 질의는 몇 개의 원천에 접근하나요?
> 2. `tut` 그래프에 `Dept {name:'물류'}`를 `MERGE`로 두 번 만들고, `MATCH (d:Dept) RETURN d.name, count(*)`로 몇 개인지 확인하세요.
> 3. 자연어로 “납땜 불량 클레임을 낸 고객은 누구야?”라고 물어보고, 에이전트가 만든 Cypher가 8장의 답과 같은 결과를 내는지 비교하세요.

> **▼ 정답 보기**
>
> 1. 세 노드가 모두 CRM에 있으므로 원천 한 곳(`remote:crm`)에서 조인까지 끝납니다. 같은 DB 안의 일은 원천에 맡기는 것을 확인할 수 있습니다.
> 2. `MERGE`는 이미 있으면 새로 만들지 않으므로 `물류` 행의 개수는 1입니다(앞에서 만든 `구매`도 1).
> 3. Tokyo Devices(SO-05, T-3 「PCB 납땜 불량」)가 나와야 합니다. 에이전트의 질의는 매번 조금씩 다를 수 있지만 결과는 같아야 합니다.

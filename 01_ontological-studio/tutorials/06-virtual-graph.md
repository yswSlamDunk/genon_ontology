# 가상 노드와 가상 관계

*분류: 데이터 연결 · 6장 · 원문: <https://www.uengine.org/docs/ontological-studio/virtual-graph.html>*

> 아직 노출되지 않은 테이블 `erp.po_line`(발주 품목)을 가상 노드로 만들고, 발주·품목과 관계로 이어 봅니다. 서로 다른 데이터베이스의 테이블을 하나의 그래프로 연결하는 과정을 실습합니다.

[▶ 영상: 가상 노드와 가상 관계 — 영상 3:50](https://www.youtube.com/watch?v=f3ASzYcuBPE)

## 가상 노드란

**가상 노드 타입**은 원천 테이블 하나를 그래프의 노드 타입으로 정의한 것입니다.

- 원천 **행 하나 = 노드 하나**, **컬럼 = 속성**입니다.
- **KEY 컬럼**이 노드를 구별하는 값입니다(보통 기본키).
- 데이터는 복사되지 않습니다. `MATCH (n:PoLine)`을 실행할 때마다 원천 `erp.po_line`을 읽습니다.
- **읽기 전용**입니다. 가상 노드에 `CREATE`나 `SET`을 하면 엔진이 거절합니다. 값을 바꾸려면 원천 시스템에서 바꿔야 하고, Ontological Studio에서는 그 일을 **액션**이 합니다(6부).

## 따라 하기 — 발주 품목을 노드로

1. 데이터소스 탭에서 `erp`를 고르고, 테이블 목록에서 `po_line`을 누릅니다. 아직 「노출 안 됨」입니다.
2. 오른쪽 아래 **가상 노드로 노출** 상자에서 노드 타입 이름을 `PoLine`, 그래프를 `sample`, KEY 컬럼을 `po_line_id`로 둡니다.
3. 속성은 그대로 두면 모든 컬럼이 같은 이름의 속성이 됩니다. 이름을 바꾸고 싶으면 오른쪽 칸을 고칩니다(예: `qty` → `quantity`).
4. 「실행될 문장」을 확인하고 「가상 노드 만들기」를 누릅니다.

![가상 노드로 노출 — 노드 타입 이름·그래프·KEY 컬럼·속성을 고르면 아래에 실행될 문장이 미리 보입니다](images/ds-form.webp)

*가상 노드로 노출 — 노드 타입 이름·그래프·KEY 컬럼·속성을 고르면 아래에 실행될 문장이 미리 보입니다*

실행되는 문장은 이것입니다.

```cypher
CREATE VIRTUAL NODE PoLine IN sample FROM erp.po_line KEY po_line_id
```

속성 이름을 바꾸면 `PROPERTIES (po_line_id, po_id, item_id, qty AS quantity)`처럼 붙습니다. 만들자마자 미리보기에 원천의 9행이 나옵니다.

![가상 노드 :PoLine이 만들어지고, 원천 erp.po_line의 9행이 미리보기에 나왔습니다](images/ds-created.webp)

*가상 노드 :PoLine이 만들어지고, 원천 erp.po\_line의 9행이 미리보기에 나왔습니다*

## 가상 그래프 보기

왼쪽 아래 가상 그래프에서 `sample`을 누르면, 데이터소스별로 묶인 노드와 관계를 그래프로 볼 수 있습니다. `PoLine`은 아직 다른 노드와 연결되어 있지 않습니다.

![가상 그래프 sample — 데이터소스별 가상 노드와 가상 관계](images/vgraph.webp)

*가상 그래프 sample — 데이터소스별 가상 노드와 가상 관계*

## 따라 하기 — 관계로 잇기

발주 품목은 특정 발주에 포함된 특정 품목을 뜻합니다. 이 두 연결을 관계로 정의합니다.

1. 가상 그래프 화면 아래 관계 만들기 칸에 관계 이름 `IN_ORDER`를 적습니다.
2. 출발 노드 `PoLine`, 속성 `po_id` → 도착 노드 `PurchaseOrder`, 속성 `po_id`를 고릅니다.
3. 「관계 만들기」를 누릅니다.

![가상 관계 만들기 — 출발 노드의 속성과 도착 노드의 속성이 같은 값이면 관계로 이어집니다](images/vrel-form.webp)

*가상 관계 만들기 — 출발 노드의 속성과 도착 노드의 속성이 같은 값이면 관계로 이어집니다*

```cypher
CREATE VIRTUAL RELATIONSHIP IN_ORDER IN sample FROM PoLine(po_id) TO PurchaseOrder(po_id)
```

같은 방법으로 품목과도 잇습니다. 이번에는 포털에서 직접 문장을 입력해 봅시다(포털은 [7장](07-cypher-basics.md)에서 자세히 다룹니다. 그래프 선택을 `sample`로 두세요).

```cypher
CREATE VIRTUAL RELATIONSHIP OF_ITEM IN sample FROM PoLine(item_id) TO Item(item_id)
```

![관계를 만든 뒤의 가상 그래프 — 실행한 문장이 아래에 남습니다](images/vgraph-after.webp)

*관계를 만든 뒤의 가상 그래프 — 실행한 문장이 아래에 남습니다*

가상 관계는 데이터를 복사하지 않습니다. **조인 규칙**(`PoLine.po_id = PurchaseOrder.po_id`)을 이름 붙여 저장해 둔 것이고, 질의할 때 그 규칙대로 원천을 조인합니다.

## 바로 써 보기

이제 “협력사별로 어떤 품목을 몇 개나 발주했나”를 묻는 질의를 쓸 수 있습니다. 협력사 → 발주 → 발주 품목 → 품목으로 네 노드의 관계를 따라 조회합니다.

```cypher
MATCH (s:Supplier)<-[:ORDERED_FROM]-(po:PurchaseOrder)<-[:IN_ORDER]-(l:PoLine)-[:OF_ITEM]->(i:Item)
RETURN s.name, i.name, sum(l.qty) AS qty
ORDER BY s.name, i.name
```

| s.name | i.name | qty |
| --- | --- | --- |
| Hanoi Assembly | PCB 기판 | 500 |
| Hanoi Assembly | 전원 케이블 | 2000 |
| Ningbo Magnetics | 마그넷 코어 | 1000 |
| Shenzhen Goldline PCB | PCB 기판 | 3000 |
| 대성케이블 | 전원 케이블 | 1500 |
| 한빛정밀 | 마그넷 코어 | 900 |

그리고 이번에는 **두 시스템에 걸친** 질문입니다. “3일 넘게 늦은 선적이 싣고 오는 품목과 그 안전재고는?” — 선적은 WMS에, 발주·발주 품목·품목은 ERP에 있습니다.

```cypher
MATCH (i:Item)<-[:OF_ITEM]-(l:PoLine)-[:IN_ORDER]->(po:PurchaseOrder)<-[:SHIPS]-(sh:Shipment)
WHERE sh.delay_days > 3
RETURN DISTINCT i.name, i.safety_stock, sh.shipment_no, sh.delay_days
```

| i.name | i.safety\_stock | sh.shipment\_no | sh.delay\_days |
| --- | --- | --- | --- |
| PCB 기판 | 500 | SHP-02 | 7 |
| PCB 기판 | 500 | SHP-03 | 9 |

두 선적 모두 PCB 기판을 싣고 오고 있습니다. 재고 담당자에게 먼저 알려야 할 품목이 나왔습니다.

## 만든 것을 지우려면

```
DROP VIRTUAL RELATIONSHIP OF_ITEM IN sample
DROP VIRTUAL RELATIONSHIP IN_ORDER IN sample
DROP VIRTUAL NODE PoLine IN sample
```

관계가 이어져 있는 노드는 지울 수 없습니다. 엔진이 `virtual relationships still join on 'PoLine' (IN_ORDER, OF_ITEM); drop them first`라며 거절하고, 데이터소스 탭은 이 이유를 한국어로 바꿔 보여 줍니다. 관계부터 지우세요. 원천 테이블은 아무 영향을 받지 않습니다.

> **[팁] 이어지는 장에서 PoLine을 씁니다**
>
> 7~9장의 몇몇 예제가 `PoLine`과 두 관계를 씁니다. 지우지 말고 두세요.

> **[주의] 가상 노드에 쓰려고 하면**
>
> `CREATE (x:Supplier {supplier_id:'S-XX'})`처럼 가상 노드 타입에 쓰기를 하면 다음과 같이 거절됩니다.
>
> ```text
> 'Supplier' is a virtual node type and read-only: its rows live in "erp"."supplier".
> Write to the source system, or MATERIALIZE VIRTUAL NODE Supplier to take a copy
> ```
>
> 원천 데이터를 고치는 일은 그 데이터의 주인인 업무 시스템이 해야 합니다. 꼭 사본이 필요하면 `MATERIALIZE VIRTUAL NODE`로 복사본을 만들 수 있지만, 복사한 뒤에는 원천의 변경 사항이 자동으로 반영되지 않습니다.

> **[확인 문제]**
>
> 1. `wms.stock_daily`를 `Stock` 가상 노드로 만들 수 있을까요? 무엇을 KEY로 삼아야 할지 생각해 보세요.
> 2. `SalesOrder`와 `Item` 사이의 `FOR_ITEM` 관계는 어떤 두 속성을 잇고 있을까요? `SHOW VIRTUAL RELATIONSHIPS`로 확인하세요.
> 3. 위의 “협력사별 품목 발주 수량” 질의를 고쳐서, 미결(`OPEN`) 발주만 세어 보세요.

> **▼ 정답 보기**
>
> 1. 이 테이블의 기본키는 (snapshot\_date, sku\_code, warehouse\_cd) 세 컬럼입니다. 그런데 `KEY`는 컬럼 하나만 받습니다(`KEY (a, b, c)`는 `expected the key column` 오류). `KEY sku_code`로 두면 만들어지기는 하지만, 같은 품목이 날짜·창고별로 여러 행(10행)이라 노드 하나를 키로 구별할 수 없습니다. 원천에 세 값을 하나로 이은 식별자 컬럼(예: 뷰)을 두는 것이 맞습니다. 데이터 모델링에서 “식별자”가 왜 중요한지 보여 주는 예입니다.
> 2. `SalesOrder.sku_code` → `Item.item_id`. CRM은 품목을 `sku_code`라 부르고 ERP는 `item_id`라 부릅니다.
> 3. `WHERE po.status = 'OPEN'`을 `RETURN` 앞에 넣습니다.
>
> ```cypher
> MATCH (s:Supplier)<-[:ORDERED_FROM]-(po:PurchaseOrder)<-[:IN_ORDER]-(l:PoLine)-[:OF_ITEM]->(i:Item)
> WHERE po.status = 'OPEN'
> RETURN s.name, i.name, sum(l.qty) AS qty ORDER BY s.name, i.name
> ```

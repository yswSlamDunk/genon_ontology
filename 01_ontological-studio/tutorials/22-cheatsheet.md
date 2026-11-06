# Cypher·패브릭 치트시트

*분류: 부록 · 22장 · 원문: <https://www.uengine.org/docs/ontological-studio/cheatsheet.html>*

> 이 튜토리얼에서 사용한 문장을 한곳에 모았습니다. 포털에서 실습할 때 참고하세요. 예제는 `sample` 그래프 기준입니다.

## 읽기

| 하고 싶은 일 | Cypher |
| --- | --- |
| 노드 찾기 | `MATCH (s:Supplier) RETURN s` |
| 속성 고르기 | `MATCH (s:Supplier) RETURN s.name, s.country` |
| 키로 노드 찾기 | `MATCH (s:Supplier {supplier_id: 'S-CN-01'}) RETURN s` |
| 거르기 | `WHERE s.country = 'China' AND s.tier = 1` |
| 목록 포함 | `WHERE sh.ship_status IN ['IN_TRANSIT', 'CUSTOMS_HOLD']` |
| 문자열 | `WHERE s.name CONTAINS 'Gold'` · `STARTS WITH` · `ENDS WITH` |
| 날짜 | `WHERE c.opened_date >= '2026-08-29'` |
| 정렬·자르기 | `ORDER BY po.amount_usd DESC SKIP 2 LIMIT 3` |
| 이름 바꾸기 | `RETURN po.po_id AS 발주` |
| 중복 제거 | `RETURN DISTINCT s.country` |
| 조건 값 | `CASE WHEN sh.delay_days > 3 THEN '지연' ELSE '정상' END` |
| 목록 펼치기 | `UNWIND ['SHP-02','SHP-03'] AS no MATCH (sh:Shipment {shipment_no: no}) RETURN sh` |

## 관계

| 하고 싶은 일 | Cypher |
| --- | --- |
| 관계 한 단계 조회 | `MATCH (po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)` |
| 반대 방향으로 조회 | `MATCH (s:Supplier)<-[:ORDERED_FROM]-(po:PurchaseOrder)` |
| 여러 관계 조회 | `(sh:Shipment)-[:SHIPS]->(po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)` |
| 관계도 돌려받기 | `MATCH (a:Shipment)-[r:SHIPS]->(b:PurchaseOrder) RETURN a, r, b` |
| 갈래 둘 | `MATCH (i:Item)<-[:FOR_ITEM]-(so:SalesOrder), (i:Item)<-[:OF_ITEM]-(l:PoLine)` |
| 연결된 데이터가 없어도 포함 | `OPTIONAL MATCH (sh:Shipment)-[:SHIPS]->(po:PurchaseOrder)` |
| 연결된 데이터가 없는 항목만 | `… OPTIONAL MATCH … WITH sh, po WHERE po IS NULL RETURN sh` |

## 집계

| 하고 싶은 일 | Cypher |
| --- | --- |
| 세기 | `RETURN count(s)` · `count(*)` |
| 묶어 세기 | `RETURN po.status, count(*) AS n, sum(po.amount_usd) AS total` |
| 목록으로 모으기 | `RETURN s.name, collect(po.po_id) AS orders` |
| 집계로 다시 거르기 | `WITH s, count(po) AS n WHERE n >= 2 RETURN s.name, n` |
| 소수 합계로 거르기 | `WITH s, sum(toFloat(po.amount_usd)) AS total WHERE total > 50000` |
| 목록 길이 | `size(collect(po.po_id))` |

## 쓰기 (저장 그래프에서만)

| 하고 싶은 일 | Cypher |
| --- | --- |
| 그래프 만들기 | `CREATE GRAPH tut` |
| 노드 | `CREATE (:Employee {emp_no: 'E1', name: '김하늘'})` |
| 관계 | `MATCH (a:Employee {emp_no:'E1'}), (b:Employee {emp_no:'E2'}) CREATE (a)-[:MENTORS]->(b)` |
| 값 바꾸기 | `MATCH (e:Employee {emp_no:'E1'}) SET e.salary = 4500` |
| 없으면 만들기 | `MERGE (d:Dept {name:'구매'})` |
| 지우기 | `MATCH (e:Employee {emp_no:'E2'}) DETACH DELETE e` |

## 데이터 패브릭

| 하고 싶은 일 | 문장 |
| --- | --- |
| 데이터소스 목록 | `SHOW DATASOURCES` |
| 연결 | `CREATE DATASOURCE mydb WITH ENGINE = 'postgres', PARAMETERS = {host: '…', port: 5432, database: '…', schema: 'public', user: '…', password: '…'}` |
| 테이블 | `SHOW TABLES FROM erp` |
| 컬럼 | `SHOW COLUMNS FROM erp.po_line` |
| 다시 읽기 · 해제 | `REFRESH DATASOURCE erp` · `DROP DATASOURCE erp` |
| 가상 노드 | `CREATE VIRTUAL NODE PoLine IN sample FROM erp.po_line KEY po_line_id` |
| 속성 이름 바꾸기 | `… KEY po_line_id PROPERTIES (po_line_id, po_id, item_id, qty AS quantity)` |
| 가상 관계 | `CREATE VIRTUAL RELATIONSHIP IN_ORDER IN sample FROM PoLine(po_id) TO PurchaseOrder(po_id)` |
| 목록 | `SHOW VIRTUAL NODES` · `SHOW VIRTUAL RELATIONSHIPS` |
| 지우기 | `DROP VIRTUAL RELATIONSHIP IN_ORDER IN sample` · `DROP VIRTUAL NODE PoLine IN sample` |
| 실행 계획 | `EXPLAIN FABRIC MATCH …` |

## 시간 여행

| 하고 싶은 일 | 방법 |
| --- | --- |
| 그때의 사실 | 포털 ⏱ 막대의 valid at |
| 그때 알던 것 | 포털 ⏱ 막대의 as known at |
| 시간 버전 켜기 (SQL) | `SELECT og_enable_temporal('hr', 'Employee');` |
| 변경 기록 (SQL) | `BEGIN; SET LOCAL og.valid_from = '2024-01-01'; SELECT og_cypher('hr', $$…$$); COMMIT;` |
| 정정 기록 (SQL) | `SET LOCAL og.valid_from = '-infinity'` |

## 함수

`count` `sum` `avg` `min` `max` `collect` · `toUpper` `toLower` `trim` `substring` `replace` `split` `toString` · `abs` `ceil` `floor` `round` `sqrt` `rand` `toInteger` `toFloat` · `id` `elementId` `labels` `type` `length` `size` `keys` `exists` · `coalesce` `timestamp` `datetime` · `vector.similarity` `vector.distance` `genai.vector.encode`

## 코드 앱 SDK

```cypher
import { query, schema, theme, onTheme, color, actions, act } from '/apps/_runtime/og.js'
const rows = await query('MATCH (s:Supplier) WHERE s.country = $c RETURN s.name AS name', { c: 'China' })
const out = await act({ class: 'Shipment', action: 'expediteShipment', ids: ['SHP-03'], params: { reason: '…' } })  // 0.1.1부터
```

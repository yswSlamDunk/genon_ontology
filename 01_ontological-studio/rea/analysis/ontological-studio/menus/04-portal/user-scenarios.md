# M4 Ontological Portal — 사용자 시나리오

- 상태: **초안 v0.1** (2026-10-31, 정적 분석 단계 — 실행 기록 전)
- 출처: 튜토리얼 `07-cypher-basics.md`, `08-cypher-relations.md`, `09-cypher-advanced.md`, `10-time-travel.md`, `22-cheatsheet.md` (맥락: `02-tour.md`, `04-architecture.md`) + 배포본 포털 코드에서 확인한 기능(튜토리얼에 없는 것은 "튜토리얼 없음"으로 표시)
- 기준 버전: 0.1.1 (ADR-0012)

## 검토 요청 (사용자)
1. 실제로 써 본 포털 화면·동작과 다른 부분이 있나요?
2. 스키마 디자이너(⇄ 레일 버튼)·벤치마크 페이지·`:timeline` 같은 튜토리얼 밖 기능을 실제로 써 본 적이 있나요? 비교 범위에 넣을지 알려 주세요.
3. 시간 여행 실습(S10)은 psql이 필요합니다. 실행 기록에 포함할지 결정이 필요합니다(현재 기본값: 포함, 분석용 데이터 폴더에서).

## 공통 사전 상태
- 분석용 데이터 폴더로 실행 중, 앞 메뉴(M8 설정, M3 데이터소스)까지 진행한 상태 (ADR-0009 연쇄 기록)
- 그래프: `ontology`(Studio 관리), `sample`(예제 가상 노드·관계). 예제 데이터소스 `crm`·`erp`·`wms`
- M3 S3·06장에서 만든 `PoLine` 가상 노드(`IN_ORDER`·`OF_ITEM` 관계)가 있어야 S4의 "갈래 둘" 예제가 동작
- 에이전트 = CLI 에이전트(Claude Code 또는 Codex) — S8 전제

---

## S1. 포털 열기와 화면 구성
- **목적:** 포털을 여는 여러 경로와 기본 화면을 확인한다.
- **단계:**
  1. 홈에서 「Ontological Portal」 카드를 누른다 → 새 탭 「Ontological Portal」.
  2. (대안) 홈 왼쪽 빠른 링크 「Ontological Portal」, 메뉴바 「런타임 › Ontological 포털 탭 열기」, 트레이 「Ontological Portal 탭」.
  3. 메뉴바 「런타임 › Ontological 포털을 브라우저에서 열기」 → 시스템 브라우저로 같은 포털이 열린다.
  4. 왼쪽 위 그래프 선택에서 `sample`을 고른다.
- **기대 결과:**
  - 왼쪽 레일 아이콘: 스키마(DB), 저장 질의(책갈피), 질의 기록(시계), 스키마 변경(⇄), 도움말(?), 벤치마크(막대 그래프 링크), 맨 아래 연결 점(초록=연결)
  - 스키마 패널: 제목 「Ontological DB」, 엔진 버전·DB 이름(`ogstudio`)·PostgreSQL 버전, **Entity types**(라벨 칩 + 인스턴스 수, 추상 타입은 `∗`), **Relationship types**, **Property keys**, **Type hierarchy**(하위 타입 들여쓰기)
  - 위: `$` 프롬프트와 입력칸(자리 표시: Cypher 예 + 자연어 예 "3일 넘게 늦은 선적은 어느 협력사 건이야?"), 시계(⏱)·✨·▶ 버튼
  - 브라우저로 연 포털에는 ✨ 버튼이 **없다**(자연어 기능은 앱 안에서만)
  - 포털은 낮 테마에서도 어둡게 보인다(02장)
  - 그래프 선택은 다음에 열 때 기억된다(처음에는 이름순 첫 그래프 = `ontology`로 추정)
- **기록할 것:** 첫 화면 캡처, 로딩 시 호출(`GET /api/health`, `/api/schema`, `/api/temporal`, `/api/schema-changes`), 탭 제목, 외부 브라우저 URL(포트)
- **주의:** 앱 탭과 외부 브라우저는 저장 질의·히스토리(브라우저 저장소)를 공유하지 않을 것으로 추정 — 확인

## S2. Cypher 기초 — 찾기·거르기·정렬 (07장)
- **목적:** MATCH·WHERE·RETURN·ORDER BY·LIMIT·DISTINCT·count·CASE의 결과를 확인한다.
- **단계 및 기대 결과 (튜토리얼 실측값, `sample` 그래프):**
  1. `MATCH (s:Supplier) RETURN s.supplier_id, s.name, s.country, s.tier` → 5행: S-KR-01 한빛정밀 Korea 1 / S-KR-02 대성케이블 Korea 2 / S-CN-01 Shenzhen Goldline PCB China 1 / S-CN-02 Ningbo Magnetics China 2 / S-VN-01 Hanoi Assembly Vietnam 2
  2. `MATCH (s:Supplier) WHERE s.country = 'China' AND s.tier = 1 RETURN s.name` → `Shenzhen Goldline PCB` 1행
  3. `MATCH (s:Supplier {supplier_id: 'S-CN-01'}) RETURN s` → 노드 1개, 결과 카드에 Graph 보기 생김
  4. `MATCH (c:Claim) WHERE c.opened_date >= '2026-08-29' RETURN c.ticket_no, c.opened_date` → 날짜 컬럼과 문자열 비교가 동작(행 수는 기록)
  5. `MATCH (po:PurchaseOrder) RETURN po.po_id, po.amount_usd, po.status ORDER BY po.amount_usd DESC LIMIT 3` → PO-001 82000 OPEN / PO-005 60000 OPEN / PO-002 41000 OPEN
  6. `MATCH (s:Supplier) RETURN DISTINCT s.country` → 3행(Vietnam·Korea·China) / `MATCH (s:Supplier) RETURN count(s) AS suppliers` → 5
  7. CASE 예제(선적 상태) → SHP-01 정상, SHP-02 지연, SHP-03 지연, SHP-04 정상, SHP-05 주의, SHP-06 주의, SHP-07 정상, SHP-08 정상
  8. 확인 문제: OPEN 발주 금액 오름차순 → PO-007(12000), PO-008(27000), PO-006(33000), PO-002(41000), PO-005(60000), PO-001(82000) 6건 / 선적 IN_TRANSIT·CUSTOMS_HOLD → SHP-02, SHP-03, SHP-06 / 고객 수 3 / HIGH 클레임 → T-1 「컨트롤러 전원 불량」, T-3 「PCB 납땜 불량」
- **기록할 것:** 각 질의의 `/api/cypher` 요청·응답(rows·columns·compiled_sql·sql_fingerprint·graph), 결과 카드 상태줄(행 수, 노드·관계 수, server ms·round trip ms, compiled SQL 지문)
- **주의:** 컬럼 순서는 질의에 적은 순서여야 한다(응답의 `columns`).

## S3. 결과 카드와 입력 보조
- **목적:** 결과 보기 전환, 저장, 기록, 자동완성 동작을 확인한다.
- **단계:**
  1. S2-3(`RETURN s`) 결과 카드에서 Graph → Table → JSON → SQL 탭을 차례로 누른다.
  2. 카드의 ★을 누르고, 레일 「Saved queries」에서 다시 눌러 실행, 「remove」로 지운다.
  3. 입력칸이 비었을 때 ↑/↓로 이전 질의를 불러온다.
  4. 입력칸에 `MATCH (n:` 입력 → 라벨 목록, `n.` 입력 → 속성 목록, Ctrl+Space → 강제 열기, ↑↓·Tab/Enter·Esc.
  5. 왼쪽 Entity types 칩(예: `Supplier`)·관계 칩·계층 항목을 누른다.
  6. 카드의 ✕로 닫는다. `:clear`로 전체 결과를 지운다.
- **기대 결과:**
  - 노드/관계를 반환하면 탭 순서 Graph·Table·JSON·SQL, 아니면 Table·JSON·SQL. 쓰기 질의는 SQL 탭 없음
  - 저장 질의는 최대 50개, 히스토리는 최대 100개(브라우저 저장소)
  - 라벨 칩 클릭 → `MATCH (n:Supplier) RETURN n LIMIT 50` 즉시 실행, 관계 칩 → `MATCH (a)-[r:ORDERED_FROM]->(b) RETURN a, r, b LIMIT 50`
  - 문법 색: 키워드·라벨·관계 타입·문자열·숫자·파라미터·함수·주석 구분
- **기록할 것:** 각 보기 캡처, 저장소 키(브라우저 개발자 도구)
- **튜토리얼 없음:** `:clear`, 칩 클릭 실행, Ctrl+Space

## S4. 관계 따라가기와 집계 (08장)
- **목적:** 관계 패턴, 여러 DB를 건너는 질의, OPTIONAL MATCH, 집계, WITH, UNWIND.
- **단계 및 기대 결과 (튜토리얼 실측값):**
  1. `MATCH (po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier) RETURN po.po_id, po.status, s.name` → 8행 (PO-001 OPEN Shenzhen Goldline PCB, PO-002 OPEN Shenzhen Goldline PCB, PO-003 CLOSED 한빛정밀, PO-004 CLOSED 대성케이블, PO-005 OPEN Ningbo Magnetics, PO-006 OPEN Hanoi Assembly, PO-007 OPEN Ningbo Magnetics, PO-008 OPEN 한빛정밀)
  2. 반대 방향 + `collect` → 대성케이블 ["PO-004"], Shenzhen ["PO-001","PO-002"], 한빛정밀 ["PO-003","PO-008"], Ningbo ["PO-005","PO-007"], Hanoi ["PO-006"]
  3. 선적→발주→협력사, `delay_days > 0`, 지연일 내림차순 → SHP-03 CUSTOMS_HOLD 9 PO-002 Shenzhen / SHP-02 IN_TRANSIT 7 PO-001 Shenzhen / SHP-06 IN_TRANSIT 3 PO-005 Ningbo / SHP-05 DELIVERED 1 PO-004 대성케이블
  4. `RETURN sh, r, po, o, s` (`delay_days > 3`) → Graph 보기: 선적 2건이 각자의 발주를 거쳐 같은 협력사(Shenzhen)로 모임
  5. 클레임→판매주문→고객 → T-1 HIGH 컨트롤러 전원 불량 SO-01 서울전자 / T-2 LOW 케이블 포장 파손 SO-04 Berlin Motion / T-3 HIGH PCB 납땜 불량 SO-05 Tokyo Devices
  6. 갈래 둘(납땜 불량 품목의 협력사, `PoLine` 필요) → PCB 기판 · Hanoi Assembly / PCB 기판 · Shenzhen Goldline PCB
  7. OPTIONAL MATCH 선적→발주 → 8행 중 SHP-08만 `po.po_id` null / `WITH sh, po WHERE po IS NULL` → SHP-08, PO-999
  8. 상태별 집계 → CLOSED 2 24000 12000 15000 / OPEN 6 255000 42500 82000
  9. 협력사별 미결 금액 → Shenzhen 2 123000 / Ningbo 2 72000 / Hanoi 1 33000 / 한빛정밀 1 27000
  10. 협력사별 최장 지연 → Shenzhen 9, Ningbo 3, 대성케이블 1, 나머지 0
  11. `WITH s, count(po) AS n WHERE n >= 2` → Ningbo, Shenzhen, 한빛정밀 (각 2)
  12. **알려진 제약:** `WITH s, sum(po.amount_usd) AS total WHERE total > 50000` → 오류 `invalid input syntax for type bigint`. `sum(toFloat(...))`로 바꾸면 성공
  13. `UNWIND ['SHP-02','SHP-03'] AS no MATCH (sh:Shipment {shipment_no: no}) RETURN sh.shipment_no, sh.eta` → 2행
  14. 확인 문제: 고객별 OPEN 판매주문 → Tokyo Devices ["SO-03","SO-05"], 서울전자 ["SO-02"] / 선적 2건 이상 발주 → PO-001 / HIGH 클레임 고객 → 서울전자 SO-01, Tokyo Devices SO-05 / OPTIONAL로 0건 포함 → 대성케이블 0
- **기록할 것:** 12의 오류 응답 형식(error·code·detail·hint·where), 라벨 없는 관계 패턴(`-[r]->`)이 가상 관계에서 빈 결과인지
- **주의:** 노드마다 라벨을 붙이지 않으면 가상 관계는 빈 결과(튜토리얼 경고).

## S5. 그래프 보기 상호작용
- **목적:** 그래프 보기에서 노드 살펴보기·확장.
- **단계:**
  1. S4-4 결과의 Graph 보기에서 노드를 누른다 → 오른쪽 검사기.
  2. 노드를 끌기, 빈 곳 끌어 화면 이동, 휠로 확대/축소, ⤢(맞춤), ❙❙(배치 멈춤/재개).
  3. 노드를 더블클릭한다.
  4. 검사기의 「expand neighbours」, 「history」를 누른다.
- **기대 결과:**
  - 검사기: 제목 `타입 · id`, 모든 속성 키·값
  - 더블클릭: 이웃 노드·관계가 같은 그림에 추가(방향별 최대 40)
  - expand neighbours: 새 결과 카드 `MATCH (n)-[r]-(m) WHERE id(n) = <id> RETURN n, r, m LIMIT 50`
  - history: `:sql SELECT * FROM og_history(<id>)`가 실행되지만 **앱 기본 설정에서는 raw SQL이 꺼져 있어 403 오류**가 표시될 것으로 예상(관찰: 앱이 해당 허용 설정을 주지 않음)
- **기록할 것:** `/api/expand` 요청·응답, 가상 노드에서 더블클릭 확장이 되는지(가상 관계는 저장된 간선이 아님 → 빈 확장 예상, 확인), history 오류 문구
- **튜토리얼 없음:** 전체

## S6. 실행 들여다보기 — SQL 탭, EXPLAIN FABRIC, :explain, :why (09장)
- **목적:** Cypher가 어떻게 SQL·원천 질의로 실행되는지 본다.
- **단계 및 기대 결과:**
  1. 협력사별 미결 금액 질의 → SQL 탭에 PostgreSQL SQL, 상태줄 `compiled SQL <12자리 지문>` (튜토리얼 예: `668a5ee48536` — 환경마다 다를 수 있음)
  2. `EXPLAIN FABRIC MATCH (sh:Shipment)-[:SHIPS]->(po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier) WHERE sh.delay_days > 3 RETURN sh.shipment_no, s.name` → 표 컬럼 step·place·operation·rows·detail, 3단계: ① remote:erp join 8행 ② remote:wms scan 2행(`delay_days > 3` 내려 보냄) ③ local Hash Join 2행
  3. 확인 문제: 클레임→판매주문→고객의 EXPLAIN FABRIC → 원천 한 곳(`remote:crm`)
  4. (튜토리얼 없음) `:explain <cypher>` → SQL·Plan 탭, 상태줄 columns 목록
  5. (튜토리얼 없음) `:why MATCH (s:Supplier) WHERE s.country = 'Japan' RETURN s` → Diagnosis: Compile check, Pattern walk(단계별 행 수/판정), Estimate(예상 행·비용·조언)
- **기록할 것:** EXPLAIN FABRIC 응답이 `/api/cypher`의 rows로 오는지, `/api/explain`·`/api/diagnose` 응답 형식

## S7. 데이터 패브릭 문장 (22장, M3 S4 연계)
- **목적:** 포털 입력칸에서 패브릭 문장을 실행한다.
- **단계 및 기대 결과:**
  1. `SHOW DATASOURCES` → crm·erp·wms (엔진·호스트·테이블 수)
  2. `SHOW TABLES FROM erp` → 6행 (expedite_request 9, item 3 Item, po_hold 8, po_line 4, purchase_order 5 PurchaseOrder, supplier 4 Supplier)
  3. `SHOW COLUMNS FROM erp.po_line`, `SHOW VIRTUAL NODES`, `SHOW VIRTUAL RELATIONSHIPS`
  4. (읽기 전용 확인) 가상 노드에 `SET`을 시도 → 거절(가상 노드는 읽기 전용)
- **기록할 것:** 결과 카드 형태(Table만?, SQL 탭 유무), 감사 기록에 어떻게 남는지
- **주의:** `CREATE/DROP DATASOURCE`, `CREATE/DROP VIRTUAL …`는 M3 범위 — 여기서는 조회 문장만.

## S8. 자연어 → Cypher (09장, 앱 안에서만)
- **목적:** 한국어 질문을 Cypher로 바꿔 실행한다.
- **단계:**
  1. `sample` 그래프에서 입력칸에 `3일 넘게 늦어진 입고 선적은 어느 협력사의 어느 발주 건이야?`를 쓰고 ⌘Enter (또는 ✨, ⇧⌘Enter).
  2. 결과를 확인한다.
  3. 확인 문제: `납땜 불량 클레임을 낸 고객은 누구야?`
  4. 쓰기 요청: 예) `tut 그래프에 직원 E3 을 만들어 줘` (S9 이후, `tut` 선택)
  5. 오류 경로: Cypher처럼 보이지만 실패하는 경우는 재현이 어려움 → 기록만.
- **기대 결과:**
  - 진행 중: 입력칸 테두리 강조, 아래 막대 "에이전트가 **sample** 그래프의 스키마를 보고 Cypher 로 바꾸는 중…" + 질문
  - 성공: 입력칸이 생성된 Cypher로 바뀌고 자동 실행, 막대에 `자연어` 태그·질문·한 줄 설명·`<에이전트 이름> · N.N s`(고쳤으면 `· 한 번 고침`)·`· 그래프에서 확인됨`
  - 튜토리얼 예(Claude Code, 8.7초): 선적→발주→협력사, `delay_days > 3`, `supplier, po_id, shipment_no, delay_days, ship_status` 컬럼, `ORDER BY sh.delay_days DESC LIMIT 100` → S4-3 중 지연 3일 초과 2행(SHP-03, SHP-02)
  - 3: Tokyo Devices (SO-05, T-3) — 질의는 매번 달라도 결과는 같아야 함
  - 4: "데이터를 바꾸는 문장이라 실행하지 않았습니다. 확인한 뒤 ▶ 로 실행하세요." — 입력칸에만 들어감
  - 실패: "그래프에서 실패하는 Cypher 입니다 — 고쳐서 실행하세요." + 엔진 오류
  - 에이전트가 CLI가 아니면(내장 에이전트) 오류: CLI 에이전트로만 동작한다는 안내
- **기록할 것 (ADR-0010 구조·계약):** IPC 요청·응답 필드(cypher·note·agent·ms·repaired·checked·write·error), 앱 로그의 `nl2cypher <graph>: N ms` 줄, 에이전트 호출 횟수(1 또는 2), Bolt로 시험 실행했는지
- **주의:** 에이전트 실행은 분석용 데이터 폴더에서만(ADR-0004).

## S9. 직접 쓰기 — 연습 그래프 (09장)
- **목적:** 저장 노드·관계를 Cypher로 만들고 고치고 지운다.
- **단계 및 기대 결과:**
  1. `CREATE GRAPH tut` (그래프 선택과 무관하게 실행) → 성공. 그래프 목록에는 **포털을 새로 고쳐야** 보임
  2. `tut` 선택 후 `CREATE (:Employee {emp_no: 'E1', name: '김하늘', dept: '구매', salary: 4200})`, E2 박바다 물류 3900
  3. `MATCH (a:Employee {emp_no: 'E1'}), (b:Employee {emp_no: 'E2'}) CREATE (a)-[:MENTORS {since: '2025-03'}]->(b)`
  4. `MATCH (a:Employee)-[m:MENTORS]->(b:Employee) RETURN a.name, m.since, b.name` → `김하늘 · 2025-03 · 박바다`
  5. `MATCH (e:Employee {emp_no:'E1'}) SET e.salary = 4500 RETURN e.salary` → 4500
  6. `MERGE (d:Dept {name:'구매'}) RETURN d.name` 두 번 → Dept 1개 / 확인 문제: `물류` MERGE 두 번 → `MATCH (d:Dept) RETURN d.name, count(*)` 각 1
  7. `MATCH (e:Employee), (d:Dept {name:'구매'}) WHERE e.dept = d.name MERGE (e)-[:WORKS_IN]->(d)`
  8. `MATCH (e:Employee {emp_no:'E2'}) DETACH DELETE e`
- **기록할 것:** 쓰기 질의 응답(SQL 탭 없음 = compiled_sql null), 실행 후 왼쪽 스키마 갱신(새 타입·인스턴스 수), 질의 기록 패널에 쓰기 표시, ⏱ 「as known at」 목록에 쓰기 항목이 생기는지
- **주의:** `ontology` 그래프는 Studio가 관리 — 직접 쓰지 않는다(튜토리얼 경고).

## S10. 시간 여행 — 바이템포럴 질의 (10장)
- **목적:** 같은 Cypher를 유효 시간·시스템 시간만 바꿔 다시 묻는다.
- **사전 준비 (psql, 고급):** 앱 데이터 폴더의 포트·비밀번호로 접속(사용자 `og`, DB `ogstudio`) → `og_create_graph('hr')`, `Employee` 타입·속성(name string, salary int), `og_enable_temporal('hr','Employee')` → 세 번 기록: ① valid_from 2021-01-01, salary 4000 생성 ② valid_from 2024-01-01, salary 4600(변경) ③ valid_from `-infinity`, salary 4700(정정)
- **단계:**
  1. 포털 새로 고침 → 그래프 `hr` 선택.
  2. ⏱ 누름 → TIME TRAVEL 막대: `valid at` 입력, `as known at` 목록(now + 최근 쓰기 "after HH:MM:SS.mmm · actor — 질의 앞부분"), 오른쪽 안내 `temporal types: Employee — …`, 「clear」.
  3. `MATCH (e:Employee) RETURN e.name, e.salary`를 아래 조합으로 실행.
- **기대 결과 (튜토리얼 실측값):**

  | valid at | as known at | 결과 |
  |---|---|---|
  | (비움) | now | 4700 |
  | 2022-06-01 | now | 4000 |
  | 2025-06-01 | now | 4700 |
  | 2025-06-01 | "…SET e.salary = 4600" 직후 | 4600 |
  | 2020-06-01 | now | (행 없음) |

  - 시점을 정하면 입력칸 테두리가 노란색, 결과 카드에 `⏱ valid 2022-06-01`(·`known <시각 · actor>`) 배지
  - 다섯 경우 모두 상태줄의 compiled SQL 지문이 **같다**
  - 시간 버전이 없는 타입(예: `sample`의 가상 노드)에 valid at을 주면 현재 값
  - 시간 버전 타입이 없는 그래프에서는 안내 `no temporal types in this graph — enable with og_enable_temporal(graph, type)`
- **기록할 것:** `/api/cypher` 요청의 `at` 필드와 응답 `at`, `/api/temporal` 응답(types·writes), 「as known at」 목록이 **현재 그래프가 아닌 전체 그래프의** 쓰기를 보여 주는지(코드상 그래프 필터 없음)
- **튜토리얼 없음:** `:timeline Employee name=김하늘 [from] [to] [@system_at]` → 유효 구간 막대 그래프·Table·JSON (S12에서)

## S11. 스키마 지도와 스키마 변경 (⇄ 디자이너, 10장 끝 언급)
- **목적:** 스키마를 지도로 보고, 변경을 쌓아 검토·실행한다.
- **단계:**
  1. 레일 ⇄ 버튼 → 오른쪽 본문에 「Schema map」(카드: 타입 이름·인스턴스 수·⏱(temporal)·자기 속성 `이름 · 타입 · 컬럼`·상속 속성 요약, 부모→자식 곡선), 왼쪽 「Schema designer」 패널.
  2. (`tut` 그래프에서) 속성 클릭 → Rename / Change type / Make required / Drop property 메뉴. 타입 머리 클릭 → Rename type / Add property(`name:type`) / New subtype / Insert type above / Remove parent / Add parent. 카드를 다른 카드에 끌어 놓기 → 부모 바꾸기.
  3. 쌓인 변경 확인(Change plan) → 「Review impact」 → 「Run」.
  4. 「Add as JSON」에 변경 JSON을 넣고 「Add to plan」.
  5. 「Ask」에 자연어 요청 → 「Propose changes」.
  6. History 목록 「refresh」, 콘솔에서 `:changes`, `:snapshot`, `:snapshot 1`, `:snapshot 2026-10-31T00:00:00Z`.
- **기대 결과:**
  - 클릭만으로는 아무것도 실행되지 않음("nothing runs until you press Run"), 지도에 쌓인 변경 표시(추가=점선, 제거=빨강, 이름 바꿈 취소선→새 이름)
  - Review: 변경마다 `N rows in scope · catalog only — no row rewritten` 또는 `rewrites rows in batches`, 변환 불가 값 수
  - Run: 변경마다 phase 칩(plan·expand·migrate·validate·contract, ms), 결과 `N ms · X / Y rows rewritten` 또는 `catalog`. 검증 위반 시 `blocked` + Retry validate / Abort
  - 이름 바꾸기·부모 바꾸기는 행을 다시 쓰지 않음(0 rows rewritten), 타입 변경·필수·속성 추가는 다시 씀
  - Ask: 앱 기본 실행에서는 **"AI assist is off — start the server with OPENAI_API_KEY"** 로 꺼져 있을 것으로 예상(관찰: 앱이 포털에 키를 넘기지 않음)
- **기록할 것:** `/api/schema-change` 각 단계 요청·응답, `/api/schema-snapshot` 형식, 실행 후 Cypher 결과 변화(이름 바뀐 속성으로 질의되는지)
- **주의:** `sample`(가상 타입)·`ontology`(Studio 관리)에서 실행하지 않는다. `tut`에서만. 스냅샷 후 진행.
- **튜토리얼 없음:** 상세 조작 전체(10장은 개념만 언급)

## S12. 콘솔 명령
- **목적:** `:`로 시작하는 포털 명령 확인.
- **단계 및 기대 결과:**
  - `:schema` → Schema/Storage 탭(JSON), 상태줄 "machine-readable schema — this is what an agent sees"
  - `:param c => 'China'` → "$c set for this page — not saved, not shown" / `MATCH (s:Supplier) WHERE s.country = $c RETURN s.name` → 2행(Shenzhen, Ningbo) / `:params` → `$c — values are not shown` / `:params clear`
  - `:sql SELECT 1` → 403 "raw SQL is disabled — start the server with OG_STUDIO_ALLOW_RAW_SQL=1 to enable it" (예상)
  - `:releases` → 이 그래프에 적용된 릴리스 표(아마 0건)
  - `:timeline` (인자 없음) → Usage 안내 / `:timeline Employee name=김하늘` (`hr`, S10 이후) → Timeline·Table·JSON
  - `:clear` → 결과 모두 지움
- **기록할 것:** 각 명령의 화면과 API 호출. `:param` 값이 히스토리에 남지 않는지
- **튜토리얼 없음:** 전체 (`:sql`·`:explain`·`:why`·`:schema`·`:changes`·`:snapshot`·`:param`·`:clear`는 포털 도움말 패널에 있음)

## S13. 질의 기록·도움말·오류 안내
- **목적:** 부가 패널과 오류 교정 제안.
- **단계 및 기대 결과:**
  1. 레일 「Query log」 → 최근 100개(질의, `N rows`/`error`, ms, 시각), 항목 클릭 시 재실행, 「refresh」
  2. 레일 「Help」 → 예제 스니펫(클릭 실행), 명령 목록
  3. 오타 질의: `MATCH (s:Suplier) RETURN s` → 오류 상자 + "Did you mean" 후보 칩 → 누르면 고쳐서 재실행
  4. 없는 함수: `MATCH (s:Supplier) RETURN head(collect(s.name))` → 지원 함수 목록을 알려 주는 오류(07장)
- **기록할 것:** 오류 메시지 원문, 감사 기록에 Studio/Bolt 질의도 섞여 보이는지(전역 기록)

## S14. 벤치마크 페이지 (튜토리얼 없음)
- **단계:** 레일의 막대 그래프 아이콘 → `/benchmark.html`.
- **기대 결과:** 배포본에는 결과 폴더가 없어 빈 보고서(척도 0개)로 예상.
- **기록할 것:** 화면 캡처, `GET /api/benchmark` 응답. 비교 범위에서 제외 후보.

## S15. 릴리스 패키지 API (UI 없음, 튜토리얼 없음)
- **목적:** 그래프 스키마+데이터를 패키지로 내보내고 다른 그래프에 적용하는 관리 API 확인.
- **단계 (실행 기록 시 HTTP 클라이언트로, Origin 헤더 없이):** `POST /api/release/export {graph:'tut'}` → `POST /api/release/plan {graph:'tut2', package}` → `POST /api/release/apply` → `GET /api/releases?graph=tut2` / 포털에서 `:releases`
- **기대 결과:** export: package(format `og-release/1`, hash `sha256:…`)·skipped·counts / plan: schema 변경 목록·instances(create/update/same)·hash_ok·already_applied / apply: release 기록
- **주의:** 포털 UI에는 내보내기·적용 화면이 없다(조회 명령 `:releases`만). 구현 범위 결정 필요.

---

## 튜토리얼에 없어 확인이 필요한 것
- 포털 탭을 새 창으로 분리했을 때(02장) 상태 유지 여부
- Studio 내비게이션 「Ontological Portal」(Studio 화면 안 iframe)과 포털 탭의 차이 — iframe에서는 ✨(자연어)가 없을 것으로 추정
- 그래프 선택 기본값, `CREATE GRAPH` 후 목록 자동 갱신 여부(코드상 새로 고침 필요)

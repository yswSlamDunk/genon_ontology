# A2 저장소 — 설계 문서 (클린룸)

- 상태: 초안 v0.1 (2026-10-31, 정적 분석 기반. 4단계 실행 기록 후 "모르는 점" 갱신)
- 대상: 데스크톱 앱이 내장하는 **관계형 DB + 그래프 저장 + Bolt 접속 지점**의 수명 주기와 접속 계약
- 이 문서는 원본 코드를 보지 않은 구현 세션이 이것만으로 만들 수 있도록 쓴다(ADR-0002, 0011). 동작·인터페이스·데이터 형태만 담는다.

---

## 1. 목적
- 사용자가 아무것도 설치·설정하지 않아도 앱을 켜면 **로컬 전용 DB 인스턴스**가 준비되고, 그 위에 **온톨로지 그래프 저장소**와 **Neo4j 호환(Bolt) 접속 지점**이 뜬다.
- 첫 실행 때 예제 업무 DB(ERP·WMS·CRM)와 그것을 가리키는 **데이터 패브릭 등록(데이터소스·가상 노드·가상 관계)**을 만들어, 다른 메뉴가 바로 쓸 수 있게 한다.
- 비밀값(DB 비밀번호 등)은 설치마다 무작위로 만들고 사용자 데이터 폴더에만 둔다.
- 앱 안의 모든 그래프 사용자(앱 셸, Studio 백엔드, 액션 서비스)는 표준 Neo4j 드라이버로 Bolt에 접속한다. 관리 콘솔(포털)만 DB에 직접 접속한다.

## 2. 사용자 시나리오 (요약)
운영 시나리오이며 상세는 `user-scenarios.md`.
- S1 첫 실행: 빈 데이터 폴더 → DB 초기화·기동 → 그래프·예제 DB·패브릭 준비 → 준비 완료 (실측 약 5초)
- S2 재실행: 초기화 단계 없이 기존 상태로 기동 (실측 약 3초)
- S3 포트 충돌: DB 포트가 바뀌면 예제 데이터소스를 새 포트로 재등록
- S4 종료: 역순 정지, DB는 빠른 종료(체크포인트 후)
- S5 비정상 종료 후: 지난 실행이 남긴 자식 프로세스 정리
- S6 데이터 폴더 지정·옛 이름 폴더 이전
- S7 외부 도구(psql, Neo4j 드라이버)로 관찰

## 3. 화면 구성과 상호작용
저장소 자체 화면은 없다. 시작 화면(A1)에 진행 단계 문구만 보인다(외부 관찰 계약):

| 단계 | 문구 |
|---|---|
| DB 기동 | `PostgreSQL 시작` |
| 첫 실행 준비 | `첫 실행 — Ontological 확장과 예제 DB 준비` |
| 그래프 접속 지점 | `Ontological Bolt 게이트웨이 · 포털 시작` |

실패하면 시작 화면에 오류 메시지와 로그 폴더 위치를 보여 준다. 대기 시간 초과 문구 형식: `<구성 이름>: <N>초 안에 준비되지 않았습니다`, 프로세스가 먼저 죽으면 `<구성 이름>: 프로세스가 종료됐습니다 (로그: logs/<이름>.log)`.
메뉴 「런타임」에 「데이터 폴더 열기」·「로그 폴더 열기」가 있다(A1).

## 4. 인터페이스 명세

### 4.1 구성 요소
| 구성 | 원본이 쓰는 것 | 구현 지침 |
|---|---|---|
| 관계형 DB | PostgreSQL 16 (앱 번들에 바이너리 포함) | 같은 메이저 권장. 앱 번들에 포함, 시스템 설치에 의존하지 않음 |
| 그래프 엔진 | DB 확장 「Ontological」 0.1.0 (벡터 확장 필요) — Cypher를 받아 DB 안에서 실행, 다중 그래프·타입 시스템·가상 노드(데이터 패브릭)·시점 조회·감사 | 7절 결정 사항 참고(재사용 vs 재구현) |
| 외부 DB 연결 | FDW 확장 4종: PostgreSQL, MySQL/MariaDB, Oracle, SQL Server(TDS) | 설치된 확장만 "연결 가능한 엔진"으로 노출 |
| Bolt 접속 지점 | 별도 네이티브 프로세스(상태 없는 변환기) | 4.3 계약 준수 |

### 4.2 포트 (외부 관찰 계약)
선호 포트(모두 `127.0.0.1`에만 바인드):

| 키 | 선호 포트 | 용도 |
|---|---|---|
| pg | 27432 | 관계형 DB |
| bolt | 27687 | Bolt |
| portal | 27474 | 포털(A1/M4) |
| backend 27800 · mcp 27810 · web 27900 · kinetic 27830 · erp 27841 · wms 27842 · crm 27843 | | 다른 대상 |

할당 규칙:
1. 후보 = 환경 변수 `ONTOLOGY_LITE_<KEY 대문자>_PORT` → 지난 실행에 쓴 포트(데이터 폴더의 포트 파일) → 선호 포트
2. 127.0.0.1에 배타적으로 시험 바인드해 되면 확정, 안 되거나 이미 다른 키가 잡았으면 OS가 주는 임의 포트
3. 결과를 데이터 폴더 `ports.json`(키→포트 JSON)에 저장 — 다음 실행에서 같은 포트를 다시 쓰려는 "끈끈한" 포트. 데이터소스와 외부 MCP 클라이언트 주소가 유지되도록.

### 4.3 Bolt 접속 계약
- 프로토콜: **Bolt 4.4** (드라이버가 범위를 제안하면 4.4로 협상). 서버 식별 문자열 `Neo4j/4.4.0 (ontological-bolt)`. TLS 없음(평문, 루프백 전용).
- 메시지: HELLO, RUN, PULL, DISCARD, BEGIN, COMMIT, ROLLBACK, RESET, GOODBYE, ROUTE. ROUTE에는 자기 자신 하나만 담은 라우팅 테이블을 돌려준다(광고 주소 = 리슨 주소).
- 인증: HELLO의 사용자/비밀번호 = **DB 역할과 그 비밀번호**. 별도 사용자 저장소 없음. 접속 지점은 받은 자격 증명으로 DB에 접속하고, 실패하면 `Neo.ClientError.Security.Unauthorized`. 권한·행 보안은 DB 역할 기준 그대로.
- 데이터베이스 선택: 세션의 database 이름 = **그래프 이름**. 지정이 없으면 기본 그래프(앱에서는 `ontology`). 없는 그래프는 `Neo.ClientError.Database.DatabaseNotFound`.
- 실행: 질의 하나는 DB 안의 Cypher 실행 함수 호출 1회(그래프 이름, 질의 문자열, 파라미터 JSON) → 결과 JSON 행을 Bolt 레코드로 다시 인코딩. 노드는 `{_id, _type, …속성}`, 관계는 `{_id, _type, _src, _dst, …}`를 Bolt Node/Relationship 구조로. 경로는 hop 리스트(경로 구조 아님). 시간·공간 타입 파라미터는 거부.
- 명시적 트랜잭션 = 그 세션 DB 연결의 트랜잭션.
- 트랜잭션 메타데이터 → DB 세션 설정(트랜잭션 범위)으로 전달: actor, source, reason, request_id(requestId), valid_at(validAt), system_at(systemAt), valid_from(validFrom), valid_to(validTo). 감사·시점 조회에 쓰인다.
- EXPLAIN/PROFILE: 실행하지 않고 읽기/쓰기만 판정해 요약 `type`을 `r`/`w`로.
- 오류: 엔진 메시지를 그대로, 코드 매핑 — 구문 오류 `Neo.ClientError.Statement.SyntaxError`, 인자/정의 없음 `…Statement.ArgumentError`, 권한 거부 `…Security.Forbidden`, 프로토콜 위반 `…Request.Invalid`("no HELLO on this connection", "RUN without a query").
- 동시 세션 상한: 앱은 32로 설정.
- 접속 지점 설정(프로세스 환경 변수로 전달): DB 호스트·포트·DB 이름, 기본 그래프, 리슨 주소, 광고 주소, 최대 세션 수. 시작하면 표준 출력에 `listening on <주소>, forwarding to postgres://<호스트>:<포트>/<DB> (default graph '<그래프>')` 형식 한 줄.

### 4.4 그래프 확장 문장 (데이터 패브릭, Bolt로 실행)
첫 실행 예제 등록에 쓰는 문장 형태(화면에도 노출되는 외부 계약, 상세 문법은 M3·M4):
- `CREATE DATASOURCE <이름> WITH ENGINE = 'postgres', PARAMETERS = {host, port, database, schema, user, password}` → 결과 한 행 `{result: "datasource erp (postgres): 6 tables as erp.*"}`
- `CREATE GRAPH <이름>`, `SHOW GRAPHS`
- `CREATE VIRTUAL NODE <타입> IN <그래프> FROM <데이터소스>.<테이블> KEY <컬럼>` → `virtual node Supplier ← erp.supplier (4 properties)`
- `CREATE VIRTUAL RELATIONSHIP <이름> IN <그래프> FROM <타입>(<속성>) TO <타입>(<속성>)` → 조인 조건으로 정의되는 관계(저장된 간선 아님)
- `SHOW VIRTUAL NODES IN <그래프>`(열: node, source …), `SHOW VIRTUAL RELATIONSHIPS IN <그래프>`(열: relationship, from, to — 끝점은 "타입.속성"), `DROP VIRTUAL NODE|RELATIONSHIP … IN <그래프>`, `DROP DATASOURCE <이름>`
- 이미 있으면 오류 메시지에 `already exists`가 포함된다.
- 데이터소스 테이블은 읽기 전용: 쓰기 시 `datasource table <스키마>.<테이블> is read-only: the fabric does not write to source systems` 오류.

## 5. 데이터 모델

### 5.1 DB 인스턴스 구성
| 항목 | 값 |
|---|---|
| 초기화 | UTF-8, 로캘 C, 인증 SCRAM-SHA-256(로컬·호스트 모두), 슈퍼유저 이름 `og` |
| 리슨 | TCP `127.0.0.1:<pg>`만, 유닉스 소켓 비활성 |
| 데스크톱용 설정 | shared_buffers 64MB, max_connections 40, work_mem 8MB, maintenance_work_mem 64MB, max_wal_size 256MB, min_wal_size 32MB, wal_level minimal, max_wal_senders 0, autovacuum_naptime 5min, log_min_messages warning, logging_collector off |
| 프로세스 env | 로캘 `C`; MySQL 연결 시 원격 TLS 인증서 검증을 끄는 설정(자체 서명 인증서 서버 허용, MySQL 기본 동작과 맞춤) |

### 5.2 데이터베이스
| DB | 내용 |
|---|---|
| `ogstudio` | 그래프 엔진 확장(+ 벡터 확장), PostgreSQL FDW 확장. 그래프 `ontology`(Studio가 온톨로지를 만드는 곳, 추상 루트 엔터티 타입 `_Entity`)와 `sample`(예제 가상 타입 전용) |
| `sample` | 예제 업무 데이터. 스키마 `erp`, `wms`, `crm` |

예제 그래프를 따로 두는 이유: Studio 그래프에 같은 이름의 클래스(예: 문서에서 만든 Supplier)가 생기면 읽기 전용 가상 타입과 충돌해 적재·발행이 실패하기 때문. 데이터소스는 그래프와 무관한 전역 객체.

### 5.3 역할
| 역할 | 권한 | 비밀번호 |
|---|---|---|
| `og` | 슈퍼유저. 앱의 모든 구성(셸, Studio, 액션 서비스, 포털)이 사용 | 설치별 무작위 |
| `fabric_ro` | `sample` CONNECT, erp/wms/crm USAGE + 모든 테이블 SELECT | 설치별 무작위, 첫 실행에 설정 |
| `sample_svc` | `sample` CONNECT, erp/wms/crm USAGE + SELECT/INSERT/UPDATE, 시퀀스 USAGE/SELECT. 예제 업무 서비스(M7)가 사용 | 설치별 무작위 |

### 5.4 예제 업무 데이터 (튜토리얼 실측값과 대응)
- erp: supplier(supplier_id PK, name, country, tier) 5행 · item(item_id PK, name, safety_stock) 4행 · purchase_order(po_id PK, supplier_id FK, order_date, amount_usd, status) 8행 · po_line(po_line_id PK, po_id FK, item_id FK, qty) 9행
- wms: shipment(shipment_no PK, ref_po_no, vendor_code, ship_status, delay_days, eta) 8행 — 하나는 ERP에 없는 발주를 가리킴(조인 실습용) · stock_daily(snapshot_date, sku_code, warehouse_cd 복합 PK, on_hand_qty) 10행
- crm: customer(cust_no PK, name, country) 3행 · sales_order(so_no PK, cust_no, sku_code, qty, status) 5행 · claim(ticket_no PK, so_no, severity, opened_date, subject) 3행
- 같은 개념이 시스템마다 다른 이름(공급사 supplier_id↔vendor_code, 발주 po_id↔ref_po_no, 품목 item_id↔sku_code) — 의도된 설계
- 서비스 확장(2차 마이그레이션, 멱등): wms.shipment에 priority(기본 `NORMAL`) 추가, 이력 테이블 wms.priority_change, erp.po_hold, erp.expedite_request, crm.notice 추가 → 결과적으로 erp 6, wms 3, crm 4 테이블
- 구체 행 값은 튜토리얼 실측값과 맞춰야 한다(예: SHP-03 지연 9일 CUSTOMS_HOLD, claim T-1~T-3). 행 데이터 표는 4단계 기록의 `pg_dump`에서 가져온다.

### 5.5 예제 패브릭 등록
- 데이터소스 3개(erp, wms, crm): 엔진 postgres, 호스트 127.0.0.1, 포트 = 현재 DB 포트, DB `sample`, 스키마 = 이름, 사용자 `fabric_ro` (같은 인스턴스로 되돌아오는 루프백)
- 그래프 `sample`에 가상 노드 7: Supplier(erp.supplier, 키 supplier_id), Item(erp.item, item_id), PurchaseOrder(erp.purchase_order, po_id), Shipment(wms.shipment, shipment_no), Customer(crm.customer, cust_no), SalesOrder(crm.sales_order, so_no), Claim(crm.claim, ticket_no)
- 가상 관계 5: ORDERED_FROM PurchaseOrder(supplier_id)→Supplier(supplier_id), SHIPS Shipment(ref_po_no)→PurchaseOrder(po_id), PLACED_BY SalesOrder(cust_no)→Customer(cust_no), FOR_ITEM SalesOrder(sku_code)→Item(item_id), ABOUT Claim(so_no)→SalesOrder(so_no)
- 데이터는 복사하지 않는다. 예제 업무 서비스가 원천을 바꾸면 가상 노드에 바로 보인다.

### 5.6 비밀값 파일 (`secrets.json`, 권한 0600)
JSON 객체 하나. 없으면 만들고, 빠진 키만 채워 넣은 뒤 다시 저장(기존 값은 바꾸지 않음).
| 키 | 형태 | 용도 |
|---|---|---|
| pgPassword | 18바이트 난수 base64url(24자) | 슈퍼유저 `og`, Bolt 로그인 |
| fabricPassword | 〃 | `fabric_ro` |
| svcPassword | 〃 | `sample_svc` |
| erpApiKey, crmToken | 〃 | 예제 서비스 인증(M7) |
| wmsBasic | `kinetic:<난수>` | 〃 |
| kineticInternal | 난수 | 액션 서비스 내부 비밀(M7) |
| kineticKey | RSA 2048 개인키 PEM(PKCS8) | 액션 토큰 서명(M7) |

## 6. 상태·저장

### 6.1 데이터 폴더
- 위치: 환경 변수 `ONTOLOGICAL_STUDIO_USER_DATA`(옛 이름 `ONTOLOGY_LITE_USER_DATA`)가 있으면 그 경로, 없으면 OS 앱 데이터 위치의 앱 이름 폴더(macOS `~/Library/Application Support/Ontological Studio`).
- 데이터 폴더 하나에 앱 인스턴스 하나(단일 인스턴스 잠금은 데이터 폴더 단위). 다른 폴더라면 동시 실행 가능, 포트는 각자 할당.
- 구성:
```
<데이터 폴더>/
  pgdata/        DB 클러스터(0700) + 단계 완료 표식 파일들
  run/           <구성 이름>.pid  (이 앱이 띄운 자식 프로세스)
  logs/          <구성 이름>.log (자식 표준 출력·오류 append, 시작마다 구분 헤더), desktop.log(셸), boot-timings.json
  ports.json     포트 할당 결과
  secrets.json   비밀값(0600)
  studio.env     사용자 설정(A3/M8)
  (기타: 세션 DB, 액션 서비스 DB, 샌드박스, 코드 앱 — 다른 대상)
```
- 원본 데이터 폴더와의 호환은 요구하지 않는다(새 구현은 자기 폴더를 쓴다). 단 `ports.json`·로그 위치 같은 관찰용 구조는 위와 같이 유지하면 비교가 쉽다.

### 6.2 단계 완료 표식 (멱등 부팅)
각 첫 실행 단계는 끝날 때 `pgdata` 안에 완료 시각을 담은 숨김 표식 파일을 남기고, 표식이 있으면 다시 하지 않는다. DB 클러스터와 같은 폴더에 두어 클러스터를 지우면 표식도 함께 사라지게 한다.

| 단계 | 언제 다시 하나 |
|---|---|
| 클러스터 초기화 | 클러스터 버전 파일이 없을 때 |
| 부트스트랩(그래프 DB·확장·기본 그래프·루트 타입·예제 DB·fabric_ro 비밀번호) | 표식 없을 때(초기화 직후 포함) |
| 서비스 마이그레이션(예제 서비스 테이블·sample_svc) | 표식 없을 때 — 옛 폴더는 다음 시작에 1회. 실행했다면 예제 패브릭 재등록을 요청 |
| 예제 패브릭 등록 | "등록 완료"와 "예제 전용 그래프 사용" 두 표식이 다 있어야 건너뜀 |
| 패브릭 포트 기록 | 매 시작 비교(6.3) |
| 예제 온톨로지 생성(Studio 쪽, M1 관련) | 표식 없을 때. 실패해도 앱은 열리고 다음 시작에 재시도 |

### 6.3 부팅 순서 (저장소 관련)
1. 데이터 폴더 준비, 지난 실행의 고아 프로세스 정리: pid 파일마다 살아 있고 명령줄이 이 앱 런타임을 가리키면 DB는 SIGINT, 나머지는 SIGTERM → 최대 10초 기다린 뒤 SIGKILL, pid 파일 삭제
2. 포트 할당·저장 → 비밀값 로드/생성
3. 클러스터 없으면 초기화: 슈퍼유저 비밀번호는 임시 파일(0600)로 넘기고 바로 삭제, 설정 추가
4. DB 기동: 죽은 프로세스의 lock 파일(postmaster.pid)이 남아 있으면 삭제 후 기동. 준비 확인은 DB 준비 상태 점검 도구로 150ms 간격, 60초 한도
5. 부트스트랩(필요 시): 관리 DB에 연결 확인 → `ogstudio` 없으면 생성 → 그래프 확장(의존 확장 포함)·PostgreSQL FDW 확장 → 그래프 `ontology` 생성 → `_Entity` 추상 엔터티 타입이 없을 때만 생성 → `sample` DB 없으면 생성하고 예제 스크립트 적재 → `fabric_ro` 비밀번호 설정
6. 서비스 마이그레이션(필요 시)
7. Bolt 접속 지점과 포털을 **동시에** 기동(각 30초 한도; Bolt는 TCP 연결, 포털은 HTTP 상태 확인)
8. 셸이 Bolt 드라이버 생성(풀 크기 4, `og`/pgPassword)
9. 패브릭 포트 점검: 지난번 기록된 DB 포트와 다르고 예제 패브릭이 등록돼 있으면 → 예제 패브릭 초기화(6.4) → 성공한 뒤에만 새 포트 기록(중간 실패 시 다음 시작에 재시도)
10. 서비스 마이그레이션을 방금 했으면 예제 패브릭 초기화(외래 테이블은 가져올 때 컬럼이 고정되고 새로 고침은 새 테이블만 반영하므로)
11. 예제 패브릭 등록(필요 시): 등록 스크립트를 주석 줄 제거 후 `;`+줄바꿈 단위로 나눠, 그래프 `ontology` 세션에서 차례로 실행(파라미터 pw, port[정수]). `already exists` 오류는 건너뛰고 그 외는 부팅 실패. 이전 버전처럼 예제가 `ontology` 그래프에 있으면 먼저 거기서 지운다
12. 이후 Studio·액션 서비스(A1/A3/M7)

### 6.4 예제 패브릭 초기화
`sample`·`ontology` 두 그래프 각각: 원천이 erp/wms/crm인 가상 노드를 찾고 → 그 노드에 닿는 가상 관계 삭제 → 가상 노드 삭제(그래프가 없으면 무시). 그다음 데이터소스 erp/wms/crm 삭제(오류 무시), 등록 표식 2개 삭제 → 같은 부팅의 11단계가 다시 등록.
사용자가 직접 만든 데이터소스·가상 타입은 건드리지 않는다.

### 6.5 종료
역순: 앱 서비스(Studio 백엔드·MCP 8초, 액션·예제 서비스 5초) → 포털·Bolt(5초) → DB(SIGINT = 빠른 종료, 20초 한도 후 강제). 각 단계 시간 초과면 SIGKILL. 셸 드라이버는 먼저 닫는다. Windows에서는 DB를 DB 제어 도구의 fast 모드로 멈춘다(신호 전달 불가).

### 6.6 옛 데이터 폴더 이전
환경 변수로 폴더를 지정하지 않았을 때만: 새 폴더에 DB 클러스터가 없고 옛 이름(`Ontology Studio Lite`) 폴더에 있으면 → 옛 폴더의 DB가 실행 중이면 옛 폴더를 그대로 사용; 아니면 새 폴더가 없을 때 이름 바꾸기, 있으면(전자 셸 기본 파일만 있는 경우) 항목별로 덮어 옮긴 뒤 옛 폴더 삭제; 실패하면 옛 폴더 사용. 결과는 셸 로그에 한 줄: `데이터 폴더를 새 이름으로 옮겼습니다: A → B` / `이전 이름의 데이터 폴더를 그대로 씁니다(그 앱이 실행 중): A` / `데이터 폴더를 옮기지 못해 이전 위치를 씁니다: <오류>`. (새 구현은 원본 앱 이름 이전이 필요 없으면 생략 가능)

## 7. 다른 기능과의 의존
| 사용자 | 접속 | 비고 |
|---|---|---|
| 셸(A1): 패브릭 브리지(M3), 자연어→Cypher(M4), 코드 앱(M5) | Bolt, `og` | |
| Studio 백엔드·MCP·스크립트(A3) | Bolt, `og`, 기본 database `ontology`. 접속 정보는 앱이 고정 주입하며 사용자 설정 파일로 덮어쓸 수 없다 | |
| 액션 서비스(M7) | Bolt, `og` | 자체 상태는 별도 파일 DB |
| 포털(M4) | DB 직접, `og`, `ogstudio` | 슈퍼유저 직접 접속 |
| 예제 업무 서비스(M7) | DB 직접, `sample_svc`, `sample` | |
| 데이터소스 메뉴(M3) | "연결 가능한 엔진" = 설치된 FDW 확장 목록(postgres/mysql/oracle/sqlserver) | 앱 시작 시 확장 디렉터리에서 확인 |

**결정 필요(REVIEW.md 후보):** 그래프 엔진 확장과 Bolt 접속 지점은 원본 제작사의 별도 프로젝트로, 보조 자료상 Apache-2.0으로 알려져 있으나 **배포본 안에는 라이선스 파일이 없다**. (a) 그 오픈소스 구성 요소를 라이선스 조건대로 재사용, (b) 다른 그래프 저장소(예: Apache AGE, Neo4j 커뮤니티)로 대체하고 4.3·4.4 계약만 맞춤, (c) 재구현 중 택해야 한다. Cypher 확장 문장(데이터 패브릭, 시점 조회)과 오류 문구가 다른 메뉴의 비교 항목에 그대로 나오므로 (a)가 비교 테스트에 가장 유리하다. Oracle 연결은 Oracle 클라이언트 라이브러리 재배포 조건 확인 필요.

## 8. 오류·예외
| 상황 | 동작 |
|---|---|
| 포트 점유 | 임의 포트로 대체, 다음엔 그 포트를 우선 |
| 죽은 DB lock 파일 | 삭제 후 기동 |
| DB 60초 내 미준비 / 프로세스 종료 | 부팅 실패: 시작 화면에 메시지·로그 폴더 |
| 부트스트랩 SQL 실패 | 오류 즉시 중단(첫 오류에서 정지 옵션), 표식 미기록 → 다음 시작에 다시 시도 |
| Bolt·포털 30초 내 미준비 | 부팅 실패 |
| 예제 패브릭 문장 `already exists` | 건너뜀(로그) |
| 그 외 패브릭 문장 오류 | 부팅 실패 |
| 예제 온톨로지 생성 실패 | 로그만, 다음 시작에 재시도 |
| 같은 데이터 폴더로 두 번째 실행 | 즉시 종료, 기존 창을 앞으로 |
| 비정상 종료 뒤 | 다음 시작에 고아 정리 + DB 자체 WAL 복구 |

로그: 셸 로그 줄 형식 `<ISO 시각> <메시지>`, 단계는 `[<단계>] <문구>`. 패브릭 등록 줄 `fabric: <첫 결과 행 JSON>` 또는 `fabric: skip (exists) <문장 앞 60자>`.

## 9. 원본과 비교할 테스트 항목
1. 빈 폴더 첫 실행 후 DB 목록에 `ogstudio`, `sample`; 역할 `og`(슈퍼유저), `fabric_ro`, `sample_svc`; `ogstudio` 확장 목록에 그래프 엔진·벡터·postgres_fdw
2. `SHOW GRAPHS` 결과에 `ontology`, `sample` 포함
3. `SHOW DATASOURCES` = erp, wms, crm; 각 테이블 수 6/3/4
4. `SHOW VIRTUAL NODES IN sample` 7개, `SHOW VIRTUAL RELATIONSHIPS IN sample` 5개 (이름·원천·키 일치)
5. 예제 행 수: supplier 5, item 4, purchase_order 8, po_line 9, shipment 8, stock_daily 10, customer 3, sales_order 5, claim 3; shipment에 priority 열(기본 NORMAL)
6. Bolt: Neo4j 드라이버(Node 5.x, Python 6.x)로 `og`/비밀번호 접속, database `ontology`·`sample` 선택, 서버 문자열 `Neo4j/4.4.0 (ontological-bolt)`, 협상 버전 4.4
7. Bolt 오류: 틀린 비밀번호 → Unauthorized, 없는 그래프 → DatabaseNotFound, 문법 오류 → Statement.SyntaxError
8. 리슨 주소: DB·Bolt 모두 127.0.0.1만, DB 유닉스 소켓 없음, 모든 인증 SCRAM
9. `ports.json` 키 10개와 선호 포트; 포트 점유 시 대체·재사용; DB 포트 변경 시 예제 데이터소스 재등록 로그
10. `secrets.json` 권한 0600, 키 8개, 재실행 시 값 불변
11. 재실행 시 첫 실행 단계 문구가 나오지 않음, 데이터 보존
12. 종료 후 남은 자식 프로세스 0, DB 다음 기동 시 복구 메시지 없음
13. 데이터소스 테이블 쓰기 시 읽기 전용 오류 문구
14. 데이터 폴더 환경 변수 지정 시 그 폴더만 사용

## 10. 모르는 점 (4단계 실행 기록에서 확인)
1. Bolt 협상: 실제 협상 버전, ROUTE 응답 형태, `neo4j://` 스킴 동작, 세션 32개 초과 시 오류 문구
2. Bolt 결과 인코딩 세부: 정수 크기, 노드/관계 id 형식(문자열/정수), 경로 표현, 요약 counters 실제 값 (구현 세션 계약용으로 캡처 필요)
3. 트랜잭션 메타데이터 키가 실제로 어디에 기록되는지(감사·시점 테이블) — M4 시점 조회와 함께 확인
4. 부트스트랩이 중간에 실패한 뒤 재시도할 때, 그래프 생성 단계가 "이미 있음" 오류로 다시 실패하는지(존재 확인 없이 호출함) — 복구 가능성
5. 사용자가 직접 만든 데이터소스는 DB 포트가 바뀌면 옛 포트를 가리킨 채 남는지(재등록 대상 아님)
6. FDW 데이터소스 비밀번호가 어디에 저장되는지(사용자 매핑 옵션으로 추정) — 슈퍼유저 외 노출 여부
7. 그래프 엔진 확장의 정확한 Cypher 지원 범위와 패브릭 문장 전체 문법 — M3·M4에서
8. DB 로그(`logs/postgres.log`)에 남는 경고 수준과 회전 정책(회전 없음으로 추정 — append만)
9. Windows 경로(서비스 제어 도구 사용)는 macOS 기준 기록에서 확인 불가
10. 4단계 기록용 스냅샷: `pg_dump`를 번들 도구로 `og` 계정에 대해 그래프 확장 객체까지 문제없이 덤프·복원할 수 있는지(ADR-0009 전제)

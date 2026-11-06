# A2 저장소 — 코드 추적 (원본 근거, 구현 세션에 넘기지 않음)

- 기준: 배포본 0.1.1. 경로 약어 — `main/` = `extracted-app-asar/src/main/`, `rt/` = `shared/app/runtime/`, `res/` = `shared/app/resources/`
- 표기: **관찰**(코드·파일에서 확인) / **추정** / **모름**
- 실행 증거: 사용자 기존 데이터 폴더 `~/Library/Application Support/Ontological Studio/`의 로그(2026-10-28 첫 실행, 10-31 재실행). 이번 분석에서는 앱을 실행하지 않았다(단, PostgreSQL 버전 확인을 위해 번들 `postgres --version`을 한 번 호출함 — notes.md 참고).

---

## 0. 구성 요소 한눈에

| 구성 | 실체 | 근거 |
|---|---|---|
| PostgreSQL | 16.15 (aarch64-apple-darwin), 번들 `rt/pg/bin/{initdb,postgres,pg_ctl,pg_isready,psql,pg_dump,…}` | `rt/pg/bin`, `logs/postgres.log` "starting PostgreSQL 16.15" |
| 확장 | `ontological` 0.1.0(pgrx/Rust, requires `vector`), `vector` 0.8.7, `postgres_fdw` 1.1, `mysql_fdw` 1.2, `oracle_fdw` 1.2, `tds_fdw` 2.0.5, `plpgsql` | `rt/pg/share/postgresql/extension/*.control` |
| 확장 라이브러리 | `rt/pg/lib/postgresql/{ontological,vector,postgres_fdw,mysql_fdw,oracle_fdw,tds_fdw}.dylib`; 클라이언트 `libmariadb.3`, `libsybdb.5`(FreeTDS), `lib/oracle/libclntsh.*`(Oracle Instant Client) | `rt/pg/lib` |
| Bolt 게이트웨이 | `rt/bin/ontological-bolt` Mach-O arm64, 1.55MB, Rust(tokio, tokio-postgres 0.7.18, NoTls) | `file`, `strings` |
| 셸 쪽 드라이버 | `neo4j-driver` 5.28.1 (Node) | `extracted-app-asar/package.json:10` |
| Studio 백엔드 드라이버 | Python `neo4j` 6.1.0 | `rt/studio/python/lib/python3.12/site-packages/neo4j-6.1.0.dist-info` |
| 포털 | Node `pg` ^8.13.0, PG 직접 접속 | `rt/portal/package.json`, `rt/portal/server/index.js:16,34-42` |

## 1. 부팅 순서 중 저장소 부분 (S1·S2)

`main/index.js:118-147` `boot()`:

1. `:119` 데이터 폴더 생성, `:121` `studio.env` 없으면 예제 복사(0600)
2. `:122` `procs.reapOrphans(rt.root)` — `run/*.pid` 각각: 살아 있고 명령줄에 런타임 경로나 `ontology-lite` 포함 → postgres는 SIGINT, 나머지 SIGTERM, 최대 10초(200ms×50) 후 SIGKILL; pid 파일 삭제 (`main/procs.js:36-51`)
3. `:123-127` 포트: `ports.json` 읽기 → `ports.allocate(saved)` → 다시 쓰기(모드 지정 없음, 실측 0644)
   - `main/ports.js:17` 선호 포트 `{pg:27432, bolt:27687, portal:27474, backend:27800, mcp:27810, web:27900, kinetic:27830, erp:27841, wms:27842, crm:27843}`
   - `:24` 우선순위: 환경 변수 `ONTOLOGY_LITE_<KEY>_PORT` > 저장값 > 선호값; 점유됐거나 중복이면 임의 포트(`listen(0)`), 127.0.0.1에서 `exclusive` 시험 바인드 (`:6-15`)
4. `:128` `pg.secrets(userData)` — `secrets.json` 있으면 읽고, 없으면 `{pgPassword, fabricPassword}` 각 `randomBytes(18).base64url`(24자) 생성, 0600 저장 (`main/postgres.js:19-25`)
5. `:129` `kinetic.ensureSecrets(sec)` — 없는 키만 채움: `svcPassword, erpApiKey, wmsBasic('kinetic:'+rnd), crmToken, kineticInternal, kineticKey(RSA 2048 PKCS8 PEM)`; 추가했으면 `saveSecrets` (`main/kinetic.js:29-40`, `main/postgres.js:27-29`)
6. `:131-132` `pg.initdb` (§2)
7. `:133` `pg.start` (§3), `:134` `pg.waitReady` — `pg_isready -h 127.0.0.1 -p <pg> -q` 150ms 간격, 60초, postgres 프로세스가 죽으면 즉시 실패 (`main/postgres.js:97-101`, `main/procs.js:99-107`)
8. `:135-138` `fresh || 부트스트랩 표식 없음` → `pg.bootstrap` (§4)
9. `:139` `pg.migrateServices` (§5)
10. `:142` Bolt·포털 병렬 기동 (§6, §7)
11. `:143` 셸 드라이버 `neo4j.driver('bolt://127.0.0.1:<bolt>', basic('og', pgPassword), {maxConnectionPoolSize:4, disableLosslessIntegers:false})`
12. `:144` `services.repointFabric` (§8.2), `:146` services 마이그레이션이 돌았으면 `resetSampleFabric` (§8.3), `:147` `seedFabric` (§8.1)
13. 이후 Studio·kinetic(A1/A3/M7), `:175` 첫 실행이면 `seedSampleOntology` (`:191-203`, 표식 `.ontology-lite-sample-ontology`, 실패해도 계속·다음 시작에 재시도)
14. `:182` `logs/boot-timings.json` `{at, fresh, timings}`

시작 화면 단계 문구(`progress`): `:131` 'PostgreSQL 시작', `:136` '첫 실행 — Ontological 확장과 예제 DB 준비', `:141` 'Ontological Bolt 게이트웨이 · 포털 시작'. 실패 시 `:388-396` `BOOT FAILED` 로그 + 화면 `setError(message, logDir)`.

## 2. initdb (`main/postgres.js:49-66`)
- `pgdata/PG_VERSION` 있으면 건너뜀(false 반환)
- `pgdata` 생성(0700). 비밀번호 임시 파일 `<userData>/.pwfile`(0600) → `initdb -D pgdata -U og --auth=scram-sha-256 --pwfile=… -E UTF8 --locale=C --no-instructions` → finally 임시 파일 삭제
- `postgresql.conf` 끝에 추가: `shared_buffers=64MB, max_connections=40, work_mem=8MB, maintenance_work_mem=64MB, max_wal_size=256MB, min_wal_size=32MB, wal_level=minimal, max_wal_senders=0, autovacuum_naptime=5min, log_min_messages=warning, logging_collector=off` (실측 파일과 일치)
- `pg_hba.conf`는 initdb 기본(모든 줄 scram-sha-256) 그대로 — 실측 확인
- `shared_preload_libraries` 설정 없음(관찰) → 확장은 필요 시 로드(추정)

## 3. PostgreSQL 기동·종료
- `main/postgres.js:68-95` `start`:
  - `postmaster.pid`가 있고 그 pid가 죽어 있으면 삭제(:70-75)
  - env: `LC_ALL=C`, `MARIADB_TLS_DISABLE_PEER_VERIFICATION=1` (mysql_fdw가 원격 TLS 인증서를 검증하지 않게, :76-82)
  - macOS/Linux: `procs.start('postgres', postgres, ['-D', pgdata, '-p', port, '-c', 'listen_addresses=127.0.0.1', '-c', 'unix_socket_directories='], {stopSignal:'SIGINT'})` — 유닉스 소켓 없음, TCP 127.0.0.1만
  - Windows: `pg_ctl start -W -D … -l logs/postgres.log -o "-p … -c listen_addresses=127.0.0.1"` (관리자 권한 대응, 자식 아님)
- `main/procs.js:53-66` `start`: `logs/<name>.log`에 append(시작 헤더 `--- <ISO> start <cmd> <args>`), `run/<name>.pid` 기록, 종료 시 pid 파일 삭제
- 종료 `main/index.js:341-358`: 코드앱 중지 → 웹 서버 닫기 → 드라이버 닫기 → backend·mcp(8s)·kinetic·erp/wms/crm(5s) → portal·bolt(5s) → `pg.stopFast`(Windows만 `pg_ctl stop -m fast -w -t 20`) → `procs.stop('postgres', 20000)`(SIGINT = fast shutdown, 시간 초과 시 SIGKILL) (`main/procs.js:68-76`)
- 트리거: `before-quit`(`:365-369`), `window-all-closed`(`:364`), SIGINT/SIGTERM(`:370`)

## 4. 첫 실행 부트스트랩 (`main/postgres.js:104-128`)
표식 `pgdata/.ontology-lite-bootstrap` 있으면 건너뜀. 모든 SQL은 `psql -h 127.0.0.1 -p <pg> -U og -d <db> -v ON_ERROR_STOP=1 -q -X (-c|-f)`, env `PGPASSWORD`, `PGCONNECT_TIMEOUT=5` (`:43-47`).
1. `postgres` DB에 `SELECT 1`, DB 목록 조회
2. `ogstudio` 없으면 `CREATE DATABASE ogstudio`
3. `ogstudio`: `CREATE EXTENSION IF NOT EXISTS ontological CASCADE`(→ vector 함께), `CREATE EXTENSION IF NOT EXISTS postgres_fdw`
4. `SELECT og_create_graph('ontology')` — **존재 확인 없음**(모름: 재시도 시 오류?)
5. `_Entity` 타입이 없을 때만 `og_create_type('ontology','_Entity','entity','{}',true)` (추상 entity)
6. `sample` DB가 없으면 생성 후 `res/sample/sample.sql` 실행
7. `sample`: `ALTER ROLE fabric_ro PASSWORD '<fabricPassword>'` (작은따옴표 이스케이프)
8. 표식 파일에 ISO 시각 기록

`res/sample/sample.sql` (152줄): 스키마 erp(supplier 5행, item 4, purchase_order 8, po_line 9), wms(shipment 8 — `SHP-08`은 ERP에 없는 PO-999 참조, stock_daily 10 — 복합키), crm(customer 3, sales_order 5, claim 3); 역할 `fabric_ro` LOGIN(없을 때만) + CONNECT·USAGE·SELECT(erp/wms/crm).

## 5. 서비스 마이그레이션 (`main/postgres.js:135-143`)
표식 `pgdata/.ontology-lite-services`. `res/sample/services.sql`(멱등: `IF NOT EXISTS`) 실행 → `ALTER ROLE sample_svc PASSWORD '<svcPassword>'` → 표식. 새 폴더에선 부트스트랩 직후, 옛 폴더에선 다음 시작에 1회.
- 추가: `wms.shipment.priority varchar(10) DEFAULT 'NORMAL'`, `wms.priority_change`, `erp.po_hold`, `erp.expedite_request`, `crm.notice`
- 역할 `sample_svc` LOGIN + SELECT/INSERT/UPDATE(erp/wms/crm 전 테이블) + 시퀀스 USAGE/SELECT; `fabric_ro`에 SELECT 재부여
- 사용처: 예제 서비스 `SAMPLE_DSN=postgresql://sample_svc:<pw>@127.0.0.1:<pg>/sample` (`main/kinetic.js:72`, `res/sample/services/common.py:14-25` psycopg)
- 반환 true면 `index.js:146`에서 예제 패브릭 재등록(외래 테이블은 가져올 때 컬럼이 고정되므로)

## 6. Bolt 게이트웨이 (`main/services.js:9-19`)
- 실행: `rt/bin/ontological-bolt`(인자 없음), env:
  `OG_BOLT_PGHOST=127.0.0.1, OG_BOLT_PGPORT=<pg>, OG_BOLT_PGDATABASE=ogstudio, OG_BOLT_GRAPH=ontology, OG_BOLT_LISTEN=127.0.0.1:<bolt>, OG_BOLT_ADVERTISED=127.0.0.1:<bolt>, OG_BOLT_MAX_SESSIONS=32`
- 준비 확인: TCP 연결 probe, 30초
- 정지: SIGTERM(기본), 5초 후 SIGKILL
- 바이너리 문자열(관찰):
  - 기본값: LISTEN `127.0.0.1:7687`, PGHOST `localhost`, PGPORT `5432`, PGDATABASE `og`, GRAPH `default`
  - 시작 로그: `ontological-bolt: listening on <addr>, forwarding to postgres://<host>:<port>/<db> (default graph '<g>')` (실측 `logs/bolt.log`), 그 외 `cannot bind`, `accept failed`, `session …`
  - 서버 식별 `Neo4j/4.4.0 (ontological-bolt)`, HELLO 필드 `principal`/`credentials`, `connection_id`, `hints`
  - PG 인증 SCRAM-SHA-256(클라이언트), TLS 없음(`NoTls`)
  - 실행 SQL: `SELECT og_cypher($1::text, $2::text, $3::text::jsonb)::text`(그래프, 질의, 파라미터), `SELECT og_cypher_check($1::text)::text`(읽기/쓰기 판정, EXPLAIN), `SELECT og_cypher_columns($1::text)`, `SELECT og_cypher_stats()::text`, `SELECT set_config($1, $2, true)`, `BEGIN/COMMIT/ROLLBACK`
  - tx_metadata → 세션 설정 키: `og.actor, og.source, og.reason, og.request_id(requestId), og.valid_at(validAt), og.system_at(systemAt), og.valid_from(validFrom), og.valid_to(validTo)`
  - 메시지: HELLO·RUN·PULL·DISCARD·BEGIN·COMMIT·ROLLBACK·ROUTE(`ttl`,`servers`,`rt`), `db` 필드, `bookmark`, `has_more`, `t_first`, `t_last`, `qid`, `type`(r/w)
  - 오류 코드: `Neo.ClientError.Security.Unauthorized`, `.Security.Forbidden`, `.Request.Invalid`, `.Statement.SyntaxError`, `.Statement.ArgumentError`, `.Database.DatabaseNotFound`; 메시지 `no HELLO on this connection`, `RUN without a query`, `unsupported Bolt message 0x..`
  - 빌드 경로 흔적 `/Users/uengine/uengine-platform/ontology-studio-desktop/.cache/cargo/...` (정보만)
- 보조 참고(배포본 아님, 소스 저장소 `ontological-db/bolt/README.md`): Bolt 4.4만, 세션 database = 그래프, HELLO 사용자/비밀번호 = PG 역할, Path는 hop 리스트, 시간·공간 타입 미지원, TLS 없음. 배포본 문자열과 모순 없음. 단 README의 LISTEN 기본값(0.0.0.0)은 배포본 문자열(127.0.0.1)과 다름 → 배포본 기준.

## 7. 다른 구성의 저장소 접속

| 클라이언트 | 경로 | 계정 | 그래프/DB | 근거 |
|---|---|---|---|---|
| 셸(Electron) | Bolt, neo4j-driver 5.28.1 | og / pgPassword | 세션 database `ontology`, `sample`, 패브릭 문장 | `main/index.js:143`, `main/services.js:251`, `main/fabric-bridge.js:57-64` |
| Studio 백엔드·MCP·스크립트 | Bolt, Python neo4j 6.1.0 | env `NEO4J_URI=bolt://127.0.0.1:<bolt>`, `NEO4J_USER=og`, `NEO4J_PASSWORD=pgPassword`, `NEO4J_DATABASE=ontology` (사용자 studio.env로 덮어쓸 수 없음) | ontology | `main/services.js:126-127`, `backend/src/shared/kernel/settings.py:41-46,188-191` |
| kinetic-action | Bolt | `KINETIC_NEO4J_*` 같은 값; 자체 저장은 SQLite `<userData>/kinetic.db` | ontology | `main/kinetic.js:80-81` |
| 포털 서버 | PostgreSQL 직접(node-postgres Pool max 8) | `PGUSER=og`, `PGPASSWORD=pgPassword`, `PGDATABASE=ogstudio` | ogstudio | `main/services.js:22-32`, `rt/portal/server/index.js:34-42` |
| 예제 서비스 erp/wms/crm | PostgreSQL 직접(psycopg) | sample_svc | sample | §5 |
| 패브릭(FDW) | postgres_fdw 루프백 → 같은 인스턴스 | fabric_ro / fabricPassword | sample | `res/sample/fabric.cypher:8-10` |
| 셸 부트스트랩 | `psql` 프로세스 | og | postgres/ogstudio/sample | §4 |

## 8. 예제 패브릭 (Bolt 경유)

### 8.1 seedFabric (`main/services.js:244-271`)
- 표식 `pgdata/.ontology-lite-fabric` **그리고** `.ontology-lite-fabric-sample-graph` 둘 다 있으면 건너뜀
- `res/sample/fabric.cypher` 읽기 → `//` 주석 줄 제거 → `;\s*\n` 기준 분리
- 옛 버전 표식만 있으면(예제가 `ontology` 그래프에 있었음) `dropSampleTypes(ontology)` 먼저
- 세션 database `ontology`에서 각 문장 실행, 파라미터 `{pw: fabricPassword, port: int(pg)}`; 오류 중 `already exists`는 무시(로그 `fabric: skip (exists) …`), 그 외는 중단
- 문장(23줄 파일): `CREATE DATASOURCE erp|wms|crm WITH ENGINE='postgres', PARAMETERS={host:'127.0.0.1', port:$port, database:'sample', schema:'<s>', user:'fabric_ro', password:$pw}`; `CREATE GRAPH sample`; `CREATE VIRTUAL NODE` ×7 (Supplier←erp.supplier KEY supplier_id, Item←erp.item, PurchaseOrder←erp.purchase_order, Shipment←wms.shipment KEY shipment_no, Customer←crm.customer, SalesOrder←crm.sales_order, Claim←crm.claim KEY ticket_no); `CREATE VIRTUAL RELATIONSHIP` ×5 (ORDERED_FROM, SHIPS, PLACED_BY, FOR_ITEM, ABOUT)
- 실측 응답(`desktop.log` 2026-10-28): `{"result":"datasource erp (postgres): 6 tables as erp.*"}`, `wms 3`, `crm 4`, `graph sample created`, `virtual node Supplier ← erp.supplier (4 properties)` …, `virtual relationship (:PurchaseOrder)-[:ORDERED_FROM]->(:Supplier) on PurchaseOrder.supplier_id = Supplier.supplier_id`
- 끝나면 두 표식 기록(두 번째 내용 `sample`)

### 8.2 repointFabric (`main/services.js:280-291`)
- `pgdata/.ontology-lite-fabric-port`(이전 PG 포트) vs 현재. 같거나 패브릭 표식이 없으면 현재 포트 기록 후 끝
- 다르면 `resetSampleFabric(…, 'PostgreSQL 포트가 A → B 로 바뀌어 …')` 후 포트 기록(실패 시 기록 안 함 → 다음에 재시도)

### 8.3 resetSampleFabric / dropSampleTypes (`main/services.js:226-241, 298-308`)
- `sample`, `ontology` 두 그래프에서: `SHOW VIRTUAL NODES IN g` 중 source가 erp/wms/crm인 노드 → 이 노드에 닿는 `SHOW VIRTUAL RELATIONSHIPS IN g`를 `DROP VIRTUAL RELATIONSHIP r IN g` → `DROP VIRTUAL NODE n IN g`. 그래프가 없으면(`not exist|unknown|no graph`) 무시
- `DROP DATASOURCE erp|wms|crm` (오류 무시)
- 표식 `.ontology-lite-fabric`, `-sample-graph` 삭제 → 같은 부팅의 seedFabric이 다시 등록

## 9. FDW 엔진 감지 (`main/index.js:206-211`)
- `rt/pg/share/postgresql/extension` 또는 `rt/pg/share/extension`에 `<ext>.control`이 있는 엔진만: postgres→postgres_fdw, mysql→mysql_fdw, oracle→oracle_fdw, sqlserver→tds_fdw. 0.1.1에선 4개 모두 있음 → 패브릭 브리지에 `engines` 전달(M3 화면의 엔진 목록)

## 10. 데이터 폴더 결정과 이전 (`main/index.js:38-81`)
- `ONTOLOGICAL_STUDIO_USER_DATA` 또는 `ONTOLOGY_LITE_USER_DATA` → 그 경로, 이전 없음 (`:67-69`)
- 아니면 `migrateUserData()` (`:41-66`): "데이터 있음" = `pgdata` 존재. 새 폴더에 없고 `<appData>/Ontology Studio Lite`에 있으면:
  - 옛 `pgdata/postmaster.pid` 또는 `run/postgres.pid`의 pid가 살아 있으면 옛 폴더를 그대로 사용
  - 새 폴더가 없으면 rename; 있으면(Electron 기본 파일만) 옛 폴더 항목마다 새 쪽 같은 이름 삭제 후 이동, 옛 폴더 rmdir
  - 실패하면 옛 폴더 사용. 결과 문구는 boot 시 로그
- `:72` `requestSingleInstanceLock()` — 데이터 폴더 단위 단일 실행
- 폴더 구성 `:74-81`: `pgdata`, `logs`, `run`, `sandbox`, `studio.env`

## 11. 데이터 폴더 실측 (사용자 기존 폴더, 값 비공개)
```
<userData>/
  pgdata/  (0700)  PG_VERSION … postgresql.conf, pg_hba.conf, postmaster.pid
           .ontology-lite-bootstrap  .ontology-lite-services  .ontology-lite-fabric
           .ontology-lite-fabric-sample-graph  .ontology-lite-fabric-port(=27432)  .ontology-lite-sample-ontology
  run/     backend.pid bolt.pid crm.pid erp.pid kinetic.pid mcp.pid portal.pid postgres.pid wms.pid
  logs/    desktop.log boot-timings.json postgres.log bolt.log portal.log backend.log mcp.log kinetic.log erp.log wms.log crm.log backend/
  ports.json (0644)  secrets.json (0600; 키: crmToken erpApiKey fabricPassword kineticInternal kineticKey pgPassword svcPassword wmsBasic)
  studio.env (0600)  sessions.db(+wal)  kinetic.db  sandbox/  codeapps/  + Electron 자체 파일
```
`postmaster.opts`: `postgres -D <pgdata> -p 27432 -c listen_addresses=127.0.0.1 -c unix_socket_directories=`.

## 12. Ontological 확장 개요 (`rt/pg/share/postgresql/extension/ontological--0.1.0.sql`, 3161줄, pgrx 생성)
- 스키마 `og_catalog`(타입 시스템·카탈로그), `og_data`(그래프 저장), `og_action`(액션별 SECURITY DEFINER 함수)
- 주요 테이블: graph, type(kind e/r/a, is_abstract, storage_table, iri), type_parent, type_label, property, role, og_constraint, rule, schema_version, og_adj/og_node/og_edge, setting, grantee, embedding, og_history, og_source, datasource(name, engine, server_name, options), virtual_rel(src/dst type·prop), agent_role, og_audit, write_grant, action, schema_change, temporal, stamped, release
- 데이터소스 테이블에 쓰기 거부 트리거 함수(`datasource table %.% is read-only …`)
- 공개 함수 약 120개(og_cypher*, og_create_graph/type/node/edge, og_create_datasource, og_fabric*, og_release_*, og_timeline, og_history, og_vector_search, og_hybrid_search, og_typeql*, og_load_rdf/og_dump_rdf, ontological_version …). 상세는 M3·M4에서.
- 실측 오류 예(`postgres.log`): `OG_RESERVED_PROPERTY: '__ontology_publish_declare' is system-managed …` — 예약 속성 규칙이 엔진에 있음(M1과 관련)

## 13. 설정값 요약
| 이름 | 값/의미 | 근거 |
|---|---|---|
| `ONTOLOGICAL_STUDIO_USER_DATA` / `ONTOLOGY_LITE_USER_DATA` | 데이터 폴더 지정 | index.js:67 |
| `ONTOLOGY_LITE_<PG|BOLT|PORTAL|BACKEND|MCP|WEB|KINETIC|ERP|WMS|CRM>_PORT` | 포트 강제 선호값 | ports.js:24 |
| `OG_BOLT_*` | §6 | services.js:13-15 |
| `PGPASSWORD`, `PGCONNECT_TIMEOUT=5` | psql 호출 | postgres.js:46 |
| `MARIADB_TLS_DISABLE_PEER_VERIFICATION=1` | postgres 프로세스 env | postgres.js:81 |
| `NEO4J_URI/USER/PASSWORD/DATABASE` | Studio 쪽, 앱이 고정 | services.js:127 |

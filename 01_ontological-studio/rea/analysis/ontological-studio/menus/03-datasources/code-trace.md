# M3 데이터소스 — 코드 추적 (원본 근거, 구현 세션에 넘기지 않음)

- 기준: 배포본 0.1.1. 경로 약어
  - `SH` = `extracted-app-asar/src`
  - `FE` = `shared/app/runtime/frontend/assets/index-Bnym06ph.js` (한 줄 번들이라 **바이트 오프셋** `@NNNN`으로 표시)
  - `BE` = `shared/app/runtime/studio/app/backend/src`
  - `EXT` = `shared/app/runtime/pg/share/postgresql/extension/ontological--0.1.0.sql`, `DYL` = `shared/app/runtime/pg/lib/postgresql/ontological.dylib`(문자열로만 확인)
- 관찰/추정 구분: 표시 없는 것은 코드에서 관찰. "(추정)"은 코드 정황으로 판단.

## 0. 전체 구조 한눈에

```
홈 카드 「데이터소스」 (SH renderer/shell/shell.js:42)  target {kind:'studio', view:'datasources'}
  └ 탭 URL ?view=datasources[&ds=<name>]   (SH main/tabs.js:24, 86)
      └ Studio SPA: Pt==='datasources' → 컴포넌트 Mt (FE @2310549)
           Mt = kt==='ontological' ? FabricDataSourcePanel : AnalyzerDataSourcePanel  (FE @2305201, kt 상수 'ontological')
           FabricDataSourcePanel (FE @86688) ── fetch '/fabric-bridge/fabric' + path
  └ 셸 로컬 웹 오리진 (SH main/web.js:69) '/fabric-bridge/*' → bridge(req,res,subpath)
      └ fabric-bridge (SH main/fabric-bridge.js:57 createBridge) ── neo4j-driver, Bolt
           └ ontological-bolt 게이트웨이 → PostgreSQL 'ogstudio' DB 의 ontological 확장(Rust)
                └ 패브릭 문장 → og_create_datasource / og_map_virtual / og_create_virtual_rel / … (EXT 1139, 1932, 1245, 1510, 1545, 2000)
                     └ postgres_fdw / mysql_fdw / oracle_fdw / tds_fdw 외부 서버·외부 테이블 → 원천 DB
```

Python 백엔드는 **이 화면에 관여하지 않는다**. 백엔드의 `/api/datasources*`(BE modules/ontology/datasource_api.py)는 다른 화면(M1 구축 브리프)과 에이전트 도구용 카탈로그 프록시이며, 그 상류도 같은 fabric-bridge다(§6).

## 1. 진입·화면 마운트

| 항목 | 위치 | 내용 |
|---|---|---|
| 홈 카드 | SH renderer/shell/shell.js:42 | 「데이터소스」 「원천 DB 를 연결하고 가상 노드로 노출합니다.」 → `{kind:'studio', view:'datasources'}` |
| 홈 최근 항목 | shell.js:219–248 | `/fabric-bridge/fabric/overview`를 읽어 데이터소스별 행 생성: `info = "<engine> · 테이블 <table_count> · 노드 <n>"`, target에 `ds: <name>` |
| 탭 URL | SH main/tabs.js:24, 86 | target의 `view`, `session`, `ds`를 쿼리스트링으로 |
| 뷰 목록 | FE @2305201 부근 | `Nt` 배열의 `{id:'datasources', label:'데이터소스', icon:'🗄'}` |
| 뷰 분기 | FE @2310549 | `Pt.value==='datasources'` → `ci(sr(V(Mt)),{class:'fullscreen-view', onOpenPortal: ()=>Vt('browser')})` |
| 대체 패널 | FE @73891 `AnalyzerDataSourcePanel` | `/api/gateway/data-fabric/api/datasources` + `/analyzer/index.html` iframe. `kt` 가 상수 `'ontological'`이라 이 빌드에선 **사용 안 됨**(죽은 코드). 셸도 `/analyzer`에 "포함되지 않은 화면" HTML을 돌려줌(SH main/web.js:35–39, 81–84) |

## 2. 프런트엔드 컴포넌트 `FabricDataSourcePanel` (FE @86688 ~ @117000)

### 2.1 요청 래퍼
- `aie = '/fabric-bridge/fabric'` (FE @86661). 함수 `i(method, path, body)`: JSON 본문이면 `content-type: application/json`. 응답 `!ok`이면 `Error(body.error || 'HTTP <status>')`에 `statement` 속성을 붙여 throw.
- 엔진 목록은 별도로 `fetch('/fabric-bridge/fabric/engines')` (FE @98983), 실패 시 프런트 내장 4개 유지.

### 2.2 상태 (요약)
- `f` overview: `{graph, sample_graph, graphs[], datasources[], virtual_nodes[], virtual_relationships[]}`
- `_` 선택: `{kind: ''|'ds'|'graph', name}`
- `v` 테이블 목록, `x` 선택 테이블 이름, `b` 테이블 검색어, `S` 컬럼, `w` 미리보기, `ce` 가상 노드 폼, `ve` 관계 폼, `Ie` 연결 모달, `E` 실행 로그(최대 30), `D` 로그 펼침, `O` 노드별 속성 캐시, `g` 배너 오류, `m` 상단 오류, `h` 쓰기 진행 중(버튼 비활성).

### 2.3 흐름
| 기능 | 위치 | 동작 |
|---|---|---|
| 첫 로딩 `L()` | FE @91903 | `GET /overview` → 쿼리 `ds`가 있고 존재하면 그 데이터소스, 아니면 첫 데이터소스 선택. 실패: 「패브릭 정보를 읽지 못했습니다: …」 + 「다시 시도」 |
| 데이터소스 선택 `ae(name)` | FE @91903 이후 | `_={kind:'ds',name}` → `re()` |
| 테이블 목록 `re(keep)` | 같은 곳 | `GET /datasources/{ds}/tables` → 이전 선택 테이블 유지 또는 첫 테이블로 `de()` |
| 테이블 검색 `j` | FE `A=Ni(...)`,`j=Ni(...)` | 클라이언트 필터: 이름 또는 `virtual_node`에 소문자 포함 |
| 테이블 선택 `de(t)` | FE @92989 이후 | `GET /datasources/{ds}/tables/{t}/columns` → 가상 노드면 `fe()`(미리보기), 아니면 노출 폼 기본값 채움 |
| 키 추정 `ue(cols)` | FE @92989 | `primary_key` 컬럼 → 없으면 NOT NULL 이면서 이름이 `^id$|_id$|_no$|_code$|_key$` → 없으면 첫 NOT NULL → 첫 컬럼 |
| 노드 이름 추정 `le` | 같은 곳 | 영숫자 외 문자로 쪼개 각 조각 첫 글자 대문자로 이어 붙임, 숫자로 시작하면 앞에 `T` |
| 그래프 기본값 | `de` 안 | 이 데이터소스를 원천으로 하는 기존 가상 노드의 그래프 → `sample_graph` → `graph` |
| 미리보기 `fe()` | FE @93661 | `GET …/preview?limit=20` → 결과 열을 SHOW COLUMNS 순서로 재정렬(모르는 열은 뒤로). 실패 시 `note`에 오류 |
| 미리보기 문장 표시 `P` | `P=Ni(...)` | `MATCH (n:<첫 노드 라벨>) RETURN n LIMIT 20` (표시·복사용. 실제 실행은 브리지가 함) |
| 경로 문구 | 템플릿 | `<행수>행 · Bolt → Ontological → <fdw> → 원천`, fdw는 엔진→`postgres_fdw|mysql_fdw|oracle_fdw|tds_fdw` 매핑(`Fe`, FE @98066 부근, `mindsdb`→mysql 별칭 포함) |
| 실행될 문장 미리보기 `he(src, path)` | FE @94163 | 폼 객체가 바뀔 때마다(깊은 감시, 180ms 디바운스) `POST path {…form, dry:true}` → `statement` 또는 `error`를 표시. 최신 요청만 반영(카운터) |
| 노드 폼 본문 `ge` | FE @94481 | `{label, graph, source:'<ds>.<table>', key, properties}`. 모든 속성이 켜져 있고 이름이 같으면 `properties: []`, 아니면 켜진 것(+KEY)만 `{column, as}` |
| 관계 폼 본문 `ye` | FE @94936 | 그래프 뷰에서만: `{name, graph:<선택 그래프>, from:{node, property}, to:{node, property}}` |
| 노드 속성 목록 `Se(node)` | FE `function xe`/`Se` | 노드의 원천 테이블로 `preview?limit=1` 열 이름(없으면 `columns` 이름)을 SHOW COLUMNS 순으로 → 캐시 `O` |
| 속성 자동 선택 `Ce` | 같은 부근 | 출발 노드 변경: 도착 노드의 KEY가 출발 속성에 있으면 그것, 아니면 양쪽 공통 이름, 아니면 첫 속성. 도착 노드 변경: 도착 노드 자신의 KEY → 공통 → 첫 속성 |
| 지도 레이아웃 `we` | FE @95965 | 폭 1000, 열=데이터소스(이름순), 노드는 열마다 y=62+58·i, 같은 열 관계는 오른쪽으로 휘는 곡선, 이름표 겹침 회피(최대 8번 21px 내림) |
| 쓰기 공통 `Te(method, path, body, after)` | FE @97225 | 성공: 로그에 `{statement, ok:true, result: result || '완료'}` → `after()`; 실패: 로그에 `{statement: err.statement || '<METHOD> <path>', ok:false, error}` + 배너 |
| 갱신 `Ee()` | 같은 곳 | `GET /overview`, 속성 캐시 비움, 데이터소스 뷰면 테이블 다시 읽기 |
| 쓰기 호출 | 같은 곳 | `De` POST `/virtual-nodes`; `Oe(label,graph)` DELETE `/virtual-nodes/{label}` 본문 `{graph}`; `ke` POST `/virtual-relationships`(성공 시 이름 칸 비움); `Ae(name,graph)` DELETE `/virtual-relationships/{name}` 본문 `{graph}`; `je` POST `/datasources/{ds}/refresh` `{}`; `Me` DELETE `/datasources/{ds}` `{}` → 선택 해제 후 `L()` |
| 로그 `ne` | FE @91786 | 앞에 추가, 30건 초과 잘라냄. 메모리에만 |
| 엔진 폼 정의 `Ne` | FE @98066 | postgres {label PostgreSQL, port 5432, schema 'public', db 'database', dbLabel 데이터베이스}; mysql {MySQL · MariaDB, 3306, schema null(칸 없음), dbLabel 「데이터베이스 (MySQL 에서는 이것이 스키마)」}; oracle {Oracle, 1521, schema '' 힌트 「소유자, 보통 대문자 (예: HR)」, db 'service' 「서비스 이름」 힌트 `FREEPDB1 · ORCLPDB1 …`}; sqlserver {SQL Server · Azure SQL, 1433, 'dbo'} |
| 모달 열기 `ze` | `function ze(){Ie.error…` (@99000 부근) | 기본 폼 `{name:'', engine:'postgres', host:'127.0.0.1', port:5432, database:'', service:'', schema:'public', user:'', password:''}` |
| 엔진 변경 `Be` | 같은 곳 | 포트와 스키마를 엔진 기본값으로 |
| 모달 본문 `Ve` | 같은 곳 | 이름·호스트·DB(또는 service)·사용자 필수, oracle은 schema 필수. mysql이면 schema 키 삭제. 미충족 시 null → 미리보기·연결 비활성 |
| 연결 `Ue` | 같은 곳 | `Te('POST','/datasources', body, ()=>{L(); ae(name)})` 성공 시 모달 닫음, 실패 시 모달 하단 오류 |
| 확인 버튼 컴포넌트 `l` | FE @88397 앞 | 1차 클릭 → 문장 힌트(키워드 강조) + 확인 버튼 + 「취소」로 바뀜 |
| 문장 강조 `s` | FE @87000 부근 | 따옴표 리터럴과 키워드 목록(CREATE, DROP, REFRESH, DATASOURCE, WITH, ENGINE, PARAMETERS, VIRTUAL, NODE, RELATIONSHIP, FROM, TO, KEY, PROPERTIES, AS, MATCH, RETURN, LIMIT, SHOW, TABLES, COLUMNS)을 span으로 감쌈. HTML 이스케이프 후 innerHTML |
| 오류 번역 `u`/`d` | FE @88397 | 정규식 → 한국어 문장 표(아래 §5). 번역되면 굵은 한국어 + 원문 `<code>` |

### 2.4 화면 문구 (관찰)
`Data fabric`, 버튼 title `데이터소스 연결`, `그래프 <graph> · Ontological`, `데이터소스 <n>`, `불러오는 중…`, `연결된 데이터소스가 없습니다.` + `연결하기`, `가상 그래프`, 태그 `Studio`/`예제`, `노드 n · 관계 m`, `데이터는 복사하지 않습니다. 가상 노드는 질의할 때마다 원천을 그 자리에서 읽습니다.`, `Ontological Portal 에서 질의`, `Datasource`, `<host> · 테이블 n · 가상 노드 m`, `테이블 다시 읽기`(title `REFRESH DATASOURCE — 원천에 새로 생긴 테이블을 가져옵니다`), `연결 해제`/`해제`/`취소`, `테이블 찾기`, `가상 노드 :X`, `노출 안 됨`, `컬럼을 읽는 중…`, 표 머리 `컬럼 타입 제약`, `NOT NULL`, `KEY`(title `가상 노드의 KEY`), `미리보기`, `그래프 g`, `문장 복사`, `노출 해제`, `원천을 읽는 중…`, `행이 없습니다.`, `가상 노드로 노출`, `원천 행 하나가 노드 하나가 됩니다. 데이터는 복사하지 않습니다.`, `노드 타입 이름`, `그래프`, `KEY 컬럼`, `속성`, `고르지 않으면 모든 컬럼이 같은 이름의 속성이 됩니다.`, `실행될 문장`, `가상 노드 만들기`, `왼쪽에서 테이블을 고르세요.`, `Virtual graph`, `가상 노드 n, 관계 m. 관계는 두 노드의 속성 값이 같은 행끼리 잇습니다.`, `지도`, `열 = 데이터소스. 노드를 누르면 원천 테이블로 갑니다.`, `노드 타입`(노드/원천/KEY/속성/저장), `가상`/`물리화`, `삭제`, `이 그래프에는 가상 노드가 없습니다. 데이터소스의 테이블에서 만드세요.`, `관계`(관계/출발/도착), `관계가 없습니다.`, `관계 만들기`, `출발 노드의 속성 값이 도착 노드의 속성 값과 같은 행끼리 이어집니다.`, `관계 이름`(placeholder `SUPPLIES`), `출발 노드`, `도착 노드`, `노드`, `왼쪽에서 데이터소스를 고르세요.`, `실행한 문장`, 모달 `CREATE DATASOURCE`/`데이터소스 연결`/`원천 스키마의 테이블을 외부 테이블로 들여옵니다(<fdw>). 행은 복사하지 않습니다 — 가상 노드로 노출한 뒤 질의할 때 읽습니다.`, `이름`+`패브릭에서 스키마 이름이 됩니다 (영문 소문자·숫자·밑줄)`(placeholder `sales`), `엔진`, `— 이 설치에 없음`, `스키마`, `호스트`, `포트`, `사용자`, `비밀번호`, `연결`. 모달은 배경 클릭·Esc로 닫힘.

## 3. 셸 fabric-bridge (SH main/fabric-bridge.js)

### 3.1 생성과 연결
- SH main/index.js:143 Bolt 드라이버: `bolt://127.0.0.1:<ports.bolt>`, 계정 `og`(PG 슈퍼유저, postgres.js:14) / `secrets.pgPassword`, 풀 4.
- index.js:150 `createBridge(() => driver, pg.GRAPH('ontology'), {sampleGraph: 'sample', engines: fabricEngines()})`.
- index.js:205–211 `fabricEngines()`: PG 확장 폴더에 `postgres_fdw|mysql_fdw|oracle_fdw|tds_fdw .control`이 있는 엔진만. (배포본 mac에는 4개 모두 존재 — `pg/share/postgresql/extension/` 확인)
- SH main/web.js:69 `/fabric-bridge/*` → bridge. web.js:74–75 `/api/gateway/data-fabric/*`, `/api/gateway/text2sql/*`도 bridge. 서버는 `127.0.0.1`에만 바인딩(web.js:88). 인증 없음.

### 3.2 읽기 (모두 READ 세션, 데이터베이스 = 그래프 이름)
| 함수 | 줄 | 패브릭 문장 | 변환 |
|---|---|---|---|
| graphs | 63–65 | `SHOW GRAPHS` | `graph` 열 |
| virtualNodes | 66–70 | 그래프마다 `SHOW VIRTUAL NODES IN <g>` | 행 + `graph` |
| virtualRelationships | 71–75 | 그래프마다 `SHOW VIRTUAL RELATIONSHIPS IN <g>` | 행 + `graph` |
| datasources | 77–79 | `SHOW DATASOURCES` | `{name, engine, display_name:name, database:name, host, table_count:tables}` |
| tables | 80–84 | `SHOW TABLES FROM <ds>` | `{name: table에서 '<ds>.' 제거, schema: ds, column_count, virtual_node, description: virtual_node ? '가상 노드 :X' : ''}` |
| sample | 85–98 | (가상 노드면) `MATCH (n:<label>) RETURN n LIMIT <1..200>` in 노드의 그래프 | `_id`,`_type` 제거; `{columns, rows(배열의 배열), virtual_node, graph}`. 가상 노드가 없으면 `{columns:[], rows:[], note:'<ds>.<t> 에 가상 노드가 없습니다. CREATE VIRTUAL NODE … FROM <ds>.<t> KEY … 로 노출하면 읽을 수 있습니다.'}`. 테이블 없으면 404 |
| columns | 101–112 | `SHOW COLUMNS FROM <ds>.<t>` | `{name, type, nullable, primary_key: !!key, description:''}`. 엔진이 SHOW COLUMNS를 모르면 샘플 1행으로 타입 추정(`integer|numeric|boolean|date|text|unknown`) |
| overview | 113–116 | 위 4개 병렬 | `{graph, sample_graph, graphs, datasources, virtual_nodes, virtual_relationships}` |

엔진의 SHOW 결과 열(DYL 문자열로 확인):
- `SHOW DATASOURCES`: `name, engine, host(options->>'host'), tables(외부 테이블 수)`, 이름순
- `SHOW TABLES FROM ds`: `table('스키마.테이블'), columns, virtual_node(여러 개면 ', '로 이어 붙임)`
- `SHOW COLUMNS FROM ds.t`: `column, type(format_type), nullable, key(가상 노드 KEY 컬럼인지)` — 원천의 기본키가 아니라 **매핑된 KEY** 여부
- `SHOW VIRTUAL NODES IN g`: `node, source('ds.t'), key, properties(속성 수), storage('virtual'|'materialized')`
- `SHOW VIRTUAL RELATIONSHIPS IN g`: `relationship, from('Type.prop'), to('Type.prop')`
- `SHOW GRAPHS`: `graph, types`

### 3.3 쓰기 (하나의 구조화 본문 → 하나의 패브릭 문장, WRITE 세션, 기본 그래프 'ontology' 세션에서 실행)
| 경로 | 줄 | 문장 |
|---|---|---|
| POST `/fabric/datasources` | 129–149, 206 | `CREATE DATASOURCE <name> WITH ENGINE = '<engine>', PARAMETERS = {k: $k, …}` — 값은 Bolt 파라미터, 표시용 `shown`은 password를 `'••••'`, port 숫자, 나머지 `'값'` |
| DELETE `/fabric/datasources/{ds}` | 150, 207 | `DROP DATASOURCE <ds>` |
| POST `/fabric/datasources/{ds}/refresh` | 151, 208 | `REFRESH DATASOURCE <ds>` |
| POST `/fabric/virtual-nodes` | 152–168, 209 | `CREATE VIRTUAL NODE <label> IN <graph> FROM <ds>.<table> KEY <key>[ PROPERTIES (col[ AS as], …)]` — properties가 있으면 KEY가 목록에 없을 때 맨 앞에 추가, `as`가 col과 같으면 생략 |
| DELETE `/fabric/virtual-nodes/{label}` | 169, 210 | `DROP VIRTUAL NODE <label> IN <graph>` |
| POST `/fabric/virtual-relationships` | 170–173, 211 | `CREATE VIRTUAL RELATIONSHIP <name> IN <graph> FROM <A>(<pa>) TO <B>(<pb>)` |
| DELETE `/fabric/virtual-relationships/{name}` | 174, 212 | `DROP VIRTUAL RELATIONSHIP <name> IN <graph>` |

- `graph` 기본값 = `sampleGraph`('sample') (117). 쿼리 `?graph=`도 받음(241).
- 엔진 정의(121–127): postgres {5432, schema 'public', 필수 host·database·user, 키 순서 host,port,database,schema,user,password}; mysql {3306, 필수 host·database·user, 키 host,port,database,user,password}; oracle {1521, 필수 host·service·schema·user, 키 host,port,service,schema,user,password}; sqlserver {1433, schema 'dbo', 필수 host·database·user, 키 host,port,database,schema,user,password}. 별칭 postgresql→postgres, mariadb→mysql, mssql→sqlserver. 빈 값 키는 빠짐(빈 password는 `''`로 포함).
- 검증 메시지(한국어, 400): `ident()`(43) 「<what> 은(는) 영문·숫자·밑줄만 쓸 수 있고 숫자로 시작할 수 없습니다: "<x>"」, `dsName()`(48) 「데이터소스 이름은 영문 소문자·숫자·밑줄만 쓸 수 있고 숫자로 시작할 수 없습니다: "<x>"」, 「지원하는 엔진: …」, 「이 설치에는 <e> 커넥터가 없습니다. 지금 쓸 수 있는 엔진: …」, 「<k> 를 입력하세요.」, 「포트는 1~65535 사이 정수여야 합니다.」. what 값: `데이터소스 이름`, `테이블 이름`, `노드 타입 이름`, `KEY 컬럼`, `컬럼 이름`, `속성 이름`, `그래프 이름`, `관계 이름`, `출발 노드`, `출발 속성`, `도착 노드`, `도착 속성`.
- `write()`(176–186): `dry`면 `{statement}`만. 실행 성공 `{statement, result: rows[0].result ?? rows[0] ?? null}`. 엔진 오류는 메시지 정리(`ERROR:` 앞부분과 `fabric statement:` 접두 제거) 후 **422** `{error, statement}`.
- 응답 공통(224–246): JSON `application/json; charset=utf-8`. 실패 `{error, statement?}` 상태 = e.status || 502. GET 미일치 404 `{error:'no route …'}`. 쓰기 경로 미일치 501 `{status:'error', type:'error', error:'이 패키지에서는 원천 DB에 임의 SQL을 보내지 않습니다. …'}`. 본문 10만 자 초과 413, JSON 아님 400.
- 호환 GET(189–197): `/api/datasources`, `/api/datasources/{ds}`, `/api/datasources/{ds}/health`, `/schemas`, `/tables`, `/tables/{t}/schema`, `/tables/{t}/sample?limit=10`, `/text2sql/meta/tables/{t}/columns?datasource=`, `/health` → `{status:'ok', engine:'ontological-fabric'}`.

## 4. Ontological 엔진 쪽 (확장 SQL·바이너리 문자열로 관찰)

- 카탈로그 테이블 `og_catalog.datasource(name PK, engine, server_name, options jsonb, created_at)` (EXT 402–408). 주석: "A datasource is a foreign server. Its credentials live in a user mapping, which only a superuser can read; this table records what is safe to show." (EXT 399–400)
- 원천 쓰기 차단 트리거 `og_refuse_source_write` (EXT 414–420): `datasource table %.% is read-only: the fabric does not write to source systems`, HINT `Write through the source system itself, or MATERIALIZE the node type and write to the copy.`
- 가상 관계 = 조인 술어 `og_catalog.virtual_rel(type_id, src_type, src_prop, dst_type, dst_prop)` (EXT 424–430)
- 가상 노드 매핑 `og_catalog.mapping(type_id, source_table, id_column, property_map, writable)` (EXT 385–391), 함수 `og_map_virtual(graph, type_name, datasource, remote, key_column, property_map)` (EXT 1932)
- 함수: `og_create_datasource(name, engine, params jsonb)` (EXT 1139), `og_drop_datasource` (1510), `og_refresh_datasource` (2000), `og_create_virtual_rel(graph, rel_name, src_type, src_prop, dst_type, dst_prop)` (1245), `og_drop_virtual` (1545), `og_materialize_mapping`.
- DYL 문자열: `CREATE SERVER …`, `CREATE USER MAPPING FOR PUBLIC SERVER … , password …`, `IMPORT FOREIGN SCHEMA …`(mysql: `OPTIONS (import_enum_as_text 'true')`, postgres: `OPTIONS (import_collate 'false')` 추정 짝), `failed to create user mapping for '…'`, `datasource parameter 'service' is required`, `unsupported datasource engine '…'`, `'…' cannot name a datasource: use lower-case letters, digits and '_', and not a system schema`, `'…' already holds local tables; choose another datasource name`, `… still backs virtual types (…)` / `…); replacing it would drop them. Drop those first, or materialize them`, `virtual relationships still join on '…' (…); drop them first`, `'…' is a virtual node type and read-only: its rows live in … . Write to the source system, or MATERIALIZE VIRTUAL NODE …`, `expected <datasource>.<table>, found '…'`, `expected NODES or RELATIONSHIPS after SHOW VIRTUAL`, `' is not a virtual node type`, `' is not a virtual relationship`, `virtual relationship (:%s)-[:%s]->(:%s) on %s.%s = %s.%s`(결과 문구 형식), `node %s materialized: %s rows copied, now stored and writable`, `-- CREATE DATASOURCE runs og_create_datasource(name, engine, parameters); the parameters are not shown`(EXPLAIN 류 출력 추정).
- 엔진 키워드 목록(DYL): `CREATE REFRESH MATERIALIZE EXPLAIN FABRIC DATASOURCE DATASOURCES TABLES COLUMNS VIRTUAL GRAPHS … KEY PROPERTIES RELATIONSHIPS`. 카탈로그 `engine` 주석에는 `mindsdb`도 있음.
- `SHOW COLUMNS`는 이 패키지가 Ontological에 덧붙인 것(SH fabric-bridge.js:99 주석 "patches/ontological").

## 5. 오류 번역표 (FE @88397, 정규식 → 화면 문장)
| 원문 패턴 | 화면 |
|---|---|
| `still backs virtual types \((…)\)` | 가상 노드 $1 이(가) 이 데이터소스를 읽고 있어 해제할 수 없습니다. 왼쪽 「가상 그래프」에서 그 노드를 먼저 지우세요. |
| `backs virtual types \((…)\); replacing` | 가상 노드 $1 이(가) 같은 이름의 데이터소스를 읽고 있습니다. 다른 이름을 쓰세요. |
| `cannot name a datasource` | 데이터소스 이름은 영문 소문자·숫자·밑줄만 쓸 수 있고, 시스템 스키마 이름은 쓸 수 없습니다. |
| `already holds local tables|already exists`(i) | 같은 이름이 이미 있습니다. 다른 이름을 쓰세요. |
| `password authentication failed|no password supplied|Access denied for user|ORA-01017|Login failed for user`(i) | 원천 DB 인증에 실패했습니다. 사용자와 비밀번호를 확인하세요. |
| `could not connect|connection refused|could not translate host name|timeout expired|Can't connect to|Unknown MySQL server host|ORA-12541|ORA-12170|Unable to connect|DB-Library error`(i) | 원천 DB 에 접속하지 못했습니다. 호스트와 포트를 확인하세요. |
| `ORA-12514|listener does not currently know of service`(i) | Oracle 리스너가 그 서비스 이름을 모릅니다. 서비스 이름(예: FREEPDB1)을 확인하세요. |
| `Unknown database '(…)'` / `database "(…)" does not exist` | 원천에 데이터베이스 $1 이(가) 없습니다. |
| `certificate verify failed|self[- ]signed certificate|TLS/SSL error`(i) | 원천 DB 의 TLS 인증서를 확인하지 못했습니다. 서버 인증서(자체 서명 여부)를 확인하세요. |
| `schema "(…)" is not present|schema "(…)" does not exist` | 원천에 스키마 $1 이(가) 없습니다. |
| `has no declared property '(…)'` | 노드에 $1 속성이 없습니다. 관계는 노드의 속성으로 잇습니다. |
| `'(…)' is not a column of` | $1 은(는) 이 테이블의 컬럼이 아닙니다. |
| `virtual relationships still join on '(…)' \((…)\)` | 관계 $2 이(가) $1 노드를 잇고 있어 지울 수 없습니다. 관계를 먼저 지우세요. |

## 6. Python 백엔드와의 관계 (이 화면 밖)
- BE shared/kernel/settings.py:202–214: `DATASOURCE_ENABLED`(기본 true), `DATAFABRIC_BASE_URL`(기본 :8004), `DATAFABRIC_TIMEOUT_SECONDS`(20), `DATAFABRIC_CATALOG_TTL_SECONDS`(300), `TEXT2SQL_BASE_URL`(끝의 `/text2sql` 제거), `DATASOURCE_MAX_ROWS`(500) 등.
- SH main/services.js:119, 137–139: 셸이 Studio 백엔드에 `DATAFABRIC_BASE_URL = TEXT2SQL_BASE_URL = http://127.0.0.1:<web>/fabric-bridge` 주입(사용자 studio.env로 덮어쓸 수 없음).
- BE modules/ontology/datasource_api.py:43–117: `GET /api/datasources/health`, `/api/datasources?source=&refresh=`, `/{name}/schemas`, `/{name}/tables?schema=`, `/{name}/tables/{t}/columns?schema=`, `/{name}/tables/{t}/sample?limit=` → datafabric_client(캐시 TTL, `safe_call`로 실패 시 `{degraded…}`) → 브리지 호환 GET(§3.2 끝). 컬럼은 먼저 `/text2sql/meta/tables/{t}/columns?datasource=` → 실패 시 `/api/datasources/{ds}/tables/{t}/schema?source=mindsdb` (datafabric_client.py:270–297).
- 소비자: FE @2275771 (구축 브리프의 데이터소스 선택 — M1), MCP 도구(A3). 같은 파일의 클래스 바인딩·behavior·reverse-bind·causal·publish 라우트(datasource_api.py:142–604)는 M1 범위.
- datasource_exec.py:533–566 `run_direct_sql` → `<TEXT2SQL>/text2sql/direct-sql` POST → 브리지는 POST 미일치 **501**(임의 SQL 불가). datasource_exec.py:745–770 `run_mindsdb_statement` → `/api/query` POST → 역시 501. 즉 이 패키지에서 SQL 직접 실행 경로는 막혀 있음(관찰). M1/M2 분석에서 영향 확인 필요.

## 7. 예제 데이터 시드·재등록 (셸)
- SH main/postgres.js:19–29 `secrets.json`(userData, 모드 0600): `pgPassword`(슈퍼유저 og), `fabricPassword`(읽기 전용 역할 fabric_ro) 무작위 생성.
- postgres.js:104–129 첫 실행: DB `ogstudio` + 확장 `ontological`, `postgres_fdw`, 그래프 `ontology` + 추상 타입 `_Entity`; DB `sample`에 `resources/sample/sample.sql` 적재; `ALTER ROLE fabric_ro PASSWORD …`.
- SH main/services.js:244–271 `seedFabric`: `resources/sample/fabric.cypher`(23줄)의 문장을 Bolt로 순서대로 실행, 파라미터 `$pw`(fabricPassword), `$port`(PG 포트). `already exists`는 건너뜀. 표식 파일 `.ontology-lite-fabric`, `.ontology-lite-fabric-sample-graph`(데이터 폴더).
- fabric.cypher:8–23: 데이터소스 erp/wms/crm(host 127.0.0.1, database 'sample', schema 각 이름, user fabric_ro), `CREATE GRAPH sample`, 가상 노드 7개, 관계 5개(ORDERED_FROM PurchaseOrder(supplier_id)→Supplier(supplier_id), SHIPS Shipment(ref_po_no)→PurchaseOrder(po_id), PLACED_BY SalesOrder(cust_no)→Customer(cust_no), FOR_ITEM SalesOrder(sku_code)→Item(item_id), ABOUT Claim(so_no)→SalesOrder(so_no)).
- services.js:280–308 `repointFabric`/`resetSampleFabric`: PG 포트가 바뀌었거나(`.ontology-lite-fabric-port`) 예제 업무 DB 스키마가 바뀌면(index.js:146) 예제 가상 타입·데이터소스를 지우고 다시 시드. 주석: "a foreign table keeps the columns it was imported with, and REFRESH DATASOURCE only picks up new tables."
- services.js:218–221 주석: 예제 가상 타입은 `sample` 그래프에 둠(Studio 그래프 `ontology`의 클래스와 이름 충돌 방지). 데이터소스는 전역.

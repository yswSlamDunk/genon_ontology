# M3 데이터소스 — 설계 문서

- 기준: Ontological Studio 0.1.1 관찰 결과(정적 분석). 클린룸 문서(ADR-0002, 0011): 원본 코드·파일 경로·내부 식별자를 담지 않는다. 화면 문구·API 경로·필드 이름·패브릭 문장 문법은 외부에서 관찰 가능한 계약이라 적는다.
- 상태: 초안 v1 (정적 분석). "모르는 점"은 4단계 실행 기록에서 확정한다.

## 1. 목적
원천 업무 DB(PostgreSQL, MySQL/MariaDB, Oracle, SQL Server)를 **데이터를 복사하지 않고** 그래프 DB(Ontological)의 데이터 패브릭에 연결하고, 원천 테이블을 **가상 노드 타입**(행 1개 = 노드 1개)으로, 테이블 간 조인 규칙을 **가상 관계**로 노출하는 화면. 화면의 모든 변경은 그래프 DB의 **패브릭 문장** 한 개로 실행되고, 실행 전 문장을 미리 보여 주며, 실행한 문장을 기록으로 남긴다.

## 2. 사용자 시나리오 (요약)
`user-scenarios.md` S1–S12 참조.
- S1 탭 열기와 구성 보기 · S2 테이블 구조·미리보기 · S3 데이터소스 연결 · S4 실행한 문장 · S5 테이블 다시 읽기·연결 해제(사용 중이면 거절)
- S6 가상 노드로 노출 · S7 가상 그래프 지도 · S8 가상 관계 만들기 · S9 관계·노드 삭제(의존 시 거절)
- S10 테이블 찾기 · S11 홈에서 특정 데이터소스로 바로 열기 · S12 미리보기 문장 복사·포털 이동

## 3. 구성 요소와 통신

```
[Studio 화면: 데이터소스 뷰] --HTTP JSON--> [로컬 웹 오리진의 패브릭 브리지 /fabric-bridge/fabric/*]
                                               --Bolt(그래프 DB 드라이버)--> [Ontological 그래프 DB]
                                                                               --FDW 외부 서버/외부 테이블--> [원천 DB]
```
- 브리지는 앱 셸(데스크톱 메인 프로세스)이 같은 로컬 오리진(127.0.0.1)에서 제공한다. Python 백엔드는 이 화면에 관여하지 않는다.
- 브리지는 그래프 DB에 **패브릭 문장만** 보낸다(내부 SQL 금지). 원천에 임의 SQL을 보내는 기능은 제공하지 않는다.
- 브리지는 그래프 DB 관리자 계정(설치 시 생성된 비밀번호)으로 접속한다. 인증은 없고 로컬 바인딩에만 의존한다.
- 화면 쓰기 요청 하나 = 구조화된 JSON 본문 하나 = 패브릭 문장 하나. 응답에 그 문장(표시용)을 돌려준다. `dry: true`면 실행 없이 문장만 돌려준다.

## 4. 패브릭 문장 (그래프 DB가 제공하는 계약)

| 문장 | 하는 일 | 결과 열 |
|---|---|---|
| `SHOW DATASOURCES` | 데이터소스 목록(이름순) | `name, engine, host, tables` |
| `SHOW TABLES FROM <ds>` | 데이터소스의 외부 테이블 | `table`(`ds.table`), `columns`(수), `virtual_node`(노출한 노드 타입 이름, 여러 개면 `, `로 연결, 없으면 null) |
| `SHOW COLUMNS FROM <ds>.<table>` | 컬럼 | `column, type, nullable, key`(가상 노드 KEY로 쓰이는 컬럼인지 — 원천 기본키가 아님) |
| `SHOW GRAPHS` | 그래프 목록 | `graph, types` |
| `SHOW VIRTUAL NODES IN <g>` | 그래프의 가상 노드 타입 | `node, source`(`ds.table`), `key, properties`(속성 수), `storage`(`virtual`/`materialized`) |
| `SHOW VIRTUAL RELATIONSHIPS IN <g>` | 그래프의 가상 관계 | `relationship, from`(`Type.prop`), `to`(`Type.prop`) |
| `CREATE DATASOURCE <ds> WITH ENGINE = '<engine>', PARAMETERS = {host:…, port:…, database:…, service:…, schema:…, user:…, password:…}` | 원천 연결: 외부 서버·사용자 매핑 생성, 원천 스키마의 테이블을 `<ds>` 스키마로 외부 테이블 가져오기 | `result`(문구) |
| `REFRESH DATASOURCE <ds>` | 원천에 새로 생긴 테이블 가져오기(기존 테이블 컬럼 변경은 반영 안 됨 — 추정) | `result` |
| `DROP DATASOURCE <ds>` | 연결 해제. 가상 노드가 사용 중이면 거절 | `result` |
| `CREATE VIRTUAL NODE <Label> IN <g> FROM <ds>.<table> KEY <col> [PROPERTIES (c1, c2 AS p2, …)]` | 가상 노드 타입. KEY는 컬럼 1개만. PROPERTIES 생략 시 모든 컬럼이 같은 이름 속성 | `result` |
| `DROP VIRTUAL NODE <Label> IN <g>` | 가상 노드 타입 삭제. 관계가 이어져 있으면 거절 | `result` |
| `CREATE VIRTUAL RELATIONSHIP <REL> IN <g> FROM <A>(<pa>) TO <B>(<pb>)` | `A.pa = B.pb`인 행끼리 잇는 조인 규칙 | `result` |
| `DROP VIRTUAL RELATIONSHIP <REL> IN <g>` | 관계 삭제 | `result` |
| (참고, 화면 없음) `MATERIALIZE VIRTUAL NODE <Label>`, `EXPLAIN FABRIC MATCH …`, `CREATE GRAPH <g>` | 사본 생성·실행 계획·그래프 생성 | |

규칙(엔진):
- 데이터소스 이름은 그래프 DB 안의 스키마 이름이 된다: 영문 소문자·숫자·밑줄, 시스템 스키마 이름 불가, 이미 로컬 테이블이 있는 스키마 이름 불가.
- 데이터소스는 **전역**, 가상 노드·관계는 **그래프별**.
- 가상 노드는 **읽기 전용**: 쓰기(CREATE/SET) 시 `'<Label>' is a virtual node type and read-only: its rows live in "<ds>"."<table>". Write to the source system, or MATERIALIZE VIRTUAL NODE <Label> to take a copy`. 외부 테이블 자체에도 쓰기 거절 트리거(`datasource table <s>.<t> is read-only: …`).
- 미리보기·질의는 매번 원천을 읽는다(복사 없음). 물리화하면 복사본이 되어 원천 변경이 반영되지 않는다.
- 주요 엔진 오류 문구: `… still backs virtual types (A, B)`(해제 거절), `virtual relationships still join on 'X' (R1, R2); drop them first`(노드 삭제 거절), `… has no declared property '…'`, `'…' is not a column of …`, `expected the key column`, `'…' cannot name a datasource: …`, `'…' already holds local tables; choose another datasource name`, `datasource parameter 'service' is required`, `unsupported datasource engine '…'`.

## 5. 화면 구성과 상호작용

### 5.1 레이아웃 (3단)
- **왼쪽 사이드바**
  - 머리: 제목 `Data fabric`, 「＋」(title 「데이터소스 연결」) → 연결 대화상자
  - `그래프 <Studio 그래프 이름> · Ontological`
  - 「데이터소스 N」 목록: 항목 = 이름 + 엔진 태그, 아랫줄 `<host> · 테이블 <table_count> · 노드 <이 데이터소스를 원천으로 하는 가상 노드 수(모든 그래프)>`. 로딩 중 「불러오는 중…」, 비어 있으면 「연결된 데이터소스가 없습니다.」 + 「연결하기」
  - 「가상 그래프」 목록: 순서 = 예제 그래프, Studio 그래프(존재할 때) 뒤에 나머지 전부(중복 제거). 태그: Studio 그래프 「Studio」, 예제 그래프 「예제」. 아랫줄 `노드 n · 관계 m`
  - 하단: 「데이터는 복사하지 않습니다. 가상 노드는 질의할 때마다 원천을 그 자리에서 읽습니다.」 + 「Ontological Portal 에서 질의」(포털 탭 열기)
- **본문**: 선택 종류에 따라 데이터소스 뷰 / 가상 그래프 뷰 / 빈 상태(「왼쪽에서 데이터소스를 고르세요.」)
- **하단 「실행한 문장」 막대**: 기록이 1건 이상일 때만 표시
- 상단 오류(개요 읽기 실패): 「패브릭 정보를 읽지 못했습니다: <원문>」 + 「다시 시도」

### 5.2 첫 진입
1. 개요 조회. 2. 화면 주소의 `ds` 쿼리 값이 실제 데이터소스면 그것을, 아니면 목록 첫 데이터소스를 선택. 3. 테이블 목록 → 첫 테이블 선택 → 컬럼 → (가상 노드면) 미리보기.

### 5.3 데이터소스 뷰
- 머리: 작은 제목 `Datasource`, 이름 + 엔진 태그, `<host> · 테이블 <n> · 가상 노드 <m>`.
- 동작 버튼: 「테이블 다시 읽기」(title 「REFRESH DATASOURCE — 원천에 새로 생긴 테이블을 가져옵니다」), 「연결 해제」.
- **확인 버튼 패턴**(삭제류 공통): 첫 클릭 → 그 자리에 실행될 문장(강조) + 확인 버튼(「해제」 또는 「삭제」) + 「취소」.
- 오류 배너: 한국어 번역(§9)이 있으면 굵게 + 원문을 코드로, 없으면 원문만. 닫기 버튼.
- **가운데 테이블 목록**: 「테이블 찾기」 입력(화면 내 필터, 테이블 이름 또는 노드 이름 부분 일치, 대소문자 무시). 항목 = 테이블 이름, 컬럼 수, 가상 노드면 칩 `:Label`(title `가상 노드 :Label`). 로딩 「불러오는 중…」.
- **오른쪽 상세** (테이블 미선택 시 「왼쪽에서 테이블을 고르세요.」)
  - 구조 카드: `ds.table` + 「가상 노드 :Label」 칩 또는 「노출 안 됨」. 표 `컬럼 | 타입 | 제약(NOT NULL 또는 빈칸) | KEY 표시(title 「가상 노드의 KEY」)`. 로딩 「컬럼을 읽는 중…」.
  - 가상 노드인 경우 **미리보기 카드**: 라벨 「미리보기」, 문장 `MATCH (n:<Label>) RETURN n LIMIT 20`, 「그래프 <g>」 태그, 「문장 복사」(클립보드), 「노출 해제」(확인: `DROP VIRTUAL NODE <Label> IN <g>`). 표: 열은 컬럼 표 순서로 정렬(모르는 열은 뒤로), null은 `null`로 표시, 숫자/문자/null에 다른 스타일. 로딩 「원천을 읽는 중…」, 0행이면 응답의 `note` 또는 「행이 없습니다.」. 바닥 `<행수>행 · Bolt → Ontological → <커넥터> → 원천` (커넥터: postgres→`postgres_fdw`, mysql/mariadb→`mysql_fdw`, oracle→`oracle_fdw`, sqlserver→`tds_fdw`). 한 테이블에 노드가 여럿이면 첫 노드 기준.
  - 노출 안 된 경우 **「가상 노드로 노출」 카드**: 안내 「원천 행 하나가 노드 하나가 됩니다. 데이터는 복사하지 않습니다.」
    - 노드 타입 이름(기본: 테이블 이름을 영숫자 외 문자로 쪼개 각 조각 첫 글자를 대문자로 이어 붙임, 숫자로 시작하면 앞에 `T`)
    - 그래프 선택(기본: 이 데이터소스의 기존 가상 노드가 있는 그래프 → 예제 그래프 → Studio 그래프)
    - KEY 컬럼 선택(기본 추정: KEY 표시된 컬럼 → NOT NULL이면서 이름이 `id` 또는 `_id`·`_no`·`_code`·`_key`로 끝남 → 첫 NOT NULL → 첫 컬럼)
    - 속성 목록: 컬럼마다 체크박스 + `컬럼 → 속성이름` 입력(기본 모두 켜짐, 같은 이름). KEY 컬럼 체크는 끌 수 없음. 꺼진 행은 이름 칸 비활성. 안내 「고르지 않으면 모든 컬럼이 같은 이름의 속성이 됩니다.」
    - 「실행될 문장」 미리보기(§5.6), 「가상 노드 만들기」(문장이 준비되고 진행 중이 아닐 때만 활성)
    - 요청 본문: 모두 켜져 있고 이름이 그대로면 `properties: []`(PROPERTIES 생략), 아니면 켜진 컬럼(+KEY)을 `{column, as}`로.

### 5.4 가상 그래프 뷰
- 머리: 작은 제목 `Virtual graph`, 그래프 이름 + 「그래프」 태그, 「가상 노드 n, 관계 m. 관계는 두 노드의 속성 값이 같은 행끼리 잇습니다.」
- **지도 카드**(노드가 있을 때): 「지도」 + 「열 = 데이터소스. 노드를 누르면 원천 테이블로 갑니다.」. SVG, 가로 1000 단위, 데이터소스 이름순 열, 열 머리에 데이터소스 이름과 구분선, 노드 상자(노드 이름, `테이블 · KEY`)를 위에서부터 58 간격. 관계는 출발→도착 화살표 곡선 + 이름표(같은 열끼리는 오른쪽으로 휘는 곡선, 이름표 겹치면 아래로 비킴). 노드 클릭 → 해당 데이터소스·테이블 상세로 이동.
- **노드 타입 카드**: 표 `노드(:Label 칩) | 원천(클릭 시 테이블로 이동) | KEY | 속성(수) | 저장(「가상」 또는 「물리화」 경고 태그) | 삭제`. 비면 「이 그래프에는 가상 노드가 없습니다. 데이터소스의 테이블에서 만드세요.」
- **관계 카드**: 표 `관계([:REL]) | 출발(Type.prop) | → | 도착 | 삭제`. 비면 「관계가 없습니다.」
- **「관계 만들기」 카드**: 안내 「출발 노드의 속성 값이 도착 노드의 속성 값과 같은 행끼리 이어집니다.」 입력: 관계 이름(placeholder `SUPPLIES`), 출발 노드(이 그래프의 노드), 속성, →, 도착 노드, 속성. 속성 선택지는 노드의 실제 속성 이름(그 노드 원천 테이블 미리보기 1행의 열, 없으면 컬럼 이름). 노드를 바꾸면 속성 자동 선택: 출발 쪽은 도착 노드의 KEY 이름이 있으면 그것, 도착 쪽은 자기 KEY; 없으면 양쪽 공통 이름, 없으면 첫 속성. 「실행될 문장」 미리보기, 「관계 만들기」. 성공 시 관계 이름 칸만 비움.

### 5.5 데이터소스 연결 대화상자
- 작은 제목 `CREATE DATASOURCE`, 제목 「데이터소스 연결」, 닫기 버튼. 배경 클릭·Esc로 닫힘.
- 설명: 「원천 스키마의 테이블을 외부 테이블로 들여옵니다(<커넥터>). 행은 복사하지 않습니다 — 가상 노드로 노출한 뒤 질의할 때 읽습니다.」
- 항목(2열 격자):
  - 이름(전체 폭) + 「패브릭에서 스키마 이름이 됩니다 (영문 소문자·숫자·밑줄)」, placeholder `sales`
  - 엔진: `PostgreSQL` / `MySQL · MariaDB` / `Oracle` / `SQL Server · Azure SQL`. 이 설치에 없는 엔진은 「— 이 설치에 없음」 붙이고 비활성(서버의 엔진 목록 기준)
  - 스키마: MySQL은 칸 없음. 힌트 Oracle 「소유자, 보통 대문자 (예: HR)」. placeholder는 엔진 기본값
  - 호스트, 포트(숫자 1–65535)
  - DB(전체 폭): PostgreSQL·SQL Server 「데이터베이스」, MySQL 「데이터베이스 (MySQL 에서는 이것이 스키마)」, Oracle 「서비스 이름」(placeholder `FREEPDB1 · ORCLPDB1 …`, 값은 `service` 필드)
  - 사용자(자동완성 끔), 비밀번호(password 입력, 자동완성 new-password)
- 기본값: 엔진 postgres, 호스트 `127.0.0.1`, 포트 5432, 스키마 `public`. 엔진 변경 시 포트·스키마를 엔진 기본값으로(postgres 5432/`public`, mysql 3306/없음, oracle 1521/빈칸, sqlserver 1433/`dbo`).
- 필수: 이름·호스트·DB(또는 서비스)·사용자, Oracle은 스키마도. 미충족이면 문장 미리보기 없음·「연결」 비활성.
- 「실행될 문장」 미리보기, 하단 오류(번역 적용, title에 원문), 「취소」, 「연결」.
- 성공: 대화상자 닫기 → 개요 다시 읽기 → 새 데이터소스 선택. 실패: 대화상자 유지 + 오류.

### 5.6 「실행될 문장」 미리보기 (공통)
- 폼 값이 바뀔 때마다 180ms 디바운스 후 해당 쓰기 API에 `dry: true`를 붙여 POST. 응답 `statement`를 강조 표시, 오류면 오류 문구(입력 검증 메시지)를 표시. 늦게 도착한 이전 응답은 버림. 폼이 미완성이면 「…」.
- 강조: 작은따옴표 리터럴, 키워드(CREATE, DROP, REFRESH, DATASOURCE, WITH, ENGINE, PARAMETERS, VIRTUAL, NODE, RELATIONSHIP, FROM, TO, KEY, PROPERTIES, AS, MATCH, RETURN, LIMIT, SHOW, TABLES, COLUMNS). HTML 이스케이프 필수.
- 비밀번호는 표시 문장에서 항상 `'••••'`.

### 5.7 「실행한 문장」
- 쓰기 작업 결과만 기록(읽기 문장은 기록 안 함). 최신이 위, 최대 30건, 메모리에만(탭 새로 고침 시 사라짐).
- 접힌 막대: 「실행한 문장」 + 건수 + 마지막 항목 `✓ <결과>` 또는 `✕ <오류>`. 펼치면 목록(문장 강조 + 결과/오류, 실패 행 강조).
- 성공 결과는 엔진의 `result` 문구, 없으면 「완료」. 실패 시 문장은 서버가 돌려준 표시 문장, 없으면 `<METHOD> <path>`.

### 5.8 쓰기 후 갱신
- 성공한 쓰기 뒤 개요를 다시 읽고 노드 속성 캐시를 비우며, 데이터소스 뷰면 테이블 목록·선택 테이블을 다시 읽는다.
- 연결 해제 성공 시 선택을 비우고 첫 진입 절차를 다시 탄다.
- 쓰기 진행 중에는 모든 쓰기 버튼 비활성.
- 다른 곳(포털 등)에서 바뀐 내용은 자동 반영하지 않는다(다음 쓰기나 재진입 때 반영).

### 5.9 홈 연동
- 홈 「최근 항목」에 데이터소스마다 행: 종류 「데이터소스」, 설명 `<engine> · 테이블 <n> · 노드 <m>`, 날짜 없음. 누르면 데이터소스 탭을 해당 데이터소스 선택 상태로 연다(주소에 `ds=<name>`).
- 홈 카드: 「데이터소스」 / 「원천 DB 를 연결하고 가상 노드로 노출합니다.」

## 6. API 명세 (브리지, 기준 경로 `/fabric-bridge/fabric`)
모든 응답 `application/json; charset=utf-8`. 오류 본문 `{ "error": string, "statement"?: string }`.

| 메서드 | 경로 | 요청 | 성공 응답 |
|---|---|---|---|
| GET | `/overview` | — | `{graph, sample_graph, graphs: string[], datasources: Datasource[], virtual_nodes: VirtualNode[], virtual_relationships: VirtualRel[]}` |
| GET | `/engines` | — | `{engines: string[]}` (설치된 커넥터가 있는 엔진: `postgres`,`mysql`,`oracle`,`sqlserver` 중) |
| GET | `/datasources/{ds}/tables` | — | `{tables: Table[]}` |
| GET | `/datasources/{ds}/tables/{t}/columns` | — | `{columns: Column[]}` |
| GET | `/datasources/{ds}/tables/{t}/preview?limit=20` | limit 1–200(기본 20) | `{columns: string[], rows: any[][], virtual_node, graph}` 또는 가상 노드 없을 때 `{columns:[], rows:[], note}` |
| POST | `/datasources` | `{name, engine, host, port?, database?, service?, schema?, user, password?, dry?}` | `{statement, result}` / dry: `{statement}` |
| POST | `/datasources/{ds}/refresh` | `{dry?}` | 같음 |
| DELETE | `/datasources/{ds}` | `{dry?}` | 같음 |
| POST | `/virtual-nodes` | `{label, graph?, source: "ds.table", key, properties?: (string | {column, as?})[], dry?}` | 같음 |
| DELETE | `/virtual-nodes/{label}` | `{graph?, dry?}` | 같음 |
| POST | `/virtual-relationships` | `{name, graph?, from:{node, property}, to:{node, property}, dry?}` | 같음 |
| DELETE | `/virtual-relationships/{name}` | `{graph?, dry?}` | 같음 |

- `graph` 생략 시 예제 그래프(`sample`). 쿼리 `?graph=`로도 지정 가능(본문 우선).
- 경로 조각은 URL 디코딩. DELETE도 JSON 본문을 받는다.
- 상태 코드: 입력 검증 실패 400(한국어 메시지), 테이블 없음 404, 엔진 거절 **422**(`error`=정리된 엔진 메시지, `statement`=표시 문장), 기타 502, 본문 과대(10만 자) 413, 정의 안 된 GET 404 `{error: "no route <path>"}`, 정의 안 된 쓰기 501(「이 패키지에서는 원천 DB에 임의 SQL을 보내지 않습니다. Ontological 데이터 패브릭의 가상 노드(Cypher)로 조회하세요.」).
- 입력 검증: 식별자 `^[A-Za-z_][A-Za-z0-9_]*$`(메시지 「<항목> 은(는) 영문·숫자·밑줄만 쓸 수 있고 숫자로 시작할 수 없습니다: "<값>"」), 데이터소스 이름(생성 시) `^[a-z_][a-z0-9_]*$`(「데이터소스 이름은 영문 소문자·숫자·밑줄만 쓸 수 있고 숫자로 시작할 수 없습니다: "<값>"」), 엔진 별칭(postgresql→postgres, mariadb→mysql, mssql→sqlserver) 외 「지원하는 엔진: …」, 설치 안 된 엔진 「이 설치에는 <e> 커넥터가 없습니다. 지금 쓸 수 있는 엔진: …」, 필수 값 「<키> 를 입력하세요.」(postgres/mysql/sqlserver: host·database·user, oracle: host·service·schema·user), 포트 「포트는 1~65535 사이 정수여야 합니다.」(생략 시 엔진 기본 포트).
- CREATE DATASOURCE 문장 조립: 엔진별 키 순서(postgres·sqlserver: host, port, database, schema, user, password / mysql: host, port, database, user, password / oracle: host, port, service, schema, user, password), 빈 값은 생략(비밀번호는 빈 문자열로라도 포함), 스키마 생략 시 엔진 기본값. **실행 문장은 값을 드라이버 파라미터로 전달**하고, 표시 문장은 값을 따옴표 리터럴로(포트는 숫자, 비밀번호는 `'••••'`).
- 가상 노드 문장: properties가 있으면 KEY 컬럼이 목록에 없을 때 맨 앞에 넣고, `as`가 컬럼명과 같으면 `AS` 생략.
- 미리보기 실행: 테이블에 가상 노드가 있으면 그 노드가 속한 그래프에서 `MATCH (n:<Label>) RETURN n LIMIT <limit>`, 노드 속성에서 내부 식별 속성(`_id`, `_type`) 제거, 첫 행의 키 순서로 열 구성.
- 컬럼: 엔진이 `SHOW COLUMNS`를 모르면(구버전) 미리보기 1행으로 타입 추정(정수/소수/불리언/`YYYY-MM-DD` 날짜/텍스트/unknown).

### 호환 엔드포인트 (다른 메뉴·에이전트용, 같은 브리지, 기준 경로 `/fabric-bridge`)
`GET /api/datasources` → `{datasources: Datasource[]}`, `GET /api/datasources/{ds}`, `/health` → `{status:'ok', datasource}`, `/schemas` → `{schemas:[{name: ds, description:'', table_count}]}`, `/tables` → `{tables}`, `/tables/{t}/schema` → `{columns}`, `/tables/{t}/sample?limit=10` → 미리보기 형식, `GET /text2sql/meta/tables/{t}/columns?datasource=` → `{columns}`, `GET /health` → `{status:'ok', engine:'ontological-fabric'}`. Studio 백엔드의 `/api/datasources*` 카탈로그 프록시(M1)가 이것을 쓴다.

## 7. 데이터 모델 (화면·API)
- **Datasource** `{name, engine, display_name(=name), database(=name), host, table_count}`
- **Table** `{name(데이터소스 접두 제거), schema(=ds), column_count, virtual_node: string|null, description('가상 노드 :X' 또는 '')}`
- **Column** `{name, type, nullable: bool, primary_key: bool(=가상 노드 KEY 컬럼 여부), description: ''}`
- **VirtualNode** `{node, source:'ds.table', key, properties: number, storage:'virtual'|'materialized', graph}`
- **VirtualRel** `{relationship, from:'Type.prop', to:'Type.prop', graph}`
- **로그 항목**(화면 메모리) `{statement, ok, result | error}`

## 8. 상태·저장
- 화면 상태(선택, 폼, 실행 로그)는 모두 메모리. 브라우저 저장소 사용 없음.
- 영구 상태는 그래프 DB 안에만 있다:
  - 데이터소스 카탈로그(이름, 엔진, 외부 서버 이름, 표시용 옵션 jsonb, 생성 시각). 표시용 옵션에는 host 등이 들어간다.
  - 외부 서버(커넥터별 FDW) + **사용자 매핑**(사용자·비밀번호). 엔진 설계상 비밀번호는 사용자 매핑에만 있고 관리자만 읽을 수 있다. 즉 비밀번호는 그래프 DB를 담은 PostgreSQL 카탈로그에 평문 옵션으로 저장된다(PostgreSQL FDW 일반 동작 — 암호화 계층 없음).
  - 원천 스키마의 외부 테이블들(데이터소스 이름 = 로컬 스키마 이름), 각 외부 테이블에 쓰기 거절 트리거.
  - 가상 노드 매핑(타입 ↔ 원천 테이블, KEY 컬럼, 속성 이름 매핑), 가상 관계(조인 술어: 출발 타입·속성, 도착 타입·속성).
- 앱 데이터 폴더에는 그래프 DB 관리자 비밀번호와 예제용 읽기 전용 계정 비밀번호가 담긴 비밀 파일(소유자만 읽기, 0600)이 있다. 사용자가 연결한 원천의 비밀번호는 이 파일에 저장하지 않는다.
- 비밀번호는 화면·응답·로그에 노출되지 않는다(표시 문장 마스킹). 단 생성 요청 본문에는 평문으로 실려 로컬 브리지로 간다.
- **예제 시드**(첫 실행): 같은 PostgreSQL의 예제 DB(스키마 erp/wms/crm)를 읽기 전용 계정으로 데이터소스 3개로 연결, 그래프 `sample` 생성, 가상 노드 7개(Supplier←erp.supplier KEY supplier_id, Item←erp.item KEY item_id, PurchaseOrder←erp.purchase_order KEY po_id, Shipment←wms.shipment KEY shipment_no, Customer←crm.customer KEY cust_no, SalesOrder←crm.sales_order KEY so_no, Claim←crm.claim KEY ticket_no)와 관계 5개(ORDERED_FROM PurchaseOrder(supplier_id)→Supplier(supplier_id), SHIPS Shipment(ref_po_no)→PurchaseOrder(po_id), PLACED_BY SalesOrder(cust_no)→Customer(cust_no), FOR_ITEM SalesOrder(sku_code)→Item(item_id), ABOUT Claim(so_no)→SalesOrder(so_no)). 이미 있으면 건너뜀. 완료 표식 파일로 한 번만.
- **재시드**: PostgreSQL 포트가 바뀌었거나 예제 DB 테이블 구조가 바뀌면 예제 가상 타입·데이터소스를 지우고 다시 시드(외부 테이블은 가져올 때의 컬럼을 유지하고 REFRESH는 새 테이블만 가져오므로).
- 그래프 이름: Studio가 온톨로지를 만드는 그래프 `ontology`, 예제 가상 타입 그래프 `sample`(이름 충돌 방지를 위해 분리).

## 9. 오류·예외 (화면 번역표)
엔진 원문에 아래 패턴이 있으면 한국어 문장을 굵게 보이고 원문을 아래에 둔다. 순서대로 첫 일치.
1. `still backs virtual types (X)` → 「가상 노드 X 이(가) 이 데이터소스를 읽고 있어 해제할 수 없습니다. 왼쪽 「가상 그래프」에서 그 노드를 먼저 지우세요.」
2. `backs virtual types (X); replacing` → 「가상 노드 X 이(가) 같은 이름의 데이터소스를 읽고 있습니다. 다른 이름을 쓰세요.」
3. `cannot name a datasource` → 「데이터소스 이름은 영문 소문자·숫자·밑줄만 쓸 수 있고, 시스템 스키마 이름은 쓸 수 없습니다.」
4. `already holds local tables` 또는 `already exists`(대소문자 무시) → 「같은 이름이 이미 있습니다. 다른 이름을 쓰세요.」
5. 인증 실패(`password authentication failed`, `no password supplied`, `Access denied for user`, `ORA-01017`, `Login failed for user`) → 「원천 DB 인증에 실패했습니다. 사용자와 비밀번호를 확인하세요.」
6. 접속 실패(`could not connect`, `connection refused`, `could not translate host name`, `timeout expired`, `Can't connect to`, `Unknown MySQL server host`, `ORA-12541`, `ORA-12170`, `Unable to connect`, `DB-Library error`) → 「원천 DB 에 접속하지 못했습니다. 호스트와 포트를 확인하세요.」
7. `ORA-12514` / `listener does not currently know of service` → 「Oracle 리스너가 그 서비스 이름을 모릅니다. 서비스 이름(예: FREEPDB1)을 확인하세요.」
8. `Unknown database 'X'` → 「원천에 데이터베이스 X 이(가) 없습니다.」
9. TLS(`certificate verify failed`, `self signed certificate`, `TLS/SSL error`) → 「원천 DB 의 TLS 인증서를 확인하지 못했습니다. 서버 인증서(자체 서명 여부)를 확인하세요.」
10. `database "X" does not exist` → 「원천에 데이터베이스 X 이(가) 없습니다.」
11. `schema "X" is not present` / `schema "X" does not exist` → 「원천에 스키마 X 이(가) 없습니다.」
12. `has no declared property 'X'` → 「노드에 X 속성이 없습니다. 관계는 노드의 속성으로 잇습니다.」
13. `'X' is not a column of` → 「X 은(는) 이 테이블의 컬럼이 아닙니다.」
14. `virtual relationships still join on 'N' (R)` → 「관계 R 이(가) N 노드를 잇고 있어 지울 수 없습니다. 관계를 먼저 지우세요.」

기타: 개요 실패는 상단 오류 + 「다시 시도」. 테이블 목록 실패는 목록 비우고 상단 오류. 컬럼 실패는 배너. 미리보기 실패는 미리보기 자리에 오류 문구.

## 10. 다른 기능과의 의존
- **A1 셸**: 로컬 웹 오리진·탭(`view=datasources`, `ds`), 첫 실행 예제 시드, 커넥터 설치 여부 판단(엔진 목록), Bolt 연결.
- **A2 저장소**: Ontological 그래프 DB 확장(패브릭 문장, SHOW COLUMNS 포함)과 FDW 커넥터 4종, 예제 DB.
- **M4 Portal**: 같은 문장을 직접 실행. 「Ontological Portal 에서 질의」 링크로 포털 탭 열기. 예제 노드는 `sample` 그래프 선택 필요.
- **M1 온톨로지 구축**: 구축 브리프의 데이터소스 선택과 클래스-데이터소스 바인딩은 Studio 백엔드의 `/api/datasources*` → 같은 브리지의 호환 엔드포인트를 쓴다. Studio 그래프의 클래스 이름이 가상 노드 이름과 같으면 충돌하므로 예제는 별도 그래프에 둔다.
- **A3/M2**: 에이전트의 데이터소스 조회 도구도 같은 카탈로그를 본다. 원천 직접 SQL 경로(text2sql direct-sql, MindsDB 문장)는 브리지가 501로 막는다 → 질의는 가상 노드 Cypher로만.
- **M7/M2 액션**: 가상 노드는 읽기 전용이라 원천 변경은 액션(업무 시스템 호출)이 한다. 변경 결과는 미리보기로 즉시 보인다.

## 11. 원본과 비교할 테스트 항목
1. 탭 진입 요청 순서: overview → tables(첫 데이터소스) → columns(첫 테이블) → (가상 노드면) preview?limit=20. `ds` 쿼리 지정 시 그 데이터소스.
2. overview 응답 필드·형식(§6, §7), 예제 상태 값: 데이터소스 3(crm·erp·wms 이름순, engine `postgres`, host `127.0.0.1`), 그래프 목록에 `ontology`·`sample`, 가상 노드 7, 관계 5.
3. `SHOW TABLES FROM erp` 상당 결과 6행과 컬럼 수·노드 이름(튜토리얼 표).
4. 미리보기: `wms.shipment` 최대 지연 `SHP-03`(9, CUSTOMS_HOLD), `crm.claim` 3행, 바닥 문구 `3행 · Bolt → Ontological → postgres_fdw → 원천`. 원천 행 변경 후 즉시 반영.
5. dry 미리보기 문장: 연결(엔진 4종별 키 순서·기본값·비밀번호 마스킹), 가상 노드(PROPERTIES 생략/포함, KEY 자동 삽입, AS 생략), 관계, 삭제류.
6. 검증 오류 메시지와 400, 엔진 거절 422 + `statement`, 번역 배너 문구(S5-3, S9-1).
7. 가상 노드 폼 기본값: `po_line` → `PoLine`, 그래프 `sample`, KEY `po_line_id`.
8. 관계 폼 속성 자동 선택(PoLine→PurchaseOrder에서 `po_id`/`po_id`).
9. 실행한 문장: 쓰기만, 최신 우선, 30건 상한, 성공 결과 문구/「완료」, 실패 시 ✕.
10. 연결 해제 거절(erp), 노드 삭제 거절(PoLine with 관계), 관계 삭제 후 노드 삭제 성공.
11. 엔진 목록 API와 대화상자 비활성 표시(설치된 커넥터 기준).
12. 정의 안 된 쓰기 경로 501 문구, 정의 안 된 GET 404.
13. 홈 최근 항목 데이터소스 행 문구와 클릭 시 `ds` 선택 상태로 열림.
14. 지도: 열 = 데이터소스, 노드 클릭 시 테이블 상세 이동(배치 좌표는 비교 대상 아님).

## 12. 모르는 점 (4단계 실행 기록에서 확인)
1. 쓰기 성공 시 엔진이 돌려주는 `result` 문구의 정확한 형식(데이터소스 생성·새로 고침·해제, 가상 노드 생성·삭제). 관계 생성은 `virtual relationship (:A)-[:R]->(:B) on A.pa = B.pb` 형식으로 추정.
2. `REFRESH DATASOURCE`가 사라진 테이블 제거·컬럼 변경을 반영하는지(셸 주석상 새 테이블만).
3. `CREATE DATASOURCE`의 표시용 옵션(jsonb)에 어떤 키가 저장되는지(비밀번호 제외 여부는 엔진 주석으로만 확인). 사용자 매핑이 `FOR PUBLIC`이라 관리자 외 역할이 외부 테이블을 읽을 수 있는지.
4. 원천 접속 실패 시 엔진 원문 오류와 응답 지연(타임아웃 시간). 대화상자에 진행 표시가 있는지(코드상 별도 스피너 없음, 버튼만 비활성).
5. 엔진 4종 중 실제로 연결 가능한 것(mac 배포본에 커넥터 4종 존재, Windows는 PostgreSQL만 — FAQ). Oracle/SQL Server 커넥터의 런타임 의존 라이브러리 유무.
6. 한 테이블에 가상 노드가 여러 개일 때(다른 그래프 포함) 칩·미리보기·노출 해제 대상.
7. 물리화된 노드의 화면 표시(「물리화」 태그)와 그때 미리보기가 원천이 아니라 사본을 읽는지.
8. 포털에서 만든 관계가 데이터소스 탭에 언제 반영되는지(자동 갱신 없음으로 추정).
9. 데이터소스 이름에 `ident` 수준만 검증하는 경로(해제·새로 고침)에 대문자 이름을 넣었을 때 엔진 응답.
10. `SHOW TABLES` 결과 정렬 순서(튜토리얼 표는 이름순).
11. 미리보기 열 이름이 속성 이름 변경(`qty AS quantity`) 시 어떻게 보이는지(속성 이름이 컬럼 표 순서에 없어 뒤로 밀릴 것으로 추정).

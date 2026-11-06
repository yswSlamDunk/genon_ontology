# A2 저장소 — 메모 (다른 대상·보안·열린 질문)

## 작업 기록
- 앱·스크립트는 실행하지 않았다. 예외: PostgreSQL 버전 확인을 위해 번들 `runtime/pg/bin/postgres --version`을 한 번 호출했다(버전 문자열만 출력, 데이터 폴더 무관). 같은 정보는 기존 `logs/postgres.log`에도 있다.
- 사용자 기존 데이터 폴더(`~/Library/Application Support/Ontological Studio`)를 **읽기만** 했다: 파일 목록, 로그, `ports.json`, `pgdata`의 설정 파일, `secrets.json`의 키 이름(값은 출력하지 않음). 이 시점 앱이 실행 중이었다(postmaster.pid·run/*.pid 존재, 2026-10-31 13:18 기동).
- Bolt 바이너리는 `file`·`otool -L`·`strings`만.

## 보안·품질 관찰
1. **모든 구성이 DB 슈퍼유저 하나(`og`)를 공유**: Studio 백엔드·MCP·액션 서비스·포털이 같은 슈퍼유저 비밀번호를 환경 변수(`NEO4J_PASSWORD`, `PGPASSWORD`, `KINETIC_NEO4J_PASSWORD`)로 받는다. 에이전트가 실행하는 스크립트(`runStudioScript`, 코드 앱 턴)도 같은 환경을 물려받으므로, 에이전트(Claude Code 등, bypassPermissions)가 슈퍼유저로 DB 전체를 다룰 수 있다(추정 — A3에서 env 전달 범위 확인).
2. Bolt·DB 모두 127.0.0.1 전용, TLS 없음. 같은 PC의 다른 사용자/프로세스는 비밀번호만 알면 접속 가능. `secrets.json`은 0600이지만 `ports.json`은 0644(포트 정보만이라 낮은 위험).
3. 비밀번호를 SQL 문자열에 끼워 `ALTER ROLE … PASSWORD '…'`로 설정(작은따옴표 이스케이프). 값이 base64url이라 실제 위험은 없음. psql 호출 시 비밀번호는 env(`PGPASSWORD`)로 — 명령줄 노출 없음. initdb 비밀번호는 임시 파일(0600)로 넘기고 삭제.
4. `MARIADB_TLS_DISABLE_PEER_VERIFICATION=1`이 postgres 프로세스 전체에 설정됨 → MySQL 데이터소스 연결 시 원격 서버 인증서 미검증(의도된 선택, 코드 주석에 근거 있음). M3 보안 메모로 넘김.
5. `MCP_ALLOW_DATASOURCE_EXPANSION=true` 기본 — MCP에 붙은 외부 AI 클라이언트가 원천 행을 읽을 수 있다는 주석(services.js). A3/M3 관련.
6. 부트스트랩의 `og_create_graph('ontology')`는 존재 확인 없이 호출 → 부트스트랩이 그 뒤 단계(예: sample.sql)에서 실패하면 다음 재시도에서 이 줄이 "이미 존재" 오류로 계속 실패할 가능성(정적 추정, 4단계에서 확인 가치 낮음 — 고장 주입 필요).
7. 사용자가 만든 데이터소스는 PG 포트 변경 시 재등록되지 않는다(예제 3개만) → 포트가 바뀌면 사용자 데이터소스가 깨질 수 있음(추정). 포트가 끈끈해서 드묾.
8. 로그는 append만, 회전 없음(`procs.start`).

## 라이선스 관찰
- 배포본 어디에도 LICENSE 파일이 없다(Resources 최상위 4단계 탐색, site-packages·node_modules 제외). 로컬 `ontological-db` 저장소 사본에도 LICENSE 파일이 없다. ADR-0002의 "ontological-db Apache-2.0" 근거를 별도로 확인해야 한다 → REVIEW.md 후보.
- `runtime/pg/lib/oracle/libclntsh.*`(Oracle Instant Client)가 번들돼 있다 — 재배포 조건이 있는 독점 라이브러리. 새 구현이 Oracle 연결을 지원하려면 조건 확인 필요.
- Bolt 바이너리에 빌드 경로 `/Users/uengine/uengine-platform/ontology-studio-desktop/...`가 남아 있음 → 배포본 셸의 원 저장소 이름이 `ontology-studio-desktop`일 가능성(ADR-0008의 "공개 브랜치 어디에도 없음"과 연결).

## 다른 대상 관련 발견
- **A1**: 부팅 순서·고아 정리·포트 할당·단일 인스턴스·데이터 폴더 이전은 A1과 겹친다. 이 문서는 저장소 관점만 다뤘다. 기존 로그 실측 부팅 시간: 첫 실행 UI 로드 4.97초, 재실행 3.13초.
- **M3**: 데이터소스 엔진 목록 = 설치된 FDW control 파일(postgres/mysql/oracle/sqlserver 4종 모두 있음). `CREATE DATASOURCE` 결과 문구 `datasource erp (postgres): 6 tables as erp.*`. 엔진 카탈로그 `og_catalog.datasource.engine` 주석은 `'postgres' | 'mysql' | 'mindsdb'`(oracle/sqlserver는 주석에 없음 — 확인 필요). 데이터소스 테이블 쓰기 거부 트리거 있음.
- **M4**: 포털은 Bolt가 아니라 PG 직접(`pg` Pool, max 8, 슈퍼유저). 포털 환경 변수 `OG_STUDIO_ALLOW_RAW_SQL`(미설정 → 원시 SQL 비허용 추정), `OG_BENCH_DIR`. 확장에 시점 조회 함수(og_as_of, og_timeline, og_history, og_release_*)가 있음 → 튜토리얼 10 시간 여행.
- **M1**: 확장이 `__`로 시작하는 속성·`_id/_type/_src/_dst`를 예약(`OG_RESERVED_PROPERTY`). 첫 실행 로그에서 `__ontology_publish_declare` 쓰기 시도가 여러 번 거부됨 — 그래도 예제 온톨로지 발행은 `ok`. Studio 쪽이 실패를 예상하고 우회하는 코드인지 M1에서 확인.
- **M1/M5**: 첫 실행 예제 온톨로지 결과 `{"nodes": 36, "relationships": 35, "publish": "ok", "kinetic_refresh": {"ok": true, "actions": 3}}`; 임베딩 서버 연결 거부 경고(`Embedding failed … Connection refused`) — 임베딩은 선택 기능으로 보임.
- **M7**: 액션 서비스 자체 저장은 SQLite `<userData>/kinetic.db`. 예제 서비스는 `sample_svc`로 PG 직접 쓰기.
- **A3**: Studio 설정에서 `NEO4J_DATABASE` 설명 "Neo4j에서는 데이터베이스, ontological-db에서는 그래프"(settings.py:44). 원래 Neo4j용으로 짠 백엔드를 Bolt 게이트웨이로 재사용하는 구조.

## 열린 질문
- 확장 `ontological`의 `superuser = false, trusted = false` — 슈퍼유저가 아닌 역할로 그래프를 쓸 수 있는가(권한 모델 `og_grant`, `og_enable_rls`). 앱은 슈퍼유저만 쓰므로 당장은 무관.
- 벡터 확장(pgvector 0.8.7)을 쓰는 기능(og_vector_search, og_hybrid_search, embedding 테이블)이 앱 어디에서 쓰이는지 — 임베딩 서버(`ER_RERANK_URL` 등)와 관계, M1/M2에서.

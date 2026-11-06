# M3 데이터소스 — 메모 (다른 대상 발견, 보안·품질 관찰, 열린 질문)

## 다른 대상에 관한 발견
- **M1 온톨로지 구축**: 구축 브리프의 데이터소스 선택은 Studio 백엔드 `/api/datasources*` → 셸 브리지 호환 엔드포인트(`/fabric-bridge/api/datasources…`, `/fabric-bridge/text2sql/meta/…`)를 탄다. 백엔드 카탈로그는 TTL 캐시(기본 300초)가 있어 데이터소스 탭에서 막 만든 것이 `refresh=true` 없이는 늦게 보일 수 있다. 같은 라우터의 클래스 바인딩·behavior·reverse-bind·causal·publish는 M1에서 분석.
- **M1/M2/A3**: 백엔드의 직접 SQL 실행 경로(`/text2sql/direct-sql` POST, MindsDB `/api/query` POST)는 브리지가 **501**로 거절한다. 이 경로에 기대는 에이전트 도구·바인딩 fetch가 이 패키지에서 실패하는지 확인 필요.
- **M4 Portal**: 패브릭 문장(SHOW/CREATE/DROP/REFRESH/MATERIALIZE/EXPLAIN FABRIC)은 포털에서도 실행된다. 예제 노드는 `sample` 그래프.
- **A1 셸**: `/analyzer` 경로(robo-data-frontend)는 "포함되지 않은 화면" 안내 HTML. 프런트 번들의 `AnalyzerDataSourcePanel`은 이 빌드에서 쓰이지 않는 죽은 코드.
- **A2 저장소**: 첫 실행 시 `ogstudio` DB에 `ontological`·`postgres_fdw` 확장, `sample` DB와 `fabric_ro` 역할. mysql/oracle/tds FDW 확장은 데이터소스 생성 시점에 엔진이 만드는 것으로 추정(확인 필요).

## 보안·품질 관찰
- 브리지는 **인증 없이** 127.0.0.1 웹 오리진에서 쓰기(데이터소스 생성·해제, 가상 타입 생성·삭제)를 받는다. 같은 PC의 다른 프로세스는 그대로 호출할 수 있다. 다른 출처의 브라우저 페이지는 DELETE·JSON POST가 사전 요청(preflight)을 일으키고 브리지가 CORS 헤더를 주지 않으므로 대체로 막히나, 본문을 `text/plain`으로 보내는 단순 POST도 브리지가 JSON으로 파싱하므로(콘텐츠 유형 검사 없음) 교차 출처 POST(예: 데이터소스 생성·새로 고침)가 통할 가능성이 있다 — 점검 대상. 브리지는 그래프 DB **관리자 계정**으로 실행한다.
- 원천 비밀번호는 PostgreSQL 사용자 매핑에 평문 옵션으로 저장(엔진 주석: 관리자만 읽음). 앱 수준 암호화·키체인 사용 없음. 매핑이 `FOR PUBLIC`(바이너리 문자열 `CREATE USER MAPPING FOR PUBLIC SERVER`)이라 같은 DB의 다른 역할도 그 자격으로 원천을 읽을 수 있을 가능성.
- `secrets.json`(0600)에 PG 관리자 비밀번호와 `fabric_ro` 비밀번호가 평문.
- 원천 쓰기는 외부 테이블 트리거로 막힌다 → 원천 계정이 쓰기 권한을 가져도 패브릭 경유 쓰기는 불가(좋은 설계). 튜토리얼은 그래도 읽기 전용 계정을 권장.
- 식별자는 화이트리스트 정규식으로 검증 후 문장에 직접 삽입, 값은 Bolt 파라미터 → 문장 주입 위험 낮음. 단 `LIMIT`은 정수 강제.
- 「실행한 문장」은 읽기 문장을 기록하지 않아 튜토리얼 5장 표현(“실행 내역을 확인”)과 기대가 어긋날 수 있음.
- 미리보기 문구의 커넥터 이름은 화면 내장 매핑으로 정해진다(서버 응답이 아님).

## 열린 질문
- 데이터소스 **수정** API/화면 없음 — 구현 범위에 넣을지(해제·재연결은 가상 타입을 먼저 지워야 해 번거로움).
- 물리화(MATERIALIZE) 화면 버튼을 둘지.
- 실행 로그를 영구 저장할지(원본은 메모리만).

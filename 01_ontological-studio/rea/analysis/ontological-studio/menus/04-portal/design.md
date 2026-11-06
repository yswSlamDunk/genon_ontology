# M4 Ontological Portal — 설계 문서 (클린룸)

- 상태: 초안 v0.1 (2026-10-31, 정적 분석 기반 — 실행 기록 후 "모르는 점" 갱신 예정)
- 기준: Ontological Studio 0.1.1의 관찰 가능한 동작
- 이 문서는 원본 코드를 보지 않은 구현 세션에 넘긴다(ADR-0002, 0011). 경로·필드·화면 문구는 외부 계약이라 적었다.

---

## 1. 목적
그래프 DB(Ontological DB)를 직접 다루는 **브라우저형 Cypher 콘솔**. 데스크톱 앱 안의 탭으로, 또는 시스템 브라우저로 연다.
- Cypher(와 데이터 패브릭 문장)를 실행하고 결과를 그래프·표·JSON·컴파일된 SQL로 본다.
- 그래프의 스키마(타입·관계·속성·타입 계층)를 사이드바와 "스키마 지도"로 본다.
- 같은 질의를 **유효 시간·시스템 시간**만 바꿔 다시 실행한다(바이템포럴 시간 여행).
- 스키마를 단계적으로 바꾼다(이름 바꾸기·부모 바꾸기·타입 변경 등, 계획→실행).
- 앱 안에서는 한국어 질문을 CLI 코딩 에이전트로 Cypher로 바꿔 실행한다.
- 관리 API로 그래프 스키마+데이터를 "릴리스 패키지"로 내보내고 적용한다(화면 없음).

## 2. 사용자 시나리오 (요약)
| # | 시나리오 | 핵심 기대 |
|---|---|---|
| S1 | 포털 열기·화면 구성 | 탭/외부 브라우저, 그래프 선택, 스키마 사이드바 |
| S2 | 기초 질의 | 튜토리얼 실측 결과와 같은 행·순서 |
| S3 | 결과 카드·입력 보조 | Graph/Table/JSON/SQL, ★ 저장, ↑↓ 기록, 자동완성 |
| S4 | 관계·집계 | 여러 원천에 걸친 패턴, OPTIONAL MATCH, WITH, UNWIND |
| S5 | 그래프 상호작용 | 검사기, 더블클릭 이웃 확장 |
| S6 | 실행 들여다보기 | SQL 탭·지문, EXPLAIN FABRIC, `:explain`, `:why` |
| S7 | 패브릭 문장 | SHOW DATASOURCES / TABLES / COLUMNS / VIRTUAL … |
| S8 | 자연어 → Cypher | 생성·시험 실행·1회 수리·자동 실행, 쓰기는 실행 안 함 |
| S9 | 직접 쓰기 | CREATE GRAPH, CREATE/SET/MERGE/DETACH DELETE |
| S10 | 시간 여행 | valid at / as known at 조합별 결과, 지문 동일 |
| S11 | 스키마 지도·변경 | 쌓기→검토→단계 실행, 다시 쓴 행 수 보고 |
| S12 | 콘솔 명령 | `:schema` `:param` `:sql` `:releases` `:timeline` `:clear` … |
| S13 | 기록·도움말·오류 제안 | Query log, "Did you mean" 칩 |
| S14 | 벤치마크 페이지 | 결과 없으면 빈 보고서 |
| S15 | 릴리스 API | export → plan → apply |

상세 단계·기대 결과는 `user-scenarios.md` 참조(같은 폴더).

## 3. 구성
```
[데스크톱 셸] ──(자식 프로세스 기동, env로 DB 접속정보)──▶ [포털 서버: HTTP, 루프백]
     │                                                   │  정적 파일(웹 UI) + /api/*
     │ IPC nl2cypher                                     │  SQL로 엔진 함수 호출
     ▼                                                   ▼
[셸 메인: NL 번역기] ──Bolt(basic auth)──▶ [Bolt 게이트웨이] ──▶ [PostgreSQL + Ontological 확장]
     └─ 한 턴 에이전트 실행기(자식 프로세스) → CLI 에이전트(Claude Code / Codex)
```
- 포털 서버는 **PostgreSQL에 직접** 연결 풀(최대 8)을 두고 엔진의 SQL 함수를 부른다. Bolt를 쓰지 않는다.
- Bolt는 NL 번역기가 스키마 보강·시험 실행에만 쓴다.
- 포털 서버는 의존성 최소(HTTP 서버 + PG 드라이버). 웹 UI는 빌드 없는 정적 HTML/JS/CSS.

### 3.1 기동 계약 (셸 ↔ 포털 서버)
- 셸이 서버를 띄울 때 넘기는 환경: 리슨 포트, 바인드 호스트 `127.0.0.1`, PG 호스트·포트·DB 이름(`ogstudio`)·사용자(`og`, DB 슈퍼유저)·비밀번호(앱이 첫 실행 때 만든 무작위 값).
- 준비 판정: `GET /api/health`가 HTTP 응답을 주면 준비(최대 30초).
- 앱 종료 시 5초 안에 정지.
- 포트: 선호 27474, 사용 중이면 다른 빈 포트. 단독 실행 기본값은 7474.
- 서버 설정 환경 변수(단독 실행 겸용):

| 변수 | 기본 | 뜻 |
|---|---|---|
| `PORT` | 7474 | 리슨 포트 |
| `OG_STUDIO_HOST` | 127.0.0.1 | 바인드 주소. 루프백이 아니면 `OG_STUDIO_ALLOW_REMOTE=1` 없이 시작 거부(오류 출력 후 종료) |
| `OG_STUDIO_ALLOW_RAW_SQL` | 꺼짐 | `1`이면 `POST /api/sql` 허용 |
| `OG_STUDIO_MAX_BODY` | 64MB | 요청 본문 상한 |
| `OPENAI_API_KEY`, `OG_STUDIO_LLM_MODEL`(기본 gpt-4.1) | 없음 | 스키마 AI 제안. 키 없으면 꺼짐 |
| `OG_BENCH_DIR` | 서버 기준 상대 폴더 | 벤치마크 결과 JSON 폴더 |
| `PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD` | | DB 접속 |

앱은 raw SQL·AI 키를 넘기지 않으므로 **앱 안에서는 두 기능이 꺼져 있는 것이 정상 동작**이다(비교 시 동일하게).

### 3.2 여는 경로 (셸)
- 홈 카드 「Ontological Portal」(설명 "Cypher 콘솔 · 스키마 지도 · 시점 조회."), 홈 사이드 빠른 링크, 트레이 메뉴, 메뉴바 「런타임 › Ontological 포털 탭 열기」 → 포털 탭(`{kind:'portal'}`), 탭 제목 고정 "Ontological Portal".
- 메뉴바 「런타임 › Ontological 포털을 브라우저에서 열기」 / 셸 동작 `open('portal')` → 시스템 브라우저로 `http://127.0.0.1:<port>/`.
- 포털 탭에는 셸 브리지(`window.liteShell`)가 주입된다 → NL 기능 활성. 외부 브라우저·Studio 화면 안의 iframe에는 없음 → NL 기능 비활성(포털은 그대로 동작).
- 포털 탭에서 포털·Studio 이외 URL로 이동하면 외부 브라우저로 넘긴다.
- Studio의 「Ontological Portal」 내비게이션 항목은 같은 포털을 iframe으로 띄운다(셸 웹 서버의 `GET /app/portal-info` → `{url, graph}`로 주소를 얻음).

## 4. 화면 구성과 상호작용

### 4.1 레이아웃 (어두운 테마 전용)
- **왼쪽 레일(아이콘):** Database schema, Saved queries, Query log, Schema changes(⇄), Help, Benchmark(별도 페이지 링크), 아래쪽 연결 점(health 성공 시 초록).
- **사이드바(레일 선택에 따라 패널 하나):**
  - *schema*: 제목 "Ontological DB" + 그래프 선택 상자. 정보 박스(`engine ontological <버전>`, `database <이름>`, PG 버전 첫 구절; 실패 시 빨간 "not connected"+오류). "Entity types (click to query)" 칩(타입 색, 인스턴스 수, 추상이면 ` ∗`·툴팁 "abstract — matches subtypes only"), "Relationship types" 칩, "Property keys"(모든 타입 속성 이름, 정렬), "Type hierarchy (subtypes are matched automatically)"(부모 없는 타입부터 `└ ` 들여쓰기, 인스턴스 수). 비었을 때 "no entity types yet" 등.
  - *saved*: 저장 질의 목록(클릭 실행, "remove"). 비었으면 "star a frame to save its query".
  - *audit*: "Query log" + refresh. 최근 100건: 질의(앞의 `[…]` 접두 제거), `N rows`(오류면 `error`, 빨강) · `x.x ms` · 시각. 클릭 실행.
  - *evolve*: 스키마 디자이너(§4.6).
  - *help*: 예제 스니펫(클릭 실행) — `MATCH (n) RETURN n LIMIT 25`, 상속 예, 관계 벡터 검색 예, `:sql` 예, 시간 여행·스키마 변경 설명, 벤치마크 링크, 명령 목록.
- **본문:** `$` 프롬프트 + 여러 줄 입력칸(자동 높이, 최대 화면 40%) + 버튼(⏱ 시간 여행, [앱 안] ✨ 자연어, ▶ 실행). 그 아래 시간 막대(숨김), [앱 안] NL 상태 막대(숨김), 결과 스트림(새 카드가 위), 디자이너 모드에서는 스키마 지도.
- **검사기(오른쪽 떠 있는 패널):** 그래프 노드 클릭 시.

### 4.2 입력과 실행
- 실행: ▶ 또는 ⌘/Ctrl+Enter. 앞뒤 공백 제거, 비면 무시.
- 기록: 실행한 질의(`:param` 제외)를 맨 앞에 추가, 최대 100개, 브라우저 저장소에 보관. 입력칸이 한 줄일 때 ↑/↓로 탐색.
- 실행 후 입력칸 비움. 카드 제목 = 질의 텍스트. 시점이 설정돼 있고 `:` 명령이 아니면 카드에 배지 `⏱ valid <값> · known <라벨>`.
- 분기:

| 입력 | 동작 |
|---|---|
| `:clear` | 결과 스트림 비움 |
| `:param <name> => <value>` | 값이 JSON이면 파싱, 아니면 바깥 작은따옴표 하나 제거한 문자열. 페이지 메모리에만 저장. 카드 "$name set for this page — not saved, not shown". 이름이 식별자가 아니면 "usage — :param name => value" |
| `:params` / `:params clear` | 이름 목록 "$a, $b — values are not shown"(없으면 "no parameters set") / "parameters cleared" |
| `:sql <SQL>` | `POST /api/sql` → Table·JSON, 상태 "N rows · raw SQL" |
| `:explain <cypher>` | `POST /api/explain` → SQL·Plan 탭, 상태 "columns: …" |
| `:why <cypher>` | `POST /api/diagnose` → Diagnosis(Compile check: "query compiles" 또는 메시지 / Pattern walk: 단계 설명 → 행 수, 판정은 경고색 + 힌트 / Estimate: 예상 행, cost, 조언) |
| `:schema` | `GET /api/schema` → Schema·Storage(JSON), 상태 "machine-readable schema — this is what an agent sees" |
| `:changes` | `GET /api/schema-changes` → Table(change_id, kind, phase, spec)·JSON |
| `:snapshot [N | 시각]` | 숫자면 version, 아니면 at → Table(type, parents, property, type_sql, column)·JSON, 상태 "schema version N" + 설명 |
| `:releases` | `GET /api/releases` → Table(#, name, status, schema `vA → vB`, changes, writes, actor, finished, package 앞 19자)·JSON |
| `:timeline <Type> <prop>=<key> [from] [to] [@system_at]` | `GET /api/timeline` → Timeline(막대)·Table·JSON. 인자 부족 시 Usage 카드 |
| 그 밖 | `POST /api/cypher` (현재 그래프, `:param` 값, 시점) |

- Cypher 성공 시 탭: 그래프 투영에 노드가 있으면 **Graph**, 항상 **Table**, **JSON**(행 배열 들여쓰기 2), 컴파일 SQL이 있으면 **SQL**(키워드 강조). 상태줄: `N row(s)` · `n nodes · m relationships` · `server X ms · round trip Y ms` · `compiled SQL <지문>`. 이어서 사이드바 스키마와 질의 기록을 다시 읽는다.
- 실패 시 Error 탭 하나, 상태 "failed · Y ms". 메시지에 `did you mean: a, b`가 있으면 "Did you mean" 아래 후보 칩. 칩을 누르면 메시지에서 작은따옴표로 감싼 틀린 이름을 질의에서 후보로 바꿔 즉시 재실행.
- 카드 머리: ★(저장 — 이미 있으면 무시, 맨 앞에 추가, 최대 50), ✕(닫기), 탭 버튼.
- `data-run` 성격의 요소(칩, 계층 항목, 기록·저장 항목, 도움말 스니펫)는 클릭하면 그 질의를 입력칸에 넣고 즉시 실행. 칩 질의: 엔티티 `MATCH (n:<T>) RETURN n LIMIT 50`, 관계 `MATCH (a)-[r:<T>]->(b) RETURN a, r, b LIMIT 50`.

### 4.3 결과 보기
- **Table:** 컬럼 = 응답 `columns`(없으면 첫 행 키). 값: null(흐림 "null"), 숫자·불리언, 문자열, 노드/관계 객체는 `(<타입>) {키: JSON값, …}`(밑줄 시작 키 제외, 타입 색), 그 밖 JSON 문자열. 행 없으면 "no rows".
- **Graph:** 상단 범례(라벨 칩), 캔버스 힘 기반 배치(반발·스프링·중심 끌림, 감쇠하며 멈춤), 노드 원(반지름 약 22) 안에 캡션(속성 `name`→`title`→`label`→`model`→`id`→타입 순, 9자 넘으면 8자+…), 간선 화살표·확대 시 관계 타입 글자, 타입별 고정 색(10색 팔레트, 이름 해시). 조작: 노드 끌기, 빈 곳 끌어 이동, 휠 확대(0.2~3배), ⤢ 맞춤, ❙❙/▶ 배치 멈춤·재개. 노드 클릭 → 선택 테두리 + 검사기. 더블클릭 → `POST /api/expand {id, limit:40}` 결과를 같은 그림에 추가(이미 있는 노드·간선 제외). 노드가 없으면 Graph 탭 자체를 만들지 않음.
- **검사기:** 제목 `<타입> · <id>`, 모든 키·값, 버튼 "expand neighbours"(→ `MATCH (n)-[r]-(m) WHERE id(n) = <id> RETURN n, r, m LIMIT 50` 실행), "history"(→ `:sql SELECT * FROM og_history(<id>)` 실행 — raw SQL이 꺼져 있으면 오류 카드), ✕.

### 4.4 입력 보조 (앱·브라우저 공통)
- 문법 색: 입력칸 아래에 같은 글꼴의 미러를 두고 색칠(입력칸 글자는 투명). 키워드, 노드 라벨(`(` 안 `:X`), 관계 타입(`[` 안 `:X`), 문자열, 숫자, `$파라미터`, 함수 호출, `//` 주석. `:sql `로 시작하거나 Cypher처럼 보이지 않으면 색칠 안 함.
- 자동완성(그래프의 `/api/schema` 기반, 이름이 `_`로 시작하는 타입·속성 숨김):
  - `var.` → 그 변수의 라벨 속성(이름·타입), 라벨 모르면 전체 속성
  - `(`…`:` → 노드 라벨(힌트 "노드"), `[`…`:` → 관계 타입(힌트 "관계")
  - 단어 → 질의 안 변수, 키워드(구문 포함: `OPTIONAL MATCH`, `ORDER BY`, `DETACH DELETE`, `SHOW DATASOURCES`, `SHOW TABLES FROM`, `SHOW VIRTUAL NODES`, `SHOW VIRTUAL RELATIONSHIPS`, `CREATE VIRTUAL NODE`, `CREATE VIRTUAL RELATIONSHIP` 등), 함수(선택 시 `name(` 삽입)
  - 접두어 일치 우선, 2자 이상이면 포함 일치도, 최대 12개. ↑↓ 선택, Tab/Enter 수락, Esc 닫기, Ctrl+Space 강제. 문자열·주석 안에서는 안 뜸.
- 그래프를 바꾸면 자동완성 스키마도 다시 읽는다.

### 4.5 시간 여행 막대
- ⏱ 버튼으로 열고 닫음(열 때 `/api/temporal` 다시 읽음). 구성: 라벨 "Time travel", `valid at` 텍스트 입력(자리 표시 "now — e.g. 2026-08-15", 자유 문자열), `as known at` 선택(첫 항목 "now"; 이후 최근 쓰기마다 `after HH:MM:SS.mmm · <actor> — <질의 앞 54자>`, 값 = 그 쓰기의 기록 시각), 안내 문구, "clear".
- 안내: 시간 버전 타입이 있으면 `temporal types: A, B — the query text does not change; the instant is a session setting`, 없으면 `no temporal types in this graph — enable with og_enable_temporal(graph, type)`.
- 둘 중 하나라도 정해지면 입력칸에 "시점 설정됨" 강조(노란 테두리), ⏱ 버튼 활성 표시.
- 실행 시 요청 `at = {valid_at?, system_at?}`(빈 것은 빼고, 둘 다 없으면 null). 질의 텍스트는 바꾸지 않는다.
- "as known at" 목록은 감사 기록의 **전역** 최근 쓰기 30건(현재 그래프로 거르지 않음 — 원본 동작, §11 참고).

### 4.6 스키마 디자이너와 스키마 지도
- ⇄ 패널을 열면 본문이 "Schema map" 모드로 바뀐다(상단: "Schema map", `schema v<N>`, 범례 extends/staged/to remove, "name · type · column", 안내 "click a property or a type · drag a card onto a new parent").
- **지도:** 스냅샷(`/api/schema-snapshot`)과 인스턴스 수(`/api/schema` stats)로 그림. 엔티티 타입 카드를 계층 트리로 배치(하위 타입 있는 트리는 넓은 순, 단독 타입은 오른쪽에 3개씩 세로 쌓기), 관계 타입 카드는 아래 "Relationship types" 줄. 카드: 색 점, 이름, ⏱(temporal), 인스턴스 수(새 타입은 "new"), 자기 속성 행 `이름(* 필수) · 타입 · 저장 컬럼`, 상속 속성은 `+ N inherited · a, b` 한 줄. 부모→자식 곡선(현재=실선, 추가 예정=점선, 제거 예정=빨강).
- **변경 쌓기(즉시 실행 안 함):**
  - 자기 속성 클릭 → 메뉴: Rename(새 이름) / Change type(int, float, string, bool, date, timestamp) / Make required / Drop property. 상속 속성은 메뉴 없음.
  - 타입 머리 클릭 → Rename type / Add property(`name:type`, 타입 생략 시 string) / New subtype / Insert type above(새 타입을 기존 부모들 아래 만들고, 이 타입에 새 부모 추가, 기존 부모 제거 — 3개 변경) / Remove parent(부모 목록) / Add parent(같은 종류 타입 최대 8개).
  - 카드를 다른 카드에 끌어 놓기 → 새 부모 추가 + 기존 부모(대상 제외) 제거.
  - "Add as JSON": 변경 객체 하나 또는 배열. 잘못된 JSON이면 경고창 "not valid JSON".
  - "Ask"(⌘/Ctrl+Enter): `POST /api/schema-assist` → 설명과 "k of n proposals pass the catalog check · <model> · <ms> ms — review below before running". 각 제안을 `AI` 표시로 쌓음, 검사 실패분은 `invalid` + 문제 문구.
- 쌓인 변경은 지도에 미리 그린다(이름 바꿈 = 취소선 → 새 이름, 타입 변경 = 취소선 → 새 타입, 삭제 = 흐림, 추가 = 강조, 새 타입 = 유령 카드).
- **Change plan 목록:** 항목마다 종류(행을 다시 쓰는 종류는 다른 색), 출처(AI), 상태(staged/reviewed/invalid/running/done/blocked/failed/aborted), 설명 문장(예: "Rename **T.p** → **q**", "**T** also becomes a **P**"), 문제, 영향, 단계 칩(이름+ms), 진행 막대, 결과. 비었으면 안내 문구. staged·reviewed·invalid·failed 항목은 ✕로 제거(서버에 계획이 있으면 abort).
- **Review impact:** staged 항목마다 plan 호출 → 영향 문구: `<N> rows in scope` · (다시 쓰는 종류면 "rewrites rows in batches", 아니면 "catalog only — no row rewritten") · 변환 불가 값 수 · 잠금 정보. 새 타입은 "catalog insert — new type, no rows". 앞선 변경에 의존해 plan이 실패하면 "depends on an earlier change in this plan — reviewed when it runs".
- **Run:** 순서대로 실행. 새 타입은 `POST /api/schema-type`. 그 밖: plan(없으면) → expand → (다시 쓰는 종류: migrate를 배치 크기(입력, 기본 100000)로 done까지 반복, 진행률 = migrated/rows) → validate → (위반 0이면) contract. 위반이 있으면 `blocked`: "validation found N violation(s) · ids …" + Retry validate / Abort. 실패하면 `failed`, 이후 항목 중단. 완료 표시: `<총 ms> ms · <written> / <rows> rows rewritten`(저장 정보 없으면 "catalog"). 항목마다 끝나면 지도 다시 읽기, 전체 끝나면 History·사이드바 갱신.
- 다시 쓰는 종류 = 속성 타입 변경, 필수로 만들기, 속성 추가. 나머지(이름 바꾸기·부모 추가/제거·타입 이름 바꾸기·속성 삭제)는 카탈로그만.
- **Clear:** 완료 안 된 서버 계획 모두 abort 후 목록 비움.
- **History:** 스키마 변경 기록 최신순 `#id kind`, phase(aborted 강조), spec JSON. refresh 버튼.

### 4.7 자연어 → Cypher (앱 탭에서만)
- 셸 브리지에 NL 함수가 있을 때만 활성화. 입력칸 자리 표시를 한국어 예 포함 문구로 바꾸고, ▶ 앞에 ✨ 버튼(툴팁 "자연어로 묻기 — CLI 에이전트가 Cypher 로 바꿔 실행합니다 (⇧ + ⌘/Ctrl + Enter)")을 추가, 입력칸 아래 상태 막대 추가.
- **질문 판정:** 맨 앞 `//` 주석 줄을 지운 뒤, 비어 있지 않고 `:`나 `(`로 시작하지 않으며 Cypher 시작 키워드(MATCH, OPTIONAL, RETURN, WITH, UNWIND, CALL, CREATE, MERGE, DELETE, DETACH, SET, REMOVE, SHOW, DROP, EXPLAIN, PROFILE, USE, FOREACH, LOAD, REFRESH, ALTER, GRANT, REVOKE, UNION; 대소문자 무시)로 시작하지 않으면 "질문".
- ▶ 클릭·⌘Enter는 포털 기본 실행보다 먼저 가로채어, 질문이면 번역. ⇧⌘Enter와 ✨는 항상 번역.
- 번역 중: 버튼 비활성, 입력칸 강조, 막대 "에이전트가 **<graph>** 그래프의 스키마를 보고 Cypher 로 바꾸는 중… <질문>".
- 응답 처리: 입력칸을 받은 Cypher로 교체. 메타 `<에이전트 이름> · <초, 소수 1자리> s`(+ `· 한 번 고침`).
  - `error` 있음 → (빨강) "그래프에서 실패하는 Cypher 입니다 — 고쳐서 실행하세요." + 질문 + 메타 + 오류문. 실행 안 함.
  - `write` 참 → (경고) "데이터를 바꾸는 문장이라 실행하지 않았습니다. 확인한 뒤 ▶ 로 실행하세요." 실행 안 함.
  - 그 밖 → (정상) `자연어` 태그 + 질문 + note + 메타(+ `· 그래프에서 확인됨`), 포털 기본 실행으로 즉시 실행(한 번 우회).
  - 예외 → "바꾸지 못했습니다. <메시지>"(IPC 래핑 접두 제거).

## 5. API 명세 (포털 HTTP, 모두 JSON)

공통 규칙
- `/api/*` 요청 보호: 브라우저 헤더 `Sec-Fetch-Site`가 있고 `same-origin`/`none`이 아니면 403 `{"error":"cross-origin request refused"}`. `Origin`이 있고 그 호스트가 `Host` 헤더와 다르면 403. 둘 다 없으면 허용(명령줄 클라이언트).
- GET/HEAD 이외는 `Content-Type: application/json` 필수, 아니면 415 `{"error":"content-type must be application/json"}`. 본문이 JSON이 아니면 오류 "invalid JSON body", 상한 초과 "request too large".
- DB 오류 응답: `{error, code, detail, hint, where}`(PG 오류 필드 그대로). 처리 안 된 예외는 500 `{error}`.
- 그래프 파라미터 생략 시 `default`.
- 정적 파일: `/` → 메인 페이지, 그 밖 경로는 웹 폴더 안 파일(폴더 밖 탈출 차단), 없으면 404 `not found`(text/plain).

| 메서드 경로 | 요청 | 성공 응답 | 실패 |
|---|---|---|---|
| GET `/api/health` | — | 200 `{ok:true, version, database, server, graphs:[{name, graph_id}]}` (그래프 이름순) | 503 `{ok:false, …}` |
| GET `/api/schema?graph=` | — | `{schema, stats}` (§6.1) | 400 |
| POST `/api/cypher` | `{graph, query, params?:{}, at?:{valid_at?, system_at?}}` | `{rows:[행객체], columns:[질의 순서], elapsed_ms, compiled_sql:string|null, sql_fingerprint:string|null, at:{…}|null, graph:{nodes, edges}}` | 400 `{…, elapsed_ms}`, 빈 질의 400 `{error:"empty query"}` |
| GET `/api/temporal?graph=` | — | `{types:[이름], writes:[{at, actor, source, query}]}` | 400 |
| POST `/api/explain` | `{graph, query, analyze?:false}` | `{sql, plan, columns}` (엔진 결과) | 400 |
| POST `/api/diagnose` | `{graph, query}` | `{error:{ok, message?}, empty:{steps:[{description, rows} | {verdict, hint}]}|null, estimate:{estimated_rows, estimated_cost, advice[]}|null}` | 400 |
| POST `/api/expand` | `{id, limit?:50}` | `{nodes, edges}` (나가는·들어오는 각각 limit) | 400 |
| GET `/api/audit` | — | 최근 100건 `[{audit_id, principal, at, query, lang, rows_out, duration_ms, error_code}]` | 400 |
| POST `/api/sql` | `{sql}` | `{rows, columns, rowCount}` | 꺼짐 403 `{error:"raw SQL is disabled — start the server with OG_STUDIO_ALLOW_RAW_SQL=1 to enable it"}` |
| POST `/api/schema-type` | `{graph, name, parents?:[], kind?:"entity"|"relation"}` | `{type_id, name, kind, parents, elapsed_ms}` | 400 "type name must be an identifier" / "kind must be entity or relation" |
| POST `/api/schema-assist` | `{graph, prompt}` | `{explanation, changes:[{change, ok, problem}], model, elapsed_ms}` | 503 "AI assist is off — start the server with OPENAI_API_KEY", 400 "empty request", 502 모델 오류/"model returned non-JSON" |
| GET `/api/schema-changes?graph=` | — | `[{change_id, kind, phase, spec, report, created_at, updated_at}]` 최신순 | 400 |
| GET `/api/schema-snapshot?graph=&version=&at=` | — | 스냅샷(§6.2) | 400 |
| POST `/api/schema-change` | `{graph, action, change?, change_id?, batch?:10000}` | `{change_id, action, phase, report, elapsed_ms, storage:{rows, written, tables}|null}` | 400 "change.type is required" / "action and change_id are required" |
| POST `/api/schema-temporal` | `{graph, type}` | `{type, temporal:true}` | 400 |
| POST `/api/schema-diff` | `{graph, snapshot, hints?:[]}` | `{changes}` | 400 |
| POST `/api/release/export` | `{graph, keys?:{Type:prop}, name?, origin?}` | `{package, skipped:[{type, reason, …}], counts:{types, instances, slices, edges}}` | 400 |
| POST `/api/release/plan` | `{graph, package}` | `{schema:[변경], instances:{create, update, same, slices, items:[{type, key, action, changed}]}, edges, hash_ok, already_applied}` | 400 "package is required" |
| POST `/api/release/apply` | `{graph, package, actor?}` | `{release, plan, log, elapsed_ms}` | 400 `{…, release_id, log, samples}` |
| GET `/api/releases?graph=` | — | 릴리스 기록 배열 | 400 |
| GET `/api/timeline?graph&type&key_prop&key&from?&to?&system_at?` | — | `{slices:[{type_name, id, valid_from, valid_to, props, recorded_at, superseded_at, source, actor, op}]}` (무한대는 null) | 400 |
| GET `/api/benchmark` | — | `{scales:[…], source}` | 500 `{error, scales:[]}` |

### 5.1 `/api/cypher` 처리 규칙
1. 풀에서 연결 하나를 잡는다.
2. `at.valid_at`/`at.system_at`이 있으면 그 연결의 세션 설정(`og.valid_at`, `og.system_at`)에 문자열로 넣는다(트랜잭션 로컬 아님). 응답 `at`은 실제 넣은 것.
3. 엔진 Cypher 실행 함수에 (graph, query, params JSON)을 넘긴다. 결과 행마다 JSON 객체 하나.
4. 컬럼 순서: 엔진의 "질의 컬럼" 함수로 얻고, 실패하거나 비면(예: `RETURN *`) 첫 행 키.
5. 엔진의 "Cypher→SQL" 함수로 컴파일 SQL을 얻는다(쓰기 질의 등 실패하면 null). 지문 = SQL의 MD5 16진 앞 12자.
6. 그래프 투영: 행 값을 재귀 탐색해 `_id`가 있으면 노드, `_src`와 `_dst`가 더 있으면 관계로 모으고(같은 `_id` 중복 제거), 양 끝 노드가 모두 있는 관계만 남긴다.
7. 마지막에 반드시 두 세션 설정을 RESET하고 연결 반환(시점이 다른 요청에 새지 않도록).
- 패브릭 문장·`CREATE GRAPH`·`EXPLAIN FABRIC`도 같은 경로로 엔진에 넘긴다(포털은 해석하지 않음).

### 5.2 스키마 변경 처리 규칙
- `plan`/`apply`는 `change.type` 필수. plan 직전에 현재 트랜잭션 id를 기록해 두고, 응답 `storage`는 "변경 대상 타입과 그 하위 타입의 저장 표들에서 전체 행 수(rows)와 그 id 이후 쓰인 행 수(written)". 카탈로그만 바꾼 변경은 written=0.
- `apply`는 새 변경 하나를 한 트랜잭션에서 전 단계 실행. 응답 `change_id`는 `"apply:<xid>"`, phase `contracted`.
- 그 밖 action(expand, migrate[batch], validate, contract, abort)은 `change_id` 필수. 응답 phase = 변경 기록의 현재 단계.
- 엔진의 단계: plan → expand → migrate(반복, report.done) → validate(report.violations, samples) → contract, 또는 abort.

### 5.3 스키마 AI 제안 규칙
- 현재 스냅샷을 "타입 [entity|relation] extends 부모… (temporal): 속성:타입 (declared)…" 줄 목록으로 요약해 시스템 지시에 넣는다.
- 지시 요지: 요청을 `{explanation(사용자 언어 1~2문장), changes[]}` JSON 하나로. 변경 9종과 필드 형식(§6.3). 규칙: 속성 변경은 그 속성을 **선언한** 타입에서만, 중간 타입 끼우기는 "새 타입 생성 → 자식에 새 부모 추가 → 옛 부모 제거" 순서, 기존 이름은 정확히, 새 이름은 식별자, 불명확·불가능하면 빈 변경 + 이유.
- 응답을 JSON으로 파싱한 뒤 서버가 순서대로 가상 적용하며 검사: 알 수 없는 종류, 새 타입 이름 형식·중복·부모 존재, 대상 타입 존재, (이름 바꾸기·삭제·타입 변경·필수) 선언 여부, 새 이름 형식, 부모 존재/제거 대상이 실제 부모인지. 문제 문구 예: `type X does not exist`, `p is not declared on T`, `parent P does not exist`, `P is not a parent of T`, `new name is not an identifier`.

### 5.4 릴리스 규칙 (UI 없음)
- 내보내기: 추상 아닌 엔티티 타입마다 키 속성 결정(요청 > 스냅샷의 key 속성 > 부모 키). 키 없으면 skipped "no key property". 정확히 그 타입의 요소만(하위 타입은 따로), 키 값마다 유효 구간 슬라이스(무한대는 null). 관계 타입마다 모든 간선의 양 끝을 키로 바꿔 기록, 끝점이 내보내지지 않았으면 skipped "endpoint not exported". 간선은 정규 JSON 문자열 순 정렬.
- 해시: `sha256:` + SHA-256(키 정렬 정규 JSON of `{types: 스냅샷 types, instances, edges}`).
- 계획: 엔진 스키마 diff(패키지 변경 기록을 이름 바꾸기 힌트로) + 인스턴스별로 대상 그래프의 같은 시점 값과 비교(이름 바뀌는 속성은 새 이름으로 비교) → create/update/same 집계. 같은 해시로 이미 적용된 릴리스가 있으면 표시.
- 적용: 해시 불일치면 오류 "package hash does not match its content". 릴리스 시작 기록(actor) → 스키마 변경(타입 생성, 시간 버전 켜기, 속성 삭제는 "destructive — not applied by a release"로 건너뜀, 나머지는 plan→expand→migrate*→validate→contract, 위반이면 abort 후 오류) → 인스턴스 슬라이스별 쓰기(각 쓰기는 자기 트랜잭션, 유효 시작·(마지막 슬라이스만) 유효 끝·출처 `release:<id>`·actor를 세션에 설정; 없으면 CREATE, 다르면 바뀐 속성만 SET) → 없던 관계만 CREATE → 완료 기록(요약). 실패 시 실패로 기록하고 400.

## 6. 데이터 모델

### 6.1 스키마(`/api/schema`의 `schema`) — 엔진이 만드는 형태
- `entity_types: [{name, abstract, instances, extends:[부모], properties:[{name, type}]}]`
- `relation_types`(일부 경로에서 `relationship_types`): `[{name, instances, extends?, properties, roles?/from?/to?}]` — 가상 관계는 끝점이 비어 있을 수 있음
- `stats`: `{types:[{name, instances}], …저장 통계}`
- 이름이 `_`로 시작하는 타입·속성은 내부용(UI 보조·NL에서 숨김).

### 6.2 스키마 스냅샷
`{version, description, types:[{name, kind:'e'|'r', parents:[], abstract, temporal, properties:{<이름>:{type, column, required, key}}}]}`

### 6.3 스키마 변경 객체
`create_type{type, parents[]}` · `rename_property{type, property, new_name}` · `rename_type{type, new_name}` · `add_parent{type, parent}` · `remove_parent{type, parent}` · `drop_property{type, property}` · `alter_property_type{type, property, to}` · `set_required{type, property, default?}` · `add_property{type, property, data_type}` (타입 값: int, float, string, bool, date, timestamp). 릴리스 diff에는 추가로 `enable_temporal{type}`, `create_type{type_kind}`, `destructive` 표시가 올 수 있다.

### 6.4 그래프 요소 JSON
- 노드: `{_id, _type, …속성}` / 관계: `{_id, _type, _src, _dst, …속성}`.

### 6.5 릴리스 패키지
`{format:"og-release/1", name, origin, graph, created_at, schema_version, snapshot, changes, instances:[{type, key_prop, key, slices:[{valid_from, valid_to, props, source}]}], edges:[{type, from:{type,key_prop,key}, to:{type,key_prop,key}}], hash}`

### 6.6 NL IPC
- 브리지 함수: `liteShell.nl2cypher(question, graph)` → IPC 채널 `lite:nl2cypher`, 요청 `{question:string, graph:string}`.
- 응답: `{cypher, note, agent, ms, repaired:boolean, checked:boolean, write:boolean, error?:string}`. 실패는 예외(메시지 문자열).

## 7. 상태·저장
| 무엇 | 어디 | 비고 |
|---|---|---|
| 선택 그래프 | 브라우저 저장소 `og.graph` | 처음엔 목록 첫 그래프(이름순), 저장된 것이 목록에 없으면 첫 그래프 |
| 저장 질의 | `og.saved` (최대 50) | 출처별(앱 탭과 외부 브라우저 분리 추정) |
| 질의 기록 | `og.history` (최대 100) | `:param` 명령 제외 |
| `:param` 값 | 페이지 메모리 | 비밀값을 기록에 남기지 않기 위함 |
| 시간 여행 선택, 디자이너 계획 | 페이지 메모리 | 새로 고침하면 사라짐(디자이너 서버 계획은 abort 안 됨 — 남을 수 있음) |
| 감사 기록·스키마 변경 기록·릴리스 기록·이력 | DB(엔진) | 포털은 읽기만(쓰기 시 엔진이 기록) |
- 그래프 목록은 페이지를 열 때만 읽는다 → `CREATE GRAPH` 뒤에는 새로 고침해야 보인다(원본 동작).

## 8. 다른 기능과의 의존
- **A1 셸:** 프로세스 기동·포트·탭·외부 열기·브리지 주입.
- **A2 저장소:** PG 슈퍼유저 접속, Ontological 확장(Cypher·패브릭·시간·스키마 변경·릴리스 SQL 함수), Bolt 게이트웨이(NL 경로).
- **A3 에이전트:** 한 턴 실행기(도구 없는 단발 호출), 선택된 CLI 에이전트(설정 M8: 「런타임 › 에이전트」).
- **M3 데이터소스:** `sample` 그래프의 가상 노드·관계, 패브릭 문장.
- **M1/M2/M5:** Studio 백엔드가 포털 관리 API 주소를 환경 변수로 받는다(어떤 엔드포인트를 쓰는지는 해당 메뉴에서 확인). Studio 화면의 포털 iframe.
- 엔진 SQL 인터페이스(외부 계약, Ontological DB): Cypher 실행·컬럼·SQL 컴파일·설명·진단(오류 설명·빈 결과·추정)·확장(이웃)·노드/간선 JSON·스키마·통계·시간 타입 목록·타입 생성·시간 버전 켜기·스키마 스냅샷/변경 기록/단계 함수/diff·타임라인·릴리스 시작/완료/목록·이력. 세션 설정 `og.valid_at`, `og.system_at`, `og.valid_from`, `og.valid_to`, `og.source`, `og.actor`. 구현 시 같은 엔진을 쓰면 이 계약을 그대로 사용한다.

### 8.1 NL 번역기(셸 메인) 동작
1. 부팅 완료 전이면 "아직 시작하는 중입니다." 예외.
2. 검사: 질문 비면 "질문이 비어 있습니다.", 그래프 이름이 영문자/밑줄 시작 영숫자·밑줄이 아니면 "그래프를 고르세요.", 현재 에이전트가 CLI 계열이 아니면 "자연어 → Cypher 는 CLI 에이전트(Claude Code · Codex)로 동작합니다. 메뉴 「런타임 › 에이전트」에서 고르세요."
3. 포털 `GET /api/schema?graph=`로 스키마를 받아 압축: 내부 타입(`_` 시작) 제외, 내부 속성(`_source_id`, `_parent_source_id`, `created_at`, `updated_at`, `embedding`) 제외 → `{node_types:[{label, extends?, properties:["이름:타입"]}], relationship_types:[{type, from?, to?}]}`. 노드 타입이 없으면 "그래프 X 에 노드 타입이 없습니다." 실패 응답이면 "그래프 X 의 스키마를 읽지 못했습니다 (상태)".
4. Bolt 세션(해당 그래프)으로 보강(각 문장 오류는 무시): `SHOW VIRTUAL RELATIONSHIPS IN <g>` → 관계의 from/to 타입과 `join: "<A.col> = <B.col>"`; `SHOW VIRTUAL NODES IN <g>` → 노드 타입의 `source`(원천 표); 끝점 모르는 저장 관계는 그 관계 한 건의 양 끝 라벨(내부 라벨 제외)로 채움.
5. 시스템 지시(요지, 영어로 작성): Ontological DB(PostgreSQL 기반 그래프 DB)용 Cypher **한 문장**으로 답하라. 형식 = cypher 코드 블록 하나 + 무엇을 반환하는지 한국어 한 줄, 그 외 금지. 그래프 이름 명시, 스키마의 라벨·관계 타입·방향·속성 이름만 사용. 허용 절: MATCH, OPTIONAL MATCH, WHERE, WITH, RETURN, ORDER BY, SKIP, LIMIT, UNWIND, DISTINCT, 집계. 허용 함수(§9 목록 34개)만 — head, last, nodes, 리스트·패턴 내포, CASE, APOC, db.* 금지. 패턴의 모든 노드에 라벨(가상 관계는 양쪽 라벨이 있어야 조인 가능) — 예시로 `(po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier)`. 관계는 스키마의 from→to 방향으로. 라벨은 패턴에만(WHERE의 라벨 조건 금지). 문자열 비교는 =, <>, STARTS WITH, ENDS WITH, CONTAINS만, 대소문자 구분, 코드 값은 스키마 예시 모양을 따를 것. 질문이 명시적으로 요구하지 않으면 쓰기 금지. 전체 노드 대신 이름 붙인 컬럼 반환(그래프를 보자는 질문 제외). 결과가 클 수 있으면 LIMIT 100.
6. 사용자 메시지: `Schema (JSON):` + 압축 스키마 JSON + 빈 줄 + `Question: <질문>`.
7. 에이전트 한 턴 호출 → 답에서 첫 코드 블록(cypher/sql/무표시) 내용을 Cypher로(블록 없으면 전체), 끝 세미콜론 제거, 블록 뒤 첫 줄을 note로. 비면 "에이전트가 Cypher 를 내지 못했습니다."
8. 쓰기 판정: 따옴표 문자열을 지운 텍스트에 단어 CREATE, MERGE, DELETE, DETACH, SET, REMOVE, DROP, REFRESH, ALTER, GRANT, REVOKE, LOAD, FOREACH 중 하나 → write=true, 시험 실행·수리 없이 반환(checked=false).
9. 읽기면 Bolt 읽기 세션으로 1회 시험 실행(결과 버림). 20초 넘게 걸리면 성공으로 간주. 오류면 메시지에서 `ERROR:` 이후 최대 400자.
10. 실패 시 수리 1회: 같은 시스템 지시 + 원래 사용자 메시지 뒤에 "이 질의가 Ontological에서 실패했다 / 질의 / Error: 메시지 / 고쳐라, 같은 답 형식"을 붙여 다시 호출 → 재추출 → 재시험. 또 실패면 `{…, repaired:true, checked:false, error}` 반환. 성공이면 checked=true.
11. 반환 `ms`는 전체 소요, `agent`는 에이전트 표시 이름(예: "Claude Code").
12. 셸 로그: `nl2cypher <graph>: <ms> ms`(+ ` (고침 1회)`, ` — 실패: <오류 120자>`), 예외면 `nl2cypher 실패: <메시지>`.

### 8.2 한 턴 에이전트 실행기
- 입력(표준 입력 JSON) `{system, user}` → 출력(표준 출력) 에이전트 답 텍스트. 앱이 Studio와 같은 환경(선택된 에이전트 id, PATH)으로 실행, 전체 5분 제한.
- 프롬프트 = system + 빈 줄 + `---` + 빈 줄 + user. **도구 없이** 단발 실행(Claude Code는 비대화 출력 모드·도구 목록 비움, Codex는 비대화 exec 모드). 프로젝트 파일을 못 보게 빈 임시 폴더에서 실행. 180초 제한.
- 실패 코드: 에이전트 못 찾음 / 시간 초과("CLI 에이전트가 180초 안에 답하지 않았습니다.") / 비정상 종료("CLI 에이전트가 실패했습니다 (exit N): …"). 셸은 stderr 마지막 줄들을 예외 메시지로 올린다.

## 9. 지원 Cypher·패브릭 문장 (포털에서 보이는 표면)
- 읽기 절: MATCH, OPTIONAL MATCH, WHERE, WITH(…WHERE), RETURN(DISTINCT, AS — 한글 별칭 가능), ORDER BY(여러 키, ASC/DESC), SKIP, LIMIT, UNWIND, UNION, CASE WHEN … END(튜토리얼 실측). 패턴 안 속성 맵 `{k: v}`, 쉼표로 여러 패턴, 방향 `->`, `<-`, 무방향 `-`. 가변 길이 `*1..3`은 저장 관계에서만.
- 조건: 비교 6종, AND/OR/NOT/XOR, IN [목록], STARTS WITH/ENDS WITH/CONTAINS, IS NULL/IS NOT NULL. 날짜 컬럼은 'YYYY-MM-DD' 문자열과 직접 비교(`date()` 없음).
- 쓰기(저장 그래프만): CREATE(노드·관계·속성), MERGE, SET, REMOVE, DELETE, DETACH DELETE. 가상 노드는 읽기 전용.
- 함수(자동완성·NL 목록 34개): count, sum, avg, min, max, collect, id, elementId, labels, type, length, size, toUpper, toLower, trim, substring, replace, split, coalesce, abs, ceil, floor, round, sqrt, rand, toString, toInteger, toFloat, timestamp, datetime, exists, keys. 튜토리얼에는 추가로 vector.similarity, vector.distance, genai.vector.encode.
- 미지원(튜토리얼 명시): `EXISTS { … }`, `CALL { … }` 하위 질의, `WHERE n:Label`, `date()`.
- 알려진 제약: 소수 컬럼 `sum()`을 WITH 뒤에서 거르면 `invalid input syntax for type bigint` → `sum(toFloat(x))`.
- 그래프·패브릭 문장(엔진이 처리): `CREATE GRAPH <g>`, `SHOW DATASOURCES`, `CREATE DATASOURCE <n> WITH ENGINE = '<e>', PARAMETERS = {…}`, `SHOW TABLES FROM <ds>`, `SHOW COLUMNS FROM <ds>.<t>`, `REFRESH DATASOURCE <ds>`, `DROP DATASOURCE <ds>`, `CREATE VIRTUAL NODE <L> IN <g> FROM <ds>.<t> KEY <col> [PROPERTIES (c, c AS p, …)]`, `CREATE VIRTUAL RELATIONSHIP <R> IN <g> FROM <A>(<col>) TO <B>(<col>)`, `SHOW VIRTUAL NODES [IN <g>]`, `SHOW VIRTUAL RELATIONSHIPS [IN <g>]`, `DROP VIRTUAL NODE|RELATIONSHIP <n> IN <g>`, `EXPLAIN FABRIC <cypher>`(행: step, place, operation, rows, detail). 엔진에는 이 밖에 GRAPHS 목록·MATERIALIZE·USE 토큰도 보인다(상세 미확인).
- 오류 교정: 모르는 라벨·변수·속성 등은 메시지 끝에 `did you mean: a, b` 형식 후보 — UI가 칩으로 보여 준다.

## 10. 오류·예외
| 상황 | 표시 |
|---|---|
| DB 연결 실패 | 연결 점 회색, 정보 박스 "not connected" + 오류 |
| Cypher 오류 | Error 탭 + 메시지(+ Did you mean 칩), 상태 "failed" |
| 다른 출처의 요청 | 403 cross-origin |
| raw SQL 꺼짐 | 403 문구 그대로 Error 카드 |
| AI 키 없음 | 디자이너 출력 박스에 503 문구 |
| 스키마 변경 검증 위반 | 항목 blocked + 위반 수 + 샘플 id, Retry/Abort |
| 스키마 변경 단계 실패 | 항목 failed + 메시지, 이후 항목 실행 중단 |
| NL: 비CLI 에이전트, 부팅 중, 그래프 없음, 스키마 없음, 에이전트 실패·시간 초과 | 막대(빨강) "바꾸지 못했습니다. <메시지>" |
| NL: 시험 실행 실패(수리 후에도) | 막대 "그래프에서 실패하는 Cypher 입니다 …" + 오류, 실행 안 함 |
| 서버 비루프백 바인드 | 시작 거부 메시지 후 종료 |
| 풀 연결 끊김 | 로그만, 다음 요청에서 재연결 |

## 11. 원본과 비교할 테스트 항목
결정적 기능(Cypher 실행)은 **결과 값까지**, 에이전트 기능(NL·AI 제안)은 **구조·계약**(ADR-0010).
1. S2·S4·S9·S10의 튜토리얼 질의 결과가 행·순서·값까지 같다(컬럼 순서 포함).
2. `/api/cypher` 응답 필드 집합과 형태가 같다(rows, columns, elapsed_ms, compiled_sql, sql_fingerprint, at, graph{nodes, edges}). 쓰기 질의는 compiled_sql·fingerprint null.
3. 같은 질의를 시점만 바꿔 실행하면 지문이 같다. 응답 후 같은 연결의 시점 설정이 남지 않는다(시점 없는 다음 요청이 현재 값).
4. 그래프 투영: 노드/관계 판정 규칙, 끝점 없는 관계 제외.
5. 보안 규칙: Sec-Fetch-Site cross-site → 403, 다른 Origin → 403, 헤더 없음 → 허용, POST에 text/plain → 415, 비루프백 바인드 거부.
6. raw SQL 꺼짐 403 문구, AI 키 없음 503 문구 동일.
7. 콘솔 명령 각각의 카드 탭 구성과 상태줄 문구.
8. 결과 카드 탭 순서 규칙(Graph 조건부, SQL 조건부), 저장(50)·기록(100) 상한, `:param` 값 비기록.
9. 시간 막대: 안내 문구 두 가지, "as known at" 옵션 형식, 배지 형식.
10. 디자이너: 변경 9종의 메뉴 진입, 쌓기·지도 표시, Review 문구, Run 단계 순서(다시 쓰는 종류만 migrate), blocked/failed 처리, Clear 시 abort.
11. AI 제안 응답 형식 `{explanation, changes[{change, ok, problem}], model, elapsed_ms}`과 서버 검사 문구.
12. NL: 질문 판정 규칙(키워드 목록), 가로채기(⌘Enter/▶/⇧⌘Enter/✨), IPC 요청·응답 필드, 쓰기 판정 단어 목록, 시험 실행 여부, 수리 최대 1회, 막대 문구 3종, 오류 문구(비CLI·빈 질문·그래프), 에이전트 호출에 도구가 없음.
13. 릴리스: 패키지 형식과 해시 계산(같은 그래프 두 번 내보내면 해시 동일), plan 집계, 해시 불일치 거부, 같은 패키지 재적용 시 already_applied.
14. 셸: 여는 경로 4가지, 외부 브라우저 URL, 포털 탭 제목, 외부 브라우저에서 ✨ 없음.

## 12. 모르는 점 (4단계 실행 기록에서 확인)
1. **Bolt 게이트웨이 인증 방식:** NL 경로의 basic 인증(`og`/비밀번호)을 게이트웨이가 그대로 PG 로그인에 쓰는지, 별도 검증인지(정적 분석으로는 추정). A2와 함께 확인.
2. 패브릭 문장(`SHOW …`, `EXPLAIN FABRIC`, `CREATE GRAPH`)의 `/api/cypher` 응답 형태 — rows/columns가 어떻게 오는지, compiled_sql이 null인지, 감사 기록 `lang`.
3. `og_schema` 실제 JSON 형태(특히 관계 타입의 키 이름 `relation_types` vs `relationship_types`, roles/from/to, 속성 key 표시)와 `stats` 형태.
4. 처음 열 때 기본 그래프(이름순 첫 = `ontology` 추정)와 앱 탭·외부 브라우저 간 저장소 공유 여부.
5. 앱 안에서 AI assist가 정말 꺼져 있는지(셸 환경에 OPENAI_API_KEY가 있으면 켜질 수 있음), raw SQL 403 여부.
6. 가상 노드에서 더블클릭 확장·검사기 history의 동작, 가상 관계의 `_src/_dst` 표현(그래프 보기에 간선이 그려지는지 — 튜토리얼 그림은 그려짐).
7. `/api/diagnose`·`/api/explain` 실제 응답 형태(steps 항목 필드, plan 구조).
8. 감사 기록에 Studio·Bolt·NL 시험 실행 질의가 섞여 보이는지, `principal`·`actor` 값, `query` 앞 `[...]` 접두의 의미.
9. NL: 에이전트 응답 시간 분포, 수리 비율, 앱 로그 줄 실제 형식, Codex 선택 시 동작 차이, 도구 없는 호출이 실제로 도구를 쓰지 않는지.
10. 시간 여행: `valid_at`에 잘못된 날짜 문자열을 주면 어떤 오류인지, 시간 버전 없는 타입의 동작(현재 값 반환) 확인, 「as known at」 목록에 다른 그래프 쓰기가 섞이는지.
11. 스키마 변경을 가상 타입(`sample`)에 시도했을 때의 오류, 디자이너 새로 고침 시 남은 서버 계획 처리.
12. 릴리스 API의 실제 사용처(Studio 백엔드가 쓰는지) — M1/M6 분석 시 확인.
13. 벤치마크 페이지가 배포본에서 빈 보고서인지.
14. Studio 화면의 포털 iframe에 그래프(예: `ontology`)가 전달되는지(iframe URL에 그래프가 안 붙는 것으로 보임).

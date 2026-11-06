# F4. 그래프 콘솔 (원본 「Ontological Portal」)

- 상태: 초안 v0.1 (2026-11-01, Claude 작성) — 사용자 보정 전
- 원본 기준: `../../analysis/ontological-studio/menus/04-portal/design.md`, `user-scenarios.md` (S1–S15)
- 관련: [01 §2 목표 구조](../01-architecture.md), [02 §12 Object set](../02-ontology-model.md), [02 §16 발행 컴파일](../02-ontology-model.md), [03 §3 세션 토큰](../03-security.md), [04 §3 단일 LLM 클라이언트](../04-agent-integration.md), [F1](F1-ontology-build.md)(스키마 편집·내보내기), [F3](F3-datasources.md)(패브릭 문장)

---

## 1. 목적
발행된 온톨로지를 **직접 질의하고 들여다보는** 고급 사용자용 콘솔.
- Cypher(와 읽기용 패브릭 문장)를 실행해 결과를 그래프·표·JSON·컴파일 SQL로 본다.
- **Object set DSL**(02 §12)을 실행해 객체 단위 결과를 본다(신규 탭).
- 발행된 버전의 **Object type·Link type 스키마 지도**를 본다.
- 같은 질의를 **시점(유효 시간·기록 시간)** 만 바꿔 다시 실행한다.
- 한국어 질문을 Cypher(또는 Object set)로 바꿔 실행한다.

업무 사용자의 질의는 F2(에이전트)와 F5(Object view)가 맡는다. 콘솔은 "엔진이 실제로 무엇을 보고 있는지" 확인하는 도구다.

## 2. 원본 기준 동작 요약 [원본]
근거: 분석 `menus/04-portal/design.md` §1–§11.
- **별도 서버**(Node, 루프백)가 PG에 **슈퍼유저로 직접** 접속해 엔진 SQL 함수를 호출. 앱 탭 또는 시스템 브라우저로 열림. 인증 없음(같은 출처·JSON 강제로만 보호, REVIEW #7).
- 어두운 테마 전용. 왼쪽 레일: Database schema / Saved queries / Query log / Schema changes(⇄) / Help / Benchmark.
- 입력: `$` 프롬프트, ⌘/Ctrl+Enter 실행, ↑/↓ 기록(100), ★ 저장(50), 문법 색, 자동완성(라벨·관계·속성·키워드·함수 34개).
- 결과 카드: Graph(노드가 있을 때)·Table·JSON·SQL(컴파일 SQL이 있을 때), 상태줄 `N row(s) · n nodes · m relationships · server X ms · round trip Y ms · compiled SQL <지문>`. 오류 시 "Did you mean" 칩.
- 콘솔 명령: `:clear :param :params :sql :explain :why :schema :changes :snapshot :releases :timeline`.
- 시간 여행 막대: `valid at`(자유 문자열), `as known at`(전역 최근 쓰기 30건 — 그래프로 거르지 않음), 지문은 시점과 무관하게 같음.
- 스키마 디자이너(⇄): 스키마 지도 + 변경 9종 쌓기 → Review impact → Run(plan→expand→migrate→validate→contract).
- 자연어→Cypher: **앱 탭 + CLI 에이전트**일 때만. 셸 메인이 스키마 압축 → 도구 없는 단발 호출 → 쓰기 판정 → 읽기면 1회 시험 실행 → 실패 시 1회 수리 → 성공이면 자동 실행.
- 앱에서 꺼진 기능: raw SQL(`:sql`), 스키마 AI 제안. 화면 없는 기능: 릴리스 패키지 API(export/plan/apply)(REVIEW #8).

## 3. 새 설계에서 달라지는 점 [제안]
| # | 원본 | 새 설계 | 근거 |
|---|---|---|---|
| C1 | 별도 포털 서버 프로세스, PG 슈퍼유저 직접 접속 | **메인 UI의 한 화면**(`view=console`). 코어 API `/api/v1/graph/*`를 씀. 읽기는 `wb_read` 역할(03 §6) | 01 §2.1 (프로세스 9→4), S5 |
| C2 | 무인증 | 세션 토큰(쿠키). 외부 브라우저로 열기는 **일회용 링크**(03 §3) | S1 |
| C3 | Cypher 쓰기 자유 | **읽기 전용 기본**. 쓰기는 설정(F8)에서 켠 경우에만, 그리고 **발행 관리 그래프에는 여전히 거부**(§3.2) [결정 대기 D-20] | 원칙 2 |
| C4 | 대상 = 그래프 이름(`default`, `ontology`, `sample` …) | 대상 = **온톨로지 + 발행 버전**(기본) 또는 원시 그래프(고급). 온톨로지 대상에서는 짧은 라벨(`Shipment`)을 이름공간 라벨(`SupplyChain.Shipment`)로 풀어 준다(§3.1) | 02 §3 이름공간 |
| C5 | 스키마 사이드바·지도 = 엔진 타입 계층 | **발행된 Object type·Link type·Interface** 지도(저장 방식·카디널리티·백킹 표시). 엔진 타입 계층은 원시 그래프 대상에서만 | 02 §5·§8·§9 |
| C6 | 스키마 디자이너(⇄, 단계 실행) | **F1 설계 화면으로 흡수**. 콘솔의 ⇄ 패널은 「버전·변경 이력」(읽기 전용)으로 바뀜 [결정 대기 D-19] | D-19 권장안 |
| C7 | 릴리스 패키지 API(화면 없음) | **온톨로지 내보내기/가져오기(YAML)**(F1, 02 §14). `:releases` → `:versions` | D-19 권장안 |
| C8 | NL→Cypher는 CLI 에이전트 + 앱 탭에서만, 셸 메인에서 실행 | 코어 Agent 모듈의 **단일 LLM 클라이언트**로 실행(CLI·내장 어느 쪽이든). 외부 브라우저에서도 동작. 검증·1회 수리 루프 유지 | 04 §3 |
| C9 | 없음 | **Object set DSL 탭**(신규) | 02 §12 |
| C10 | 「as known at」 목록 = 전역 쓰기 | 현재 대상(온톨로지/그래프)의 쓰기로 거름 + 발행 버전 시각을 함께 보여 줌 | 원본 결함(D-12) |
| C11 | 저장 질의·기록 = 브라우저 저장소(출처별 분리) | 코어 `workbench.runtime`에 저장 → 앱 탭·외부 브라우저 공유. `:param` 값은 여전히 저장 안 함 | 일관성 |
| C12 | raw SQL(`:sql`) — 앱에서는 꺼짐 | **제공하지 않음**(명령은 남겨 안내 카드). 엔진 내부 SQL 접근은 개발 빌드 전용 [제안] | 원본 앱 동작과 같음 + 보안 |
| C13 | 벤치마크 페이지 | 제외(배포본에서 빈 보고서, 튜토리얼 없음) | 범위 축소 |
| C14 | 스키마 AI 제안(OpenAI 키 직접) | 제외 — F1의 build 모드 에이전트가 같은 역할(작업본 편집) | 04 §3 단일 클라이언트 |

### 3.1 대상과 라벨 해석
- 상단 「대상」 선택:
  - **온톨로지**(기본): `<표시 이름> · v<N>`(발행본만). 버전 선택(최근 10개 + 「모든 버전」). 과거 버전을 고르면 그 버전의 스키마 지도와 자동완성을 쓰고, 질의는 그 버전이 발행한 그래프 표현에 대해 실행한다(지난 버전의 컴파일 결과가 남아 있지 않으면 「이 버전은 스키마만 볼 수 있습니다」) [확인 필요 — 버전별 컴파일 결과 보존 범위는 F1].
  - **원시 그래프**(고급, 접힘): `sample`(예제, 튜토리얼 재현용), 사용자가 만든 연습 그래프, 발행 관리 그래프(읽기 전용, 라벨이 이름공간 형태 그대로).
- 온톨로지 대상의 라벨 해석 [제안]: 질의 안의 노드 라벨·관계 타입이 이름공간 없이 쓰이면 코어가 그 온톨로지의 apiName으로 풀어 쓴다(`(s:Shipment)` → ``(s:`SupplyChain.Shipment`)``, `[:purchaseOrder]` → 해당 Link type의 컴파일 관계 이름). Interface 라벨(`Partner`)은 구현 타입들의 합집합으로. 바뀐 질의 전문은 결과 카드의 「해석된 Cypher」 탭에 보인다. 풀 수 없는 이름은 원본처럼 `did you mean: …` 후보와 함께 오류.
- 속성 이름: Object type 속성 apiName(camelCase)을 쓴다. live 타입에서 원천 컬럼 이름으로 쓰면 「속성 이름을 쓰세요: ref_po_no → (없음), 비슷한 속성: purchaseOrderNo」 같은 후보 안내.

### 3.2 쓰기 정책 [결정 대기 D-20]
| 대상 | 설정 「콘솔 Cypher 쓰기」 꺼짐(기본) | 켬 |
|---|---|---|
| 온톨로지(발행 관리 그래프) | 거부 | **거부** — 객체 변경은 Action(편집 레이어·감사·승인)으로만. 「온톨로지 객체는 액션으로 바꿉니다. 질의·액션 화면을 쓰세요.」 |
| 원시 그래프 `sample`(가상 노드만) | 거부 | 엔진 규칙대로(가상 노드는 읽기 전용 오류) |
| 사용자 연습 그래프 | 거부 | 허용(`CREATE GRAPH`, CREATE/MERGE/SET/REMOVE/DELETE/DETACH DELETE, 비관리 그래프의 가상 타입 DDL) |
- 쓰기 판정은 키워드 검사가 아니라 **엔진 수준**: 읽기 요청은 읽기 전용 트랜잭션 + `wb_read` 역할로 실행해 엔진이 거부하게 한다. 키워드 검사(원본 쓰기 단어 목록)는 UI 사전 경고용으로만.
- 쓰기가 켜져 있어도 실행 전 **확인 막대**(웹 UI, 네이티브 창 아님): 「데이터를 바꾸는 문장입니다. 대상: <그래프>. 실행할까요?」 [제안]. 감사 `actor = human`, `source = console`.
- 튜토리얼 09장(직접 쓰기)과 10장(시간 여행 준비) 재현은 연습 그래프 + 쓰기 켬으로 한다.

## 4. 사용자 시나리오
| # | 시나리오 | 원본 | 새 기대 결과 요약 |
|---|---|---|---|
| S1 | 콘솔 열기·화면 구성 | S1 | 홈 카드 「그래프 콘솔」, 메뉴, 트레이, 데이터소스 화면 링크 → 같은 창의 탭(`view=console`). 「브라우저에서 열기」는 일회용 링크 |
| S2 | Cypher 기초 | S2 | `sample` 대상: 튜토리얼 실측 결과 그대로(예: Supplier 5행 순서·값, OPEN 발주 6건). 온톨로지 대상: 같은 질문을 속성 apiName으로 써서 같은 값 |
| S3 | 결과 카드·입력 보조 | S3 | 탭 구성·상태줄·★(50)·기록(100)·자동완성 같음. 자동완성 후보에 표시 이름·설명 힌트 추가 |
| S4 | 관계·집계 | S4 | `sample`에서 원본 값 그대로. 온톨로지 대상에서 Link type 이름으로 같은 결과 |
| S5 | 그래프 상호작용 | S5 | 검사기·더블클릭 확장 같음. 검사기에 「Object view 열기」(F5) 추가 |
| S6 | 실행 들여다보기 | S6 | SQL 탭·지문·`EXPLAIN FABRIC`·`:explain`·`:why` 같음 + 「해석된 Cypher」 탭 |
| S7 | 패브릭 문장 | S7 | `SHOW …` 읽기 문장 실행 가능. `CREATE DATASOURCE`는 거부 + 데이터소스 화면 안내 |
| S8 | 자연어 → Cypher | S8 | CLI·내장 어느 에이전트로도 동작. 응답 계약·막대 문구 3종·쓰기 미실행·1회 수리 같음 |
| S9 | 직접 쓰기 | S9 | 기본 거부(의도된 차이). 설정에서 켜고 연습 그래프에서 원본과 같은 결과 |
| S10 | 시간 여행 | S10 | 연습 그래프 `hr`(쓰기 켬 + 시간 버전): 다섯 조합 결과 4700/4000/4700/4600/없음, 지문 동일 |
| S11 | 스키마 지도·변경 | S11 | 지도는 발행된 Object/Link type(읽기 전용). 변경은 F1으로 이동(「구축 화면에서 고치기」) |
| S12 | 콘솔 명령 | S12 | §5.6 표(유지·변경·제거) |
| S13 | 기록·도움말·오류 제안 | S13 | 같음. Query log는 코어 감사에서 이 대상·콘솔 출처로 거름 |
| S14 | 벤치마크 | S14 | 제외 |
| S15 | 릴리스 API | S15 | F1 내보내기/가져오기로 대체 |
| N1 | Object set DSL 실행 | 신규 | `{base:{objectType: Shipment}, filter: "delayDays > 3", traverse:[{link: purchaseOrder},{link: supplier}]}` → 협력사 객체 목록, 각 행 「Object view」 |
| N2 | 질문 → Object set | 신규 | DSL 탭에서 「3일 넘게 늦은 선적의 협력사」 → DSL 생성·검증·실행 |
| N3 | 과거 버전 스키마 보기 | 신규 | 버전 v2 선택 → 지도에 v2 타입, 현재 대비 차이 배지(추가/삭제/변경) |
| N4 | Object set 저장 | 신규 | 결과 카드 ★ → 「Object set으로 저장」(이름·설명) → rid, F5 위젯에서 사용 |
| N5 | 외부 브라우저 열기 | S1 일부 | 메뉴 「그래프 콘솔을 브라우저에서 열기」 → 기본 브라우저 + 일회용 링크(60초) → 쿠키 교환 → 같은 기능(NL 포함) |

## 5. 화면 구성과 상호작용

### 5.1 레이아웃
원본 배치를 유지하되 메인 UI의 테마(밝음/어두움)를 따른다(원본은 어두운 테마 전용 — 의도된 차이).
- **왼쪽 레일**: 스키마 / 저장 질의 / Query log / 버전·변경 이력(⇄ 대체) / 도움말 / 아래쪽 연결 점(코어 그래프 상태).
- **상단 막대**: 「대상」 선택(§3.1), 버전 선택, 모드 탭 **[Cypher | Object set]**.
- **사이드바**(레일 선택에 따라):
  - *스키마*: 제목 「그래프 콘솔」 + 대상 정보 박스(`온톨로지 <apiName> · v<N> · 발행 <날짜>`, 엔진 이름·버전, PG 버전; 실패 시 빨간 "not connected" + 오류 — 원본 문구). "Object types (click to query)" 칩(색·아이콘, 표시 이름, 객체 수 — live는 「live」 표시 후 수를 비동기로, 시간이 걸리면 「?」), "Link types" 칩(`from → to`, 카디널리티), "Interfaces" 칩(구현 타입 수), "Properties"(타입 선택 시 그 타입 속성: apiName · baseType · 필수 `*` · PII 🔒). 원시 그래프 대상이면 원본 사이드바(Entity types / Relationship types / Property keys / Type hierarchy) 그대로.
  - *저장 질의*: 원본과 같음 + 종류 아이콘(Cypher / Object set). 비면 "star a frame to save its query"(원본 문구).
  - *Query log*: 원본과 같은 행 형식(`N rows`/`error` · `x.x ms` · 시각). 최근 100건, 이 대상·콘솔 출처.
  - *버전·변경 이력*: 발행 버전 목록(`v<N> · <날짜> · <발행자> · 변경 요약`), 버전을 누르면 그 버전 대상으로 전환, 「차이 보기」(F1 제안 diff 화면으로).
  - *도움말*: 원본 스니펫을 새 대상 기준으로 갱신(`MATCH (n:Supplier) RETURN n LIMIT 25`, Link 따라가기, Object set 예, 시간 여행 설명, 명령 목록).
- **본문**: `$` 프롬프트 + 여러 줄 입력칸 + 버튼(⏱ 시간 여행, ✨ 자연어, ▶ 실행) → 시간 막대(숨김) → NL 상태 막대(숨김) → 결과 스트림(새 카드가 위).
- **검사기**(오른쪽 떠 있는 패널): 원본과 같음.

### 5.2 Cypher 입력과 실행
- 실행: ▶ 또는 ⌘/Ctrl+Enter, 앞뒤 공백 제거, 비면 무시(원본).
- 기록: `:param` 제외, 최대 100, ↑/↓ 탐색(입력칸 한 줄일 때)(원본). 저장 위치만 코어로(C11).
- 실행 후 입력칸 비움, 카드 제목 = 질의, 시점 설정 시 배지 `⏱ valid <값> · known <라벨>`(원본).
- 성공 카드 탭: **Graph**(노드 있을 때) · **Table** · **JSON** · **SQL**(컴파일 SQL 있을 때) · **해석된 Cypher**(라벨 해석이 일어났을 때, 신규). 상태줄 원본 형식 + 대상 `· v<N>`.
- 실패 카드: Error 탭, "Did you mean" 칩(원본 규칙: 메시지의 작은따옴표 이름을 후보로 바꿔 재실행).
- 카드 머리: ★ / ✕ / 탭(원본). ★ 은 Cypher 저장(50). Object set 카드의 ★ 은 N4.
- 클릭 실행 요소: 칩 질의 — Object type `MATCH (n:<Type>) RETURN n LIMIT 50`, Link type `MATCH (a)-[r:<link>]->(b) RETURN a, r, b LIMIT 50`(원본 형식, 라벨은 대상 기준).
- 결과 상한 [제안]: 행 1,000(넘으면 `truncated` + 「LIMIT을 쓰세요」), 시간 30초(설정에서 조정), 응답 10MB.

### 5.3 결과 보기 (원본 유지)
- Table·Graph·검사기 규칙은 원본 §4.3과 같다(캡션 우선순위 `name`→`title`→`label`→`model`→`id`→타입은 **titleKey 속성 → 원본 순서**로 바꿈).
- 노드 색: Object type `color`가 있으면 그것, 없으면 원본 해시 팔레트.
- 검사기 버튼: "expand neighbours"(원본), "history"(원본은 raw SQL이라 앱에서 오류 → **타임라인 API로 대체**, 시간 버전·편집 레이어 이력 표시), **「Object view 열기」**(F5, 온톨로지 대상일 때).
- PII 속성 값: 콘솔은 사람 사용자의 로컬 화면이므로 값 표시. 단 카드 복사·내보내기 때 PII 속성 포함 여부를 묻는다 [제안]. LLM에는 절대 보내지 않음(§8).

### 5.4 입력 보조
- 문법 색·자동완성 규칙은 원본 §4.4와 같다. 후보 원천: 온톨로지 대상이면 발행 레지스트리(Object type apiName·Link type 방향 이름·속성 apiName, 힌트에 displayName), 원시 그래프면 엔진 스키마.
- 이름이 `_`로 시작하는 내부 타입·속성 숨김(원본).
- 키워드 후보에서 쓰기·DDL 구문(`CREATE`, `MERGE`, `DETACH DELETE`, `CREATE VIRTUAL …`)은 쓰기 설정이 켜져 있을 때만.

### 5.5 시간 여행 막대
- 원본 구성·문구 유지: "Time travel", `valid at`(자리 표시 "now — e.g. 2026-08-15"), `as known at`(첫 항목 "now"; 이후 `after HH:MM:SS.mmm · <actor> — <질의 앞 54자>`), 안내 문구 두 가지, "clear". 설정 시 입력칸 노란 테두리.
- **변경**:
  - `as known at` 목록은 **현재 대상의 쓰기만**(C10), 최근 30건 + 「발행 v<N>」 시각 항목들(그 버전 발행 직후 시점).
  - 온톨로지 대상의 쓰기 항목 actor는 `사람 <이름>` / `에이전트(<모드>)` / `시스템(동기화)`로 표시(03 §4 actor 구분).
  - `valid at` 값 검증: ISO 날짜/시각 또는 `now`. 형식이 틀리면 실행 전 「날짜 형식이 아닙니다: <값> (예: 2026-08-15)」 [제안 — 원본은 자유 문자열].
  - 안내 문구의 활성화 힌트 `enable with og_enable_temporal(graph, type)`는 온톨로지 대상에서는 「시간 버전은 Object type 설정에서 켭니다(온톨로지 구축)」로 바꿈. 원시 그래프 대상에서는 원본 문구.
- 요청 `at = {valid_at?, system_at?}`, 질의 텍스트는 바꾸지 않음, 응답 후 세션 시점 설정 초기화(원본 §5.1-7 규칙 유지).
- live Object type에는 시점 데이터가 없다 → 시점이 설정된 채 live 타입을 질의하면 현재 값 + 카드 경고 「live Object type <이름>은(는) 시점 조회를 지원하지 않아 현재 값을 보여 줍니다.」 [제안]

### 5.6 콘솔 명령
| 명령 | 처리 | 원본 대비 |
|---|---|---|
| `:clear` | 결과 스트림 비움 | 같음 |
| `:param <n> => <v>`, `:params`, `:params clear` | 원본 문구·규칙 그대로, 페이지 메모리에만 | 같음 |
| `:explain <cypher>` | SQL·Plan 탭 | 같음 |
| `:why <cypher>` | Diagnosis(Compile check / Pattern walk / Estimate) | 같음 |
| `:schema` | 온톨로지 대상: `describe_ontology` 결과(04 §5) JSON + 상태 "machine-readable schema — this is what an agent sees"(원본 문구, 실제로 에이전트 도구와 같은 출력) / 원시 그래프: 원본 | 내용 변경 |
| `:snapshot [N | 시각]` | 온톨로지 대상: 버전 N의 Object/Link type 표(type, kind, property, baseType, backing) / 원시 그래프: 원본 | 내용 변경 |
| `:versions` | 발행 버전 표(#, 발행 시각, 발행자, 제안 id, 변경 수, 골든 결과) | `:releases` 대체 |
| `:changes` | 온톨로지 대상: 최근 제안 목록(id, 상태, 요약) / 원시 그래프: 원본 스키마 변경 기록 | 내용 변경 |
| `:timeline <Type> <prop>=<key> [from] [to] [@system_at]` | 원본 형식·카드(Timeline·Table·JSON). 온톨로지 대상에서는 `<Type>`=Object type apiName, `<prop>=<key>`는 기본 키. 편집 레이어 변경도 막대에 표시 | 확장 |
| `:objects <DSL JSON>` | Object set DSL 탭과 같은 실행을 Cypher 입력칸에서 | 신규 |
| `:sql …` | 안내 카드 「raw SQL은 이 플랫폼에서 제공하지 않습니다.」 | 제거(원본 앱도 꺼짐) |
| `:releases` | 안내 카드 「`:versions`를 쓰세요. 패키지 내보내기는 온톨로지 구축 › 내보내기에서.」 | 대체 |

### 5.7 Object set DSL 탭 (신규)
- 입력: YAML 또는 JSON 편집기(02 §12 스키마 기반 자동완성·검증 — `base.objectType` 후보, `filter` 식의 속성 이름, `traverse.link` 후보는 현재 타입 기준). 필터 식 문법은 02 §7.5.
- 예시 버튼: 「지연 선적」, 「협력사별 발주」, 「거래처(Interface) 중 JP」.
- 실행 → `POST /api/v1/object-sets/query`. 결과 카드 탭:
  - **Objects**: 표(열 = titleKey + 속성 선택, 기본은 Object view의 주요 속성), 행 클릭 → 검사기(속성·원천 표시·편집 레이어 값 표시), 「Object view 열기」.
  - **Graph**: traverse가 있으면 경로 그림.
  - **Plan**: 코어 번역 결과 — 저장 방식별 실행 계획(live → 원천 질의 요약, indexed/native → Cypher 원문). 「Cypher로 열기」(Cypher 탭에 붙여 넣기).
  - **JSON**: 응답 원문.
- 상태줄: `N objects · <저장 방식 요약> · server X ms`.
- ★ → 「Object set으로 저장」(N4): 이름(`camelCase`)·표시 이름·설명 → 작업본이 아니라 **런타임 저장 Object set**(02 §12 "저장하면 rid") [확인 필요: 저장 Object set이 온톨로지 정의(발행 대상)인지 런타임 자산인지 — §12].
- 시간 여행 막대의 값은 `asOf`로 넘긴다(02 §12).

### 5.8 자연어 → Cypher / Object set
**트리거와 판정**(원본 유지):
- ✨ 버튼(툴팁 「자연어로 묻기 — 에이전트가 Cypher 로 바꿔 실행합니다 (⇧ + ⌘/Ctrl + Enter)」 — 원본 문구에서 "CLI 에이전트"를 "에이전트"로), ⇧⌘Enter는 항상 번역. ▶/⌘Enter는 **질문 판정** 규칙(원본 §4.7: 맨 앞 `//` 줄 제거, `:`·`(` 시작 아님, Cypher 시작 키워드 목록 아님)에 맞으면 번역.
- DSL 탭에서는 ✨가 Object set DSL을 만든다.

**처리 흐름**(코어, `POST /api/v1/graph/nl2cypher`):
1. 사전 검사(원본 문구 유지): 빈 질문 「질문이 비어 있습니다.」, 대상 없음 「그래프를 고르세요.」, 부팅 중 「아직 시작하는 중입니다.」, 에이전트 미준비 「에이전트를 쓸 수 없습니다. 설정에서 에이전트나 LLM 키를 정하세요.」(원본의 「CLI 에이전트로 동작합니다…」 오류는 **없어짐** — 내장 에이전트도 지원).
2. 스키마 압축: 온톨로지 대상이면 발행 레지스트리에서 `{objectTypes:[{label, displayName, aiDescription(200자), properties:["apiName:baseType"], implements?}], linkTypes:[{type, from, to, cardinality}], interfaces:[…]}`. PII 속성은 이름만(값·예시 없음). 원시 그래프면 원본 규칙(내부 타입·속성 제외, 가상 관계 join·노드 source 보강).
3. 프롬프트: 원본 시스템 지시 요지 유지(한 문장, cypher 코드 블록 + 한국어 한 줄, 허용 절·함수 목록, 패턴의 모든 노드에 라벨, 관계 방향, WHERE 라벨 조건 금지, 질문이 요구하지 않으면 쓰기 금지, 이름 붙인 컬럼, LIMIT 100) + 온톨로지 대상이면 「라벨은 Object type apiName, 관계는 Link type 방향 이름」.
4. **단일 LLM 클라이언트** 호출(04 §3): Agent 모듈의 `complete(system, user, {tools: none, timeoutSec: 180})`. 현재 에이전트가 CLI면 원본처럼 빈 임시 폴더·도구 없는 단발 실행, 내장이면 설정한 LLM의 작은 모델(F8). 어느 쪽이든 **도구 없음**.
5. 추출: 첫 코드 블록(cypher/sql/무표시) → Cypher, 끝 세미콜론 제거, 블록 뒤 첫 줄 = note. 비면 「에이전트가 Cypher 를 내지 못했습니다.」(원본).
6. 쓰기 판정: 원본 단어 목록(CREATE, MERGE, DELETE, DETACH, SET, REMOVE, DROP, REFRESH, ALTER, GRANT, REVOKE, LOAD, FOREACH) → `write=true`, 시험 실행 없이 반환(원본).
7. 시험 실행: 읽기 전용 트랜잭션으로 1회 실행(결과 버림), 20초 넘으면 성공 간주(원본). 오류는 `ERROR:` 이후 400자.
8. **수리 1회**: 원본과 같은 형식으로 오류를 붙여 재호출 → 재추출 → 재시험. 또 실패면 `{repaired:true, checked:false, error}`.
9. 응답 `{cypher, note, agent, ms, repaired, checked, write, error?}` — **원본 필드 그대로**. 추가 필드 `resolvedCypher`(라벨 해석 후), `target`.
- Object set 버전(`POST /api/v1/object-sets/nl`)도 같은 흐름: 출력 = DSL JSON 코드 블록, 시험 = 검증(02 §17식 정적 검증 + `limit 1` 실행), 수리 1회, 응답 `{objectSet, note, agent, ms, repaired, checked, error?}`(`write`는 항상 false).

**화면 처리**(원본 유지): 입력칸을 받은 질의로 교체, 메타 `<에이전트 이름> · <초> s`(+ `· 한 번 고침`).
- `error` → 빨강 「그래프에서 실패하는 Cypher 입니다 — 고쳐서 실행하세요.」, 실행 안 함.
- `write` → 경고 「데이터를 바꾸는 문장이라 실행하지 않았습니다. 확인한 뒤 ▶ 로 실행하세요.」(쓰기 설정이 꺼져 있으면 뒤에 「콘솔 쓰기가 꺼져 있습니다(설정).」).
- 정상 → `자연어` 태그 + 질문 + note + 메타(+ `· 그래프에서 확인됨`), 즉시 실행.
- 예외 → 「바꾸지 못했습니다. <메시지>」.
- 감사: NL 호출 1건(actor = human, via = agent 단발), 시험 실행 질의는 Query log에 `nl-check` 태그로(원본은 섞여 보이는지 미확인).

### 5.9 스키마 지도 (원본 ⇄ 지도 대체, 읽기 전용)
- 레일의 스키마 영역 상단 「지도로 보기」 또는 `:map` → 본문이 "Schema map" 모드(원본 이름 유지).
- 카드 = Object type: 색 점·아이콘, 표시 이름(apiName), 저장 방식 배지(`live`/`indexed`/`native`), 객체 수, 속성 행 `apiName(* 필수) · baseType · ← 원천 컬럼/식`(원본의 `name · type · column` 범례를 계승), 공유 속성은 `⇢ <SharedProperty>`.
- 선 = Link type: `from → to` 곡선 + 방향 이름 + 카디널리티(`1..*`), 조인 방식 아이콘(fk / join / link-object / stored). Interface는 점선 상자로 구현 타입을 묶음(원본 extends 곡선 자리).
- 배치: Type group 별 묶음 → 그 안에서 Link 연결 밀도 순(원본 계층 트리 배치 규칙은 Interface 구현에 사용).
- 상호작용: 카드 클릭 → 칩 질의 실행, 「구축 화면에서 고치기」 → F1 편집기(해당 타입), 「Object set」 → DSL 탭에 `{base:{objectType}}`.
- 범례: 원본 "extends/staged/to remove"는 "버전 비교" 토글로 대체 — 현재 대상 버전과 바로 앞 버전(또는 작업본)의 차이를 추가(강조)/삭제(흐림)/변경(취소선 → 새 값)으로 그림(원본 쌓인 변경 표시 규칙 재사용).
- 편집 기능 없음(D-19: 디자이너는 F1).

## 6. API
모두 코어 `/api/v1`, 세션 토큰 필수, JSON. 원본 포털 API(`/api/cypher` 등)와 **필드 형태를 맞춘다**.

| 메서드 경로 | 요청 | 응답 | 원본 대응 |
|---|---|---|---|
| GET `/graph/targets` | — | `{ontologies:[{rid, apiName, displayName, versions:[{n, publishedAt}]}], graphs:[{name, managed, temporal}]}` | `/api/health`의 graphs |
| GET `/graph/health` | — | `{ok, engine:{name, version}, database, server}` | `/api/health` |
| GET `/graph/schema?target=` | — | 온톨로지: `{ontology, version, objectTypes, linkTypes, interfaces, stats}` / 그래프: 원본 `{schema, stats}` | `/api/schema` |
| POST `/graph/cypher` | `{target, version?, query, params?, at?:{valid_at?, system_at?}}` | `{rows, columns, elapsed_ms, compiled_sql, sql_fingerprint, at, graph:{nodes, edges}, resolved_query?, truncated}` | `/api/cypher` (필드 같음 + 2개) |
| POST `/graph/explain` | `{target, query, analyze?}` | `{sql, plan, columns}` | 같음 |
| POST `/graph/diagnose` | `{target, query}` | 원본 형태 | 같음 |
| POST `/graph/expand` | `{target, id, limit?:50}` | `{nodes, edges}` | 같음 |
| GET `/graph/temporal?target=` | — | `{types, writes:[{at, actor:{kind,id,label}, source, query}], versions:[{n, at}]}` | `/api/temporal` (대상으로 거름) |
| GET `/graph/timeline?target&type&key_prop&key&from&to&system_at` | — | `{slices:[…원본 필드…, edit?:{actionRun, property}]}` | `/api/timeline` |
| GET `/graph/audit?target=&limit=100` | — | 원본 행 형태 `[{audit_id, principal, at, query, lang, rows_out, duration_ms, error_code}]` + `actor_kind`, `origin` | `/api/audit` |
| POST `/graph/nl2cypher` | `{question, target, version?}` | `{cypher, note, agent, ms, repaired, checked, write, error?, resolvedCypher?, target}` | IPC `lite:nl2cypher` |
| POST `/object-sets/query` | `{objectSet: DSL, select?: [prop], pageToken?, pageSize?: 100}` | `{objects:[{objectType, pk, title, properties, sources?}], nextPageToken?, plan, elapsed_ms}` | 신규(01 §4) |
| POST `/object-sets/nl` | `{question, ontology}` | §5.8 | 신규 |
| POST `/object-sets` | `{name, displayName, description, objectSet}` | `{rid}` | 신규 |
| GET/POST/DELETE `/console/saved`, `/console/history` | 저장 질의(50)·기록(100) | | 브라우저 저장소 대체 |
- 제거: `/api/sql`, `/api/schema-type`, `/api/schema-assist`, `/api/schema-change(s)`, `/api/schema-snapshot`(→ `/graph/schema?version=`), `/api/schema-temporal`, `/api/schema-diff`, `/api/release/*`, `/api/releases`, `/api/benchmark`. 스키마 변경·내보내기는 F1 API.
- 오류: 원본 `{error, code, detail, hint, where}` 형태 유지. 빈 질의 400 `{error:"empty query"}`(원본). 쓰기 거부 403 `{error:"write is disabled for this target", hint}`. 시간 초과 408.
- 보안 헤더 검사(원본 `Sec-Fetch-Site`·`Origin` 규칙)는 게이트웨이의 공통 검사(P §6)로 일반화. 원본의 `content-type must be application/json`(415) 유지.

## 7. 데이터
- **대상(Target)**: `{kind: ontology, rid, version} | {kind: graph, name}`.
- **발행 레지스트리**(02 §16)를 읽어 스키마·자동완성·라벨 해석·NL 프롬프트를 만든다. 콘솔은 메타를 쓰지 않는다.
- **저장 질의/기록**: `workbench.runtime.console_saved {id, kind: cypher|objectset, title, body, target, createdAt}`(50), `console_history`(100, `:param` 제외).
- **Object set**(저장): 02 §12. 저장 위치 열린 질문(§12-2).
- **감사**: 콘솔 질의(읽기 포함)는 엔진 감사(원본처럼) + 쓰기는 `workbench.audit`(actor, source = console).
- 그래프 요소 JSON(`{_id, _type, …}`/`{_id, _type, _src, _dst, …}`)은 원본 계약 유지. 온톨로지 대상에서는 `_type`이 이름공간 라벨, 응답에 `_objectType`(apiName)·`_pk` 추가 [제안].

## 8. 에이전트 연동
- 콘솔 자체는 에이전트 모드를 쓰지 않는다. NL 번역은 Agent 모듈의 **도구 없는 단발 호출**(§5.8) — 04 §4 모드 표 밖의 내부 호출로, 권한은 "읽기 스키마 텍스트를 받고 텍스트를 돌려줌"뿐.
- LLM에 보내는 것: 발행 스키마(이름·타입·설명), 질문, (수리 시) 오류 메시지. **데이터 값·PII·결과 행은 보내지 않는다.** 시험 실행 결과는 버린다(원본과 같음).
- 에이전트 도구 중 `cypher_readonly(query)`(04 §5, 설정으로 켬)는 이 콘솔과 같은 코어 경로(`/graph/cypher`, 읽기 전용 트랜잭션, 같은 라벨 해석)를 쓴다. `object_set_query(dsl)`도 같은 `/object-sets/query`.
- 외부 MCP: 콘솔 API를 직접 노출하지 않는다. `read` 범위 = Object set, `data` 범위 = live 값 포함(04 §8).

## 9. 보안·권한
- 세션 토큰(쿠키), Host/Origin 검사, CORS 없음(03 §3). 외부 브라우저는 일회용 링크 → HttpOnly 쿠키 교환, 링크 유효 60초·1회.
- 읽기 실행 역할 `wb_read`(03 §6) + 읽기 전용 트랜잭션 + `statement_timeout`. 원본의 슈퍼유저 직접 접속 제거(S5).
- 쓰기(설정 켬)는 별도 역할 `wb_console_write` — 연습 그래프에만 권한, 발행 관리 그래프·메타·감사 스키마 권한 없음 [제안, 03 §6에 역할 추가 필요].
- 쓰기 설정을 켜는 행위 자체는 네이티브 확인 창 증표 필요(F8 §9).
- `:param` 값은 저장·감사·LLM에 남기지 않는다(원본 원칙 유지: 감사의 query에는 `$name`만).
- 시점 세션 설정 누수 방지: 요청 끝에 반드시 RESET(원본 §5.1-7).
- 결과 상한(§5.2)으로 대량 추출 억제. 「내보내기」(CSV/JSON)는 상한 안에서만.

## 10. 오류·예외
| 상황 | 표시 | 원본 대비 |
|---|---|---|
| 엔진 연결 실패 | 연결 점 회색, 정보 박스 "not connected" + 오류 | 같음 |
| Cypher 오류 | Error 탭 + Did you mean 칩, 상태 "failed · Y ms" | 같음 |
| 라벨 해석 실패(온톨로지 대상) | 「Object type 또는 Link type이 아닙니다: 'Shipmnt' — did you mean: Shipment」(칩 동작 같음) | 신규 |
| 쓰기 거부(설정 꺼짐) | 「콘솔은 읽기 전용입니다. 쓰기는 설정 › 보안에서 켤 수 있습니다(연습 그래프 전용).」 | 신규 |
| 쓰기 거부(발행 관리 그래프) | 「온톨로지 객체는 액션으로 바꿉니다. 질의·액션 화면을 쓰세요.」 | 신규 |
| `CREATE DATASOURCE` 실행 | 「데이터소스 연결은 데이터소스 화면에서 합니다(비밀번호를 질의 기록에 남기지 않기 위해).」 + 링크 | 신규 |
| 가상 노드 쓰기 | 엔진 원문 `'<Label>' is a virtual node type and read-only: …` | 같음 |
| 결과 상한 초과 | 카드 상단 「1,000행까지만 보여 줍니다. LIMIT을 쓰세요.」 | 신규 |
| 시간 초과 | 「30초 안에 끝나지 않아 중단했습니다.」 | 신규 |
| `valid at` 형식 오류 | 「날짜 형식이 아닙니다: <값> (예: 2026-08-15)」 | 신규 |
| live 타입 시점 질의 | 카드 경고(§5.5) | 신규 |
| NL 오류 | 원본 막대 문구 3종 + 「바꾸지 못했습니다. <메시지>」 | 같음(비CLI 오류 제거) |
| `:sql`, `:releases` | 안내 카드(§5.6) | 원본 403 문구 대체 |

## 11. 원본과 비교할 테스트
결정적 기능은 결과 값까지, 에이전트 기능은 구조·계약(ADR-0010 방식).

**같아야 함**
1. `sample` 대상에서 튜토리얼 07·08장 질의(원본 S2·S4) 결과의 행·순서·값·컬럼 순서.
2. 온톨로지(예제) 대상에서 같은 질문을 속성 apiName으로 쓴 질의의 값이 1과 같다(예: OPEN 발주 금액 오름차순 6건 PO-007…PO-001).
3. `/graph/cypher` 응답 필드(rows, columns, elapsed_ms, compiled_sql, sql_fingerprint, at, graph{nodes, edges}).
4. 시점만 바꾼 실행의 지문 동일, 응답 뒤 시점 설정 비누수(시점 없는 다음 요청 = 현재 값).
5. 시간 여행 S10 다섯 조합 결과(연습 그래프 `hr`, 쓰기 켬).
6. 그래프 투영 규칙(노드/관계 판정, 끝점 없는 관계 제외).
7. 결과 카드 탭 규칙, 저장 50·기록 100 상한, `:param` 비기록, 콘솔 명령(유지분)의 카드 구성·문구.
8. NL: 질문 판정 키워드, 가로채기(⌘Enter/▶/⇧⌘Enter/✨), 응답 필드, 쓰기 단어 목록, 쓰기면 시험 안 함, 수리 최대 1회, 막대 문구 3종, 호출에 도구 없음.
9. 자동완성 규칙(접두 우선, 2자 이상 포함 일치, 최대 12개, 문자열·주석 안 비활성).

**의도된 차이 (D-12)**
1. 별도 포털 서버 없음, 콘솔은 메인 UI 탭(`view=console`), 탭 제목 「그래프 콘솔」.
2. 토큰 없는 요청 401, 외부 브라우저는 일회용 링크.
3. 쓰기 기본 거부(S9), 발행 관리 그래프 쓰기 항상 거부(D-20).
4. NL이 내장 에이전트·외부 브라우저에서도 동작.
5. `as known at` 목록이 대상별로 걸러짐(원본은 전역).
6. 스키마 디자이너·AI 제안·raw SQL·릴리스 API·벤치마크 없음(D-19).
7. 저장 질의·기록이 앱 탭과 외부 브라우저에서 공유.
8. 밝은 테마 지원.

## 12. 열린 질문
1. **라벨 해석**(§3.1)을 코어가 질의 텍스트 수준에서 할지(파서 필요), 엔진의 그래프별 별칭 기능으로 할지 — D-02 결정에 달림. 해석이 어려우면 온톨로지 대상에서도 이름공간 라벨을 직접 쓰게 하고 자동완성으로 보완.
2. 저장 Object set은 온톨로지 정의(작업본·발행 대상)인가, 런타임 자산인가. 대시보드·코드 앱이 참조하므로 버전 고정이 필요하면 전자.
3. 과거 발행 버전의 그래프 표현을 보존할지(버전별 질의) — 저장 비용. 최소안: 스키마만 보존, 질의는 현재 버전만.
4. live Object type이 변환식을 쓰면 Cypher가 보는 속성은 무엇인가(원천 컬럼 vs 매핑된 속성) — 02 §16의 컴파일 방식에 달림→ **해결: 02 §16에 반영** — 변환식은 원천 쪽 읽기 전용 뷰로 컴파일되어 Cypher도 매핑된 속성 이름을 본다.
5. 콘솔 쓰기에 웹 확인 막대로 충분한가, 네이티브 창이 필요한가(연습 그래프 한정이므로 웹 막대 권장).
6. 결과 상한(1,000행/30초)의 기본값과 설정 노출 여부.
7. 원본 「history」(og_history) 대체로 타임라인 API가 충분한지 [확인 필요].

# F7. 시스템 등록

- 상태: 초안 v0.1 (2026-11-01, Claude 작성) — 사용자 보정 전
- 원본 기준 동작: [`menus/07-systems/design.md`](../../analysis/ontological-studio/menus/07-systems/design.md), [`user-scenarios.md`](../../analysis/ontological-studio/menus/07-systems/user-scenarios.md)
- 관련 문서: [01](../01-architecture.md) §2.1 Action 모듈, [02](../02-ontology-model.md) §7.1 Backing source `system` · §10 Action type `callSystem` · §17 검증, [03](../03-security.md) §7 비밀 관리 · S8, [F2](F2-query-action.md) §7.4 실행, F1(액션 편집기), F8(설정)
- 결정 대기: **D-14**(①비밀 공급 ②헬스 판정 ③같은 이름 덮어쓰기 ④재시도 적용), D-12

---

## 1. 목적

Action type의 `callSystem` 규칙(02 §10)과 Backing source `system`(02 §7.1)이 부르는 **업무 시스템(마이크로서비스)** 을 등록·관리한다.

- 등록 정보: 소유(표시 이름·담당 팀·연락처·태그·아이콘), 닿는 법(프로토콜·환경별 주소·활성 환경), 할 수 있는 것(스펙에서 읽은 **operation 카탈로그** + 직접 추가 API), 인증(방식 + **OS 키체인의 비밀 참조**), 호출 정책(타임아웃·재시도·헬스 경로).
- 비밀 값은 화면에서 한 번 입력받아 키체인에 넣고, DB·API 응답·로그·미리보기 어디에도 값이 나오지 않는다(03 §7).
- 업무 시스템에는 **그 시스템의 인증만** 보낸다(내부 비밀 헤더 없음, 03 S8).
- 예제 시스템 3개(구매 ERP·물류 WMS·고객 CRM)는 첫 실행 때 등록된다(원본과 같음).

## 2. 원본 기준 동작 요약 [원본]

| 영역 | 원본 0.1.1 동작 |
|---|---|
| 구성 | 화면 → 분석 백엔드 프록시(`/api/act/…`, 인증 없음, 화면 공용 신원 토큰으로 대리) → 별도 액션 실행기(`/api/kinetic/…`, JWT) → 업무 시스템 직접 호출. 레지스트리는 실행기 전용 SQLite |
| 목록 | 카드(이름순): 아이콘·프로토콜·상태 점(✓/!/?), 표시 이름·slug·설명·`API N개 · 담당 팀`·태그, 「+ 시스템 등록」 카드. 진입 시 시스템마다 상태 확인 자동 호출. 신원 배지 `<sub> · 관리자`/`조회 전용` |
| 상세 | 정보 표(게이트웨이 `/svc/<name>`(표시용, 실제 라우팅 없음)·활성 주소·스펙·인증(**환경 변수 이름**만)·정책·담당·태그·수정 시각), 「상태 확인」「스펙 다시 읽기」「편집」「삭제」, API 표(메서드·경로·operationId·설명·출처 스펙/직접 추가, 「조회」(경로 변수 없는 GET만), 「삭제」(직접 추가만)), API 추가 폼 |
| 마법사 | 6단계: 1 기본 정보 · 2 프로토콜·스펙(7종, REST·OData 외 「어댑터 필요」; 파일/URL/없음; 형식 자동 판별) · 3 환경·주소 · 4 인증(6종, 비밀 값 대신 환경 변수 이름) · 5 정책(타임아웃 5000, 재시도 0–5 기본 2, 헬스 `/health`) · 6 연결 테스트(스펙/헬스/환경변수 3줄)·저장. 1–4단계 충족이면 테스트·등록 가능(테스트 통과 불필요) |
| 규칙 | 이름 `^[a-z0-9][a-z0-9-]{0,62}$`, `routes` 예약. Swagger 2.0 → OpenAPI 3 변환, WSDL은 operation 이름만, 그 밖 비REST는 원문만. 수동 API는 스펙 재입수와 무관하게 유지, 같은 id는 수동 우선 |
| 약점·불일치 | ① 사용자 시스템 비밀을 실행기가 읽을 길이 사실상 없음(튜토리얼은 설정 파일에 적으라 하나 실행기에 전달 안 됨 — REVIEW #11) ② 헬스: 0.1.1은 HTTP 3xx 이상 = 실패, 튜토리얼은 5xx만 실패·404/405 경고 ③ 같은 이름 등록 시 **경고 없이 교체** ④ 시스템별 재시도 값은 **저장·표시만**, 호출에 미적용 ⑤ 실행기 내부 비밀 헤더가 **업무 시스템 호출에도 전송**(REVIEW #13) ⑥ 사용 중 시스템 삭제는 삭제 **후에** 경고 ⑦ 예제 시스템은 지워도 재시작 시 다시 등록 |

## 3. 새 설계에서 달라지는 점 [제안]

| # | 원본 | 새 설계 | 근거 |
|---|---|---|---|
| C1 | 별도 실행기 + 백엔드 프록시 + 공용 신원 JWT | 코어 **Action 모듈**의 시스템 레지스트리. 화면은 세션 토큰으로 `/api/v1/systems…` 직접 호출. 등록·수정은 사람만 | 01 §2.1, 03 §3 |
| C2 | 인증 = 환경 변수 **이름** | 인증 = 마법사에서 **값 입력 → OS 키체인**, DB에는 `secret_ref`(이름·종류·설정 시각·마지막 사용)만. 화면에는 「저장됨 ••••」 | **D-14 ①**, 03 §7 |
| C3 | 헬스 3xx 이상 실패 | **5xx·무응답만 실패, 404·405는 경고**(튜토리얼), 3단계 `ok/warn/fail` | **D-14 ②** |
| C4 | 같은 이름 등록 = 조용히 교체 | 생성 모드에서 같은 이름이면 409 → 화면이 **덮어쓰기 확인** → 확인 시 교체(수동 API·최초 등록 시각 유지는 원본과 같음) | **D-14 ③** |
| C5 | 재시도 저장만 | 재시도를 **실제 적용**: 5xx·연결 오류·타임아웃에, GET 또는 멱등 키가 있는 호출에만, 지수 백오프 | **D-14 ④** |
| C6 | 내부 비밀 헤더가 업무 시스템에도 감 | 업무 시스템 호출 헤더 = 허용 목록(§7.4)만. 내부 비밀 헤더 자체가 없음 | 03 S8 |
| C7 | 삭제 후 「이 시스템을 쓰던 액션」 경고 | 삭제·스펙 갱신·API 삭제·프로토콜 변경 **전에** 사용처(발행·작업본 Action type, Backing source)를 보여 주고 확인 | 02 §17-9 영향 분석 |
| C8 | 빈 헬스 경로 → `/health`로 대체 | 빈 헬스 경로 = **활성 주소 자체**를 점검(튜토리얼) | D-12(튜토리얼이 더 합리적) |
| C9 | 「게이트웨이 `/svc/<name>`」 표시(실제 라우팅 없음) | 화면에서 게이트웨이 줄 제거(오해 방지). 응답 필드 `route`는 비교용으로 유지 | D-12 |
| C10 | 지운 예제 시스템이 재시작 시 다시 등록 | 지운 예제는 기억하고 다시 등록하지 않음. F8 「예제 시스템 복원」 | D-12 (§12 Q3) |
| C11 | `callSystem` 검증은 액션 생성 때 실행기 조회(불통이면 경고만) | 작업본 검증·발행 컴파일에서 레지스트리와 대조(§7.6), 발행 시 operation 시그니처를 액션 카탈로그에 고정 | 02 §16·§17-7 |

## 4. 사용자 시나리오

| # | 시나리오 | 원본과의 차이 |
|---|---|---|
| S1 | 목록 보기: 예제 3개(이름순 `sample-crm, sample-erp, sample-wms`), 상태 점 자동 확인, 「+ 시스템 등록」 | 상태 점 3단계(✓ 정상 / ~ 경고 / ! 이상 / ? 미확인). 신원 배지 `<사용자> · 관리자` |
| S2 | 상세: 정보 표, API 표(ERP 6·WMS 3·CRM 4) | 인증 줄 = `API 키 · X-API-Key ← 키체인(저장됨)`. 게이트웨이 줄 없음. 「사용처」 줄(이 시스템을 쓰는 Action type·Object type) 추가 |
| S3 | 상태 확인 | 404/405 → `연결됨 · 경고 · HTTP 404`(주황 `~`) |
| S4 | 스펙 다시 읽기 | 사라질 operation을 쓰는 Action type이 있으면 먼저 확인 창(§5.5) |
| S5 | API 직접 추가·삭제 | 같음 + 삭제 전 사용처 확인 |
| S6 | GET API 바로 조회 | 같음 |
| S7 | 새 시스템 6단계 마법사(Petstore) | 4단계에서 비밀 **값**을 입력(키체인). 튜토리얼처럼 헬스 경로를 비우면 활성 주소 자체를 점검 → Petstore 테스트 통과 |
| S8 | 연결 테스트 해석(`mock-cmms`, API 키 인증) | 3번째 줄이 「환경변수」 → 「비밀」: `없음: API 키 값` 또는 「필요한 비밀이 모두 저장돼 있습니다 (값은 보지 않음)」. 튜토리얼의 "설정 파일에 적고 재시작" 단계가 필요 없음 |
| S9 | 비REST 등록(어댑터 필요) | 같음 |
| S10 | 편집(환경 추가·전환, 정책 변경) | 같음 + 비밀 「교체」·「삭제」 |
| S11 | 삭제와 사용 중 경고 | **삭제 전** 확인 창에 사용처 목록. 확인하면 삭제(원본처럼 거절하지는 않음) |
| S12 | 같은 이름으로 다시 등록 | 확인 창 「같은 이름의 시스템 'petstore' 가 이미 있습니다. 덮어쓸까요? (직접 추가한 API 와 최초 등록 시각은 유지됩니다)」 |
| S13 | Action 모듈 준비 전 | 배너 문구 변경(§10) |
| S14 | 예제 서비스 포트 변경 후 재시작 | 같음(예제 주소 자동 갱신) |
| N1 | **재시도 적용**: 예제 WMS가 첫 호출에 503을 돌려주게 한 뒤 액션 실행 | 같은 Idempotency-Key로 재시도해 성공, 단계 `httpAttempts: 2` |
| N2 | **비밀 노출 없음**: 등록 직후 응답·목록·감사·로그·DB 덤프·미리보기에서 입력한 비밀 문자열 검색 | 어디에도 없음 |
| N3 | **내부 헤더 없음**: 요청 기록용 모의 시스템을 등록해 액션 실행 | 받은 헤더 = 허용 목록뿐 |
| N4 | **callSystem 참조 깨짐**: Action type이 쓰는 operation을 스펙에서 지우고 「스펙 다시 읽기」 | 확인 창에 영향받는 Action type, 진행하면 그 Action type이 「참조 깨짐」, 계획 시 404 |

## 5. 화면 구성과 상호작용

### 5.1 공통 머리말 [원본 유지 + 수정]
- 「‹ 목록」(목록이 아니면), 제목 「시스템 등록」, 부제 「액션이 호출하는 업무 시스템」(원본 부제의 게이트웨이 경로 문구 제거, C9).
- 신원 배지 `<사용자 표시 이름> · 관리자`. 등록·수정 권한이 없는 주체(F8에서 역할을 줄인 경우)면 `조회 전용`(툴팁 「시스템 관리 역할이 없어 등록·수정·삭제가 거부됩니다」).
- 목록에서만 「새로고침」. 작업 결과 배너(성공 일반/실패 빨강) 한 줄. 모듈 미준비 시 빨간 배너(§10). 원본의 "실행기 상태를 페이지 수명 동안 1회만 읽음"은 따르지 않는다(새로고침 시 다시 읽음).

### 5.2 목록 [원본 유지]
카드 구성·아이콘 8종(`mes cmms aps erp sap scm wms generic`, 목록 밖 icon은 이름에 키가 있는지로, 아니면 기타)·빈 상태 문구(「등록된 시스템이 없습니다. 「+ 시스템 등록」으로 시작하세요.」)는 원본과 같다. 상태 문구:

| 상태 | 문구 | 점 |
|---|---|---|
| 확인 전 / 중 | `상태 미확인` / `확인 중` | ? |
| ok | `정상 · <ms>ms` | ✓ |
| warn | `연결됨 · 경고 · HTTP <code>` (404·405), `연결됨 · 경고 · HTTP <code> · 인증 확인 필요`(401·403), 그 밖 4xx·3xx `연결됨 · 경고 · HTTP <code>` | ~ (주황) |
| fail + HTTP | `이상 · HTTP <code>` (5xx) | ! |
| fail + 무응답 | `응답 없음 · <오류>` | ! |
| fail + 비밀 없음 | `인증 불가 · <사유>` | ! |

### 5.3 상세
- 머리·버튼·설명은 원본과 같음. 「스펙 다시 읽기」 비활성 툴팁 「스펙 URL 이 없습니다」.
- 정보 표: 활성 주소(`base_url (환경 이름)`), 환경 칩(2개 이상), 스펙, 인증(§5.6 표기), 정책(`<timeout> ms · 재시도 <n> · 헬스 <path 또는 "활성 주소">`), 담당, 태그, 수정 시각, **사용처**(신규: 「Action type 2 · Object type 1」, 펼치면 `Shipment.expediteShipment — setPriority 단계(setShipmentPriority), 보상` 식 목록; 작업본 전용 사용처는 「작업본」 배지).
- API 표·「조회」·「삭제」·API 추가 폼·안내 문구는 원본과 같다(경로 변수 자동 추가 안내, 본문 JSON 오류 문구, 성공 배너). API 표에 「사용처」 열(그 operation을 쓰는 규칙 수) 추가.

### 5.4 등록·편집 마법사 (6단계) [원본 유지 + 4단계·6단계 수정]
왼쪽 단계 목록(번호 클릭 자유 이동, 조건 충족 ✓), 제목 「새 시스템 — <단계>」/「<name> 편집 — <단계>」, 「취소」·「이전」·「다음」·「등록」/「저장」 — 원본과 같다.

| 단계 | 입력 | ✓ 조건 | 원본 대비 |
|---|---|---|---|
| 1 기본 정보 | 표시 이름, 이름(편집 시 잠금), 설명, 담당 팀, 연락처, 태그, 아이콘 | 이름 규칙(원본 문구 「영문 소문자·숫자·- 만, 'routes' 는 예약어입니다.」). **이름 입력 시 기존 목록과 같으면 즉시 경고** 「같은 이름의 시스템이 이미 있습니다 — 등록하면 덮어쓰기를 확인합니다.」 | 경고 추가 |
| 2 프로토콜·스펙 | 프로토콜 카드 7종, 스펙 방식(파일/URL/없음), 형식(자동 판별 기본) | 원본과 같음 | 같음. 「어댑터 필요」 경고 문구 원본 그대로 |
| 3 환경·주소 | 환경 행(활성 라디오·이름·주소), 「환경 추가」 | 원본과 같음 | 같음 |
| 4 인증 | 방식 6종(§5.6). 비밀 칸은 **password 입력**(붙여넣기 허용, 보기 토글 없음). 편집 시 저장된 비밀은 「저장됨 ••••  · 마지막 사용 <시각>」 + 「교체」·「삭제」 | 방식별 필수(생성 모드는 비밀 값 필수, 편집 모드는 기존 비밀 있으면 생략 가능) | 안내 문구 변경: 「🔒 비밀 값은 이 PC 의 OS 키체인에만 저장됩니다 — 화면·DB·로그에는 남지 않고, 호출하는 순간에만 읽습니다.」 |
| 5 정책 | 타임아웃(ms, 기본 5000), 재시도(0–5, 기본 2), 헬스 경로(빈 값 = 활성 주소) | 항상 | 안내 「재시도는 5xx·연결 오류·타임아웃에만, GET 또는 멱등 키가 있는 호출에만 합니다. 서비스는 Idempotency-Key 로 중복을 걸러야 합니다.」(원본 문구에 타임아웃 추가) |
| 6 연결 테스트·저장 | 요약 표, 「연결 테스트」, 결과 패널 | 테스트 결과 있음 | 3번째 줄 「비밀」(§6.2) |

- 「연결 테스트」·「등록/저장」은 1–4단계 충족 시 활성, 테스트 통과는 저장 조건 아님(원본과 같음).
- 테스트에 쓸 비밀: 생성 모드에서는 입력한 값을 **저장하지 않고 이번 테스트에만** 쓴다(요청 본문의 쓰기 전용 필드, §6.1).
- 「등록」 → 409 `conflict`(같은 이름)면 덮어쓰기 확인 창(S12 문구) → 「덮어쓰기」 시 `?overwrite=true`로 재요청. 성공 배너 원본 문구(「시스템 '<표시이름>' 을(를) 등록했습니다 — API N개.」, 실행 불가면 「 실행 어댑터가 필요해 액션 실행은 거부됩니다.」).
- 편집 저장: 원본처럼 부분 수정 → 스펙 URL이 바뀌었으면 스펙 다시 읽기(§5.5 확인 포함) → 「'<name>' 을(를) 저장했습니다.」.

### 5.5 영향 확인 창 (신규, C7)
스펙 다시 읽기·API 삭제·프로토콜/주소 변경·시스템 삭제 전에 코어가 **사용처 diff**를 계산한다(`GET …/usage` 또는 `dryRun=true`).
- 영향 없음 → 원본 흐름 그대로(삭제는 원본 확인 문구).
- 영향 있음 → 창 「이 변경으로 다음 액션이 실행할 수 없게 됩니다」 + 목록(`Shipment.expediteShipment — setPriority 단계: operation 'setShipmentPriority' 이(가) 사라짐` / 보상 단계 / Backing source) + 「그래도 진행」/「취소」. 진행하면 결과 배너에 원본 경고 문구(「… 이 시스템을 쓰던 액션: A, B. 액션 단계를 고치고 다시 발행하세요.」)를 유지.
- 진행 후 그 Action type은 액션 카탈로그에서 「참조 깨짐」 표시(F1·F2), 계획 시 404 `not_found`(시스템/operation) — F1 작업본 검증에도 오류로 나온다.

### 5.6 인증 방식과 표기
| 방식(kind) | 화면 라벨 | 공개 설정(저장) | 비밀(키체인) | 표기 |
|---|---|---|---|---|
| `none` | 없음 | — | — | `없음` |
| `api_key` | API 키 | 위치(헤더/쿼리), 헤더 이름(기본 `X-API-Key`) 또는 쿼리 이름 | `apiKey` | `API 키 · <헤더 또는 ?쿼리> ← 키체인(저장됨|없음)` |
| `basic` | Basic | — | `username`, `password` (원본은 `user:password` 한 값) | `Basic ← 키체인(…)` |
| `bearer` | Bearer 토큰 | 헤더(기본 `Authorization`) | `token` | `Bearer · <헤더> ← 키체인(…)` |
| `oauth2_client_credentials` | OAuth2 Client Credentials | 토큰 URL, Client ID, 스코프 | `clientSecret` | `OAuth2 client credentials · <client_id> · <token_url>` |
| `login_token` | 로그인 토큰 (JSON 로그인) | 로그인 URL, 아이디 필드(기본 loginId), 비밀번호 필드(기본 password), 고정 본문(JSON), 토큰 위치(기본 token), 헤더(기본 Authorization), 스킴(기본 Bearer), TTL | `username`, `password` | 원본 형식에서 `← $ENV` 대신 `← 키체인` |
- 토큰 캐시 규칙(OAuth2: 만료 60초 전 갱신, `expires_in` 없으면 300초 / 로그인 토큰: JWT `exp` 또는 TTL, 60초 전 갱신, 401이면 1회 재로그인)은 원본과 같다. 받은 토큰은 **메모리에만** 캐시.
- 로그인 토큰 화면 오류 문구는 원본과 같되, 「…환경변수 이름을 적으세요」 문구는 「아이디를 입력하세요.」/「비밀번호를 입력하세요.」로 바뀐다.

## 6. API (`/api/v1/systems`, Action 모듈)

공통: 세션 토큰 필수. 오류 `{"error":{"code","message"}}` + `X-Request-Id`. 오류 코드 → 상태: `unauthenticated` 401, `forbidden` 403, `not_found` 404, `invalid_params`·`not_executable`·`not_readonly` 422, `conflict` 409, `bad_gateway` 502, `unavailable` 503 — 원본과 같다. 쓰기(등록·수정·삭제·refresh·API 추가/삭제·비밀) = 사람 주체 + 시스템 관리 역할. 읽기(목록·상세·상태·operations·조회·usage) = 사람, 그리고 에이전트는 §8 도구로만.

| 메서드 | 경로 | 요청 | 응답 | 원본 대응 |
|---|---|---|---|---|
| GET | `/api/v1/systems` | — | `[System]` 이름순 | `/api/act/systems` |
| POST | `/api/v1/systems?overwrite=false` | SystemBody | 201 System(+operations) / **409 `conflict`** 「시스템 '<n>' 이 이미 있습니다.」(overwrite 아닐 때) | 같음(원본은 교체) |
| POST | `/api/v1/systems/test` | SystemBody(+임시 비밀) | TestResult (저장 안 함) | `/systems/test` |
| GET | `/api/v1/systems/{name}` | — | System + `operations` + `usage` | 같음 |
| PATCH | `/api/v1/systems/{name}` | 부분 SystemBody(name·protocol 제외) | System | 같음 |
| DELETE | `/api/v1/systems/{name}?dryRun=` | — | `{deleted, used_by:["Type.action", …], usage}` (dryRun이면 `deleted:false`) | 같음 + dryRun |
| POST | `/api/v1/systems/{name}/refresh?dryRun=` | — | `{system, operations_added, operations_removed, broken_usage:[…]}` | `/refresh` |
| GET | `/api/v1/systems/{name}/health` | — | HealthResult | `/health` |
| POST | `/api/v1/systems/{name}/query` | `{operation_id, path_params?, query?}` | `{ok, http_status, data, latency_ms, truncated, error?}` | `/query` |
| GET | `/api/v1/systems/{name}/operations` | — | `[Operation]` | 같음 |
| POST | `/api/v1/systems/{name}/operations` | Operation 본문 | Operation(`source:"manual"`) | 같음 |
| DELETE | `/api/v1/systems/{name}/operations/{operationId}?dryRun=` | — | `{deleted, broken_usage}` / 409 스펙 출처 / 404 | 같음 + dryRun |
| GET | `/api/v1/systems/{name}/usage` | — | `{actionTypes:[{rid, apiName, objectType, rule, role: step|compensation, operation, published, draft}], backingSources:[…]}` | **신규** |
| PUT | `/api/v1/systems/{name}/secrets/{field}` | `{value}` | `{field, set:true, setAt}` | **신규**(비밀 교체) |
| DELETE | `/api/v1/systems/{name}/secrets/{field}` | — | `{field, set:false}` | **신규** |

- 경로 조각은 URL 인코딩(원본과 같음). 응답 필드 이름은 원본 System 응답을 그대로 쓴다(비교 대상 결정적 기능이므로 snake_case 유지, F2 §12 Q1과 같은 쟁점).

### 6.1 SystemBody
원본 본문(이름·표시 정보·`protocol`·`spec_format`·`base_url`·`environments`·`active_environment`·`openapi_url`·`openapi`·`openapi_text`·`auth`·`timeout_ms`·`retries`·`health_path`)과 같고, 인증만 바뀐다:
```yaml
auth:
  kind: none|api_key|basic|bearer|oauth2_client_credentials|login_token
  # 공개 설정 (방식별 허용 필드만; 원본의 *_env 필드는 없음)
  header?, query_param?, token_url?, client_id?, scopes?, login_body?, username_field?,
  password_field?, token_path?, scheme?, ttl_seconds?
  secret_values?:            # 쓰기 전용. 응답·로그·감사에 절대 나오지 않음
    { apiKey? | token? | username? | password? | clientSecret? }
```
- 처리: 코어는 `secret_values`를 받는 즉시 키체인에 쓰고(키 이름 `workbench/system/<name>/<field>`), 본문에서 지운 뒤 나머지를 처리한다. `/systems/test`에서는 키체인에 쓰지 않고 그 요청 동안만 메모리에서 쓴다.
- 요청 로깅·오류 보고는 `secret_values`와 인증 헤더를 가린다(구조화 로그의 가림 목록, 01 §7).
- 공개 설정 칸에 비밀처럼 보이는 키(`secret, value, password, passwd, pwd, client_secret, token, api_key, apikey, access_token`)로 값을 보내면 422 「auth.<k>: 비밀 값은 secret_values 로만 보냅니다.」(원본 「비밀 값은 등록하지 않습니다…」 검사의 후계). `login_body`에 비밀번호 필드 키 금지 규칙도 유지.
- 그 밖의 등록 규칙(이름·환경·주소·표시 필드 길이·스펙 입수 우선순위·형식 판별·Swagger 변환·WSDL·OpenAPI operation 추출·`servers` 경로 접두·프로토콜 결정·정책 범위, 오류 문구)은 원본 design §5.2를 그대로 따른다. 차이: `timeout_ms`가 본문에 없을 때 기본값은 화면과 같은 **5000**(원본 서버 기본 10000과 화면 5000의 불일치 정리), `health_path` 빈 값은 저장도 빈 값(= 활성 주소, C8).
- `?overwrite=true`일 때 교체 규칙은 원본과 같다(최초 등록 시각·수동 API 유지, 표시 정보는 본문에 없으면 이전 값). 비밀은 본문에 새 값이 있으면 교체, 없으면 유지.

### 6.2 TestResult
```yaml
spec:   { ok, format, operations, operation_ids[≤200], note? } | { ok:false, format, operations:0, error }
health: { ok, level: ok|warn|fail, http_status, url, latency_ms, error? }   # 인증 없이, 3초
auth:   { ok, kind, required:[field], missing:[field], checked_in:"keychain" }
protocol, executable, adapter_required
ok: spec.ok && health.level != "fail" && auth.ok
```
- 화면 3줄: 스펙(원본과 같음) / 헬스 `정상 · HTTP <s> · <ms>ms` · `연결됨 · 경고 · HTTP 404` · `HTTP <s>` · `응답 없음` / 비밀 `없음: API 키 값`(필드 표시 이름) 또는 「필요한 비밀이 모두 저장돼 있습니다 (값은 보지 않음)」.
- 원본 필드 `required_env`·`missing_env`는 `required`·`missing`(비밀 필드 이름)으로 바뀐다 — 의도된 차이.

### 6.3 HealthResult — 헬스 판정 (D-14 ②)
`{ok, level, http_status|null, latency_ms, checked_at, error?}`. 활성 주소 + 헬스 경로(빈 값이면 활성 주소 그대로)에 **인증을 붙여** GET, 3초, 리다이렉트는 따라가지 않음.

| 결과 | level | ok |
|---|---|---|
| 2xx | ok | true |
| 404, 405 (헬스 경로가 없음) | warn | true |
| 401, 403 (인증 확인 필요) | warn | true |
| 그 밖 3xx·4xx | warn | true |
| 5xx | fail | false |
| 연결 실패·타임아웃 | fail | false (`error` = `<예외 종류>: <설명>`) |
| 인증 준비 실패(비밀 없음·토큰 발급 실패) | fail | false (`error` = `auth_unavailable: <사유>`) |
- `ok` 의미가 원본(상태 < 300)과 달라진다 — 의도된 차이. 연결 테스트의 헬스는 인증 없이 같은 판정.

### 6.4 Operation·조회·API 추가
원본 계약 그대로: Operation `{operation_id, method, path, summary, parameters[{name, in, required, schema}], request_body_schema, source: openapi|wsdl|manual}`, 조회 규칙(GET만 — 422 `not_readonly` 원본 문구, 비REST — 422 `not_executable` 원본 문구, 목록 500건 상한 `truncated`, 감사), API 추가 검증(operation_id 형식, 메서드 5종, 경로 변수 선언 「경로 변수 [...] 가 parameters(in: path) 에 없습니다.」), 스펙 출처 삭제 409 원본 문구, 없는 operation 404 원본 문구.

## 7. 데이터 (02의 개념으로)

### 7.1 System — `workbench.runtime.system`
원본 시스템 레코드(design §6.1)와 같은 필드 + 다음 변경:
| 필드 | 원본 | 새 |
|---|---|---|
| `rid` | 없음 | UUID(불변). Action type은 이름으로 쓰고 컴파일 시 rid로 고정 |
| 인증 | `auth_*_env` 등 환경 변수 이름 | 공개 설정만 + `secrets: [secret_ref id]` |
| `retries` | 저장만 | 호출에 적용 |
| `health_path` | 빈 값 → `/health` | 빈 값 허용(= 활성 주소) |
| `sample` | 없음 | 예제 여부(bool), 삭제 기억은 `sample_tombstone` 표 |
| `manual_ops`, `openapi`(변환된 OpenAPI 3), `spec_text` | | 같음 |
- operation 카탈로그 = 스펙 추출 + 수동(같은 id는 수동 우선) — 원본과 같음. 시스템마다 계산 결과를 캐시하고 저장 시 무효화.

### 7.2 Secret ref — `workbench.secret_ref` (03 §7)
`{id, owner:{kind:"system", name}, field, label, setAt, lastUsedAt, keychainKey}`. 값은 키체인에만. 시스템 삭제 시 키체인 항목도 지운다. 키체인 접근이 거부되면(사용자가 OS 프롬프트 거절) 호출은 `auth_unavailable: 키체인 접근이 거부되었습니다`.

### 7.3 재시도 (D-14 ④)
- 대상: 응답 5xx, 연결 오류, 타임아웃. 4xx는 재시도하지 않는다(로그인 토큰 401 1회 재로그인은 별도 규칙).
- 조건: 메서드 GET, 또는 `Idempotency-Key` 헤더가 붙은 호출(액션 단계·보상은 항상 붙음). 그 밖(멱등 키 없는 쓰기)은 재시도 안 함.
- 횟수 = 시스템 `retries`(0–5, 미설정 2). 간격 = 200ms × 2^(n−1) ± 20% 지터, 응답의 `Retry-After`(초, 30 이하)가 있으면 그것.
- 멱등 키: 한 단계 시도(`:a<시도>`) 안의 HTTP 재시도는 **같은 키**를 쓴다(서비스가 중복을 거르게). 실행 단위 재시도(F2 `retry`)는 시도 번호가 바뀐다 — 원본과 같음.
- 기록: 단계의 `httpAttempts`, 마지막 상태·오류. 조회·상태 확인은 재시도하지 않는다(사람이 다시 누름).

### 7.4 업무 시스템 호출 계약 (액션·조회·상태 공통)
- 주소: 활성 환경 주소 + operation 경로(경로 변수 채움, URL 인코딩) + 쿼리 — 원본과 같음.
- **보내는 헤더 = 허용 목록만**: `Content-Type`, `Accept: application/json`, `User-Agent: <제품명>/<버전>`, `Idempotency-Key`(액션), `X-Kinetic-Run`(액션, run id — 비밀 아님, 원본 계약 유지), 시스템 인증 헤더(또는 쿼리), Action type 인자 매핑의 `header.<이름>`. 원본의 내부 비밀 헤더는 **존재하지 않는다**(03 S8).
- 인자 매핑 `header.<이름>`으로 인증 헤더 이름·`Authorization`·`Idempotency-Key`·`X-Kinetic-Run`·`Cookie`·`Host`를 덮어쓰지 못한다(검증 오류, §7.6).
- 인증 주입: §5.6 방식별, 값은 호출 순간 키체인에서 읽음(프로세스 메모리 캐시 5분, 비밀 교체 시 무효화). 비밀이 없으면 원본처럼 "인증 없이 보내기"가 아니라 **호출하지 않고** `auth_unavailable` 실패(조용히 무인증 호출하는 원본 동작은 의도된 차이).
- 미리보기(F2 계획)·감사·로그에서는 인증 헤더·인증 쿼리 값을 `••••`로.
- 타임아웃 = 시스템 `timeout_ms`, 동시 호출 상한 8. 결과: 2xx 성공, 응답은 JSON(아니면 텍스트 앞 2000자) — 원본과 같음.
- 실행 가능 프로토콜은 rest·odata. 그 밖은 계획 단계 422 `not_executable`(원본과 같음).

### 7.5 예제 시스템
원본 design §6.2·§6.3과 같은 3개(`sample-erp` api_key·`X-API-Key`, `sample-wms` basic, `sample-crm` bearer; operation 6/3/4; timeout 5000, retries 2, health `/health`, 환경 `local`). 차이: 예제 비밀은 첫 실행 때 무작위로 만들어 **키체인**에 넣고 예제 서비스 프로세스에도 같은 값을 환경으로 준다(예제 서비스는 우리가 띄우는 프로세스이므로). 포트 변경 시 주소 갱신 규칙(base_url·스펙 주소·`local` 환경만 바꿈, 로그 「시스템 주소 갱신 <name>: <old> → <new>」)은 원본과 같다. 사용자가 지운 예제는 다시 등록하지 않는다(C10).

### 7.6 Action type `callSystem`과의 연결

Action type 규칙(02 §10):
```yaml
- callSystem:
    name: setPriority                    # 단계 이름 (원본 규칙: 소문자 시작 영숫자_)
    system: sample-wms                   # 레지스트리 name
    operation: setShipmentPriority       # operation_id
    args: { path.shipment_no: $target.shipmentNo, body.priority: $params.newPriority }
    compensation: { system?: sample-wms, operation: setShipmentPriority, args: { body.priority: $before.priority } }
```
Backing source `system`(02 §7.1): `{system, operation, recordsPath}` — operation은 **GET**이어야 한다.

| 시점 | 검사 | 결과 |
|---|---|---|
| 작업본 저장·검증(F1, 02 §17-7) | 시스템 존재, operation 존재, 실행 가능 프로토콜, `args` 키 형식 `path.|query.|header.|body.`, **필수 path 파라미터가 모두 매핑됨**, 매핑한 path·query 이름이 operation 파라미터에 있음(없으면 경고), `body.*`가 요청 본문 스키마에 없는 경로면 경고, 금지 헤더(§7.4) 덮어쓰기 오류, 보상 operation도 같은 검사, Backing source는 GET 여부 | 오류는 저장은 되되 제안·발행 불가, 경고는 표시 |
| 발행 컴파일(02 §16) | 위 검사 재실행 + 각 단계의 **operation 시그니처 고정**: `{systemRid, operation_id, method, path, paramsHash, bodySchemaHash}`를 액션 카탈로그에 저장 | 실패 시 발행 원자적 중단 |
| 계획(F2) | 시스템·operation이 아직 있고 실행 가능한지(없으면 404 원본 문구 「시스템 '<n>' 이 등록되지 않았습니다.」/「operation '<id>' 이 없습니다.」, 불가 422 `not_executable`). 고정한 시그니처와 현재 operation의 method·path가 다르면 422 `invalid_params` 「등록 시스템의 API '<id>' 가 발행 이후 바뀌었습니다 (<변경>). 액션을 다시 발행하세요.」, 파라미터·본문 스키마 해시만 다르면 경고(계획 표의 주의 줄) | |
| 레지스트리 변경(§5.5) | 사용처 계산: 발행본 + 작업본의 모든 Action type 단계·보상, Backing source | 확인 창, 감사 detail에 `broken_usage` |

- 사용처 조회는 F1 액션 편집기의 시스템·operation 드롭다운에도 쓰인다(원본 경계와 같음). 편집기는 operation을 고르면 파라미터 목록으로 `args` 초안을 채운다(`path.<p>`는 필수 표시).
- 인자 식 뿌리·매핑 키는 원본 그대로 유지한다(02 §10).

## 8. 에이전트 연동 (모드·도구)
| 모드 | 도구 | 비고 |
|---|---|---|
| `build` | `system_list()` → `[{name, display_name, description, base_url, operations_count, health_path, executable}]`, `system_operations(system)`, `query_system(system, operation_id, path_params?, query?)` | 원본 구축 도구와 같은 이름. 액션 초안 작성 시 operation 존재 확인용 |
| `act` | `query_system` | F2. GET만 |
| 모든 모드 | — | **레지스트리 쓰기·비밀 도구 없음**. 에이전트는 시스템을 등록·수정·삭제할 수 없고, 비밀 필드는 존재 여부(`auth.ok`)만 본다 |
- 도구 결과의 System에는 인증 공개 설정도 넣지 않는다(방식 이름만). 조회 결과 크기 상한은 원본과 같다(목록 500, 에이전트 전달은 04 §5 상한).

## 9. 보안·권한
- 쓰기는 사람 주체(세션 토큰) + 시스템 관리 역할(1인 모드 기본 보유). 에이전트·코드 앱·외부 MCP 토큰은 레지스트리 쓰기 불가(403).
- 비밀: 값은 키체인에만(03 §7). 응답·감사·로그·DB·미리보기·에이전트 도구 결과·오류 메시지에 값이 나오지 않음(N2 테스트). 비밀 입력 칸은 브라우저 자동 완성 끔.
- 업무 시스템에 내부 정보 전송 없음(§7.4, N3 테스트). 원본 설정상의 내부 비밀 헤더 개념 폐지.
- 스펙 URL·헬스·조회 대상은 사용자가 등록한 주소뿐(서버 측 요청 위조 방지: 등록 주소의 호스트 외로 리다이렉트를 따라가지 않음, 스펙 URL 다운로드 10초·크기 상한 5MB).
- 감사(`workbench.audit`): `register_system`(name, overwrite 여부), `update_system`(바뀐 필드 이름 목록 — 비밀은 `secret:<field>` 이름만), `delete_system`(name, used_by), `refresh_system`(operations 수, removed, broken_usage), `add_operation`, `delete_operation`, `set_secret`/`delete_secret`(필드 이름만), `query`(system, operation_id, http_status, ok, truncated). actor kind·id, requestId.

## 10. 오류·예외 (원본 문구 유지 여부)
| 상황 | 동작 | 원본 |
|---|---|---|
| Action 모듈 준비 전 | 목록 503 `unavailable` 「액션 모듈이 아직 준비되지 않았습니다. 잠시 후 새로고침하세요.」, 배너 같은 문구 | 문구 변경(실행기 개념 없음) |
| 토큰 없음·무효 | 401 「인증이 필요합니다.」 | 원본은 무인증 |
| 역할 없음 | 403 → 화면 「권한이 없습니다 — 시스템 관리 역할이 필요합니다.」 | 문구 변경(공용 신원 토큰 언급 제거) |
| 이름 규칙 위반 | 화면·서버 422 원본 문구 | 유지 |
| 같은 이름 생성 | 409 `conflict` → 덮어쓰기 확인 | **변경**(D-14 ③) |
| 스펙 입수 실패 | 등록 422(원본 문구), 테스트는 `spec.ok=false` | 유지 |
| 헬스 404·405 | `warn` 「연결됨 · 경고」 | **변경**(D-14 ②) |
| 비밀 값을 공개 칸에 | 422(§6.1 문구) | 문구 변경 |
| 비밀 없음으로 호출 | 호출 안 함, `auth_unavailable: '<field>' 비밀이 저장돼 있지 않습니다` | **변경**(원본은 무인증 전송) |
| 키체인 접근 거부 | `auth_unavailable: 키체인 접근이 거부되었습니다` | 신규 |
| 비REST | 등록 성공 `executable:false`, 계획·조회 422 `not_executable` 원본 문구 | 유지 |
| 스펙 출처 API 삭제 | 409 원본 문구 | 유지 |
| 사용 중 시스템 삭제·operation 제거 | 사전 확인 후 허용, `used_by`/`broken_usage` | 시점 변경 |
| 스펙 URL 없는 refresh | 422 「시스템 '<n>' 에 openapi_url 이 없습니다.」 | 유지 |
| 연결 테스트 미지원 | 해당 없음(원본의 404/405 「…아직 지원하지 않습니다」 분기 삭제) | 삭제 |

## 11. 원본과 비교할 테스트

### 11.1 같아야 함 (결정적 기능 — 값까지)
1. 첫 실행 후 목록 3건, 이름순, 표시 정보·`operations_count` 4/6/3, `route` `/svc/<name>`, `executable:true`, `retries:2`, `timeout_ms:5000`.
2. `sample-erp` 상세 operations 6건(id·method·path), `source:"openapi"`, auth `{kind:"api_key", header:"X-API-Key", query_param:null}`.
3. 등록 검증 오류: 이름 `Bad_Name`·`routes`, base_url `ftp://…`, retries 6 → 422(원본 문구).
4. `overwrite=true` 재등록 → created_at 유지, 수동 API 유지.
5. Swagger 2.0 업로드 → `spec_format:"swagger2"`, operation 추출, basePath 접두. WSDL → `soap`, `executable:false`, `POST /` operation.
6. 수동 API: 경로 변수 미선언 422, `source:"manual"`, refresh 후 유지, 스펙 operation 삭제 409.
7. 조회: GET → `{ok, http_status, data, latency_ms, truncated}`, POST operation → 422 `not_readonly`.
8. 포트 변경 재시작 → 예제 base_url·openapi_url·환경 갱신, 나머지 유지.
9. 마법사 6단계 라벨·✓ 규칙, 1–4단계 충족 시 테스트·등록 활성(테스트 미통과로도 등록), 「조회」 노출 조건, 배너 문구(등록·저장·스펙 다시 읽기·API 추가/삭제).
10. 업무 시스템 호출: URL 조립, `Idempotency-Key` 형식, `X-Kinetic-Run`, 인증 주입 결과(예제 서비스가 200).
11. 감사 이벤트 종류(register/update/delete/refresh/add_operation/delete_operation/query).

### 11.2 의도된 차이 (D-12, D-14)
| # | 차이 | 확인 |
|---|---|---|
| D1 | 인증은 키체인 비밀(`secret_values`), 응답에 `*_env` 필드 없음, 테스트 `auth.required/missing` = 필드 이름 | N2, S8 |
| D2 | 헬스 3단계: 404 → `level:"warn", ok:true` | S3 |
| D3 | 같은 이름 생성 409 → 확인 후 overwrite | S12 |
| D4 | 재시도 적용(503 한 번 후 성공, 같은 멱등 키) | N1 |
| D5 | 업무 시스템이 받은 헤더 = 허용 목록, 내부 비밀 헤더 없음 | N3 |
| D6 | 사용처 사전 확인(dryRun), 참조 깨짐 표시 | N4, S11 |
| D7 | 빈 헬스 경로 = 활성 주소 점검(Petstore 통과) | S7 |
| D8 | 비밀 없음이면 호출 안 함(`auth_unavailable`) | 비밀 삭제 후 상태 확인 |
| D9 | 지운 예제 시스템은 재시작 후에도 없음 | S11-2 |
| D10 | 화면에 게이트웨이 줄 없음, 부제 변경, 서버 timeout 기본 5000 | 화면·API |
| D11 | 원본 JWKS·발급 토큰 계약(`/kinetic-idp/jwks.json`) 없음 — 03 §3 세션 토큰으로 대체 | 비교 대상에서 제외 |

## 12. 열린 질문
- Q1. 환경별로 다른 비밀(개발/운영 키)을 지원할지. 이 문서는 시스템당 1벌. 필요하면 `secret_ref`에 `environment`를 더한다.
- Q2. 원본 호환용 "환경 변수에서 비밀 읽기"(고급 옵션)를 남길지 — CI·헤드리스 실행에서 유용하나 03 원칙(비밀은 키체인)과 충돌. 권장: 두지 않음.
- Q3. 지운 예제 시스템을 다시 등록하지 않는 동작(C10)이 F8 「예제 데이터 복원」과 어떻게 묶일지.
- Q4. 키체인 접근 주체: 코어(Python) 프로세스가 직접 OS 키체인 API를 쓰는가, 셸이 중개하는가(03 §7 미정). 이 문서는 "코어 Secret 포트"로만 적었다. [확인 필요: 구현 검토]
- Q5. 헬스 401·403을 `warn`으로 둔 것(인증을 붙여 불렀는데 거부 = 비밀이 틀림) — `fail`이 맞는지.
- Q6. 비REST 어댑터(SOAP·gRPC 등) 실행 지원 시점 — 원본처럼 등록만(v2 이후 검토).

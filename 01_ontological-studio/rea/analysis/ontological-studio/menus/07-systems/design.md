# M7 시스템 등록 — 설계 문서

- 대상 버전: Ontological Studio 0.1.1 동작 기준 (클린룸, ADR-0002·0011)
- 이 문서만으로 구현할 수 있도록 썼다. 화면 문구·API 경로·필드 이름은 비교 테스트를 위해 원본과 같게 적었다.
- 관련 공통 설계: A1 셸(부팅·포트·로컬 웹 오리진·탭), A2 저장소(비밀값 파일·예제 DB)

## 1. 목적

액션(키네틱 액션)이 데이터베이스에 직접 쓰지 않고 **업무 시스템의 API를 부르도록**, 그 업무 시스템(마이크로서비스)을 등록·관리하는 레지스트리 화면과 서비스를 만든다.

- 등록 정보: 누가 소유하는지(표시 이름·담당 팀·연락처·태그·아이콘), 어떻게 닿는지(프로토콜·환경별 주소·활성 환경), 무엇을 할 수 있는지(스펙에서 읽은 API = operation 목록 + 수동 추가 API), 어떻게 인증하는지(방식과 **비밀 값을 담은 환경 변수 이름**), 호출 정책(타임아웃·재시도·헬스 경로).
- **비밀 값은 절대 저장·표시하지 않는다.** 등록에는 환경 변수 이름만 남고, 실제 값은 액션 실행기 프로세스 환경에서 호출 순간에 읽는다.
- 앱에는 예제 업무 시스템 3개(구매 ERP·물류 WMS·고객 CRM)와 액션 실행기가 내장되어, 첫 실행부터 예제 시스템이 등록된 상태가 된다.

## 2. 사용자 시나리오 (요약)
상세는 `user-scenarios.md`.

| # | 시나리오 | 핵심 확인 |
|---|---|---|
| S1 | 목록 보기 | 카드 3개(이름순), 상태 점, 신원 배지, 「+ 시스템 등록」 카드 |
| S2 | 상세 보기 | 게이트웨이 경로 `/svc/<name>`, 활성 주소, 스펙 주소, 인증(환경 변수 이름만), 정책, API 표 |
| S3 | 상태 확인 | 헬스 경로 GET, 정상/이상/응답 없음 |
| S4 | 스펙 다시 읽기 | 스펙 주소에서 재입수, 수동 API 유지 |
| S5 | API 직접 추가·삭제 | 경로 변수 검사, 스펙 출처는 삭제 불가 |
| S6 | GET 조회 | 계획·승인 없이 읽기, GET만 |
| S7 | 6단계 등록 마법사 | 기본 정보 → 프로토콜·스펙 → 환경·주소 → 인증 → 정책 → 연결 테스트·저장 |
| S8 | 연결 테스트 해석 | 스펙/헬스/환경 변수 3항목 |
| S9 | 비REST 등록 | 「어댑터 필요」 — 등록은 되나 실행 불가 |
| S10 | 편집 | 이름·프로토콜 고정, 환경 전환, 스펙 주소 변경 시 재입수 |
| S11 | 삭제 | 거절 없이 삭제, 쓰던 액션 목록 경고 |
| S12 | 같은 이름 등록 | 교체(덮어쓰기) |
| S13 | 실행기 없음 | 배너와 원인 문구 |
| S14 | 포트 변경 후 재시작 | 예제 시스템 주소 자동 갱신 |

## 3. 구성

```
[화면: 시스템 등록 view=systems]
      │  /api/act/…   (로컬 웹 오리진 → 분석 백엔드, 인증 없음)
[분석 백엔드: 실행기 프록시]   ── 화면 대신 공용 신원 토큰으로 호출, 오류 형식 통일
      │  /api/kinetic/…  (Bearer JWT)
[액션 실행기]  ── 레지스트리 저장(SQLite), 스펙 해석, 헬스·조회·액션 호출
      │  업무 시스템 주소로 직접 HTTP (+인증 주입, 멱등 키)
[업무 시스템: 예제 ERP·WMS·CRM 또는 사용자 등록 시스템]
```

- 화면은 실행기에 직접 붙지 않는다(한 오리진, 장애 문구 한 곳). 실행기 앞 경로를 `/api/act`로 둔 이유는 게이트웨이 뒤 배포에서 `/api/kinetic`과 겹치지 않게 하려는 것.
- 0.1.1은 **직접 호출 모드**: 별도 API 게이트웨이 없이 실행기가 등록된 활성 주소로 직접 부르고 인증을 붙인다. 「게이트웨이 경로 `/svc/<name>`」은 표시·계약상의 이름이며 0.1.1 데스크톱에서는 실제로 라우팅되지 않는다.

## 4. 화면 구성과 상호작용

### 4.1 공통 머리말
- 목록이 아니면 왼쪽에 「‹ 목록」 버튼.
- 제목 「시스템 등록」, 부제 「키네틱 액션이 호출하는 서비스 · 게이트웨이 경로 `/svc/<이름>`」.
- 신원 배지: `<sub> · 관리자`(역할에 `kinetic_admin` 있음) 또는 `<sub 또는 '신원 미설정'> · 조회 전용`(경고색, 툴팁 「kinetic_admin 역할이 없어 등록·수정·삭제가 거부됩니다」). 상태 응답의 identity가 null이면 배지 없음.
- 목록 화면에서만 「새로고침」.
- 실행기 상태가 `reachable:false`면 빨간 배너: 「kinetic-action 에 닿지 못했습니다 (<url>). <error>」. 실행기 상태는 페이지 수명 동안 한 번만 읽어 재사용한다(원본 동작).
- 작업 결과 배너(성공=일반, 실패=빨강) 한 줄.

### 4.2 목록(그리드)
- 진입 시: 실행기 상태 조회(비동기) + 시스템 목록 조회 → 시스템마다 상태 확인을 병렬로 자동 호출.
- 카드(이름순):
  - 머리(아이콘 색 그라데이션): 이모지 아이콘, 프로토콜 라벨, 상태 점(✓ 정상 / ! 이상 / ? 미확인·확인 중), 점 툴팁 = 상태 문구
  - 몸통: 표시 이름(없으면 이름), 이름(slug, 표시 이름이 있을 때만), 설명, `API N개` · `· 담당 팀` · 「어댑터 필요」(실행 불가일 때), 태그 칩
  - 카드 클릭 → 상세
- 마지막 카드 「+ 시스템 등록」(부제 「REST(OpenAPI·Swagger) · SOAP · gRPC · GraphQL …」) → 마법사(생성 모드).
- 비어 있으면 「등록된 시스템이 없습니다. 「+ 시스템 등록」으로 시작하세요.」
- 목록 실패 시 빈 목록 + 오류 배너.

상태 문구 규칙:
| 상태 | 문구 |
|---|---|
| 확인 전 | `상태 미확인` |
| 확인 중 | `확인 중` |
| ok | `정상 · <latency_ms>ms` |
| 실패 + HTTP 상태 있음 | `이상 · HTTP <code>` |
| 실패 + 상태 없음 | `응답 없음 · <error>` |

아이콘 키 8종: `mes`(🏭 MES), `cmms`(🔧 CMMS), `aps`(📅 APS), `erp`(🏢 ERP), `sap`(💼 SAP), `scm`(🚚 SCM), `wms`(📦 WMS), `generic`(🔌 기타). 등록의 icon이 이 목록에 없으면 이름에 키가 들어 있는지로 고르고, 그래도 없으면 기타.

### 4.3 상세
- 머리: 아이콘, 표시 이름 + 이름(code), 배지(프로토콜, 「어댑터 필요」, 상태 점, 상태 문구), 버튼 「상태 확인」, 「스펙 다시 읽기」(스펙 주소 없으면 비활성, 툴팁 「OpenAPI URL 이 없습니다」 / 있으면 「OpenAPI 를 다시 읽어 API 를 갱신합니다 (직접 추가한 API 는 유지)」), 「편집」, 「삭제」.
- 설명 전문.
- 정보 표: 게이트웨이(`route`), 활성 주소(`base_url` + `(활성 환경 이름)`), 환경(2개 이상일 때 `이름 · 주소` 칩), 스펙(스펙 주소 또는 스펙 형식 라벨 또는 `—`), 인증(4.5 표기), 정책(`<timeout> ms` 또는 「기본 타임아웃」 · `재시도 <n 또는 기본>` · `헬스 <path 또는 —>`), 담당(팀 · 연락처, 있을 때), 태그, 수정(로컬 시각).
- 「API (operation) N개」 + 「API 추가」/「API 추가 닫기」 토글.
- API 표 열: 메서드(색 배지), 경로, operationId, 설명, 출처(「스펙」/「직접 추가」), 동작:
  - 「조회」 — 메서드가 GET이고 경로에 `{`가 없을 때만. 결과 패널: 「조회 결과 · <id> · HTTP <s> · <ms>ms [· 잘림]」, 「닫기」, 로딩 「조회 중…」, 오류 문구 또는 JSON(배열 20건 초과 시 앞 20건 + `… 외 N건`).
  - 「삭제」 — 출처가 직접 추가일 때만, 확인 창 「API '<id>' 을(를) 지울까요?」.
  - 없으면 「API 가 없습니다.」
- 안내: 「스펙에서 온 API 는 스펙을 고친 뒤 「스펙 다시 읽기」로 갱신합니다. 직접 추가한 API 만 여기서 지울 수 있습니다.」
- API 추가 폼: operationId, 메서드(GET/POST/PUT/PATCH/DELETE, 기본 POST), 경로(예 `/work-orders/{id}`), 설명, 파라미터 행(이름, 위치 path/query/header, 타입 string/integer/number/boolean, 필수 체크, 삭제) + 「파라미터 추가」, 경로의 `{변수}` 중 path 파라미터로 선언 안 된 것이 있으면 「경로의 {x} 를 path 파라미터로 추가하세요. [자동 추가]」, 요청 본문 JSON Schema(선택, 텍스트). 제출은 operationId가 있고 경로가 `/`로 시작할 때만 켜짐. 본문 JSON 오류 → 「요청 본문 JSON 오류: …」. 성공 → 「API '<id>' 을(를) 추가했습니다.」 후 상세 재조회.

### 4.4 등록·편집 마법사 (6단계)
왼쪽 단계 목록(번호 버튼, 클릭으로 자유 이동, 현재 단계 강조, 현재가 아니고 조건 충족이면 ✓). 오른쪽 패널 제목 「새 시스템 — <단계명>」 또는 「<name> 편집 — <단계명>」. 아래 「취소」·「이전」(2단계부터)·「다음」(6단계 전)·「등록」/「저장」(6단계).

| 단계 | 입력 | 조건(✓) |
|---|---|---|
| 1 기본 정보 | 표시 이름, 이름(레지스트리 키 · 영문 소문자·숫자·-; 편집 시 잠금; 위반 시 「영문 소문자·숫자·- 만, 'routes' 는 예약어입니다.」), 설명, 담당 팀, 연락처, 태그(쉼표 구분), 아이콘(8종, 기본 기타) | 이름이 `^[a-z0-9][a-z0-9-]*$`이고 `routes`가 아님 |
| 2 프로토콜·스펙 | 프로토콜 카드 7개(편집 시 잠금): REST「OpenAPI 3 · Swagger 2.0」, OData「$metadata」, SOAP「WSDL · 어댑터 필요」, gRPC「.proto · 어댑터 필요」, GraphQL「SDL · 어댑터 필요」, DB 프로시저「어댑터 필요」, 비동기 메시지「AsyncAPI · 어댑터 필요」. REST·OData가 아니면 경고 「실행 어댑터 필요 — 등록만 됩니다. 실행기는 지금 HTTP+JSON(REST·OData)만 호출하므로, 이 시스템을 쓰는 액션은 계획 단계에서 거부(not_executable)됩니다. 스펙은 올려 두면 API 목록으로 보입니다.」 스펙 방식 라디오: 파일 업로드(편집 시 잠금) / URL / 없음(API 를 직접 추가). 파일: 끌어다 놓기·클릭, 허용 확장자 `.json .yaml .yml .wsdl .xml .proto .graphql .graphqls .gql`, 선택 후 「<파일명> / <형식> · N자 · 다시 고르려면 클릭」. URL: 예 `http://localhost:8034/openapi.json`, 편집 시 안내 「URL 을 바꾸면 저장 뒤 스펙을 다시 읽습니다.」 스펙 형식 선택(없음 모드 제외): 자동 판별 / OpenAPI 3 / Swagger 2.0 / WSDL / GraphQL SDL / Protocol Buffers / AsyncAPI / OData $metadata | 없음, 또는 URL 비지 않음, 또는 파일 내용 있음 |
| 3 환경·주소 | 안내 「환경마다 주소가 다르면 모두 적고, 지금 쓸 환경을 고릅니다. 게이트웨이는 활성 환경 주소로 넘깁니다.」 행: 활성 라디오 + 이름 + 주소 + 삭제(행 1개면 비활성), 「환경 추가」. 기본 행 `default`. 활성 환경 행을 지우면 첫 행이 활성 | 이름과 `http(s)://` 주소가 있는 행 ≥1, 활성 환경이 그중 하나. 아니면 「환경 이름과 http(s) 주소를 하나 이상 적고 활성 환경을 고르세요.」 |
| 4 인증 | 4.5 참조. 「없음」이 아니면 안내 「🔒 비밀 값은 저장하지 않습니다 — 환경변수(비밀 저장소) **이름**만 저장하고, 게이트웨이가 실행 시점에 값을 읽습니다.」 | 방식별 필수 입력 |
| 5 정책 | 타임아웃(ms, 기본 5000, 최소 100 단위 100), 재시도(GET · 멱등 키 POST, 0–5, 기본 2), 헬스 체크 경로(기본 `/health`). 안내 「재시도는 5xx·연결 오류에만, 멱등 키가 있는 호출에만 합니다. 서비스는 Idempotency-Key 로 중복을 걸러야 합니다.」 | 항상 |
| 6 연결 테스트·저장 | 요약 표(이름 `표시이름 + code`, 프로토콜(+어댑터 필요), 스펙(파일명(형식) / 「파일 없음」 / URL / 「URL 없음」 / 「없음 — API 를 직접 추가」), 활성 환경 `이름 · 주소`, 인증 표기, 정책 `Nms · 재시도 n · 헬스 path|—`), 「연결 테스트」 버튼, 결과 패널 | 테스트 결과가 있음 |

- 「연결 테스트」와 「등록/저장」은 **1–4단계 조건이 모두 맞으면** 켜진다. 테스트 통과는 저장 조건이 아니다.
- 파일을 고르면 형식을 판별한다: `.proto`→proto, `.graphql/.graphqls/.gql`→GraphQL SDL, `.wsdl` 또는 `<definitions`→WSDL, `<edmx:Edmx`→OData $metadata, JSON/YAML의 `swagger`→Swagger 2.0, `openapi`→OpenAPI 3, `asyncapi`→AsyncAPI. 생성 모드에서는 형식에 맞춰 프로토콜을 자동 변경(WSDL→SOAP, proto→gRPC, SDL→GraphQL, AsyncAPI→비동기, $metadata→OData). 파일을 바꾸면 이전 테스트 결과를 지운다.
- 테스트 결과 패널(각 줄 정상/실패 색):
  - 스펙: `operation N개 · <형식 라벨>`(N=0이면 실패색), 스펙 없음 모드는 「스펙 없음 — 저장 뒤 API 를 직접 추가합니다」, 해석 실패는 `해석 실패: <오류>`
  - 헬스: `정상 · HTTP <s> · <ms>ms` 또는 오류 문구 / `HTTP <s>` / `응답 없음`
  - 환경변수: `없음: A, B` 또는 「필요한 이름이 모두 있습니다 (값은 보지 않음)」
  - operation 앞 12개(메서드 배지·경로·id) + `… N개 더`
  - 「응답 원문」 펼침(JSON 그대로)
  - 테스트 API가 404/405면 「실행기가 연결 테스트(POST /systems/test)를 아직 지원하지 않습니다. 저장은 할 수 있습니다. (<msg>)」
- 생성 성공: 「시스템 '<표시이름 또는 이름>' 을(를) 등록했습니다 — API N개.」 + (실행 불가면) 「 실행 어댑터가 필요해 액션 실행은 거부됩니다.」 → 목록 재조회 → 그 시스템 상세.
- 편집 저장: 이름·프로토콜·파일 원문을 빼고 부분 수정 요청 → 스펙 주소가 바뀌었으면 이어서 스펙 다시 읽기 → 「'<name>' 을(를) 저장했습니다.」 → 상세.
- 편집 진입 시 폼 채우기: 스펙 방식 = 스펙 주소가 있으면 URL, 없으면 없음. 환경이 비어 있으면 `[활성 환경 이름 또는 default, base_url]` 한 줄. 헬스 경로는 저장값 그대로.
- 오류(저장·테스트): 403이면 「권한이 없습니다 — 스튜디오 신원(KINETIC_STUDIO_TOKEN)에 kinetic_admin 역할이 필요합니다. (<msg>)」, 그 밖은 서버 메시지.

### 4.5 인증 방식과 입력·표기

| 방식(kind) | 화면 라벨 | 입력 | 필수 | 상세·요약 표기 |
|---|---|---|---|---|
| `none` | 없음 | — | — | `없음` |
| `api_key` | API 키 | 위치 라디오(헤더/쿼리 파라미터), 헤더 이름(예 X-Api-Key) 또는 쿼리 파라미터 이름(예 api_key), 키 값을 담은 환경변수 이름(예 CMMS_API_KEY) | env + 헤더 또는 쿼리 이름 | `API 키 · <헤더 또는 ?쿼리> ← $ENV` |
| `basic` | Basic | `"user:password" 를 담은 환경변수 이름` | env | `Basic ← $ENV` |
| `bearer` | Bearer 토큰 | 헤더(기본 Authorization), 토큰을 담은 환경변수 이름 | env | `Bearer · <헤더> ← $ENV` |
| `oauth2_client_credentials` | OAuth2 Client Credentials | 토큰 URL, Client ID, Client Secret 환경변수 이름, 스코프(공백·쉼표 구분). 안내 「게이트웨이가 토큰을 발급·캐시하고(만료 60초 전 갱신) Bearer 로 붙입니다.」 | 셋 다 | `OAuth2 client credentials · <client_id> ← $<env> · <token_url>` |
| `login_token` | 로그인 토큰 (JSON 로그인) | 로그인 URL, 아이디 필드(기본 loginId), 아이디 환경변수, 비밀번호 필드(기본 password), 비밀번호 환경변수, 로그인 본문 고정 필드(JSON, 선택), 토큰 위치(점 경로, 기본 token), 헤더(기본 Authorization), 스킴(기본 Bearer, 빈 값 = 토큰만). 안내 「게이트웨이가 로그인해 토큰을 받아 캐시하고(JWT exp 또는 30분, 만료 60초 전 갱신) 헤더에 붙입니다. 401 이면 한 번 다시 로그인합니다.」 | URL http(s), 두 env 이름 형식, 필드·토큰 위치 형식, 본문 JSON 객체 | `로그인 토큰 · <url> · <id필드> ← $<env>, <pw필드> ← $<env> · 응답 <path> → <헤더>: <스킴>` |

로그인 토큰 화면 오류 문구: 「로그인 URL 은 http(s) 주소여야 합니다.」, 「아이디 환경변수 이름을 적으세요 (영문·숫자·_ — 값이 아니라 이름).」, 「비밀번호 환경변수 이름을 적으세요 (…)」, 「<아이디 필드|비밀번호 필드|토큰 위치> '<v>' 은(는) 쓸 수 없습니다.」, 「로그인 본문 고정 필드는 JSON 객체여야 합니다.」

### 4.6 삭제
확인 창 「시스템 '<name>' 을(를) 레지스트리에서 지울까요?\n이 시스템을 쓰는 발행된 액션은 실행이 실패하게 됩니다.」 → 성공 시 `used_by`가 비면 「'<name>' 을(를) 지웠습니다.」, 있으면 빨간 배너 「'<name>' 을(를) 지웠습니다. 주의 — 이 시스템을 쓰던 액션: A, B. 액션 단계를 고치고 다시 발행하세요.」 → 목록.

## 5. API 명세

### 5.1 화면용 API (분석 백엔드, 로컬 오리진, 인증 없음)
모든 오류: HTTP 상태 + `{"error":{"code","message"}}`. 실행기에 닿지 못하면 503 `unavailable` 「kinetic-action 에 닿지 못했습니다 (<url>): <예외>. KINETIC_URL 과 서비스 기동 여부를 확인하세요.」. 실행기의 401(코드 없을 때) → 「kinetic-action 인증 실패 — KINETIC_STUDIO_TOKEN 을 확인하세요.」, 403 → 메시지 뒤에 「 — 스튜디오 신원에 필요한 역할이 없습니다 (레지스트리 쓰기는 kinetic_admin, 승인은 kinetic_approver).」(메시지에 `kinetic_`이 없을 때). 실행기 JSON이 아니면 502 `bad_response`.

| 메서드 | 경로 | 실행기 대응 | 타임아웃 |
|---|---|---|---|
| GET | `/api/act/health` | `GET /api/kinetic/health` | 3초 |
| GET | `/api/act/systems` | `GET /api/kinetic/systems` | 15초 |
| POST | `/api/act/systems` | `POST /api/kinetic/systems` | 15초 |
| POST | `/api/act/systems/test` | `POST /api/kinetic/systems/test` | 30초 |
| GET | `/api/act/systems/{name}` | `GET /api/kinetic/systems/{name}` | 15초 |
| PATCH | `/api/act/systems/{name}` | `PATCH …/{name}` | 15초 |
| DELETE | `/api/act/systems/{name}` | `DELETE …/{name}` | 15초 |
| POST | `/api/act/systems/{name}/refresh` | `POST …/{name}/refresh` | 15초 |
| GET | `/api/act/systems/{name}/health` | `GET …/{name}/health` | 6초 |
| POST | `/api/act/systems/{name}/query` | `POST …/{name}/query` | 30초 |
| GET | `/api/act/systems/{name}/operations` | `GET …/{name}/operations` | 15초 |
| POST | `/api/act/systems/{name}/operations` | `POST …/{name}/operations` | 15초 |
| DELETE | `/api/act/systems/{name}/operations/{operation_id}` | `DELETE …` | 15초 |

- 경로 조각(name, operation_id)은 URL 인코딩해 다른 경로로 새지 않게 한다.
- 실행기 호출의 행위자는 공용 신원 토큰(설정 `KINETIC_STUDIO_TOKEN`) 하나다(로그인 없음).

**`GET /api/act/health`** → `{url: <실행기 origin>, identity: {configured: bool, sub: str, roles: [str]}, reachable: bool, error?: str}`. identity는 토큰 페이로드를 **서명 검증 없이** 읽어 `sub`·`roles`만 담는다(토큰 값은 싣지 않음). 실행기 불통이면 `reachable:false`, `error`.
- 셸 대체 응답(내장 실행기가 아직 안 떴거나 실패): `GET /api/act/health` → 200 `{"url":"시작하지 않음","identity":null,"reachable":false,"error":"키네틱 액션 실행기(kinetic-action)가 아직 시작되지 않았거나 시작하지 못했습니다. 로그 폴더의 kinetic.log 를 확인하세요."}`, `GET /api/act/systems` → 503 `{"detail": <같은 문구>}`. 다른 `/api/act/*`는 백엔드로 보낸다.

**등록·테스트 본문 (SystemBody)** — 알 수 없는 필드도 그대로 전달.
```
{
  name: str (필수),
  display_name?, description?, owner_team?, contact?: str,
  tags?: [str], icon?: str,
  protocol?: "rest"|"odata"|"soap"|"grpc"|"graphql"|"db_procedure"|"async",
  spec_format?: "openapi3"|"swagger2"|"wsdl"|"graphql_sdl"|"proto"|"asyncapi"|"odata_metadata",
  base_url?: str,
  environments?: [{name, base_url}], active_environment?: str,
  openapi_url?: str,         // 스펙 주소
  openapi?: object|str,      // 스펙 객체(문자열이면 JSON으로 풀어 보고, 안 되면 openapi_text로)
  openapi_text?: str,        // 업로드 원문(JSON/YAML/XML/SDL/proto)
  auth?: {kind, …방식별 필드},
  timeout_ms?: int, retries?: int, health_path?: str
}
```
백엔드 전처리: 빈 문자열·빈 배열 필드 제거, 태그 공백 제거, 이름·주소 공백 제거; 환경은 이름·주소가 모두 있는 것만, 활성 환경이 비면 첫 환경, `base_url`이 비면 활성 환경 주소; 인증은 방식별 허용 필드만(api_key: header·query_param·secret_env / bearer: header·secret_env / basic: secret_env / oauth2: token_url·client_id·client_secret_env·scopes / login_token: token_url·login_body·username_field·username_env·password_field·password_env·token_path·header·ttl_seconds·scheme), 빈 값 제거. 인증 사전 검증(실패 시 422 `invalid_params`):
- 모든 `*_env` 값은 `^[A-Za-z_][A-Za-z0-9_]*$` 형태 — 아니면 「auth.<f> '<v>' 은(는) 환경변수 이름이 아닙니다 — 비밀 값이 아니라 그 값을 담은 환경변수 이름(영문·숫자·_)을 적습니다.」
- login_token: token_url http(s), username_env·password_env 필수, 필드 이름·점 경로·헤더 형식, login_body는 JSON 객체(문자열이면 파싱)이고 비밀번호 필드 이름을 키로 갖지 않음, ttl_seconds 양의 정수.

**수정 본문 (PATCH)**: SystemBody에서 name·protocol을 뺀 필드 중 보낸 것만(null 아닌 값). `environments`를 보내면 목록 교체. 스펙 원문(`openapi`/`openapi_text`)을 보내면 스펙 교체(화면은 쓰지 않음). `openapi_url` 변경은 주소만 바꾸며 operation 갱신은 refresh로.

**System 응답**
```
{
  name, display_name (없으면 name), description (""), owner_team (""), contact (""),
  tags: [], icon (없으면 "generic"),
  protocol (없으면 "rest"), spec_format|null,
  executable: bool (protocol ∈ {rest, odata}), adapter_required: !executable,
  base_url (활성 환경 주소), environments: [{name, base_url}], active_environment,
  openapi_url|null,
  auth: {kind, …공개 필드},           // 비밀 값 없음
  auth_kind, auth_header|null, auth_secret_env|null,
  timeout_ms, retries (null이면 2), health_path (없으면 "/health"),
  operations_count, route: "/svc/<name>",
  created_at, updated_at              // RFC3339 UTC 초, 'Z'
}
```
상세(GET 하나)는 여기에 `operations: [Operation]`.
- 공개 auth: api_key `{kind, header(쿼리면 null), query_param, secret_env}`, basic·bearer `{kind, header, secret_env}`(basic의 header는 `Authorization`), oauth2 `{kind, token_url, client_id, client_secret_env, scopes}`, login_token `{kind, token_url, login_body, username_field, username_env, password_field, password_env, token_path, scheme, ttl_seconds, header}`(빈 값은 기본값 loginId·password·token·Bearer·1800·Authorization로 채움).

**Operation**: `{operation_id, method, path, summary, parameters: [{name, in, required, schema}], request_body_schema|null, source: "openapi"|"wsdl"|"manual"}`

**연결 테스트 응답 (저장 안 함)**
```
{
  spec:   {ok: true, format, operations: N, operation_ids: [≤200], note?: "스펙 없음 — 수동 등록 API 만 쓰는 시스템"}
        | {ok: false, format, operations: 0, error},
  health: {ok, http_status|null, url, latency_ms, error?},   // 인증 없이 활성 주소+헬스 경로 GET 3초, ok = 상태 < 300
  auth:   {ok, kind, required_env: [..], missing_env: [..], checked_in: "kinetic-action", injected_by: "kinetic-action"},
  protocol, executable, adapter_required,
  ok: spec.ok && health.ok && auth.ok
}
```
- 환경 처리 실패 시 health `{ok:false, http_status:null, latency_ms:null, error}`. 주소가 http(s)가 아니면 「http(s) 주소가 아니라 health 를 부를 수 없습니다 (어댑터 필요).」
- `required_env`: api_key·basic·bearer → secret_env, oauth2 → client_secret_env, login_token → username_env·password_env. `missing_env` = 실행기 프로세스 환경에 비어 있는 것. **값은 보지 않는다.**

**상태 확인 응답**: `{ok, http_status|null, latency_ms, checked_at, error?}` — 활성 주소+헬스 경로를 **인증을 붙여** GET 3초, ok = 상태 < 300. error는 `HTTP <s>` / `<예외 종류>: <설명>` / `auth_unavailable: <사유>`.

**조회 요청/응답**: `{operation_id, path_params?: {}, query?: {}}` → `{ok, http_status|null, data, latency_ms, truncated, error?}`. 규칙: operation_id 필수 문자열, path_params·query는 객체, query 값은 스칼라 또는 스칼라 배열(None 무시), 시스템은 실행 가능 프로토콜이어야 함(아니면 422 `not_executable` 「시스템 '<n>' 은 protocol '<p>' 라 어댑터가 필요합니다 (현재 실행 가능: rest·odata).」), operation은 GET이어야 함(아니면 422 `not_readonly` 「'<id>' 는 <M> operation 입니다 — 조회는 GET 만, 쓰기는 액션(plan → execute)으로 하세요.」). 경로 변수 채움, `Accept: application/json`, 시스템 타임아웃. data는 JSON(아니면 텍스트), 목록 항목이 상한(기본 500)을 넘으면 잘라 `truncated:true`. 감사 기록 남김.

**API 추가 본문**: `{operation_id, method(기본 POST, 대문자화), path, summary, parameters, request_body_schema?}` → Operation(+`source:"manual"`). 같은 operation_id면 교체.

**삭제 응답**: `{deleted: true, used_by: ["Class.action", …]}` — 발행된 액션 중 단계 또는 보상 단계가 이 시스템을 쓰는 것. 사용 중이어도 삭제한다.

### 5.2 실행기 API (레지스트리 부분, `/api/kinetic`)
5.1 표와 같은 경로·본문·응답. 추가 사항:
- 인증: `Authorization: Bearer <JWT>` 필수. RS256, JWKS URL에서 공개키 조회(5분 캐시), `aud`=`kinetic-action`, `iss`=설정값, `sub`·`exp` 필수, 시계 여유 30초. 실패 401 `unauthenticated` 「Bearer 토큰이 필요합니다.」/「토큰 검증 실패: …」 + 헤더 `WWW-Authenticate: Bearer resource_metadata="<public_base>/.well-known/oauth-protected-resource"`. `roles`는 문자열이면 배열로 정규화.
- 역할: 등록·테스트·수정·삭제·refresh·API 추가/삭제 = `kinetic_admin`(없으면 403 `forbidden` 「역할 'kinetic_admin' 이 필요합니다.」). 목록·상세·상태·operations·조회 = 유효 토큰이면 누구나.
- `GET /api/kinetic/health` → `{ok:true}` (인증 없음).
- `GET /api/kinetic/systems/routes` — 내부 비밀 헤더 `X-Kinetic-Internal` 일치 시에만(아니면 403 「내부 호출 전용입니다 (X-Kinetic-Internal).」). 실행 가능 시스템마다 `{id:"svc-<name>", system, path_prefix:"/svc/<name>", uri, timeout_ms, retries, auth_kind, auth_header, auth_value_env, auth_query_param, basic_env, oauth2:{token_url,client_id,client_secret_env,scopes}|null, login_token:{…}|null}` — 게이트웨이 배포용, 비밀 값 없음.
- `/.well-known/oauth-protected-resource`(및 `/mcp` 접미) → `{resource, authorization_servers:[issuer], bearer_methods_supported:["header"], scopes_supported:[]}`.
- 모든 응답에 `X-Request-Id`(요청 값 또는 새 값).
- 오류 코드 → 상태: unauthenticated 401, forbidden 403, not_found 404, invalid_params·not_executable·not_readonly 422, conflict 409, bad_gateway 502, 그 밖 400.

등록 규칙(실행기):
- 이름 `^[a-z0-9][a-z0-9-]{0,62}$`, `routes` 금지 → 422 「name 은 소문자·숫자·'-' 만 허용됩니다 ('routes' 제외).」
- **같은 이름이면 교체**. 최초 등록 시각·수동 API는 유지. 표시 정보(display_name·owner_team·contact·tags·icon)는 본문에 없으면 이전 값 유지, description은 본문 값 또는 이전 값.
- 스펙 입수 우선순위: 스펙 객체 > 원문 텍스트 > 스펙 주소(10초 GET). 원문은 JSON → YAML 순으로 읽고, XML/SDL/proto는 원문 유지. 형식 판별: `swagger: 2…`→swagger2, `openapi: 3…`→openapi3, `asyncapi` 키→asyncapi, `paths`만 있으면 openapi3, XML의 Edmx→odata_metadata, WSDL definitions/description→wsdl, `syntax="proto2|3"` 또는 service+rpc→proto, `type Query {`/`schema {` 등→graphql_sdl. 판별 불가 → 422 「스펙 형식을 알 수 없습니다 (…)」. 빈 원문 → 「스펙 원문이 비어 있습니다.」 읽기 실패 → 「스펙을 JSON·YAML 로 읽지 못했습니다: …」, 객체 아님 → 「스펙 문서가 객체(JSON/YAML 매핑)가 아닙니다.」, 주소 실패 → 「스펙을 가져오지 못했습니다: …」. 스펙이 하나도 없으면 빈 명세(수동 API 전용).
- Swagger 2.0은 OpenAPI 3으로 변환해 저장: 경로·파라미터(body→requestBody, formData→form 본문, path/query/header/cookie), 응답, definitions→components.schemas(`$ref` 재작성), securityDefinitions→securitySchemes, `servers[0].url = <scheme>://<host><basePath>`(https 우선, host 없으면 basePath만).
- WSDL은 portType/interface 안의 operation 이름만 뽑아 `POST /` 「SOAP operation (어댑터 필요)」 operation으로 표시. 다른 비REST 형식은 원문만 보관(operation 0).
- OpenAPI operation 추출: `operationId` 있는 get/post/put/patch/delete만. 파라미터 = 경로 공통 + 개별(`$ref` 펼침), 요청 본문 스키마 = `application/json`만(`$ref` 펼침, 깊이 8 제한). `servers[0].url`의 경로 부분(변수 없을 때)이 활성 주소 끝에 이미 있지 않으면 operation 경로 앞에 붙인다.
- 프로토콜 = 본문 값 > 스펙 형식 기본(wsdl→soap, graphql_sdl→graphql, proto→grpc, asyncapi→async, odata_metadata→odata) > rest.
- 환경: environments를 주면 목록 교체(각 이름 `^[A-Za-z0-9][A-Za-z0-9_.-]{0,49}$`, 중복 금지 「환경 이름 '<n>' 이 중복됩니다.」). 활성 환경 = 본문 값(목록에 있어야 함) > 등록 시 base_url과 같은 주소의 환경 > 첫 환경. environments 없이 base_url만 주면 활성 환경 주소만 변경(새 등록이면 `default` 하나). 저장된 base_url = 활성 환경 주소. 주소는 rest·odata·soap·graphql이면 http(s) 필수(「base_url 은 http(s) URL 이어야 합니다.」), 그 밖은 비지 않고 2000자 이하.
- 인증: kind는 6종(아니면 「auth.kind 는 none|api_key|…」). `secret`·`value`·`password`·`client_secret`·`token`·`api_key` 키에 값이 있으면 422 「auth.<k>: 비밀 값은 등록하지 않습니다 — 환경변수 이름(*_env)을 주세요.」 env 이름은 `^[A-Z_][A-Z0-9_]*$`(대문자만) — 아니면 「auth.<f> 는 환경변수 이름이어야 합니다 (값 아님). 예: CMMS_API_KEY」. basic은 secret_env 필수. api_key는 header와 query_param 중 하나만, 기본 헤더 `X-API-Key`; bearer 기본 헤더 `Authorization`; basic 헤더는 항상 `Authorization`. oauth2: token_url http(s), client_id 1–200자, scopes 문자열 배열(문자열이면 공백 분리). login_token: token_url http(s), login_body 객체(≤4000자, 아이디·비밀번호 필드 키 금지, 비밀처럼 보이는 키(`secret, value, password, passwd, pwd, client_secret, token, api_key, apikey, access_token`)에 값 금지), 필드 이름 형식·서로 달라야 함, token_path 점 경로(최대 10단), 헤더 형식, scheme 0–30자 영문 시작(빈 값 허용), ttl 60–86400.
- 정책: timeout_ms 정수(최소 1; 등록 본문에 없으면 **10000**), retries 0–5 정수(없으면 저장 안 함 → 표시 2), health_path `/` 시작(없으면 `/health`).
- 표시: display_name ≤200, owner_team ≤200, contact ≤500, tags ≤30개·각 1–50자(중복 제거), icon `^[a-z0-9][a-z0-9_-]{0,39}$`(빈 값 허용).
- refresh: 스펙 주소가 없으면 422 「시스템 '<n>' 에 openapi_url 이 없습니다.」. 주소에서 다시 입수(이전 형식 힌트 사용).
- API 추가 검증: operation_id `^[A-Za-z_][A-Za-z0-9_.-]{0,99}$`, method 5종, path `/` 시작, 파라미터 in ∈ path/query/header(path는 required 강제), 경로의 `{변수}`는 모두 path 파라미터로 선언(「경로 변수 [...] 가 parameters(in: path) 에 없습니다.」), 본문 스키마는 객체.
- API 삭제: 수동 API만. 스펙 출처면 409 「스펙에서 온 operation 은 지울 수 없습니다 (명세를 고치고 refresh).」, 없으면 404 「operation '<id>' 이 없습니다.」
- 없는 시스템: 404 「시스템 '<n>' 이 등록되지 않았습니다.」
- 감사 기록 이벤트: `register_system`(name), `update_system`(name, 바뀐 필드 이름 목록), `delete_system`(name, used_by), `refresh_system`(name, operations 수), `add_operation`, `delete_operation`, `query`(system, operation_id, http_status, ok, truncated). 행위자 sub와 request_id 포함.

### 5.3 실행기 → 업무 시스템 호출 계약 (액션·조회·상태 공통)
M2(액션 실행)가 의존하는 시스템 측 계약.
- 주소: 활성 환경 주소 + operation 경로(경로 변수 채움) + 쿼리.
- 헤더: `Idempotency-Key`(액션 단계마다 고유 — 전진 `<plan>:<대상>:<단계>:a<시도>`, 보상은 끝에 `:c`), `X-Kinetic-Run`(실행 ID), 내부 비밀 헤더(설정 시), 인증 헤더/쿼리. 미리보기 등에 노출할 때는 `Authorization`, `X-API-Key`, 내부 비밀 헤더를 가린다.
- 인증 주입(실행기 프로세스 환경 변수에서 값을 읽음, 값이 비면 인증 없이 보냄):
  - api_key: 헤더 `<header>: <값>` 또는 쿼리 `<param>=<값>`
  - basic: `Authorization: Basic base64(<값>)` (값 = `user:password`)
  - bearer: `<header>: Bearer <값>` (값이 이미 `Bearer `로 시작하면 그대로)
  - oauth2 client credentials: 토큰 URL에 form POST(`grant_type=client_credentials, client_id, client_secret, scope`), 응답 `access_token`, `expires_in`(없으면 300초)에서 60초 뺀 시각까지 캐시, `Authorization: Bearer`. 실패 → `auth_unavailable`
  - login_token: 로그인 URL에 JSON POST(고정 본문 + 아이디·비밀번호 필드), 응답에서 점 경로로 토큰, 만료 = JWT `exp` 또는 ttl, 60초 전 갱신, `<header>: <scheme> <token>`(스킴 비면 토큰만). 업무 호출이 401이면 그 토큰을 버리고 한 번 재로그인·재시도. 아이디/비밀번호 env 없음·로그인 실패 → `auth_unavailable`
  - 비밀 값·토큰 응답 본문은 로그에 남기지 않는다.
- 타임아웃: 시스템 `timeout_ms`. 동시 호출 상한(기본 8).
- 결과: 2xx면 성공, 응답은 JSON(아니면 텍스트 앞 2000자).
- **0.1.1 관찰:** 시스템별 `retries` 값은 저장·표시만 되고 직접 모드 호출에는 쓰이지 않는다(재시도는 실행 단위 재시도 API의 몫). 구현 시 원본과 맞추려면 동일하게, 개선하려면 결정 필요(9절).
- 실행 가능 프로토콜은 rest·odata뿐. 다른 프로토콜 시스템을 쓰는 액션은 계획 단계에서 422 `not_executable`.

### 5.4 신원 토큰과 키 배포 (셸 책임)
- 앱은 설치별 RSA 2048 서명키를 비밀값 파일에 두고, 공개키를 로컬 웹 오리진 `GET /kinetic-idp/jwks.json`으로 내보낸다: `{"keys":[{kty, n, e, kid, alg:"RS256", use:"sig"}]}`. kid = 개인키 PEM의 SHA-256 base64url 앞 16자.
- 부팅 때마다 토큰을 새로 발급(유효 30일): 헤더 `{alg:"RS256", typ:"JWT", kid}`, 페이로드 `{sub, roles, aud:"kinetic-action", iss:"ontology-studio-lite", iat, exp}`.
  | 용도 | sub | roles |
  |---|---|---|
  | 화면(Studio) | `lite-user` | `kinetic_admin`, `kinetic_approver`, `scm_operator` |
  | 에이전트 | `lite-agent` | `scm_operator` |
  | 예제 등록·주소 갱신(셸 내부) | `lite-setup` | `kinetic_admin` |
- 역할 카탈로그(구축 에이전트에 보여 줌): `[{"role":"scm_operator","description":"공급망 운영 담당 — 출하 우선순위·발주 보류·고객 안내를 요청할 수 있다","claims":[]}]`.

## 6. 데이터 모델

### 6.1 시스템 레코드 (키: name)
| 필드 | 형태 | 비고 |
|---|---|---|
| name | 문자열 ≤63 | 키, 변경 불가 |
| display_name, description, owner_team, contact | 문자열 | |
| tags | 문자열 배열(JSON) | |
| icon | 문자열 키 | |
| protocol | 문자열 | 비면 rest |
| spec_format | 문자열 | |
| openapi | JSON 문자열 | OpenAPI 3 문서(변환 후), 비REST·스펙 없음은 `{}` |
| spec_text | 문자열 | OpenAPI로 못 바꾸는 원문 보관 |
| openapi_url | 문자열 | 스펙 주소 |
| base_url | 문자열 | 활성 환경 주소(파생값이지만 저장) |
| environments | JSON `[{name, base_url}]` | |
| active_environment | 문자열 | |
| auth_kind, auth_header, auth_secret_env, auth_query_param, auth_token_url, auth_client_id, auth_client_secret_env, auth_scopes(JSON), auth_login(JSON: login_body, username_field, username_env, password_field, password_env, token_path, scheme, ttl_seconds) | | 비밀 값 없음 |
| timeout_ms | 정수, 필수 | |
| retries | 정수 또는 null | |
| health_path | 문자열 | |
| manual_ops | JSON Operation 배열 | 스펙 재입수와 무관하게 유지 |
| created_at, updated_at | RFC3339 UTC | |

- operation 목록 = 스펙에서 뽑은 것 + 수동(같은 id는 수동 우선). 계산 결과는 시스템별로 메모리 캐시하고 저장 시 무효화.
- 같은 저장소(액션 실행기 DB)에 계획·실행·감사 표가 함께 있다(M2). 감사 행: `{id, ts, event, actor_sub, request_id, plan_id, run_id, detail(JSON)}`.

### 6.2 예제 시스템 (첫 실행 자동 등록)
| name | 표시 이름 | 설명 | 담당 팀 | icon | tags | 인증 | API |
|---|---|---|---|---|---|---|---|
| sample-erp | 구매 ERP | 발주 보류·해제, 협력사 납기 독촉 | 구매팀 | erp | erp, purchasing, sample | api_key, 헤더 `X-API-Key`, env `ERP_API_KEY` | 6 |
| sample-wms | 물류 WMS | 입고 선적 조회·우선순위 변경 | 물류팀 | wms | wms, logistics, sample | basic, env `WMS_BASIC` | 3 |
| sample-crm | 고객 CRM | 고객 안내 발송·철회 | 고객지원팀 | crm | crm, customer, sample | bearer, env `CRM_TOKEN` | 4 |
공통: protocol rest, base_url `http://127.0.0.1:<서비스 포트>`, openapi_url `<base_url>/openapi.json`, health_path `/health`, timeout_ms 5000, retries 2, environments `[{name:"local", base_url}]`, active `local`.

### 6.3 예제 업무 시스템 (내장 마이크로서비스)
각자 자기 스키마만 고치는 작은 REST 서비스. 업무 DB는 A2의 예제 DB(`sample`), 접속 계정은 전용 역할(SELECT/INSERT/UPDATE만). OpenAPI 문서를 `/openapi.json`에 제공, `/health`(DB `SELECT 1`, 스키마 비노출, 인증 없음) → `{"status":"ok"}`.

| 시스템 | 인증 | operation (operationId · 메서드 경로 · 동작) |
|---|---|---|
| ERP (발주) | `X-API-Key` = env 값, 불일치 401 「X-API-Key 가 맞지 않습니다」 | getPurchaseOrder · GET `/purchase-orders/{po_id}` · 발주 + 보류 이력 / holdPurchaseOrder · POST `/purchase-orders/{po_id}/hold` 본문 `{reason (필수), requestedBy?}` · 상태 ON_HOLD, 이전 상태 기록, 이미 보류면 409, 응답 `{id, poId, status:"ON_HOLD", previousStatus}` / releasePurchaseOrder · POST `/purchase-orders/{po_id}/release` `{reason?}` · 최근 보류 해제·이전 상태 복원, 보류 아님 409, 응답 `{poId, status, holdId}` / createExpediteRequest · POST `/expedite-requests` `{poId, reason, requestedBy?}` · 협력사 독촉 생성, 응답 `{id, poId, supplierId, status:"SENT"}` / withdrawExpediteRequest · POST `/expedite-requests/{request_id}/withdraw` `{reason?}` · SENT만 철회, 아니면 409 / listExpediteRequests · GET `/expedite-requests` |
| WMS (선적) | Basic, env 값 `user:password`, 실패 401 + `WWW-Authenticate: Basic` | getShipment · GET `/shipments/{shipment_no}` / setShipmentPriority · POST `/shipments/{shipment_no}/priority` `{priority: URGENT|HIGH|NORMAL, reason?, requestedBy?}` · 우선순위 변경·이력, 입고 완료(DELIVERED)인데 NORMAL 아님이면 409, 응답 `{shipmentNo, priority, previous, status: <바뀐 값>}` (되돌리기에도 사용) / listShipments · GET `/shipments?min_delay=0` · 지연일 내림차순 |
| CRM (고객) | Bearer = env 값, 불일치 401 | getCustomer · GET `/customers/{cust_no}` · 고객 + 안내 목록 / createNotice · POST `/notices` `{custNo, subject, message, requestedBy?}` · 고객 없으면 404, 응답 `{id, custNo, status:"SENT"}` / withdrawNotice · POST `/notices/{notice_id}/withdraw` `{reason?}` · SENT만 / listNotices · GET `/notices` |
- 없는 대상은 404(「발주 X 가 없습니다」 등). 쓰기 API는 `Idempotency-Key`가 같으면 처음 결과를 그대로 돌려준다(프로세스 메모리, 재시작 시 초기화).
- 예제 DB 추가 객체(첫 실행 1회, 재실행 안전): `wms.shipment.priority`(기본 NORMAL) 열, 이력 표 `wms.priority_change`, `erp.po_hold`, `erp.expedite_request`, `crm.notice`. 읽기 전용 패브릭 계정에 SELECT 권한.

## 7. 상태·저장

- 레지스트리: 액션 실행기 전용 SQLite 파일 `<사용자 데이터 폴더>/kinetic.db`. 시작할 때 표가 없으면 만들고, 이미 있으면 빠진 열만 추가한다(데이터 보존). PostgreSQL URL도 받을 수 있게 설계됨(0.1.1은 SQLite).
- 비밀 값: A2 비밀값 파일에 예제 서비스 비밀 3개·내부 비밀·서명키. 예제 비밀은 실행기와 예제 서비스 프로세스 환경 변수로만 전달.
- **사용자가 등록한 시스템의 비밀 값**: 실행기는 자기 프로세스 환경 변수에서 읽는다. 0.1.1 내장 실행기 환경 = 앱 실행 환경 + 예제 비밀 3개 + 실행기 설정이며 `studio.env` 내용은 들어가지 않는다(코드 관찰, 튜토리얼과 불일치 — 9절 결정·10절 확인).
- 화면 상태(마법사 입력, 테스트 결과)는 저장하지 않는다. 탭을 닫으면 사라진다.
- 실행기 프로세스(A1 프로세스 관리): 이름 `kinetic`, 로그 `logs/kinetic.log`. 예제 서비스 `erp`·`wms`·`crm`. 선호 포트 27830, 27841–27843.

### 7.1 부팅 시 셸 동작
1. 비밀값 파일에 위 키가 없으면 생성.
2. `studio.env`에 `KINETIC_URL`이 있으면 외부 실행기로 보고 내장 실행기·예제 서비스를 띄우지 않으며, Studio에는 사용자의 `KINETIC_*` 값을 넘긴다. 없으면 내장 주소·발급 토큰을 넘긴다. (둘 다 없을 수 없음; 자리표시자는 닿지 않는 주소)
3. 내장 실행기·예제 서비스 3개를 시작하고(Studio 시작과 병렬) 각자 헬스로 준비 확인(60초).
4. 준비되면 **주소 갱신**: 예제 시스템이 등록돼 있고 base_url이 현재 포트 주소와 다르면, 기존 레코드를 바탕으로 base_url·스펙 주소·환경(`local`)만 바꿔 재등록(다른 사용자 수정은 유지). 로그 「시스템 주소 갱신 <name>: <old> → <new> (<status>)」.
5. **예제 등록**: 없는 예제 시스템만 등록(사용자가 고친 예제 등록은 보존, 지운 것은 다시 등록됨). 로그 「시스템 등록: a, b」.
6. 성공하면 실행기 가동 표시(홈 카드·info의 `kineticConfigured`), 실패하면 「kinetic-action 을 시작하지 못했습니다 — 액션 없이 계속합니다: <msg>」 로그만 남기고 계속.

## 8. 다른 기능과의 의존

| 대상 | 의존 내용 |
|---|---|
| A1 셸 | 포트 할당, 프로세스 관리, 로컬 웹 오리진(JWKS 경로, 실행기 미가동 대체 응답, `/api/*` 프록시), 홈 카드 「시스템 등록」(실행기 구성 시 표시) |
| A2 저장소 | 비밀값 파일, 예제 DB와 서비스 계정·추가 표 |
| M3 데이터소스 / M4 포털 | 예제 업무 시스템이 원천 DB를 바꾸면 가상 노드에 바로 보임(액션 결과 확인 경로) |
| M1 온톨로지 구축 | 구축 마법사 「소스」 단계가 시스템 목록을 읽어 시스템을 재료로 선택. 구축 에이전트 도구: 시스템 목록(name·description·base_url·operations_count·route·health_path), 시스템 API 목록, GET 조회(현재 값 확인), 액션 생성 시 operation 존재 확인(실행기 불통이면 경고만, 시스템 없음/operation 없음 구분). 액션 정의의 단계·보상 = `{system, operation_id, arg_mapping}` — arg_mapping 키는 `path.<이름>`·`query.<이름>`·`header.<이름>`·`body.<속성>` |
| M1 액션 편집기 | 시스템·operation 목록 드롭다운, 실행기 불통 시 「kinetic-action 에 닿지 못했습니다 (<url>). 정의는 저장되지만 시스템·operation 목록과 dry-run 은 쓸 수 없습니다. <error>」 |
| M2 질의·액션 | 계획 시 단계·보상의 시스템이 등록돼 있고 실행 가능하며 operation이 있어야 함(없으면 404, 실행 불가 422). 실행 시 5.3 호출 계약. 에이전트용 GET 조회 도구. 시스템 삭제 시 해당 액션 실패 |
| 예제 온톨로지 | 예제 액션 3개가 sample-wms·sample-erp·sample-crm의 operation을 단계·보상으로 사용 |

## 9. 오류·예외

| 상황 | 동작 |
|---|---|
| 실행기 미시작 | 상태 200 `reachable:false`, 목록 503 `{detail}` → 화면 배너 + 목록 오류 |
| 외부 실행기 불통 | 503 `unavailable` |
| 토큰 무효·만료 | 401 → 「kinetic-action 인증 실패 …」 또는 실행기 메시지 |
| 역할 없음 | 403 → 화면 「권한이 없습니다 — …kinetic_admin 역할이 필요합니다.」 |
| 이름 규칙 위반 | 화면에서 막음, 서버 422 |
| 같은 이름 등록 | 교체(경고 없음) |
| 스펙 입수 실패 | 등록 422, 테스트는 spec.ok=false로 계속 |
| 헬스 경로 404 등 | 테스트·상태 모두 실패로 표시(3xx 이상 = 실패) |
| 비밀 값을 인증 칸에 적음 | 백엔드/실행기 422 |
| 비REST 시스템 | 등록 성공, `executable:false`, 액션 계획 422 `not_executable`, 조회 422 |
| 스펙 출처 API 삭제 | 409 |
| 사용 중 시스템 삭제 | 허용, `used_by`로 경고 |
| 스펙 주소 없는 refresh | 422 |
| 헬스 시 인증 토큰 발급 실패 | `auth_unavailable: …` |

## 10. 원본과 비교할 테스트 항목

결정적 기능이므로 값까지 비교한다(에이전트 기능 아님).
1. 첫 실행 후 `GET /api/act/systems` → 3건, 이름순 `sample-crm, sample-erp, sample-wms`, 6.2 표의 값과 `operations_count` 4/6/3, `route` `/svc/<name>`, `executable:true`, `retries:2`, `timeout_ms:5000`.
2. `GET /api/act/systems/sample-erp` → `operations` 6건(id·method·path가 6.3과 동일), `source:"openapi"`, auth `{kind:"api_key", header:"X-API-Key", query_param:null, secret_env:"ERP_API_KEY"}`. 응답 어디에도 비밀 값 없음.
3. `GET /api/act/systems/sample-wms/health` → `ok:true, http_status:200`, 필드 4개(`ok, http_status, latency_ms, checked_at`).
4. `GET /api/act/health` → `reachable:true`, identity `{configured:true, sub:"lite-user", roles:[kinetic_admin, kinetic_approver, scm_operator]}`.
5. 테스트 API: (a) 스펙 URL 정상·헬스 정상·인증 none → `ok:true`; (b) 존재하지 않는 env 이름 → `auth.ok:false, missing_env:[…]`; (c) 헬스 404 → `health.ok:false, error:"HTTP 404"`; (d) 스펙 없음 → `spec.note`; (e) 저장 안 됨(목록 변화 없음).
6. 등록 검증: 이름 `Bad_Name`·`routes` → 422; `auth:{kind:"api_key", secret_env:"lowercase"}` → 422; `auth:{kind:"bearer", token:"x"}` → 422; base_url `ftp://…` → 422; retries 6 → 422.
7. 같은 이름 재등록 → 200, created_at 유지, 수동 API 유지.
8. Swagger 2.0 문서 업로드 → `spec_format:"swagger2"`, operation 추출, basePath 접두 처리.
9. WSDL 업로드 → protocol `soap`, `executable:false`, operation = portType operation 이름(`POST /`).
10. 수동 API: 경로 변수 미선언 → 422; 추가 → `source:"manual"`; refresh 후 유지; 스펙 operation 삭제 → 409.
11. 조회: GET 목록 operation → `{ok, http_status, data, latency_ms, truncated}`; POST operation → 422 `not_readonly`.
12. 삭제: 예제 액션이 쓰는 시스템 → `{deleted:true, used_by:[…]}`; 재시작 후 예제 시스템 복원.
13. 포트 변경 재시작 → 예제 base_url·openapi_url·environments 갱신, 나머지 필드 유지.
14. 실행기 미가동 시 셸 대체 응답 2종(문구·상태 코드 일치).
15. JWKS: `GET /kinetic-idp/jwks.json` 구조, 발급 토큰의 aud/iss/sub/roles/exp(30일).
16. 화면: 마법사 6단계 라벨·✓ 규칙, 1–4단계 충족 시 테스트·등록 버튼 활성(테스트 미통과로도 등록 가능), 「조회」 버튼 노출 조건, 신원 배지 문구, 배너 문구(등록·저장·삭제·스펙 다시 읽기·API 추가/삭제).
17. 감사 기록: 등록·수정(바뀐 필드 목록)·삭제(used_by)·refresh·API 추가/삭제·조회 이벤트가 남는지.

## 11. 구현 시 결정할 것 (원본 동작 vs 개선)
1. **사용자 시스템 비밀 값 공급 방식**: 원본(코드 기준)은 실행기 환경에 `studio.env`를 넣지 않아 튜토리얼 안내와 다르다. 재현할지, `studio.env`(또는 별도 비밀 저장소)를 실행기 환경에 넣을지.
2. **헬스 판정**: 원본 0.1.1은 3xx 이상 = 실패. 튜토리얼은 5xx만 실패, 404/405는 「연결됨 · 경고」. 어느 쪽을 기준으로 할지.
3. **빈 헬스 경로**: 원본은 `/health`로 대체. 튜토리얼은 "활성 주소 자체 점검". 
4. **시스템별 재시도**: 원본 직접 모드는 미적용. 
5. **같은 이름 등록 덮어쓰기**: 원본은 경고 없이 교체. 생성 모드에서 중복을 막을지.
6. 실행기를 별도 서비스로 둘지(원본 구조), 백엔드에 합칠지 — 외부 계약(`/api/act/*`)만 맞추면 내부 구조는 자유.

## 12. 모르는 점 (4단계 실행 기록에서 확인)
1. `studio.env`에 사용자 시스템 비밀(예 `CMMS_API_KEY=…`)을 적고 재시작했을 때 테스트의 `missing_env`가 비는지(코드상 안 빌 것으로 추정).
2. 튜토리얼의 「연결됨 · 경고 ~」 표시가 0.1.1에 정말 없는지(번들 문자열상 없음), Petstore 테스트 결과(튜토리얼: API 19개, 통과).
3. 예제 서비스 OpenAPI의 `servers` 유무와 실제 operation 경로(접두 처리 영향).
4. CRM 카드 아이콘이 「기타」로 보이는지, 카드·상세 실제 레이아웃(캡처).
5. 실행기 상태 1회 캐시로 인해, 부팅 중 열린 탭이 실행기 기동 후에도 배너를 유지하는지.
6. 내장 실행기 가동 중 `GET /api/act/systems`의 실제 응답 시간·상태 확인 병렬 호출 수.
7. 업무 시스템 호출 시 내부 비밀 헤더가 사용자 등록 외부 시스템에도 전송되는지(코드상 전송 — notes 참고).
8. 삭제 후 재시작 시 예제 시스템이 정말 다시 등록되는지, 그때 예제 액션이 정상 동작하는지.
9. 토큰 30일 만료 — 앱을 30일 이상 켜 두면 화면 호출이 401이 되는지(부팅 때만 발급).
10. 편집 화면에서 「파일 업로드」로 스펙을 바꿀 방법이 없는지(라디오 잠김) 확인.
